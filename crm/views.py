from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Sum
from django.shortcuts import redirect, render
from django.utils import timezone

from .models import (
    AdCampaign,
    Customer,
    DeviceBrand,
    DeviceGroup,
    DeviceModel,
    Order,
    OrderComment,
    OrderEvent,
    OrderService,
    Product,
)


DEFAULT_DEVICE_GROUPS = [
    'Ноутбук', 'Телефон', 'Робот-пылесос', 'Фен', 'Стайлер',
    'Планшет', 'Моноблок', 'ПК', 'Пылесос', 'Игровая приставка',
]

DEFAULT_BRANDS = [
    'Apple', 'Samsung', 'Xiaomi', 'Dyson', 'Dreame', 'Roborock',
    'Asus', 'Lenovo', 'MSI', 'HP', 'Acer',
]

DEFAULT_MODELS = [
    'iPhone', 'MacBook', 'Galaxy', 'Redmi', 'Dyson V8', 'Dyson Airwrap',
    'Dreame L10s', 'Roborock Q Revo', 'VivoBook', 'IdeaPad',
]

STATUS_GROUPS = {
    'Новые': [
        ('new', 'Новый'),
        ('client', 'У клиента'),
        ('prepaid', 'Предоплата'),
    ],
    'В работе': [
        ('in_work', 'Ремонт'),
        ('pickup', 'Забор'),
        ('diagnostics', 'Диагностика'),
        ('approval', 'Согласование'),
    ],
    'Отложенные': [
        ('waiting_master', 'Ожидает ответ мастера'),
    ],
    'Доставка': [
        ('sent', 'Доставка'),
    ],
    'Закрытые успешно': [
        ('completed', 'Выдан с ремонтом'),
    ],
    'Закрытые неуспешно': [
        ('cancelled', 'Отказ'),
    ],
}


def _get_or_create_by_name(model, name):
    name = (name or '').strip()
    if not name or name == '- Не задано -':
        return None
    obj, _ = model.objects.get_or_create(name=name)
    return obj


def _parse_deadline(value):
    if not value:
        return None
    try:
        parsed = timezone.datetime.fromisoformat(value)
    except ValueError:
        return None
    if timezone.is_naive(parsed):
        parsed = timezone.make_aware(parsed, timezone.get_current_timezone())
    return parsed


def _current_user(request):
    return request.user if request.user.is_authenticated else None


def _create_order(request):
    customer_name = request.POST.get('customer_name', '').strip()
    customer_phone = request.POST.get('customer_phone', '').strip()
    customer_address = request.POST.get('address', '').strip()

    customer = None
    if customer_name or customer_phone:
        customer, _ = Customer.objects.get_or_create(
            phone=customer_phone,
            defaults={'name': customer_name or customer_phone or 'Клиент', 'address': customer_address},
        )
        changed = False
        if customer_name and customer.name != customer_name:
            customer.name = customer_name
            changed = True
        if customer_address and customer.address != customer_address:
            customer.address = customer_address
            changed = True
        if changed:
            customer.save()

    order = Order.objects.create(
        order_type=request.POST.get('order_type') or 'ЗАКАЗ',
        customer=customer,
        manager=_current_user(request),
        serial_number=request.POST.get('serial_number', '').strip(),
        device_group=_get_or_create_by_name(DeviceGroup, request.POST.get('device_group')),
        device_brand=_get_or_create_by_name(DeviceBrand, request.POST.get('device_brand')),
        device_model=_get_or_create_by_name(DeviceModel, request.POST.get('device_model')),
        condition=request.POST.get('condition', '').strip() or 'Потертости, царапины',
        issue=request.POST.get('issue', '').strip(),
        password=request.POST.get('password', '').strip(),
        ad_campaign=_get_or_create_by_name(AdCampaign, request.POST.get('ad_campaign')),
        manager_notes=request.POST.get('manager_notes', '').strip(),
        estimated_price=request.POST.get('estimated_price') or 0,
        prepayment=request.POST.get('prepayment') or 0,
        urgent=bool(request.POST.get('urgent')),
        deadline=_parse_deadline(request.POST.get('deadline')),
    )
    OrderEvent.objects.create(order=order, user=_current_user(request), text='Создан новый заказ')
    messages.success(request, f'Заказ {order.order_number} создан')


def _add_comment(request):
    order = Order.objects.filter(id=request.POST.get('order_id')).first()
    text = request.POST.get('comment_text', '').strip()
    if not order or not text:
        return
    OrderComment.objects.create(order=order, user=_current_user(request), text=text)
    messages.success(request, f'Комментарий добавлен в заказ {order.order_number}')


def _change_status(request):
    order = Order.objects.filter(id=request.POST.get('order_id')).first()
    new_status = request.POST.get('status')
    valid_statuses = {status for group in STATUS_GROUPS.values() for status, _ in group}
    if not order or new_status not in valid_statuses:
        return
    old_status = order.get_status_display()
    order.status = new_status
    order.save(update_fields=['status', 'updated_at'])
    close_note = ' Заказ закрыт.' if new_status in {'completed', 'cancelled'} else ''
    OrderEvent.objects.create(
        order=order,
        user=_current_user(request),
        text=f'Статус изменен: {old_status} → {order.get_status_display()}.{close_note}',
    )
    messages.success(request, f'Статус заказа {order.order_number} обновлен')


def _save_service(request):
    order = Order.objects.filter(id=request.POST.get('order_id')).first()
    if not order:
        return
    service_id = request.POST.get('service_id')
    service = OrderService.objects.filter(id=service_id, order=order).first() if service_id else None
    if service is None:
        service = OrderService(order=order)
    service.name = request.POST.get('service_name', '').strip() or 'Услуга'
    service.price = request.POST.get('service_price') or 0
    service.cost_price = request.POST.get('service_cost_price') or 0
    service.warranty_days = request.POST.get('warranty_days') or 0
    service.quantity = 1
    service.executor = _current_user(request)
    is_new = service.pk is None
    service.save()
    OrderEvent.objects.create(
        order=order,
        user=_current_user(request),
        text=('Добавлена услуга: ' if is_new else 'Изменена услуга: ') + service.name,
    )
    messages.success(request, f'Услуга сохранена в заказе {order.order_number}')


def dashboard(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create_order':
            _create_order(request)
        elif action == 'add_comment':
            _add_comment(request)
        elif action == 'change_status':
            _change_status(request)
        elif action == 'save_service':
            _save_service(request)
        return redirect('dashboard')

    orders = (
        Order.objects.select_related('customer', 'device_group', 'device_brand', 'device_model', 'manager')
        .prefetch_related('events__user', 'comments__user', 'services')
        .order_by('-created_at')[:100]
    )

    stats = {
        'orders_total': Order.objects.count(),
        'orders_new': Order.objects.filter(status='new').count(),
        'orders_in_work': Order.objects.filter(status='in_work').count(),
        'customers_total': Customer.objects.count(),
        'products_total': Product.objects.count(),
        'stock_total': Product.objects.aggregate(total=Sum('quantity'))['total'] or 0,
        'revenue_total': Order.objects.aggregate(total=Sum('total_price'))['total'] or 0,
        'profit_total': Order.objects.aggregate(total=Sum('profit'))['total'] or 0,
    }

    return render(request, 'crm/dashboard.html', {
        'orders': orders,
        'stats': stats,
        'device_groups': list(DeviceGroup.objects.order_by('name').values_list('name', flat=True)) or DEFAULT_DEVICE_GROUPS,
        'device_brands': list(DeviceBrand.objects.order_by('name').values_list('name', flat=True)) or DEFAULT_BRANDS,
        'device_models': list(DeviceModel.objects.order_by('name').values_list('name', flat=True)) or DEFAULT_MODELS,
        'ad_campaigns': list(AdCampaign.objects.order_by('name').values_list('name', flat=True)),
        'users': User.objects.order_by('username'),
        'status_groups': STATUS_GROUPS,
    })
