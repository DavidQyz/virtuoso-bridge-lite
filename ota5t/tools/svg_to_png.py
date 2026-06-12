#!/usr/bin/env python3
"""Tiny SVG -> PNG rasterizer for the hand-authored MOS symbol SVGs.
Supports the primitives we use: <line>, <circle>, <polygon>, <rect>, <text>.
(Not a general SVG renderer -- just enough to proof our symbol art.)
Run: .venv/Scripts/python.exe ota5t/tools/svg_to_png.py <file.svg>
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, Polygon, Rectangle

svg = Path(sys.argv[1]).read_text(encoding="utf-8")
m = re.search(r'viewBox="([\d.\s]+)"', svg)
vb = [float(x) for x in m.group(1).split()]
W, H = vb[2], vb[3]

fig, ax = plt.subplots(figsize=(W / 80, H / 80))
ax.set_xlim(0, W); ax.set_ylim(H, 0)        # y down, like SVG
ax.axis("off"); ax.set_aspect("equal")


def fnum(tag, attr, default=None):
    mm = re.search(rf'{attr}="([-\d.]+)"', tag)
    return float(mm.group(1)) if mm else default


for tag in re.findall(r'<line[^>]*>', svg):
    sw = fnum(tag, "stroke-width", 2)
    ax.add_line(Line2D([fnum(tag, "x1"), fnum(tag, "x2")],
                       [fnum(tag, "y1"), fnum(tag, "y2")],
                       color="black", lw=sw, solid_capstyle="round"))

for tag in re.findall(r'<rect[^>]*/?>', svg):
    x, y, w, h = (fnum(tag, "x"), fnum(tag, "y"),
                  fnum(tag, "width"), fnum(tag, "height"))
    fill = re.search(r'fill="([^"]+)"', tag)
    if fill and fill.group(1) == "white":
        ax.add_patch(Rectangle((x, y), w, h, facecolor="white", edgecolor="none",
                               zorder=0))
    else:                                  # hollow (5V gate plate etc.)
        ax.add_patch(Rectangle((x, y), w, h, fill=False, edgecolor="black",
                               lw=fnum(tag, "stroke-width", 4)))

for tag in re.findall(r'<circle[^>]*>', svg):
    ax.add_patch(Circle((fnum(tag, "cx"), fnum(tag, "cy")), fnum(tag, "r"),
                        fill=False, edgecolor="black", lw=fnum(tag, "stroke-width", 4)))

for tag in re.findall(r'<polygon[^>]*>', svg):
    pts = re.search(r'points="([-\d.,\s]+)"', tag).group(1).split()
    xy = [tuple(map(float, p.split(","))) for p in pts]
    ax.add_patch(Polygon(xy, closed=True, color="black"))

for tag in re.findall(r'<text[^>]*>.*?</text>', svg):
    x, y = fnum(tag, "x"), fnum(tag, "y")
    txt = re.search(r'>([^<]*)<', tag).group(1)
    fs = fnum(tag, "font-size", 20)
    ax.text(x, y, txt, fontsize=fs * 0.8, fontweight="bold", va="baseline")

out = Path(sys.argv[1]).with_suffix(".png")
fig.savefig(out, dpi=130, bbox_inches="tight")
print(f"rasterized -> {out}")
