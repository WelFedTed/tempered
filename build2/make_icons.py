"""Draws the raster site icons in docs/ from the same shape as docs/favicon.svg.

Needs Pillow. Run: python build2/make_icons.py
"""
import os
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, 'docs')
BG, INK, ACC = '#e9e7e1', '#1b1a18', '#e8590c'


def icon(px, tile=True, pad=0.0):
    """Icon at px square. tile: rounded bench-grey background. pad: extra margin (fraction) for maskable icons."""
    s = 16  # supersample
    n = px * s
    im = Image.new('RGBA', (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if tile:
        d.rounded_rectangle([0, 0, n - 1, n - 1], radius=n * 0.22 if not pad else 0, fill=BG)
    # 32-unit artwork, scaled into the area left after padding
    area = n * (1 - 2 * pad)
    k = area / 32
    o = n * pad
    u = lambda v: o + v * k
    w = 3 * k
    d.rounded_rectangle([u(6), u(2), u(26), u(30)], radius=5 * k, fill=INK)
    d.rounded_rectangle([u(6) + w, u(2) + w, u(26) - w, u(30) - w], radius=2 * k, fill=BG if tile else (0, 0, 0, 0))
    r = 2.8 * k
    d.ellipse([u(16.5) - r, u(12.5) - r, u(16.5) + r, u(12.5) + r], fill=ACC)
    return im.resize((px, px), Image.LANCZOS)


icon(180).save(os.path.join(DOCS, 'apple-touch-icon.png'))
icon(192).save(os.path.join(DOCS, 'icon-192.png'))
icon(512).save(os.path.join(DOCS, 'icon-512.png'))
icon(512, pad=0.12).save(os.path.join(DOCS, 'icon-maskable-512.png'))
icon(48).save(os.path.join(DOCS, 'favicon.ico'), sizes=[(16, 16), (32, 32), (48, 48)])
print('icons written to', DOCS)
