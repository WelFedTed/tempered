"""Builds the same divider as protector_divider.scad with manifold3d and writes STLs."""
import sys
import numpy as np
import trimesh
from manifold3d import CrossSection, Manifold, JoinType

P = dict(pack_long=180, pack_short=95, clearance=4, label_w=50, label_h=25,
         pocket_depth=0.6, tab_show=30, thickness=2, foot_depth=12, window=True, divider_width=0)
TABLET = dict(P, pack_long=280, pack_short=200, divider_width=200, foot_depth=18)


def rr(w, h, r, x=0, y=0):
    return CrossSection.square([w - 2 * r, h - 2 * r]).offset(r, JoinType.Round).translate([x + r, y + r])


def divider(tab_pos, p=P):
    W = p["divider_width"] or p["pack_long"] + p["clearance"]
    body_h = p["pack_short"] - 10
    top = p["pack_short"] + p["tab_show"]
    tab_w = p["label_w"] + 6
    tab_x = {"left": 6, "right": W - 6 - tab_w, "centre": (W - tab_w) / 2}[tab_pos]
    tab_y0 = body_h - 12
    outline = rr(W, body_h, 3) + rr(tab_w, top - tab_y0, 3, tab_x, tab_y0)
    if p["window"]:
        outline = outline - rr(W - 24, body_h - 26, 6, 12, 12)
    t = p["thickness"]
    plate = outline.extrude(t)
    foot = Manifold.cube([W, 2, p["foot_depth"]]).translate([0, 0, t])
    pocket = Manifold.cube([p["label_w"] + 1, p["label_h"] + 1, p["pocket_depth"] + 0.01]).translate(
        [tab_x + (tab_w - p["label_w"] - 1) / 2, top - 2.5 - (p["label_h"] + 1), -0.01])
    return (plate + foot) - pocket


def to_trimesh(m):
    mesh = m.to_mesh()
    return trimesh.Trimesh(vertices=np.array(mesh.vert_properties)[:, :3], faces=np.array(mesh.tri_verts))


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    for name, params in (("divider", P), ("tablet_divider", TABLET)):
      for pos in ("left", "centre", "right"):
        tm = to_trimesh(divider(pos, params))
        path = f"{out}/{name}_tab_{pos}.stl"
        tm.export(path)
        print(name, pos, "watertight", tm.is_watertight, "bounds", tm.bounds.round(2).tolist(),
              "volume cm3", round(tm.volume / 1000, 1))
