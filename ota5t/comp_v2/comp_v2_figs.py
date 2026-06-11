#!/usr/bin/env python3
"""Render COMP_V2 vs COMP_CG(V4) comparison figures from the two char JSONs.
Run: .venv/Scripts/python.exe ota5t/comp_v2/comp_v2_figs.py
"""
from __future__ import annotations
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
V2 = json.loads((HERE / "comp_v2_char.json").read_text(encoding="utf-8"))
V4 = json.loads((HERE.parent / "comp_cg" / "comp_char.json").read_text(encoding="utf-8"))

inn2 = [r["inn"] for r in V2["rows"]]
tp2  = [r["tprop"] * 1e9 for r in V2["rows"]]
pw2  = [r["p_tot"] * 1e6 for r in V2["rows"]]
inn4 = [r["inn"] for r in V4["rows"]]
tp4  = [r["tprop"] * 1e9 for r in V4["rows"]]
pw4  = [r["p_tot"] * 1e6 for r in V4["rows"]]

# original V4 (si-netlist ground truth), 3-way when available
orig_path = HERE.parent / "comp_cg" / "comp_orig_char.json"
ORIG = json.loads(orig_path.read_text(encoding="utf-8")) if orig_path.exists() else None
if ORIG:
    inn0 = [r["inn"] for r in ORIG["rows"]]
    tp0  = [r["tprop"] * 1e9 for r in ORIG["rows"]]
    pw0  = [r["p_tot"] * 1e6 for r in ORIG["rows"]]

# ---------- Figure 1: delay comparison ----------
fig, ax = plt.subplots(figsize=(7.2, 4.4))
if ORIG:
    ax.plot(inn0, tp0, "C2.-", lw=1.1, ms=3,
            label="V4 original (test/COMP_V4_ORIG, si netlist)")
ax.plot(inn4, tp4, "C7.-", lw=1.1, ms=3, label="V4 replica (COMP_CG)")
ax.plot(inn2, tp2, "C0.-", lw=1.4, ms=4, label="V2 (COMP_V2, dual-threshold)")
ax.axhline(1.0, color="C3", lw=.8, ls="--")
i1 = inn2.index(1.0)
ax.plot(1.0, tp2[i1], "C3o", ms=6)
lbl = f"  INN=1V: {tp2[i1]:.3f} ns  (V4: {tp4[inn4.index(1.0)]:.3f}"
if ORIG:
    lbl += f", orig: {tp0[inn0.index(1.0)]:.3f}"
ax.annotate(lbl + ")", (1.0, tp2[i1]), fontsize=8, color="C3", va="top")
ax.set_xlabel("INN reference voltage (V)")
ax.set_ylabel("propagation delay  tprop (ns)")
ax.set_title(f"Comparator tprop, 3 versions  (VCM={V2['vcm']:g} V, "
             "0-5 V half-wave 13.56 MHz)", fontsize=11)
ax.grid(True, alpha=.3)
ax.set_xlim(0, 5)
ax.legend(fontsize=9)
fig.tight_layout()
fig.savefig(HERE / "comp_v2_delay_vs_v4.png", dpi=130)
print("saved -> comp_v2_delay_vs_v4.png")

# ---------- Figure 2: power comparison ----------
fig2, ax2 = plt.subplots(figsize=(7.2, 4.4))
if ORIG:
    ax2.plot(inn0, pw0, "C2.-", lw=1.1, ms=3,
             label="V4 original (si netlist)")
ax2.plot(inn4, pw4, "C7.-", lw=1.1, ms=3, label="V4 replica (COMP_CG)")
ax2.plot(inn2, pw2, "C1.-", lw=1.4, ms=4, label="V2 (COMP_V2)")
ax2.set_xlabel("INN reference voltage (V)")
ax2.set_ylabel("average power over one period (uW)")
ax2.set_title("Comparator total power, 3 versions  (one 73.7 ns period)",
              fontsize=11)
ax2.grid(True, alpha=.3)
ax2.set_xlim(0, 5)
ax2.legend(fontsize=9)
fig2.tight_layout()
fig2.savefig(HERE / "comp_v2_power_vs_v4.png", dpi=130)
print("saved -> comp_v2_power_vs_v4.png")
