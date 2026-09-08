from app import create_app
from app.models import Invoice

app = create_app()
client = app.test_client()

print("Testing user login...")
res = client.post('/auth/login', data={'email_or_mobile':'demo@mybillingsystem.com', 'password':'demo123'}, follow_redirects=True)
print("Login ->", res.status_code)

routes_to_test = [
    '/dashboard/',
    '/products/',
    '/customers/',
    '/billing/create',
    '/billing/history',
    '/reports/',
    '/shop/settings'
]

for route in routes_to_test:
    resp = client.get(route)
    print(f"{route} -> status {resp.status_code}")

with app.app_context():
    inv = Invoice.query.first()
    if inv:
        r1 = client.get(f'/billing/view/{inv.id}')
        r2 = client.get(f'/invoice/{inv.invoice_number}/{inv.secure_token}')
        print(f"Protected Invoice View ({inv.invoice_number}) -> status {r1.status_code}")
        print(f"Public Secure Token Invoice View -> status {r2.status_code}")

print("All route checks complete!")
