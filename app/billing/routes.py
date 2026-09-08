import uuid
from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from sqlalchemy import func
from app.billing import billing_bp
from app.models import db, Shop, Product, Customer, Invoice, InvoiceItem
from app.utils.helpers import generate_whatsapp_link

def get_next_invoice_number(shop):
    prefix = shop.invoice_prefix or 'INV-'
    count = Invoice.query.filter_by(shop_id=shop.id).count()
    return f"{prefix}{count + 1:06d}"

@billing_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    shop = Shop.query.filter_by(user_id=current_user.id).first_or_404()

    if request.method == 'POST':
        customer_id = request.form.get('customer_id', type=int)
        cust_name = request.form.get('customer_name', '').strip()
        cust_mobile = request.form.get('customer_mobile', '').strip()
        cust_whatsapp = request.form.get('customer_whatsapp', '').strip() or cust_mobile
        cust_address = request.form.get('customer_address', '').strip()

        # Quick customer creation/retrieval
        customer = None
        if customer_id:
            customer = Customer.query.filter_by(id=customer_id, shop_id=shop.id).first()
        elif cust_name and cust_mobile:
            customer = Customer.query.filter_by(shop_id=shop.id, mobile=cust_mobile).first()
            if not customer:
                customer = Customer(
                    shop_id=shop.id,
                    name=cust_name,
                    mobile=cust_mobile,
                    whatsapp=cust_whatsapp,
                    address=cust_address
                )
                db.session.add(customer)
                db.session.flush()

        payment_method = request.form.get('payment_method', 'Cash')
        payment_status = request.form.get('payment_status', 'Paid')
        notes = request.form.get('notes', '').strip()

        # Product lines from POST
        product_ids = request.form.getlist('product_id[]')
        product_names = request.form.getlist('product_name[]')
        quantities = request.form.getlist('quantity[]')
        units = request.form.getlist('unit[]')
        rates = request.form.getlist('rate[]')
        discounts = request.form.getlist('discount[]')
        gst_rates = request.form.getlist('gst_rate[]')

        if not product_names or len(product_names) == 0:
            flash('Please add at least one product to create a bill.', 'danger')
            return redirect(url_for('billing.create'))

        invoice_number = get_next_invoice_number(shop)
        secure_token = str(uuid.uuid4())

        subtotal = 0.0
        total_discount = 0.0
        taxable_amount = 0.0
        total_tax = 0.0

        invoice_items = []

        for i in range(len(product_names)):
            p_name = product_names[i].strip()
            if not p_name:
                continue
                
            qty = float(quantities[i]) if i < len(quantities) and quantities[i] else 1.0
            unit = units[i] if i < len(units) and units[i] else 'Piece'
            rate = float(rates[i]) if i < len(rates) and rates[i] else 0.0
            disc = float(discounts[i]) if i < len(discounts) and discounts[i] else 0.0
            gst = float(gst_rates[i]) if i < len(gst_rates) and gst_rates[i] else 0.0

            line_gross = qty * rate
            line_disc_val = (line_gross * (disc / 100.0)) if disc <= 100 else disc
            line_taxable = line_gross - line_disc_val
            line_tax_val = line_taxable * (gst / 100.0)
            line_total_val = line_taxable + line_tax_val

            subtotal += line_gross
            total_discount += line_disc_val
            taxable_amount += line_taxable
            total_tax += line_tax_val

            p_id = int(product_ids[i]) if i < len(product_ids) and product_ids[i].isdigit() else None
            
            # Stock deduction if product exists
            if p_id:
                product_obj = Product.query.filter_by(id=p_id, shop_id=shop.id).first()
                if product_obj:
                    product_obj.stock_qty = max(0.0, product_obj.stock_qty - qty)

            item = InvoiceItem(
                product_id=p_id,
                product_name=p_name,
                quantity=qty,
                unit=unit,
                rate=rate,
                discount=disc,
                gst_rate=gst,
                line_tax=line_tax_val,
                line_total=line_total_val
            )
            invoice_items.append(item)

        cgst = total_tax / 2.0
        sgst = total_tax / 2.0
        igst = 0.0  # Default intra-state GST split
        grand_total = taxable_amount + total_tax

        invoice = Invoice(
            shop_id=shop.id,
            customer_id=customer.id if customer else None,
            invoice_number=invoice_number,
            secure_token=secure_token,
            subtotal=subtotal,
            discount_amount=total_discount,
            taxable_amount=taxable_amount,
            total_tax=total_tax,
            cgst_amount=cgst,
            sgst_amount=sgst,
            igst_amount=igst,
            grand_total=grand_total,
            payment_method=payment_method,
            payment_status=payment_status,
            amount_paid=grand_total if payment_status == 'Paid' else 0.0,
            notes=notes,
            items=invoice_items
        )

        db.session.add(invoice)

        # Update customer stats
        if customer:
            customer.total_spent = (customer.total_spent or 0.0) + grand_total
            customer.total_invoices = (customer.total_invoices or 0) + 1

        db.session.commit()

        flash(f'Invoice {invoice_number} created successfully!', 'success')
        return redirect(url_for('billing.view_invoice', invoice_id=invoice.id))

    next_inv_no = get_next_invoice_number(shop)
    products = Product.query.filter_by(shop_id=shop.id).order_by(Product.name.asc()).all()
    customers = Customer.query.filter_by(shop_id=shop.id).order_by(Customer.name.asc()).all()

    return render_template('billing/create.html', shop=shop, next_inv_no=next_inv_no, products=products, customers=customers)


@billing_bp.route('/history')
@login_required
def history():
    shop = Shop.query.filter_by(user_id=current_user.id).first_or_404()
    
    search_q = request.args.get('q', '').strip()
    status_filter = request.args.get('status', '').strip()

    query = Invoice.query.filter_by(shop_id=shop.id)

    if search_q:
        query = query.filter(Invoice.invoice_number.ilike(f"%{search_q}%"))
        
    if status_filter:
        query = query.filter_by(payment_status=status_filter)

    invoices = query.order_by(Invoice.invoice_date.desc()).all()
    
    return render_template('billing/history.html', invoices=invoices, search_q=search_q, status_filter=status_filter)


@billing_bp.route('/view/<int:invoice_id>')
@login_required
def view_invoice(invoice_id):
    shop = Shop.query.filter_by(user_id=current_user.id).first_or_404()
    invoice = Invoice.query.filter_by(id=invoice_id, shop_id=shop.id).first_or_404()

    cust_mobile = invoice.customer_rel.mobile if invoice.customer_rel else ""
    whatsapp_url = generate_whatsapp_link(
        mobile_no=cust_mobile,
        invoice_no=invoice.invoice_number,
        shop_name=shop.shop_name,
        total_amount=invoice.grand_total,
        secure_token=invoice.secure_token,
        request_host=request.host
    )

    return render_template('billing/view_invoice.html', invoice=invoice, shop=shop, whatsapp_url=whatsapp_url)


@billing_bp.route('/delete/<int:invoice_id>', methods=['POST'])
@login_required
def delete_invoice(invoice_id):
    shop = Shop.query.filter_by(user_id=current_user.id).first_or_404()
    invoice = Invoice.query.filter_by(id=invoice_id, shop_id=shop.id).first_or_404()

    inv_no = invoice.invoice_number
    db.session.delete(invoice)
    db.session.commit()

    flash(f'Invoice {inv_no} deleted successfully.', 'info')
    return redirect(url_for('billing.history'))
