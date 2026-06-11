#!/usr/bin/env python3
"""
Build the common-gate comparator schematic in library `test`, cell `COMP_CG`.
Faithful replica of test_rect/comparator_newV4_for_use_nb (same instance
names, same connectivity, same CDF sizing) so the netlists can be diffed.

Topology (from live V4 netlist, incl. body-bias network):
    M0  pmos5v_mac D=COMP_OUT G=net78    S=INP  B=V_BB  w=500n fingers=4
    M1  pmos5v_mac D=net78    G=net78    S=INN  B=V_BB  w=500n fingers=4  (diode)
    M10 pmos5v_mac D=V_BB     G=V_BB     S=INN  B=V_BB  w=500n simM=2
    M11 pmos5v_mac D=V_BB     G=V_BB     S=INP  B=V_BB  w=500n simM=2
    M2  nmos5v_mac D=COMP_OUT G=V_BN     S=VSS  B=VSS   w=220n
    M3  nmos5v_mac D=net78    G=V_BN     S=VSS  B=VSS   w=220n
    M5  nmos5v_mac D=MID_INV  G=COMP_OUT S=VSS  B=VSS   w=220n fingers=2 simM=2
    M6  pmos5v_mac D=MID_INV  G=COMP_OUT S=VDD  B=VDD   w=220n
    M9  nmos2v_mac D=V_BN     G=N_EN     S=VSS  B=VSS   w=220n l=180n
    M20 nmos2v_mac D=OUT      G=MID_INV  S=VSS  B=VSS   w=220n l=180n
    M21 pmos2v_mac D=OUT      G=MID_INV  S=VDD  B=VDD   w=880n l=180n
    M22 nmos2v_mac D=COMP_VCM G=EN       S=V_BN B=VSS   w=220n l=180n
    I3  test_rect/DBB1 (symbol)  IN1=INP IN2=INN OUT=V_BB  (n-well max-selector)

L defaults (not set explicitly, same as V4): pmos5v 500n, nmos5v 600n, 2v 180n.

Pins: INP INN EN N_EN (input), OUT (output), VDD VSS COMP_VCM (inputOutput).
V_BB / V_BN / net78 / COMP_OUT / MID_INV are internal nets.

Run:
    .venv/Scripts/python.exe ota5t/comp_cg/build_comp.py
"""
from virtuoso_bridge import VirtuosoClient
from virtuoso_bridge.virtuoso.schematic import (
    schematic_create_inst_by_master_name as inst,
    schematic_create_pin as pin,
)
from virtuoso_bridge.virtuoso.schematic.ops import schematic_label_instance_term
from virtuoso_bridge.virtuoso.schematic.params import set_instance_params

LIB, CELL = "test", "COMP_CG"
c = VirtuosoClient.from_env()

# clean rebuild
c.execute_skill(
    f'when(ddGetObj("{LIB}" "{CELL}") ddDeleteObj(ddGetObj("{LIB}" "{CELL}")))')

# (cell, name, x, y) — generous grid so label stubs never collide
MOS = [
    ("pmos5v_mac", "M10", -6,  9),
    ("pmos5v_mac", "M11", -6,  3),
    ("pmos5v_mac", "M1",   0,  8),
    ("pmos5v_mac", "M0",   6,  8),
    ("nmos5v_mac", "M3",   0,  2),
    ("nmos5v_mac", "M2",   6,  2),
    ("nmos2v_mac", "M22", 12,  4),
    ("nmos2v_mac", "M9",  12, -2),
    ("pmos5v_mac", "M6",  18,  8),
    ("nmos5v_mac", "M5",  18,  2),
    ("pmos2v_mac", "M21", 24,  8),
    ("nmos2v_mac", "M20", 24,  2),
]

# name -> (D, G, S, B) nets, exact V4 connectivity
CONN = {
    "M0":  ("COMP_OUT", "net78",    "INP",  "V_BB"),
    "M1":  ("net78",    "net78",    "INN",  "V_BB"),
    "M10": ("V_BB",     "V_BB",     "INN",  "V_BB"),
    "M11": ("V_BB",     "V_BB",     "INP",  "V_BB"),
    "M2":  ("COMP_OUT", "V_BN",     "VSS",  "VSS"),
    "M3":  ("net78",    "V_BN",     "VSS",  "VSS"),
    "M5":  ("MID_INV",  "COMP_OUT", "VSS",  "VSS"),
    "M6":  ("MID_INV",  "COMP_OUT", "VDD",  "VDD"),
    "M9":  ("V_BN",     "N_EN",     "VSS",  "VSS"),
    "M20": ("OUT",      "MID_INV",  "VSS",  "VSS"),
    "M21": ("OUT",      "MID_INV",  "VDD",  "VDD"),
    "M22": ("COMP_VCM", "EN",       "V_BN", "VSS"),
}

with c.schematic.edit(LIB, CELL) as sch:
    for cell, name, x, y in MOS:
        sch.add(inst("tsmc18", cell, "symbol", name, x, y, "R0"))
    sch.add(inst("test_rect", "DBB1", "symbol", "I3", -12, 6, "R0"))

    for name, (d, g, s, b) in CONN.items():
        sch.add_net_label_to_transistor(name, drain_net=d, gate_net=g,
                                        source_net=s, body_net=b)
    # DBB1 block terminals (geometric stubs)
    sch.add(schematic_label_instance_term("I3", "IN1", "INP"))
    sch.add(schematic_label_instance_term("I3", "IN2", "INN"))
    sch.add(schematic_label_instance_term("I3", "OUT", "V_BB"))

    # top-level pins (name-matched to nets)
    sch.add(pin("INP",      -16, 12, "R0", direction="input"))
    sch.add(pin("INN",      -16, 11, "R0", direction="input"))
    sch.add(pin("EN",        12,  9, "R0", direction="input"))
    sch.add(pin("N_EN",      12, -6, "R0", direction="input"))
    sch.add(pin("OUT",       28,  5, "R0", direction="output"))
    sch.add(pin("VDD",        6, 14, "R0", direction="inputOutput"))
    sch.add(pin("VSS",        6, -8, "R0", direction="inputOutput"))
    sch.add(pin("COMP_VCM",  16, 12, "R0", direction="inputOutput"))

print("[1] instances + labels + pins placed (schCheck+dbSave done on exit)")

# open GUI so geGetEditCellView() resolves for param setting
c.open_window(LIB, CELL, view="schematic")
print("[2] GUI window opened")

# CDF sizing copied verbatim from V4 (totalM = fingers x simM is derived)
SIZING = {
    "M0":  dict(w="500n", nf="4"),
    "M1":  dict(w="500n", nf="4"),
    "M10": dict(w="500n", simM="2"),
    "M11": dict(w="500n", simM="2"),
    "M2":  dict(w="220n"),
    "M3":  dict(w="220n"),
    "M5":  dict(w="220n", nf="2", simM="2"),
    "M6":  dict(w="220n"),
    "M9":  dict(w="220n", l="180n"),
    "M20": dict(w="220n", l="180n"),
    "M21": dict(w="880n", l="180n"),
    "M22": dict(w="220n", l="180n"),
}
for name, kw in SIZING.items():
    set_instance_params(c, name, param_filters=None, **kw)
    print(f"[3] sized {name}: {kw}")

print(f"DONE: {LIB}/{CELL} built")
