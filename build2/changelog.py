"""Record what changed in the fit groups since the last published catalogue.

Compares data.json at a git ref (default HEAD, the last commit) with the working data.json,
and writes an entry to docs/data/changelog.json for the Changes page.
Running it again for the same base replaces that entry instead of adding another.

  python build2/changelog.py "Verified Moto G fits"            # HEAD -> working copy
  python build2/changelog.py "Title" --base abc123 --head def456 --date 2026-11-22
"""
import argparse, collections, datetime, json, os, subprocess

ROOT = os.environ.get('PROTECTOR_ROOT', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'docs', 'data', 'changelog.json')

ap = argparse.ArgumentParser()
ap.add_argument('title')
ap.add_argument('--base', default='HEAD', help='git ref of the previous catalogue')
ap.add_argument('--head', help='git ref of the new catalogue (default: working data.json)')
ap.add_argument('--date', default=datetime.date.today().isoformat())
ap.add_argument('--summary', default='', help='one or two sentences on what was done')
a = ap.parse_args()


def at(ref):
    return json.loads(subprocess.run(['git', 'show', f'{ref}:data.json'], cwd=ROOT, capture_output=True, check=True).stdout)


def short(ref):
    return subprocess.run(['git', 'rev-parse', '--short', ref], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()


old = at(a.base)
new = at(a.head) if a.head else json.load(open(os.path.join(ROOT, 'data.json'), encoding='utf-8'))
real = lambda d: [g for g in d['groups'] if g['brands'] != ['UNI']]
O = {m: g for g in real(old) for m in g['models']}
N = {m: g for g in real(new) for m in g['models']}

changes = []
for g in real(new):
    olds = list(dict.fromkeys(O[m]['id'] for m in g['models'] if m in O))
    added = [m for m in g['models'] if m not in O]
    kinds = []
    if not olds:
        kinds.append('new')
    else:
        prev = next(O[m] for m in g['models'] if m in O)  # the old group of this group's first known model
        same = len(olds) == 1 and set(prev['models']) == set(g['models'])
        if len(olds) > 1: kinds.append('merged')
        elif not same: kinds.append('split' if not added and len(g['models']) < len(prev['models']) else 'models changed')
        if olds != [g['id']]: kinds.append('renumbered' if same else 'new code' if g['id'] not in olds else None)
        kinds = [k for k in kinds if k]
        checks = {O[m]['check'] for m in g['models'] if m in O}
        if g['check'] == 'Confirmed' and checks != {'Confirmed'}: kinds.append('confirmed')
        if g['check'] != 'Confirmed' and 'Confirmed' in checks: kinds.append('unconfirmed')
        if added: kinds.append('models added')
    if not kinds: continue
    c = dict(code=g['id'], kinds=kinds, old=olds, models=g['models'], check=g['check'])
    if added: c['added'] = added
    changes.append(c)
removed = sorted(m for m in O if m not in N)

REPRINT = {'new', 'merged', 'split', 'models changed', 'renumbered', 'new code', 'models added'}
count = collections.Counter(k for c in changes for k in c['kinds'])
when = (subprocess.run(['git', 'log', '-1', '--format=%cI', a.head], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
        if a.head else datetime.datetime.now().astimezone().isoformat(timespec='seconds'))
entry = dict(date=a.date, time=when, title=a.title, summary=a.summary, base=short(a.base), head=short(a.head) if a.head else None,
             counts=dict(count), reprint=sum(1 for c in changes if REPRINT & set(c['kinds'])),
             changes=changes, removed=removed)

log = json.load(open(OUT, encoding='utf-8')) if os.path.exists(OUT) else {'entries': []}
log['entries'] = [e for e in log['entries'] if e.get('base') != entry['base'] or e.get('head') != entry['head']]
log['entries'].append(entry)
log['entries'].sort(key=lambda e: (e['date'], e.get('time', '')), reverse=True)
with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(log, f, ensure_ascii=False, separators=(',', ':'))
print(a.date, a.title, '|', dict(count), '| labels to reprint:', entry['reprint'], '| removed models:', len(removed))
