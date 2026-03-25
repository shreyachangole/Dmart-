/* ─────────────────────────────────────────────
   D-mart Checkout — checkout.js
   Step 1 → Customer details
   Step 2 → UPI QR payment
   Step 3 → Processing → Invoice
───────────────────────────────────────────── */

let SESSION_ID = '';
let UPI_ID     = '';
let cart       = [];
let discount   = 0;
let grandTotal = 0;

function initCheckout(sessionId, upiId) {
  SESSION_ID = sessionId;
  UPI_ID     = upiId || 'dmart@upi';

  fetch('/api/cart/' + SESSION_ID).then(r => r.json()).then(data => {
    cart     = data.cart     || [];
    discount = data.discount || 0;
    if (cart.length === 0) {
      window.location.href = '/cart/' + SESSION_ID;
      return;
    }
    renderOrderSummary();
  });
}

/* ── Step 1: Order summary sidebar ── */
function renderOrderSummary() {
  const subtotal = cart.reduce((s, i) => s + i.total, 0);
  const gst      = cart.reduce((s, i) => s + i.tax_amount, 0);
  grandTotal     = Math.max(0, subtotal + gst - discount);

  const itemsEl = document.getElementById('summary-items');
  if (itemsEl) {
    itemsEl.innerHTML = cart.map(i => `
      <div class="summary-item">
        <span class="summary-item-name">${i.name} × ${i.quantity}</span>
        <span class="summary-item-price">₹${(i.total + i.tax_amount).toFixed(2)}</span>
      </div>`).join('');
  }

  const sub = document.getElementById('s-subtotal');
  const g   = document.getElementById('s-gst');
  const tot = document.getElementById('s-total');
  const dr  = document.getElementById('s-discount-row');
  const dv  = document.getElementById('s-discount');

  if (sub) sub.textContent = '₹' + subtotal.toFixed(2);
  if (g)   g.textContent   = '₹' + gst.toFixed(2);
  if (tot) tot.textContent = '₹' + grandTotal.toFixed(2);

  if (discount > 0 && dr && dv) {
    dr.style.display = 'flex';
    dv.textContent   = '-₹' + discount.toFixed(2);
  }
}

/* ── Step 1: Submit customer details ── */
function submitDetails() {
  const name    = document.getElementById('f-name').value.trim();
  const phone   = document.getElementById('f-phone').value.trim();
  const email   = document.getElementById('f-email').value.trim();
  const address = document.getElementById('f-address') ? document.getElementById('f-address').value.trim() : '';
  const errEl   = document.getElementById('field-error');

  errEl.style.display = 'none';

  if (!name)                       { showFieldError('Please enter your full name.');         return; }
  if (!phone || phone.length < 10) { showFieldError('Please enter a valid phone number.');   return; }
  if (!email || !email.includes('@')) { showFieldError('Please enter a valid email address.'); return; }

  fetch('/api/checkout/save-customer', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: SESSION_ID, name, phone, email, address }),
  }).then(r => r.json()).then(data => {
    if (data.success) goToStep2();
    else showFieldError(data.message);
  });
}

function showFieldError(msg) {
  const el = document.getElementById('field-error');
  el.textContent   = '⚠️ ' + msg;
  el.style.display = '';
  el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

/* ── Step 2: Generate UPI QR ── */
function goToStep2() {
  setStep(2);

  const badge = document.getElementById('qr-amount-badge');
  if (badge) badge.textContent = '₹' + grandTotal.toFixed(2);

  // UPI deep link — scannable by GPay, PhonePe, Paytm
  const upiLink = `upi://pay?pa=${encodeURIComponent(UPI_ID)}&pn=${encodeURIComponent('D-mart')}&am=${grandTotal.toFixed(2)}&cu=INR&tn=${encodeURIComponent('D-mart Bill Payment')}`;

  const qrEl = document.getElementById('upi-qr');
  if (qrEl) {
    qrEl.innerHTML = '';
    new QRCode(qrEl, {
      text: upiLink,
      width: 200, height: 200,
      colorDark:  '#1a6b2f',
      colorLight: '#ffffff',
      correctLevel: QRCode.CorrectLevel.H,
    });
  }
}

/* ── Confirm payment ── */
function confirmPayment() {
  setStep(3);

  fetch('/api/checkout/confirm-payment', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: SESSION_ID }),
  }).then(r => r.json()).then(data => {
    if (data.success) {
      // Small delay so user sees processing screen
      setTimeout(() => { window.location.href = data.redirect; }, 1800);
    }
  });
}

function cancelPayment() {
  if (confirm('Cancel payment and return to cart?')) {
    window.location.href = '/cart/' + SESSION_ID;
  }
}

/* ── Step management ── */
function setStep(n) {
  [1, 2, 3].forEach(i => {
    const panel = document.getElementById('step' + i);
    const ind   = document.getElementById('step-ind-' + i);
    if (panel) panel.style.display = (i === n) ? '' : 'none';
    if (ind) {
      ind.classList.remove('active', 'done');
      if (i < n)  ind.classList.add('done');
      if (i === n) ind.classList.add('active');
    }
  });
  document.querySelectorAll('.step-line').forEach((el, idx) => {
    el.classList.toggle('done', idx < n - 1);
  });
  // Scroll top
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

/* ── Toast ── */
let toastTimer = null;
function showToast(msg, type) {
  const el = document.getElementById('toast');
  if (!el) return;
  el.textContent = msg;
  el.className   = 'toast show' + (type === 'error' ? ' error' : '');
  if (toastTimer) clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { el.className = 'toast'; }, 3000);
}