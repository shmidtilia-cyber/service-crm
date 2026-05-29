from decimal import Decimal

from django.contrib import messages
from django.db.models import Sum
from django.shortcuts import redirect, render

from .models import Order, OrderEvent, OrderPayment


def finance_dashboard(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        order = Order.objects.filter(id=request.POST.get('order_id')).first()
        if not order:
            messages.error(request, 'Укажите заказ')
            return redirect('finance_dashboard')

        try:
            amount = Decimal(str(request.POST.get('amount') or '0').replace(',', '.'))
        except Exception:
            amount = Decimal('0')

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

    return render(request, 'crm/finance.html', {
        'payments': payments,
        'orders': orders,
        'cash_balance': cash_income - cash_expense,
        'card_balance': card_income - card_expense,
        'total_income': cash_income + card_income,
        'total_expense': cash_expense + card_expense,
    })
