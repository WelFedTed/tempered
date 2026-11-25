"""Export data.json for the GitHub Pages site.

Writes into docs/data/:
  catalogue.json  compact copy of data.json used by the search page and label maker
  fit-groups.csv  one row per fit group
  models.csv      one row per model
  brands.csv      brand codes
"""
import csv, json, os, datetime

ROOT = os.environ.get('PROTECTOR_ROOT', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'docs', 'data')
os.makedirs(OUT, exist_ok=True)

d = json.load(open(os.path.join(ROOT, 'data.json'), encoding='utf-8'))
groups, brands = d['groups'], d['brands']

# Compact form, trailing empty fields dropped:
# brands [[code, name, notes]]
# apart  [[group id, group id]] known to need different glass
# groups [[id, brand codes, device, check, note, models, sources, fit tags]]
#   models  [[name, released, model numbers, screen size, body dimensions]]
#   sources [[name, url]]
def trim(a):
    while a and a[-1] in ('', [], None): a.pop()
    return a


def per_model(g, key):
    return g.get(key) or [''] * len(g['models'])


# Pairs of groups that sellers show need different glass ("separate" findings in build/verified.json),
# so the site never suggests one as a similar-size glass to try for the other
gid = {m: g['id'] for g in groups for m in g['models']}
apart = set()
for f in json.load(open(os.path.join(ROOT, 'build', 'verified.json'), encoding='utf-8')):
    if f['fit'] != 'separate' or f.get('weak'): continue
    ids = sorted({gid[m] for m in f['models'] if m in gid})
    apart.update((x, y) for i, x in enumerate(ids) for y in ids[i + 1:])

site = dict(
    built=datetime.date.today().isoformat(),
    brands=brands,
    apart=sorted(list(x) for x in apart),
    groups=[trim([g['id'], g['brands'], g['device'], g['check'], g['note'],
                  [trim([m, r, c, sc, dm]) for m, r, c, sc, dm in
                   zip(g['models'], g['released'], per_model(g, 'codes'), per_model(g, 'screens'), per_model(g, 'dims'))],
                  g.get('sources', []), g.get('tags', [])]) for g in groups],
)
with open(os.path.join(OUT, 'catalogue.json'), 'w', encoding='utf-8', newline='\n') as f:
    json.dump(site, f, ensure_ascii=False, separators=(',', ':'))


def write_csv(name, header, rows):
    with open(os.path.join(OUT, name), 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(header)
        w.writerows(rows)


def released(r):
    return '' if r.startswith('1900') else r


write_csv('fit-groups.csv', ['Group', 'Brand', 'Device', 'Fit check', 'Fits models', 'First released', 'Notes', 'Fit tags', 'Sources'],
          [[g['id'], g['brand'], g['device'], g['check'], '; '.join(g['models']),
            min((released(r) for r in g['released'] if released(r)), default=''), g['note'], ' '.join(g.get('tags', [])),
            ' '.join(u for _, u in g.get('sources', []))] for g in groups])
write_csv('models.csv', ['Model', 'Group', 'Brand', 'Device', 'Released', 'Model numbers', 'Screen', 'Body (mm)'],
          [[m, g['id'], g['brand'], g['device'], released(r), c, sc, dm.replace(' mm', '')] for g in groups
           for m, r, c, sc, dm in zip(g['models'], g['released'], per_model(g, 'codes'), per_model(g, 'screens'), per_model(g, 'dims'))])
write_csv('brands.csv', ['Code', 'Brand', 'Notes'], brands)

print(len(groups), 'groups,', sum(len(g['models']) for g in groups), 'models,', len(brands), 'brands ->', OUT)
