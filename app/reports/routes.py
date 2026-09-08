import csv
import io
from datetime import datetime, timedelta
from flask import render_template, redirect, url_for, request, Response
from flask_login import login_required, current_user
from sqlalchemy import func
from app.reports import reports_bp
from app.models import db, Shop, Invoice, InvoiceItem, Product

@reports_bp.route('/')
@login_required
def index():
    shop = Shop.query.filter_by(user_id=current_user.id).first_or_404()

    # Total stats
    total_revenue = db.session.query(func.coalesce(func.sum(Invoice.grand_total), 0.0)).filter(Invoice.shop_id == shop.id).scalar()
    total_tax_collected = db.session.query(func.coalesce(func.sum(Invoice.total_tax), 0.0)).filter(Invoice.shop_id == shop.id).scalar()
    total_invoices_count = Invoice.query.filter_by(shop_id=shop.id).count()

    # GST Breakdown
    total_cgst = db.session.query(func.coalesce(func.sum(Invoice.cgst_amount), 0.0)).filter(Invoice.shop_id == shop.id).scalar()
    total_sgst = db.session.query(func.coalesce(func.sum(Invoice.sgst_amount), 0.0)).filter(Invoice.shop_id == shop.id).scalar()
    total_igst = db.session.query(func.coalesce(func.sum(Invoice.igst_amount), 0.0)).filter(Invoice.shop_id == shop.id).scalar()

    # Payment Methods summary
    pm_stats = db.session.query(
        Invoice.payment_method,
        func.count(Invoice.id),
        func.sum(Invoice.grand_total)
    ).filter(Invoice.shop_id == shop.id).group_by(Invoice.payment_method).all()

    # Top selling items
    top_items = db.session.query(
        InvoiceItem.product_name,
        func.sum(InvoiceItem.quantity).label('total_qty'),
        func.sum(InvoiceItem.line_total).label('total_revenue')
    ).join(Invoice).filter(Invoice.shop_id == shop.id)\
     .group_by(InvoiceItem.product_name)\
     .order_by(func.sum(InvoiceItem.line_total).desc()).limit(10).all()

    return render_template(
        'reports/index.html',
        shop=shop,
        total_revenue=total_revenue,
        total_tax_collected=total_tax_collected,
        total_invoices_count=total_invoices_count,
        total_cgst=total_cgst,
        total_sgst=total_sgst,
        total_igst=total_igst,
        pm_stats=pm_stats,
        top_items=top_items
    )


@reports_bp.route('/export/csv')
@login_required
def export_csv():
    shop = Shop.query.filter_by(user_id=current_user.id).first_or_404()
    invoices = Invoice.query.filter_by(shop_id=shop.id).order_by(Invoice.invoice_date.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Invoice Number', 'Date', 'Customer', 'Subtotal', 'Discount', 'Taxable Amount', 'CGST', 'SGST', 'IGST', 'Total Tax', 'Grand Total', 'Payment Method', 'Payment Status'])

    for inv in invoices:
        cust_name = inv.customer_rel.name if inv.customer_rel else "Walk-in Customer"
        writer.writerow([
            inv.invoice_number,
            inv.invoice_date.strftime('%Y-%m-%d %H:%M'),
            cust_name,
            f"{inv.subtotal:.2f}",
            f"{inv.discount_amount:.2f}",
            f"{inv.taxable_amount:.2f}",
            f"{inv.cgst_amount:.2f}",
            f"{inv.sgst_amount:.2f}",
            f"{inv.igst_amount:.2f}",
            f"{inv.total_tax:.2f}",
            f"{inv.grand_total:.2f}",
            inv.payment_method,
            inv.payment_status
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename=sales_report_{shop.shop_name.replace(' ', '_')}.csv"}
    )
