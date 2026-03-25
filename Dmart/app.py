from flask import Flask, render_template, jsonify, request
from Dmart.products import PRODUCTS, COUPONS, STORE
import uuid, math, smtplib, os, io
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime
from Dmart.pdf_invoice import generate_invoice_pdf


app = Flask(__name__)
app.secret_key = 'dmart_secret_2024'

GST_RATE = 5
sessions = {}

# ── Email config ──────────────────────────────────────────────────────────────
# Set as environment variables:
#   Windows CMD : set EMAIL_USER=you@gmail.com  &  set EMAIL_PASS=app_password
#   PowerShell  : $env:EMAIL_USER="you@gmail.com"; $env:EMAIL_PASS="app_password"
# Use a Gmail App Password (not your regular password).
# Generate at: https://myaccount.google.com/apppasswords
EMAIL_USER = os.environ.get('EMAIL_USER')
EMAIL_PASS = os.environ.get('EMAIL_PASS')
EMAIL_FROM_NAME = 'D-mart Smart Billing'


# ── Helpers ───────────────────────────────────────────────────────────────────
def _new_session():
    return {'cart': [], 'coupon': None, 'discount': 0, 'customer': None, 'paid': False}

def _ensure(sid):
    if sid not in sessions:
        sessions[sid] = _new_session()


# ═=============================================================================
#  EMAIL SENDER  (HTML body + PDF attachment)
# ═════════════════════════════════════════════════════════════════════════════
def send_invoice_email(customer, cart, subtotal, gst, discount, grand,
                       invoice_no, coupon):
    """
    Sends a styled HTML email with the PDF invoice attached.
    Returns (success: bool, error_message: str | None)
    """
    try:
        to_email = customer['email']
        date_str = datetime.now().strftime('%d %B %Y, %I:%M %p')

        # ── Generate PDF ──────────────────────────────────────────────────
        pdf_bytes = generate_invoice_pdf(
            customer   = customer,
            cart       = cart,
            subtotal   = subtotal,
            gst        = gst,
            discount   = discount,
            grand      = grand,
            invoice_no = invoice_no,
            coupon     = coupon,
            store      = STORE,
        )

        # ── HTML email body ───────────────────────────────────────────────
        item_rows = ''.join(f"""
          <tr>
            <td style="padding:9px 12px;border-bottom:1px solid #eee;color:#555;font-size:13px;">{i+1}</td>
            <td style="padding:9px 12px;border-bottom:1px solid #eee;">
              <strong style="color:#1a1a1a;font-size:13px;">{item['name']}</strong><br/>
              <span style="font-size:11px;color:#888;">{item['brand']} · {item['code']}</span>
            </td>
            <td style="padding:9px 12px;border-bottom:1px solid #eee;text-align:center;color:#555;font-size:13px;">{item['quantity']}</td>
            <td style="padding:9px 12px;border-bottom:1px solid #eee;text-align:right;color:#555;font-size:13px;">₹{item['price']:.2f}</td>
            <td style="padding:9px 12px;border-bottom:1px solid #eee;text-align:right;font-weight:700;color:#1a6b2f;font-size:13px;">₹{(item['total']+item['tax_amount']):.2f}</td>
          </tr>""" for i, item in enumerate(cart))

        discount_row = f"""
          <tr>
            <td colspan="4" style="padding:8px 12px;text-align:right;color:#f5a623;font-weight:600;font-size:13px;">
              Coupon Discount ({coupon.get('code','') if coupon else ''})
            </td>
            <td style="padding:8px 12px;text-align:right;color:#2e9e4f;font-weight:700;font-size:13px;">-₹{discount:.2f}</td>
          </tr>""" if discount > 0 else ''

        html_body = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"/></head>
        <body style="margin:0;padding:0;background:#f0f4f0;font-family:'Segoe UI',Arial,sans-serif;">
        <div style="max-width:620px;margin:32px auto;background:#fff;border-radius:16px;
                    overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.10);">

          <div style="background:#1a6b2f;padding:28px 32px;">
            <h1 style="margin:0 0 4px;color:#fff;font-size:28px;letter-spacing:-1px;">D-mart</h1>
            <p style="margin:0;color:rgba(255,255,255,0.7);font-size:12px;">{STORE['address']}</p>
            <span style="display:inline-block;margin-top:12px;background:#27ae60;color:#fff;
                         font-size:11px;font-weight:700;padding:4px 16px;border-radius:20px;">
              ✅ PAYMENT SUCCESSFUL
            </span>
          </div>

          <div style="padding:20px 32px;background:#f7fbf8;border-bottom:1px solid #e0ece3;">
            <table width="100%"><tr>
              <td>
                <div style="font-size:10px;color:#888;text-transform:uppercase;letter-spacing:1px;">Invoice No.</div>
                <div style="font-size:17px;font-weight:800;color:#1a1a1a;font-family:monospace;">{invoice_no}</div>
              </td>
              <td style="text-align:right;">
                <div style="font-size:10px;color:#888;text-transform:uppercase;letter-spacing:1px;">Date</div>
                <div style="font-size:13px;font-weight:600;color:#1a1a1a;">{date_str}</div>
              </td>
            </tr></table>
          </div>

          <div style="padding:16px 32px;border-bottom:1px solid #eee;">
            <div style="font-size:10px;color:#888;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">Bill To</div>
            <div style="font-size:16px;font-weight:700;color:#1a1a1a;">{customer['name']}</div>
            <div style="font-size:13px;color:#555;margin-top:4px;line-height:1.7;">
              📞 {customer['phone']}<br/>✉️ {customer['email']}
              {'<br/>📍 ' + customer['address'] if customer.get('address') else ''}
            </div>
          </div>

          <div style="padding:16px 32px 0;">
            <table width="100%" style="border-collapse:collapse;">
              <thead>
                <tr style="background:#e8f5ec;">
                  <th style="padding:9px 12px;text-align:left;font-size:11px;color:#1a6b2f;text-transform:uppercase;">#</th>
                  <th style="padding:9px 12px;text-align:left;font-size:11px;color:#1a6b2f;text-transform:uppercase;">Product</th>
                  <th style="padding:9px 12px;text-align:center;font-size:11px;color:#1a6b2f;text-transform:uppercase;">Qty</th>
                  <th style="padding:9px 12px;text-align:right;font-size:11px;color:#1a6b2f;text-transform:uppercase;">Price</th>
                  <th style="padding:9px 12px;text-align:right;font-size:11px;color:#1a6b2f;text-transform:uppercase;">Total</th>
                </tr>
              </thead>
              <tbody>{item_rows}</tbody>
              <tfoot>
                <tr><td colspan="4" style="padding:8px 12px;text-align:right;color:#555;font-size:13px;">Subtotal</td>
                    <td style="padding:8px 12px;text-align:right;font-weight:600;font-size:13px;">₹{subtotal:.2f}</td></tr>
                <tr><td colspan="4" style="padding:6px 12px;text-align:right;color:#555;font-size:13px;">GST @ 5%</td>
                    <td style="padding:6px 12px;text-align:right;font-weight:600;font-size:13px;">₹{gst:.2f}</td></tr>
                {discount_row}
                <tr style="background:#e8f5ec;">
                  <td colspan="4" style="padding:12px;text-align:right;font-size:15px;font-weight:800;color:#1a1a1a;">Total Paid</td>
                  <td style="padding:12px;text-align:right;font-size:17px;font-weight:800;color:#1a6b2f;">₹{grand:.2f}</td>
                </tr>
              </tfoot>
            </table>
          </div>

          <div style="padding:20px 32px;text-align:center;border-top:1px solid #eee;margin-top:16px;">
            <p style="font-size:14px;font-weight:700;color:#1a6b2f;margin:0 0 6px;">
              🛍️ Thank you for shopping at D-mart!
            </p>
            <p style="font-size:12px;color:#888;margin:0;">
              Your invoice PDF is attached to this email.<br/>
              GSTIN: {STORE['gstin']} · {STORE['phone']}
            </p>
          </div>

        </div>
        </body></html>"""

        # ── Plain text fallback ───────────────────────────────────────────
        text_body = (
            f"D-mart Invoice {invoice_no}\n{'='*40}\n"
            f"Date: {date_str}\nCustomer: {customer['name']}\n"
            f"Phone: {customer['phone']}\nEmail: {customer['email']}\n\n"
            + '\n'.join(f"  {i['name']} x{i['quantity']}  ₹{(i['total']+i['tax_amount']):.2f}" for i in cart)
            + f"\n\nSubtotal : ₹{subtotal:.2f}\nGST (5%) : ₹{gst:.2f}"
            + (f"\nDiscount : -₹{discount:.2f}" if discount > 0 else "")
            + f"\n{'='*40}\nTOTAL    : ₹{grand:.2f}\n\n"
            "Thank you for shopping at D-mart!\n"
            "Your invoice PDF is attached to this email."
        )

        # ── Build MIME message ────────────────────────────────────────────
        msg              = MIMEMultipart('mixed')
        msg['Subject']   = f'🧾 D-mart Invoice {invoice_no} — ₹{grand:.2f}'
        msg['From']      = f'{EMAIL_FROM_NAME} <{EMAIL_USER}>'
        msg['To']        = to_email

        # Attach HTML + text as alternative part
        alt = MIMEMultipart('alternative')
        alt.attach(MIMEText(text_body, 'plain', 'utf-8'))
        alt.attach(MIMEText(html_body, 'html',  'utf-8'))
        msg.attach(alt)

        # Attach PDF
        pdf_part = MIMEApplication(pdf_bytes, _subtype='pdf')
        pdf_part.add_header(
            'Content-Disposition', 'attachment',
            filename=f'{invoice_no}.pdf'
        )
        msg.attach(pdf_part)

        # ── Send via Gmail SMTP ───────────────────────────────────────────
        print(f"[EMAIL] Connecting to smtp.gmail.com:587...")
        print(f"[EMAIL] Sending from: {EMAIL_USER}")
        print(f"[EMAIL] Sending to  : {to_email}")

        if EMAIL_USER == 'your_gmail@gmail.com' or EMAIL_PASS == 'your_app_password_here':
            err = "EMAIL_USER or EMAIL_PASS not configured. Run test_email.py for setup instructions."
            print(f"[EMAIL ERROR] {err}")
            return False, err

        with smtplib.SMTP('smtp.gmail.com', 587, timeout=15) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            print("[EMAIL] Logging in...")
            server.login(EMAIL_USER, EMAIL_PASS)
            print("[EMAIL] Login successful. Sending...")
            server.sendmail(EMAIL_USER, to_email, msg.as_string())

        print(f"[EMAIL] SUCCESS — Invoice {invoice_no} + PDF sent to {to_email}")
        return True, None

    except smtplib.SMTPAuthenticationError:
        err = ("Gmail authentication failed. You must use a Gmail App Password, NOT your regular password. "
               "Generate one at https://myaccount.google.com/apppasswords")
        print(f"[EMAIL ERROR] {err}")
        return False, err

    except smtplib.SMTPRecipientsRefused as e:
        err = f"Recipient refused: {to_email} — {e}"
        print(f"[EMAIL ERROR] {err}")
        return False, err

    except smtplib.SMTPException as e:
        err = f"SMTP error: {e}"
        print(f"[EMAIL ERROR] {err}")
        return False, err

    except OSError as e:
        err = f"Network error (check internet connection): {e}"
        print(f"[EMAIL ERROR] {err}")
        return False, err

    except Exception as e:
        err = f"Unexpected error: {type(e).__name__}: {e}"
        print(f"[EMAIL ERROR] {err}")
        return False, err


# ═════════════════════════════════════════════════════════════════════════════
#  FLASK ROUTES  (unchanged from original)
# ═════════════════════════════════════════════════════════════════════════════
@app.route('/')
def index():
    sid = str(uuid.uuid4())
    sessions[sid] = _new_session()
    return render_template('index.html', store=STORE, session_id=sid)

@app.route('/scanner/<session_id>')
def scanner(session_id):
    _ensure(session_id)
    return render_template('scanner.html', store=STORE, session_id=session_id)

@app.route('/cart/<session_id>')
def cart_page(session_id):
    _ensure(session_id)
    return render_template('cart.html', store=STORE, session_id=session_id)

@app.route('/checkout/<session_id>')
def checkout_page(session_id):
    _ensure(session_id)
    return render_template('checkout.html', store=STORE, session_id=session_id)

@app.route('/invoice/<session_id>')
def invoice_page(session_id):
    _ensure(session_id)
    sess = sessions[session_id]
    if not sess.get('paid') or not sess.get('customer'):
        return render_template('cart.html', store=STORE, session_id=session_id)
    cart       = sess['cart']
    customer   = sess['customer']
    discount   = sess['discount']
    subtotal   = round(sum(i['total'] for i in cart), 2)
    gst        = round(sum(i['tax_amount'] for i in cart), 2)
    grand      = round(subtotal + gst - discount, 2)
    invoice_no = 'INV-' + session_id[:8].upper()
    return render_template('invoice.html',
        store=STORE, session_id=session_id, cart=cart,
        customer=customer, subtotal=subtotal, gst=gst,
        discount=discount, grand=grand, invoice_no=invoice_no,
        coupon=sess.get('coupon'))


@app.route('/api/products')
def all_products():
    out = {}
    for bc, p in PRODUCTS.items():
        out[bc] = {**p, 'tax': GST_RATE}
    return jsonify(out)


@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    data = request.json
    sid  = data.get('session_id')
    bc   = data.get('barcode')
    _ensure(sid)
    product = PRODUCTS.get(bc)
    if not product:
        return jsonify({'success': False, 'message': 'Product not found'})
    cart = sessions[sid]['cart']
    for item in cart:
        if item['barcode'] == bc:
            item['quantity']  += 1
            item['total']      = round(item['quantity'] * item['price'], 2)
            item['tax_amount'] = round(item['total'] * GST_RATE / 100, 2)
            return jsonify({'success': True, 'cart': cart})
    cart.append({
        'barcode':    bc,   'name':      product['name'],
        'brand':      product['brand'], 'code':      product['code'],
        'price':      product['price'], 'tax':       GST_RATE,
        'quantity':   1,                'total':     product['price'],
        'tax_amount': round(product['price'] * GST_RATE / 100, 2),
        'category':   product['category'], 'image_url': product['image_url'],
    })
    return jsonify({'success': True, 'cart': cart})


@app.route('/api/cart/remove', methods=['POST'])
def remove_from_cart():
    data = request.json
    sid  = data.get('session_id')
    bc   = data.get('barcode')
    _ensure(sid)
    sessions[sid]['cart'] = [i for i in sessions[sid]['cart'] if i['barcode'] != bc]
    return jsonify({'success': True, 'cart': sessions[sid]['cart']})


@app.route('/api/cart/<session_id>')
def get_cart(session_id):
    _ensure(session_id)
    return jsonify(sessions[session_id])


@app.route('/api/coupon/apply', methods=['POST'])
def apply_coupon():
    data   = request.json
    sid    = data.get('session_id')
    code   = data.get('code', '').strip().upper()
    _ensure(sid)
    coupon = COUPONS.get(code)
    if not coupon:
        return jsonify({'success': False, 'message': 'Invalid coupon code'})
    cart  = sessions[sid]['cart']
    total = round(sum(i['total'] + i['tax_amount'] for i in cart), 2)
    disc  = round(total * coupon['value'] / 100, 2) if coupon['type'] == 'percent' \
            else min(float(coupon['value']), total)
    sessions[sid]['coupon']   = {'code': code, **coupon}
    sessions[sid]['discount'] = disc
    return jsonify({'success': True, 'discount': disc, 'desc': coupon['desc'],
                    'message': f"Coupon applied! You save ₹{disc:.2f}"})


@app.route('/api/coupon/remove', methods=['POST'])
def remove_coupon():
    data = request.json
    sid  = data.get('session_id')
    _ensure(sid)
    sessions[sid]['coupon']   = None
    sessions[sid]['discount'] = 0
    return jsonify({'success': True})


@app.route('/api/checkout/save-customer', methods=['POST'])
def save_customer():
    data = request.json
    sid  = data.get('session_id')
    _ensure(sid)
    customer = {
        'name':    data.get('name', '').strip(),
        'phone':   data.get('phone', '').strip(),
        'email':   data.get('email', '').strip(),
        'address': data.get('address', '').strip(),
    }
    if not all([customer['name'], customer['phone'], customer['email']]):
        return jsonify({'success': False, 'message': 'Name, phone and email are required'})
    sessions[sid]['customer'] = customer
    return jsonify({'success': True})


@app.route('/api/checkout/confirm-payment', methods=['POST'])
def confirm_payment():
    """Marks payment as complete and redirects to invoice. Does NOT send email."""
    data = request.json
    sid  = data.get('session_id')
    _ensure(sid)
    sessions[sid]['paid'] = True
    return jsonify({'success': True, 'redirect': f'/invoice/{sid}'})


@app.route('/api/send-invoice-email', methods=['POST'])
def send_invoice_email_route():
    """
    Called only when user explicitly clicks 'Send Invoice to Email' on the invoice page.
    """
    data = request.json
    sid  = data.get('session_id')
    _ensure(sid)
    sess = sessions[sid]

    if not sess.get('paid'):
        return jsonify({'success': False, 'message': 'Payment not completed'})

    customer   = sess.get('customer')
    cart       = sess.get('cart', [])
    discount   = sess.get('discount', 0)
    coupon     = sess.get('coupon')
    subtotal   = round(sum(i['total'] for i in cart), 2)
    gst        = round(sum(i['tax_amount'] for i in cart), 2)
    grand      = round(subtotal + gst - discount, 2)
    invoice_no = 'INV-' + sid[:8].upper()

    if not customer or not customer.get('email'):
        return jsonify({'success': False, 'message': 'No email address found'})

    email_sent, email_error = send_invoice_email(
        customer=customer, cart=cart, subtotal=subtotal,
        gst=gst, discount=discount, grand=grand,
        invoice_no=invoice_no, coupon=coupon,
    )

    if email_sent:
        return jsonify({'success': True,  'message': f"Invoice sent to {customer['email']}"})
    else:
        return jsonify({'success': False, 'message': email_error or 'Failed to send email'})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)