#!/usr/bin/env python3
"""Render OTA_V2 vs FC-baseline Bode comparison from the two char JSONs.
Run: .venv/Scripts/python.exe ota5t/ota_v2/ota_v2_figs.py
"""
from __future__ import annotations
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
V2 = json.loads((HERE / "ota_v2_char.json").read_text(encoding="utf-8"))
FC = json.loads((HERE / "fc_baseline.json").read_text(encoding="utf-8"))
m2, mf = V2["metrics"], FC["metrics"]

fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.6, 6.8), sharex=True)
a1.semilogx(FC["freq"], FC["mag_db"], "C7", lw=1.2,
            label=f"FC baseline  (A0={mf['a0']:.1f}dB, GBW={mf['ugf']/1e6:.1f}MHz, "
                  f"PM={mf['pm']:.0f}°, {mf['power']*1e6:.1f}µW)")
a1.semilogx(V2["freq"], V2["mag_db"], "C0", lw=1.6,
            label=f"OTA_V2 (RFC)  (A0={m2['a0']:.1f}dB, GBW={m2['ugf']/1e6:.1f}MHz, "
                  f"PM={m2['pm']:.0f}°, {m2['power']*1e6:.1f}µW)")
a1.axhline(0, color="grey", lw=.6, ls=":")
for ugf, c in ((mf["ugf"], "C7"), (m2["ugf"], "C0")):
    a1.axvline(ugf, color=c, lw=.7, ls="--")
a1.set_ylabel("|A| (dB)")
a1.set_title(f"OTA_V2 (RFC) vs FC — GBW ×{m2['ugf']/mf['ugf']:.1f} @ "
             f"{m2['power']/mf['power']:.2f}× power", fontsize=11)
a1.grid(True, which="both", alpha=.3)
a1.legend(fontsize=8.5, loc="lower left")

a2.semilogx(FC["freq"], FC["phase_deg"], "C7", lw=1.2)
a2.semilogx(V2["freq"], V2["phase_deg"], "C0", lw=1.6)
a2.axhline(-120, color="C3", lw=.6, ls=":", label="PM=60° reference (-120°)")
for ugf, c in ((mf["ugf"], "C7"), (m2["ugf"], "C0")):
    a2.axvline(ugf, color=c, lw=.7, ls="--")
a2.set_ylabel("phase (deg)")
a2.set_xlabel("frequency (Hz)")
a2.grid(True, which="both", alpha=.3)
a2.legend(fontsize=8.5)

fig.tight_layout()
fig.savefig(HERE / "ota_v2_bode_vs_fc.png", dpi=130)
print("saved -> ota_v2_bode_vs_fc.png")
