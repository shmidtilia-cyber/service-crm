from datetime import timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Count, Sum
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
    OrderPayment,
    OrderService,
    Product,
    UserProfile,
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
    'Новые': [('new', 'Новый'), ('client', 'У клиента'), ('prepaid', 'Предоплата')],
    'В работе': [('in_work', 'Ремонт'), ('pickup', 'Забор'), ('diagnostics', 'Диагностика'), ('approval', 'Согласование')],
    'Отложенные': [('waiting_master', 'Ожидает ответ мастера')],
    'Доставка': [('sent', 'Доставка')],
    'Закрытые успешно': [('completed', 'Выдан с ремонтом')],
    'Закрытые неуспешно': [('cancelled', 'Отказ')],
}


def money(value):
    try:
        return Decimal(str(value or '0').replace(',', '.'))
    except Exception:
        return Decimal('0')


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

    executor = User.objects.filter(id=request.POST.get('executor')).first()
    order = Order.objects.create(
        order_type=request.POST.get('order_type') or 'ЗАКАЗ',
        customer=customer,
        manager=_current_user(request),
        executor=executor,
        serial_number=request.POST.get('serial_number', '').strip(),
        device_group=_get_or_create_by_name(DeviceGroup, request.POST.get('device_group')),
        device_brand=_get_or_create_by_name(DeviceBrand, request.POST.get('device_brand')),
        device_model=_get_or_create_by_name(DeviceModel, request.POST.get('device_model')),
        condition=request.POST.get('condition', '').strip() or 'Потертости, царапины',
        issue=request.POST.get('issue', '').strip(),
        password=request.POST.get('password', '').strip(),
        ad_campaign=_get_or_create_by_name(AdCampaign, request.POST.get('ad_campaign')),
        manager_notes=request.POST.get('manager_notes', '').strip(),
        estimated_price=money(request.POST.get('estimated_price')),
        prepayment=money(request.POST.get('prepayment')),
        urgent=bool(request.POST.get('urgent')),
        deadline=_parse_deadline(request.POST.get('deadline')),
    )
    if order.prepayment and order.prepayment > 0:
        OrderPayment.objects.create(order=order, payment_type='income', cashbox='cash', amount=order.prepayment, comment='Предоплата')
    OrderEvent.objects.create(order=order, user=_current_user(request), text='Создан новый заказ')
    messages.success(request, f'Заказ {order.order_number} создан')


def _add_comment(request):
    order = Order.objects.filter(id=request.POST.get('order_id')).first()
    text = request.POST.get('comment_text', '').strip()
    if order and text:
        OrderComment.objects.create(order=order, user=_current_user(request), text=text)
        messages.success(request, f'Комментарий добавлен в заказ {order.order_number}')


def _create_income_on_close(order, request):
    if not order or order.total_price <= 0:
        return
    if order.payments.filter(payment_type='income', comment__icontains='Оплата при закрытии').exists():
        return
    cashbox = request.POST.get('cashbox') or request.POST.get('payment_cashbox') or 'cash'
    OrderPayment.objects.create(
        order=order,
        payment_type='income',
        cashbox=cashbox,
        amount=order.total_price,
        comment='Оплата при закрытии заказа',
    )
    order.payment_status = 'paid'
    order.save(update_fields=['payment_status', 'updated_at'])
    OrderEvent.objects.create(order=order, user=_current_user(request), text=f'Оплата при закрытии: {order.total_price} ₽')


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
    if new_status == 'completed':
        order.recalculate_money()
        _create_income_on_close(order, request)
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
    service.price = money(request.POST.get('service_price'))
    service.cost_price = money(request.POST.get('service_cost_price'))
    service.discount = money(request.POST.get('service_discount'))
    service.warranty_days = int(request.POST.get('warranty_days') or 0)
    service.quantity = int(request.POST.get('quantity') or 1)
    executor = User.objects.filter(id=request.POST.get('service_executor')).first()
    service.executor = executor or order.executor or _current_user(request)
    is_new = service.pk is None
    service.save()
    OrderEvent.objects.create(order=order, user=_current_user(request), text=('Добавлена услуга: ' if is_new else 'Изменена услуга: ') + service.name)
    messages.success(request, f'Услуга сохранена в заказе {order.order_number}')


def _add_order_payment(request):
    order = Order.objects.filter(id=request.POST.get('order_id')).first()
    if not order:
        return
    payment_type = request.POST.get('payment_type') or 'income'
    cashbox = request.POST.get('cashbox') or 'cash'
    amount = money(request.POST.get('amount'))
    comment = request.POST.get('payment_comment', '').strip()
    if amount <= 0:
        messages.error(request, 'Сумма платежа должна быть больше 0')
        return
    OrderPayment.objects.create(order=order, payment_type=payment_type, cashbox=cashbox, amount=amount, comment=comment)
    if payment_type == 'expense':
        order.total_cost = (order.total_cost or Decimal('0')) + amount
        order.save(update_fields=['total_cost', 'updated_at'])
    order.recalculate_money()
    messages.success(request, 'Платеж добавлен')


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
        elif action == 'add_payment':
            _add_order_payment(request)
        return redirect('dashboard')

    orders = Order.objects.select_related('customer', 'device_group', 'device_brand', 'device_model', 'manager', 'executor').prefetch_related('events__user', 'comments__user', 'services', 'payments').order_by('-created_at')[:100]
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
    popular_services = OrderService.objects.values('name').annotate(cnt=Count('id')).order_by('-cnt')[:12]
    return render(request, 'crm/dashboard.html', {
        'orders': orders,
        'stats': stats,
        'device_groups': list(DeviceGroup.objects.order_by('name').values_list('name', flat=True)) or DEFAULT_DEVICE_GROUPS,
        'device_brands': list(DeviceBrand.objects.order_by('name').values_list('name', flat=True)) or DEFAULT_BRANDS,
        'device_models': list(DeviceModel.objects.order_by('name').values_list('name', flat=True)) or DEFAULT_MODELS,
        'ad_campaigns': list(AdCampaign.objects.order_by('name').values_list('name', flat=True)),
        'users': User.objects.order_by('username'),
        'status_groups': STATUS_GROUPS,
        'popular_services': popular_services,
    })


def users_settings(request):
    for user in User.objects.all():
        UserProfile.objects.get_or_create(user=user)
    if request.method == 'POST':
        action = request.POST.get('action')
        user = User.objects.filter(id=request.POST.get('user_id')).first()
        if action == 'toggle_user' and user:
            user.is_active = not user.is_active
            user.save(update_fields=['is_active'])
            messages.success(request, 'Статус пользователя обновлен')
            return redirect('users_settings')
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        role = request.POST.get('role', 'manager')
        is_active = bool(request.POST.get('is_active'))
        if not username:
            messages.error(request, 'Укажите логин пользователя')
            return redirect('users_settings')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Пользователь с таким логином уже существует')
            return redirect('users_settings')
        new_user = User(username=username, email=username if '@' in username else '', first_name=request.POST.get('full_name', '').strip(), is_active=is_active)
        new_user.set_password(password or '12345678')
        new_user.save()
        profile, _ = UserProfile.objects.get_or_create(user=new_user)
        profile.role = role if role in dict(UserProfile.ROLE_CHOICES) else 'manager'
        profile.save()
        messages.success(request, 'Пользователь создан')
        return redirect('users_settings')
    users = User.objects.select_related('profile').order_by('username')
    return render(request, 'crm/users.html', {'users': users, 'role_choices': UserProfile.ROLE_CHOICES})


def company_dashboard(request):
    today = timezone.localdate()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    now = timezone.now()
    orders = Order.objects.select_related('manager', 'executor', 'customer').all()
    closed_statuses = ['completed', 'cancelled']
    kpi = {
        'orders_total': orders.count(),
        'orders_today': orders.filter(created_at__date=today).count(),
        'orders_week': orders.filter(created_at__date__gte=week_start).count(),
        'orders_month': orders.filter(created_at__date__gte=month_start).count(),
        'in_work': orders.exclude(status__in=closed_statuses).count(),
        'completed': orders.filter(status='completed').count(),
        'cancelled': orders.filter(status='cancelled').count(),
        'overdue': orders.exclude(status__in=closed_statuses).filter(deadline__lt=now).count(),
        'revenue': orders.aggregate(total=Sum('total_price'))['total'] or 0,
        'profit': orders.aggregate(total=Sum('profit'))['total'] or 0,
        'master_salary': orders.aggregate(total=Sum('master_salary'))['total'] or 0,
        'manager_salary': orders.aggregate(total=Sum('manager_salary'))['total'] or 0,
    }
    status_stats = []
    for group, statuses in STATUS_GROUPS.items():
        for status_key, status_label in statuses:
            status_stats.append({'key': status_key, 'label': status_label, 'group': group, 'count': orders.filter(status=status_key).count()})
    masters = User.objects.annotate(executed_count=Count('executed_orders'), executed_revenue=Sum('executed_orders__total_price'), executed_profit=Sum('executed_orders__profit')).order_by('-executed_count')[:10]
    recent_orders = orders.order_by('-updated_at')[:12]
    overdue_orders = orders.exclude(status__in=closed_statuses).filter(deadline__lt=now).order_by('deadline')[:12]
    daily_labels, daily_counts, daily_revenue = [], [], []
    for index in range(6, -1, -1):
        day = today - timedelta(days=index)
        day_orders = orders.filter(created_at__date=day)
        daily_labels.append(day.strftime('%d.%m'))
        daily_counts.append(day_orders.count())
        daily_revenue.append(float(day_orders.aggregate(total=Sum('total_price'))['total'] or 0))
    return render(request, 'crm/company.html', {
        'kpi': kpi,
        'status_stats': status_stats,
        'masters': masters,
        'recent_orders': recent_orders,
        'overdue_orders': overdue_orders,
        'daily_labels': daily_labels,
        'daily_counts': daily_counts,
        'daily_revenue': daily_revenue,
    })
