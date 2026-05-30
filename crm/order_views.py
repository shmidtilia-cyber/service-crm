from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render

from .models import AdCampaign, DeviceBrand, DeviceGroup, DeviceModel, Order, OrderService
from .views import DEFAULT_BRANDS, DEFAULT_DEVICE_GROUPS, DEFAULT_MODELS, STATUS_GROUPS, _add_order_payment, _add_comment, _change_status, _save_service, _update_order


def _redirect_after_save(request, order):
    close_after_save = request.POST.get('close_after_save') == '1'
    if close_after_save:
        return redirect('dashboard')

    tab = request.POST.get('active_tab') or 'main'
    allowed_tabs = {'main', 'services', 'payments', 'comments', 'history', 'files'}
    if tab not in allowed_tabs:
        tab = 'main'

    return redirect(f'/orders/{order.id}/?tab={tab}')


def order_detail(request, order_id):
    order = get_object_or_404(
        Order.objects.select_related('customer', 'device_group', 'device_brand', 'device_model', 'manager', 'executor', 'ad_campaign')
        .prefetch_related('events__user', 'comments__user', 'services__executor', 'payments'),
        id=order_id,
    )

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_order':
            _update_order(request)
        elif action == 'change_status':
            _change_status(request)
        elif action == 'save_service':
            _save_service(request)
        elif action == 'add_payment':
            _add_order_payment(request)
        elif action == 'add_comment':
            _add_comment(request)
        else:
            messages.error(request, 'Неизвестное действие')
        return _redirect_after_save(request, order)

    active_tab = request.GET.get('tab') or 'main'
    if active_tab not in {'main', 'services', 'payments', 'comments', 'history', 'files'}:
        active_tab = 'main'

    popular_services = OrderService.objects.values('name').order_by('name')[:12]

    return render(request, 'crm/order_detail.html', {
        'order': order,
        'users': User.objects.order_by('username'),
        'status_groups': STATUS_GROUPS,
        'popular_services': popular_services,
        'active_tab': active_tab,
        'device_groups': list(DeviceGroup.objects.order_by('name').values_list('name', flat=True)) or DEFAULT_DEVICE_GROUPS,
        'device_brands': list(DeviceBrand.objects.order_by('name').values_list('name', flat=True)) or DEFAULT_BRANDS,
        'device_models': list(DeviceModel.objects.order_by('name').values_list('name', flat=True)) or DEFAULT_MODELS,
        'ad_campaigns': list(AdCampaign.objects.order_by('name').values_list('name', flat=True)) or ['Яндекс', 'Google', 'Авито', 'Рекомендация'],
    })
