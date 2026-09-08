# 🚀 MyBillingSystem - Commercial SaaS Billing & Invoice Management Platform

**MyBillingSystem** is a modern, responsive, production-ready SaaS billing and invoice management platform designed specifically for Indian shop owners, Kirana stores, retail outlets, and small businesses.

---

## 🌟 Key Features

1. **Authentication & Multi-Tenant Data Isolation**
   - Secure login & registration with Bcrypt password hashing.
   - Database-level `shop_id` isolation ensuring Shop A can never access Shop B data.
2. **Shop Setup & Profile Settings**
   - Shop name, logo upload (PNG, JPG, WEBP), owner details, address, state, GSTIN, and custom invoice prefixes (e.g. `INV-`).
3. **Interactive Billing Calculation Engine**
   - Instant real-time math without page reloads.
   - Calculates subtotal, line discounts, taxable amounts, CGST, SGST, IGST, and grand totals.
   - Auto-decrements product inventory stock levels.
4. **Professional Invoice, PDF & Native Printing**
   - Generates clean tax invoices displaying shop logo, GSTIN, item breakdowns, and custom thank-you notes.
   - 1-click A4 PDF downloads powered by `html2pdf.js`.
   - Native print optimization (`@media print`) that hides dashboard sidebars and buttons.
5. **WhatsApp Billing & Secure Token Link Sharing**
   - Official WhatsApp deep-link integration (`api.whatsapp.com/send`) pre-formatted with bill summaries and secure random UUID links (`/invoice/<invoice_number>/<secure_token>`).
   - Customers can open, view, or download PDF receipts directly from mobile.
6. **Product & Customer Management**
   - Complete inventory management with SKU, categories, selling prices, GST rates (0%, 5%, 12%, 18%, 28%), stock quantities, and units (Piece, Kg, Gram, Liter, Box, Packet).
   - Low stock warning alerts when inventory falls below threshold.
   - Customer directory tracking purchase history and total spent.
7. **Sales Analytics & Reports**
   - 7-day revenue trend chart via `Chart.js`.
   - Financial GST tax summary (CGST, SGST, IGST collected).
   - Export full sales report to CSV.
8. **Comprehensive SEO & Content Infrastructure**
   - 7 dedicated SEO landing pages (`/billing-software`, `/invoice-generator`, `/gst-billing-software`, etc.).
   - Blog section with detailed articles on GST invoices, WhatsApp billing, and retail inventory tips.
   - Valid Schema.org structured data JSON-LD, `sitemap.xml`, and `robots.txt`.

---

## 🛠️ Quick Setup Instructions

### 1. Requirements
- Python 3.9+ installed on your system.

### 2. Installation
Navigate to the project directory and install dependencies:
```bash
cd mybillingsystem
pip install -r requirements.txt
```

### 3. Initialize & Seed Database
Seed realistic Indian store demo data (Raja General Store, Pune):
```bash
python seed.py
```

### 4. Run Application
Start the Flask dev server:
```bash
python run.py
```
Open your browser and visit: `http://127.0.0.1:5000`

---

## 🔑 Demo Login Credentials

- **Email**: `demo@mybillingsystem.com`
- **Password**: `demo123`

--

Website Link

https://mybilling-pd65.onrender.com/

