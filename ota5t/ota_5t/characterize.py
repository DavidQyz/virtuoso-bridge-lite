#!/usr/bin/env python3
"""
Small-signal characterization of the 5T OTA (final sizing).
Three open-loop AC runs share the huge-L/huge-C bias network (output self-
biases to Vcm, loop open at AC):
    stim='diff' : AC on differential input  -> Adm(f)   (Bode / gain)
    stim='vdd'  : AC on VDD                 -> Add(f)   (PSRR = Adm/Add)
    stim='cm'   : AC on input common mode   -> Acm(f)   (CMRR = Adm/Acm)

Saves results to ota5t/ota_5t/char_data.json (consumed by svg_figs.py).
Run:  .venv/Scripts/python.exe ota5t/ota_5t/characterize.py
"""
from __future__ import annotations
import json
import math
from pathlib import Path

from virtuoso_bridge.spectre.runner import SpectreSimulator
from run_ota import parse_info  # same dir

MODELS = ("/mnt/hgfs/share_folder/"
          "tsmc18_HRI_1K_1.8V_5V_1.0fF_GA_GB_1P6M_4K_MIM_15K/models/spectre")
HERE = Path(__file__).resolve().parent

# FINAL locked sizing (run_ota.py iteration v3); schematic uses nmos2v/pmos2v
# which map to the same nch/pch core models simulated here as nch_mac/pch_mac.
P = dict(w1=3.0, l1=1.0, nf1=1, w3=6.0, l3=1.0, nf3=1, w5=5.0, l5=1.0, nf5=1,
         vcm=0.9, vb=0.63, cl=1.0, vdd=1.8)


def netlist(stim: str) -> str:
    din = 1 if stim == "diff" else 0
    dvd = 1 if stim == "vdd" else 0
    dcm = 1 if stim == "cm" else 0
    return f"""// 5T OTA characterization stim={stim} - tsmc18 BCD gen2, ideal bias
simulator lang=spectre
global 0
include "{MODELS}/c018bcd_gen2_v1d6_usage.scs" section=pre_simu
include "{MODELS}/c018bcd_gen2_v1d6_usage.scs" section=tt_lib

Vdd   (vdd   0)     vsource dc={P['vdd']} mag={dvd}
Vcm   (vincm 0)     vsource dc={P['vcm']} mag={dcm}
Vbias (vbias 0)     vsource dc={P['vb']}
Vinp  (vinp  vincm) vsource dc=0 mag={din}

Lfb (vout vinn)  inductor l=1T
Cac (vinn vincm) capacitor c=1T

M1 (vx    vinp vtail 0)   nch_mac w={P['w1']}u l={P['l1']}u nf={P['nf1']}
M2 (vout  vinn vtail 0)   nch_mac w={P['w1']}u l={P['l1']}u nf={P['nf1']}
M3 (vx    vx   vdd   vdd) pch_mac w={P['w3']}u l={P['l3']}u nf={P['nf3']}
M4 (vout  vx   vdd   vdd) pch_mac w={P['w3']}u l={P['l3']}u nf={P['nf3']}
M5 (vtail vbias 0    0)   nch_mac w={P['w5']}u l={P['l5']}u nf={P['nf5']}
CL (vout 0) capacitor c={P['cl']}p

save vout
opInfo info what=oppoint where=rawfile
ac ac start=1 stop=10G dec=40
"""


def run(stim: str):
    scs = HERE / f"char_{stim}.scs"
    scs.write_text(netlist(stim), encoding="utf-8")
    sim = SpectreSimulator.from_env(work_dir=str(HERE / "char" / stim))
    res = sim.run_simulation(scs, {})
    d = res.data or {}
    f = [float(x.real) if isinstance(x, complex) else float(x)
         for x in d.get("ac_freq", [])]
    vout = list(d.get("ac_vout", []))
    if not f or not vout:
        raise RuntimeError(f"stim={stim}: no AC data; errors={res.errors[:3]}")
    return f, vout


def db(z):    return 20*math.log10(abs(z)) if abs(z) > 0 else -400.0
def phase(z): return math.degrees(math.atan2(z.imag, z.real))


def main():
    f, adm = run("diff")
    _, add = run("vdd")
    _, acm = run("cm")

    mag = [db(v) for v in adm]
    ph  = [phase(v) for v in adm]
    psrr = [db(adm[i]) - db(add[i]) for i in range(len(f))]
    cmrr = [db(adm[i]) - db(acm[i]) for i in range(len(f))]

    dc_gain = mag[0]
    ugf = pm = f3 = None
    for i in range(1, len(mag)):
        if mag[i-1] >= 0 >= mag[i]:
            t = mag[i-1]/(mag[i-1]-mag[i])
            ugf = f[i-1]*(f[i]/f[i-1])**t
            pm = 180 + (ph[i-1] + t*(ph[i]-ph[i-1]))
            break
    for i in range(1, len(mag)):
        if mag[i] <= dc_gain-3:
            t = (mag[i-1]-(dc_gain-3))/(mag[i-1]-mag[i])
            f3 = f[i-1]*(f[i]/f[i-1])**t
            break

    info = next((HERE / "char" / "diff").rglob("opInfo.info"), None)
    devs = parse_info(info) if info else {}
    itail = abs(devs["M5"]["ids"]) if devs else 0.0

    metrics = dict(dc_gain=dc_gain, f3=f3, ugf=ugf, pm=pm,
                   psrr_dc=psrr[0], cmrr_dc=cmrr[0],
                   itail=itail, power=itail*P["vdd"])
    # device table (subset)
    devtab = {}
    for nm in ("M1", "M2", "M3", "M4", "M5"):
        x = devs.get(nm)
        if x:
            idd = abs(x["ids"])
            devtab[nm] = dict(id=idd, gm=x["gm"], gds=x["gds"],
                              gm_id=x["gm"]/idd, av0=x["gm"]/x["gds"],
                              vth=x["vth"], vds=x["vds"], vdsat=x["vdsat"],
                              sat=abs(x["vds"]) > abs(x["vdsat"]))

    out = dict(freq=f, mag_db=mag, phase_deg=ph, psrr_db=psrr, cmrr_db=cmrr,
               metrics=metrics, devtab=devtab, sizing=P)
    (HERE / "char_data.json").write_text(json.dumps(out), encoding="utf-8")

    print("===== 5T OTA characterization =====")
    print(f"DC gain   : {dc_gain:6.2f} dB")
    print(f"-3dB BW   : {f3/1e3:8.2f} kHz" if f3 else "-3dB: n/a")
    print(f"GBW       : {ugf/1e6:6.3f} MHz" if ugf else "GBW: n/a")
    print(f"PM        : {pm:6.1f} deg" if pm else "PM: n/a")
    print(f"PSRR(DC)  : {psrr[0]:6.2f} dB")
    print(f"CMRR(DC)  : {cmrr[0]:6.2f} dB")
    print(f"Itail     : {itail*1e6:6.2f} uA   power {itail*P['vdd']*1e6:.1f} uW")
    print("saved -> ota5t/ota_5t/char_data.json")


if __name__ == "__main__":
    main()
