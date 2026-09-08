from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.products import products_bp
from app.models import db, Shop, Product, Category

@products_bp.route('/')
@login_required
def index():
    shop = Shop.query.filter_by(user_id=current_user.id).first_or_404()
    
    category_id = request.args.get('category_id', type=int)
    search_query = request.args.get('q', '').strip()

    query = Product.query.filter_by(shop_id=shop.id)

    if category_id:
        query = query.filter_by(category_id=category_id)

    if search_query:
        query = query.filter(Product.name.ilike(f"%{search_query}%") | Product.sku.ilike(f"%{search_query}%"))

    products = query.order_by(Product.name.asc()).all()
    categories = Category.query.filter_by(shop_id=shop.id).all()

    return render_template('products/index.html', products=products, categories=categories, current_category=category_id, search_query=search_query)


@products_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    shop = Shop.query.filter_by(user_id=current_user.id).first_or_404()
    categories = Category.query.filter_by(shop_id=shop.id).all()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        sku = request.form.get('sku', '').strip()
        category_id = request.form.get('category_id', type=int)
        new_category = request.form.get('new_category', '').strip()
        purchase_price = request.form.get('purchase_price', type=float, default=0.0)
        selling_price = request.form.get('selling_price', type=float, default=0.0)
        gst_rate = request.form.get('gst_rate', type=float, default=0.0)
        stock_qty = request.form.get('stock_qty', type=float, default=0.0)
        unit = request.form.get('unit', 'Piece').strip()

        if not name or selling_price < 0:
            flash('Product name and valid selling price are required.', 'danger')
            return redirect(url_for('products.index'))

        # If user created a new category on the fly
        if new_category:
            existing_cat = Category.query.filter_by(shop_id=shop.id, name=new_category).first()
            if not existing_cat:
                existing_cat = Category(shop_id=shop.id, name=new_category)
                db.session.add(existing_cat)
                db.session.commit()
            category_id = existing_cat.id

        product = Product(
            shop_id=shop.id,
            category_id=category_id,
            name=name,
            sku=sku if sku else None,
            purchase_price=purchase_price,
            selling_price=selling_price,
            gst_rate=gst_rate,
            stock_qty=stock_qty,
            unit=unit
        )
        db.session.add(product)
        db.session.commit()

        flash(f'Product "{name}" added successfully.', 'success')
        return redirect(url_for('products.index'))

    return redirect(url_for('products.index'))


@products_bp.route('/edit/<int:product_id>', methods=['POST'])
@login_required
def edit(product_id):
    shop = Shop.query.filter_by(user_id=current_user.id).first_or_404()
    product = Product.query.filter_by(id=product_id, shop_id=shop.id).first_or_404()

    product.name = request.form.get('name', '').strip()
    product.sku = request.form.get('sku', '').strip() or None
    product.category_id = request.form.get('category_id', type=int)
    product.purchase_price = request.form.get('purchase_price', type=float, default=0.0)
    product.selling_price = request.form.get('selling_price', type=float, default=0.0)
    product.gst_rate = request.form.get('gst_rate', type=float, default=0.0)
    product.stock_qty = request.form.get('stock_qty', type=float, default=0.0)
    product.unit = request.form.get('unit', 'Piece').strip()

    db.session.commit()
    flash(f'Product "{product.name}" updated successfully.', 'success')
    return redirect(url_for('products.index'))


@products_bp.route('/delete/<int:product_id>', methods=['POST'])
@login_required
def delete(product_id):
    shop = Shop.query.filter_by(user_id=current_user.id).first_or_404()
    product = Product.query.filter_by(id=product_id, shop_id=shop.id).first_or_404()

    name = product.name
    db.session.delete(product)
    db.session.commit()

    flash(f'Product "{name}" deleted.', 'info')
    return redirect(url_for('products.index'))


@products_bp.route('/api/search')
@login_required
def api_search():
    shop = Shop.query.filter_by(user_id=current_user.id).first_or_404()
    query_str = request.args.get('q', '').strip()

    products = Product.query.filter(
        Product.shop_id == shop.id,
        Product.name.ilike(f"%{query_str}%") | Product.sku.ilike(f"%{query_str}%")
    ).limit(20).all()

    return jsonify([{
        'id': p.id,
        'name': p.name,
        'sku': p.sku or '',
        'selling_price': p.selling_price,
        'gst_rate': p.gst_rate,
        'stock_qty': p.stock_qty,
        'unit': p.unit
    } for p in products])
