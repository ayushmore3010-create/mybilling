from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.auth import auth_bp
from app.models import db, User, Shop

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        mobile = request.form.get('mobile', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validations
        if not full_name or not email or not mobile or not password:
            flash('All fields are required.', 'danger')
            return render_template('auth/register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')

        if User.query.filter_by(email=email).first():
            flash('An account with this email already exists.', 'warning')
            return render_template('auth/register.html')

        # Create user
        user = User(
            full_name=full_name,
            email=email,
            mobile=mobile
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash('Account created successfully! Please set up your shop profile.', 'success')
        return redirect(url_for('shop.setup'))

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        login_input = request.form.get('email_or_mobile', '').strip().lower()
        password = request.form.get('password', '')
        remember = True if request.form.get('remember') else False

        user = User.query.filter((User.email == login_input) | (User.mobile == login_input)).first()

        if not user or not user.check_password(password):
            flash('Invalid email/mobile or password. Please try again.', 'danger')
            return render_template('auth/login.html')

        login_user(user, remember=remember)
        
        # Check if shop profile exists
        shop = Shop.query.filter_by(user_id=user.id).first()
        if not shop:
            return redirect(url_for('shop.setup'))

        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
            
        flash(f'Welcome back, {user.full_name}!', 'success')
        return redirect(url_for('dashboard.index'))

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('public.index'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        flash('If an account exists for this email, password reset instructions have been sent.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/forgot_password.html')
