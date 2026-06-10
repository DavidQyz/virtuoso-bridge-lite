#!/usr/bin/env python3
"""
Characterize the folded-cascode PMOS-input OTA: Bode / PSRR / CMRR + op table.
Reuses fc_ota.netlist (diff/vdd/cm stims). Renders PNGs via matplotlib.
Run: .venv/Scripts/python.exe ota5t/fc_characterize.py
"""
from __future__ import annotations
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from virtuoso_bridge.spectre.runner import SpectreSimulator
from fc_ota import netlist, P
from run_ota import parse_info

HERE = Path(__file__).resolve().parent


def run(stim):
    scs = HERE / f"fcc_{stim}.scs"
    scs.write_text(netlist(P, stim), encoding="utf-8")
    sim = SpectreSimulator.from_env(work_dir=str(HERE / "fcc" / stim))
    res = sim.run_simulation(scs, {})
    d = res.data or {}
    f = [float(x.real) if isinstance(x, complex) else float(x) for x in d.get("ac_freq", [])]
    out = list(d.get("ac_out", []))
    if not f or not out:
        raise RuntimeError(f"{stim}: no AC data {res.errors[:2]}")
    return f, out


def db(z):    return 20*math.log10(abs(z)) if abs(z) > 0 else -400.0
def ph(z):    return math.degrees(math.atan2(z.imag, z.real))


def main():
    f, adm = run("diff")
    _, add = run("vdd")
    _, acm = run("cm")
    mag = [db(v) for v in adm]
    pha = [ph(v) for v in adm]
    psrr = [db(adm[i]) - db(add[i]) for i in range(len(f))]
    cmrr = [db(adm[i]) - db(acm[i]) for i in range(len(f))]
    # matched sim -> CM gain hits numerical floor -> CMRR meaningless above ~120dB.
    cmrr_inf = cmrr[0] > 130
    cmrr_disp = [min(c, 120) for c in cmrr]
    cmrr_lbl = ("CMRR >120 dB (matched sim;\nmismatch-limited -> Monte Carlo)"
                if cmrr_inf else f"CMRR (DC {cmrr[0]:.0f} dB)")

    dc = mag[0]
    ugf = pm = None
    for i in range(1, len(mag)):
        if mag[i-1] >= 0 >= mag[i]:
            t = mag[i-1]/(mag[i-1]-mag[i])
            ugf = f[i-1]*(f[i]/f[i-1])**t
            pm = 180 + (pha[i-1]+t*(pha[i]-pha[i-1]))
            break

    info = next((HERE / "fcc" / "diff").rglob("opInfo.info"), None)
    devs = parse_info(info) if info else {}
    itail = abs(devs["M0"]["ids"]) if devs else 0.0

    print(f"DC gain {dc:.1f} dB | GBW {ugf/1e6:.1f} MHz | PM {pm:.0f} deg "
          f"| PSRR {psrr[0]:.0f} dB | CMRR {cmrr[0]:.0f} dB "
          f"| Itail {itail*1e6:.2f} uA")

    # Figure: 2x2 dashboard
    fig, ax = plt.subplots(2, 2, figsize=(11.5, 7.6))
    ax[0, 0].semilogx(f, mag, "C0"); ax[0, 0].axhline(0, color="grey", ls=":", lw=.6)
    if ugf: ax[0, 0].axvline(ugf, color="C3", ls="--", lw=.8)
    ax[0, 0].set_title(f"Differential gain  A0={dc:.1f} dB"); ax[0, 0].set_ylabel("dB")
    ax[0, 0].grid(True, which="both", alpha=.3)
    ax[1, 0].semilogx(f, pha, "C1"); ax[1, 0].axhline(-90, color="grey", ls=":", lw=.6)
    if ugf: ax[1, 0].axvline(ugf, color="C3", ls="--", lw=.8)
    ax[1, 0].set_title(f"Phase  (PM={pm:.0f}deg @ {ugf/1e6:.1f} MHz)")
    ax[1, 0].set_ylabel("deg"); ax[1, 0].set_xlabel("Hz"); ax[1, 0].grid(True, which="both", alpha=.3)
    ax[0, 1].semilogx(f, psrr, "C2", label=f"PSRR (DC {psrr[0]:.0f} dB)")
    ax[0, 1].semilogx(f, cmrr_disp, "C4", ls="--", label=cmrr_lbl)
    ax[0, 1].set_title("PSRR(+) and CMRR vs frequency")
    ax[0, 1].set_ylim(-20, 130)
    ax[0, 1].set_ylabel("dB"); ax[0, 1].set_xlabel("Hz"); ax[0, 1].legend(fontsize=8); ax[0, 1].grid(True, which="both", alpha=.3)

    ax[1, 1].axis("off")
    rows = [f"{'dev':<4}{'ID/uA':>7}{'gm/uS':>7}{'gm/ID':>6}{'reg':>5}"]
    for nm in ("M0", "M1", "M3", "M5", "M7", "M9"):
        x = devs.get(nm)
        if x:
            idd = abs(x["ids"])
            r = "sat" if abs(x["vds"]) > abs(x["vdsat"]) else "LIN"
            rows.append(f"{nm:<4}{idd*1e6:7.3f}{x['gm']*1e6:7.2f}{x['gm']/idd:6.1f}{r:>5}")
    txt = ("FOLDED-CASCODE PMOS-INPUT OTA (tsmc18 1.8V, ideal bias)\n"
           "  in pair  M1,M2 : W=3u/L=1u (pmos)\n"
           "  tail     M0    : W=4u/L=1u (pmos)\n"
           "  N sinks  M3,M4 : W=1u/L=1u\n"
           "  N casc   M5,M6 : W=1u/L=0.5u\n"
           "  P casc/mir M7-10: W=2u/L=0.5u\n"
           f"  Vcm={P['vcm']}V (low! PMOS-in)  OUT~{P['vcm']+P['voff']}V  CL=50fF\n"
           f"  bias: Vbtail={P['vbtail']} Vbn={P['vbn']} Vbnc={P['vbnc']} Vbpc={P['vbpc']}\n"
           f"  Itail={itail*1e6:.2f}uA  Power~{itail*1.8*2*1e6:.1f}uW\n\n" + "\n".join(rows))
    ax[1, 1].text(0.0, 0.99, txt, va="top", family="monospace", fontsize=9.5)
    fig.suptitle("Folded-cascode PMOS-input OTA — summary (Spectre, tsmc18, ideal bias)", fontsize=12)
    fig.tight_layout(); fig.savefig(HERE / "fc_ota_summary.png", dpi=130)

    # standalone Bode
    fig2, (a, b) = plt.subplots(2, 1, figsize=(7.2, 6.4), sharex=True)
    a.semilogx(f, mag, "C0"); a.axhline(0, color="grey", ls=":", lw=.6)
    if ugf: a.axvline(ugf, color="C3", ls="--", lw=.8)
    a.set_ylabel("|Adm| (dB)"); a.grid(True, which="both", alpha=.3)
    a.set_title(f"Folded-cascode PMOS-input OTA  (A0={dc:.1f}dB, GBW={ugf/1e6:.1f}MHz, PM={pm:.0f}deg)")
    b.semilogx(f, pha, "C1"); b.axhline(-90, color="grey", ls=":", lw=.6)
    if ugf: b.axvline(ugf, color="C3", ls="--", lw=.8)
    b.set_ylabel("phase (deg)"); b.set_xlabel("frequency (Hz)"); b.grid(True, which="both", alpha=.3)
    fig2.tight_layout(); fig2.savefig(HERE / "fc_ota_bode.png", dpi=130)
    print("saved fc_ota_summary.png, fc_ota_bode.png")


if __name__ == "__main__":
    main()
