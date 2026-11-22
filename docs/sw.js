// Tempered offline support.
// Pages, scripts and the catalogue are served network-first and fall back to the cache,
// so the site works without internet once it has been opened, and updates show as soon as you're online.
const CACHE = 'tempered-v2';
const CORE = [
  './', 'index.html', 'labels.html', 'storage.html', 'changes.html',
  'assets/site.css', 'assets/catalogue.js', 'data/catalogue.json', 'data/changelog.json',
  'favicon.svg', 'favicon.ico', 'apple-touch-icon.png', 'site.webmanifest'
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(CORE)).then(() => self.skipWaiting()));
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
  // Our files, the PDF and QR libraries, and fonts. Everything else goes straight to the network.
  const cdn = /(^|\.)cdnjs\.cloudflare\.com$|(^|\.)fonts\.(googleapis|gstatic)\.com$/.test(url.hostname);
  if (!own && !cdn) return;
  e.respondWith(fetch(req).then(res => {
    if (res.ok || res.type === 'opaque') {
      const copy = res.clone();
      caches.open(CACHE).then(c => c.put(req, copy));
    }
    return res;
  }).catch(() => {
    // Offline: pages match without their ?q= search, so a search link still opens the cached page
    const page = own && (url.pathname.endsWith('.html') || url.pathname.endsWith('/'));
    return caches.match(req, {ignoreSearch: page})
      .then(hit => hit || (req.mode === 'navigate' ? caches.match('index.html') : Response.error()));
  }));
});
