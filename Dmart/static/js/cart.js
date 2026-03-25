/* ─────────────────────────────────────────────
   D-mart Cart Page — cart.js
───────────────────────────────────────────── */

let SESSION_ID = '';
let cart       = [];
let discount   = 0;
let couponData = null;

function initCart(sessionId) {
  SESSION_ID = sessionId;
  fetchCart();
}

function fetchCart() {
  fetch('/api/cart/' + SESSION_ID).then(r => r.json()).then(data => {
    cart       = data.cart     || [];
    discount   = data.discount || 0;
    couponData = data.coupon   || null;
    renderPage();
  });
}

/* ── Render ── */
function renderPage() {
  renderItems();
  renderSummary();
  renderCouponState();
}

function renderItems() {
  const listEl   = document.getElementById('cart-items-list');
  const emptyEl  = document.getElementById('cart-empty');
  const scanMore = document.getElementById('btn-scan-more');
  const countEl  = document.getElementById('cart-count-label');
  const totalQty = cart.reduce((s, i) => s + i.quantity, 0);

  countEl.textContent = totalQty + ' item' + (totalQty !== 1 ? 's' : '');

  if (!cart || cart.length === 0) {
    emptyEl.style.display = 'flex';
    listEl.innerHTML      = '';
    if (scanMore) scanMore.style.display = 'none';
    return;
  }

  emptyEl.style.display = 'none';
  if (scanMore) scanMore.style.display = 'flex';

  listEl.innerHTML = cart.map(item => `
    <div class="cart-item-full" id="ci-${item.barcode}">
      <img class="product-img-cart"
           src="${item.image_url}"
           alt="${item.name}"
           onerror="this.style.background='#eee'" />
      <div class="item-details">
        <div class="item-name-full">${item.name}</div>
        <div class="item-brand">${item.brand} · ${item.category}</div>
        <div class="item-unit-price">₹${item.price.toFixed(2)} per unit</div>
      </div>
      <div class="item-actions">
        <div class="item-total-price">₹${(item.total + item.tax_amount).toFixed(2)}</div>
        <div class="item-controls-row">
          <div class="qty-controls">
            <button class="qty-btn" onclick="changeQty('${item.barcode}',-1)">−</button>
            <span class="qty-num">${item.quantity}</span>
            <button class="qty-btn" onclick="changeQty('${item.barcode}',1)">+</button>
          </div>
          <button class="btn-delete" onclick="removeItem('${item.barcode}')" title="Remove item">🗑</button>
        </div>
      </div>
    </div>
  `).join('');
}

function renderSummary() {
  const subtotal   = cart.reduce((s, i) => s + i.total, 0);
  const totalTax   = cart.reduce((s, i) => s + i.tax_amount, 0);
  const billBefore = subtotal + totalTax;
  const finalTotal = Math.max(0, billBefore - discount);
  const totalQty   = cart.reduce((s, i) => s + i.quantity, 0);

  // items count line (if element exists)
  const countLine = document.getElementById('bill-items-count');
  if (countLine) countLine.textContent = totalQty + ' item' + (totalQty !== 1 ? 's' : '') + ' in cart';

  document.getElementById('bill-subtotal').textContent = '₹' + subtotal.toFixed(2);
  document.getElementById('bill-gst').textContent      = '₹' + totalTax.toFixed(2);
  document.getElementById('bill-total').textContent    = '₹' + finalTotal.toFixed(2);

  const discountRow  = document.getElementById('discount-row');
  const savingsTag   = document.getElementById('savings-tag');
  const savingsAmt   = document.getElementById('savings-amount');
  const billDiscount = document.getElementById('bill-discount');

  if (discount > 0) {
    discountRow.style.display = 'flex';
    savingsTag.style.display  = '';
    billDiscount.textContent  = '-₹' + discount.toFixed(2);
    savingsAmt.textContent    = '₹' + discount.toFixed(2);
  } else {
    discountRow.style.display = 'none';
    savingsTag.style.display  = 'none';
  }
}

function renderCouponState() {
  const inputRow    = document.getElementById('coupon-input-row');
  const successEl   = document.getElementById('coupon-success');
  const successText = document.getElementById('coupon-success-text');
  const errorEl     = document.getElementById('coupon-error');

  errorEl.style.display = 'none';

  if (couponData) {
    inputRow.style.display  = 'none';
    successEl.style.display = 'flex';
    successText.textContent = `✅ ${couponData.code} — ${couponData.desc}`;
  } else {
    inputRow.style.display  = 'flex';
    successEl.style.display = 'none';
  }
}

/* ── Cart actions ── */
function removeItem(barcode) {
  fetch('/api/cart/remove', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: SESSION_ID, barcode }),
  }).then(r => r.json()).then(data => {
    if (data.success) {
      cart = data.cart;
      couponData ? recalcDiscount() : renderPage();
      showToast('🗑️ Item removed');
    }
  });
}

function changeQty(barcode, delta) {
  const item = cart.find(i => i.barcode === barcode);
  if (!item) return;
  if (delta === -1 && item.quantity === 1) { removeItem(barcode); return; }

  if (delta === 1) {
    fetch('/api/cart/add', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: SESSION_ID, barcode }),
    }).then(r => r.json()).then(d => {
      if (d.success) { cart = d.cart; couponData ? recalcDiscount() : renderPage(); }
    });
    return;
  }

  // Decrease
  fetch('/api/cart/remove', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: SESSION_ID, barcode }),
  }).then(() => {
    let chain = Promise.resolve();
    for (let i = 0; i < item.quantity - 1; i++) {
      chain = chain.then(() => fetch('/api/cart/add', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: SESSION_ID, barcode }),
      }));
    }
    chain.then(() => fetchCart());
  });
}

function recalcDiscount() {
  if (!couponData) { fetchCart(); return; }
  fetch('/api/coupon/apply', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: SESSION_ID, code: couponData.code }),
  }).then(r => r.json()).then(d => {
    discount = d.success ? d.discount : 0;
    fetchCart();
  });
}

/* ── Coupon ── */
function applyCoupon() {
  const code    = document.getElementById('coupon-input').value.trim().toUpperCase();
  const errorEl = document.getElementById('coupon-error');

  if (!code) { errorEl.style.display = ''; errorEl.textContent = 'Please enter a coupon code.'; return; }
  if (cart.length === 0) { errorEl.style.display = ''; errorEl.textContent = 'Add products to cart first.'; return; }

  fetch('/api/coupon/apply', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: SESSION_ID, code }),
  }).then(r => r.json()).then(data => {
    if (data.success) {
      discount   = data.discount;
      couponData = { code, desc: data.desc };
      errorEl.style.display = 'none';
      renderPage();
      showToast('🎉 ' + data.message, 'success');
    } else {
      errorEl.style.display = '';
      errorEl.textContent   = '❌ ' + data.message;
    }
  });
}

function removeCoupon() {
  fetch('/api/coupon/remove', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: SESSION_ID }),
  }).then(r => r.json()).then(() => {
    discount   = 0;
    couponData = null;
    document.getElementById('coupon-input').value = '';
    renderPage();
    showToast('Coupon removed');
  });
}

/* ── Proceed to checkout ── */
function goToCheckout() {
  if (!cart || cart.length === 0) {
    showToast('❌ Your cart is empty', 'error'); return;
  }
  window.location.href = '/checkout/' + SESSION_ID;
}

/* ── Toast ── */
let toastTimer = null;
function showToast(msg, type) {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.className   = 'toast show' + (type ? ' ' + type : '');
  if (toastTimer) clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { el.className = 'toast'; }, 3200);
}