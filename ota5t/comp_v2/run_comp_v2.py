#!/usr/bin/env python3
"""
COMP_V2 — common-gate comparator with low-swing 2V decision path.

Architecture change vs COMP_CG (V4):
  Front end UNCHANGED (M0/M1 CG pair, M2/M3 sinks, DBB, EN switches) -- the
  M2 current-source load is what throttles M0 in triode at high INP, keeping
  P_INP bounded; any scheme that pins M0's drain low would unleash hundreds
  of uA at INP=5V.  The redesign is the decision chain:

    MCL  nmos5v pass-clamp, G=VDD:  YC = min(comp_out, VDD - VthN5(body))
    INV1' skewed 2V inverter at YC (M5 strong N short-L / M6 weak long-L P)
    INV2  unchanged 2V inverter -> OUT

  Wins: decision threshold 0.75V (nmos5v) -> ~0.45V (nmos2v); comp_out node
  sheds the thick-oxide INV1 gate load; decision devices are L=0.18u.
  Voltage safety: comp_out still swings to ~INP (5V) but only MCL's drain
  (5V-rated) sees it; YC is clamped <= ~0.9-1.0V so all 2V gates are safe.

Usage:
    .venv/Scripts/python.exe ota5t/comp_v2/run_comp_v2.py one <vcm> <vref>
    .venv/Scripts/python.exe ota5t/comp_v2/run_comp_v2.py vcm [v1 v2 ...]
    .venv/Scripts/python.exe ota5t/comp_v2/run_comp_v2.py sw <param> v1 v2 ...
    .venv/Scripts/python.exe ota5t/comp_v2/run_comp_v2.py inn [vcm]
    .venv/Scripts/python.exe ota5t/comp_v2/run_comp_v2.py pwr [vcm]
"""
from __future__ import annotations
import json
import math
import sys
from pathlib import Path

from virtuoso_bridge.spectre.runner import SpectreSimulator

MODELS = ("/mnt/hgfs/share_folder/"
          "tsmc18_HRI_1K_1.8V_5V_1.0fF_GA_GB_1P6M_4K_MIM_15K/models/spectre")
HERE = Path(__file__).resolve().parent

F0     = 13.56e6
T      = 1.0 / F0
TH     = T / 2.0
T0     = 10e-9
ARCH2  = T0 + T
TSTOP  = T0 + 2 * T + 5e-9

# V2 design knobs (spectre `parameters`, all sweepable via `sw` mode).
# pc/fb are Python-side include flags (0/1), not spectre params:
#   pc: M_PC precharge floor  (nmos5v G=COMP_VCM D=VDD S=comp_out, weak/long)
#   fb: M_FB regen feedback   (pmos5v G=mid S=VDD D=comp_out, weak/long)
# FINAL V2.1 sizing (2026-06-11 sweeps): minimum-cap decision chain wins --
# wcl/w5a/w5n all at 0.22u; tprop 0.923ns @ INN=1V, 8.74uW (V4: 1.015ns/8.75uW)
KNOBS = dict(vref=1.0, vcm=1.0, wcl="0.22u", w5n="0.22u", w5a="0.22u",
             nf0="4", l6p="0.72u", w21="0.88u", wpc="0.22u", lpc="2.4u",
             wfb="0.22u", lfb="1u")
FLAGS = dict(pc=0, fb=0)


def halfwave_pwl(npts_per_arch: int = 150) -> str:
    pts: list[tuple[float, float]] = [(0.0, 0.0)]
    for k in range(2):
        ts = T0 + k * T
        if pts[-1][0] < ts:
            pts.append((ts, 0.0))
        for i in range(1, npts_per_arch + 1):
            t = ts + TH * i / npts_per_arch
            pts.append((t, 5.0 * math.sin(2 * math.pi * F0 * (t - ts))))
        pts[-1] = (pts[-1][0], 0.0)
    pts.append((TSTOP + 1e-9, 0.0))
    flat = [f"{t:.6e} {max(v, 0.0):.6f}" for t, v in pts]
    lines = ["  ".join(flat[i:i + 6]) for i in range(0, len(flat), 6)]
    return " \\\n    ".join(lines)


def netlist(sweep_param: str, values: list, knobs: dict,
            flags: dict | None = None) -> str:
    flags = flags or FLAGS
    vals = " ".join(f"{v:g}" if isinstance(v, (int, float)) else str(v)
                    for v in values)
    p = " ".join(f"{k}={v}" for k, v in knobs.items())
    extras = ""
    if flags.get("pc"):
        extras += ("MPC (vdd     comp_vcm comp_out 0) "
                   "nch_5_mac w=wpc l=lpc nf=1   // precharge floor\n")
    if flags.get("fb"):
        # regen on YC (2V domain only -- never load comp_out: pinning the 5V
        # node would defeat M0's triode current limiting at high INP)
        extras += ("MFB (yc      mid    vdd  vdd) "
                   "pch_mac   w=wfb l=lfb nf=1   // regen feedback on YC\n")
    return f"""// COMP_V2 tprop testbench - low-swing 2V decision path
simulator lang=spectre
global 0
include "{MODELS}/c018bcd_gen2_v1d6_usage.scs" section=pre_simu
include "{MODELS}/c018bcd_gen2_v1d6_usage.scs" section=tt_lib

parameters {p}

Vdd  (vdd 0)      vsource dc=1.8
Ven  (en 0)       vsource dc=1.8
Vnen (n_en 0)     vsource dc=0
Vvcm (comp_vcm 0) vsource dc=vcm
Vinn (inn 0)      vsource dc=vref
Vinp (inp 0)      vsource type=pwl wave=[ \\
    {halfwave_pwl()} ]

// --- front end: identical to COMP_CG/V4 (d g s b) ---
M0  (comp_out net78 inp  v_bb) pch_5_mac w=2u    l=0.5u  nf=nf0
M1  (net78   net78  inn  v_bb) pch_5_mac w=2u    l=0.5u  nf=4
M10 (v_bb    v_bb   inn  v_bb) pch_5_mac w=0.5u  l=0.5u  nf=1 multi=2
M11 (v_bb    v_bb   inp  v_bb) pch_5_mac w=0.5u  l=0.5u  nf=1 multi=2
M2  (comp_out v_bn  0    0)    nch_5_mac w=0.22u l=0.6u  nf=1
M3  (net78   v_bn   0    0)    nch_5_mac w=0.22u l=0.6u  nf=1
M22 (comp_vcm en    v_bn 0)    nch_mac   w=0.22u l=0.18u nf=1
M9  (v_bn    n_en   0    0)    nch_mac   w=0.22u l=0.18u nf=1
MD0 (v_bb    inn    inp  v_bb) pch_5_mac w=0.22u l=0.5u  nf=1
MD1 (inn     inp    v_bb v_bb) pch_5_mac w=0.22u l=0.5u  nf=1

// --- V2 decision path: dual-threshold parallel sense on `mid` ---
//  path A (= V4): M5 nmos5v G=comp_out -- 0.75V threshold, but gate OD keeps
//                 growing as comp_out -> INP (fast completion at high INN)
//  path B (new):  MCL clamp + M5B nmos2v G=yc -- 0.45V threshold, L=0.18u
//                 (fires early; rescues the low-INN region where comp_out
//                  plateaus near INP and never reaches path A's threshold)
MCL (comp_out vdd   yc   0)    nch_5_mac w=wcl   l=0.6u  nf=1
M5  (mid     comp_out 0  0)    nch_5_mac w=w5a   l=0.6u  nf=1
M5B (mid     yc     0    0)    nch_mac   w=w5n   l=0.18u nf=1
M6  (mid     comp_out vdd vdd) pch_5_mac w=0.22u l=0.5u  nf=1
M20 (out     mid    0    0)    nch_mac   w=0.22u l=0.18u nf=1
M21 (out     mid    vdd  vdd)  pch_mac   w=w21   l=0.18u nf=1
{extras}
save inp out comp_out yc mid v_bn v_bb Vdd:p Vinp:p Vinn:p Vvcm:p
sw1 sweep param={sweep_param} values=[{vals}] {{
  tr tran stop={TSTOP:g} errpreset=conservative maxstep=50p
}}
"""


def cross(t, y, thresh, tmin, rising=True):
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
    t = [float(x) for x in sig["time"]]
    inp = [float(x) for x in sig["inp"]]
    out = [float(x) for x in sig["out"]]
    t_x = cross(t, inp, vref, ARCH2)
    res = dict(t_x=t_x, t_out=None, tprop=None, out_pre=None, out_max=None)
    if t_x is None:
        return res
    pre = [v for tt, v in zip(t, out) if ARCH2 - 5e-9 <= tt < t_x]
    res["out_pre"] = max(pre) if pre else None
    res["t_out"] = cross(t, out, 0.9, t_x)
    res["out_max"] = max(v for tt, v in zip(t, out) if tt >= t_x)
    if res["t_out"] is not None:
        res["tprop"] = res["t_out"] - t_x
    return res


def power(sig: dict, vref: float, vcm: float) -> dict:
    t = [float(x) for x in sig["time"]]
    inp = [float(x) for x in sig["inp"]]
    cur = {k: [float(x) for x in sig[k]]
           for k in ("Vdd:p", "Vinp:p", "Vinn:p", "Vvcm:p") if k in sig}
    if len(cur) < 4:
        return {}
    lo, hi = ARCH2, ARCH2 + T

    def integ(p_of_i):
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


def run(tag: str, sweep_param: str, values: list, knobs: dict,
        flags: dict | None = None):
    scs = HERE / f"v2_{tag}.scs"
    scs.write_text(netlist(sweep_param, values, knobs, flags),
                   encoding="utf-8")
    sim = SpectreSimulator.from_env(work_dir=str(HERE / "sim" / tag))
    res = sim.run_simulation(scs, {})
    print(f"ok: {res.ok}")
    for e in (res.errors or [])[:8]:
        print("  ERR:", e)
    return res


def report(res, sweep_param: str, values: list, knobs: dict):
    pts = (res.metadata or {}).get("sweep_points") or {}
    if not pts:
        print("NO SWEEP DATA; data keys:", sorted((res.data or {}))[:20])
        return
    print(f"\n  {'#':>3} {sweep_param:>8} {'tprop/ns':>10} {'out_pre/V':>10} "
          f"{'out_max/V':>10} {'Ptot/uW':>9}")
    for idx in sorted(pts):
        if idx > len(values):
            continue
        sig = pts[idx]
        v = values[idx - 1]
        vref = float(v) if sweep_param == "vref" else float(knobs["vref"])
        vcm = float(v) if sweep_param == "vcm" else float(knobs["vcm"])
        m = measure(sig, vref)
        p = power(sig, vref, vcm)
        tp = f"{m['tprop'] * 1e9:.3f}" if m["tprop"] is not None else "  --"
        op = f"{m['out_pre']:.3f}" if m["out_pre"] is not None else "--"
        om = f"{m['out_max']:.3f}" if m["out_max"] is not None else "--"
        pt = f"{p.get('p_tot', 0) * 1e6:.2f}" if p else "--"
        print(f"  {idx:>3} {v!s:>8} {tp:>10} {op:>10} {om:>10} {pt:>9}")


def main():
    # peel off k=v overrides anywhere in argv (knobs incl. pc=1/fb=1 flags)
    f = dict(FLAGS)
    k = dict(KNOBS)
    args = []
    for a in sys.argv[1:]:
        if "=" in a:
            kk, vv = a.split("=", 1)
            if kk in f:
                f[kk] = int(vv)
            else:
                k[kk] = vv
        else:
            args.append(a)
    sys.argv = [sys.argv[0]] + args
    mode = sys.argv[1] if len(sys.argv) > 1 else "one"
    if mode == "one":
        k["vcm"] = float(sys.argv[2]) if len(sys.argv) > 2 else k["vcm"]
        k["vref"] = float(sys.argv[3]) if len(sys.argv) > 3 else k["vref"]
        res = run("one", "vcm", [k["vcm"]], k, f)
        pts = (res.metadata or {}).get("sweep_points") or {}
        if pts:
            sig = pts[min(pts)]
            m = measure(sig, k["vref"])
            p = power(sig, k["vref"], k["vcm"])
            print({kk: (f"{v * 1e9:.3f}ns" if kk.startswith("t") and v else v)
                   for kk, v in m.items()})
            print({kk: f"{v * 1e6:.2f}uW" for kk, v in p.items()})
            t = sig["time"]; yc = sig["yc"]
            print(f"  points={len(t)}  yc_max={max(float(x) for x in yc):.3f}V"
                  f"  out(end)={float(sig['out'][-1]):.3f}")
    elif mode == "vcm":
        vals = ([float(v) for v in sys.argv[2:]] or
                [0.7, 0.8, 0.9, 1.0, 1.1, 1.2])
        res = run("vcm", "vcm", vals, k, f)
        report(res, "vcm", vals, k)
    elif mode == "sw":
        pname = sys.argv[2]
        vals = sys.argv[3:]
        res = run(f"sw_{pname}", pname, vals, k, f)
        report(res, pname, vals, k)
    elif mode == "inn":
        k["vcm"] = float(sys.argv[2]) if len(sys.argv) > 2 else k["vcm"]
        vals = [round(0.1 * i, 1) for i in range(1, 50)]
        res = run("inn", "vref", vals, k, f)
        report(res, "vref", vals, k)
    elif mode == "pwr":
        k["vcm"] = float(sys.argv[2]) if len(sys.argv) > 2 else k["vcm"]
        vals = [round(0.1 * i, 1) for i in range(1, 50)]
        res = run("pwr", "vref", vals, k, f)
        pts = (res.metadata or {}).get("sweep_points") or {}
        rows = []
        for idx in sorted(pts):
            if idx > len(vals):
                continue
            vref = vals[idx - 1]
            m = measure(pts[idx], vref)
            p = power(pts[idx], vref, k["vcm"])
            rows.append(dict(inn=vref, tprop=m["tprop"], **p))
            tp = f"{m['tprop'] * 1e9:.3f}" if m["tprop"] else "--"
            print(f"  INN={vref:4.1f}  tprop={tp:>7}ns  "
                  f"Ptot={p.get('p_tot', 0) * 1e6:8.2f}uW")
        out = HERE / "comp_v2_char.json"
        out.write_text(json.dumps(dict(vcm=k["vcm"], f0=F0, rows=rows),
                                  indent=1), encoding="utf-8")
        print(f"saved -> {out}")
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
