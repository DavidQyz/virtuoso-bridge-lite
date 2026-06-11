#!/usr/bin/env python3
"""Render COMP_CG characterization figures from comp_char.json.
Run: .venv/Scripts/python.exe ota5t/comp_cg/comp_figs.py
"""
from __future__ import annotations
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
D = json.loads((HERE / "comp_char.json").read_text(encoding="utf-8"))
rows = D["rows"]
inn   = [r["inn"] for r in rows]
tp_ns = [r["tprop"] * 1e9 for r in rows]
p_vdd = [r["p_vdd"] * 1e6 for r in rows]
p_inp = [r["p_inp"] * 1e6 for r in rows]
p_inn = [r["p_inn"] * 1e6 for r in rows]
p_tot = [r["p_tot"] * 1e6 for r in rows]

# ---------- Figure 1: INN vs propagation delay ----------
fig, ax = plt.subplots(figsize=(7.2, 4.4))
ax.plot(inn, tp_ns, "C0.-", lw=1.2, ms=4)
ax.axhline(1.0, color="C3", lw=.8, ls="--")
i1 = inn.index(1.0)
ax.plot(1.0, tp_ns[i1], "C3o", ms=6)
ax.annotate(f"  INN=1V: {tp_ns[i1]:.3f} ns (soft target 1 ns)",
            (1.0, tp_ns[i1]), fontsize=8, color="C3", va="bottom")
imin = tp_ns.index(min(tp_ns))
ax.annotate(f"min {tp_ns[imin]:.3f} ns @ {inn[imin]:.1f} V",
            (inn[imin], tp_ns[imin]), fontsize=8, va="top", ha="center",
            xytext=(inn[imin], tp_ns[imin] - 0.12), color="C0")
ax.set_xlabel("INN reference voltage (V)")
ax.set_ylabel("propagation delay  tprop (ns)")
ax.set_title(f"COMP_CG  tprop vs INN   (VCM={D['vcm']:g} V, "
             "0-5 V half-wave 13.56 MHz)", fontsize=11)
ax.grid(True, alpha=.3)
ax.set_xlim(0, 5)
fig.tight_layout()
fig.savefig(HERE / "comp_inn_delay.png", dpi=130)
print("saved -> comp_inn_delay.png")

# ---------- Figure 2: INN vs average power (one half-wave period) ----------
fig2, ax2 = plt.subplots(figsize=(7.2, 4.4))
ax2.plot(inn, p_tot, "k.-",  lw=1.4, ms=4, label="P_total")
ax2.plot(inn, p_inn, "C1.-", lw=1.1, ms=3, label="P_INN  (ref input, M1 diode branch)")
ax2.plot(inn, p_inp, "C2.-", lw=1.1, ms=3, label="P_INP  (signal input, M0 branch + DBB)")
ax2.plot(inn, p_vdd, "C0.-", lw=1.1, ms=3, label="P_VDD (1.8 V rail, INV1+INV2)")
ax2.set_xlabel("INN reference voltage (V)")
ax2.set_ylabel("average power over one period (uW)")
ax2.set_title("COMP_CG  power per source vs INN   "
              "(one 73.7 ns half-wave period)", fontsize=11)
ax2.grid(True, alpha=.3)
ax2.set_xlim(0, 5)
ax2.legend(fontsize=8, loc="upper left")
fig2.tight_layout()
fig2.savefig(HERE / "comp_inn_power.png", dpi=130)
print("saved -> comp_inn_power.png")
