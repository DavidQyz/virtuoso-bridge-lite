#!/usr/bin/env python3
"""Render OTA characterization figures (PNG) from char_data.json via matplotlib.
Run: .venv/Scripts/python.exe ota5t/ota_5t/make_figs.py
"""
from __future__ import annotations
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
D = json.loads((HERE / "char_data.json").read_text(encoding="utf-8"))
f = D["freq"]; m = D["metrics"]; dt = D["devtab"]
ugf = m["ugf"]

# ---------- Figure 1: Bode ----------
fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.2, 6.4), sharex=True)
a1.semilogx(f, D["mag_db"], "C0")
a1.axhline(0, color="grey", lw=.6, ls=":")
a1.axvline(ugf, color="C3", lw=.8, ls="--")
a1.set_ylabel("|Adm|  (dB)")
a1.set_title(f"5T OTA open-loop differential gain   "
             f"(A0={m['dc_gain']:.1f} dB,  GBW={ugf/1e6:.1f} MHz,  PM={m['pm']:.0f}°)")
a1.grid(True, which="both", alpha=.3)
a1.annotate(f"GBW {ugf/1e6:.1f} MHz", (ugf, 4), color="C3", fontsize=8)
a2.semilogx(f, D["phase_deg"], "C1")
a2.axhline(-90, color="grey", lw=.6, ls=":")
a2.axvline(ugf, color="C3", lw=.8, ls="--")
a2.set_ylabel("phase (deg)"); a2.set_xlabel("frequency (Hz)")
a2.grid(True, which="both", alpha=.3)
fig.tight_layout(); fig.savefig(HERE / "ota5t_bode.png", dpi=130)

# ---------- Figure 2: PSRR + CMRR ----------
fig2, ax = plt.subplots(figsize=(7.2, 4.2))
ax.semilogx(f, D["psrr_db"], "C2", label=f"PSRR  (DC {m['psrr_dc']:.0f} dB)")
ax.semilogx(f, D["cmrr_db"], "C4", label=f"CMRR  (DC {m['cmrr_dc']:.0f} dB)")
ax.set_xlabel("frequency (Hz)"); ax.set_ylabel("rejection (dB)")
ax.set_title("5T OTA  PSRR(+) and CMRR vs frequency")
ax.grid(True, which="both", alpha=.3); ax.legend()
fig2.tight_layout(); fig2.savefig(HERE / "ota5t_psrr_cmrr.png", dpi=130)

# ---------- Figure 3: dashboard ----------
fig3, axs = plt.subplots(2, 2, figsize=(11.5, 7.6))
axs[0, 0].semilogx(f, D["mag_db"], "C0"); axs[0, 0].axhline(0, color="grey", ls=":", lw=.6)
axs[0, 0].axvline(ugf, color="C3", ls="--", lw=.8)
axs[0, 0].set_title(f"Differential gain  A0={m['dc_gain']:.1f} dB"); axs[0, 0].set_ylabel("dB")
axs[0, 0].grid(True, which="both", alpha=.3)
axs[1, 0].semilogx(f, D["phase_deg"], "C1"); axs[1, 0].axhline(-90, color="grey", ls=":", lw=.6)
axs[1, 0].axvline(ugf, color="C3", ls="--", lw=.8)
axs[1, 0].set_title(f"Phase  (PM={m['pm']:.0f}° @ {ugf/1e6:.1f} MHz)")
axs[1, 0].set_ylabel("deg"); axs[1, 0].set_xlabel("Hz"); axs[1, 0].grid(True, which="both", alpha=.3)
axs[0, 1].semilogx(f, D["psrr_db"], "C2", label="PSRR"); axs[0, 1].semilogx(f, D["cmrr_db"], "C4", label="CMRR")
axs[0, 1].set_title(f"PSRR (DC {m['psrr_dc']:.0f} dB) / CMRR (DC {m['cmrr_dc']:.0f} dB)")
axs[0, 1].set_ylabel("dB"); axs[0, 1].set_xlabel("Hz"); axs[0, 1].legend(); axs[0, 1].grid(True, which="both", alpha=.3)

axs[1, 1].axis("off")
rows = [f"{'dev':<4}{'ID/uA':>7}{'gm/uS':>7}{'gm/ID':>7}{'gm/gds':>7}{'reg':>5}"]
for nm in ("M1", "M2", "M3", "M4", "M5"):
    x = dt.get(nm)
    if x:
        rows.append(f"{nm:<4}{x['id']*1e6:7.1f}{x['gm']*1e6:7.1f}"
                    f"{x['gm_id']:7.1f}{x['av0']:7.0f}{'sat' if x['sat'] else 'LIN':>5}")
txt = ("FINAL SIZING  (tsmc18 1.8V, ideal bias)\n"
       "  M1,M2 input : W=3u  L=1u\n"
       "  M3,M4 load  : W=6u  L=1u\n"
       "  M5 tail     : W=5u  L=1u\n"
       f"  Vcm={D['sizing']['vcm']}V  Vbias={D['sizing']['vb']}V  CL={D['sizing']['cl']}pF\n"
       f"  Itail={m['itail']*1e6:.1f}uA  Power={m['power']*1e6:.1f}uW\n\n" + "\n".join(rows))
axs[1, 1].text(0.0, 0.98, txt, va="top", family="monospace", fontsize=10)
fig3.suptitle("5T OTA — design summary (Spectre, tsmc18 1.8V BCD, ideal voltage-source bias)",
              fontsize=12)
fig3.tight_layout(); fig3.savefig(HERE / "ota5t_summary.png", dpi=130)
print("saved ota5t_bode.png, ota5t_psrr_cmrr.png, ota5t_summary.png")
