<h1>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/media/logo-dark.png">
    <img src="docs/media/logo-light.png" alt="Tempered" width="420">
  </picture>
</h1>

**Screen protector fit guide.** An open reference for tempered glass: which glass fits which device, and which models share the same glass. It's for any repair shop or reseller that wants to catalogue, store and label protector stock.

**Site:** https://welfedted.github.io/tempered/

- **Fit finder:** type a model and get its fit group code plus every other model that takes the same glass. Filter by device type and brand, and sort the results.
- **Label maker:** print divider tabs and pack stickers as PDFs for thermal label printers or A4 sheets.
- **Storage system:** a drawer layout and 3D-printable label dividers (STL and OpenSCAD).
- **Data downloads:** fit groups, models and brands as CSV or JSON in [`docs/data/`](docs/data).

The catalogue has 9,139 fit groups covering 12,217 models from 157 brands: phones, tablets, e-readers, wearables and handheld consoles.

## Codes

`APP-1013-C` breaks down as:

- **`APP`**: a 3-letter brand code (see [`brands.csv`](docs/data/brands.csv)).
- **`1013`**: the fit group number.
- **`C`**: the glass type, used on printed labels. `C` is Clear, `P` Privacy, `M` Matte.

| Range | Category |
|---|---|
| 0001+ | Misc: universal round watch glass (`UNI-0001` to `UNI-0024`, 23–46 mm), iPods |
| 1001+ | Phones |
| 2001+ | Tablets and e-readers |
| 3001+ | Wearables |
| 4001+ | Handheld consoles |
| 5001+ | Laptops (reserved) |

How the numbers are assigned:

- **Order:** within a brand and category, groups are numbered oldest first by the earliest release in the group. Adding a missing older model can shift later numbers, so a rebuild can mean reprinting some labels.
- **Groups across brands:** a group spanning brands (rebadges and same-body twins) takes the code of the brand with the earliest model.
- **Related brand names share one code:** Sony Ericsson → SON, HMD → NOK, iQOO → VIV, Alcatel → TCL, CMF → NTH, Fitbit → GOO, BenQ-Siemens → BEN, Redmi/Poco → XIA, nubia/Red Magic → ZTE, and the Fossil watch brands → FOS.

## How reliable are the fits?

Every group is marked **Confirmed** or **Check** (shown as "Unverified" on the site):

- **Confirmed** (81 groups): a glass maker or seller lists the models together.
- **Check**: either the models match on body size, screen size and resolution, or the model stands alone. Test the fit before swapping.

Fixes are very welcome. If you've confirmed that a pack fits, or found a mismatch, [open an issue](https://github.com/WelFedTed/tempered/issues).

## Scope

- **Included:** smartphones, tablets, e-readers, smartwatches and bands with screens, and handheld consoles.
- **Not included yet:** feature and KaiOS phones, laptops and Chromebooks, sat navs and bike computers, home consoles, and trackers without a screen.

## Building the catalogue

Requires Python 3. The scripts have no other dependencies.

```sh
python build/build.py      # sources -> data.json
python build2/export.py    # data.json -> docs/data/ (site JSON and CSVs)
```

- **`build/build.py`** is the whole pipeline; read it top to bottom. In order, it:
  1. loads `ds/base.json` and `ds/extra.json` (a Sep 2024 device snapshot);
  2. adds every smartphone, tablet and watch for known brands from the July 2026 GSMArena catalogue in `ds/gsmarena-catalog-builder/`, skipping cancelled, rumoured and feature phones;
  3. adds hand-researched lists from `build/newmodels.py`. Each line is `date|C|CODE|Name[;Name…]`, where C is P/T/W/H/M and `;` joins models that share glass;
  4. merges known shared-glass sets, variants and spec twins (union-find over identical body and screen specs, restricted to brand families and carrier rebadges);
  5. links round watches to universal round glass by display diameter;
  6. numbers the groups and writes `data.json`.
- **`build2/classify.py`** decides phone, tablet or watch for catalogue devices.
- **`build2/newcodes.json`** maps brand names to codes for brands added from the catalogue.

`data.json` is the source of truth. The site reads `docs/data/catalogue.json`, so run both scripts after any change and commit the results.

## Site

- The site is static, in [`docs/`](docs), served by GitHub Pages from `main`.
- To preview it locally, run `python -m http.server 8765 --directory docs` and open http://localhost:8765.
- [`docs/assets/catalogue.js`](docs/assets/catalogue.js) holds the shared loading and search code.
- The label maker uses [jsPDF](https://github.com/parallax/jsPDF) from cdnjs.
- The look is "label tape": bench paper (`#F4F2EC`), ink (`#111111`) and one signal orange (`#E8590C`), with headings in [Archivo](https://fonts.google.com/specimen/Archivo) at weight 900 and codes in [JetBrains Mono](https://fonts.google.com/specimen/JetBrains+Mono), both from Google Fonts.
- The mark is a screen with its protector peeling back at the corner. `docs/favicon.svg` is the site icon, and `python build2/make_icons.py` (needs Pillow) redraws the PNG and ICO versions from the same shape. The README logo is `docs/media/logo-light.png` and `logo-dark.png`.

## Dividers

[`dividers/protector_divider.scad`](dividers/protector_divider.scad) is the parametric divider. Set `pack_long` and `pack_short` to your pack size.

[`dividers/make_stl.py`](dividers/make_stl.py) builds the same shapes with `manifold3d`, `trimesh` and `numpy`. The published STLs are copied into `docs/dividers/`.

## Data sources

- **Device catalogue:** [gsmarena-catalog-builder](https://github.com/adelindanaila05/gsmarena-catalog-builder), full catalogue snapshot of July 2026. Product names and source-site data remain the property of their owners.
- **Hand-researched lists:** compiled from manufacturer announcements, retailer and protector-maker compatibility lists, and review sites. Release months for some watch, e-reader and retro brands are approximate; this is noted on those brands.
