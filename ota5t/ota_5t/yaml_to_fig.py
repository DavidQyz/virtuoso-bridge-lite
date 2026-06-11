#!/usr/bin/env python3
"""
Render circuit.yaml -> circuit.svg (import into Figma) + circuit.png (preview).
The YAML is the single source of truth; this is just its view layer.
Run: .venv/Scripts/python.exe ota5t/ota_5t/yaml_to_fig.py
"""
from __future__ import annotations
from pathlib import Path

import yaml
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon

HERE = Path(__file__).resolve().parent
SPEC = yaml.safe_load((HERE / "circuit.yaml").read_text(encoding="utf-8"))

PCOL = {"nmos": "#2c6fbf", "pmos": "#c0392b"}


def line(ax, x1, y1, x2, y2, **kw):
    ax.add_line(Line2D([x1, x2], [y1, y2], solid_capstyle="round", **kw))


def pin_label(ax, x, y, net, faint, ha="center", va="center", dx=0.0, dy=0.0):
    sig = net not in faint
    ax.text(x + dx, y + dy, net, fontsize=7.3, ha=ha, va=va,
            color=("#111" if sig else "#9aa0a6"),
            fontweight=("bold" if sig else "normal"),
            zorder=5)


def draw_mos(ax, d, faint):
    cx, cy = d["x"], d["y"]
    col = PCOL[d["kind"]]
    h = 0.33
    # gate bar + channel bar
    line(ax, cx - 0.17, cy - h, cx - 0.17, cy + h, color="#222", lw=1.8)
    line(ax, cx, cy - h, cx, cy + h, color=col, lw=3.0)
    # leads: gate(left), drain(top), source(bottom), bulk(right)
    line(ax, cx - 0.17, cy, cx - 0.62, cy, color="#222", lw=1.2)      # G
    line(ax, cx, cy + h, cx, cy + 0.62, color="#222", lw=1.2)         # D
    line(ax, cx, cy - h, cx, cy - 0.62, color="#222", lw=1.2)         # S
    line(ax, cx, cy, cx + 0.5, cy, color="#222", lw=1.2)             # B
    # type arrow on source lead
    ya = cy - 0.20
    if d["kind"] == "nmos":   # arrow points up into channel
        tri = [(cx, ya), (cx - 0.09, ya - 0.12), (cx + 0.09, ya - 0.12)]
    else:                      # pmos: arrow points down
        tri = [(cx, ya - 0.12), (cx - 0.09, ya), (cx + 0.09, ya)]
    ax.add_patch(Polygon(tri, closed=True, color=col, zorder=4))
    # device label
    ax.text(cx - 0.66, cy + 0.42, d["name"], fontsize=8.5, ha="right",
            va="bottom", color=col, fontweight="bold", zorder=5)
    ax.text(cx - 0.66, cy + 0.30, d["size"], fontsize=6.2, ha="right",
            va="top", color="#666", zorder=5)
    # pin net labels
    p = d["pins"]
    pin_label(ax, cx, cy + 0.66, p["d"], faint, va="bottom")
    pin_label(ax, cx, cy - 0.66, p["s"], faint, va="top")
    pin_label(ax, cx - 0.66, cy, p["g"], faint, ha="right")
    pin_label(ax, cx + 0.54, cy, p["b"], faint, ha="left")


def main():
    faint = set(SPEC.get("faint_nets", []))
    fig, ax = plt.subplots(figsize=(11.5, 10))
    ax.set_xlim(0, 10.4); ax.set_ylim(0, 10.2); ax.axis("off")
    ax.set_aspect("equal")

    # power rails
    for r in SPEC.get("rails", []):
        y = r["y"]
        line(ax, 1.0, y, 9.4, y, color="#444", lw=2.2)
        ax.text(9.5, y, r.get("label", r["net"]), fontsize=9, va="center",
                ha="left", color="#444", fontweight="bold")

    for d in SPEC["devices"]:
        draw_mos(ax, d, faint)

    # ports
    for pt in SPEC.get("ports", []):
        c = "#1a7f37" if pt["dir"] == "out" else "#8250df"
        ax.plot(pt["x"], pt["y"], marker=">" if pt["dir"] == "out" else "<",
                ms=11, color=c, zorder=6)
        ax.text(pt["x"] + (0.18 if pt["dir"] == "out" else -0.18), pt["y"],
                pt["net"], fontsize=9, fontweight="bold", color=c,
                ha="left" if pt["dir"] == "out" else "right", va="center")

    # titles
    ax.text(5.2, 10.0, SPEC["title"], fontsize=14, ha="center",
            va="top", fontweight="bold")
    ax.text(5.2, 9.62, SPEC.get("subtitle", ""), fontsize=9.5, ha="center",
            va="top", color="#333")
    # legend box
    leg = SPEC.get("legend", [])
    for i, t in enumerate(leg):
        ax.text(0.2, 0.45 - i*0.28, "• " + t, fontsize=8, ha="left",
                va="top", color="#444")
    # device-type key
    ax.add_patch(Polygon([(7.6, 0.5), (7.75, 0.5), (7.75, 0.62), (7.6, 0.62)],
                         color=PCOL["pmos"]))
    ax.text(7.8, 0.56, "PMOS", fontsize=8, va="center")
    ax.add_patch(Polygon([(8.7, 0.5), (8.85, 0.5), (8.85, 0.62), (8.7, 0.62)],
                         color=PCOL["nmos"]))
    ax.text(8.9, 0.56, "NMOS", fontsize=8, va="center")

    fig.tight_layout()
    fig.savefig(HERE / "circuit.svg", bbox_inches="tight")
    fig.savefig(HERE / "circuit.png", dpi=140, bbox_inches="tight")
    print("saved circuit.svg (Figma import) + circuit.png (preview)")


if __name__ == "__main__":
    main()
