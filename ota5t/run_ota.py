#!/usr/bin/env python3
"""
5-transistor OTA — tsmc18 BCD gen2 (1.8 V core nch_mac / pch_mac).
Ideal-voltage-source bias.  Open-loop AC via huge-L / huge-C feedback so the
output self-biases to Vcm while the loop is open at AC.

Topology (NMOS input pair, PMOS mirror load, NMOS tail):
    M1,M2  nch_mac  input pair      (gates vinp/vinn, sources -> vtail)
    M3,M4  pch_mac  mirror load     (M3 diode @ vx, M4 output @ vout)
    M5     nch_mac  tail current    (gate vbias, ideal)

Run:  uv run python ota5t/run_ota.py
"""
from __future__ import annotations
import math
import re
from pathlib import Path

from virtuoso_bridge.spectre.runner import SpectreSimulator

MODELS = ("/mnt/hgfs/share_folder/"
          "tsmc18_HRI_1K_1.8V_5V_1.0fF_GA_GB_1P6M_4K_MIM_15K/models/spectre")

HERE = Path(__file__).resolve().parent

# ---- design knobs (edit + rerun to iterate) --------------------------------
P = dict(
    w1=3.0,  l1=1.0, nf1=1,   # input pair M1,M2  (um)
    w3=6.0,  l3=1.0, nf3=1,   # mirror load M3,M4 (um)
    w5=5.0,  l5=1.0, nf5=1,   # tail M5           (um)
    vcm=0.9, vb=0.63, cl=1.0, # Vcm(V), tail gate bias(V), load cap(pF)
)

# bsim4 oppoint STRUCT field order (from .info TYPE section)
_INFO_FIELDS = ["ids", "vgs", "vds", "vbs", "vgd", "vdb", "vgb",
                "vth", "vdsat", "gm", "gds", "gmbs", "betaeff"]


def parse_info(path: Path) -> dict:
    """Parse a Spectre `info what=oppoint` STRUCT PSF into {inst: {field: val}}."""
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    devs: dict[str, dict] = {}
    j = lines.index("VALUE") + 1 if "VALUE" in lines else len(lines)
    while j < len(lines):
        s = lines[j].strip()
        if s == "END" or s == "":
            break
        m = re.match(r'"([^"]+)"\s+"bsim4"\s*\(', s)
        if m:
            name, vals, j = m.group(1), [], j + 1
            while j < len(lines) and lines[j].strip() != ")":
                try:
                    vals.append(float(lines[j].strip()))
                except ValueError:
                    pass
                j += 1
            devs[name] = dict(zip(_INFO_FIELDS, vals))
        j += 1
    return devs


def netlist(p: dict, mode: str) -> str:
    """mode='gain' -> AC on input ; mode='psrr' -> AC on vdd."""
    in_ac  = 1 if mode == "gain" else 0
    vdd_ac = 1 if mode == "psrr" else 0
    return f"""// 5T OTA gain/psrr testbench ({mode}) - tsmc18 BCD gen2, ideal bias
simulator lang=spectre
global 0
include "{MODELS}/c018bcd_gen2_v1d6_usage.scs" section=pre_simu
include "{MODELS}/c018bcd_gen2_v1d6_usage.scs" section=tt_lib

// --- ideal supplies / bias ---
Vdd   (vdd   0)     vsource dc=1.8 mag={vdd_ac}
Vcm   (vincm 0)     vsource dc={p['vcm']}
Vbias (vbias 0)     vsource dc={p['vb']}
Vinp  (vinp  vincm) vsource dc=0 mag={in_ac}

// --- open-loop AC bias network: DC short (L) sets vout=vcm, AC open ---
Lfb (vout vinn)  inductor l=1T
Cac (vinn vincm) capacitor c=1T

// --- 5T OTA core (d g s b) ---
M1 (vx    vinp vtail 0)   nch_mac w={p['w1']}u l={p['l1']}u nf={p['nf1']}
M2 (vout  vinn vtail 0)   nch_mac w={p['w1']}u l={p['l1']}u nf={p['nf1']}
M3 (vx    vx   vdd   vdd) pch_mac w={p['w3']}u l={p['l3']}u nf={p['nf3']}
M4 (vout  vx   vdd   vdd) pch_mac w={p['w3']}u l={p['l3']}u nf={p['nf3']}
M5 (vtail vbias 0    0)   nch_mac w={p['w5']}u l={p['l5']}u nf={p['nf5']}
CL (vout 0) capacitor c={p['cl']}p

save vout vx vtail vinp vinn
opInfo info what=oppoint where=rawfile
ac ac start=1 stop=10G dec=20
"""


def run(p: dict, mode: str):
    scs = HERE / f"ota5t_{mode}.scs"
    scs.write_text(netlist(p, mode), encoding="utf-8")
    sim = SpectreSimulator.from_env(work_dir=str(HERE / "sim" / mode))
    return sim.run_simulation(scs, {})


def op_table(devs: dict):
    """Print per-device sizing/operating-point table."""
    hdr = ("dev", "ID/uA", "gm/uS", "gds/uS", "gm/ID", "Av0", "Vov/mV",
           "Vth/mV", "Vds/mV", "Vdsat/mV", "region")
    print("\n  " + "".join(f"{h:>8}" for h in hdr))
    for name in ("M1", "M2", "M3", "M4", "M5"):
        x = devs.get(name)
        if not x:
            continue
        idd = abs(x["ids"]); gm = x["gm"]; gds = x["gds"]
        vov = abs(x["vgs"]) - abs(x["vth"])
        sat = "SAT" if abs(x["vds"]) > abs(x["vdsat"]) + 0.003 else "**LIN**"
        row = (name, idd*1e6, gm*1e6, gds*1e6, gm/idd, gm/gds,
               vov*1e3, x["vth"]*1e3, x["vds"]*1e3, x["vdsat"]*1e3, sat)
        print("  " + "".join(
            f"{c:>8}" if isinstance(c, str) else f"{c:>8.2f}" for c in row))
    # hand estimate of DC gain from op data
    try:
        gm1 = devs["M1"]["gm"]
        gout = devs["M2"]["gds"] + devs["M4"]["gds"]
        print(f"\n  hand A0 = gm1/(gds2+gds4) = {20*math.log10(gm1/gout):.1f} dB"
              f"   (gm1={gm1*1e6:.1f}uS, gout={gout*1e6:.2f}uS)")
    except KeyError:
        pass


def main():
    res = run(P, "gain")
    print("ok:", res.ok)
    if res.errors:
        print("ERRORS:")
        for e in res.errors[:8]:
            print("  ", e)
    d = res.data or {}

    # --- operating point (parse STRUCT .info ourselves) ---
    info = next((HERE / "sim" / "gain").rglob("opInfo.info"), None)
    if info:
        op_table(parse_info(info))
    else:
        print("opInfo.info not found")

    # --- AC: DC gain, GBW, phase margin ---
    freq = d.get("ac_freq")
    vout = d.get("ac_vout")
    if freq and vout:
        f = [float(x.real) if isinstance(x, complex) else float(x) for x in freq]
        mag = [20*math.log10(abs(v)) if abs(v) > 0 else -300 for v in vout]
        ph  = [math.degrees(math.atan2(v.imag, v.real)) for v in vout]
        print(f"\nAC: points={len(f)}  f0={f[0]:.3g}  fmax={f[-1]:.3g}")
        print(f"DC gain = {mag[0]:.2f} dB   phase@DC = {ph[0]:.1f} deg")
        # unity-gain crossing
        fug = pm = None
        for i in range(1, len(mag)):
            if mag[i-1] >= 0 >= mag[i]:
                # log-interp the crossing
                t = mag[i-1] / (mag[i-1] - mag[i])
                fug = f[i-1] * (f[i]/f[i-1])**t
                phc = ph[i-1] + t*(ph[i]-ph[i-1])
                pm = 180 + phc   # neg-fb loop: PM = 180 + open-loop phase
                break
        if fug:
            print(f"GBW (unity) = {fug/1e6:.3f} MHz   phase margin = {pm:.1f} deg")
        else:
            print("no unity-gain crossing in range")
    else:
        print("\nNO AC DATA (ac_freq/ac_vout missing) — check include/analysis")
        print("keys sample:", sorted(d)[:30])


if __name__ == "__main__":
    main()
