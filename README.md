<h1>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/media/logo-dark.png">
    <img src="docs/media/logo-light.png" alt="Tempered" width="420">
  </picture>
</h1>

**Screen protector fit guide.** An open reference for tempered glass: which glass fits which device, and which models share the same glass. It's for any repair shop or reseller that wants to catalogue, store and label protector stock.

**Site:** https://welfedted.github.io/tempered/

- **Fit finder:** type a model or its model number (e.g. `A2221`, `SM-S938B`, `iphone a222`) and get its fit group code plus every other model that takes the same glass. Results show screen size and body dimensions for measuring, fit tags (ultrasonic fingerprint, cover screen only, two screens, measure first…), seller sources, and a **Report a fit** link that opens a pre-filled GitHub issue. Filter by device type, brand and fit tag, and sort the results.
- **Similar Sized Protectors:** under the results for a specific model, other groups with the same screen size (within 0.05in) and a body within 1.5 mm, closest first, as glass to try when nothing confirmed is in stock. They're not confirmed to fit, and groups sellers have shown need different glass are left out.
- **Label maker:** print divider tabs and pack stickers as PDFs for thermal label printers or A4 sheets, with a QR code in the top-right corner that opens the group in the fit finder, a Code 128 barcode of the label code (e.g. `APP-1014-C`) along the bottom, the fit tags in short form, and optionally a sell price you type in.
- **Changes:** a changelog of every update to the fit groups (merged, split, new, renumbered, confirmed), with a button to print every label an update changed.
- **Storage system:** a drawer layout and 3D-printable label dividers (STL and OpenSCAD).
- **Works offline:** once opened, the site and catalogue are cached, so lookups still work without internet.
- **Data downloads:** fit groups, models (with model numbers, screen size and dimensions) and brands as CSV or JSON in [`docs/data/`](docs/data).

The catalogue has 8,968 fit groups covering 12,343 models from 157 brands: phones, tablets, e-readers, wearables and handheld consoles.

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

Every group is marked **Confirmed**, **Variant** (shown as "Same model" on the site) or **Check** (shown as "Unverified"):

- **Confirmed** (706 groups): a glass maker or seller lists the models together, or sells glass for that one model alone.
- **Variant** (129 groups): the models are one device sold in region, carrier, SIM, memory or connectivity versions (such as Duos, LTE, Wi-Fi or USA), and their bodies are within 1 mm. 4G/5G versions count only when both bodies are on record and match. They almost always take the same glass, but no seller has confirmed it.
- **Check**: either the models match on body size, screen size and resolution, or the model stands alone. Test the fit before swapping.

Groups checked against protector brands, retailers and marketplaces carry their source links on the site. The findings live in [`build/verified.json`](build/verified.json); each entry is:

```json
{"models": ["Galaxy S24", "Galaxy S25"], "fit": "same", "sources": [{"name": "PanzerGlass", "url": "https://..."}], "note": "PanzerGlass lists both"}
```

- **`same`:** the models take one glass. Their groups are merged.
- **`own`:** glass is sold for that one model alone.
- **`separate`:** the models need different glass. Any that share a group are split apart.
- **`"weak": true`:** thin evidence, such as one marketplace listing. Its note and sources are shown, but it doesn't merge groups or mark them Confirmed.

A group is Confirmed when its models are all linked by `same` findings (or it's a single model with an `own` finding). If only some are, the note says which ones sellers confirm.

Fixes are very welcome. If you've confirmed that a pack fits, or found a mismatch, use **Report a fit** on the result, or [open a fit report](https://github.com/WelFedTed/tempered/issues/new?template=fit-report.yml).

## Scope

- **Included:** smartphones, tablets, e-readers, smartwatches and bands with screens, and handheld consoles.
- **Not included yet:** feature and KaiOS phones, laptops and Chromebooks, sat navs and bike computers, home consoles, and trackers without a screen.

## Building the catalogue

Requires Python 3. The scripts have no other dependencies.

```sh
python build/build.py      # sources -> data.json
python build2/export.py    # data.json -> docs/data/ (site JSON and CSVs)
python build2/changelog.py "What changed" --summary "One or two sentences"   # adds an entry to the Changes page
```

`changelog.py` compares `data.json` in the last commit with the new build, so run it before committing. Running it again replaces that entry. Then commit everything to `main`; the **Build check** workflow rebuilds the catalogue and fails if the committed data doesn't match.

- **`build/build.py`** is the whole pipeline; read it top to bottom. In order, it:
  1. loads `ds/base.json` and `ds/extra.json` (a Sep 2024 device snapshot);
  2. adds every smartphone, tablet and watch for known brands from the July 2026 GSMArena catalogue in `ds/gsmarena-catalog-builder/`, skipping cancelled, rumoured and feature phones;
  3. adds hand-researched lists from `build/newmodels.py`. Each line is `date|C|CODE|Name[;Name…]`, where C is P/T/W/H/M and `;` joins models that share glass;
  4. merges known shared-glass sets, variants and spec twins (union-find over identical body and screen specs, restricted to brand families and carrier rebadges);
  5. applies the verified findings in `build/verified.json`;
  6. links round watches to universal round glass by display diameter;
  7. numbers the groups and writes `data.json`, with model numbers (from the GSMArena catalogue plus Apple's official lists in `build/modelnumbers.json`), screen sizes, body dimensions and fit tags. Sizes come from the GSMArena catalogue, then hand-researched sizes in `build/sizes.json` (`{"Model": {"screen": "1.4in", "dims": "47 x 47 x 14.5 mm", "source": url}}`, with `"cover": true` for a foldable's cover screen and folded body). Foldables show their cover screen and folded body, since that's what the glass fits.
- **`build2/classify.py`** decides phone, tablet or watch for catalogue devices.
- **`build2/newcodes.json`** maps brand names to codes for brands added from the catalogue.

`data.json` is the source of truth. The site reads `docs/data/catalogue.json`, so run both scripts after any change and commit the results.

## Site

- The site is static, in [`docs/`](docs), served by GitHub Pages from `main`.
- To preview it locally, run `python -m http.server 8765 --directory docs` and open http://localhost:8765.
- [`docs/assets/catalogue.js`](docs/assets/catalogue.js) holds the shared loading and search code.
- The label maker uses [jsPDF](https://github.com/parallax/jsPDF) and [qrcode-generator](https://github.com/kazuhikoarase/qrcode-generator) and [JsBarcode](https://github.com/lindell/JsBarcode) from cdnjs.
- [`docs/sw.js`](docs/sw.js) is the service worker for offline use. Bump its `CACHE` name when you change which files it pre-caches.
- The look is "label tape": bench paper (`#F4F2EC`), ink (`#111111`) and one signal orange (`#E8590C`), with headings in [Archivo](https://fonts.google.com/specimen/Archivo) at weight 900 and codes in [JetBrains Mono](https://fonts.google.com/specimen/JetBrains+Mono), both from Google Fonts.
- The mark is a screen with its protector peeling back at the corner. `docs/favicon.svg` is the site icon, and `python build2/make_icons.py` (needs Pillow) redraws the PNG and ICO versions from the same shape. The README logo is `docs/media/logo-light.png` and `logo-dark.png`.

## Dividers

[`dividers/protector_divider.scad`](dividers/protector_divider.scad) is the parametric divider. Set `pack_long` and `pack_short` to your pack size.

[`dividers/make_stl.py`](dividers/make_stl.py) builds the same shapes with `manifold3d`, `trimesh` and `numpy`. The published STLs are copied into `docs/dividers/`.

## Data sources

- **Device catalogue:** [gsmarena-catalog-builder](https://github.com/adelindanaila05/gsmarena-catalog-builder), full catalogue snapshot of July 2026. Product names and source-site data remain the property of their owners.
- **Hand-researched lists:** compiled from manufacturer announcements, retailer and protector-maker compatibility lists, and review sites. Release months for some watch, e-reader and retro brands are approximate; this is noted on those brands.
- **Model numbers:** the GSMArena catalogue, plus Apple's "Identify your iPhone / iPad / Apple Watch / iPod" support pages.
- **Sizes:** the GSMArena catalogue, plus maker spec pages (Apple Technical Specifications, Garmin, Amazfit, handheld makers) and spec sites for the rest; each hand-researched size in `build/sizes.json` records its source.

## Licence

Code is under the MIT License. The fit-group catalogue (groupings, codes, fit checks, notes, tags and changelog) is under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Device names, specs and model numbers from third-party sources remain their owners'. See [`LICENSE`](LICENSE).
