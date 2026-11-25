import json, re, sys, collections, html
import os as _os; ROOT = _os.environ.get('PROTECTOR_ROOT', _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
sys.path.insert(0, ROOT + '/build')
import newmodels as NM

BASE = json.load(open(ROOT + '/ds/base.json', encoding='utf-8'))
MON = {m: i+1 for i, m in enumerate('Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split())}
CAT = {'P': 'Phone', 'T': 'Tablet', 'W': 'Wearable', 'H': 'Handheld', 'M': 'Misc'}
CATBASE = {'Misc': 0, 'Phone': 1000, 'Tablet': 2000, 'Wearable': 3000, 'Handheld': 4000}
CODE = {'Apple': 'APP', 'Samsung': 'SAM', 'Google': 'GOO', 'Oppo': 'OPP', 'OnePlus': 'ONE', 'ZTE': 'ZTE',
        'Microsoft': 'MIC', 'Lenovo': 'LEN', 'Asus': 'ASU', 'Motorola': 'MOT', 'Xiaomi': 'XIA'}
C, K = 'Confirmed', 'Check'

models = []   # dict(code, name, cat, date, seq)
seq = 0
def add(code, name, cat, date):
    global seq
    seq += 1
    models.append(dict(code=code, name=name.strip(), cat=cat, date=date, seq=seq))

def disp(brand, n):
    n = re.sub(r'^razr', 'Razr', n)
    if brand == 'Oppo': return n if n.startswith('Oppo') else 'Oppo ' + n
    if brand == 'OnePlus': return 'OnePlus ' + n
    if brand == 'ZTE': return n if re.match(r'nubia|Telstra|Optus', n) else 'ZTE ' + n
    if brand == 'Motorola': return n if n.lower().startswith('moto') else 'Motorola ' + n
    if brand == 'Xiaomi': return n if re.match(r'Redmi|Poco|Black Shark', n) else 'Xiaomi ' + n
    if brand == 'Lenovo': return 'Lenovo ' + n
    if brand == 'Asus': return 'Asus ' + n
    if brand == 'Microsoft': return n if n.startswith('Surface') else 'Microsoft ' + n
    if brand == 'Sony': return n if n.startswith(('Xperia', 'Sony')) else 'Sony ' + n
    if brand == 'Razer': return 'Razer ' + n
    if brand == 'Sony Ericsson': return 'Sony Ericsson ' + n
    if brand == 'Samsung': return n if re.match(r'Galaxy|Gear', n) or re.match(r'^[A-Z]{1,2}\d{3,5}[A-Z]? Galaxy', n) else 'Samsung ' + n
    return n

# Samsung watch case sizes
SAMW = {'Galaxy Watch': [42, 46], 'Galaxy Watch Active2': [40, 44], 'Galaxy Watch Active2 Aluminum': [40, 44],
        'Galaxy Watch3': [41, 45], 'Galaxy Watch4': [40, 44], 'Galaxy Watch4 Classic': [42, 46],
        'Galaxy Watch5': [40, 44], 'Galaxy Watch5 Pro': [45], 'Galaxy Watch6': [40, 44],
        'Galaxy Watch6 Classic': [43, 47], 'Galaxy Watch7': [40, 44], 'Galaxy Watch FE': [40],
        'Galaxy Watch Ultra': [47], 'Galaxy Watch Active': [40]}

# 1. Dataset (Sep 2024 snapshot); Apple, Google, Surface tablets are replaced by manual lists
BASE += json.load(open(ROOT + '/ds/extra.json', encoding='utf-8'))
CODE.update({'Sony': 'SON', 'Razer': 'RAZ', 'Sony Ericsson': 'SON'})
for r in reversed(BASE):  # base is newest-first; reverse so seq rises with age order
    b, t, ann = r['brand'], r['type'], r['ann']
    if b not in CODE or t == 'phone' or not ann: continue
    if b in ('Apple', 'Google'): continue
    if b == 'Microsoft' and (t == 'tablet' or (r['name'].startswith('Surface') and 'Duo' not in r['name'])): continue
    if 'Nexus' in r['name']: continue
    y, m = ann.split(); date = f"{y}-{MON[m]:02d}"
    cat = {'smartphone': 'Phone', 'tablet': 'Tablet', 'watch': 'Wearable'}[t]
    n = r['name']
    if b == 'Samsung' and t == 'watch':
        if n == 'Watch Phone': continue
        if n in SAMW:
            for s in SAMW[n]: add('SAM', f"{n} {s}mm", cat, date)
            continue
    add(CODE[b], disp(b, n), cat, date)

# 1b. Full GSMArena catalogue (Jul 2026): add devices the snapshot and manual lists miss
import sys as _s; _s.path.insert(0, ROOT + '/build2')
from classify import classify as _cls, date as _date
CODE.update({'Nvidia': 'NVI', 'Acer': 'ACE', 'Garmin-Asus': 'GAR'})
NEWB = {'Nokia': 'NOK', 'HMD': 'NOK', 'vivo': 'VIV', 'Realme': 'REA', 'Huawei': 'HUA', 'Honor': 'HON', 'TCL': 'TCL',
        'alcatel': 'TCL', 'Nothing': 'NTH', 'LG': 'LGE', 'HTC': 'HTC', 'BlackBerry': 'BLB', 'Fairphone': 'FAI'}
NEWB2 = json.load(open(ROOT + '/build2/newcodes.json', encoding='utf-8')); NEWB2['BenQ-Siemens'] = 'BEN'
NEWB.update(NEWB2)
CODE.update(NEWB)
WSIZE = {'Huawei Watch GT 2': [42, 46], 'Huawei Watch GT 3': [42, 46], 'Huawei Watch GT 3 Pro': [43, 46],
         'Huawei Watch GT 4': [41, 46], 'Huawei Watch GT 5': [41, 46], 'Huawei Watch GT 5 Pro': [42, 46],
         'Huawei Watch GT 6': [41, 46], 'Honor MagicWatch 2': [42, 46]}
# Brand words dropped before comparing names, only within that brand (a global strip of "vivo" merged BLU's
# Vivo Selfie into its Selfie)
_OWN = {'OPP': 'oppo', 'ONE': 'oneplus', 'ZTE': 'zte', 'XIA': 'xiaomi', 'MOT': 'motorola|moto', 'LEN': 'lenovo',
        'ASU': 'asus', 'SAM': 'samsung', 'SON': 'sony ericsson|sony', 'NVI': 'nvidia', 'ACE': 'acer',
        'GAR': 'garmin-asus|garmin', 'MIC': 'microsoft', 'RAZ': 'razer', 'NOK': 'nokia|hmd', 'VIV': 'vivo',
        'REA': 'realme', 'HUA': 'huawei', 'HON': 'honor', 'TCL': 'tcl|alcatel', 'NTH': 'nothing', 'LGE': 'lg',
        'HTC': 'htc', 'BLB': 'blackberry', 'FAI': 'fairphone'}
def _norm(code, n):
    n = n.lower()
    if code in _OWN: n = re.sub(r'\b(' + _OWN[code] + r')\b', '', n)
    return re.sub(r'[^a-z0-9+]', '', n)
CATALOG_ADDED = []
def add_catalog():
    have = {(m['code'], _norm(m['code'], m['name'])) for m in models}
    have |= {(m['code'], _norm(m['code'], re.sub(r' \d+mm$', '', m['name']))) for m in models if m['cat'] == 'Wearable'}
    cat = json.load(open(ROOT + '/ds/gsmarena-catalog-builder/catalogs/gsmarena-full-catalog.gscatalog', encoding='utf-8'))['devices']
    for r in cat:
        b = r['brand']
        if b not in CODE or b in ('Apple', 'Google', 'Nvidia'): continue
        st = r['specs'].get('Launch', {}).get('Status', '')
        if re.search(r'Cancelled|Rumored', st): continue
        d = _date(r)
        if not d: continue
        t = _cls(r)
        if t == 'phone': continue
        if b == 'Amazon' and 'Fire Phone' not in r['model']: t = 'tablet'
        nm = r['model'][len(b)+1:] if r['model'].startswith(b + ' ') else r['model']
        if b == 'Microsoft' and (t == 'tablet' or nm.startswith('Surface')): continue
        if 'Nexus' in nm: continue
        code = CODE[b]; cat_ = {'smartphone': 'Phone', 'tablet': 'Tablet', 'watch': 'Wearable'}[t]
        if b in NEWB: name = re.sub(r'^alcatel ', 'Alcatel ', r['model'])
        else: name = 'NVIDIA ' + nm if b == 'Nvidia' else ('Garmin-Asus ' + nm if b == 'Garmin-Asus' else ('Acer ' + nm if b == 'Acer' else disp(b, nm)))
        if b == 'Samsung' and t == 'watch' and nm in SAMW:
            names = [f"{nm} {x}mm" for x in SAMW[nm]]
        elif name in WSIZE:
            names = [f"{name} {x}mm" for x in WSIZE[name]]
        else: names = [name]
        for nn in names:
            k = (code, _norm(code, nn))
            if k in have: continue
            have.add(k); add(code, nn, cat_, d); CATALOG_ADDED.append((code, cat_, d, nn))

# 2. Manual lists
def load(text, code):
    for line in text.strip().splitlines():
        d, c, n = line.split('|')
        add(code, n, CAT[c], d)
for txt, code in [(NM.APPLE, 'APP'), (NM.GOOGLE, 'GOO'), (NM.MICROSOFT, 'MIC'), (NM.OPEL, 'OPE'),
                  (NM.SAMSUNG, 'SAM'), (NM.OPPO, 'OPP'), (NM.ONEPLUS, 'ONE'), (NM.MOTOROLA, 'MOT'),
                  (NM.XIAOMI, 'XIA'), (NM.ZTE, 'ZTE'), (NM.LENOVO, 'LEN'), (NM.ASUS, 'ASU'), (NM.SONY, 'SON'), (NM.SONY_ERICSSON, 'SON'), (NM.NVIDIA, 'NVI')]:
    load(txt, code)
load(NM.ACER, 'ACE')
SETS = []
for txt, code in [(NM.GARMIN, 'GAR'), (NM.ZTE2, 'ZTE')]:
    for line in [l for l in txt.strip().splitlines() if l.strip()]:
        d, c, ns = line.split('|')
        names = ns.split(';')
        for n in names: add(code, n, CAT[c], d)
        if len(names) > 1: SETS.append((code, names))
for line in [l for l in (NM.HANDHELD + NM.HANDHELD2 + NM.HANDHELD3 + NM.HANDHELD4 + NM.EXTRA + NM.EXTRA2 + NM.HANDHELD5 + NM.IPOD + NM.EXTRA3 + NM.EXTRA4).splitlines() if l.strip()]:
    d, c, code, ns = line.split('|')
    names = ns.split(';')
    for n in names: add(code, n, CAT[c] if c in CAT else 'Handheld', d)
    if len(names) > 1: SETS.append((code, names))

add_catalog()
json.dump(CATALOG_ADDED, open(ROOT + '/build2/added.json', 'w', encoding='utf-8', newline='\n'))
# de-duplicate same code+name (manual list overlapping the snapshot)
seen = {}
for m in models:
    k = (m['code'], m['name'].lower())
    if k not in seen: seen[k] = m
    elif m['date'] < seen[k]['date']: seen[k]['date'] = m['date']
models = list(seen.values())
byname = {(m['code'], m['name']): m for m in models}

# 3. Shared-fit groups: (code, [models], status, note)
SHARED = [
 ('APP', ['iPhone 3G', 'iPhone 3GS'], C, 'iFixit lists both'),
 ('APP', ['iPhone 4', 'iPhone 4S'], C, 'Belkin, Supershieldz list both'),
 ('APP', ['iPhone 5', 'iPhone 5c', 'iPhone 5s', 'iPhone SE (1st gen)'], C, 'iFixit NuGlas lists all four'),
 ('APP', ['iPhone 6', 'iPhone 6s', 'iPhone 7', 'iPhone 8', 'iPhone SE (2nd gen)', 'iPhone SE (3rd gen)'], C, 'Belkin ScreenForce lists all six'),
 ('APP', ['iPhone 6 Plus', 'iPhone 6s Plus', 'iPhone 7 Plus', 'iPhone 8 Plus'], K, 'Sellers list these together: test before swapping'),
 ('APP', ['iPhone X', 'iPhone XS', 'iPhone 11 Pro'], C, 'Belkin list'),
 ('APP', ['iPhone XR', 'iPhone 11'], C, 'Belkin list'),
 ('APP', ['iPhone XS Max', 'iPhone 11 Pro Max'], C, 'Belkin list'),
 ('APP', ['iPhone 12', 'iPhone 12 Pro'], C, 'Belkin list'),
 ('APP', ['iPhone 13', 'iPhone 13 Pro', 'iPhone 14', 'iPhone 16e', 'iPhone 17e'], C, 'Belkin, PanzerGlass, Spigen list these together. ESR says its own 17e glass is 17e-only.'),
 ('APP', ['iPhone 13 Pro Max', 'iPhone 14 Plus'], C, 'Belkin list'),
 ('APP', ['iPhone 15', 'iPhone 16'], C, 'PanzerGlass list'),
 ('APP', ['iPhone 15 Plus', 'iPhone 16 Plus'], C, ''),
 ('APP', ['iPhone 16 Pro', 'iPhone 17'], C, 'Belkin sells one SKU for both'),
 ('APP', ['iPhone 17 Pro', 'iPhone 18 Pro'], C, 'Anker list. Some brands also list 17 Pro with 16 Pro/17: test first'),
 ('APP', ['iPhone 17 Pro Max', 'iPhone 18 Pro Max'], C, 'Anker list'),
 ('APP', ['iPad 2', 'iPad (3rd gen)', 'iPad (4th gen)'], C, 'JETech, SuperGuardZ list all three'),
 ('APP', ['iPad mini (1st gen)', 'iPad mini 2', 'iPad mini 3'], C, 'SuperGuardZ, BISEN list all three'),
 ('APP', ['iPad Air', 'iPad Air 2', 'iPad Pro 9.7', 'iPad (5th gen)', 'iPad (6th gen)'], C, '9.7in. SaharaCase, Targus list all five'),
 ('APP', ['iPad mini 4', 'iPad mini (5th gen)'], C, 'Retailer listing'),
 ('APP', ['iPad Pro 12.9 (1st gen)', 'iPad Pro 12.9 (2nd gen)'], K, 'Same screen size: test before swapping'),
 ('APP', ['iPad Pro 10.5', 'iPad Air (3rd gen)', 'iPad (7th gen)', 'iPad (8th gen)', 'iPad (9th gen)'], C, '10.2/10.5in. Belkin ScreenForce lists all five'),
 ('APP', ['iPad Pro 11 (1st gen)', 'iPad Pro 11 (2nd gen)', 'iPad Pro 11 (3rd gen)', 'iPad Pro 11 (4th gen)', 'iPad Air (4th gen)', 'iPad Air (5th gen)'], C, 'ESR list. OtterBox also lists Air 4/5 with Air 11 M2/M3: test before swapping'),
 ('APP', ['iPad Pro 12.9 (3rd gen)', 'iPad Pro 12.9 (4th gen)', 'iPad Pro 12.9 (5th gen)', 'iPad Pro 12.9 (6th gen)'], C, 'ESR list'),
 ('APP', ['iPad (10th gen)', 'iPad (A16)'], C, 'OtterBox list. Does not fit Air or Pro 11'),
 ('APP', ['iPad mini (6th gen)', 'iPad mini (A17 Pro)'], C, 'ESR list'),
 ('APP', ['iPad Air 11 (M2)', 'iPad Air 11 (M3)', 'iPad Air 11 (M4)'], C, 'Supershieldz, TORRAS list all three'),
 ('APP', ['iPad Air 13 (M2)', 'iPad Air 13 (M3)'], C, 'ESR list'),
 ('APP', ['iPad Pro 11 (M4)', 'iPad Pro 11 (M5)'], C, 'OtterBox, ZAGG list'),
 ('APP', ['iPad Pro 13 (M4)', 'iPad Pro 13 (M5)'], K, 'Likely shared, not confirmed'),
 ('APP', ['Apple Watch (1st gen) 38mm', 'Apple Watch Series 1 38mm', 'Apple Watch Series 2 38mm', 'Apple Watch Series 3 38mm'], C, 'Listings cover Series 1-3; 1st gen is the same case'),
 ('APP', ['Apple Watch (1st gen) 42mm', 'Apple Watch Series 1 42mm', 'Apple Watch Series 2 42mm', 'Apple Watch Series 3 42mm'], C, 'Listings cover Series 1-3; 1st gen is the same case'),
 ('APP', ['Apple Watch Series 4 40mm', 'Apple Watch Series 5 40mm', 'Apple Watch Series 6 40mm', 'Apple Watch SE (1st gen) 40mm', 'Apple Watch SE (2nd gen) 40mm'], C, 'PanzerGlass, Belkin list Series 4/5/6/SE'),
 ('APP', ['Apple Watch Series 4 44mm', 'Apple Watch Series 5 44mm', 'Apple Watch Series 6 44mm', 'Apple Watch SE (1st gen) 44mm', 'Apple Watch SE (2nd gen) 44mm'], C, 'PanzerGlass, Belkin list Series 4/5/6/SE'),
 ('APP', ['Apple Watch Series 7 41mm', 'Apple Watch Series 8 41mm', 'Apple Watch Series 9 41mm'], C, 'Mous list'),
 ('APP', ['Apple Watch Series 7 45mm', 'Apple Watch Series 8 45mm', 'Apple Watch Series 9 45mm'], C, 'Spigen, ZAGG, Mous list'),
 ('APP', ['Apple Watch Series 10 42mm', 'Apple Watch Series 11 42mm'], C, 'ZAGG list'),
 ('APP', ['Apple Watch Series 10 46mm', 'Apple Watch Series 11 46mm'], C, 'SaharaCase, ZAGG list'),
 ('APP', ['Apple Watch Ultra 49mm', 'Apple Watch Ultra 2 49mm'], C, 'PanzerGlass list'),
 ('SAM', ['Galaxy S24', 'Galaxy S25'], C, 'Belkin, OtterBox, PanzerGlass list'),
 ('SAM', ['Galaxy S24+', 'Galaxy S25+'], C, 'Belkin, PanzerGlass list'),
 ('SAM', ['Galaxy A16', 'Galaxy A16 5G', 'Galaxy A17'], C, 'ZAGG, PanzerGlass list'),
 ('SAM', ['Galaxy A36', 'Galaxy A56', 'Galaxy A37'], C, 'OtterBox lists A36/A56; retailer lists A37 too'),
 ('SAM', ['Galaxy Tab A9', 'Galaxy Tab A11'], C, '8.7in. Blueshift list'),
 ('SAM', ['Galaxy Tab A9+', 'Galaxy Tab A11+'], C, 'Cygnett, ZAGG, Speck list'),
 ('SAM', ['Galaxy Tab S7', 'Galaxy Tab S8', 'Galaxy Tab S9', 'Galaxy Tab S9 FE', 'Galaxy Tab S10 FE', 'Galaxy Tab S10 Lite', 'Galaxy Tab S11'], C, 'Samsung lists S9, S9 FE, S10 FE, S10 Lite; others add S7, S8, S11'),
 ('SAM', ['Galaxy Tab S7+', 'Galaxy Tab S7 FE', 'Galaxy Tab S8+', 'Galaxy Tab S9+', 'Galaxy Tab S9 FE+', 'Galaxy Tab S10+'], C, 'PanzerGlass list'),
 ('SAM', ['Galaxy Tab S9 Ultra', 'Galaxy Tab S10 Ultra'], C, 'Spigen list'),
 ('GOO', ['Pixel 9', 'Pixel 9 Pro', 'Pixel 10', 'Pixel 10 Pro'], C, ''),
 ('GOO', ['Pixel 9 Pro XL', 'Pixel 10 Pro XL'], C, 'PanzerGlass list'),
 ('GOO', ['Pixel 11', 'Pixel 11 Pro'], C, 'Case-Mate, Mous, dbrand list both. Not the same size as Pixel 10 glass'),
 ('OPP', ['Oppo A5 4G', 'Oppo A5 5G'], C, 'Blueshift lists both'),
 ('OPP', ['Oppo A6x 4G', 'Oppo A6x 5G'], C, 'Panzer lists both'),
 ('ONE', ['OnePlus Nord N10 5G', 'OnePlus Nord N200 5G'], C, 'Third-party listing'),
 ('ONE', ['OnePlus Nord N30', 'OnePlus Nord CE 3 Lite'], C, 'Same phone, two names'),
 ('MOT', ['Motorola Razr 50', 'Motorola Razr 2024'], C, 'Same phone, two names. Glass is for the cover screen'),
 ('MOT', ['Motorola Razr 50 Ultra', 'Motorola Razr+ 2024'], C, 'Same phone, two names. Glass is for the cover screen'),
 ('MOT', ['Motorola Razr 60', 'Motorola Razr 2025'], C, 'Same phone, two names. Glass is for the cover screen'),
 ('MOT', ['Motorola Razr 60 Ultra', 'Motorola Razr Ultra 2025'], C, 'Same phone, two names. Glass is for the cover screen'),
 ('MOT', ['Motorola Razr 70', 'Motorola Razr 2026'], C, 'Same phone, two names. Glass is for the cover screen'),
 ('MOT', ['Motorola Razr 70 Ultra', 'Motorola Razr Ultra 2026'], C, 'Same phone, two names. Glass is for the cover screen'),
 ('MIC', ['Surface RT', 'Surface 2'], K, 'Same body size: test before swapping'),
 ('MIC', ['Surface Pro', 'Surface Pro 2'], K, 'Same body size: test before swapping'),
 ('MIC', ['Surface Go', 'Surface Go 2', 'Surface Go 3', 'Surface Go 4'], C, 'Supershieldz also lists all four'),
 ('MIC', ['Surface Pro 4', 'Surface Pro 5', 'Surface Pro 6', 'Surface Pro 7', 'Surface Pro 7+'], C, '12.3in. amFilm list'),
 ('MIC', ['Surface Pro 8', 'Surface Pro 9', 'Surface Pro 10', 'Surface Pro 11', 'Surface Pro X'], C, '13in. amFilm, Fintie list'),
 ('LEN', ['Lenovo Tab P11', 'Lenovo Tab P11 Plus'], C, 'Retailer lists both'),
 ('LEN', ['Lenovo Tab M11', 'Lenovo Tab K11', 'Lenovo Idea Tab 11'], C, 'Third-party listing'),
 ('LEN', ['Lenovo Tab P12', 'Lenovo Idea Tab Pro', 'Lenovo Yoga Tab Plus'], C, '12.7in. Retailer listing'),
 ('VAL', ['Steam Deck (LCD)', 'Steam Deck OLED'], C, 'Spigen, dbrand, JSAUX list both'),
 ('SON', ['PSP-1000', 'PSP-2000 (Slim)', 'PSP-3000'], K, 'Film packs list all three; ZedLabz says the bezel differs by revision: test first'),
 ('SON', ['Sony Ericsson G700', 'Sony Ericsson G700 Business Edition'], K, 'Same phone, business software bundle'),
 ('SON', ['Sony Ericsson Xperia PLAY', 'Sony Ericsson Xperia PLAY CDMA'], K, 'Same phone, CDMA version'),
 ('SON', ['Sony Ericsson Xperia Neo', 'Sony Ericsson Xperia neo V'], K, 'Neo V is a refresh in the same body: test first'),
 ('SON', ['Sony Ericsson Xperia Arc', 'Sony Ericsson Xperia Arc S'], K, 'Arc S is a refresh in the same body: test first'),
 ('GPD', ['GPD Win 4 (2022)', 'GPD Win 4 (2023)', 'GPD Win 4 (2024)', 'GPD Win 4 (2025)'], K, '6in slider. Same body each year; GPD sells one Win 4 protector: test first'),
 ('GPD', ['GPD Win Max 2 (2022)', 'GPD Win Max 2 (2023)', 'GPD Win Max 2 (2024)', 'GPD Win Max 2 (2025)'], K, '10.1in. Same body each year: test first'),
 ('GPD', ['GPD Win Mini (2023)', 'GPD Win Mini (2024)'], K, 'Same body: test first. Walieoka: 2024 glass does not fit the 2025'),
 ('AYA', ['AYANEO Founder', 'AYANEO (2021)', 'AYANEO 2021 Pro'], K, '7in. Same body: test first'),
 ('AYA', ['AYANEO Next', 'AYANEO Next Pro'], K, '7in. Same body: test first'),
 ('AYA', ['AYANEO Air', 'AYANEO Air Pro', 'AYANEO Air 1S'], K, '5.5in OLED. Same body: test first'),
 ('AYA', ['AYANEO 2', 'AYANEO Geek', 'AYANEO 2S', 'AYANEO Geek 1S'], K, '7in. Same body: test first'),
 ('KON', ['KONKR Pocket FIT', 'KONKR Pocket FIT Elite'], K, '6in. Same design and screen, two chips: test first'),
 ('ONX', ['OneXPlayer', 'OneXPlayer 1S'], K, '8.4in. Same body: test first'),
 ('ONX', ['OneXPlayer Mini', 'OneXPlayer Mini Pro'], K, '7in. Same body: test first'),
 ('ONX', ['OneXPlayer 2', 'OneXPlayer 2 Pro', 'OneXPlayer 2 Pro (2024)'], K, '8.4in. Same body: test first'),
 ('ONX', ['OneXFly', 'OneXFly (8840U)'], K, '7in. Same body, chip upgrade'),
 ('ONX', ['OneXPlayer X1', 'OneXPlayer X1 Pro'], K, '10.95in. Same body: test first'),
 ('BIT', ['Bittboy Pocket Go V2', 'Bittboy Metal Pocket Go'], K, 'Metal-shell version of the V2: test first'),
 ('MOD', ['ModRetro Chromatic', 'ModRetro Chromatic (2026 clear edition)'], K, 'Same handheld in a new shell: test first. Some units have a sapphire screen'),
 ('FUN', ['FunnyPlaying Retro Pixel Pocket', 'FunnyPlaying Retro Pixel Pocket (2025)'], K, '3in 1:1. 2025 model keeps the same body and display, new chip'),
 ('NVI', ['NVIDIA Shield Tablet', 'NVIDIA Shield Tablet LTE', 'NVIDIA Shield Tablet K1'], K, '8in. Same tablet; K1 is the 2015 re-release'),
 ('RAZ', ['Razer Edge', 'Razer Edge 5G'], K, 'Same handheld, Wi-Fi and 5G versions'),
 ('RET', ['Retroid Pocket 2', 'Retroid Pocket 2+', 'Retroid Pocket 2S'], C, 'Retailer 3-pack lists 2S/2+/2'),
 ('RET', ['Retroid Pocket 3', 'Retroid Pocket 3+'], K, 'Same body and 4.7in screen: test first'),
 ('RET', ['Retroid Pocket 4', 'Retroid Pocket 4 Pro'], C, 'Mr.Shield lists both'),
 ('ANB', ['Anbernic RG35XX', 'Anbernic RG35XX Plus'], C, 'Retailer lists RG35XX/RG35XX Plus'),
 ('ANB', ['Anbernic RG353V', 'Anbernic RG353VS'], C, 'atFoliX lists both'),
 ('AYN', ['AYN Loki Zero', 'AYN Loki Max'], K, 'Same 6in body: test first'),
 ('AYN', ['AYN Loki Mini', 'AYN Loki Mini Pro'], K, 'Same body: test first'),
 ('ASU', ['ROG Ally', 'ROG Ally X', 'ROG Xbox Ally', 'ROG Xbox Ally X', 'MSI Claw A1M', 'MSI Claw 7 AI+'], C, '7in. JSAUX lists all four Allys; Spigen and MSI add the 7in Claws'),
]
# Notes and statuses for single-model groups
SINGLE = {
 ('APP', 'iPhone 15 Pro'): (C, 'Does not fit 16 Pro (bigger 6.3in screen)'),
 ('APP', 'iPhone 15 Pro Max'): (C, ''),
 ('APP', 'iPhone 12 mini'): (C, ''), ('APP', 'iPhone 12 Pro Max'): (C, 'Belkin list'),
 ('APP', 'iPhone 13 mini'): (C, ''), ('APP', 'iPhone 14 Pro'): (C, 'Belkin list'),
 ('APP', 'iPhone 14 Pro Max'): (C, 'Belkin list'),
 ('APP', 'iPhone 16 Pro Max'): (K, 'Some listings pair it with 17 Pro Max; Belkin sells separately'),
 ('APP', 'iPad Air 13 (M4)'): (K, 'May share the Air 13 M2/M3 group: test first'),
 ('APP', 'Apple Watch Ultra 3 49mm'): (K, 'Supershieldz lists it with Ultra/Ultra 2; ESR sells Ultra 3 glass separately'),
 ('APP', 'Apple Watch SE 3 40mm'): (K, 'Same case size as Series 4-6/SE 40mm: test first'),
 ('APP', 'Apple Watch SE 3 44mm'): (K, 'Same case size as Series 4-6/SE 44mm: test first'),
 ('SAM', 'Galaxy S25 Ultra'): (C, 'Belkin: S25 Ultra only'),
 ('SAM', 'Galaxy S26'): (K, 'Brands sell S26-specific glass'),
 ('SAM', 'Galaxy S26 Ultra'): (C, 'S25 Ultra glass does not fit'),
 ('SAM', 'Galaxy A35'): (K, 'Belkin sells A35 and A55 separately; AXS lists A35/A55/A36/A56 as one'),
 ('SAM', 'Galaxy A55'): (K, 'See Galaxy A35 note'),
 ('SAM', 'Galaxy A57'): (C, 'Samsung sells its own A57 glass'),
 ('SAM', 'Galaxy Tab S8 Ultra'): (K, 'Spigen: S9/S10 Ultra glass is not for S8 Ultra'),
 ('SAM', 'Galaxy Tab S11 Ultra'): (K, 'Some listings group it with S9/S10 Ultra'),
 ('SAM', 'Galaxy Watch9 40mm'): (C, 'Spigen makes size-specific Watch9 glass'),
 ('SAM', 'Galaxy Watch9 44mm'): (C, 'Spigen makes size-specific Watch9 glass'),
 ('GOO', 'Pixel 11 Pro XL'): (C, 'Case-Mate, Mous, dbrand sell it separately from 11/11 Pro'),
 ('GOO', 'Pixel 6 Pro'): (K, 'Curved screen'),

 ('NIN', 'Nintendo Switch'): (C, '6.2in. Nintendo: each Switch model needs its own protector'),
 ('NIN', 'Nintendo Switch Lite'): (C, '5.5in'),
 ('NIN', 'Nintendo Switch OLED'): (C, '7.0in'),
 ('NIN', 'Nintendo Switch 2'): (C, '7.9in. Nintendo: older Switch protectors don\'t fit'),
 ('LEN', 'Legion Go'): (C, 'Spigen: Go S glass does not fit Go'),
 ('LEN', 'Legion Go S'): (C, '8in'),
 ('LEN', 'Legion Go 2'): (C, '8.8in. Sold separately from Go S glass'),
 ('MSI', 'MSI Claw 8 AI+'): (C, "8in. MSI's own 8in glass"),
 ('SON', 'PS Vita (PCH-1000)'): (K, 'Vita 1000 (OLED) and Slim glass differ; some film packs list both'),
 ('SON', 'PS Vita Slim (PCH-2000)'): (K, 'Vita 1000 (OLED) and Slim glass differ; some film packs list both'),
 ('SON', 'PSP Go'): (K, 'Sliding screen'),
 ('RET', 'Retroid Pocket Flip'): (K, 'Sliding screen'),
 ('RET', 'Retroid Pocket Flip 2'): (K, 'Clamshell. Sold with two chips, same body'),
 ('RET', 'Retroid Pocket Mini V2'): (K, 'Different screen from the first Mini: check'),
 ('MIY', 'Miyoo Mini V4'): (K, 'Bigger screen than v1-v3 in a similar body: do not swap'),
 ('AYN', 'AYN Thor'): (K, 'Two screens: buy top and bottom sets'),
 ('LOG', 'Logitech G Cloud'): (K, '7in. Black Edition is the same handheld'),
 ('LEN', 'Legion C700'): (K, 'Cloud handheld, China launch Aug 2026'),
 ('LEN', 'Lenovo G700 Cloud Gaming Handheld'): (K, 'Cloud handheld, China launch Aug 2026'),
 ('GPD', 'GPD Win Mini (2025)'): (C, 'Walieoka: Win Mini 2024 glass does not fit the 2025'),
 ('GPD', 'GPD Win Max 3'): (K, '9.06in. Pre-order Nov 2026'),
 ('AYA', 'AYANEO Flip DS'): (K, 'Two screens: buy top and bottom sets'),
 ('AYA', 'AYANEO Pocket DS'): (K, 'Two screens: buy top and bottom sets'),
 ('AYA', 'AYANEO Slide'): (K, 'Sliding screen'),
 ('ONX', 'OneXFly F1 Pro'): (K, '7in OLED. Different panel from the OneXFly: test first'),
 ('POW', 'Powkiddy RGB20SX'): (K, 'Same 4in 1:1 screen as RGB30 in a different body'),
 ('ZOT', 'Zotac Zone'): (K, '7in AMOLED'),
 ('ZOT', 'Zotac Zone Pro'): (K, 'Shown as Zone 2 before launch. Same size as Zone: test first'),
 ('BIT', 'Bittboy (v1-v3.5)'): (K, 'Board revisions in the same body'),
 ('CLK', 'ClockworkPi DevTerm'): (K, 'Wide 6.86in screen. All core module versions share one body'),
 ('CLK', 'ClockworkPi uConsole'): (K, '5in. All core module versions share one body'),
 ('FUN', 'FunnyPlaying FPGBC'): (K, 'Game Boy Color style kit: check the lens size'),
 ('ANA', 'Analogue Pocket'): (K, '3.5in. Every edition (Glow, Transparent, Classic, Aluminium, Supreme) uses the same screen'),
 ('PAN', 'Playdate'): (K, '2.7in. One model so far'),
 ('SEG', 'Sega Game Gear'): (K, '3.2in. Glass goes on the screen lens; includes the 2000 Majesco re-release'),
 ('SEG', 'Sega Nomad'): (K, '3.25in. Glass goes on the screen lens'),
 ('SEG', 'Sega Game Gear Micro'): (K, '1.15in. All four colour editions share one body'),
 ('NVI', 'NVIDIA Shield Portable'): (K, '5in flip screen'),
 ('NVI', 'NVIDIA Tegra Note 7'): (K, '7in. Also sold under partner brands such as EVGA'),
 ('APP', 'iPhone Duo'): (K, 'Foldable: glass is for the 5.4in outer (cover) screen'),
 ('APP', 'iPad mini (A20 Pro)'): (K, '8.5in OLED. Bigger screen than mini 6/7: their glass will not fit'),
 ('APP', 'Apple Watch Series 12 42mm'): (K, 'Looks the same as Series 10/11: test their 42mm glass first'),
 ('APP', 'Apple Watch Series 12 46mm'): (K, 'Looks the same as Series 10/11: test their 46mm glass first'),
 ('APP', 'Apple Watch Ultra 4 49mm'): (K, 'Looks the same as Ultra 3: test first'),
 ('ASU', 'ROG Xbox Ally X20'): (K, '7.4in OLED. Bigger screen than the 7in Allys: do not swap'),
 ('MSI', 'MSI Claw 8 EX AI+'): (K, 'Same 8in display spec as Claw 8 AI+ but redesigned body: test first'),
 ('MSI', 'MSI Claw A8'): (K, 'Same 8in size as Claw 8 AI+: test first'),
}

SETNOTE = {
 'nubia Red Magic 12 Pro+': (K, 'Global version of the 12 Pro+: same phone'),
 'Legion Go 2': (C, '8.8in. SteamOS version is the same hardware. Sold separately from Go S glass'),
 'Legion Go S': (C, '8in. SteamOS version is the same hardware'),
 'Lenovo Legion Y700 (Gen 5)': (K, 'Same tablet: Y700 in China, Legion Tab (8.8", 5) elsewhere'),
 'Retroid Pocket Duo Lite': (K, 'Two screens: buy top and bottom sets. Lite+ uses the Lite body'),
 'Miyoo Mini Plus': (K, 'V2 keeps the same body and screen'),
 'Miyoo Flip': (K, 'V2 is a hinge revision in the same body'),
 'TrimUI Brick': (K, 'Hammer is the same hardware in a metal shell: test first'),
 'iPod (5th gen, video)': (K, '2.5in. iPod classic uses the same screen and front: test first'),
 'iPod touch (5th gen)': (K, '4in. 5th, 6th and 7th gen share the same body; sellers list them together'),
 'AYN Odin 2': (K, 'Odin 2 Max has an AMOLED panel in the same body: test first'),
 'MagicX Mini Zero 28': (K, 'V2 is a revision in the same body'),
 'Mangmi Air Y': (K, '4.2in. Air Y and Air Y Pro share the display and body size'),
 'GKD 350H': (K, '350H Plus is the same handheld in a metal shell: test first'),
 'Evercade EXP': (K, '4.3in. EXP-R is a revision in the same body'),
 'Evercade Nexus': (K, '5.89in. Nexus 64 Edition is the same hardware'),
 'Hyperkin SupaBoy S': (K, '4.3in. Every colour edition since the SupaBoy S uses the same internals'),
 'Huawei Band 11': (K, 'Band 11 and Band 11 Pro both use 1.62in screens: test before swapping'),
}
for code, names in SETS:
    st, note = SETNOTE.get(names[0], (K, 'Same case and screen size: test before swapping'))
    SHARED.append((code, names, st, note))
SINGLE.update({
 ('MIC', 'Surface Duo'): (K, 'Two screens: buy a set that covers both screens'),
 ('MIC', 'Surface Duo 2'): (K, 'Two screens: buy a set that covers both screens. The hinge also has a small glance screen'),
 ('ACE', 'Acer Iconia A14 (2026)'): (K, '2026 refresh: check against the 2025 A14'),
 ('ACE', 'Acer Iconia A16 (2026)'): (K, '2026 refresh: check against the 2025 A16'),
 ('ACE', 'Acer Iconia X14 (2026)'): (K, '2026 refresh: check against the 2025 X14'),
 ('ACE', 'Acer Nitro Blaze 7'): (K, '7in'),
 ('HYP', 'Hyperkin SupaBoy'): (K, '3.5in original model'),
 ('EVC', 'Evercade (original handheld)'): (K, '4.3in'),
 ('EVC', 'Evercade Super Pocket'): (K, '2.8in. Every game edition shares one body'),
 ('MYA', 'My Arcade Micro Player'): (K, 'Mini arcade cabinet. Every game edition shares one body'),
 ('MYA', 'My Arcade Micro Player Pro'): (K, 'Mini arcade cabinet. Every game edition shares one body'),
 ('MYA', 'My Arcade Pocket Player'): (K, 'Every game edition shares one body'),
 ('MYA', 'My Arcade Pocket Player Pro'): (K, 'Every game edition shares one body'),
 ('MYA', 'My Arcade Nano Player'): (K, 'Every game edition shares one body'),
 ('MYA', 'My Arcade Nano Player Pro'): (K, 'Every game edition shares one body'),
 ('MYA', 'My Arcade Pico Player'): (K, 'Every game edition shares one body'),
 ('MYA', 'My Arcade Atari Gamestation Go'): (K, '7in'),
 ('MYA', 'My Arcade Gamestation Retro Go'): (K, '8in'),
 ('ACE', 'Acer Nitro Blaze 8'): (K, '8.8in'),
 ('ACE', 'Acer Nitro Blaze 11'): (K, '10.95in, detachable controllers'),
 ('ACE', 'Acer Predator Atlas 8'): (K, '8in'),
 ('ONX', 'OneXFly Apex Air'): (K, '8in. Same body as OneXFly Apex: test its glass first'),
})

# GSMArena devices by name: the full name ("Samsung Galaxy Z Fold5") or without the brand ("Galaxy Z Fold5", "Nexus 5").
# A short name that two devices share is left out.
GS = json.load(open(ROOT + '/ds/gsmarena-catalog-builder/catalogs/gsmarena-full-catalog.gscatalog', encoding='utf-8'))['devices']
def _nk(s): return re.sub(r'[^a-z0-9]', '', s.lower())
_GSFULL, _GSSHORT = {}, {}
for r in GS:
    _GSFULL.setdefault(_nk(r['model']), r)
    s = _nk(r['model'].split(' ', 1)[-1])
    _GSSHORT[s] = r if _GSSHORT.get(s, r) is r else None
def gs_lookup(name): return _GSFULL.get(_nk(name)) or _GSSHORT.get(_nk(name))

def foldnote(m):
    n = m['name']
    if m['cat'] != 'Phone': return ''
    r = gs_lookup(n)
    if r:  # GSMArena says whether the screen folds: flip feature phones, flip-camera phones and the ZTE Open don't
        d = r['specs'].get('Display') or {}
        big = float((re.match(r'\s*([\d.]+)\s*inches', d.get('Size') or '') or [0, 0])[1]) >= 5  # not a flip feature phone
        fold = 'oldable' in (d.get('Type') or '') or (big and 'Unfolded' in ((r['specs'].get('Body') or {}).get('Dimensions') or ''))
    else:
        fold = (re.search(r'\b(Z Fold|Z Flip|TriFold|Fold\d|Flip\d|Fold\b|Flip\b|Open\b|Mix Fold|Mix Flip|Mate X|Magic V\d|Magic V\b)', n) and
                not re.search(r'\bGo Flip\b', n)) or (m['code'] == 'HUA' and 'Pocket' in n) or (m['code'] == 'MOT' and 'Razr' in n and m['date'] >= '2019')
    return 'Foldable: glass is for the outer (cover) screen' if fold else ''

groups = []
claimed = set()
for code, names, st, note in SHARED:
    mem = []
    for n in names:
        mc = 'ASU' if code == 'ASU' else code
        m = byname.get((mc, n))
        if not m: print('MISSING', code, n); continue
        mem.append(m); claimed.add(id(m))
    groups.append(dict(code=code, members=mem, status=st, note=note))

# Variant merges: leading Samsung model codes, tablet connectivity variants
def vkey(m):
    n = m['name']
    if m['code'] == 'SAM': n = re.sub(r'^[A-Z]{1,2}\d{3,5}[A-Z]? (?=Galaxy)', '', n)
    if m['cat'] == 'Tablet':
        n = re.sub(r'\s*(\+ )?\b(Wi-Fi \+ Cellular|Wi-Fi \+ 3G|Wi-Fi \+ 4G|Wi-Fi|Cellular|3G|4G|LTE|CDMA)\b', '', n).strip()
        if m['code'] == 'SON': n = re.sub(r'\s*\bWiFi\b', '', n).strip()
    if m['cat'] == 'Wearable' and 'Fitbit' not in n: n = re.sub(r' (Aluminum|LTE|3G|\(eSIM\))(?= |$)', '', n)
    return (m['code'], m['cat'], n.lower())
buckets = collections.OrderedDict()
for m in sorted(models, key=lambda m: (m['date'], m['seq'])):
    if id(m) in claimed: continue
    buckets.setdefault(vkey(m), []).append(m)
for k, mem in buckets.items():
    if len(mem) > 1:
        groups.append(dict(code=k[0], members=mem, status=K, note='Variants of one model (region, carrier or connectivity): check fit'))
    else:
        m = mem[0]
        st, note = SINGLE.get((m['code'], m['name']), (K, ''))
        groups.append(dict(code=m['code'], members=mem, status=st, note=note))

# Notes
for g in groups:
    g['cat'] = g['members'][0]['cat']
    assert all(x['cat'] == g['cat'] for x in g['members']), g
    g['members'].sort(key=lambda m: (m['date'], m['seq']))
    g['date'] = g['members'][0]['date']; g['seq'] = g['members'][0]['seq']
    fn = foldnote(g['members'][0])
    if fn and 'cover' not in g['note']: g['note'] = (g['note'] + '. ' if g['note'] else '') + fn
    if g['code'] == 'OPE': g['note'] = (g['note'] + '. ' if g['note'] else '') + 'Release order approximate'
    if g['cat'] == 'Handheld' and re.search(r'\bDS\b|3DS|2DS|DSi|RG DS|RG DDS|Pocket Duo', ' '.join(x['name'] for x in g['members'])):
        g['note'] = g['note'] if g['note'].startswith('Two screens') else 'Two screens: buy top and bottom sets'

# Cross-brand and same-body twins
def TRUEB(m): return 'MSI' if m['name'].startswith('MSI ') else m['code']
FAM = {'OPP': 'BBK', 'ONE': 'BBK', 'REA': 'BBK', 'HUA': 'HW', 'HON': 'HW', 'LEN': 'LM', 'MOT': 'LM', 'TCL': 'TCL', 'BLB': 'TCL',
       'TEC': 'TRS', 'INF': 'TRS', 'ITE': 'TRS', 'BLV': 'BLV', 'OSC': 'BLV', 'MMX': 'MMX', 'YUX': 'MMX'}
REBADGE = {'VOD', 'TMO', 'OTW', 'ORA', 'ATT', 'QTE', 'IMA'}  # carrier/rebadger brands: may merge with any one maker
gidx = {}
for i, g in enumerate(groups):
    for m in g['members']: gidx[id(m)] = i
bymn = {(m['code'], m['name']): m for m in models}
parent = list(range(len(groups)))
def find(i):
    while parent[i] != i: parent[i] = parent[parent[i]]; i = parent[i]
    return i
def union(i, j): parent[find(i)] = find(j)
viaspec = set()
def _cname(r):
    b = r['brand']; nm = r['model'][len(b)+1:] if r['model'].startswith(b + ' ') else r['model']
    if b in NEWB: return re.sub(r'^alcatel ', 'Alcatel ', r['model'])
    if b == 'Acer': return 'Acer ' + nm
    if b == 'Garmin-Asus': return 'Garmin-Asus ' + nm
    return disp(b, nm)
def _spec(r):
    sp = r['specs']
    dm = re.search(r'([\d.]+)\s*x\s*([\d.]+)\s*x\s*([\d.]+)\s*mm', sp.get('Body', {}).get('Dimensions') or '')
    rs = re.search(r'(\d+)\s*x\s*(\d+)\s*pixels', sp.get('Display', {}).get('Resolution') or '')
    sz = re.search(r'([\d.]+)\s*inches', sp.get('Display', {}).get('Size') or '')
    return (dm.groups(), sz.group(1), rs.groups()) if dm and rs and sz else None
_cat = GS
# Screen size and body from GSMArena: {screen, dims}, plus for foldables {cscreen, cdims}: the cover screen and folded body,
# which is what cover glass fits. Bodies like "163.7 x 73.9 x 8.5 or 8.8 mm" keep the first thickness.
def _sizes(r):
    out = {}
    body = (r['specs'].get('Body') or {}).get('Dimensions') or ''
    disp = r['specs'].get('Display') or {}
    dm = re.match(r'\s*(?:Unfolded:\s*)?([\d.]+)\s*x\s*([\d.]+)\s*x\s*([\d.]+)(?!\s*in\b)', body)
    if dm: out['dims'] = ' x '.join(dm.groups()) + ' mm'
    sz = re.match(r'\s*([\d.]+)\s*inches', disp.get('Size') or '')
    if sz: out['screen'] = sz.group(1) + 'in'
    fd = re.search(r'Folded:\s*([\d.]+)\s*x\s*([\d.]+)\s*x\s*([\d.]+)', body)
    if fd: out['cdims'] = ' x '.join(fd.groups()) + ' mm'
    res = disp.get('Resolution') or ''
    cs = re.search(r'([\d.]+)\s*(?:inches|")', res.split('|', 1)[1]) if '|' in res else None
    if cs: out['cscreen'] = cs.group(1) + 'in'
    return out
ROUND = {}
SPECB = collections.defaultdict(set)
for r in _cat:
    b = r['brand']
    if b not in CODE or b == 'Nvidia': continue
    m = bymn.get((CODE[b], _cname(r)))
    if not m: continue
    mn = html.unescape((r['specs'].get('Misc') or {}).get('Models') or '').strip()
    if mn: m['codes'] = ', '.join(dict.fromkeys([c for c in m.get('codes', '').split(', ') if c] + [c.strip() for c in re.split(r',\s+', mn) if c.strip()]))
    # Size, for measuring before swapping glass, and ultrasonic fingerprint readers, which need FP-compatible glass
    m.update(_sizes(r))
    if 'ultrasonic' in ((r['specs'].get('Features') or {}).get('Sensors') or ''): m['ufp'] = True
    k = _spec(r)
    if k: SPECB[(m['cat'],) + k].add(gidx[id(m)])
    if m['cat'] == 'Wearable' and k and k[2][0] == k[2][1] and 'Moto 360 (1st' not in m['name']:
        ROUND[m['name']] = float(k[1]) * 25.4
# Sizes still missing: GSMArena under another brand or spelling (LG Nexus 5, iPhone 4s), then hand-researched sizes
# from build/sizes.json. These only fill gaps for display; they never group models.
for m in models:
    if m.get('screen') and m.get('dims'): continue
    r = gs_lookup(m['name'])
    # Watches listed once per family: "Apple Watch Series 9 45mm" -> GSMArena's "Apple Watch Series 9", used only when
    # its case is that size (GSMArena lists one size, e.g. the 45mm)
    sz = re.search(r'^(.*?)\s+(\d\d)mm$', m['name']) if not r and m['cat'] == 'Wearable' else None
    if sz:
        r2 = gs_lookup(sz.group(1)) or gs_lookup(sz.group(1) + ' Aluminum')
        dm = re.match(r'\s*([\d.]+)\s*x\s*([\d.]+)', ((r2 or {}).get('specs', {}).get('Body') or {}).get('Dimensions') or '')
        if dm and abs(float(dm.group(1)) - int(sz.group(2))) <= 1.5: r = r2
    if r:
        for k, v in _sizes(r).items(): m.setdefault(k, v)
SIZES = json.load(open(ROOT + '/build/sizes.json', encoding='utf-8'))
_byname = {m['name']: m for m in models}
for n, v in SIZES.items():
    m = _byname.get(n)
    if not m: print('SIZES: unknown model', n); continue
    pre = 'c' if v.get('cover') else ''  # foldables: the cover screen and folded body
    if v.get('screen'): m.setdefault(pre + 'screen', v['screen'])
    if v.get('dims'): m.setdefault(pre + 'dims', v['dims'])
# Official model numbers the catalogue lacks (Apple support pages and similar): build/modelnumbers.json
for n, v in json.load(open(ROOT + '/build/modelnumbers.json', encoding='utf-8')).items():
    m = next((x for x in models if x['name'] == n), None)
    if not m: print('MODELNO: unknown model', n); continue
    have = [c for c in m.get('codes', '').split(', ') if c]
    low = {c.lower() for c in have}
    nums = [re.sub(r'^(iphone|ipad|ipod|watch)', lambda x: {'iphone': 'iPhone', 'ipad': 'iPad', 'ipod': 'iPod', 'watch': 'Watch'}[x.group(1).lower()], c, flags=re.I)
            for c in v['numbers']]
    m['codes'] = ', '.join(have + [c for c in dict.fromkeys(nums) if c.lower() not in low])
for key, gs in SPECB.items():
    gs = sorted(gs)
    if len(gs) < 2: continue
    codes = {TRUEB(groups[i]['members'][0]) for i in gs}
    if len({FAM.get(c, c) for c in codes - REBADGE}) > 1: continue
    for i in gs[1:]: union(i, gs[0])
    viaspec.update(gs)
MANUAL_TWINS = [[('HON', 'Honor 20'), ('HUA', 'Huawei nova 5T')],
                [('BLB', 'BlackBerry DTEK50'), ('TCL', 'Alcatel Idol 4')],
                [('BLB', 'BlackBerry DTEK60'), ('TCL', 'Alcatel Idol 4s')],
                [('WIT', 'Withings Steel HR'), ('NOK', 'Nokia Steel HR')]]
TWIN_NOTE = {'Honor 20': 'Honor 20 and Huawei nova 5T are the same phone',
             'BlackBerry DTEK50': 'TCL-made: DTEK50 is a rebadged Alcatel Idol 4',
             'BlackBerry DTEK60': 'TCL-made: DTEK60 is a rebadged Alcatel Idol 4s',
             'OnePlus Pad': 'Press reports: Oppo Pad 2 is a rebranded OnePlus Pad',
             'OnePlus Pad 2': 'Press reports: Oppo Pad 3 Pro is the OnePlus Pad 2 under a new name',
             'OnePlus Pad 2 Pro': 'Press reports: OnePlus Pad 2 Pro is a rebranded Oppo Pad 4 Pro',
             'OnePlus Pad Lite': 'Press reports: OnePlus Pad Lite is nearly identical to the Oppo Pad SE',
             'Moto Tab G70': 'Press reports: Moto Tab G70 is a rebranded Lenovo Tab P11 Plus',
             'OnePlus Nord N300': 'Press reports: Nord N300 is a rebranded Oppo A77 5G / K10 5G',
             'OnePlus Open': 'OnePlus Open and Oppo Find N3 are the same foldable',
             'Withings Steel HR': 'Same watch: sold as Withings, then Nokia (2017-19), then Withings again'}
for tw in MANUAL_TWINS:
    ix = [gidx[id(bymn[k])] for k in tw if k in bymn]
    for i in ix[1:]: union(i, ix[0])
comp = collections.defaultdict(list)
for i in range(len(groups)): comp[find(i)].append(i)
new_groups = []
for root, ix in comp.items():
    if len(ix) == 1: new_groups.append(groups[ix[0]]); continue
    mem = [m for i in ix for m in groups[i]['members']]
    mem.sort(key=lambda m: (m['date'], m['seq']))
    brands = list(dict.fromkeys(TRUEB(m) for m in mem))
    notes = list(dict.fromkeys(groups[i]['note'] for i in ix if groups[i]['note']))
    notes = [n for n in notes if not n.startswith('Variants of one model')]
    tn = [TWIN_NOTE[m['name'].replace('Motorola Moto Tab','Moto Tab')] for m in mem if m['name'].replace('Motorola Moto Tab','Moto Tab') in TWIN_NOTE]
    lead = tn[0] if tn else ('Same body size and screen specs, sold under several brands: test before swapping' if len(brands) > 1
                              else 'Same body size and screen specs: test before swapping')
    st = C if all(groups[i]['status'] == C for i in ix) and len(brands) == 1 else K
    confd = [m['name'] for i in ix if groups[i]['status'] == C for m in groups[i]['members']]
    if confd and st == K: notes.insert(0, 'Seller-confirmed for ' + ', '.join(confd) + '; the rest match on specs')
    g = dict(code=TRUEB(mem[0]), members=mem, status=st, note='. '.join([lead] + [n for n in notes if n != lead]),
             cat=mem[0]['cat'], date=mem[0]['date'], seq=mem[0]['seq'])
    new_groups.append(g)
TWIN_STATS = (len(groups), len(new_groups))
groups = new_groups
for g in groups: g['brands'] = list(dict.fromkeys(TRUEB(m) for m in sorted(g['members'], key=lambda m: (m['date'], m['seq']))))

# 4b. Verified fits from vendor and reseller listings (build/verified.json)
#   same:     the models take the same glass; their groups are merged
#   own:      glass is sold for this one model alone
#   separate: the models need different glass; any that share a group are split apart
#   weak: true marks thin evidence (one marketplace listing, or one brand with conflicting listings).
#         Its note and sources are shown, but it doesn't merge groups or mark them Confirmed.
VERIFIED = json.load(open(ROOT + '/build/verified.json', encoding='utf-8'))
def _refresh(g):
    g['members'].sort(key=lambda m: (m['date'], m['seq']))
    m0 = g['members'][0]
    g.update(code=TRUEB(m0), date=m0['date'], seq=m0['seq'], cat=m0['cat'])
    g['brands'] = list(dict.fromkeys(TRUEB(m) for m in g['members']))
gof = {m['name']: g for g in groups for m in g['members']}
VER_MISSING = sorted({n for f in VERIFIED for n in f['models'] if n not in gof})
for n in VER_MISSING: print('VERIFIED: unknown model', n)
def _clean_note(t):
    # Research notes are shown to shop staff: drop remarks about the catalogue's own grouping
    t = re.sub(r'^(possible )?missed merge:\s*|^partial:\s*', '', t.strip(), flags=re.I)
    t = re.sub(r'\s*\([^)]*catalog(ue)?[^)]*\)', '', t)
    t = re.sub(r',?\s*merging [^.;]*?(catalog(ue)? )?groups?\b', '', t, flags=re.I)
    t = re.sub(r',?\s*merging [^.;]*\b[A-Z]{3}-\d{4}\b[^.;]*', '', t)  # group codes change when groups are renumbered
    t = re.sub(r',?\s*an? (possible )?missed merge[^.;]*', '', t, flags=re.I)
    parts = [x for x in re.split(r'(?<=[.;])\s+', t) if not re.search(r'catalog(ue)?|work list|TODO', x, re.I)]
    t = ' '.join(parts).strip().rstrip('.;')
    return t[:1].upper() + t[1:]
vown, vsrc, vnote = set(), collections.defaultdict(list), collections.defaultdict(list)
for f in VERIFIED:
    names = [n for n in f['models'] if n in gof]
    src = [[x['name'], x['url']] for x in f.get('sources', [])]
    for n in names:
        vsrc[n] += src
        if f.get('note'): vnote[n].append(_clean_note(f['note']))
    if f['fit'] != 'separate': continue
    kept = set()  # the listed models need different glass: where two share a group, the later ones leave it
    for n in names:
        g = gof[n]
        if id(g) not in kept: kept.add(id(g)); continue
        m = next(x for x in g['members'] if x['name'] == n)
        g['members'].remove(m); _refresh(g)
        if len(g['members']) == 1: g['note'] = ''
        ng = dict(members=[m], status=K, note=''); _refresh(ng)
        groups.append(ng); gof[n] = ng
# Models proven to share glass: manual Confirmed groups plus verified "same" findings
vpar = {}
def vfind(n):
    vpar.setdefault(n, n)
    while vpar[n] != n: vpar[n] = vpar[vpar[n]]; n = vpar[n]
    return n
for g in groups:
    if g['status'] == C and len(g['members']) > 1:
        for m in g['members'][1:]: vpar[vfind(m['name'])] = vfind(g['members'][0]['name'])
for f in VERIFIED:
    names = [n for n in f['models'] if n in gof]
    if f.get('weak'): continue
    if f['fit'] == 'own':
        vown.update(names)
    elif f['fit'] == 'same' and len(names) > 1:
        for n in names[1:]: vpar[vfind(n)] = vfind(names[0])
        tgt = gof[names[0]]
        for n in names[1:]:
            g = gof[n]
            if g is tgt: continue
            tgt['members'] += g['members']
            tgt['note'] = '. '.join(x for x in dict.fromkeys([tgt['note'], g['note']]) if x)
            for m in g['members']: gof[m['name']] = tgt
            groups.remove(g)
        _refresh(tgt)
def _keep(note):  # note sentences that still hold once a fit is verified
    return [x.rstrip('.') for x in note.split('. ') if x and not re.search(r'test before swapping|test first|check fit|Seller-confirmed|Sellers confirm|the rest match|Likely shared', x)]
VER_STATS = collections.Counter()
for g in groups:
    names = [m['name'] for m in g['members']]
    if not any(n in vsrc for n in names): continue
    g['sources'] = [list(x) for x in dict.fromkeys(tuple(x) for n in names for x in vsrc[n])]
    vn = [x for n in names for x in vnote[n]]
    whole = len(names) > 1 and len({vfind(n) for n in names}) == 1
    if whole or (len(names) == 1 and names[0] in vown):
        g['status'] = C
        g['note'] = '. '.join(dict.fromkeys((vn or ['Sellers list these together' if whole else 'Sold for this model only']) + _keep(g['note'])))
        VER_STATS['confirmed'] += 1
    else:
        g['status'] = K
        sets = collections.defaultdict(list)
        for n in names: sets[vfind(n)].append(n)
        proven = [x for x in sets.values() if len(x) > 1]
        lead = ['Sellers confirm ' + '; '.join(', '.join(x) for x in proven) + '. The rest match on specs: test before swapping'] if proven else []
        g['note'] = '. '.join(dict.fromkeys(lead + vn + (_keep(g['note']) if proven else [x for x in g['note'].split('. ') if x])))
        VER_STATS['partly'] += 1
print('Verified:', dict(VER_STATS), 'from', len(VERIFIED), 'findings')

# Universal round glass (Misc range): one group per 1mm size
GARMIN_IN = {'Forerunner 45': 1.04, 'Forerunner 45S': 1.04, 'Forerunner 55': 1.04, 'Forerunner 245': 1.2, 'Forerunner 245 Music': 1.2,
 'Forerunner 255': 1.3, 'Forerunner 255 Music': 1.3, 'Forerunner 255S': 1.1, 'Forerunner 255S Music': 1.1, 'Forerunner 265': 1.3,
 'Forerunner 265S': 1.1, 'Forerunner 955': 1.3, 'Forerunner 955 Solar': 1.3, 'Forerunner 965': 1.4, 'Forerunner 165': 1.2,
 'Forerunner 165 Music': 1.2, 'Forerunner 745': 1.2, 'Forerunner 945': 1.2, 'Forerunner 945 LTE': 1.2, 'Forerunner 935': 1.2,
 'Forerunner 645': 1.2, 'Forerunner 645 Music': 1.2, 'Forerunner 570 42mm': 1.2, 'Forerunner 570 47mm': 1.4, 'Forerunner 970': 1.4,
 'Forerunner 70': 1.2, 'Forerunner 170': 1.2, 'Forerunner 170 Music': 1.2, 'Forerunner 230': 1.23, 'Forerunner 235': 1.23,
 'Forerunner 630': 1.23, 'Forerunner 735XT': 1.23, 'fenix 3': 1.2, 'fenix 3 HR': 1.2, 'fenix 5S': 1.1, 'fenix 5': 1.2, 'fenix 5X': 1.2,
 'fenix 5S Plus': 1.2, 'fenix 5 Plus': 1.2, 'fenix 5X Plus': 1.2, 'fenix 6S': 1.2, 'fenix 6': 1.3, 'fenix 6X': 1.4, 'fenix 7S': 1.2,
 'fenix 7': 1.3, 'fenix 7X': 1.4, 'fenix 7S Pro': 1.2, 'fenix 7 Pro': 1.3, 'fenix 7X Pro': 1.4, 'epix (Gen 2)': 1.3,
 'epix Pro (Gen 2) 42mm': 1.2, 'epix Pro (Gen 2) 47mm': 1.3, 'epix Pro (Gen 2) 51mm': 1.4, 'fenix 8 AMOLED 43mm': 1.3,
 'fenix 8 AMOLED 47mm': 1.4, 'fenix 8 AMOLED 51mm': 1.4, 'fenix 8 Solar 47mm': 1.3, 'fenix 8 Solar 51mm': 1.4, 'fenix E 47mm': 1.3,
 'fenix 8 Pro AMOLED 47mm': 1.4, 'fenix 8 Pro AMOLED 51mm': 1.4, 'fenix 9 43mm': 1.3, 'fenix 9 Pro 43mm': 1.3, 'fenix 9 47mm': 1.4,
 'fenix 9 Pro 47mm': 1.4, 'fenix 9 51mm': 1.4, 'fenix 9 Pro 51mm': 1.5, 'fenix 9 Pro Solar 47mm': 1.3, 'fenix 9 Pro Solar 51mm': 1.4, 'Venu': 1.2, 'Venu 2': 1.3, 'Venu 2S': 1.1, 'Venu 2 Plus': 1.3,
 'Venu 3': 1.4, 'Venu 3S': 1.2, 'Venu 4 41mm': 1.2, 'Venu 4 45mm': 1.4, 'vivoactive 3': 1.2, 'vivoactive 3 Music': 1.2,
 'vivoactive 4': 1.3, 'vivoactive 4S': 1.1, 'vivoactive 5': 1.2, 'vivoactive 6': 1.2, 'Enduro': 1.4, 'Enduro 2': 1.4, 'Enduro 3': 1.4,
 'Enduro 4': 1.4, 'MARQ (Gen 2)': 1.3, 'Approach S62': 1.3, 'Approach S60': 1.2, 'Approach S70 42mm': 1.1, 'Approach S70 47mm': 1.4,
 'Descent Mk2': 1.4, 'Descent Mk2i': 1.4, 'Descent Mk3 43mm': 1.2, 'Descent Mk3i 51mm': 1.4, 'D2 Mach 2 47mm': 1.4,
 'quatix 8 47mm': 1.4, 'quatix 8 51mm': 1.4, 'quatix 8 Pro 47mm': 1.4}
for k, v in GARMIN_IN.items(): ROUND['Garmin ' + k] = v * 25.4
SPLIT_IN = {'Galaxy Watch 42mm': 1.2, 'Galaxy Watch 46mm': 1.3, 'Galaxy Watch Active 40mm': 1.1, 'Galaxy Watch Active2 40mm': 1.2,
 'Galaxy Watch Active2 44mm': 1.4, 'Galaxy Watch Active2 Aluminum 40mm': 1.2, 'Galaxy Watch Active2 Aluminum 44mm': 1.4,
 'Galaxy Watch3 41mm': 1.2, 'Galaxy Watch3 45mm': 1.4, 'Galaxy Watch4 40mm': 1.2, 'Galaxy Watch4 44mm': 1.4,
 'Galaxy Watch4 Classic 42mm': 1.2, 'Galaxy Watch4 Classic 46mm': 1.4, 'Galaxy Watch5 40mm': 1.2, 'Galaxy Watch5 44mm': 1.4,
 'Galaxy Watch5 Pro 45mm': 1.4, 'Galaxy Watch6 40mm': 1.3, 'Galaxy Watch6 44mm': 1.5, 'Galaxy Watch6 Classic 43mm': 1.3,
 'Galaxy Watch6 Classic 47mm': 1.5, 'Galaxy Watch FE 40mm': 1.2, 'Galaxy Watch7 40mm': 1.3, 'Galaxy Watch7 44mm': 1.5,
 'Galaxy Watch Ultra 47mm': 1.5, 'Galaxy Watch8 40mm': 1.34, 'Galaxy Watch8 44mm': 1.47, 'Galaxy Watch8 Classic 46mm': 1.34,
 'Huawei Watch GT 2 42mm': 1.2, 'Huawei Watch GT 2 46mm': 1.39, 'Huawei Watch GT 3 42mm': 1.32, 'Huawei Watch GT 3 46mm': 1.43,
 'Huawei Watch GT 3 Pro 43mm': 1.32, 'Huawei Watch GT 3 Pro 46mm': 1.43, 'Huawei Watch GT 4 41mm': 1.32, 'Huawei Watch GT 4 46mm': 1.43,
 'Huawei Watch GT 5 41mm': 1.32, 'Huawei Watch GT 5 46mm': 1.43, 'Huawei Watch GT 5 Pro 42mm': 1.32, 'Huawei Watch GT 5 Pro 46mm': 1.43,
 'Huawei Watch GT 6 41mm': 1.32, 'Huawei Watch GT 6 46mm': 1.47, 'Honor MagicWatch 2 42mm': 1.2, 'Honor MagicWatch 2 46mm': 1.39}
SPLIT_IN.update(NM.ROUND6)
for k, v in SPLIT_IN.items(): ROUND.setdefault(k, v * 25.4)
import math
wear = {m['name']: m for g in groups if g['cat'] == 'Wearable' for m in g['members']}
UNI = collections.defaultdict(list)
for n, mm in ROUND.items():
    if n in wear: UNI[max(23, min(46, math.ceil(mm - 0.2)))].append(wear[n])
UNI_GROUP = {}
for sz in range(23, 47):
    seq += 1
    pm = dict(code='UNI', name=f'Universal round glass {sz}mm', cat='Misc', date='1900-01', seq=seq)
    mem = [pm] + sorted(UNI.get(sz, []), key=lambda m: (m['date'], m['seq']))
    g = dict(code='UNI', members=mem, status=K, cat='Misc', date='1900-01', seq=seq, brands=['UNI'],
             note=f'{sz}mm diameter, flat lenses only. Measure the flat part of the lens first' + (f'. Watches listed have a display about {sz-1}-{sz}mm across' if UNI.get(sz) else ''))
    groups.append(g); UNI_GROUP[sz] = g

# Number oldest first per brand + category
cnt = collections.Counter()
for g in sorted(groups, key=lambda g: (g['date'], g['seq'])):
    key = (g['code'], g['cat'])
    cnt[key] += 1
    assert cnt[key] <= 999, key
    g['id'] = f"{g['code']}-{CATBASE[g['cat']] + cnt[key]:04d}"

BRANDS = [
 ['APP', 'Apple', 'iPhone, iPad, Apple Watch'],
 ['SAM', 'Samsung', 'Galaxy phones, Galaxy Tab, Galaxy Watch and Gear. Ultrasonic fingerprint phones need FP-compatible glass'],
 ['GOO', 'Google', 'Nexus and Pixel phones, tablets, Pixel Watch, and Fitbit trackers and watches (Google owns Fitbit). Screen-free Fitbit Air not included'],
 ['OPP', 'Oppo', ''],
 ['ONE', 'OnePlus', ''],
 ['ZTE', 'ZTE', 'Includes nubia, Red Magic and ZTE-made Telstra and Optus phones'],
 ['MIC', 'Microsoft', 'Lumia and Surface Duo phones, Surface tablets'],
 ['LEN', 'Lenovo', 'Phones, Tab tablets, Legion Go and cloud handhelds'],
 ['ASU', 'Asus', 'Phones, tablets, Zenwatch, ROG Ally handhelds. ASU-4001 also fits the 7in MSI Claws'],
 ['MOT', 'Motorola', 'Phones, tablets, Moto 360 and Moto Watch'],
 ['XIA', 'Xiaomi / Redmi / Poco', ''],
 ['OPE', 'Opel Mobile', 'Smartphones only. Release order approximate'],
 ['NOK', 'Nokia / HMD', 'Nokia smartphones (Symbian, Lumia, Android), HMD phones, Nokia Steel HR/Go. Microsoft-branded Lumias are under MIC. Feature and KaiOS phones not included'],
 ['VIV', 'vivo / iQOO', 'vivo and iQOO phones, tablets and watches'],
 ['REA', 'Realme', 'Phones, tablets, watches and bands'],
 ['HUA', 'Huawei', 'Phones, MatePad tablets, watches and bands. Band release months approximate. Feature phones not included'],
 ['HON', 'Honor', 'Phones (including pre-2020 Huawei-era Honor models), tablets, watches and bands. Band release months approximate'],
 ['TCL', 'TCL / Alcatel', 'TCL and Alcatel smartphones and tablets. Feature and KaiOS phones not included'],
 ['NTH', 'Nothing / CMF', 'Nothing and CMF phones and watches'],
 ['LGE', 'LG', 'Smartphones, tablets and watches (LG left phones in 2021). Feature phones not included'],
 ['HTC', 'HTC', 'Windows Mobile, Windows Phone and Android phones, tablets'],
 ['BLB', 'BlackBerry', 'BlackBerry OS, BB10 and Android phones, PlayBook tablets'],
 ['FAI', 'Fairphone', 'Fairphone 1 to 6'],
 ['KOG', 'Kogan', 'Kogan Agora phones and tablets (Australian). Release months approximate'],
 ['ASP', 'Aspera', 'Aspera smartphones (Australian). Easy/flip and rugged button phones not included. Release months approximate'],
 ['ALL', 'Allview', 'Smartphones and tablets. Feature phones not included'],
 ['AMZ', 'Amazon', 'Fire Phone, Fire tablets and Kindle e-readers. Kids editions use the standard model glass'],
 ['AMO', 'Amoi', 'Smartphones and tablets. Feature phones not included'],
 ['ARC', 'Archos', 'Smartphones and tablets. Feature phones not included'],
 ['ATT', 'AT&T', 'Carrier/rebadge brand. Phones made by HTC, ZTE, Alcatel and others are grouped with the maker twin where specs match'],
 ['BEN', 'BenQ / BenQ-Siemens', 'BenQ and BenQ-Siemens smartphones. Feature phones not included'],
 ['BLV', 'Blackview', 'Rugged and budget phones and tablets. Oscal (Blackview sub-brand) twins grouped where specs match'],
 ['BLU', 'BLU', 'Smartphones and tablets. Feature phones not included'],
 ['BQX', 'BQ', 'Smartphones and tablets. Feature phones not included'],
 ['CAS', 'Casio', "G'zOne smartphones and Wear OS watches (Pro Trek WSD, G-Shock GSW). Plain digital watches not included"],
 ['CAT', 'Cat (Caterpillar)', 'Rugged Cat phones (made by Bullitt). Feature phones not included'],
 ['CEL', 'Celkon', 'Smartphones and tablets. Feature phones not included'],
 ['CPD', 'Coolpad', 'Smartphones and tablets. Feature phones not included'],
 ['CUB', 'Cubot', 'Smartphones and tablets. Feature phones not included'],
 ['DEL', 'Dell', 'Smartphones and tablets. Feature phones not included'],
 ['DOO', 'Doogee', 'Smartphones and tablets. Feature phones not included'],
 ['ENE', 'Energizer', 'Smartphones and tablets. Feature phones not included'],
 ['ETE', 'Eten', 'Smartphones and tablets. Feature phones not included'],
 ['FUJ', 'Fujitsu Siemens', 'Smartphones and tablets. Feature phones not included'],
 ['GIG', 'Gigabyte', 'Smartphones and tablets. Feature phones not included'],
 ['GIO', 'Gionee', 'Smartphones and tablets. Feature phones not included'],
 ['HAI', 'Haier', 'Smartphones and tablets. Feature phones not included'],
 ['HPQ', 'HP', 'Smartphones and tablets. Feature phones not included'],
 ['IMA', 'i-mate', 'Carrier/rebadge brand. Phones made by HTC, ZTE, Alcatel and others are grouped with the maker twin where specs match'],
 ['IMO', 'i-mobile', 'Smartphones and tablets. Feature phones not included'],
 ['ICE', 'Icemobile', 'Smartphones and tablets. Feature phones not included'],
 ['INF', 'Infinix', 'Transsion brand. Twins of Tecno and itel phones are grouped together where specs match'],
 ['INQ', 'INQ', 'Smartphones and tablets. Feature phones not included'],
 ['INX', 'Intex', 'Smartphones and tablets. Feature phones not included'],
 ['ITE', 'itel', 'Transsion brand. Twins of Tecno and Infinix phones are grouped together where specs match. Feature phones not included'],
 ['JOL', 'Jolla', 'Smartphones and tablets. Feature phones not included'],
 ['KAR', 'Karbonn', 'Smartphones and tablets. Feature phones not included'],
 ['KYO', 'Kyocera', 'Rugged phones (DuraForce, Torque) and DuraSlate. Flip/feature phones not included'],
 ['LAV', 'Lava', 'Smartphones and tablets. Feature phones not included'],
 ['LEE', 'LeEco', 'Smartphones and tablets. Feature phones not included'],
 ['MXW', 'Maxwest', 'Smartphones and tablets. Feature phones not included'],
 ['MEI', 'Meizu', 'Smartphones and tablets. Feature phones not included'],
 ['MMX', 'Micromax', 'Smartphones and tablets. YU (Micromax online brand) twins grouped where specs match. Feature phones not included'],
 ['MIT', 'Mitac', 'Smartphones and tablets. Feature phones not included'],
 ['MSB', 'Mitsubishi', 'Smartphones and tablets. Feature phones not included'],
 ['MWG', 'MWg', 'Smartphones and tablets. Feature phones not included'],
 ['NEC', 'NEC', 'Terrain smartphone and the TurboExpress / PC Engine GT handheld (1990)'],
 ['NEO', 'Neonode', 'Smartphones and tablets. Feature phones not included'],
 ['NIU', 'NIU', 'Smartphones and tablets. Feature phones not included'],
 ['OTW', 'O2', 'Carrier/rebadge brand. Phones made by HTC, ZTE, Alcatel and others are grouped with the maker twin where specs match'],
 ['ORA', 'Orange', 'Carrier/rebadge brand. Phones made by HTC, ZTE, Alcatel and others are grouped with the maker twin where specs match'],
 ['OSC', 'Oscal', 'Blackview sub-brand. Twins grouped with Blackview where specs match'],
 ['OUK', 'Oukitel', 'Smartphones and tablets. Feature phones not included'],
 ['PLM', 'Palm', 'Palm Pre/Pixi/Treo smartphones and the 2018 Palm phone'],
 ['PNS', 'Panasonic', 'Smartphones and tablets. Feature phones not included'],
 ['PNT', 'Pantech', 'Smartphones and tablets. Feature phones not included'],
 ['PAR', 'Parla', 'Smartphones and tablets. Feature phones not included'],
 ['PHI', 'Philips', 'Smartphones and tablets. Feature phones not included'],
 ['PLU', 'Plum', 'Smartphones and tablets. Feature phones not included'],
 ['POS', 'Posh', 'Smartphones and tablets. Feature phones not included'],
 ['PRE', 'Prestigio', 'Smartphones and tablets. Feature phones not included'],
 ['QMO', 'QMobile', 'Smartphones and tablets. Feature phones not included'],
 ['QTE', 'Qtek', 'Carrier/rebadge brand. Phones made by HTC, ZTE, Alcatel and others are grouped with the maker twin where specs match'],
 ['RUG', 'RugOne', 'Smartphones and tablets. Feature phones not included'],
 ['SAG', 'Sagem', 'Smartphones and tablets. Feature phones not included'],
 ['SEN', 'Sendo', 'Smartphones and tablets. Feature phones not included'],
 ['SHA', 'Sharp', 'Smartphones and tablets. Feature phones not included'],
 ['SIE', 'Siemens', 'Smartphones and tablets. Feature phones not included'],
 ['SNM', 'Sonim', 'Rugged phones. Feature phones not included'],
 ['SPI', 'Spice', 'Smartphones and tablets. Feature phones not included'],
 ['TMO', 'T-Mobile', 'Carrier/rebadge brand. Phones made by HTC, ZTE, Alcatel and others are grouped with the maker twin where specs match'],
 ['TEC', 'Tecno', 'Transsion brand. Twins of Infinix and itel phones are grouped together where specs match'],
 ['TME', 'Tel.Me.', 'Smartphones and tablets. Feature phones not included'],
 ['TLT', 'Telit', 'Smartphones and tablets. Feature phones not included'],
 ['THU', 'Thuraya', 'Smartphones and tablets. Feature phones not included'],
 ['TOS', 'Toshiba', 'Smartphones and tablets. Feature phones not included'],
 ['ULE', 'Ulefone', 'Smartphones and tablets. Feature phones not included'],
 ['UMI', 'Umidigi', 'Smartphones and tablets. Feature phones not included'],
 ['UNN', 'Unnecto', 'Smartphones and tablets. Feature phones not included'],
 ['VRT', 'Vertu', 'Vertu smartphones. Signature button phones not included'],
 ['VER', 'verykool', 'Smartphones and tablets. Feature phones not included'],
 ['VOD', 'Vodafone', 'Carrier/rebadge brand. Phones made by HTC, ZTE, Alcatel and others are grouped with the maker twin where specs match'],
 ['WIK', 'Wiko', 'Smartphones and tablets. Feature phones not included'],
 ['XOL', 'XOLO', 'Smartphones and tablets. Feature phones not included'],
 ['YEZ', 'Yezz', 'Smartphones and tablets. Feature phones not included'],
 ['YOT', 'Yota', 'Smartphones and tablets. Feature phones not included'],
 ['YUX', 'YU', 'Micromax online brand'],
 ['NIN', 'Nintendo', 'Game Boy to Switch 2 and Pokémon mini'],
 ['VAL', 'Valve', 'Steam Deck'],
 ['MSI', 'MSI', 'Claw handhelds. 7in Claws use ASU-4001'],
 ['LOG', 'Logitech', 'G Cloud handheld'],
 ['GPD', 'GPD', 'Win, Win Max, Win Mini and XD/XP handhelds. Pocket, MicroPC and Duo laptops not included. Release months approximate'],
 ['SON', 'Sony', 'Sony and Sony Ericsson smartphones (2002 on), Xperia tablets, SmartWatch, PSP, PS Vita, PlayStation Portal'],
 ['RAZ', 'Razer', 'Razer Phone and Razer Edge'],
 ['RET', 'Retroid', 'Retroid Pocket handhelds. Release months approximate'],
 ['MIY', 'Miyoo', 'Release months approximate'],
 ['AYN', 'AYN', 'Odin, Loki and Thor handhelds. Release months approximate'],
 ['ANB', 'Anbernic', 'RG and WIN handhelds. Release months approximate'],
 ['TRI', 'TrimUI', 'Release months approximate'],
 ['AYA', 'AYANEO', 'Windows and Android handhelds. Release months approximate'],
 ['KON', 'KONKR', "AYANEO's budget brand. Release months approximate"],
 ['ONX', 'OneXPlayer', 'Windows handhelds. Super X tablet not included. Release months approximate'],
 ['ZOT', 'Zotac', 'Zone handhelds'],
 ['BIT', 'Bittboy', 'Release months approximate'],
 ['POW', 'Powkiddy', 'Main retro handhelds only; Powkiddy makes many short-run models. Release months approximate'],
 ['MOD', 'ModRetro', 'Chromatic handheld. M64 is a home console, not included'],
 ['FUN', 'FunnyPlaying', 'Own handhelds only. Their IPS screen kits go in Nintendo Game Boys (NIN)'],
 ['CLK', 'ClockworkPi', 'GameShell, DevTerm, uConsole and PicoCalc kits. Release months approximate'],
 ['ANA', 'Analogue', 'Pocket handheld. Analogue 3D, Duo, Mega Sg and Super Nt are home consoles, not included'],
 ['PAN', 'Panic (Playdate)', 'Playdate handheld'],
 ['SEG', 'SEGA', 'Game Gear, Nomad and Game Gear Micro'],
 ['ATA', 'Atari', 'Lynx handhelds'],
 ['SNK', 'SNK', 'Neo Geo Pocket handhelds'],
 ['BAN', 'Bandai', 'WonderSwan handhelds'],
 ['TIG', 'Tiger', 'Game.com handhelds'],
 ['NVI', 'NVIDIA', 'Shield Portable handheld and Shield/Tegra tablets. Shield TV has no screen'],
 ['ACE', 'Acer', 'Liquid phones, Iconia tablets, Liquid Leap wearables, Nitro Blaze and Predator Atlas handhelds. Laptops and Chromebooks not included'],
 ['MGX', 'MagicX', 'Retro handhelds. Release months approximate'],
 ['MNG', 'Mangmi', 'Android handhelds. Release months approximate'],
 ['GKD', 'GKD (Game Kiddy)', 'Retro handhelds. Release months approximate'],
 ['EVC', 'Evercade', 'Handhelds only. VS and Alpha are home and bartop systems, not included'],
 ['HYP', 'Hyperkin', 'SupaBoy SNES handhelds. Retron home consoles not included'],
 ['MYA', 'My Arcade', 'Grouped by body style: every licensed game edition of a body shares one group. Release months approximate. Plug-and-play TV consoles not included'],
 ['UNI', 'Universal', 'Universal round watch glass by diameter (Misc range). Flat lenses only: measure the flat part of the lens before fitting'],
 ['GAR', 'Garmin', 'Garmin watches and bands (2003 on) plus Garmin-Asus phones. Watch release months approximate. Sat navs, bike computers and handheld GPS not included'],
 ['AMF', 'Amazfit', 'Amazfit watches and bands. Screen-free Helio Strap and Helio Ring not included. Release months approximate'],
 ['FOS', 'Fossil Group', 'Fossil, Skagen, Michael Kors Access, Diesel and Emporio Armani Wear OS watches. Hybrids without touchscreens not included. Release months approximate'],
 ['TIC', 'TicWatch (Mobvoi)', 'TicWatch Wear OS and GTX/GTH watches. Release months approximate'],
 ['POL', 'Polar', 'Watches with screens. Screen-free Polar Loop not included. Release months approximate'],
 ['SUU', 'Suunto', 'Watches from Ambit on. Release months approximate'],
 ['COR', 'Coros', 'GPS watches. Dura bike computer not included. Release months approximate'],
 ['WIT', 'Withings', 'Hybrid and ScanWatch watches. Glass covers the whole analog face: measure the lens. Release months approximate'],
 ['SPT', 'Spacetalk', 'Kids and seniors 4G watches (Australian). Glass is model-specific. Release months approximate'],
 ['KOB', 'Kobo', 'E-readers (Tablet range). Release months approximate'],
 ['RMK', 'reMarkable', 'E-ink tablets (Tablet range)'],
 ['BOX', 'Onyx Boox', 'Main e-reader and e-ink tablet lines (Tablet range). Boox releases many variants: check the screen size. Release months approximate'],
 ['PKB', 'PocketBook', 'Main e-readers (Tablet range). Release months approximate'],
]
for sz, g in UNI_GROUP.items():
    for m in g['members'][1:]:
        og = next(x for x in groups if x is not g and m in x['members'])
        add = f"Universal round glass: try {g['id']} ({sz}mm); measure first"
        if add not in og['note']: og['note'] = (og['note'] + '. ' if og['note'] else '') + add
NAME = {b[0]: b[1] for b in BRANDS}
ORDER = [b[0] for b in BRANDS]
groups.sort(key=lambda g: (ORDER.index(g['code']), g['id']))
# Fit tags: caveats staff should know before fitting, from notes and specs
TAGS = [('cover', r'cover screen|Foldable'), ('two-screens', r'^Two screens|two screens'), ('case-friendly', r'case[- ]friendly'),
        ('curved', r'curved'), ('uv', r'\bUV\b'), ('measure', r'measure')]  # hybrid glass stays in notes: it describes listings, not the device
def fit_tags(g):
    t = [k for k, rx in TAGS if re.search(rx, g['note'], re.I)]
    if any(m.get('ufp') for m in g['members']): t.insert(0, 'fingerprint')
    return t
def _per_model(g, key, out):
    cover = 'cover' in fit_tags(g)  # foldables: cover glass fits the cover screen and the folded body
    vals = [m.get('c' + key, '') if cover else m.get(key, '') for m in g['members']]
    if key == 'dims' and g['cat'] != 'Wearable':  # longest side first, so sizes compare (some tablets are listed landscape)
        def _long(v):
            n = re.findall(r'[\d.]+', v)
            return f'{n[1]} x {n[0]} x {n[2]} mm' if len(n) == 3 and float(n[1]) > float(n[0]) else v
        vals = [_long(v) if v else v for v in vals]
    return {out: vals} if any(vals) else {}
# Apple identifiers in one spelling (GSMArena has both iphone15,2 and iPhone15,2)
def _mnfix(codes):
    fixed = re.sub(r'(?<![A-Za-z])(iphone|ipad|ipod|watch)(?=\d)', lambda x: {'iphone': 'iPhone', 'ipad': 'iPad', 'ipod': 'iPod', 'watch': 'Watch'}[x.group(1).lower()], codes, flags=re.I)
    return ', '.join(dict.fromkeys(c for c in fixed.split(', ') if c))
out = []
for g in groups:
    out.append(dict(id=g['id'], brand=' + '.join(NAME[c] for c in g['brands']), brands=g['brands'], models=[m['name'] for m in g['members']],
                    released=[m['date'] for m in g['members']], check=g['status'], note=g['note'], device=g['cat'],
                    **({'sources': g['sources']} if g.get('sources') else {}),
                    **({'codes': [_mnfix(m.get('codes', '')) for m in g['members']]} if any(m.get('codes') for m in g['members']) else {}),
                    **_per_model(g, 'screen', 'screens'), **_per_model(g, 'dims', 'dims'), **({'tags': fit_tags(g)} if fit_tags(g) else {})))
json.dump(dict(brands=BRANDS, groups=out), open(ROOT + '/data.json', 'w', encoding='utf-8', newline='\n'), indent=0)
print(len(out), 'groups,', sum(len(g['models']) for g in out), 'models')
print(collections.Counter((g['id'][:3], g['device']) for g in out))
print('Confirmed', sum(g['check'] == C for g in out))
