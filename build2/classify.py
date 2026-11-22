import json,re
def fnum(s):
    m=re.search(r'([\d.]+)\s*inches',s or ''); return float(m.group(1)) if m else None
def classify(r):
    s=r['specs']; n=r['model'].lower()
    os_=(s.get('Platform',{}).get('OS') or '')
    size=fnum(s.get('Display',{}).get('Size'))
    body=json.dumps(s.get('Body',{})).lower()
    net=s.get('Network',{}).get('Technology','')
    if re.search(r'watch|gear (s|live|fit|2|sport)|gear$|band|fit\b|moto 360|zenwatch|smartwatch|vivowatch', n) and (size is None or size<2.2): return 'watch'
    if re.search(r'watch|nubia alpha', n) and 'proprietary' in os_.lower(): return 'watch'
    if re.search(r'watchos|wear ?os|android wear|tizen.*watch', os_.lower()): return 'watch'
    smart=bool(re.search(r'android|ios|ipados|windows|symbian|blackberry|webos|tizen|bada|maemo|meego|linux|firefox|sailfish|harmony|ubuntu|chrome|palm|uiq|series 60|s60|s40|hyperos|coloros', os_.lower()))
    rm=re.search(r'~([\d.]+)%', s.get('Display',{}).get('Size') or ''); ratio=float(rm.group(1)) if rm else 0
    if size and size<7.5 and ratio>=80: size=6.99
    fold=re.search(r'fold|\bopen\b|find n|mix alpha|flip|trifold|razr|mate x|magic v|huawei.*pocket', n)
    if smart and not fold and ((size and size>=7.0) or (re.search(r'\b(tab|pad|tablet|ipad|xoom|slate|vivotab|surface)\b', n) and (size is None or size>=5))): return 'tablet'
    if smart: return 'smartphone'
    return 'phone'

MON={m:i+1 for i,m in enumerate('January February March April May June July August September October November December'.split())}
def date(r):
    L=r['specs'].get('Launch',{})
    for f in ('Announced','Status'):
        t=L.get(f) or ''
        m=re.search(r'(\d{4}),\s*(January|February|March|April|May|June|July|August|September|October|November|December)',t)
        if m: return f"{m.group(1)}-{MON[m.group(2)]:02d}"
        m=re.search(r'(\d{4}),\s*Q([1-4])',t)
        if m: return f"{m.group(1)}-{int(m.group(2))*3-1:02d}"
        m=re.search(r'(\d{4})',t)
        if m: return f"{m.group(1)}-06"
    return None
