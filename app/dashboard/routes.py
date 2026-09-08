from datetime import datetime, timedelta
from flask import render_template, redirect, url_for, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func
from app.dashboard import dashboard_bp
from app.models import db, Shop, Product, Customer, Invoice, InvoiceItem

@dashboard_bp.route('/')
@login_required
def index():
    shop = Shop.query.filter_by(user_id=current_user.id).first()
    if not shop:
        return redirect(url_for('shop.setup'))

    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    # 1. Today's sales
    todays_sales = db.session.query(func.coalesce(func.sum(Invoice.grand_total), 0.0))\
        .filter(Invoice.shop_id == shop.id, Invoice.created_at >= today_start).scalar()

    # 2. Total sales
    total_sales = db.session.query(func.coalesce(func.sum(Invoice.grand_total), 0.0))\
        .filter(Invoice.shop_id == shop.id).scalar()

    # 3. Today's bills count
    todays_bills = Invoice.query.filter(Invoice.shop_id == shop.id, Invoice.created_at >= today_start).count()

    # 4. Total customers
    total_customers = Customer.query.filter_by(shop_id=shop.id).count()

    # 5. Total products
    total_products = Product.query.filter_by(shop_id=shop.id).count()

    # 6. Recent Invoices
    recent_invoices = Invoice.query.filter_by(shop_id=shop.id)\
        .order_by(Invoice.created_at.desc()).limit(5).all()

    # 7. Low stock products (quantity <= 5)
    low_stock_products = Product.query.filter(Product.shop_id == shop.id, Product.stock_qty <= 5)\
        .order_by(Product.stock_qty.asc()).limit(5).all()

    # 8. Sales Chart Data for last 7 days
    dates = []
    daily_totals = []
    for i in range(6, -1, -1):
        day_date = datetime.utcnow().date() - timedelta(days=i)
        day_start = datetime.combine(day_date, datetime.min.time())
        day_end = datetime.combine(day_date, datetime.max.time())
        
        day_sum = db.session.query(func.coalesce(func.sum(Invoice.grand_total), 0.0))\
            .filter(Invoice.shop_id == shop.id, Invoice.created_at >= day_start, Invoice.created_at <= day_end).scalar()
            
        dates.append(day_date.strftime('%b %d'))
        daily_totals.append(round(day_sum, 2))

    return render_template(
        'dashboard/index.html',
        shop=shop,
        todays_sales=todays_sales,
        total_sales=total_sales,
        todays_bills=todays_bills,
        total_customers=total_customers,
        total_products=total_products,
        recent_invoices=recent_invoices,
        low_stock_products=low_stock_products,
        chart_dates=dates,
        chart_totals=daily_totals
    )
