#!/usr/bin/env python3
"""
Build the 5-transistor OTA schematic in library `test`, cell `OTA_5T`.
Connectivity by net labels (same name = same net). Sizes set per instance.

Topology (NMOS input pair / PMOS mirror load / NMOS tail):
    M1 nch_mac  D=VX    G=VINP  S=VTAIL B=VSS   W=3u  L=1u
    M2 nch_mac  D=VOUT  G=VINN  S=VTAIL B=VSS   W=3u  L=1u
    M3 pch_mac  D=VX    G=VX    S=VDD   B=VDD   W=6u  L=1u   (diode)
    M4 pch_mac  D=VOUT  G=VX    S=VDD   B=VDD   W=6u  L=1u
    M5 nch_mac  D=VTAIL G=VBIAS S=VSS   B=VSS   W=5u  L=1u
Pins: VINP(in) VINN(in) VOUT(out) VBIAS(in) VDD(io) VSS(io)

Run (venv python directly to avoid uv lock):
    .venv/Scripts/python.exe ota5t/build_ota.py
"""
from virtuoso_bridge import VirtuosoClient
from virtuoso_bridge.virtuoso.schematic import (
    schematic_create_inst_by_master_name as inst,
    schematic_create_pin as pin,
)
from virtuoso_bridge.virtuoso.schematic.params import set_instance_params

LIB, CELL = "test", "OTA_5T"
c = VirtuosoClient.from_env()

# clean rebuild
c.execute_skill(
    f'when(ddGetObj("{LIB}" "{CELL}") ddDeleteObj(ddGetObj("{LIB}" "{CELL}")))')

with c.schematic.edit(LIB, CELL) as sch:
    # --- place instances (lib, cell, view, name, x, y, orient) ---
    sch.add(inst("tsmc18", "nmos2v_mac", "symbol", "M1", 0,  0, "R0"))
    sch.add(inst("tsmc18", "nmos2v_mac", "symbol", "M2", 8,  0, "R0"))
    sch.add(inst("tsmc18", "pmos2v_mac", "symbol", "M3", 0,  6, "R0"))
    sch.add(inst("tsmc18", "pmos2v_mac", "symbol", "M4", 8,  6, "R0"))
    sch.add(inst("tsmc18", "nmos2v_mac", "symbol", "M5", 4, -6, "R0"))
    # --- connectivity via MOS-aware net labels (D, G, S, B) ---
    sch.add_net_label_to_transistor("M1", drain_net="VX",   gate_net="VINP",
                                    source_net="VTAIL", body_net="VSS")
    sch.add_net_label_to_transistor("M2", drain_net="VOUT", gate_net="VINN",
                                    source_net="VTAIL", body_net="VSS")
    sch.add_net_label_to_transistor("M3", drain_net="VX",   gate_net="VX",
                                    source_net="VDD",   body_net="VDD")
    sch.add_net_label_to_transistor("M4", drain_net="VOUT", gate_net="VX",
                                    source_net="VDD",   body_net="VDD")
    sch.add_net_label_to_transistor("M5", drain_net="VTAIL", gate_net="VBIAS",
                                    source_net="VSS",   body_net="VSS")
    # --- top-level pins (name-matched to nets) ---
    sch.add(pin("VINP",  -5,  0, "R0", direction="input"))
    sch.add(pin("VINN",  13,  0, "R0", direction="input"))
    sch.add(pin("VOUT",  13,  6, "R0", direction="output"))
    sch.add(pin("VBIAS", -3, -6, "R0", direction="input"))
    sch.add(pin("VDD",    4, 11, "R0", direction="inputOutput"))
    sch.add(pin("VSS",    4,-11, "R0", direction="inputOutput"))

print("[1] instances + labels + pins placed (schCheck+dbSave done on exit)")

# open GUI so geGetEditCellView() resolves for param setting
c.open_window(LIB, CELL, view="schematic")
print("[2] GUI window opened")

# set per-instance sizes (nf=1 default -> only w/l)
for name, w, l in [("M1", "3u", "1u"), ("M2", "3u", "1u"),
                   ("M3", "6u", "1u"), ("M4", "6u", "1u"),
                   ("M5", "5u", "1u")]:
    set_instance_params(c, name, w=w, l=l, param_filters=None)
    print(f"[3] sized {name}: W={w} L={l}")

print("DONE: test/OTA_5T built")
