import json
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import redirect, render

from .models import AdCampaign, CompanySettings, DeviceBrand, DeviceGroup, DeviceModel, UserProfile

CONFIG_PATH = Path(settings.BASE_DIR) / 'crm_runtime_settings.json'

DEFAULT_SETTINGS = {
    'locations': [
        {'id': 1, 'name': 'Основная локация', 'address': '', 'phone': '', 'active': True},
    ],
    'statuses': [
        {'id': 1, 'group': 'Новые', 'code': 'new', 'name': 'Новый', 'color': '#1976d2', 'order': 10, 'roles': ['admin', 'manager', 'master'], 'final': False, 'salary': False, 'cash_income': False},
        {'id': 2, 'group': 'В работе', 'code': 'in_work', 'name': 'Ремонт', 'color': '#00a651', 'order': 20, 'roles': ['admin', 'manager', 'master'], 'final': False, 'salary': False, 'cash_income': False},
        {'id': 3, 'group': 'Закрытые успешно', 'code': 'completed', 'name': 'Выдан с ремонтом', 'color': '#607d8b', 'order': 90, 'roles': ['admin', 'manager'], 'final': True, 'salary': True, 'cash_income': True},
        {'id': 4, 'group': 'Закрытые неуспешно', 'code': 'cancelled', 'name': 'Отказ', 'color': '#bdbdbd', 'order': 100, 'roles': ['admin', 'manager'], 'final': True, 'salary': False, 'cash_income': True},
    ],
    'form_fields': [
        {'id': 1, 'section': 'Заказы и расчёты', 'code': 'device_group', 'name': 'Тип техники', 'required': True, 'visible': True, 'order': 10},
        {'id': 2, 'section': 'Заказы и расчёты', 'code': 'serial_number', 'name': 'IMEI / серийный номер', 'required': True, 'visible': True, 'order': 20},
        {'id': 3, 'section': 'Заказы и расчёты', 'code': 'device_brand', 'name': 'Бренд', 'required': False, 'visible': True, 'order': 30},
        {'id': 4, 'section': 'Заказы и расчёты', 'code': 'device_model', 'name': 'Модель', 'required': False, 'visible': True, 'order': 40},
        {'id': 5, 'section': 'Обращения', 'code': 'customer_name', 'name': 'Клиент', 'required': True, 'visible': True, 'order': 50},
        {'id': 6, 'section': 'Контакты', 'code': 'customer_phone', 'name': 'Телефон', 'required': False, 'visible': True, 'order': 60},
        {'id': 7, 'section': 'Устройства', 'code': 'condition', 'name': 'Состояние', 'required': True, 'visible': True, 'order': 70},
    ],
}


def load_runtime_settings():
    if not CONFIG_PATH.exists():
        save_runtime_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding='utf-8'))
    except Exception:
        data = DEFAULT_SETTINGS.copy()
    for key, value in DEFAULT_SETTINGS.items():
        data.setdefault(key, value)
    return data


def save_runtime_settings(data):
    CONFIG_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def next_id(items):
    return max([int(item.get('id', 0)) for item in items] or [0]) + 1


def as_bool(value):
    return value in ['1', 'true', 'on', 'yes']


def settings_dashboard(request):
    company, _ = CompanySettings.objects.get_or_create(id=1)
    runtime = load_runtime_settings()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'save_company':
            company.shop_name = request.POST.get('shop_name', '').strip() or 'Fadeev-CRM'
            company.company_name = request.POST.get('company_name', '').strip()
            company.company_info = request.POST.get('company_info', '').strip()
            company.currency = request.POST.get('currency', '').strip() or '₽'
            company.order_prefix = request.POST.get('order_prefix', '').strip() or 'F'
            company.order_start_number = int(request.POST.get('order_start_number') or 1000)
            company.save()
            messages.success(request, 'Общие настройки сохранены')

        elif action == 'create_user':
            username = request.POST.get('username', '').strip()
            full_name = request.POST.get('full_name', '').strip()
            password = request.POST.get('password', '').strip() or '12345678'
            role = request.POST.get('role') or 'manager'
            if username and not User.objects.filter(username=username).exists():
                user = User(username=username, email=username if '@' in username else '', first_name=full_name, is_active=True)
                user.set_password(password)
                user.save()
                profile, _ = UserProfile.objects.get_or_create(user=user)
                profile.role = role
                profile.save()
                messages.success(request, 'Сотрудник добавлен')
            else:
                messages.error(request, 'Укажите уникальный логин сотрудника')

        elif action == 'toggle_user':
            user = User.objects.filter(id=request.POST.get('user_id')).first()
            if user:
                user.is_active = not user.is_active
                user.save(update_fields=['is_active'])
                messages.success(request, 'Статус сотрудника изменён')

        elif action == 'save_location':
            item_id = request.POST.get('id')
            item = None
            if item_id:
                item = next((x for x in runtime['locations'] if str(x.get('id')) == str(item_id)), None)
            if not item:
                item = {'id': next_id(runtime['locations'])}
                runtime['locations'].append(item)
            item.update({
                'name': request.POST.get('name', '').strip() or 'Новая локация',
                'address': request.POST.get('address', '').strip(),
                'phone': request.POST.get('phone', '').strip(),
                'active': as_bool(request.POST.get('active')),
            })
            save_runtime_settings(runtime)
            messages.success(request, 'Локация сохранена')

        elif action == 'delete_location':
            runtime['locations'] = [x for x in runtime['locations'] if str(x.get('id')) != str(request.POST.get('id'))]
            save_runtime_settings(runtime)
            messages.success(request, 'Локация удалена')

        elif action == 'save_status':
            item_id = request.POST.get('id')
            item = None
            if item_id:
                item = next((x for x in runtime['statuses'] if str(x.get('id')) == str(item_id)), None)
            if not item:
                item = {'id': next_id(runtime['statuses'])}
                runtime['statuses'].append(item)
            item.update({
                'group': request.POST.get('group', '').strip() or 'Новые',
                'code': request.POST.get('code', '').strip() or f'status_{item.get("id")}',
                'name': request.POST.get('name', '').strip() or 'Новый статус',
                'color': request.POST.get('color', '').strip() or '#1976d2',
                'order': int(request.POST.get('order') or 100),
                'roles': request.POST.getlist('roles') or ['admin'],
                'final': as_bool(request.POST.get('final')),
                'salary': as_bool(request.POST.get('salary')),
                'cash_income': as_bool(request.POST.get('cash_income')),
            })
            runtime['statuses'] = sorted(runtime['statuses'], key=lambda x: int(x.get('order', 100)))
            save_runtime_settings(runtime)
            messages.success(request, 'Статус сохранён')

        elif action == 'delete_status':
            runtime['statuses'] = [x for x in runtime['statuses'] if str(x.get('id')) != str(request.POST.get('id'))]
            save_runtime_settings(runtime)
            messages.success(request, 'Статус удалён')

        elif action == 'save_dictionary':
            dict_type = request.POST.get('dict_type')
            name = request.POST.get('name', '').strip()
            if name:
                if dict_type == 'group':
                    DeviceGroup.objects.get_or_create(name=name)
                elif dict_type == 'brand':
                    DeviceBrand.objects.get_or_create(name=name)
                elif dict_type == 'model':
                    brand = DeviceBrand.objects.filter(id=request.POST.get('brand_id')).first()
                    DeviceModel.objects.get_or_create(name=name, defaults={'brand': brand})
                elif dict_type == 'ad':
                    AdCampaign.objects.get_or_create(name=name)
                messages.success(request, 'Запись справочника сохранена')

        elif action == 'delete_dictionary':
            dict_type = request.POST.get('dict_type')
            item_id = request.POST.get('id')
            model_map = {'group': DeviceGroup, 'brand': DeviceBrand, 'model': DeviceModel, 'ad': AdCampaign}
            model = model_map.get(dict_type)
            if model:
                model.objects.filter(id=item_id).delete()
                messages.success(request, 'Запись справочника удалена')

        elif action == 'save_field':
            item_id = request.POST.get('id')
            item = None
            if item_id:
                item = next((x for x in runtime['form_fields'] if str(x.get('id')) == str(item_id)), None)
            if not item:
                item = {'id': next_id(runtime['form_fields'])}
                runtime['form_fields'].append(item)
            item.update({
                'section': request.POST.get('section', '').strip() or 'Заказы и расчёты',
                'code': request.POST.get('code', '').strip() or f'field_{item.get("id")}',
                'name': request.POST.get('name', '').strip() or 'Новое поле',
                'required': as_bool(request.POST.get('required')),
                'visible': as_bool(request.POST.get('visible')),
                'order': int(request.POST.get('order') or 100),
            })
            runtime['form_fields'] = sorted(runtime['form_fields'], key=lambda x: int(x.get('order', 100)))
            save_runtime_settings(runtime)
            messages.success(request, 'Поле формы сохранено')

        elif action == 'delete_field':
            runtime['form_fields'] = [x for x in runtime['form_fields'] if str(x.get('id')) != str(request.POST.get('id'))]
            save_runtime_settings(runtime)
            messages.success(request, 'Поле формы удалено')

        return redirect('settings_dashboard')

    for user in User.objects.all():
        UserProfile.objects.get_or_create(user=user)

    return render(request, 'crm/settings.html', {
        'company': company,
        'users': User.objects.select_related('profile').order_by('username'),
        'role_choices': UserProfile.ROLE_CHOICES,
        'locations': runtime['locations'],
        'statuses': runtime['statuses'],
        'form_fields': runtime['form_fields'],
        'device_groups': DeviceGroup.objects.order_by('name'),
        'device_brands': DeviceBrand.objects.order_by('name'),
        'device_models': DeviceModel.objects.select_related('brand').order_by('name'),
        'ad_campaigns': AdCampaign.objects.order_by('name'),
    })
