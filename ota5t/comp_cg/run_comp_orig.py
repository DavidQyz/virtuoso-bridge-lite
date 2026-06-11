#!/usr/bin/env python3
"""
Characterize the ORIGINAL V4 comparator (test/COMP_V4_ORIG, copied from
test_rect/comparator_newV4_for_use_nb) using the Cadence-generated netlist.

The device body comes from `si -batch -command nl` (v4_orig_netlist.scs) --
every CDF-evaluated parameter (ad/as/pd/ps/sd/nrd/nrs...) is the database
ground truth, not a hand transcription.  Stimuli / measures are imported
from run_comp.py so all three versions (ORIG / COMP_CG replica / COMP_V2)
see byte-identical excitation.

Usage:
    .venv/Scripts/python.exe ota5t/comp_cg/run_comp_orig.py pwr [vcm]
    .venv/Scripts/python.exe ota5t/comp_cg/run_comp_orig.py one <vcm> <vref>
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

from virtuoso_bridge.spectre.runner import SpectreSimulator
from run_comp import (cross, measure, power, halfwave_pwl,
                      ARCH2, T, T0, TSTOP, F0, MODELS)

HERE = Path(__file__).resolve().parent
BODY = (HERE / "v4_orig_netlist.scs").read_text(encoding="utf-8")


def netlist(values: list[float], vref: float, vcm: float) -> str:
    vals = " ".join(f"{v:g}" for v in values)
    return f"""// ORIGINAL V4 comparator tprop testbench (si-generated body)
simulator lang=spectre
global 0
include "{MODELS}/c018bcd_gen2_v1d6_usage.scs" section=pre_simu
include "{MODELS}/c018bcd_gen2_v1d6_usage.scs" section=tt_lib

parameters vref={vref:g} vcm={vcm:g}

Vdd  (VDD 0)      vsource dc=1.8
Vvss (VSS 0)      vsource dc=0
Ven  (EN 0)       vsource dc=1.8
Vnen (N_EN 0)     vsource dc=0
Vvcm (COMP_VCM 0) vsource dc=vcm
Vinn (INN 0)      vsource dc=vref
Vinp (INP 0)      vsource type=pwl wave=[ \\
    {halfwave_pwl()} ]

// ---- si-generated body of test/COMP_V4_ORIG ----
{BODY}
// ---- end body ----

save INP OUT COMP_OUT MID_INV Vdd:p Vinp:p Vinn:p Vvcm:p
sw1 sweep param=vref values=[{vals}] {{
  tr tran stop={TSTOP:g} errpreset=conservative maxstep=50p
}}
"""


def adapt(sig: dict) -> dict:
    """Map uppercase si-netlist signal names onto run_comp's lowercase keys."""
    s = dict(sig)
    s["inp"] = sig["INP"]
    s["out"] = sig["OUT"]
    return s


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "pwr"
    vcm = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
    if mode == "one":
        vref = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
        vals = [vref]
    else:
        vals = [round(0.1 * i, 1) for i in range(1, 50)]

    scs = HERE / "comp_orig.scs"
    scs.write_text(netlist(vals, 1.0, vcm), encoding="utf-8")
    sim = SpectreSimulator.from_env(work_dir=str(HERE / "orig" / mode))
    res = sim.run_simulation(scs, {})
    print(f"ok: {res.ok}")
    for e in (res.errors or [])[:8]:
        print("  ERR:", e)

    pts = (res.metadata or {}).get("sweep_points") or {}
    rows = []
    for idx in sorted(pts):
        if idx > len(vals):
            continue
        vref = vals[idx - 1]
        sig = adapt(pts[idx])
        m = measure(sig, vref)
        p = power(sig, vref, vcm)
        rows.append(dict(inn=vref, tprop=m["tprop"], **p))
        tp = f"{m['tprop'] * 1e9:.3f}" if m["tprop"] else "--"
        print(f"  INN={vref:4.1f}  tprop={tp:>7}ns  "
              f"Ptot={p.get('p_tot', 0) * 1e6:8.2f}uW")
    if mode == "pwr":
        out = HERE / "comp_orig_char.json"
        out.write_text(json.dumps(dict(vcm=vcm, f0=F0, rows=rows), indent=1),
                       encoding="utf-8")
        print(f"saved -> {out}")


if __name__ == "__main__":
    main()
