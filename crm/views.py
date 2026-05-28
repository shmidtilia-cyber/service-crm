from django.db.models import Sum
from django.shortcuts import render

from .models import Customer, Order, Product


def dashboard(request):
    orders = (
        Order.objects.select_related('customer', 'device_group', 'device_brand', 'device_model')
        .order_by('-created_at')[:10]
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
    })
