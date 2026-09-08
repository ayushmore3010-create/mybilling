from flask import render_template, request, Response, flash, redirect, url_for
from app.public import public_bp
from app.models import Invoice, Shop
from app.utils.helpers import generate_whatsapp_link

@public_bp.route('/')
def index():
    return render_template('landing/index.html')


@public_bp.route('/pricing')
def pricing():
    return render_template('landing/pricing.html')


@public_bp.route('/faq')
def faq():
    return render_template('landing/faq.html')


@public_bp.route('/about')
def about():
    return render_template('landing/about.html')


@public_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        flash('Thank you for contacting MyBillingSystem! Our team will get back to you shortly.', 'success')
        return redirect(url_for('public.contact'))
    return render_template('landing/contact.html')


# --- SEO LANDING PAGES ---
@public_bp.route('/billing-software')
def seo_billing_software():
    return render_template('seo/billing_software.html')


@public_bp.route('/invoice-generator')
def seo_invoice_generator():
    return render_template('seo/invoice_generator.html')


@public_bp.route('/gst-billing-software')
def seo_gst_billing_software():
    return render_template('seo/gst_billing_software.html')


@public_bp.route('/billing-software-for-small-business')
def seo_small_business():
    return render_template('seo/small_business.html')


@public_bp.route('/billing-software-for-retail-shop')
def seo_retail_shop():
    return render_template('seo/retail_shop.html')


@public_bp.route('/online-invoice-generator')
def seo_online_invoice():
    return render_template('seo/online_invoice.html')


@public_bp.route('/whatsapp-invoice')
def seo_whatsapp_invoice():
    return render_template('seo/whatsapp_invoice.html')


# --- BLOG SECTION ---
BLOG_POSTS = {
    'gst-invoice-guide-for-small-businesses': {
        'title': 'Complete GST Invoice Guide for Small Businesses in India',
        'desc': 'Learn how to issue GST-compliant bills, understand CGST, SGST, IGST rates, and avoid tax errors in your retail shop.',
        'date': 'August 01, 2026',
        'author': 'MyBillingSystem Editorial',
        'template': 'blog/gst_guide.html'
    },
    'how-to-send-invoice-on-whatsapp': {
        'title': 'How to Send Digital Bills & Invoices on WhatsApp to Shop Customers',
        'desc': 'Save paper and print costs by instantly sending PDF invoices to customers directly on WhatsApp with 1-click sharing.',
        'date': 'July 25, 2026',
        'author': 'MyBillingSystem Editorial',
        'template': 'blog/whatsapp_guide.html'
    },
    'manual-billing-vs-billing-software': {
        'title': 'Manual Paper Billing vs Digital Billing Software: Which is Better for Your Shop?',
        'desc': 'Compare traditional paper bill books with modern online SaaS billing systems for Indian retailers and Kirana stores.',
        'date': 'July 18, 2026',
        'author': 'MyBillingSystem Editorial',
        'template': 'blog/manual_vs_digital.html'
    },
    'how-to-manage-shop-inventory': {
        'title': '5 Practical Inventory Management Tips for Retail Shop Owners in India',
        'desc': 'Track stock, set low-stock warnings, avoid out-of-stock items, and maintain higher profit margins with smart billing.',
        'date': 'July 10, 2026',
        'author': 'MyBillingSystem Editorial',
        'template': 'blog/inventory_guide.html'
    }
}

@public_bp.route('/blog')
def blog_index():
    return render_template('blog/index.html', posts=BLOG_POSTS)


@public_bp.route('/blog/<slug>')
def blog_detail(slug):
    post = BLOG_POSTS.get(slug)
    if not post:
        return render_template('errors/404.html'), 404
    return render_template(post['template'], post=post, slug=slug)


# --- PUBLIC SECURE INVOICE ROUTE ---
@public_bp.route('/invoice/<invoice_number>/<secure_token>')
def public_invoice(invoice_number, secure_token):
    invoice = Invoice.query.filter_by(invoice_number=invoice_number, secure_token=secure_token).first_or_404()
    shop = Shop.query.get(invoice.shop_id)

    cust_mobile = invoice.customer_rel.mobile if invoice.customer_rel else ""
    whatsapp_url = generate_whatsapp_link(
        mobile_no=cust_mobile,
        invoice_no=invoice.invoice_number,
        shop_name=shop.shop_name,
        total_amount=invoice.grand_total,
        secure_token=invoice.secure_token,
        request_host=request.host
    )

    return render_template('billing/public_invoice.html', invoice=invoice, shop=shop, whatsapp_url=whatsapp_url)


# --- LEGAL PAGES ---
@public_bp.route('/privacy')
def privacy():
    return render_template('legal/privacy.html')


@public_bp.route('/terms')
def terms():
    return render_template('legal/terms.html')


@public_bp.route('/refund')
def refund():
    return render_template('legal/refund.html')


# --- SEO SITEMAP & ROBOTS.TXT ---
@public_bp.route('/sitemap.xml')
def sitemap():
    host = request.host_url.rstrip('/')
    urls = [
        '/', '/pricing', '/faq', '/about', '/contact',
        '/billing-software', '/invoice-generator', '/gst-billing-software',
        '/billing-software-for-small-business', '/billing-software-for-retail-shop',
        '/online-invoice-generator', '/whatsapp-invoice',
        '/blog', '/privacy', '/terms', '/refund'
    ]
    for slug in BLOG_POSTS:
        urls.append(f'/blog/{slug}')

    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for u in urls:
        xml_content += f'  <url>\n    <loc>{host}{u}</loc>\n    <changefreq>daily</changefreq>\n    <priority>0.8</priority>\n  </url>\n'
    xml_content += '</urlset>'

    return Response(xml_content, mimetype='application/xml')


@public_bp.route('/robots.txt')
def robots():
    host = request.host_url.rstrip('/')
    content = f"User-agent: *\nAllow: /\nDisallow: /dashboard/\nDisallow: /billing/\nDisallow: /products/\nDisallow: /customers/\nDisallow: /shop/\n\nSitemap: {host}/sitemap.xml\n"
    return Response(content, mimetype='text/plain')
