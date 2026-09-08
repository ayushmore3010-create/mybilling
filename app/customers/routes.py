from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.customers import customers_bp
from app.models import db, Shop, Customer, Invoice

@customers_bp.route('/')
@login_required
def index():
    shop = Shop.query.filter_by(user_id=current_user.id).first_or_404()
    search_query = request.args.get('q', '').strip()

    query = Customer.query.filter_by(shop_id=shop.id)

    if search_query:
        query = query.filter(
            Customer.name.ilike(f"%{search_query}%") |
            Customer.mobile.ilike(f"%{search_query}%") |
            Customer.email.ilike(f"%{search_query}%")
        )

    customers = query.order_by(Customer.created_at.desc()).all()
    return render_template('customers/index.html', customers=customers, search_query=search_query)


@customers_bp.route('/add', methods=['POST'])
@login_required
def add():
    shop = Shop.query.filter_by(user_id=current_user.id).first_or_404()

    name = request.form.get('name', '').strip()
    mobile = request.form.get('mobile', '').strip()
    whatsapp = request.form.get('whatsapp', '').strip() or mobile
    email = request.form.get('email', '').strip() or None
    address = request.form.get('address', '').strip() or None

    if not name or not mobile:
        flash('Customer Name and Mobile Number are required.', 'danger')
        return redirect(url_for('customers.index'))

    customer = Customer(
        shop_id=shop.id,
        name=name,
        mobile=mobile,
        whatsapp=whatsapp,
        email=email,
        address=address
    )
    db.session.add(customer)
    db.session.commit()

    flash(f'Customer "{name}" added successfully.', 'success')
    return redirect(url_for('customers.index'))


@customers_bp.route('/edit/<int:customer_id>', methods=['POST'])
@login_required
def edit(customer_id):
    shop = Shop.query.filter_by(user_id=current_user.id).first_or_404()
    customer = Customer.query.filter_by(id=customer_id, shop_id=shop.id).first_or_404()

    customer.name = request.form.get('name', '').strip()
    customer.mobile = request.form.get('mobile', '').strip()
    customer.whatsapp = request.form.get('whatsapp', '').strip() or customer.mobile
    customer.email = request.form.get('email', '').strip() or None
    customer.address = request.form.get('address', '').strip() or None

    db.session.commit()
    flash(f'Customer "{customer.name}" updated successfully.', 'success')
    return redirect(url_for('customers.index'))


@customers_bp.route('/delete/<int:customer_id>', methods=['POST'])
@login_required
def delete(customer_id):
    shop = Shop.query.filter_by(user_id=current_user.id).first_or_404()
    customer = Customer.query.filter_by(id=customer_id, shop_id=shop.id).first_or_404()

    name = customer.name
    db.session.delete(customer)
    db.session.commit()

    flash(f'Customer "{name}" deleted.', 'info')
    return redirect(url_for('customers.index'))


@customers_bp.route('/api/search')
@login_required
def api_search():
    shop = Shop.query.filter_by(user_id=current_user.id).first_or_404()
    query_str = request.args.get('q', '').strip()

    customers = Customer.query.filter(
        Customer.shop_id == shop.id,
        (Customer.name.ilike(f"%{query_str}%")) | (Customer.mobile.ilike(f"%{query_str}%"))
    ).limit(10).all()

    return jsonify([{
        'id': c.id,
        'name': c.name,
        'mobile': c.mobile,
        'whatsapp': c.whatsapp or c.mobile,
        'address': c.address or ''
    } for c in customers])
