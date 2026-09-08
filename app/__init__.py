import os
from flask import Flask, render_template, session, g
from flask_login import LoginManager, current_user
from config import Config
from app.models import db, User, Shop
from app.utils.helpers import format_currency

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app(config_class=Config):
    app = Flask(__name__, 
                template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates'),
                static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static'))
    
    app.config.from_object(config_class)
    
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    # Register custom template filter
    app.jinja_env.filters['inr'] = format_currency

    # Context processor to inject current shop into templates
    @app.context_processor
    def inject_shop():
        if current_user.is_authenticated:
            shop = Shop.query.filter_by(user_id=current_user.id).first()
            return dict(current_shop=shop)
        return dict(current_shop=None)

    # Register Blueprints
    from app.public.routes import public_bp
    from app.auth.routes import auth_bp
    from app.shop.routes import shop_bp
    from app.dashboard.routes import dashboard_bp
    from app.products.routes import products_bp
    from app.customers.routes import customers_bp
    from app.billing.routes import billing_bp
    from app.reports.routes import reports_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(shop_bp, url_prefix='/shop')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(products_bp, url_prefix='/products')
    app.register_blueprint(customers_bp, url_prefix='/customers')
    app.register_blueprint(billing_bp, url_prefix='/billing')
    app.register_blueprint(reports_bp, url_prefix='/reports')

    # Register Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    with app.app_context():
        db.create_all()

    return app
