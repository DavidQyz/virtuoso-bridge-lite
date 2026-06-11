#!/usr/bin/env python3
"""
Generic schematic renderer: YAML (source of truth) -> SVG + PNG.
Reads a *.yaml describing devices/wires/ports and draws it. The YAML is
authoritative; this file is only the view layer. Edit the YAML, re-run.

Usage: .venv/Scripts/python.exe ota5t/render_schematic.py [spec.yaml]
       default spec = ota5t/fc_schematic.yaml
"""
from __future__ import annotations
import sys
from pathlib import Path
import yaml
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon, Circle, Rectangle

RED, BLUE, WIRE, RAIL = "#c0392b", "#2c6fbf", "#222", "#444"
HERE = Path(__file__).resolve().parent
SPEC_PATH = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "fc_schematic.yaml"
S = yaml.safe_load(SPEC_PATH.read_text(encoding="utf-8"))


def main():
    cv = S["canvas"]
    fig, ax = plt.subplots(figsize=cv.get("figsize", [12, 11]))
    ax.set_xlim(*cv["xlim"]); ax.set_ylim(*cv["ylim"])
    ax.axis("off"); ax.set_aspect("equal")

    def line(x1, y1, x2, y2, c=WIRE, w=1.3):
        ax.add_line(Line2D([x1, x2], [y1, y2], color=c, lw=w, solid_capstyle="round"))

    # ---- devices: draw symbols, collect terminal coords ----
    term: dict[str, dict] = {}
    for d in S["devices"]:
        cx, cy = d["x"], d["y"]
        col = RED if d["kind"] == "pmos" else BLUE
        s = 0.30
        line(cx, cy - s, cx, cy + s, col, 2.6)                      # channel
        gx = cx - 0.15 if d["gate"] == "left" else cx + 0.15
        gt = cx - 0.55 if d["gate"] == "left" else cx + 0.55
        line(gx, cy - s, gx, cy + s, WIRE, 1.7)                     # gate bar
        line(gx, cy, gt, cy, WIRE, 1.2)                             # gate lead
        line(cx, cy + s, cx, cy + 0.55, WIRE, 1.2)                  # top lead
        line(cx, cy - s, cx, cy - 0.55, WIRE, 1.2)                  # bottom lead
        # source arrow (pmos: top, nmos: bottom)
        if d["kind"] == "pmos":
            ax.add_patch(Polygon([(cx, cy + s), (cx - 0.1, cy + s + 0.14),
                                  (cx + 0.1, cy + s + 0.14)], color=col, zorder=4))
        else:
            ax.add_patch(Polygon([(cx, cy - s), (cx - 0.1, cy - s - 0.14),
                                  (cx + 0.1, cy - s - 0.14)], color=col, zorder=4))
        lx = cx + 0.62 if d["label"] == "right" else cx - 0.62
        ax.text(lx, cy + 0.34, d["name"], fontsize=12.5, fontweight="bold",
                color=col, ha="left" if d["label"] == "right" else "right",
                va="center", zorder=7)
        term[d["name"]] = {"top": (cx, cy + 0.55), "bot": (cx, cy - 0.55),
                           "gate": (gt, cy)}

    # ---- blocks (sub-cells drawn as labelled boxes; pins resolvable as Name.Pin) ----
    for b in S.get("blocks", []):
        bx, by, bw, bh = b["x"], b["y"], b["w"], b["h"]
        ax.add_patch(Rectangle((bx, by), bw, bh, facecolor="#eef0f7",
                               edgecolor="#444", lw=1.6, zorder=2))
        ax.text(bx + bw/2, by + bh/2, b.get("title", b["name"]), fontsize=9,
                ha="center", va="center", zorder=3, color="#333", fontweight="bold")
        td = {}
        for p in b.get("pins", []):
            side, frac, ext = p["side"], p.get("frac", 0.5), 0.45
            if side == "left":
                ax_, ay = bx, by + bh*frac; ex, ey = ax_-ext, ay
            elif side == "right":
                ax_, ay = bx+bw, by + bh*frac; ex, ey = ax_+ext, ay
            elif side == "top":
                ax_, ay = bx + bw*frac, by+bh; ex, ey = ax_, ay+ext
            else:
                ax_, ay = bx + bw*frac, by; ex, ey = ax_, ay-ext
            line(ax_, ay, ex, ey, WIRE, 1.2)
            td[p["name"]] = (ex, ey)
            lx = ax_ + (0.06 if side == "right" else -0.06 if side == "left" else 0)
            ax.text(lx, ay + (0.08 if side in ("top", "bottom") else 0.07), p["name"],
                    fontsize=6.5, color="#666",
                    ha="left" if side == "right" else "right" if side == "left" else "center",
                    va="bottom")
        term[b["name"]] = td

    def resolve(pt):
        if isinstance(pt, str):
            dev, t = pt.split(".")
            return term[dev][t]
        return tuple(pt)

    # ---- rails ----
    for r in S.get("rails", []):
        line(r["x0"], r["y"], r["x1"], r["y"], RAIL, 2.4)
        ax.text(r["x1"] + 0.1, r["y"], r["net"], fontsize=11, fontweight="bold",
                color=RAIL, va="center")
    rail_y = {r["net"]: r["y"] for r in S.get("rails", [])}
    for net, conns in S.get("rail_connections", {}).items():
        for c in conns:
            x, y = resolve(c)
            line(x, y, x, rail_y[net], WIRE, 1.3)

    # ---- wires ----
    for w in S.get("wires", []):
        pts = [resolve(p) for p in w["path"]]
        for i in range(len(pts) - 1):
            line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], WIRE, 1.3)

    # ---- junction dots ----
    for x, y in S.get("dots", []):
        ax.add_patch(Circle((x, y), 0.055, color=WIRE, zorder=6))

    # ---- ideal-bias pins ----
    for b in S.get("bias_pins", []):
        x, y = resolve(b["at"])
        ex = x - 0.45 if b["side"] == "left" else x + 0.45
        line(x, y, ex, y, WIRE, 1.2)
        ax.text(ex + (-0.08 if b["side"] == "left" else 0.08), y, b["name"],
                fontsize=8.5, color="#777",
                ha="right" if b["side"] == "left" else "left", va="center")

    # ---- I/O ports ----
    for p in S.get("ports", []):
        x, y = resolve(p["at"]) if "at" in p else tuple(p["xy"])
        out = p["kind"] == "out"
        c = "#1a7f37" if out else "#8250df"
        ax.plot(x, y, marker=">" if out else "<", ms=13, color=c, zorder=7)
        ax.text(x + (0.2 if out else -0.2), y, p["name"], fontsize=11,
                fontweight="bold", color=c,
                ha="left" if out else "right", va="center")

    ax.text(sum(cv["xlim"]) / 2, cv.get("title_y", cv["ylim"][1] - 0.3),
            S["meta"]["title"], fontsize=15, fontweight="bold", ha="center")

    fig.tight_layout()
    stem = SPEC_PATH.stem
    fig.savefig(HERE / f"{stem}.svg", bbox_inches="tight")
    fig.savefig(HERE / f"{stem}.png", dpi=145, bbox_inches="tight")
    print(f"rendered {SPEC_PATH.name} -> {stem}.svg + {stem}.png")


if __name__ == "__main__":
    main()
