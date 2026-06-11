#!/usr/bin/env python3
"""
OTA_V2 — Recycling Folded Cascode (RFC), PMOS input, tsmc18 1.8V.

Architecture change vs fc_ota (conventional folded cascode):
  The input pair is split in half (M1A/M1B, M2A/M2B). The fold-node current
  sinks (old M3/M4, constant-current waste) become 1:K current MIRRORS driven
  by the recycled halves of the input signal, CROSS-coupled so signal currents
  add at the fold nodes:  Gm = gm_half * (1+K).
  In weak/moderate inversion gm ~ I/(n*VT), so at fixed total power Gm is
  ~K-independent and equals ~I_total/2/(n*VT): RFC converts ALL supply current
  into effective input transconductance (the conventional FC wastes the
  cascode-branch share). Measured FC baseline: gm_in=7.68uS @ 2.11uA total
  -> RFC same-power target ~2.3x GBW; 2x power budget (<=4.2uA) -> more.
  Output stage (NMOS cascode + PMOS cascode mirror) unchanged -> same swing,
  same low-Vcm PMOS input. vbn bias pin ELIMINATED (mirrors self-bias).

Usage:
  .venv/Scripts/python.exe ota5t/ota_v2/run_ota_v2.py diff [k=v ...]
  .venv/Scripts/python.exe ota5t/ota_v2/run_ota_v2.py sw <knob> v1 v2 ... [k=v ...]
  .venv/Scripts/python.exe ota5t/ota_v2/run_ota_v2.py full [k=v ...]   # +PSRR/CMRR, save JSON
  .venv/Scripts/python.exe ota5t/ota_v2/run_ota_v2.py baseline          # re-run FC, save JSON
"""
from __future__ import annotations
import json
import math
import re
import sys
from pathlib import Path

from virtuoso_bridge.spectre.runner import SpectreSimulator

MODELS = ("/mnt/hgfs/share_folder/"
          "tsmc18_HRI_1K_1.8V_5V_1.0fF_GA_GB_1P6M_4K_MIM_15K/models/spectre")
HERE = Path(__file__).resolve().parent

# ---- design knobs (all overridable from CLI as k=v) ------------------------
# FINAL OTA_V2 point (2026-06-12 sweeps): A0=75.6dB GBW=69.5MHz PM=61deg
# @ Itot=3.98uA / 7.17uW (1.89x FC baseline 3.80uW). Sweep findings:
#   - wider w_in: GBW up but PM collapses (non-dominant poles bind, not Gm)
#   - K=3 optimal at iso-power (weak inversion makes Gm ~K-independent)
#   - pole fixes: w_mb 0.22 (less mirror C), l_m 0.35 + l_pc 0.35 (faster
#     mirrors, costs ~2.5dB of A0 margin)
#   - current scaling is PM-neutral (gm of every pole scales with I):
#     vbtail 1.285/1.28/1.275 -> 73.0/76.6/80.3 MHz, all PM=61, if more
#     power is ever allowed.
P = dict(
    w_in=3.0,  l_in=1.0,        # input pair, PER SIDE total; halves get w_in/2
    w_tail=8.0, l_tail=1.0, vbtail=1.29,
    w_mb=0.22, l_m=0.35, K=3,   # recycling mirror: K parallel units of w_mb/l_m
    w_nc=1.0,  l_nc=0.5, vbnc=0.90,   # NMOS cascodes
    w_pc=2.0,  l_pc=0.35, vbpc=0.95,  # PMOS cascodes + mirror tops
    vcm=0.30, voff=0.60, cl=0.05,     # input CM, output offset, load pF
)

_INFO_FIELDS = ["ids", "vgs", "vds", "vbs", "vgd", "vdb", "vgb",
                "vth", "vdsat", "gm", "gds", "gmbs", "betaeff"]


def parse_info(path: Path) -> dict:
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


def netlist(p: dict, stim: str = "diff") -> str:
    din = 1 if stim == "diff" else 0
    dvd = 1 if stim == "vdd" else 0
    dcm = 1 if stim == "cm" else 0
    wh = p["w_in"] / 2.0
    return f"""// OTA_V2 recycling folded cascode - tsmc18, ideal bias, stim={stim}
simulator lang=spectre
global 0
include "{MODELS}/c018bcd_gen2_v1d6_usage.scs" section=pre_simu
include "{MODELS}/c018bcd_gen2_v1d6_usage.scs" section=tt_lib

Vdd   (vdd   0)     vsource dc=1.8 mag={dvd}
Vcm   (vincm 0)     vsource dc={p['vcm']} mag={dcm}
Vbt   (vbtail 0)    vsource dc={p['vbtail']}
Vbnc  (vbnc  0)     vsource dc={p['vbnc']}
Vbpc  (vbpc  0)     vsource dc={p['vbpc']}
Vinp  (vinp  vincm) vsource dc=0 mag={din}

// open-loop AC bias: DC short (L) + level-shift sets OUT=vcm+voff; AC open
Lfb  (out  nls)  inductor l=1T
Voff (nls  vinn) vsource dc={p['voff']}
Cac  (vinn vincm) capacitor c=1T

nodeset out={p['vcm'] + p['voff']} nls={p['vcm'] + p['voff']} vinn={p['vcm']} \\
    ntail=0.85 x1=0.45 x2=0.45 nA=0.25 nB=0.25 nA2=1.45 nA3=1.55 nB3=1.55

// ---- recycling folded cascode core (d g s b) ----
M0   (ntail vbtail vdd  vdd) pch_mac w={p['w_tail']}u l={p['l_tail']}u
M1A  (nA    vinp  ntail vdd) pch_mac w={wh}u l={p['l_in']}u
M1B  (x2    vinp  ntail vdd) pch_mac w={wh}u l={p['l_in']}u
M2A  (nB    vinn  ntail vdd) pch_mac w={wh}u l={p['l_in']}u
M2B  (x1    vinn  ntail vdd) pch_mac w={wh}u l={p['l_in']}u
// recycling mirrors (cross-coupled): M2B->x1->MN1A@nA ; M1B->x2->MN2A@nB
// 1:K via K parallel UNIT devices (multi=K) -- same model bin, exact ratio
MN1B (x1    x1    0     0)   nch_mac w={p['w_mb']}u l={p['l_m']}u
MN1A (nA    x1    0     0)   nch_mac w={p['w_mb']}u l={p['l_m']}u multi={p['K']}
MN2B (x2    x2    0     0)   nch_mac w={p['w_mb']}u l={p['l_m']}u
MN2A (nB    x2    0     0)   nch_mac w={p['w_mb']}u l={p['l_m']}u multi={p['K']}
// cascodes + mirror tops (same as FC)
M5   (nA2   vbnc  nA    0)   nch_mac w={p['w_nc']}u l={p['l_nc']}u
M6   (out   vbnc  nB    0)   nch_mac w={p['w_nc']}u l={p['l_nc']}u
M7   (nA2   vbpc  nA3   vdd) pch_mac w={p['w_pc']}u l={p['l_pc']}u
M8   (out   vbpc  nB3   vdd) pch_mac w={p['w_pc']}u l={p['l_pc']}u
M9   (nA3   nA2   vdd   vdd) pch_mac w={p['w_pc']}u l={p['l_pc']}u
M10  (nB3   nA2   vdd   vdd) pch_mac w={p['w_pc']}u l={p['l_pc']}u
CL   (out 0) capacitor c={p['cl']}p

save out
opInfo info what=oppoint where=rawfile
ac ac start=1 stop=1G dec=40
"""


def db(z):
    return 20 * math.log10(abs(z)) if abs(z) > 0 else -400.0


def ph(z):
    return math.degrees(math.atan2(z.imag, z.real))


def run(p: dict, stim: str, tag: str | None = None):
    tag = tag or stim
    scs = HERE / f"otav2_{tag}.scs"
    scs.write_text(netlist(p, stim), encoding="utf-8")
    sim = SpectreSimulator.from_env(work_dir=str(HERE / "sim" / tag))
    res = sim.run_simulation(scs, {})
    d = res.data or {}
    f = [float(x.real) if isinstance(x, complex) else float(x)
         for x in d.get("ac_freq", [])]
    out = list(d.get("ac_out", []))
    if not f or not out:
        raise RuntimeError(f"{tag}: no AC data; errors={res.errors[:3]}")
    return f, out


def ac_metrics(f, vout):
    mag = [db(v) for v in vout]
    pha = [ph(v) for v in vout]
    a0 = mag[0]
    ugf = pm = None
    for i in range(1, len(mag)):
        if mag[i - 1] >= 0 >= mag[i]:
            t = mag[i - 1] / (mag[i - 1] - mag[i])
            ugf = f[i - 1] * (f[i] / f[i - 1]) ** t
            pm = 180 + (pha[i - 1] + t * (pha[i] - pha[i - 1]))
            break
    return dict(a0=a0, ugf=ugf, pm=pm, mag=mag, pha=pha)


def op_summary(tag: str, p: dict) -> dict:
    info = next((HERE / "sim" / tag).rglob("opInfo.info"), None)
    devs = parse_info(info) if info else {}
    itail = abs(devs.get("M0", {}).get("ids", 0))
    itot = itail + abs(devs.get("M9", {}).get("ids", 0)) \
                 + abs(devs.get("M10", {}).get("ids", 0))
    gmh = devs.get("M1A", {}).get("gm", 0)
    return dict(devs=devs, itail=itail, itot=itot, gm_half=gmh,
                gm_eff=(1 + p["K"]) * gmh)


def print_op(o: dict, m: dict, p: dict):
    print(f"\n  A0={m['a0']:.1f}dB  GBW={(m['ugf'] or 0)/1e6:.1f}MHz  "
          f"PM={m['pm']:.0f}deg" if m['ugf'] else f"  A0={m['a0']:.1f}dB  no UGF")
    print(f"  Itail={o['itail']*1e6:.3f}uA  Itot={o['itot']*1e6:.3f}uA  "
          f"P={o['itot']*1.8e6:.2f}uW  "
          f"gm_half={o['gm_half']*1e6:.2f}uS  Gm=(1+K)gm={o['gm_eff']*1e6:.1f}uS  "
          f"GBW_calc={o['gm_eff']/(2*math.pi*p['cl']*1e-12)/1e6:.1f}MHz")
    hdr = ("dev", "ID/uA", "gm/uS", "gm/ID", "Vdsat/mV", "Vds/mV", "reg")
    print("  " + "".join(f"{h:>9}" for h in hdr))
    for nm in ("M0", "M1A", "M1B", "MN1B", "MN1A", "M5", "M6", "M7", "M9"):
        x = o["devs"].get(nm)
        if not x:
            continue
        i = abs(x["ids"])
        sat = "SAT" if abs(x["vds"]) > abs(x["vdsat"]) + 0.005 else "LIN!"
        print("  " + f"{nm:>9}{i*1e6:9.3f}{x['gm']*1e6:9.2f}{x['gm']/i:9.1f}"
              f"{x['vdsat']*1e3:9.0f}{x['vds']*1e3:9.0f}{sat:>9}")


def apply_kv(p: dict, args: list[str]) -> list[str]:
    rest = []
    for a in args:
        if "=" in a:
            k, v = a.split("=", 1)
            if k not in p:
                raise SystemExit(f"unknown knob: {k} (knobs: {sorted(p)})")
            p[k] = type(P[k])(v) if not isinstance(P[k], int) else int(float(v))
        else:
            rest.append(a)
    return rest


def main():
    p = dict(P)
    args = apply_kv(p, sys.argv[1:])
    mode = args[0] if args else "diff"

    if mode == "diff":
        f, vout = run(p, "diff")
        m = ac_metrics(f, vout)
        o = op_summary("diff", p)
        print_op(o, m, p)

    elif mode == "sw":
        knob, vals = args[1], args[2:]
        print(f"  {knob:>8} {'A0/dB':>7} {'GBW/MHz':>8} {'PM/deg':>7} "
              f"{'Itot/uA':>8} {'P/uW':>6}")
        for v in vals:
            q = dict(p)
            apply_kv(q, [f"{knob}={v}"])
            try:
                f, vout = run(q, "diff", tag=f"sw_{knob}")
                m = ac_metrics(f, vout)
                o = op_summary(f"sw_{knob}", q)
                print(f"  {v:>8} {m['a0']:7.1f} "
                      f"{(m['ugf'] or 0)/1e6:8.1f} "
                      f"{(m['pm'] if m['pm'] is not None else float('nan')):7.0f} "
                      f"{o['itot']*1e6:8.3f} {o['itot']*1.8e6:6.2f}")
            except RuntimeError as e:
                print(f"  {v:>8}  FAILED: {e}")

    elif mode == "full":
        f, adm = run(p, "diff")
        _, add = run(p, "vdd")
        _, acm = run(p, "cm")
        m = ac_metrics(f, adm)
        o = op_summary("diff", p)
        psrr = [db(adm[i]) - db(add[i]) for i in range(len(f))]
        cmrr = [db(adm[i]) - db(acm[i]) for i in range(len(f))]
        print_op(o, m, p)
        print(f"  PSRR(DC)={psrr[0]:.0f}dB  CMRR(DC)={cmrr[0]:.0f}dB")
        devtab = {nm: {k: x[k] for k in ("ids", "gm", "gds", "vdsat", "vds")}
                  for nm, x in o["devs"].items()}
        (HERE / "ota_v2_char.json").write_text(json.dumps(dict(
            params=p, freq=f, mag_db=m["mag"], phase_deg=m["pha"],
            psrr_db=psrr, cmrr_db=cmrr,
            metrics=dict(a0=m["a0"], ugf=m["ugf"], pm=m["pm"],
                         itot=o["itot"], power=o["itot"] * 1.8,
                         gm_eff=o["gm_eff"], psrr_dc=psrr[0], cmrr_dc=cmrr[0]),
            devtab=devtab), indent=1), encoding="utf-8")
        print("  saved -> ota_v2_char.json")

    elif mode == "baseline":
        sys.path.insert(0, str(HERE.parent / "fc_ota"))
        import fc_ota
        scs = HERE / "fc_baseline.scs"
        scs.write_text(fc_ota.netlist(fc_ota.P, "diff"), encoding="utf-8")
        sim = SpectreSimulator.from_env(work_dir=str(HERE / "sim" / "fcbase"))
        res = sim.run_simulation(scs, {})
        d = res.data or {}
        f = [float(x.real) if isinstance(x, complex) else float(x)
             for x in d.get("ac_freq", [])]
        vout = list(d.get("ac_out", []))
        m = ac_metrics(f, vout)
        info = next((HERE / "sim" / "fcbase").rglob("opInfo.info"), None)
        devs = parse_info(info)
        itot = sum(abs(devs[k]["ids"]) for k in ("M0", "M9", "M10"))
        (HERE / "fc_baseline.json").write_text(json.dumps(dict(
            freq=f, mag_db=m["mag"], phase_deg=m["pha"],
            metrics=dict(a0=m["a0"], ugf=m["ugf"], pm=m["pm"], itot=itot,
                         power=itot * 1.8, gm_in=devs["M1"]["gm"])),
            indent=1), encoding="utf-8")
        print(f"  FC baseline: A0={m['a0']:.1f}dB GBW={m['ugf']/1e6:.1f}MHz "
              f"PM={m['pm']:.0f} Itot={itot*1e6:.2f}uA  -> fc_baseline.json")
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
