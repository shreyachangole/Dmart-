/* ─────────────────────────────────────────────
   D-mart Smart Scanner — scanner.js
───────────────────────────────────────────── */
 
let SESSION_ID      = '';
let cart            = [];
let scannerActive   = false;
let allProducts     = {};
let detectedHandler = null;
 
let lastBarcode   = '';
let lastScanTime  = 0;
let addInProgress = false;
 
const SCAN_COOLDOWN_MS = 4000;
 
/* ── INIT ── */
function initScanner(sessionId) {
  SESSION_ID = sessionId;
  fetch('/api/products')
    .then(r => r.json())
    .then(d => { allProducts = d; });
  fetch('/api/cart/' + SESSION_ID)
    .then(r => r.json())
    .then(d => { cart = d.cart || []; renderCart(); });
}
 
/* ── CAMERA ── */
function startCamera() {
  setBanner('', 'Requesting camera permission…', false);
 
  if (detectedHandler) {
    Quagga.offDetected(detectedHandler);
    detectedHandler = null;
  }
 
  Quagga.init({
    inputStream: {
      type   : 'LiveStream',
      target : document.getElementById('interactive'),
      constraints: { facingMode: 'environment', width: { ideal: 1280 }, height: { ideal: 720 } },
    },
    decoder: {
      readers: ['ean_reader','ean_8_reader','code_128_reader','upc_reader','upc_e_reader','code_39_reader'],
    },
    locate: true,
  }, function(err) {
    if (err) {
      console.error('Quagga init error:', err);
      setBanner('error', 'Camera permission denied or not available.', false);
      showToast('Camera access denied. Use Search instead.', 'error');
      return;
    }
    Quagga.start();
    scannerActive   = true;
    detectedHandler = onBarcodeDetected;
    Quagga.onDetected(detectedHandler);
 
    document.getElementById('idle-state').style.display   = 'none';
    document.getElementById('interactive').style.display  = 'block';
    document.getElementById('scan-overlay').style.display = 'flex';
    document.getElementById('btn-start').style.display    = 'none';
    document.getElementById('btn-stop').style.display     = '';
    setBanner('active', 'Camera active — point at a product barcode', true);
  });
}
 
function stopCamera() {
  if (detectedHandler) { Quagga.offDetected(detectedHandler); detectedHandler = null; }
  if (scannerActive)   { Quagga.stop(); scannerActive = false; }
  addInProgress = false;
 
  document.getElementById('idle-state').style.display   = '';
  document.getElementById('interactive').style.display  = 'none';
  document.getElementById('scan-overlay').style.display = 'none';
  document.getElementById('btn-start').style.display    = '';
  document.getElementById('btn-stop').style.display     = 'none';
  setBanner('', 'Scanner stopped. Press "Start Scanning" to resume.', false);
}
 
function onBarcodeDetected(result) {
  const code = result.codeResult.code;
  const now  = Date.now();
 
  if (!/^\d{8,14}$/.test(code))                                       return;
  if (addInProgress)                                                   return;
  if (code === lastBarcode && (now - lastScanTime) < SCAN_COOLDOWN_MS) return;
 
  console.log('[Scanner] Barcode:', code);
  addToCart(code, 'scan');
}
 
/* ── SEARCH ── */
function onSearchInput() {
  const query      = document.getElementById('search-input').value.trim().toLowerCase();
  const resultsEl  = document.getElementById('search-results');
  const noResultEl = document.getElementById('no-results');
 
  if (!query) { resultsEl.style.display = 'none'; noResultEl.style.display = 'none'; return; }
 
  const matches = Object.entries(allProducts).filter(([bc, p]) =>
    p.name.toLowerCase().includes(query)     ||
    p.brand.toLowerCase().includes(query)    ||
    p.category.toLowerCase().includes(query) ||
    bc.includes(query)                       ||
    p.code.toLowerCase().includes(query)
  );
 
  if (matches.length === 0) { resultsEl.style.display = 'none'; noResultEl.style.display = ''; return; }
 
  noResultEl.style.display = 'none';
  resultsEl.style.display  = 'flex';
 
  resultsEl.innerHTML = matches.map(([bc, p]) => `
    <div class="search-result-item">
      <img class="product-img" src="${p.image_url}" alt="${p.name}"
           onerror="this.style.background='#eee';this.src=''" />
      <div class="result-info">
        <div class="result-name">${p.name}</div>
        <div class="result-meta">${p.brand} &middot; ${p.code}</div>
      </div>
      <span class="result-price">&#x20B9;${p.price.toFixed(2)}</span>
      <button class="btn-add-product" onclick="addToCart('${bc}','search')">+ Add</button>
    </div>
  `).join('');
}
 
/* ── CART API ── */
function addToCart(barcode, source) {
  if (source === 'scan') {
    addInProgress = true;
    setBanner('active', 'Adding to cart…', true);
  }
 
  fetch('/api/cart/add', {
    method  : 'POST',
    headers : { 'Content-Type': 'application/json' },
    body    : JSON.stringify({ session_id: SESSION_ID, barcode }),
  })
  .then(r => { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
  .then(data => {
    if (data.success) {
      cart = data.cart;
      if (source === 'scan') { lastBarcode = barcode; lastScanTime = Date.now(); }
      renderCart();
      const item  = cart.find(i => i.barcode === barcode);
      const name  = item ? item.name : barcode;
      showToast((source === 'scan' ? 'Scanned: ' : 'Added: ') + name);
      if (source === 'scan') setBanner('active', 'Added: ' + name + ' — scan next item', true);
    } else {
      showToast('Product not found: ' + barcode, 'error');
      if (source === 'scan') setBanner('active', 'Not found. Try another item.', true);
    }
  })
  .catch(err => {
    console.error('[Cart] Add failed:', err);
    showToast('Network error — check connection.', 'error');
  })
  .finally(() => { if (source === 'scan') addInProgress = false; });
}
 
function removeFromCart(barcode) {
  fetch('/api/cart/remove', {
    method  : 'POST',
    headers : { 'Content-Type': 'application/json' },
    body    : JSON.stringify({ session_id: SESSION_ID, barcode }),
  })
  .then(r => r.json())
  .then(data => { if (data.success) { cart = data.cart; renderCart(); showToast('Item removed'); } });
}
 
function changeQty(barcode, delta) {
  const item = cart.find(i => i.barcode === barcode);
  if (!item) return;
  if (delta === -1 && item.quantity === 1) { removeFromCart(barcode); return; }
  if (delta === 1) { addToCart(barcode, 'qty'); return; }
 
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
    chain.then(() =>
      fetch('/api/cart/' + SESSION_ID).then(r => r.json())
        .then(d => { cart = d.cart || []; renderCart(); })
    );
  });
}
 
/* ── RENDER CART ── */
function renderCart() {
  const listEl   = document.getElementById('cart-list');
  const emptyEl  = document.getElementById('cart-empty');
  const totalsEl = document.getElementById('cart-totals');
  const badgeEl  = document.getElementById('cart-count-badge');
  const totalQty = cart.reduce((s, i) => s + i.quantity, 0);
 
  // Badge on View Cart button
  badgeEl.style.display = totalQty > 0 ? 'grid' : 'none';
  badgeEl.textContent   = totalQty;
 
  if (!cart || cart.length === 0) {
    emptyEl.style.display  = 'flex';
    listEl.style.display   = 'none';
    totalsEl.style.display = 'none';
    listEl.innerHTML = '';
    return;
  }
 
  // Hide empty state, show list + totals
  emptyEl.style.display  = 'none';
  listEl.style.display   = 'flex';
  totalsEl.style.display = 'flex';
 
  // Build each cart item
  listEl.innerHTML = cart.map(item => {
    const lineTotal  = (item.total + item.tax_amount).toFixed(2);
    const unitPrice  = item.price.toFixed(2);
    const imgSrc     = item.image_url || '';
    const brand      = item.brand    || '';
    const name       = item.name     || '';
    const barcode    = item.barcode  || '';
    const qty        = item.quantity || 1;
 
    return `<div class="cart-item">
      <img class="product-img-sm"
           src="${imgSrc}"
           alt="${name}"
           onerror="this.style.background='#e8f5ec';this.style.border='1px solid #b2d9bc'" />
      <div class="item-info">
        <div class="item-name">${name}</div>
        <div class="item-brand-tag">${brand}</div>
        <div class="item-unit">&#x20B9;${unitPrice} each</div>
      </div>
      <div class="item-right">
        <div class="item-price">&#x20B9;${lineTotal}</div>
        <div class="qty-row">
          <button class="qty-btn" onclick="changeQty('${barcode}',-1)">&#8722;</button>
          <span class="qty-num">${qty}</span>
          <button class="qty-btn" onclick="changeQty('${barcode}',1)">&#43;</button>
          <button class="btn-delete" onclick="removeFromCart('${barcode}')" title="Remove">&#128465;</button>
        </div>
      </div>
    </div>`;
  }).join('');
 
  // Totals — use innerHTML so ₹ symbol renders correctly
  const subtotal   = cart.reduce((s, i) => s + i.total, 0);
  const totalTax   = cart.reduce((s, i) => s + i.tax_amount, 0);
  const grandTotal = subtotal + totalTax;
 
  document.getElementById('subtotal-val').innerHTML = '&#x20B9;' + subtotal.toFixed(2);
  document.getElementById('gst-val').innerHTML      = '&#x20B9;' + totalTax.toFixed(2);
  document.getElementById('grand-val').innerHTML    = '&#x20B9;' + grandTotal.toFixed(2);
}
 
/* ── HELPERS ── */
function setBanner(state, text, dotActive) {
  document.getElementById('banner-text').textContent = text;
  document.getElementById('banner-dot').className =
    'banner-dot' + (dotActive ? ' active' : '') + (state === 'error' ? ' error' : '');
}
 
let toastTimer = null;
function showToast(msg, type) {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.className   = 'toast show' + (type === 'error' ? ' error' : '');
  if (toastTimer) clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { el.className = 'toast'; }, 3500);
}