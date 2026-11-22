"""Fail if a fresh build differs from what's committed (run after build.py and export.py).

The site JSON carries its build date, so it is compared without that field.
"""
import json, subprocess, sys

FILES = ['data.json', 'docs/data/fit-groups.csv', 'docs/data/models.csv', 'docs/data/brands.csv']
bad = [f for f in FILES if subprocess.run(['git', 'diff', '--quiet', '--', f]).returncode]

committed = json.loads(subprocess.run(['git', 'show', 'HEAD:docs/data/catalogue.json'], capture_output=True, check=True).stdout)
built = json.load(open('docs/data/catalogue.json', encoding='utf-8'))
committed.pop('built', None); built.pop('built', None)
if committed != built: bad.append('docs/data/catalogue.json')

if bad:
    print('The committed catalogue does not match a fresh build. Run build/build.py and build2/export.py, then commit:')
    for f in bad: print('  ' + f)
    subprocess.run(['git', 'diff', '--stat', '--'] + FILES)
    sys.exit(1)
print('Committed catalogue matches a fresh build.')
