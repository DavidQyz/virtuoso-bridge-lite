#!/usr/bin/env python3
"""
Folded-cascode PMOS-input OTA — proper schematic (wires, like Virtuoso).
Only device names (M0..M10) are labelled. No sizes. Internal nodes are plain
wires + junction dots; only rails / I-O / ideal-bias pins carry net labels.
Outputs fc_schematic.svg (import into Figma) + fc_schematic.png (preview).
Run: .venv/Scripts/python.exe ota5t/fc_schematic.py
"""
from __future__ import annotations
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon, Circle

HERE = Path(__file__).resolve().parent
RED, BLUE, WIRE = "#c0392b", "#2c6fbf", "#222"
fig, ax = plt.subplots(figsize=(12.2, 11))
ax.set_xlim(0, 12); ax.set_ylim(0, 11); ax.axis("off"); ax.set_aspect("equal")


def L(x1, y1, x2, y2, c=WIRE, w=1.3):
    ax.add_line(Line2D([x1, x2], [y1, y2], color=c, lw=w, solid_capstyle="round"))


def wire(pts, c=WIRE, w=1.3):
    for i in range(len(pts) - 1):
        L(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], c, w)


def dot(x, y):
    ax.add_patch(Circle((x, y), 0.05, color=WIRE, zorder=6))


def mos(cx, cy, kind, name, gate="left", lbl_side="right"):
    """Draw MOS. PMOS source=top, NMOS source=bottom. Returns terminals."""
    s, col = 0.30, (RED if kind == "pmos" else BLUE)
    L(cx, cy - s, cx, cy + s, col, 2.6)                      # channel bar
    gx = cx - 0.15 if gate == "left" else cx + 0.15
    gt = cx - 0.55 if gate == "left" else cx + 0.55
    L(gx, cy - s, gx, cy + s, WIRE, 1.7)                     # gate bar
    L(gx, cy, gt, cy, WIRE, 1.2)                             # gate lead
    L(cx, cy + s, cx, cy + 0.55, WIRE, 1.2)                  # top lead
    L(cx, cy - s, cx, cy - 0.55, WIRE, 1.2)                  # bottom lead
    # type arrow on the SOURCE lead (pmos: top, nmos: bottom)
    if kind == "pmos":
        ax.add_patch(Polygon([(cx, cy + s), (cx - 0.1, cy + s + 0.14),
                              (cx + 0.1, cy + s + 0.14)], color=col, zorder=4))
    else:
        ax.add_patch(Polygon([(cx, cy - s), (cx - 0.1, cy - s - 0.14),
                              (cx + 0.1, cy - s - 0.14)], color=col, zorder=4))
    lx = cx + 0.62 if lbl_side == "right" else cx - 0.62
    ax.text(lx, cy + 0.34, name, fontsize=12, fontweight="bold", color=col,
            ha="left" if lbl_side == "right" else "right", va="center", zorder=7)
    return {"top": (cx, cy + 0.55), "bot": (cx, cy - 0.55), "gate": (gt, cy)}


def bias(term, name, side):
    x, y = term
    ex = x - 0.45 if side == "left" else x + 0.45
    L(x, y, ex, y, WIRE, 1.2)
    ax.text(ex + (-0.08 if side == "left" else 0.08), y, name, fontsize=8.5,
            color="#777", ha="right" if side == "left" else "left", va="center")


def port(x, y, name, kind):
    c = "#1a7f37" if kind == "out" else "#8250df"
    m = ">" if kind == "out" else "<"
    ax.plot(x, y, marker=m, ms=13, color=c, zorder=7)
    ax.text(x + (0.2 if kind == "out" else -0.2), y, name, fontsize=11,
            fontweight="bold", color=c, ha="left" if kind == "out" else "right",
            va="center")


VDD_Y, VSS_Y = 10.3, 0.8
# ---- devices ----
M0  = mos(6.0, 9.0, "pmos", "M0", gate="left",  lbl_side="right")
M9  = mos(2.6, 9.0, "pmos", "M9", gate="left",  lbl_side="right")
M10 = mos(9.4, 9.0, "pmos", "M10", gate="right", lbl_side="left")
M7  = mos(2.6, 7.5, "pmos", "M7", gate="left",  lbl_side="right")
M8  = mos(9.4, 7.5, "pmos", "M8", gate="right", lbl_side="left")
M1  = mos(4.8, 7.5, "pmos", "M1", gate="left",  lbl_side="right")
M2  = mos(7.2, 7.5, "pmos", "M2", gate="right", lbl_side="left")
M5  = mos(2.6, 5.0, "nmos", "M5", gate="left",  lbl_side="right")
M6  = mos(9.4, 5.0, "nmos", "M6", gate="right", lbl_side="left")
M3  = mos(2.6, 3.0, "nmos", "M3", gate="left",  lbl_side="right")
M4  = mos(9.4, 3.0, "nmos", "M4", gate="right", lbl_side="left")

# ---- rails ----
L(1.0, VDD_Y, 11.0, VDD_Y, "#444", 2.4)
L(1.0, VSS_Y, 11.0, VSS_Y, "#444", 2.4)
ax.text(11.1, VDD_Y, "VDD", fontsize=11, fontweight="bold", color="#444", va="center")
ax.text(11.1, VSS_Y, "VSS", fontsize=11, fontweight="bold", color="#444", va="center")
for t in (M0["top"], M9["top"], M10["top"]):
    L(t[0], t[1], t[0], VDD_Y)
for t in (M3["bot"], M4["bot"]):
    L(t[0], t[1], t[0], VSS_Y)

# ---- nets (wires + dots) ----
# ntail: M0.bot - M1.top - M2.top
wire([(6.0, 8.45), (6.0, 8.2)]); wire([(4.8, 8.2), (7.2, 8.2)])
wire([(4.8, 8.05), (4.8, 8.2)]); wire([(7.2, 8.05), (7.2, 8.2)])
for d in [(4.8, 8.2), (6.0, 8.2), (7.2, 8.2)]: dot(*d)
# left stack internals
wire([(2.6, 8.45), (2.6, 8.05)])          # nA3 (M9.bot-M7.top)
wire([(2.6, 6.95), (2.6, 5.55)])          # nA2 (M7.bot-M5.top)
wire([(2.6, 4.45), (2.6, 3.55)])          # nA  (M5.bot-M3.top)
# right stack internals
wire([(9.4, 8.45), (9.4, 8.05)])          # nB3
wire([(9.4, 6.95), (9.4, 5.55)])          # OUT (M8.bot-M6.top)
wire([(9.4, 4.45), (9.4, 3.55)])          # nB
# input drains fold to the stacks
wire([(4.8, 6.95), (4.8, 4.0), (2.6, 4.0)]); dot(2.6, 4.0)   # M1.d -> nA
wire([(7.2, 6.95), (7.2, 4.0), (9.4, 4.0)]); dot(9.4, 4.0)   # M2.d -> nB
# mirror-gate bus: nA2 -> M9.gate & M10.gate (top route; crossings = no-connect)
wire([(2.6, 6.2), (1.2, 6.2), (1.2, 9.7), (10.6, 9.7), (10.6, 9.0)])
wire([(10.6, 9.0), M10["gate"][0], M10["gate"][1]])
wire([(1.2, 9.0), M9["gate"][0], M9["gate"][1]])
dot(2.6, 6.2); dot(1.2, 9.0)
# output
wire([(9.4, 6.2), (10.7, 6.2)]); dot(9.4, 6.2); port(10.7, 6.2, "OUT", "out")

# ---- ideal-bias pins + I/O ports ----
bias(M0["gate"], "Vb_tail", "left")
bias(M7["gate"], "Vb_pc", "left");  bias(M8["gate"], "Vb_pc", "right")
bias(M5["gate"], "Vb_nc", "left");  bias(M6["gate"], "Vb_nc", "right")
bias(M3["gate"], "Vb_n",  "left");  bias(M4["gate"], "Vb_n",  "right")
port(M1["gate"][0] - 0.05, M1["gate"][1], "VIN+", "in")
port(M2["gate"][0] + 0.05, M2["gate"][1], "VIN-", "in")

ax.text(6.0, 10.85, "Folded-cascode PMOS-input OTA", fontsize=15,
        fontweight="bold", ha="center")
fig.tight_layout()
fig.savefig(HERE / "fc_schematic.svg", bbox_inches="tight")
fig.savefig(HERE / "fc_schematic.png", dpi=145, bbox_inches="tight")
print("saved fc_schematic.svg + fc_schematic.png")
