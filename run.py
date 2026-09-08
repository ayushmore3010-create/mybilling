from app import create_app
from seed import seed_database

app = create_app()

if __name__ == '__main__':
    # Auto-seed sample database if empty
    with app.app_context():
        from app.models import User
        if User.query.count() == 0:
            seed_database()

    print("[SERVER] Starting MyBillingSystem SaaS Application on http://127.0.0.1:5000 ...")
    app.run(host='0.0.0.0', port=5000, debug=False)
