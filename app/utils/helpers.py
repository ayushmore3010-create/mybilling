import urllib.parse

def format_currency(amount):
    """Formats float as INR string: e.g. 12450.0 -> ₹12,450.00"""
    try:
        val = float(amount or 0)
        return f"₹{val:,.2f}"
    except (ValueError, TypeError):
        return "₹0.00"

def generate_whatsapp_link(mobile_no, invoice_no, shop_name, total_amount, secure_token, request_host):
    """Generates official WhatsApp click-to-chat link with pre-filled message"""
    if not mobile_no:
        return "#"
    
    clean_mobile = str(mobile_no).replace("+", "").replace(" ", "").replace("-", "").strip()
    if len(clean_mobile) == 10:
        clean_mobile = "91" + clean_mobile
        
    public_url = f"http://{request_host}/invoice/{invoice_no}/{secure_token}"
    
    message = (
        f"Hello! Thank you for shopping with *{shop_name}*.\n\n"
        f"📄 *Invoice No:* {invoice_no}\n"
        f"💰 *Total Amount:* ₹{total_amount:,.2f}\n\n"
        f"Click the link below to view or download your invoice:\n"
        f"👉 {public_url}\n\n"
        f"Powered by MyBillingSystem"
    )
    
    encoded_message = urllib.parse.quote(message)
    return f"https://api.whatsapp.com/send?phone={clean_mobile}&text={encoded_message}"
