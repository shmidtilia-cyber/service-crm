from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Sum
from django.shortcuts import redirect, render

from .models import Order, OrderEvent, OrderPayment


def parse_amount(value):
    try:
        return Decimal(str(value or '0').replace(',', '.'))
    except Exception:
        return Decimal('0')


def finance_dashboard(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action in ['salary_payout', 'salary_deduction']:
            employee = User.objects.filter(id=request.POST.get('user_id')).first()
            order = Order.objects.order_by('-created_at').first()
            amount = parse_amount(request.POST.get('amount'))

            if not employee or not order or amount <= 0:
                messages.error(request, 'Укажите сотрудника и сумму')
                return redirect('finance_dashboard')

            if action == 'salary_payout':
                comment = f'Выплата зарплаты: {employee.username}'
            else:
                comment = f'Штраф сотруднику: {employee.username}'

            OrderPayment.objects.create(
                order=order,
                payment_type='expense',
                cashbox=request.POST.get('cashbox') or 'cash',
                amount=amount,
                comment=comment,
            )
            OrderEvent.objects.create(order=order, text=comment)
            messages.success(request, 'Операция по зарплате сохранена')
            return redirect('finance_dashboard')

        order = Order.objects.filter(id=request.POST.get('order_id')).first()
        if not order:
            messages.error(request, 'Укажите заказ')
            return redirect('finance_dashboard')

        amount = parse_amount(request.POST.get('amount'))
        if amount <= 0:
            messages.error(request, 'Сумма должна быть больше 0')
            return redirect('finance_dashboard')

        cashbox = request.POST.get('cashbox') or 'cash'
        comment = request.POST.get('comment', '').strip()

        if action == 'expense':
            payment_type = 'expense'
            order.total_cost = (order.total_cost or Decimal('0')) + amount
            order.save(update_fields=['total_cost', 'updated_at'])
            order.recalculate_money()
        else:
            payment_type = 'income'

        payment = OrderPayment.objects.create(
            order=order,
            payment_type=payment_type,
            cashbox=cashbox,
            amount=amount,
            comment=comment,
        )
        OrderEvent.objects.create(order=order, text=comment or str(payment))
        messages.success(request, 'Финансовая операция добавлена')
        return redirect('finance_dashboard')

    payments = OrderPayment.objects.select_related('order', 'order__customer').order_by('-created_at')[:200]
    orders = Order.objects.select_related('customer').order_by('-created_at')[:200]

    cash_income = OrderPayment.objects.filter(cashbox='cash', payment_type='income').aggregate(total=Sum('amount'))['total'] or Decimal('0')
    cash_expense = OrderPayment.objects.filter(cashbox='cash', payment_type='expense').aggregate(total=Sum('amount'))['total'] or Decimal('0')
    card_income = OrderPayment.objects.filter(cashbox='card', payment_type='income').aggregate(total=Sum('amount'))['total'] or Decimal('0')
    card_expense = OrderPayment.objects.filter(cashbox='card', payment_type='expense').aggregate(total=Sum('amount'))['total'] or Decimal('0')

    salary_rows = []
    for employee in User.objects.order_by('username'):
        master_salary = Order.objects.filter(executor=employee).aggregate(total=Sum('master_salary'))['total'] or Decimal('0')
        manager_salary = Order.objects.filter(manager=employee).aggregate(total=Sum('manager_salary'))['total'] or Decimal('0')
        accrued = master_salary + manager_salary
        paid = OrderPayment.objects.filter(payment_type='expense', comment__startswith=f'Выплата зарплаты: {employee.username}').aggregate(total=Sum('amount'))['total'] or Decimal('0')
        deductions = OrderPayment.objects.filter(payment_type='expense', comment__startswith=f'Штраф сотруднику: {employee.username}').aggregate(total=Sum('amount'))['total'] or Decimal('0')
        salary_rows.append({
            'user': employee,
            'master_salary': master_salary,
            'manager_salary': manager_salary,
            'accrued': accrued,
            'paid': paid,
            'fines': deductions,
            'balance': accrued - paid - deductions,
        })

    return render(request, 'crm/finance.html', {
        'payments': payments,
        'orders': orders,
        'cash_balance': cash_income - cash_expense,
        'card_balance': card_income - card_expense,
        'total_income': cash_income + card_income,
        'total_expense': cash_expense + card_expense,
        'salary_rows': salary_rows,
    })
