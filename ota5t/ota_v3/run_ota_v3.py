#!/usr/bin/env python3
"""
OTA_V3 — RFC first stage + Monticelli-style class-AB output stage.

Goal (user spec): drive capability / slew rate is the headline; stage-1 power
~= original FC system (~2.1uA); GBW secondary but maximized; swing near rail.

Architecture:
  Stage 1: recycling folded cascode (OTA_V2 core) scaled to (K+1)*Ib ~= 2.1uA.
           RFC also slews class-AB-ish (mirrors overdrive dynamically).
  Stage 2: push-pull common-source MP_O / MN_O. Class-AB quiescent set by an
           IDEAL floating level shifter V_AB between the two gates
           (Monticelli floating battery; a real chip uses a translinear
           loop -- modeled ideal here, noted in README).
  Comp:    Miller Cc + nulling Rz from OUT to stage-1 output.

Usage:
  .venv/Scripts/python.exe ota5t/ota_v3/run_ota_v3.py diff [k=v ...]
  .venv/Scripts/python.exe ota5t/ota_v3/run_ota_v3.py sw <knob> v1 v2 ... [k=v ...]
  .venv/Scripts/python.exe ota5t/ota_v3/run_ota_v3.py full [k=v ...]
  .venv/Scripts/python.exe ota5t/ota_v3/run_ota_v3.py slew [k=v ...]   # buffer step tran
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

P = dict(
    # stage 1: RFC at FC-like power: (K+1)*Ib ~ 2.1uA -> Ib=0.525, tail=1.05uA
    w_in=3.0,  l_in=1.0,
    w_tail=4.0, l_tail=1.0, vbtail=1.29,
    w_mb=0.22, l_m=0.35, K=3,
    w_nc=1.0,  l_nc=0.5, vbnc=0.90,
    w_pc=2.0,  l_pc=0.35, vbpc=0.95,
    # stage 2: class-AB push-pull (quiescent set by vab + sizes)
    w_on=2.0,  l_on=0.35,    # NMOS output device
    w_op=5.0,  l_op=0.35,    # PMOS output device
    vab=0.85,                # floating battery; gate-drive sum = 1.8-vab -> IQ~1.8uA
    # compensation: cmode=miller (Cc+Rz OUT->gn) or ahuja (Cc OUT->nB fold
    # node; comp current rides the cascode, freeing stage-1 from SR duty).
    # Miller final was 57.5MHz @ PM=62 but SR-capped at I1/Cc (~25-47 V/us).
    cmode="ahuja",
    cc=0.05,   rz=60.0,      # Miller cap (pF) + nulling R (kOhm, miller only)
    # operating point: feedback forces OUT = vcm+voff = 0.9V (mid-rail);
    # gn self-settles at push/pull equilibrium; IQ is set by vab + W ratios.
    vcm=0.30, voff=0.60, cl=0.05,
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


def core(p: dict) -> str:
    """Shared OTA_V3 core devices (stage1 + classAB stage2 + comp network)."""
    wh = p["w_in"] / 2.0
    if p["cmode"] == "miller":
        comp_block = (f"Cc   (out   ncz)  capacitor c={p['cc']}p\n"
                      f"Rz   (ncz   gn)   resistor r={p['rz']}k")
    else:  # ahuja: comp current rides the cascode via the fold node
        comp_block = (f"Cc   (out   ncz)  capacitor c={p['cc']}p\n"
                      f"Rz   (ncz   nB)   resistor r={p['rz']}k")
    return f"""
// ---- stage 1: recycling folded cascode (d g s b) ----
// NOTE input assignment: stage 2 inverts, so the DRIVEN input (vinp) sits on
// the M2 side and FEEDBACK (vinn) on the M1 side to keep overall fb negative.
M0   (ntail vbtail vdd  vdd) pch_mac w={p['w_tail']}u l={p['l_tail']}u
M1A  (nA    vinn  ntail vdd) pch_mac w={wh}u l={p['l_in']}u
M1B  (x2    vinn  ntail vdd) pch_mac w={wh}u l={p['l_in']}u
M2A  (nB    vinp  ntail vdd) pch_mac w={wh}u l={p['l_in']}u
M2B  (x1    vinp  ntail vdd) pch_mac w={wh}u l={p['l_in']}u
MN1B (x1    x1    0     0)   nch_mac w={p['w_mb']}u l={p['l_m']}u
MN1A (nA    x1    0     0)   nch_mac w={p['w_mb']}u l={p['l_m']}u multi={p['K']}
MN2B (x2    x2    0     0)   nch_mac w={p['w_mb']}u l={p['l_m']}u
MN2A (nB    x2    0     0)   nch_mac w={p['w_mb']}u l={p['l_m']}u multi={p['K']}
M5   (nA2   vbnc  nA    0)   nch_mac w={p['w_nc']}u l={p['l_nc']}u
M6   (gn    vbnc  nB    0)   nch_mac w={p['w_nc']}u l={p['l_nc']}u
M7   (nA2   vbpc  nA3   vdd) pch_mac w={p['w_pc']}u l={p['l_pc']}u
M8   (gp    vbpc  nB3   vdd) pch_mac w={p['w_pc']}u l={p['l_pc']}u
M9   (nA3   nA2   vdd   vdd) pch_mac w={p['w_pc']}u l={p['l_pc']}u
M10  (nB3   nA2   vdd   vdd) pch_mac w={p['w_pc']}u l={p['l_pc']}u
// ---- class-AB level shift: gp = gn + vab (ideal Monticelli battery) ----
Vab  (gp    gn)   vsource dc={p['vab']}
// ---- stage 2: push-pull common source ----
MN_O (out   gn    0     0)   nch_mac w={p['w_on']}u l={p['l_on']}u
MP_O (out   gp    vdd   vdd) pch_mac w={p['w_op']}u l={p['l_op']}u
// ---- compensation ({p['cmode']}) ----
{comp_block}
CL   (out   0)    capacitor c={p['cl']}p
"""


def netlist_ac(p: dict, stim: str = "diff") -> str:
    din = 1 if stim == "diff" else 0
    dvd = 1 if stim == "vdd" else 0
    dcm = 1 if stim == "cm" else 0
    return f"""// OTA_V3 RFC + class-AB, AC stim={stim}
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

// open-loop AC bias: DC short (L) + level shift -> stage-1 out (gn) ~ VGS(MN_O)
Lfb  (out  nls)  inductor l=1T
Voff (nls  vinn) vsource dc={p['voff']}
Cac  (vinn vincm) capacitor c=1T

nodeset out=0.9 nls=0.9 vinn={p['vcm']} ntail=0.85 x1=0.45 x2=0.45 \\
    nA=0.25 nB=0.25 nA2=1.45 nA3=1.55 nB3=1.55 gn=0.55 gp=1.25
{core(p)}
save out gn gp
opInfo info what=oppoint where=rawfile
ac ac start=1 stop=1G dec=40
"""


_SLEW_HDR = """simulator lang=spectre
global 0
include "{models}/c018bcd_gen2_v1d6_usage.scs" section=pre_simu
include "{models}/c018bcd_gen2_v1d6_usage.scs" section=tt_lib

Vdd   (vdd   0)     vsource dc=1.8
Vstep (vinp  0)     vsource type=pulse val0={v0} val1={v1} delay={tedge} \\
    rise=1n fall=1n width={tw}
Rfb   (out  vinn)   resistor r=1m
"""

_SLEW_TAIL = """save out vinp
tr tran stop={tstop} errpreset=conservative maxstep=200p
"""


def netlist_slew(p: dict, v0: float, v1: float, tedge: float, tw: float) -> str:
    """OTA_V3 unity-gain buffer step response."""
    hdr = _SLEW_HDR.format(models=MODELS, v0=v0, v1=v1, tedge=tedge, tw=tw)
    return (f"// OTA_V3 slew: buffer step {v0}->{v1}V\n" + hdr + f"""
Vbt   (vbtail 0)    vsource dc={p['vbtail']}
Vbnc  (vbnc  0)     vsource dc={p['vbnc']}
Vbpc  (vbpc  0)     vsource dc={p['vbpc']}
nodeset out={v0} vinn={v0} ntail=0.85 x1=0.45 x2=0.45 nA=0.25 nB=0.25 \\
    nA2=1.45 nA3=1.55 nB3=1.55 gn=0.55 gp=1.45
{core(p)}
""" + _SLEW_TAIL.format(tstop=tedge + 2 * tw))


def netlist_slew_fc(v0: float, v1: float, tedge: float, tw: float) -> str:
    """FC baseline (fc_ota final P) in the same buffer config."""
    hdr = _SLEW_HDR.format(models=MODELS, v0=v0, v1=v1, tedge=tedge, tw=tw)
    return ("// FC baseline slew: buffer step\n" + hdr + """
Vbt   (vbtail 0)    vsource dc=1.30
Vbn   (vbn   0)     vsource dc=0.52
Vbnc  (vbnc  0)     vsource dc=0.90
Vbpc  (vbpc  0)     vsource dc=0.95
nodeset out=0.65 vinn=0.65 ntail=1.6 nA2=1.5 nB2=1.5
M0  (ntail vbtail vdd  vdd)  pch_mac w=4u l=1u
M1  (nA    vinp  ntail vdd)  pch_mac w=3u l=1u
M2  (nB    vinn  ntail vdd)  pch_mac w=3u l=1u
M3  (nA    vbn   0     0)    nch_mac w=1u l=1u
M4  (nB    vbn   0     0)    nch_mac w=1u l=1u
M5  (nA2   vbnc  nA    0)    nch_mac w=1u l=0.5u
M6  (out   vbnc  nB    0)    nch_mac w=1u l=0.5u
M7  (nA2   vbpc  nA3   vdd)  pch_mac w=2u l=0.5u
M8  (out   vbpc  nB3   vdd)  pch_mac w=2u l=0.5u
M9  (nA3   nA2   vdd   vdd)  pch_mac w=2u l=0.5u
M10 (nB3   nA2   vdd   vdd)  pch_mac w=2u l=0.5u
CL  (out 0) capacitor c=50f
""" + _SLEW_TAIL.format(tstop=tedge + 2 * tw))


def netlist_slew_v2(v0: float, v1: float, tedge: float, tw: float) -> str:
    """OTA_V2 (RFC, final P) in the same buffer config."""
    hdr = _SLEW_HDR.format(models=MODELS, v0=v0, v1=v1, tedge=tedge, tw=tw)
    return ("// OTA_V2 slew: buffer step\n" + hdr + """
Vbt   (vbtail 0)    vsource dc=1.29
Vbnc  (vbnc  0)     vsource dc=0.90
Vbpc  (vbpc  0)     vsource dc=0.95
nodeset out=0.65 vinn=0.65 ntail=0.85 x1=0.45 x2=0.45 nA=0.25 nB=0.25 \\
    nA2=1.45 nA3=1.55 nB3=1.55
M0   (ntail vbtail vdd  vdd) pch_mac w=8u l=1u
M1A  (nA    vinp  ntail vdd) pch_mac w=1.5u l=1u
M1B  (x2    vinp  ntail vdd) pch_mac w=1.5u l=1u
M2A  (nB    vinn  ntail vdd) pch_mac w=1.5u l=1u
M2B  (x1    vinn  ntail vdd) pch_mac w=1.5u l=1u
MN1B (x1    x1    0     0)   nch_mac w=0.22u l=0.35u
MN1A (nA    x1    0     0)   nch_mac w=0.22u l=0.35u multi=3
MN2B (x2    x2    0     0)   nch_mac w=0.22u l=0.35u
MN2A (nB    x2    0     0)   nch_mac w=0.22u l=0.35u multi=3
M5   (nA2   vbnc  nA    0)   nch_mac w=1u l=0.5u
M6   (out   vbnc  nB    0)   nch_mac w=1u l=0.5u
M7   (nA2   vbpc  nA3   vdd) pch_mac w=2u l=0.35u
M8   (out   vbpc  nB3   vdd) pch_mac w=2u l=0.35u
M9   (nA3   nA2   vdd   vdd) pch_mac w=2u l=0.35u
M10  (nB3   nA2   vdd   vdd) pch_mac w=2u l=0.35u
CL   (out 0) capacitor c=50f
""" + _SLEW_TAIL.format(tstop=tedge + 2 * tw))


def db(z):
    return 20 * math.log10(abs(z)) if abs(z) > 0 else -400.0


def ph(z):
    return math.degrees(math.atan2(z.imag, z.real))


def run_scs(text: str, tag: str):
    scs = HERE / f"otav3_{tag}.scs"
    scs.write_text(text, encoding="utf-8")
    sim = SpectreSimulator.from_env(work_dir=str(HERE / "sim" / tag))
    return sim.run_simulation(scs, {})


def run_ac(p: dict, stim: str, tag: str | None = None):
    tag = tag or stim
    res = run_scs(netlist_ac(p, stim), tag)
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
    i1 = abs(devs.get("M0", {}).get("ids", 0)) \
        + abs(devs.get("M9", {}).get("ids", 0)) \
        + abs(devs.get("M10", {}).get("ids", 0))
    iq2 = abs(devs.get("MN_O", {}).get("ids", 0))
    return dict(devs=devs, i_stage1=i1, iq_out=iq2, itot=i1 + iq2,
                gm_half=devs.get("M1A", {}).get("gm", 0),
                gm2=devs.get("MN_O", {}).get("gm", 0)
                + devs.get("MP_O", {}).get("gm", 0))


def print_op(o: dict, m: dict, p: dict):
    print(f"  A0={m['a0']:.1f}dB  GBW={(m['ugf'] or 0)/1e6:.1f}MHz  "
          f"PM={(m['pm'] if m['pm'] is not None else float('nan')):.0f}deg")
    print(f"  stage1={o['i_stage1']*1e6:.2f}uA  IQ_out={o['iq_out']*1e6:.2f}uA  "
          f"Itot={o['itot']*1e6:.2f}uA  P={o['itot']*1.8e6:.2f}uW  "
          f"Gm1={(1+p['K'])*o['gm_half']*1e6:.1f}uS  gm2={o['gm2']*1e6:.1f}uS")
    hdr = ("dev", "ID/uA", "gm/uS", "gm/ID", "Vdsat/mV", "Vds/mV", "reg")
    print("  " + "".join(f"{h:>9}" for h in hdr))
    for nm in ("M0", "M1A", "MN1A", "M5", "M6", "M9", "MN_O", "MP_O"):
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
                raise SystemExit(f"unknown knob: {k}")
            p[k] = type(P[k])(v) if not isinstance(P[k], int) else int(float(v))
        else:
            rest.append(a)
    return rest


def _cross(t, v, th, tmin, rising):
    for i in range(1, len(t)):
        if t[i] < tmin:
            continue
        a, b = v[i - 1] - th, v[i] - th
        if (a < 0 <= b) if rising else (a > 0 >= b):
            return t[i - 1] + (t[i] - t[i - 1]) * (-a) / (b - a) if a != b else t[i]
    return None


def slew_both_edges(t, vout, v0, v1, t_edge, t_w):
    """10-90% SR for the rising edge (at t_edge) and falling (at t_edge+t_w)."""
    lo, hi = min(v0, v1), max(v0, v1)
    p10, p90 = lo + 0.1 * (hi - lo), lo + 0.9 * (hi - lo)
    ta = _cross(t, vout, p10, t_edge, True)
    tb = _cross(t, vout, p90, t_edge, True)
    sr_r = (p90 - p10) / (tb - ta) if (ta and tb and tb > ta) else None
    tc = _cross(t, vout, p90, t_edge + t_w, False)
    td = _cross(t, vout, p10, t_edge + t_w, False)
    sr_f = (p90 - p10) / (td - tc) if (tc and td and td > tc) else None
    return sr_r, sr_f


def main():
    p = dict(P)
    args = apply_kv(p, sys.argv[1:])
    mode = args[0] if args else "diff"

    if mode == "diff":
        f, vout = run_ac(p, "diff")
        m = ac_metrics(f, vout)
        o = op_summary("diff", p)
        print_op(o, m, p)

    elif mode == "sw":
        knob, vals = args[1], args[2:]
        print(f"  {knob:>8} {'A0/dB':>7} {'GBW/MHz':>8} {'PM/deg':>7} "
              f"{'Itot/uA':>8} {'IQout/uA':>9}")
        for v in vals:
            q = dict(p)
            apply_kv(q, [f"{knob}={v}"])
            try:
                f, vout = run_ac(q, "diff", tag=f"sw_{knob}")
                m = ac_metrics(f, vout)
                o = op_summary(f"sw_{knob}", q)
                print(f"  {v:>8} {m['a0']:7.1f} {(m['ugf'] or 0)/1e6:8.1f} "
                      f"{(m['pm'] if m['pm'] is not None else float('nan')):7.0f} "
                      f"{o['itot']*1e6:8.2f} {o['iq_out']*1e6:9.2f}")
            except RuntimeError as e:
                print(f"  {v:>8}  FAILED: {str(e)[:60]}")

    elif mode == "full":
        f, adm = run_ac(p, "diff")
        _, add = run_ac(p, "vdd")
        _, acm = run_ac(p, "cm")
        m = ac_metrics(f, adm)
        o = op_summary("diff", p)
        psrr = [db(adm[i]) - db(add[i]) for i in range(len(f))]
        cmrr = [db(adm[i]) - db(acm[i]) for i in range(len(f))]
        print_op(o, m, p)
        print(f"  PSRR(DC)={psrr[0]:.0f}dB  CMRR(DC)={cmrr[0]:.0f}dB")
        (HERE / "ota_v3_char.json").write_text(json.dumps(dict(
            params=p, freq=f, mag_db=m["mag"], phase_deg=m["pha"],
            psrr_db=psrr, cmrr_db=cmrr,
            metrics=dict(a0=m["a0"], ugf=m["ugf"], pm=m["pm"],
                         i_stage1=o["i_stage1"], iq_out=o["iq_out"],
                         itot=o["itot"], power=o["itot"] * 1.8,
                         psrr_dc=psrr[0], cmrr_dc=cmrr[0])), indent=1),
            encoding="utf-8")
        print("  saved -> ota_v3_char.json")

    elif mode == "slewall":
        # 3-way slew shootout: FC / OTA_V2 / OTA_V3 in the same buffer config.
        # Step window 0.35-0.95V: inside FC/V2 cascode output compliance AND
        # PMOS input CM range, so the comparison is fair to all three.
        v0, v1, t_edge, t_w = 0.35, 0.95, 20e-9, 400e-9
        gens = [("fc",  netlist_slew_fc(v0, v1, t_edge, t_w)),
                ("v2",  netlist_slew_v2(v0, v1, t_edge, t_w)),
                ("v3",  netlist_slew(p, v0, v1, t_edge, t_w))]
        result = dict(v0=v0, v1=v1, t_edge=t_edge, t_width=t_w, traces={})
        for name, text in gens:
            res = run_scs(text, f"slew_{name}")
            d = res.data or {}
            t = [float(x) for x in d.get("time", [])]
            vo = [float(x) for x in d.get("out", [])]
            if not t:
                print(f"  {name}: NO TRAN DATA {res.errors[:2]}")
                continue
            sr_r, sr_f = slew_both_edges(t, vo, v0, v1, t_edge, t_w)
            result["traces"][name] = dict(time=t, out=vo, sr_rise=sr_r,
                                          sr_fall=sr_f)
            print(f"  {name}: SR+ ={sr_r/1e6 if sr_r else 0:8.1f} V/us   "
                  f"SR- ={sr_f/1e6 if sr_f else 0:8.1f} V/us")
        (HERE / "ota_v3_slew.json").write_text(json.dumps(result, indent=1),
                                               encoding="utf-8")
        print("  saved -> ota_v3_slew.json")
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
