// Shared catalogue loading and search for the Tempered pages.
window.Tempered = (() => {
  const DEVICE = {Phone: 'Phone', Tablet: 'Tablet', Wearable: 'Wearable', Handheld: 'Handheld', Misc: 'Misc', Laptop: 'Laptop'};
  const MON = 'Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split(' ');

  const esc = s => String(s).replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));
  const norm = s => String(s).normalize('NFKD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/\+/g, ' plus ').replace(/[^a-z0-9]+/g, ' ').trim();
  const terms = q => norm(q).split(' ').filter(Boolean);
  const month = r => { const [y, m] = r.split('-'); return m ? `${MON[+m - 1]} ${y}` : y; };
  const linkCodes = html => html.replace(/\b([A-Z]{3}-\d{4})\b/g, '<a href="./?q=$1" data-code="$1">$1</a>');

  function highlight(text, ts) {
    if (!ts.length) return esc(text);
    const re = new RegExp('(' + [...ts].sort((a, b) => b.length - a.length).map(t => t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|') + ')', 'gi');
    return String(text).split(re).map((p, i) => i % 2 ? `<mark>${esc(p)}</mark>` : esc(p)).join('');
  }

  async function load(base = '') {
    const res = await fetch(base + 'data/catalogue.json');
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const d = await res.json();
    const brandNames = {}, brandNotes = {};
    for (const [c, n, note] of d.brands) { brandNames[c] = n; brandNotes[c] = note || ''; }
    let modelCount = 0;
    const used = new Set();
    const groups = d.groups.map(([id, brands, dev, check, note, models]) => {
      modelCount += models.length;
      brands.forEach(b => used.add(b));
      const brandName = brands.map(b => brandNames[b] || b).join(' + ');
      const hay = norm(id + ' ' + brandName + ' ' + models.map(m => m[0]).join(' '));
      const dates = models.map(m => m[1]).filter(r => r && !r.startsWith('1900')).sort();
      return {id, brands, dev, check, note, models, brandName, hay, hayC: hay.replace(/ /g, ''),
        mnorm: models.map(m => norm(m[0])), earliest: dates[0] || '', latest: dates[dates.length - 1] || ''};
    });
    const brandOrder = d.brands.map(b => b[0]).filter(c => used.has(c))
      .sort((a, b) => brandNames[a].localeCompare(brandNames[b], 'en', {sensitivity: 'base'}));
    return {built: d.built, groups, brandNames, brandNotes, brandOrder, modelCount, byId: Object.fromEntries(groups.map(g => [g.id, g]))};
  }

  function score(g, qn, ts) {
    if (!ts.length) return 1;
    const qc = ts.join('');
    const all = ts.every(t => g.hay.includes(t) || g.hayC.includes(t));
    if (!all && !g.hayC.includes(qc)) return 0;
    if (norm(g.id) === qn) return 1000;
    let best = 1;
    const starts = ts.map(t => new RegExp('(^| )' + t));
    for (const mn of g.mnorm) {
      let s = 0;
      if (mn === qn) s = 100;
      else if ((' ' + mn + ' ').includes(' ' + qn + ' ')) s = 60 - Math.min(20, (mn.length - qn.length) / 3);
      else if (starts.every(r => r.test(mn))) s = 40;
      else if (ts.every(t => mn.includes(t))) s = 20;
      if (s > best) best = s;
    }
    // Universal glass is the fallback: rank a model's own group above it.
    return g.brands[0] === 'UNI' && best > 5 ? best - 5 : best;
  }

  function search(cat, q, {dev = '', brand = ''} = {}) {
    const ts = terms(q), qn = ts.join(' ');
    const out = [];
    for (const g of cat.groups) {
      if (dev && g.dev !== dev) continue;
      if (brand && !g.brands.includes(brand)) continue;
      const s = score(g, qn, ts);
      if (s) out.push([s, g]);
    }
    out.sort((a, b) => b[0] - a[0] || b[1].latest.localeCompare(a[1].latest) || a[1].id.localeCompare(b[1].id));
    return out.map(x => x[1]);
  }

  return {DEVICE, esc, norm, terms, month, highlight, linkCodes, load, search};
})();
