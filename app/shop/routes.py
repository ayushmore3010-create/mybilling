import os
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.shop import shop_bp
from app.models import db, Shop

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'svg', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@shop_bp.route('/setup', methods=['GET', 'POST'])
@login_required
def setup():
    existing_shop = Shop.query.filter_by(user_id=current_user.id).first()
    if existing_shop:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        shop_name = request.form.get('shop_name', '').strip()
        owner_name = request.form.get('owner_name', '').strip()
        mobile = request.form.get('mobile', '').strip()
        email = request.form.get('email', '').strip()
        address = request.form.get('address', '').strip()
        city = request.form.get('city', '').strip()
        state = request.form.get('state', '').strip()
        pincode = request.form.get('pincode', '').strip()
        gstin = request.form.get('gstin', '').strip().upper()
        invoice_prefix = request.form.get('invoice_prefix', 'INV-').strip()

        if not shop_name or not owner_name or not mobile or not address:
            flash('Shop Name, Owner Name, Mobile, and Address are required.', 'danger')
            return render_template('shop/setup.html')

        # Handle Logo Upload
        logo_filename = None
        if 'logo' in request.files:
            file = request.files['logo']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(f"shop_{current_user.id}_{file.filename}")
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                logo_filename = filename

        shop = Shop(
            user_id=current_user.id,
            shop_name=shop_name,
            owner_name=owner_name,
            mobile=mobile,
            email=email,
            address=address,
            city=city,
            state=state,
            pincode=pincode,
            gstin=gstin if gstin else None,
            invoice_prefix=invoice_prefix if invoice_prefix else 'INV-',
            logo_path=logo_filename
        )
        db.session.add(shop)
        db.session.commit()

        flash('Your shop profile has been configured successfully!', 'success')
        return redirect(url_for('dashboard.index'))

    return render_template('shop/setup.html')


@shop_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    shop = Shop.query.filter_by(user_id=current_user.id).first_or_404()

    if request.method == 'POST':
        shop.shop_name = request.form.get('shop_name', '').strip()
        shop.owner_name = request.form.get('owner_name', '').strip()
        shop.mobile = request.form.get('mobile', '').strip()
        shop.email = request.form.get('email', '').strip()
        shop.address = request.form.get('address', '').strip()
        shop.city = request.form.get('city', '').strip()
        shop.state = request.form.get('state', '').strip()
        shop.pincode = request.form.get('pincode', '').strip()
        shop.gstin = request.form.get('gstin', '').strip().upper()
        shop.invoice_prefix = request.form.get('invoice_prefix', 'INV-').strip()
        shop.footer_note = request.form.get('footer_note', 'Thank you for shopping with us!').strip()
        shop.tax_type = request.form.get('tax_type', 'GST')

        if 'logo' in request.files:
            file = request.files['logo']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(f"shop_{current_user.id}_{file.filename}")
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                shop.logo_path = filename

        db.session.commit()
        flash('Shop settings updated successfully.', 'success')
        return redirect(url_for('shop.settings'))

    return render_template('shop/settings.html', shop=shop)
