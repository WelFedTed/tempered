// Screen protector drawer divider with a label pocket on a staggered tab.
// Packs stand on their long edge, face towards you, filed behind each divider.
// Measure one pack and set pack_long / pack_short, then render one STL per tab position.
// Tablet packs: e.g. pack_long = 280, pack_short = 200, divider_width = 200, foot_depth = 18.
// A divider narrower than the pack still separates groups: the packs lean on it.
// Print flat, front (label) face down. No supports needed. PLA or PETG, 0.2 mm layers.

/* [Your packs] */
pack_long  = 180;   // pack's long side, lies across the drawer (mm)
pack_short = 95;    // pack height when standing on its long edge (mm)
clearance  = 4;     // extra width so the divider slides in easily (mm)
divider_width = 0;  // 0 = pack_long + clearance. Set narrower for tablet packs (e.g. 200) so it fits the print bed

/* [Label] */
label_w      = 50;  // label width (mm): 50 x 25 thermal label by default
label_h      = 25;  // label height (mm)
pocket_depth = 0.6; // recess the label sits in (mm)
tab_show     = 30;  // how far the tab rises above the tops of the packs (mm)
tab_pos      = "left"; // [left, centre, right] print a mix so tabs don't hide each other

/* [Body] */
thickness  = 2;     // plate thickness (mm)
foot_depth = 12;    // foot behind the divider that stops it tipping (mm)
window     = true;  // cut-out to save filament

W      = divider_width > 0 ? divider_width : pack_long + clearance;
body_h = pack_short - 10;
top    = pack_short + tab_show;
tab_w  = label_w + 6;
tab_x  = tab_pos == "left" ? 6 : tab_pos == "right" ? W - 6 - tab_w : (W - tab_w) / 2;
tab_y0 = body_h - 12;

module rr(w, h, r) { translate([r, r]) offset(r = r) square([w - 2 * r, h - 2 * r]); }

module outline() {
  union() {
    rr(W, body_h, 3);
    translate([tab_x, tab_y0]) rr(tab_w, top - tab_y0, 3);
  }
}

difference() {
  union() {
    linear_extrude(thickness) difference() {
      outline();
      if (window) translate([12, 12]) rr(W - 24, body_h - 26, 6);
    }
    // foot on the back face, along the bottom edge
    translate([0, 0, thickness]) cube([W, 2, foot_depth]);
  }
  // label pocket on the front face (the face on the print bed)
  translate([tab_x + (tab_w - label_w - 1) / 2, top - 2.5 - (label_h + 1), -0.01])
    cube([label_w + 1, label_h + 1, pocket_depth + 0.01]);
}
