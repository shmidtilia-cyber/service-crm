from decimal import Decimal
import random
import string

from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Администратор'),
        ('manager', 'Менеджер'),
        ('master', 'Мастер'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField('Роль', max_length=30, choices=ROLE_CHOICES, default='manager')
    full_name = models.CharField('ФИО', max_length=255, blank=True)
    position = models.CharField('Должность', max_length=255, blank=True)
    phone = models.CharField('Телефон', max_length=50, blank=True)
    can_manage_users = models.BooleanField('Может управлять пользователями', default=False)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    def __str__(self):
        return f'{self.user.username} — {self.get_role_display()}'


class Category(models.Model):
    name = models.CharField('Название категории', max_length=255, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField('Название товара', max_length=255)
    sku = models.CharField('Артикул', max_length=100, unique=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    purchase_price = models.DecimalField('Закупочная цена', max_digits=12, decimal_places=2, default=0)
    sale_price = models.DecimalField('Розничная цена', max_digits=12, decimal_places=2, default=0)
    quantity = models.PositiveIntegerField('Количество', default=0)
    image = models.ImageField('Фото', upload_to='products/', blank=True, null=True)
    description = models.TextField('Описание', blank=True)
    created_at = models.DateTimeField('Дата добавления', auto_now_add=True)

    def __str__(self):
        return f'{self.name} ({self.sku})'


class Customer(models.Model):
    name = models.CharField('Имя', max_length=255)
    phone = models.CharField('Телефон', max_length=50, blank=True)
    email = models.EmailField('Email', blank=True)
    address = models.CharField('Адрес', max_length=255, blank=True)
    comment = models.TextField('Комментарий', blank=True)

    def __str__(self):
        return self.name


class DeviceGroup(models.Model):
    name = models.CharField('Тип техники', max_length=255, unique=True)

    def __str__(self):
        return self.name


class DeviceBrand(models.Model):
    name = models.CharField('Бренд', max_length=255, unique=True)

    def __str__(self):
        return self.name


class DeviceModel(models.Model):
    name = models.CharField('Модель', max_length=255, unique=True)
    brand = models.ForeignKey(DeviceBrand, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name


class AdCampaign(models.Model):
    name = models.CharField('Рекламная кампания', max_length=255, unique=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    ORDER_TYPE_CHOICES = [
        ('Выездной', 'Выездной'),
        ('Гарантий', 'Гарантий'),
        ('Доставка', 'Доставка'),
        ('ЗАКАЗ', 'ЗАКАЗ'),
        ('Принят в СЦ', 'Принят в СЦ'),
    ]

    ORDER_STATUS_CHOICES = [
        ('new', 'Новый'),
        ('in_work', 'В работе'),
        ('assembled', 'Собран'),
        ('sent', 'Отправлен'),
        ('completed', 'Завершен'),
        ('cancelled', 'Отменен'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('not_paid', 'Не оплачен'),
        ('part_paid', 'Частично оплачен'),
        ('paid', 'Оплачен'),
    ]

    order_number = models.CharField('Номер заказа', max_length=50, unique=True, blank=True)
    order_type = models.CharField('Тип заказа', max_length=50, choices=ORDER_TYPE_CHOICES, default='ЗАКАЗ')
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_orders')
    executor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='executed_orders')
    serial_number = models.CharField('Серийный номер / IMEI', max_length=255, blank=True)
    device_group = models.ForeignKey(DeviceGroup, on_delete=models.SET_NULL, null=True, blank=True)
    device_brand = models.ForeignKey(DeviceBrand, on_delete=models.SET_NULL, null=True, blank=True)
    device_model = models.ForeignKey(DeviceModel, on_delete=models.SET_NULL, null=True, blank=True)
    condition = models.TextField('Состояние', default='Потертости, царапины')
    issue = models.TextField('Неисправность', blank=True)
    password = models.CharField('Пароль', max_length=255, blank=True)
    ad_campaign = models.ForeignKey(AdCampaign, on_delete=models.SET_NULL, null=True, blank=True)
    manager_notes = models.TextField('Заметки менеджера', blank=True)
    estimated_price = models.DecimalField('Ориентировочная цена', max_digits=12, decimal_places=2, default=0)
    prepayment = models.DecimalField('Предоплата', max_digits=12, decimal_places=2, default=0)
    urgent = models.BooleanField('Срочно', default=False)
    deadline = models.DateTimeField('Крайний срок', null=True, blank=True)
    total_price = models.DecimalField('Сумма заказа', max_digits=12, decimal_places=2, default=0)
    total_cost = models.DecimalField('Затраты по заказу', max_digits=12, decimal_places=2, default=0)
    profit = models.DecimalField('Прибыль', max_digits=12, decimal_places=2, default=0)
    master_salary = models.DecimalField('Зарплата мастера', max_digits=12, decimal_places=2, default=0)
    manager_salary = models.DecimalField('Зарплата менеджера', max_digits=12, decimal_places=2, default=0)
    status = models.CharField('Статус заказа', max_length=30, choices=ORDER_STATUS_CHOICES, default='new')
    payment_status = models.CharField('Статус оплаты', max_length=30, choices=PAYMENT_STATUS_CHOICES, default='not_paid')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    def save(self, *args, **kwargs):
        if not self.order_number:
            last_order = Order.objects.order_by('-id').first()
            last_number = 999
            if last_order and last_order.order_number.startswith('F'):
                try:
                    last_number = int(last_order.order_number.replace('F', ''))
                except ValueError:
                    last_number = 999
            self.order_number = f'F{last_number + 1}'
        super().save(*args, **kwargs)

    @staticmethod
    def generate_serial():
        letters = ''.join(random.choices(string.ascii_uppercase, k=3))
        numbers = ''.join(random.choices(string.digits, k=9))
        return f'{letters}{numbers}'

    def recalculate_money(self):
        services = self.services.all()
        total_price = sum((service.total for service in services), Decimal('0'))
        total_cost = sum((service.total_cost for service in services), Decimal('0'))
        profit_before_salary = max(total_price - total_cost, Decimal('0'))
        master_salary = profit_before_salary * Decimal('0.15')
        manager_base = max(profit_before_salary - master_salary, Decimal('0'))
        manager_salary = manager_base * Decimal('0.15')
        final_profit = profit_before_salary - master_salary - manager_salary
        self.total_price = total_price
        self.total_cost = total_cost
        self.master_salary = master_salary
        self.manager_salary = manager_salary
        self.profit = final_profit
        self.save(update_fields=['total_price', 'total_cost', 'master_salary', 'manager_salary', 'profit', 'updated_at'])

    def __str__(self):
        return self.order_number


class OrderService(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='services')
    name = models.CharField('Услуга', max_length=255)
    price = models.DecimalField('Цена', max_digits=12, decimal_places=2, default=0)
    cost_price = models.DecimalField('Себестоимость', max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField('Скидка', max_digits=12, decimal_places=2, default=0)
    warranty_days = models.PositiveIntegerField('Гарантия, дней', default=0)
    quantity = models.PositiveIntegerField('Количество', default=1)
    executor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Исполнитель')
    created_at = models.DateTimeField('Дата добавления', auto_now_add=True)

    @property
    def total(self):
        total = (self.price * self.quantity) - self.discount
        return total if total > 0 else Decimal('0')

    @property
    def total_cost(self):
        return self.cost_price * self.quantity

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.order.recalculate_money()

    def delete(self, *args, **kwargs):
        order = self.order
        super().delete(*args, **kwargs)
        order.recalculate_money()

    def __str__(self):
        return self.name


class OrderPayment(models.Model):
    PAYMENT_TYPE_CHOICES = [('income', 'Приход'), ('expense', 'Расход')]
    CASHBOX_CHOICES = [('cash', 'Наличные'), ('card', 'Безналичные')]
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    payment_type = models.CharField('Тип операции', max_length=20, choices=PAYMENT_TYPE_CHOICES)
    cashbox = models.CharField('Касса', max_length=20, choices=CASHBOX_CHOICES, default='cash')
    amount = models.DecimalField('Сумма', max_digits=12, decimal_places=2)
    comment = models.CharField('Комментарий', max_length=255, blank=True)
    created_at = models.DateTimeField('Дата', auto_now_add=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            sign = 'приход' if self.payment_type == 'income' else 'расход'
            OrderEvent.objects.create(order=self.order, text=f'Добавлена финансовая операция: {sign} {self.amount} ₽')

    def __str__(self):
        return f'{self.get_payment_type_display()} {self.amount}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField('Количество', default=1)
    price = models.DecimalField('Цена', max_digits=12, decimal_places=2, default=0)
    subtotal = models.DecimalField('Сумма', max_digits=12, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.product.sale_price
        self.subtotal = self.price * self.quantity
        super().save(*args, **kwargs)


class OrderEvent(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='events')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    text = models.TextField('Событие')
    created_at = models.DateTimeField('Дата', auto_now_add=True)

    def __str__(self):
        return self.text


class OrderComment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    text = models.TextField('Комментарий')
    created_at = models.DateTimeField('Дата', auto_now_add=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            OrderEvent.objects.create(order=self.order, user=self.user, text=f'Комментарий: {self.text}')

    def __str__(self):
        return self.text


class CompanySettings(models.Model):
    shop_name = models.CharField('Название CRM', max_length=255, default='Fadeev-CRM')
    logo = models.ImageField('Логотип', upload_to='settings/', blank=True, null=True)
    currency = models.CharField('Валюта', max_length=20, default='₽')
    min_stock = models.PositiveIntegerField('Минимальный остаток', default=3)
    company_name = models.CharField('Название компании', max_length=255, blank=True)
    company_info = models.TextField('Данные компании', blank=True)
    order_prefix = models.CharField('Префикс номера заказа', max_length=10, default='F')
    order_start_number = models.PositiveIntegerField('Начальный номер заказа', default=1000)

    def __str__(self):
        return self.shop_name
