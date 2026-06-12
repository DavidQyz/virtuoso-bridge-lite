#!/usr/bin/env python3
"""
Generic schematic renderer: YAML (source of truth) -> SVG + PNG.
Reads a *.yaml describing devices/wires/ports and draws it. The YAML is
authoritative; this file is only the view layer. Edit the YAML, re-run.

Usage: .venv/Scripts/python.exe ota5t/tools/render_schematic.py <spec.yaml>
       SVG/PNG land next to the YAML (each device folder owns its figures).
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
DEV_COLOR = {"pmos": RED, "nmos": BLUE}
SYM_DIR = Path(__file__).resolve().parent / "symbols"
_SYM_CACHE: dict[str, dict] = {}


def load_symbol(kind: str, vclass: str) -> dict:
    """Load a MOS symbol cell (tools/symbols/<kind>_<vclass>.yaml), cached."""
    key = f"{kind}_{vclass}"
    if key not in _SYM_CACHE:
        path = SYM_DIR / f"{key}.yaml"
        if not path.exists():
            raise SystemExit(f"symbol cell not found: {path}")
        _SYM_CACHE[key] = yaml.safe_load(path.read_text(encoding="utf-8"))
    return _SYM_CACHE[key]


if len(sys.argv) < 2:
    sys.exit("usage: render_schematic.py <spec.yaml>")
SPEC_PATH = Path(sys.argv[1]).resolve()
S = yaml.safe_load(SPEC_PATH.read_text(encoding="utf-8"))


def main():
    cv = S["canvas"]
    fig, ax = plt.subplots(figsize=cv.get("figsize", [12, 11]))
    ax.set_xlim(*cv["xlim"]); ax.set_ylim(*cv["ylim"])
    ax.axis("off"); ax.set_aspect("equal")

    def line(x1, y1, x2, y2, c=WIRE, w=1.3):
        ax.add_line(Line2D([x1, x2], [y1, y2], color=c, lw=w, solid_capstyle="round"))

    # ---- devices: instantiate MOS symbol cells from tools/symbols/ ----
    # Each device picks cell "<kind>_<vclass>" (vclass default 2v). The cell is
    # drawn in a gate-on-LEFT frame; gate:"right" mirrors it in x. Terminal
    # anchors (top/bot/gate/bulk) come from the cell so wiring stays valid.
    term: dict[str, dict] = {}
    for d in S["devices"]:
        cx, cy = d["x"], d["y"]
        kind = d["kind"]
        vclass = str(d.get("vclass", "2v")).lower()
        col = DEV_COLOR[kind]
        cell = load_symbol(kind, vclass)
        sx = -1 if d["gate"] == "right" else 1          # mirror to put gate on right
        cmap = {"d": col, "w": WIRE}
        a = cell["anchors"]
        # Place the cell so the D/S column lands exactly on the device's (x,y).
        # The channel sits to the side to make room for the offset stubs, but
        # top/bot anchors stay at cx so existing wiring needs no change.
        ds_off = a["top"][0]
        ox = cx - sx * ds_off

        for pr in cell["prims"]:
            t = pr[0]
            if t == "L":
                _, x1, y1, x2, y2, lw, ck = pr
                line(ox + sx * x1, cy + y1, ox + sx * x2, cy + y2, cmap[ck], lw)
            elif t == "C":
                _, x0, y0, r, ck = pr
                ax.add_patch(Circle((ox + sx * x0, cy + y0), r, fill=False,
                                    edgecolor=cmap[ck], lw=1.3, zorder=4))
            elif t == "R":   # hollow rectangle (5V gate plate). [R, x0,y0,w,h,lw,ck]
                _, x0, y0, rw, rh, lw, ck = pr
                wx = ox + (sx * x0 if sx > 0 else sx * (x0 + rw))
                ax.add_patch(Rectangle((wx, cy + y0), rw, rh, fill=False,
                                       edgecolor=cmap[ck], lw=lw, zorder=4))

        term[d["name"]] = {
            "top":  (ox + sx * a["top"][0],  cy + a["top"][1]),
            "bot":  (ox + sx * a["bot"][0],  cy + a["bot"][1]),
            "gate": (ox + sx * a["gate"][0], cy + a["gate"][1]),
            "bulk": (ox + sx * a["bulk"][0], cy + a["bulk"][1]),
        }
        lx = cx + 0.66 if d["label"] == "right" else cx - 0.66
        ax.text(lx, cy + 0.34, d["name"], fontsize=12.5, fontweight="bold",
                color=col, ha="left" if d["label"] == "right" else "right",
                va="center", zorder=7)

    # ---- ideal voltage sources (circle, +/- marks), e.g. floating V_AB ----
    for v in S.get("vsources", []):
        vx, vy, r = v["x"], v["y"], 0.22
        ax.add_patch(Circle((vx, vy), r, facecolor="white", edgecolor=WIRE,
                            lw=1.4, zorder=5))
        ax.text(vx, vy + 0.10, "+", fontsize=8, ha="center", va="center", zorder=6)
        ax.text(vx, vy - 0.10, "−", fontsize=8, ha="center", va="center", zorder=6)
        ax.text(vx + r + 0.08, vy, v.get("name", ""), fontsize=8.5, color="#555",
                ha="left", va="center", zorder=6)
        term[v["name"]] = {"plus": (vx, vy + r), "minus": (vx, vy - r)}

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
        k = p["kind"]
        if k == "bias":                       # bias node: small dot + label, no arrow
            ax.add_patch(Circle((x, y), 0.07, color="#b08000", zorder=7))
            tl = p.get("tside", "right") == "left"   # label side (default right)
            ax.text(x + (-0.15 if tl else 0.15), y, p["name"], fontsize=9.5,
                    color="#b08000", fontweight="bold",
                    ha="right" if tl else "left", va="center")
            continue
        out = k == "out"
        c = "#1a7f37" if out else "#8250df"
        ax.plot(x, y, marker=">" if out else "<", ms=13, color=c, zorder=7)
        ax.text(x + (0.2 if out else -0.2), y, p["name"], fontsize=11,
                fontweight="bold", color=c,
                ha="left" if out else "right", va="center")

    ax.text(sum(cv["xlim"]) / 2, cv.get("title_y", cv["ylim"][1] - 0.3),
            S["meta"]["title"], fontsize=15, fontweight="bold", ha="center")

    fig.tight_layout()
    stem = SPEC_PATH.stem
    out_dir = SPEC_PATH.parent
    fig.savefig(out_dir / f"{stem}.svg", bbox_inches="tight")
    fig.savefig(out_dir / f"{stem}.png", dpi=145, bbox_inches="tight")
    print(f"rendered {SPEC_PATH.name} -> {stem}.svg + {stem}.png")


if __name__ == "__main__":
    main()
