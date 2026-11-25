// Tempered offline support.
// Pages, scripts and the catalogue are served network-first and fall back to the cache,
// so the site works without internet once it has been opened, and updates show as soon as you're online.
const CACHE = 'tempered-v6';
const CORE = [
  './', 'index.html', 'labels.html', 'storage.html', 'changes.html',
  'assets/site.css', 'assets/catalogue.js', 'data/catalogue.json', 'data/changelog.json',
  'favicon.svg', 'favicon.ico', 'apple-touch-icon.png', 'site.webmanifest'
];
// The label maker's PDF, QR code and barcode libraries, so labels still print in full offline
const LIBS = [
  'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js',
  'https://cdnjs.cloudflare.com/ajax/libs/qrcode-generator/1.4.4/qrcode.min.js',
  'https://cdnjs.cloudflare.com/ajax/libs/jsbarcode/3.11.6/JsBarcode.all.min.js'
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(async c => {
    await c.addAll(CORE);
    // cdnjs allows CORS, so these come back as real (checkable) responses; a failure here doesn't block install
    await Promise.all(LIBS.map(u => fetch(u, {mode: 'cors'}).then(r => r.ok && c.put(u, r)).catch(() => {})));
  }).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  const own = url.origin === location.origin;
  // Our files, the PDF, QR and barcode libraries, and fonts. Everything else goes straight to the network.
  const cdn = /(^|\.)cdnjs\.cloudflare\.com$|(^|\.)fonts\.(googleapis|gstatic)\.com$/.test(url.hostname);
  if (!own && !cdn) return;
  // Pages are stored once each, without their ?q= search or #hash, so every QR scan doesn't add a copy
  const page = own && (req.mode === 'navigate' || url.pathname.endsWith('.html') || url.pathname.endsWith('/'));
  const key = page ? url.origin + url.pathname : req;
  const fonts = /fonts\.(googleapis|gstatic)\.com$/.test(url.hostname);
  e.respondWith(fetch(req).then(res => {
    // Keep only good responses. Fonts come back opaque (status unknown), so they're the one exception.
    if (res.ok || (fonts && res.type === 'opaque')) {
      const copy = res.clone();
      caches.open(CACHE).then(c => c.put(key, copy));
    }
    return res;
  }).catch(() => caches.match(key, {ignoreVary: true})
    .then(hit => hit || (page ? caches.match(new URL('index.html', self.registration.scope).href) : Response.error()))));
});
