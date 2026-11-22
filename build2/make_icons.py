"""Draws the raster site icons in docs/ from the same mark as docs/favicon.svg.

The mark is a screen with its protector peeling back at the top-right corner.
Raster icons are an ink tile with the mark in bench paper and the fold in orange.

Needs Pillow. Run: python build2/make_icons.py
"""
import os
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, 'docs')
INK, PAPER, ACC = '#111111', '#f4f2ec', '#e8590c'

# Mark in a 40 x 52 unit box: body x 2..38, y 2..50, corner radius 7, fold cut from (25, 2) to (38, 15).
W, H = 40, 52


def icon(px, pad=0.2, radius=0.22):
    """Icon at px square: ink tile (radius as a fraction, 0 = full bleed) with the mark filling 1 - 2*pad of the height."""
    s = 16  # supersample
    n = px * s
    im = Image.new('RGBA', (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if radius:
        d.rounded_rectangle([0, 0, n - 1, n - 1], radius=n * radius, fill=INK)
    else:
        d.rectangle([0, 0, n - 1, n - 1], fill=INK)
    k = n * (1 - 2 * pad) / H
    ox, oy = (n - W * k) / 2, (n - H * k) / 2
    u = lambda x, y: (ox + x * k, oy + y * k)
    # Body, then cut the peeled corner back to the tile colour, then the fold.
    d.rounded_rectangle([*u(2, 2), *u(38, 50)], radius=7 * k, fill=PAPER)
    d.polygon([u(25, 2), u(38.6, 1.4), u(38.6, 15)], fill=INK)
    d.rectangle([*u(25, 1.4), *u(38.6, 2)], fill=INK)
    d.polygon([u(25, 2), u(38, 15), u(25, 15)], fill=ACC)
    return im.resize((px, px), Image.LANCZOS)


icon(180, radius=0).save(os.path.join(DOCS, 'apple-touch-icon.png'))
icon(192).save(os.path.join(DOCS, 'icon-192.png'))
icon(512).save(os.path.join(DOCS, 'icon-512.png'))
icon(512, pad=0.26, radius=0).save(os.path.join(DOCS, 'icon-maskable-512.png'))
icon(48, pad=0.12, radius=0.2).save(os.path.join(DOCS, 'favicon.ico'), sizes=[(16, 16), (32, 32), (48, 48)])
print('icons written to', DOCS)
