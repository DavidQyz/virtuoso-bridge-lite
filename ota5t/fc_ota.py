#!/usr/bin/env python3
"""
Folded-cascode PMOS-input OTA — tsmc18 1.8V, ideal-source bias.
Inspired by the thesis IDAC clamp OTA (PMOS input for very low input CM).

Topology (single-ended out):
  M0  pch tail (VDD)            -> ntail
  M1,M2 pch input pair (g=vinp/vinn, s=ntail) -> fold nodes nA,nB
  M3,M4 nch bottom current sinks (g=vbn)       -> nA,nB to VSS
  M5,M6 nch cascode (g=vbnc)                    -> nA2 / OUT
  M7,M8 pch cascode (g=vbpc)                    -> nA2 / OUT
  M9,M10 pch cascode mirror load (g=nA2 diode) -> nA3 / nB3
  CL = 50fF.  Output biased to mid-rail via huge-L + level-shift feedback.

Run: .venv/Scripts/python.exe ota5t/fc_ota.py
"""
from __future__ import annotations
import math
from pathlib import Path

from virtuoso_bridge.spectre.runner import SpectreSimulator
from run_ota import parse_info

MODELS = ("/mnt/hgfs/share_folder/"
          "tsmc18_HRI_1K_1.8V_5V_1.0fF_GA_GB_1P6M_4K_MIM_15K/models/spectre")
HERE = Path(__file__).resolve().parent

P = dict(
    # input pair / tail
    w_in=3.0, l_in=1.0, nf_in=1,
    w_tail=4.0, l_tail=1.0,
    # bottom NMOS sinks
    w_sink=1.0, l_sink=1.0,
    # NMOS cascode
    w_nc=1.0, l_nc=0.5,
    # PMOS cascode + mirror
    w_pc=2.0, l_pc=0.5,
    # ideal bias voltages
    vcm=0.30, voff=0.60,
    vbtail=1.30, vbn=0.52, vbnc=0.90, vbpc=0.95,
    cl=0.05,  # pF -> 50 fF
)


def netlist(p, stim="diff"):
    din = 1 if stim == "diff" else 0
    dvd = 1 if stim == "vdd" else 0
    return f"""// folded-cascode PMOS-input OTA - tsmc18, ideal bias, stim={stim}
simulator lang=spectre
global 0
include "{MODELS}/c018bcd_gen2_v1d6_usage.scs" section=pre_simu
include "{MODELS}/c018bcd_gen2_v1d6_usage.scs" section=tt_lib

Vdd   (vdd   0)     vsource dc=1.8 mag={dvd}
Vcm   (vincm 0)     vsource dc={p['vcm']}
Vbt   (vbtail 0)    vsource dc={p['vbtail']}
Vbn   (vbn   0)     vsource dc={p['vbn']}
Vbnc  (vbnc  0)     vsource dc={p['vbnc']}
Vbpc  (vbpc  0)     vsource dc={p['vbpc']}
Vinp  (vinp  vincm) vsource dc=0 mag={din}

// open-loop AC bias: DC short (L) + level-shift sets OUT=vcm+voff; AC open
Lfb  (out  nls)  inductor l=1T
Voff (nls  vinn) vsource dc={p['voff']}
Cac  (vinn vincm) capacitor c=1T

nodeset out={p['vcm']+p['voff']} nls={p['vcm']+p['voff']} vinn={p['vcm']} ntail=1.6 nA2=1.5 nB2=1.5

M0  (ntail vbtail vdd  vdd)  pch_mac w={p['w_tail']}u l={p['l_tail']}u
M1  (nA    vinp  ntail vdd)  pch_mac w={p['w_in']}u l={p['l_in']}u nf={p['nf_in']}
M2  (nB    vinn  ntail vdd)  pch_mac w={p['w_in']}u l={p['l_in']}u nf={p['nf_in']}
M3  (nA    vbn   0     0)    nch_mac w={p['w_sink']}u l={p['l_sink']}u
M4  (nB    vbn   0     0)    nch_mac w={p['w_sink']}u l={p['l_sink']}u
M5  (nA2   vbnc  nA    0)    nch_mac w={p['w_nc']}u l={p['l_nc']}u
M6  (out   vbnc  nB    0)    nch_mac w={p['w_nc']}u l={p['l_nc']}u
M7  (nA2   vbpc  nA3   vdd)  pch_mac w={p['w_pc']}u l={p['l_pc']}u
M8  (out   vbpc  nB3   vdd)  pch_mac w={p['w_pc']}u l={p['l_pc']}u
M9  (nA3   nA2   vdd   vdd)  pch_mac w={p['w_pc']}u l={p['l_pc']}u
M10 (nB3   nA2   vdd   vdd)  pch_mac w={p['w_pc']}u l={p['l_pc']}u
CL  (out 0) capacitor c={p['cl']}p

save out
opInfo info what=oppoint where=rawfile
ac ac start=1 stop=1G dec=40
"""


def run(p, stim="diff"):
    scs = HERE / f"fc_{stim}.scs"
    scs.write_text(netlist(p, stim), encoding="utf-8")
    sim = SpectreSimulator.from_env(work_dir=str(HERE / "fc" / stim))
    return sim.run_simulation(scs, {})


def op_table(devs):
    order = ["M0", "M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9", "M10"]
    print(f"\n  {'dev':>4}{'ID/uA':>8}{'gm/uS':>8}{'gds/uS':>8}{'gm/ID':>7}"
          f"{'Vds/mV':>8}{'Vdsat/mV':>9}{'reg':>6}")
    for nm in order:
        x = devs.get(nm)
        if not x:
            continue
        idd = abs(x["ids"])
        sat = "SAT" if abs(x["vds"]) > abs(x["vdsat"]) + 0.005 else "**LIN**"
        print(f"  {nm:>4}{idd*1e6:8.3f}{x['gm']*1e6:8.2f}{x['gds']*1e6:8.3f}"
              f"{x['gm']/idd:7.1f}{x['vds']*1e3:8.0f}{x['vdsat']*1e3:9.0f}{sat:>6}")


def main():
    res = run(P, "diff")
    print("ok:", res.ok, "| errors:", res.errors[:3])
    info = next((HERE / "fc" / "diff").rglob("opInfo.info"), None)
    if info:
        devs = parse_info(info)
        op_table(devs)
        if "M1" in devs and "M6" in devs and "M8" in devs:
            gm1 = devs["M1"]["gm"]
            gout = devs["M6"]["gds"] + devs["M8"]["gds"]  # crude (no cascode boost)
            print(f"\n  gm1={gm1*1e6:.2f}uS  (cascode raises Rout >> 1/gout)")
    d = res.data or {}
    f = [float(x.real) if isinstance(x, complex) else float(x) for x in d.get("ac_freq", [])]
    vo = list(d.get("ac_out", []))
    if f and vo:
        mag = [20*math.log10(abs(v)) if abs(v) > 0 else -400 for v in vo]
        ph = [math.degrees(math.atan2(v.imag, v.real)) for v in vo]
        print(f"\n  DC gain = {mag[0]:.2f} dB   phase@DC = {ph[0]:.0f} deg")
        for i in range(1, len(mag)):
            if mag[i-1] >= 0 >= mag[i]:
                t = mag[i-1]/(mag[i-1]-mag[i])
                ugf = f[i-1]*(f[i]/f[i-1])**t
                pm = 180 + (ph[i-1]+t*(ph[i]-ph[i-1]))
                print(f"  GBW = {ugf/1e6:.2f} MHz   PM = {pm:.0f} deg")
                break
    else:
        print("  no AC data")


if __name__ == "__main__":
    main()
