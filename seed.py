from app import create_app, db
from app.models import User, Shop, Category, Product, Customer, Invoice, InvoiceItem
from datetime import datetime, timedelta
import uuid

def seed_database():
    app = create_app()
    with app.app_context():
        print("[SEED] Seeding database with realistic Indian shop demo data...")

        # 1. Create Demo User
        demo_user = User.query.filter_by(email='demo@mybillingsystem.com').first()
        if not demo_user:
            demo_user = User(
                email='demo@mybillingsystem.com',
                full_name='Rahul Patil',
                mobile='9876543210'
            )
            demo_user.set_password('demo123')
            db.session.add(demo_user)
            db.session.commit()
            print("[OK] Created Demo User: demo@mybillingsystem.com / demo123")

        # 2. Create Demo Shop
        shop = Shop.query.filter_by(user_id=demo_user.id).first()
        if not shop:
            shop = Shop(
                user_id=demo_user.id,
                shop_name='Raja General Store',
                owner_name='Rahul Patil',
                mobile='9876543210',
                email='demo@mybillingsystem.com',
                address='Shop No. 14, Main Market, MG Road',
                city='Pune',
                state='Maharashtra',
                pincode='411001',
                gstin='27ABCDE1234F1Z5',
                invoice_prefix='INV-',
                footer_note='Thank you for shopping with Raja General Store!'
            )
            db.session.add(shop)
            db.session.commit()
            print("[OK] Created Demo Shop: Raja General Store")

        # 3. Create Categories
        categories_data = ['Groceries & Staples', 'Dairy & Beverages', 'Personal Care', 'Apparel & Clothing', 'Electronics']
        cat_map = {}
        for c_name in categories_data:
            cat = Category.query.filter_by(shop_id=shop.id, name=c_name).first()
            if not cat:
                cat = Category(shop_id=shop.id, name=c_name)
                db.session.add(cat)
                db.session.flush()
            cat_map[c_name] = cat.id
        db.session.commit()

        # 4. Create Sample Products
        products_data = [
            {'name': 'Fortune Sunlite Refined Oil 1L', 'cat': 'Groceries & Staples', 'sku': 'OIL-001', 'purchase': 140, 'selling': 180, 'gst': 5, 'stock': 45, 'unit': 'Liter'},
            {'name': 'Aashirvaad Shudh Chakki Atta 5kg', 'cat': 'Groceries & Staples', 'sku': 'ATTA-005', 'purchase': 210, 'selling': 260, 'gst': 0, 'stock': 30, 'unit': 'Packet'},
            {'name': 'India Gate Basmati Rice 1kg', 'cat': 'Groceries & Staples', 'sku': 'RICE-001', 'purchase': 90, 'selling': 120, 'gst': 5, 'stock': 60, 'unit': 'Kg'},
            {'name': 'Tata Salt Vacuum Evaporated 1kg', 'cat': 'Groceries & Staples', 'sku': 'SALT-001', 'purchase': 20, 'selling': 28, 'gst': 0, 'stock': 100, 'unit': 'Packet'},
            {'name': 'Amul Taaza Toned Milk 1L', 'cat': 'Dairy & Beverages', 'sku': 'MILK-001', 'purchase': 50, 'selling': 56, 'gst': 0, 'stock': 25, 'unit': 'Liter'},
            {'name': 'Amul Butter 500g', 'cat': 'Dairy & Beverages', 'sku': 'BUTTER-500', 'purchase': 240, 'selling': 275, 'gst': 12, 'stock': 15, 'unit': 'Box'},
            {'name': 'Red Label Tea 250g', 'cat': 'Dairy & Beverages', 'sku': 'TEA-250', 'purchase': 110, 'selling': 140, 'gst': 5, 'stock': 3, 'unit': 'Box'}, # Low stock alert sample
            {'name': 'Dove Cream Beauty Bathing Soap 100g', 'cat': 'Personal Care', 'sku': 'SOAP-001', 'purchase': 45, 'selling': 60, 'gst': 18, 'stock': 50, 'unit': 'Piece'},
            {'name': 'Colgate Strong Teeth Toothpaste 200g', 'cat': 'Personal Care', 'sku': 'PASTE-200', 'purchase': 85, 'selling': 110, 'gst': 18, 'stock': 4, 'unit': 'Piece'}, # Low stock alert sample
            {'name': 'Men\'s Pure Cotton Casual Shirt', 'cat': 'Apparel & Clothing', 'sku': 'SHIRT-101', 'purchase': 450, 'selling': 799, 'gst': 5, 'stock': 20, 'unit': 'Piece'},
            {'name': 'Women\'s Printed Kurti S/M/L', 'cat': 'Apparel & Clothing', 'sku': 'KURTI-202', 'purchase': 350, 'selling': 650, 'gst': 5, 'stock': 18, 'unit': 'Piece'},
            {'name': 'Boat BassHeads 100 Wired Earphones', 'cat': 'Electronics', 'sku': 'EAR-100', 'purchase': 250, 'selling': 399, 'gst': 18, 'stock': 2, 'unit': 'Piece'}, # Low stock alert
            {'name': 'Realme 10,000mAh Fast Charging Powerbank', 'cat': 'Electronics', 'sku': 'PB-10K', 'purchase': 750, 'selling': 1199, 'gst': 18, 'stock': 12, 'unit': 'Piece'},
        ]

        prod_objs = []
        for p in products_data:
            existing_p = Product.query.filter_by(shop_id=shop.id, name=p['name']).first()
            if not existing_p:
                existing_p = Product(
                    shop_id=shop.id,
                    category_id=cat_map[p['cat']],
                    name=p['name'],
                    sku=p['sku'],
                    purchase_price=p['purchase'],
                    selling_price=p['selling'],
                    gst_rate=p['gst'],
                    stock_qty=p['stock'],
                    unit=p['unit']
                )
                db.session.add(existing_p)
                db.session.flush()
            prod_objs.append(existing_p)
        db.session.commit()
        print(f"[OK] Created {len(prod_objs)} Products")

        # 5. Create Customers
        customers_data = [
            {'name': 'Ramesh Kumar', 'mobile': '9812345678', 'address': 'Flat 201, Shanti Society, Pune'},
            {'name': 'Sunita Sharma', 'mobile': '9823456789', 'address': 'Block B-4, Deccan Gymkhana, Pune'},
            {'name': 'Amit Shah', 'mobile': '9834567890', 'address': 'Shop #5, Kothrud, Pune'},
            {'name': 'Priya Verma', 'mobile': '9845678901', 'address': 'Aundh Road, Pune'},
            {'name': 'Vikas Joshi', 'mobile': '9856789012', 'address': 'Viman Nagar, Pune'}
        ]

        cust_objs = []
        for c in customers_data:
            existing_c = Customer.query.filter_by(shop_id=shop.id, mobile=c['mobile']).first()
            if not existing_c:
                existing_c = Customer(
                    shop_id=shop.id,
                    name=c['name'],
                    mobile=c['mobile'],
                    whatsapp=c['mobile'],
                    address=c['address']
                )
                db.session.add(existing_c)
                db.session.flush()
            cust_objs.append(existing_c)
        db.session.commit()
        print(f"[OK] Created {len(cust_objs)} Customers")

        # 6. Create Sample Past Invoices if none exist
        if Invoice.query.filter_by(shop_id=shop.id).count() == 0:
            sample_invoices = [
                {
                    'inv_no': 'INV-000001',
                    'cust': cust_objs[0],
                    'date': datetime.utcnow() - timedelta(days=5),
                    'items': [
                        {'prod': prod_objs[0], 'qty': 2, 'disc': 0},
                        {'prod': prod_objs[1], 'qty': 1, 'disc': 5}
                    ],
                    'pm': 'Cash', 'status': 'Paid'
                },
                {
                    'inv_no': 'INV-000002',
                    'cust': cust_objs[1],
                    'date': datetime.utcnow() - timedelta(days=3),
                    'items': [
                        {'prod': prod_objs[9], 'qty': 1, 'disc': 10},
                        {'prod': prod_objs[7], 'qty': 2, 'disc': 0}
                    ],
                    'pm': 'UPI', 'status': 'Paid'
                },
                {
                    'inv_no': 'INV-000003',
                    'cust': cust_objs[2],
                    'date': datetime.utcnow() - timedelta(days=1),
                    'items': [
                        {'prod': prod_objs[12], 'qty': 1, 'disc': 0},
                        {'prod': prod_objs[11], 'qty': 1, 'disc': 0}
                    ],
                    'pm': 'Card', 'status': 'Paid'
                },
                {
                    'inv_no': 'INV-000004',
                    'cust': cust_objs[3],
                    'date': datetime.utcnow(),
                    'items': [
                        {'prod': prod_objs[2], 'qty': 5, 'disc': 0},
                        {'prod': prod_objs[4], 'qty': 2, 'disc': 0}
                    ],
                    'pm': 'Cash', 'status': 'Paid'
                }
            ]

            for inv_data in sample_invoices:
                subtotal = 0.0
                total_disc = 0.0
                taxable = 0.0
                total_tax = 0.0
                items = []

                for item in inv_data['items']:
                    p = item['prod']
                    qty = item['qty']
                    disc = item['disc']
                    rate = p.selling_price
                    gst = p.gst_rate

                    line_gross = qty * rate
                    line_disc_val = (line_gross * disc) / 100.0
                    line_taxable = line_gross - line_disc_val
                    line_tax_val = (line_taxable * gst) / 100.0
                    line_total = line_taxable + line_tax_val

                    subtotal += line_gross
                    total_disc += line_disc_val
                    taxable += line_taxable
                    total_tax += line_tax_val

                    inv_item = InvoiceItem(
                        product_id=p.id,
                        product_name=p.name,
                        quantity=qty,
                        unit=p.unit,
                        rate=rate,
                        discount=disc,
                        gst_rate=gst,
                        line_tax=line_tax_val,
                        line_total=line_total
                    )
                    items.append(inv_item)

                grand_total = taxable + total_tax

                inv_obj = Invoice(
                    shop_id=shop.id,
                    customer_id=inv_data['cust'].id,
                    invoice_number=inv_data['inv_no'],
                    secure_token=str(uuid.uuid4()),
                    invoice_date=inv_data['date'],
                    subtotal=subtotal,
                    discount_amount=total_disc,
                    taxable_amount=taxable,
                    total_tax=total_tax,
                    cgst_amount=total_tax / 2.0,
                    sgst_amount=total_tax / 2.0,
                    grand_total=grand_total,
                    payment_method=inv_data['pm'],
                    payment_status=inv_data['status'],
                    amount_paid=grand_total if inv_data['status'] == 'Paid' else 0.0,
                    items=items
                )
                db.session.add(inv_obj)

                # Update customer
                inv_data['cust'].total_spent = (inv_data['cust'].total_spent or 0) + grand_total
                inv_data['cust'].total_invoices = (inv_data['cust'].total_invoices or 0) + 1

            db.session.commit()
            print("[OK] Created Sample Invoices with dynamic tax calculations")

        print("[SUCCESS] Database seeding finished successfully!")

if __name__ == '__main__':
    seed_database()
