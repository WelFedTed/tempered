// Shared catalogue loading and search for the Tempered pages.
window.Tempered = (() => {
  // Fit tags: caveats to know before fitting. [label on the site, short form for printed labels]
  const TAGS = {
    fingerprint: ['Ultrasonic fingerprint: use FP-compatible glass', 'FP-SAFE'],
    cover: ['Cover screen only', 'COVER'],
    'two-screens': ['Two screens: top and bottom sets', '2 SCREENS'],
    'case-friendly': ['Case-friendly glass', 'CASE-FRIENDLY'],
    curved: ['Curved screen', 'CURVED'],
    uv: ['UV glue glass', 'UV'],
    measure: ['Measure first', 'MEASURE']
  };
  const SITE = 'https://welfedted.github.io/tempered/';
  const REPO = 'https://github.com/WelFedTed/tempered';
  // A pre-filled "Fit report" issue form (.github/ISSUE_TEMPLATE/fit-report.yml) for a group
  const reportUrl = g => REPO + '/issues/new?' + new URLSearchParams({
    template: 'fit-report.yml', title: `Fit report: ${g.id}`, group: g.id, models: g.models.map(m => m[0]).join('\n')
  });
  // Service worker: keeps the site and catalogue usable offline
  if ('serviceWorker' in navigator && location.protocol === 'https:') navigator.serviceWorker.register('sw.js').catch(() => {});
  const DEVICE = {Phone: 'Phone', Tablet: 'Tablet', Wearable: 'Wearable', Handheld: 'Handheld', Misc: 'Misc', Laptop: 'Laptop'};
  const MON = 'Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split(' ');

  const esc = s => String(s).replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));
  const norm = s => String(s).normalize('NFKD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/\+/g, ' plus ').replace(/[^a-z0-9]+/g, ' ').trim();
  const terms = q => norm(q).split(' ').filter(Boolean);
  const compact = s => norm(s).replace(/ /g, '');
  // Model numbers compare without spaces or punctuation, except commas (so iPhone1,2 is not iPhone12)
  const codeKey = s => String(s).toLowerCase().replace(/[^a-z0-9,]/g, '');
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
    const groups = d.groups.map(([id, brands, dev, check, note, models, sources = [], tags = []]) => {
      modelCount += models.length;
      brands.forEach(b => used.add(b));
      const brandName = brands.map(b => brandNames[b] || b).join(' + ');
      const hay = norm(id + ' ' + brandName + ' ' + models.map(m => m[0]).join(' '));
      const dates = models.map(m => m[1]).filter(r => r && !r.startsWith('1900')).sort();
      // Model numbers (e.g. A2221, SM-S938B/DS, iPhone12,1): compact full form and the part before / or (
      const codes = models.map(m => (m[2] || '').split(', ').filter(Boolean));
      const ccodes = codes.map(list => list.map(c => [codeKey(c), codeKey(c.split(/[\/(]/)[0])]));
      return {id, brands, dev, check, note, models, sources, tags, brandName, hay, hayC: hay.replace(/ /g, ''), codes, ccodes,
        mnorm: models.map(m => norm(m[0])), mcomp: models.map(m => compact(m[0])), earliest: dates[0] || '', latest: dates[dates.length - 1] || ''};
    });
    const brandOrder = d.brands.map(b => b[0]).filter(c => used.has(c))
      .sort((a, b) => brandNames[a].localeCompare(brandNames[b], 'en', {sensitivity: 'base'}));
    return {built: d.built, groups, brandNames, brandNotes, brandOrder, modelCount, byId: Object.fromEntries(groups.map(g => [g.id, g]))};
  }

  // How the query matches one model's numbers, ignoring spaces and punctuation other than commas:
  // 3 = a whole model number, 2 = the start of one, 1 = part of one (3+ characters), 0 = no match
  function codeHit(cc, qc) {
    if (qc.length < 3) return 0;
    let hit = 0;
    for (const e of cc) {
      if (!e) continue;  // model numbers switched off ("Include model numbers")
      const [full, base] = e;
      if (full === qc || base === qc) return 3;
      if (full.startsWith(qc)) hit = 2;
      else if (!hit && full.includes(qc)) hit = 1;
    }
    return hit;
  }
  // Partial model numbers rank below name matches, so "A22" finds the Galaxy A22 before the A22xx iPhones
  const CODE_SCORE = [0, 25, 45, 950];
  // Words of a search as typed ("samsung sm-S92" -> samsung, sm-S92), for searches that mix a name and a model number
  const words = q => String(q).trim().split(/\s+/).map(w => ({ts: terms(w), key: codeKey(w)})).filter(w => w.ts.length);
  const nameOk = (g, w) => w.ts.every(t => g.hay.includes(t) || g.hayC.includes(t));
  // Mixed search: every word matches the name/brand or a model number, and at least one is a model number
  function mixedScore(g, ws) {
    if (ws.length < 2) return 0;
    let worst = 3;
    for (const w of ws) {
      if (nameOk(g, w)) continue;
      const h = Math.max(0, ...g.ccodes.map(cc => codeHit(cc, w.key)));
      if (!h) return 0;
      worst = Math.min(worst, h);
    }
    return [0, 25, 45, 900][worst];
  }
  // The model numbers of each model in g that match the query, for display
  // Commas only count inside an identifier like iPhone12,1, so "A2221, A2223" and "A2221," still match
  const tidy = q => String(q).replace(/,(?![a-z0-9])|(?<![a-z0-9]),/gi, ' ');
  function codeMatches(g, q) {
    q = tidy(q);
    const qc = codeKey(q), ts = terms(q), tc = ts.join('');
    const keys = words(q).filter(w => !nameOk(g, w)).map(w => w.key).filter(k => k.length >= 3);
    // When the group already matches by name ("iphone 11"), only an exact model number is worth showing
    const named = ts.every(t => g.hay.includes(t) || g.hayC.includes(t));
    return g.codes.map((list, i) => {
      const hit = codeHit(g.ccodes[i], qc);
      if (named && hit < 3) return [];
      // Skip partial number matches on a model whose name already matches: they explain nothing
      if (hit && !(hit < 3 && (ts.every(t => g.mnorm[i].includes(t)) || g.mcomp[i].includes(tc))))
        return list.filter((c, j) => codeHit([g.ccodes[i][j]], qc));
      return keys.length ? list.filter((c, j) => keys.some(k => codeHit([g.ccodes[i][j]], k))) : [];
    });
  }

  function score(g, qn, ts, qk, ws) {
    if (!ts.length) return 1;
    const qc = ts.join('');
    const ch = Math.max(0, ...g.ccodes.map(cc => codeHit(cc, qk)));
    if (ch === 3) return CODE_SCORE[3];
    const all = ts.every(t => g.hay.includes(t) || g.hayC.includes(t));
    if (!all && !g.hayC.includes(qc)) return CODE_SCORE[ch] || mixedScore(g, ws);
    if (norm(g.id) === qn) return 1000;
    let best = 1;
    const starts = ts.map(t => new RegExp('(^| )' + t));
    g.mnorm.forEach((mn, i) => {
      let s = 0;
      const mc = g.mcomp[i];
      if (mn === qn) s = 100;
      else if (mc === qc) s = 90;
      else if ((' ' + mn + ' ').includes(' ' + qn + ' ')) s = 60 - Math.min(20, (mn.length - qn.length) / 3);
      else if (starts.every(r => r.test(mn))) s = 40;
      else if (mc.startsWith(qc)) s = 38;
      else if (ts.every(t => mn.includes(t))) s = 20;
      if (s > best) best = s;
    });
    best = Math.max(best, CODE_SCORE[ch]);
    // Universal glass is the fallback: rank a model's own group above it.
    return g.brands[0] === 'UNI' && best > 5 ? best - 5 : best;
  }

  function search(cat, q, {dev = '', brand = ''} = {}) {
    // A search of only punctuation ("(", ",") matches nothing, rather than every group
    if (String(q).trim() && !terms(q).length) return [];
    q = tidy(q);
    const ts = terms(q), qn = ts.join(' '), qk = codeKey(q), ws = words(q);
    const out = [];
    for (const g of cat.groups) {
      if (dev && g.dev !== dev) continue;
      if (brand && !g.brands.includes(brand)) continue;
      const s = score(g, qn, ts, qk, ws);
      if (s) out.push([s, g]);
    }
    out.sort((a, b) => b[0] - a[0] || b[1].latest.localeCompare(a[1].latest) || a[1].id.localeCompare(b[1].id));
    return out.map(x => x[1]);
  }

  return {TAGS, SITE, REPO, reportUrl, DEVICE, esc, norm, terms, month, highlight, linkCodes, load, search, codeMatches};
})();
