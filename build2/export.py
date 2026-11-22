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

# Compact form: brands [[code, name, notes]],
# groups [[id, brand codes, device, check, note, [[model, released, model numbers?]], [[source name, url]]?]]
site = dict(
    built=datetime.date.today().isoformat(),
    brands=brands,
    groups=[[g['id'], g['brands'], g['device'], g['check'], g['note'],
             [[m, r] + ([c] if c else []) for m, r, c in zip(g['models'], g['released'], g.get('codes') or [''] * len(g['models']))]]
            + ([g['sources']] if g.get('sources') else [])
            for g in groups],
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


write_csv('fit-groups.csv', ['Group', 'Brand', 'Device', 'Fit check', 'Fits models', 'First released', 'Notes', 'Sources'],
          [[g['id'], g['brand'], g['device'], g['check'], '; '.join(g['models']),
            min((released(r) for r in g['released'] if released(r)), default=''), g['note'],
            ' '.join(u for _, u in g.get('sources', []))] for g in groups])
write_csv('models.csv', ['Model', 'Group', 'Brand', 'Device', 'Released', 'Model numbers'],
          [[m, g['id'], g['brand'], g['device'], released(r), c] for g in groups
           for m, r, c in zip(g['models'], g['released'], g.get('codes') or [''] * len(g['models']))])
write_csv('brands.csv', ['Code', 'Brand', 'Notes'], brands)

print(len(groups), 'groups,', sum(len(g['models']) for g in groups), 'models,', len(brands), 'brands ->', OUT)
