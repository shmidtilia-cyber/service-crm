from datetime import datetime, timedelta
from decimal import Decimal

from django.db.models import Count, Sum
from django.shortcuts import render
from django.utils import timezone

from .models import Order, OrderPayment, AdCampaign


def _period(request):
    today = timezone.localdate()
    start_raw = request.GET.get('start')
    end_raw = request.GET.get('end')
    if start_raw and end_raw:
        try:
            start = datetime.strptime(start_raw, '%Y-%m-%d').date()
            end = datetime.strptime(end_raw, '%Y-%m-%d').date()
            return start, end
        except ValueError:
            pass
    return today - timedelta(days=30), today


def reports_dashboard(request):
    start, end = _period(request)
    end_next = end + timedelta(days=1)

    payments = OrderPayment.objects.select_related('order', 'order__customer').filter(
        created_at__date__gte=start,
        created_at__date__lt=end_next,
    ).order_by('-created_at')

    finance_income = payments.filter(payment_type='income').aggregate(total=Sum('amount'))['total'] or Decimal('0')
    finance_expense = payments.filter(payment_type='expense').aggregate(total=Sum('amount'))['total'] or Decimal('0')

    orders_period = Order.objects.select_related('customer', 'manager', 'executor', 'ad_campaign').filter(
        created_at__date__gte=start,
        created_at__date__lt=end_next,
    )
    closed_orders = Order.objects.select_related('customer', 'manager', 'executor', 'ad_campaign').filter(
        updated_at__date__gte=start,
        updated_at__date__lt=end_next,
        status__in=['completed', 'cancelled'],
    )
    work_orders = Order.objects.select_related('customer', 'manager', 'executor', 'ad_campaign').exclude(
        status__in=['completed', 'cancelled']
    )

    ad_rows = []
    campaigns = AdCampaign.objects.order_by('name')
    for campaign in campaigns:
        qs = Order.objects.filter(
            ad_campaign=campaign,
            created_at__date__gte=start,
            created_at__date__lt=end_next,
        )
        count = qs.count()
        revenue = qs.aggregate(total=Sum('total_price'))['total'] or Decimal('0')
        profit = qs.aggregate(total=Sum('profit'))['total'] or Decimal('0')
        closed = qs.filter(status='completed').count()
        avg = revenue / count if count else Decimal('0')
        ad_rows.append({
            'campaign': campaign,
            'count': count,
            'closed': closed,
            'in_work': qs.exclude(status__in=['completed', 'cancelled']).count(),
            'cancelled': qs.filter(status='cancelled').count(),
            'revenue': revenue,
            'profit': profit,
            'avg': avg,
        })

    return render(request, 'crm/reports.html', {
        'start': start,
        'end': end,
        'payments': payments[:300],
        'finance_income': finance_income,
        'finance_expense': finance_expense,
        'finance_balance': finance_income - finance_expense,
        'orders_created': orders_period.order_by('-created_at')[:300],
        'orders_closed': closed_orders.order_by('-updated_at')[:300],
        'orders_work': work_orders.order_by('-updated_at')[:300],
        'orders_created_count': orders_period.count(),
        'orders_closed_count': closed_orders.count(),
        'orders_work_count': work_orders.count(),
        'ad_rows': ad_rows,
    })
