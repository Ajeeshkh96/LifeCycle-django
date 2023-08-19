from __future__ import annotations

from .models import Category
from .models import Product
from orders.models import Order


def menu_links(request):
    links = Category.objects.all()
    return dict(links=links)


def menu_links1(request):
    links1 = Product.objects.all()
    return dict(links1=links1)


from django.db.models import Sum, Count
from datetime import datetime, timedelta


def generate_daily_sales_report():
    today = datetime.now()
    start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = today.replace(hour=23, minute=59, second=59, microsecond=999999)

    orders = Order.objects.filter(
        created_at__range=(start_date, end_date)
    ).filter(is_ordered=True)
    total_sales_amount = orders.aggregate(total_sales=Sum("order_total"))[
        "total_sales"
    ]
    total_orders = orders.count()

    print("Daily Sales Report:")
    print("Date:", start_date.strftime("%Y-%m-%d"))
    print("Total Sales Amount:", total_sales_amount)
    print("Total Orders:", total_orders)


def generate_weekly_sales_report():
    today = datetime.now()
    start_date = today - timedelta(days=today.weekday())
    end_date = start_date + timedelta(days=6)

    orders = Order.objects.filter(
        created_at__range=(start_date, end_date)
    ).filter(is_ordered=True)
    total_sales_amount = orders.aggregate(total_sales=Sum("order_total"))[
        "total_sales"
    ]
    total_orders = orders.count()

    print("Weekly Sales Report:")
    print("Start Date:", start_date.strftime("%Y-%m-%d"))
    print("End Date:", end_date.strftime("%Y-%m-%d"))
    print("Total Sales Amount:", total_sales_amount)
    print("Total Orders:", total_orders)


def generate_yearly_sales_report():
    today = datetime.now()
    start_date = today.replace(
        month=1, day=1, hour=0, minute=0, second=0, microsecond=0
    )
    end_date = today.replace(
        month=12, day=31, hour=23, minute=59, second=59, microsecond=999999
    )

    orders = Order.objects.filter(
        created_at__range=(start_date, end_date)
    ).filter(is_ordered=True)
    total_sales_amount = orders.aggregate(total_sales=Sum("order_total"))[
        "total_sales"
    ]
    total_orders = orders.count()

    print("Yearly Sales Report:")
    print("Start Date:", start_date.strftime("%Y-%m-%d"))
    print("End Date:", end_date.strftime("%Y-%m-%d"))
    print("Total Sales Amount:", total_sales_amount)
    print("Total Orders:", total_orders)


if __name__ == "__main__":
    generate_daily_sales_report()
    generate_weekly_sales_report()
    generate_yearly_sales_report()
