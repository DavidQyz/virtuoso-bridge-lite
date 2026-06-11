#!/usr/bin/env python3
"""
Common-gate comparator (test/COMP_CG) transient characterization.

Stimulus per spec:
    INP : 0-5 V half-wave rectified sine, 13.56 MHz (pwl, Python-generated)
    INN : DC reference VREF
    VDD : 1.8 V,  EN=1.8, N_EN=0,  COMP_VCM = bias under study
Metric:
    tprop = t(OUT rising past 0.9 V) - t(INP rising past INN), measured on
    the 2nd half-wave arch (1st arch is warm-up).

Netlist devices mirror test/COMP_CG exactly.  NOTE: in the _mac spectre
macros w = TOTAL width (per-finger = w/nf, bin-checked against Wmin), so
CDF per-finger values are multiplied by fingers here: M0/M1 w=2u nf=4,
M5 w=0.44u nf=2 multi=2.  DBB1 expanded inline (MD0/MD1, cross-coupled
pmos5v max-selector for the n-well).

Usage:
    .venv/Scripts/python.exe ota5t/comp_cg/run_comp.py vcm            # sweep COMP_VCM @ INN=1V
    .venv/Scripts/python.exe ota5t/comp_cg/run_comp.py inn <vcm>      # sweep INN @ fixed vcm
    .venv/Scripts/python.exe ota5t/comp_cg/run_comp.py one <vcm> <vref>   # single point, dump detail
"""
from __future__ import annotations
import math
import sys
from pathlib import Path

from virtuoso_bridge.spectre.runner import SpectreSimulator

MODELS = ("/mnt/hgfs/share_folder/"
          "tsmc18_HRI_1K_1.8V_5V_1.0fF_GA_GB_1P6M_4K_MIM_15K/models/spectre")
HERE = Path(__file__).resolve().parent

F0     = 13.56e6            # Hz
T      = 1.0 / F0           # 73.746 ns
TH     = T / 2.0            # arch width
T0     = 10e-9              # settle before 1st arch
ARCH2  = T0 + T             # start of measurement arch (= start of period 2)
TSTOP  = T0 + 2 * T + 5e-9  # full 2nd period (arch + dead time) for energy


def halfwave_pwl(npts_per_arch: int = 150) -> str:
    """PWL wave for 2 half-sine arches: [t0 v0 t1 v1 ...] with line breaks."""
    pts: list[tuple[float, float]] = [(0.0, 0.0)]
    for k in range(2):                       # two arches
        ts = T0 + k * T
        if pts[-1][0] < ts:
            pts.append((ts, 0.0))
        for i in range(1, npts_per_arch + 1):
            t = ts + TH * i / npts_per_arch
            pts.append((t, 5.0 * math.sin(2 * math.pi * F0 * (t - ts))))
        pts[-1] = (pts[-1][0], 0.0)          # exact zero at arch end
    pts.append((TSTOP + 1e-9, 0.0))
    flat = [f"{t:.6e} {max(v, 0.0):.6f}" for t, v in pts]
    lines = ["  ".join(flat[i:i + 6]) for i in range(0, len(flat), 6)]
    return " \\\n    ".join(lines)


def netlist(sweep_param: str, values: list[float], vref: float, vcm: float) -> str:
    vals = " ".join(f"{v:g}" for v in values)
    return f"""// COMP_CG tprop testbench - tsmc18, half-wave 13.56MHz on INP
simulator lang=spectre
global 0
include "{MODELS}/c018bcd_gen2_v1d6_usage.scs" section=pre_simu
include "{MODELS}/c018bcd_gen2_v1d6_usage.scs" section=tt_lib

parameters vref={vref:g} vcm={vcm:g} win=2u

// --- supplies / control ---
Vdd  (vdd 0)      vsource dc=1.8
Ven  (en 0)       vsource dc=1.8
Vnen (n_en 0)     vsource dc=0
Vvcm (comp_vcm 0) vsource dc=vcm
Vinn (inn 0)      vsource dc=vref
Vinp (inp 0)      vsource type=pwl wave=[ \\
    {halfwave_pwl()} ]

// --- comparator core, exact COMP_CG sizing (d g s b) ---
M0  (comp_out net78 inp  v_bb) pch_5_mac w=win   l=0.5u  nf=4
M1  (net78   net78  inn  v_bb) pch_5_mac w=win   l=0.5u  nf=4
M10 (v_bb    v_bb   inn  v_bb) pch_5_mac w=0.5u  l=0.5u  nf=1 multi=2
M11 (v_bb    v_bb   inp  v_bb) pch_5_mac w=0.5u  l=0.5u  nf=1 multi=2
M2  (comp_out v_bn  0    0)    nch_5_mac w=0.22u l=0.6u  nf=1
M3  (net78   v_bn   0    0)    nch_5_mac w=0.22u l=0.6u  nf=1
M5  (mid_inv comp_out 0  0)    nch_5_mac w=0.44u l=0.6u  nf=2 multi=2
M6  (mid_inv comp_out vdd vdd) pch_5_mac w=0.22u l=0.5u  nf=1
M9  (v_bn    n_en   0    0)    nch_mac   w=0.22u l=0.18u nf=1
M20 (out     mid_inv 0   0)    nch_mac   w=0.22u l=0.18u nf=1
M21 (out     mid_inv vdd vdd)  pch_mac   w=0.88u l=0.18u nf=1
M22 (comp_vcm en    v_bn 0)    nch_mac   w=0.22u l=0.18u nf=1
// --- DBB1 (I3) expanded: cross-coupled n-well max-selector ---
MD0 (v_bb    inn    inp  v_bb) pch_5_mac w=0.22u l=0.5u  nf=1
MD1 (inn     inp    v_bb v_bb) pch_5_mac w=0.22u l=0.5u  nf=1

save inp out comp_out mid_inv v_bn v_bb net78 Vdd:p Vinp:p Vinn:p Vvcm:p
sw1 sweep param={sweep_param} values=[{vals}] {{
  tr tran stop={TSTOP:g} errpreset=conservative maxstep=50p
}}
"""


def cross(t: list[float], y: list[float], thresh: float,
          tmin: float, rising: bool = True) -> float | None:
    """First threshold crossing after tmin (linear interp)."""
    for i in range(1, len(t)):
        if t[i] < tmin:
            continue
        a, b = y[i - 1] - thresh, y[i] - thresh
        if (a < 0 <= b) if rising else (a > 0 >= b):
            if a == b:
                return t[i]
            return t[i - 1] + (t[i] - t[i - 1]) * (-a) / (b - a)
    return None


def measure(sig: dict, vref: float) -> dict:
    """tprop on the 2nd arch + sanity levels."""
    t = [float(x) for x in sig["time"]]
    inp = [float(x) for x in sig["inp"]]
    out = [float(x) for x in sig["out"]]
    t_x = cross(t, inp, vref, ARCH2)                  # INP rises past INN
    res = dict(t_x=t_x, t_out=None, tprop=None, out_pre=None, out_max=None)
    if t_x is None:
        return res
    pre = [v for tt, v in zip(t, out) if ARCH2 - 5e-9 <= tt < t_x]
    res["out_pre"] = max(pre) if pre else None        # should be low (<0.9)
    res["t_out"] = cross(t, out, 0.9, t_x)
    res["out_max"] = max(v for tt, v in zip(t, out) if tt >= t_x)
    if res["t_out"] is not None:
        res["tprop"] = res["t_out"] - t_x
    return res


def power(sig: dict, vref: float, vcm: float) -> dict:
    """Average power drawn from each source over the 2nd full period.

    SPICE convention: I(V:p) flows from + through the source, so power
    DELIVERED by the source = -V * I.  Trapezoid over [ARCH2, ARCH2+T].
    """
    t = [float(x) for x in sig["time"]]
    inp = [float(x) for x in sig["inp"]]
    cur = {k: [float(x) for x in sig[k]]
           for k in ("Vdd:p", "Vinp:p", "Vinn:p", "Vvcm:p") if k in sig}
    if len(cur) < 4:
        return {}
    lo, hi = ARCH2, ARCH2 + T

    def integ(p_of_i: list[float]) -> float:          # ∫p dt / T
        e = 0.0
        for i in range(1, len(t)):
            if t[i] <= lo or t[i - 1] >= hi:
                continue
            e += 0.5 * (p_of_i[i] + p_of_i[i - 1]) * (t[i] - t[i - 1])
        return e / T

    n = len(t)
    p_vdd = integ([-1.8 * x for x in cur["Vdd:p"]])
    p_inp = integ([-inp[i] * cur["Vinp:p"][i] for i in range(n)])
    p_inn = integ([-vref * x for x in cur["Vinn:p"]])
    p_vcm = integ([-vcm * x for x in cur["Vvcm:p"]])
    return dict(p_vdd=p_vdd, p_inp=p_inp, p_inn=p_inn, p_vcm=p_vcm,
                p_tot=p_vdd + p_inp + p_inn + p_vcm)


def run(tag: str, sweep_param: str, values: list[float],
        vref: float, vcm: float):
    scs = HERE / f"comp_{tag}.scs"
    scs.write_text(netlist(sweep_param, values, vref, vcm), encoding="utf-8")
    sim = SpectreSimulator.from_env(work_dir=str(HERE / "comp" / tag))
    res = sim.run_simulation(scs, {})
    print(f"ok: {res.ok}")
    for e in (res.errors or [])[:8]:
        print("  ERR:", e)
    return res


def report(res, sweep_param: str, values: list[float], vref_fixed: float):
    pts = (res.metadata or {}).get("sweep_points") or {}
    if not pts:
        print("NO SWEEP DATA; data keys:", sorted((res.data or {}))[:20])
        return
    print(f"\n  {'#':>3} {sweep_param + '/V':>8} {'tprop/ns':>10} "
          f"{'out_pre/V':>10} {'out_max/V':>10}")
    for idx in sorted(pts):
        if idx > len(values):      # stale files from a previous larger sweep
            continue
        sig = pts[idx]
        v = values[idx - 1]
        vref = v if sweep_param == "vref" else vref_fixed
        m = measure(sig, vref)
        tp = f"{m['tprop'] * 1e9:.3f}" if m["tprop"] is not None else "  --"
        op = f"{m['out_pre']:.3f}" if m["out_pre"] is not None else "--"
        om = f"{m['out_max']:.3f}" if m["out_max"] is not None else "--"
        print(f"  {idx:>3} {v:>8.2f} {tp:>10} {op:>10} {om:>10}")


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "vcm"
    if mode == "vcm":
        vals = ([float(v) for v in sys.argv[2:]] or
                [0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.2])
        res = run("vcm", "vcm", vals, vref=1.0, vcm=0.6)
        report(res, "vcm", vals, vref_fixed=1.0)
    elif mode == "inn":
        vcm = float(sys.argv[2]) if len(sys.argv) > 2 else 0.6
        vals = [round(0.1 * i, 1) for i in range(1, 50)]   # 0.1 .. 4.9
        res = run("inn", "vref", vals, vref=1.0, vcm=vcm)
        report(res, "vref", vals, vref_fixed=vcm)
    elif mode == "pwr":            # full INN sweep -> tprop + power -> JSON
        import json
        vcm = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
        vals = [round(0.1 * i, 1) for i in range(1, 50)]   # 0.1 .. 4.9
        res = run("pwr", "vref", vals, vref=1.0, vcm=vcm)
        pts = (res.metadata or {}).get("sweep_points") or {}
        rows = []
        for idx in sorted(pts):
            if idx > len(vals):
                continue
            vref = vals[idx - 1]
            m = measure(pts[idx], vref)
            p = power(pts[idx], vref, vcm)
            rows.append(dict(inn=vref, tprop=m["tprop"], **p))
            tp = f"{m['tprop'] * 1e9:.3f}" if m["tprop"] else "--"
            print(f"  INN={vref:4.1f}  tprop={tp:>7}ns  "
                  f"Pvdd={p.get('p_vdd', 0) * 1e6:8.2f}uW  "
                  f"Pinp={p.get('p_inp', 0) * 1e6:8.2f}uW  "
                  f"Pinn={p.get('p_inn', 0) * 1e6:8.2f}uW  "
                  f"Pvcm={p.get('p_vcm', 0) * 1e6:8.2f}uW  "
                  f"Ptot={p.get('p_tot', 0) * 1e6:8.2f}uW")
        out = HERE / "comp_char.json"
        out.write_text(json.dumps(dict(vcm=vcm, f0=F0, rows=rows), indent=1),
                       encoding="utf-8")
        print(f"saved -> {out}")
    elif mode == "win":            # input-pair total width sweep (nf=4 fixed)
        vals = [1e-6, 1.5e-6, 2e-6, 3e-6, 4e-6]
        res = run("win", "win", vals, vref=1.0, vcm=1.0)
        report(res, "win", vals, vref_fixed=1.0)
    elif mode == "one":
        vcm = float(sys.argv[2]); vref = float(sys.argv[3])
        res = run("one", "vcm", [vcm], vref=vref, vcm=vcm)
        pts = (res.metadata or {}).get("sweep_points") or {}
        if pts:
            sig = pts[min(pts)]
            m = measure(sig, vref)
            print({k: (f"{v * 1e9:.3f}ns" if k.startswith("t") and v else v)
                   for k, v in m.items()})
            t = sig["time"]; out = sig["out"]; co = sig["comp_out"]
            print(f"  points={len(t)}  out(end)={float(out[-1]):.3f}  "
                  f"comp_out(end)={float(co[-1]):.3f}")
    else:
        print("usage: run_comp.py [vcm | inn <vcm> | one <vcm> <vref>]")


if __name__ == "__main__":
    main()
