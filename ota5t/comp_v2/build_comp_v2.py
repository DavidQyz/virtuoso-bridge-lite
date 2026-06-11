#!/usr/bin/env python3
"""
Build the V2 comparator schematic in library `test`, cell `COMP_V2`.

vs test/COMP_CG (V4):
  + MCL  nmos5v pass-clamp (D=COMP_OUT, G=VDD, S=YC): YC = min(comp_out, ~1V)
  + M5B  nmos2v (G=YC) -- low-threshold (0.45V) early-fire pull-down on MID
  ~ M5   nmos5v single finger 220n (was 0.88u eff) -- late-overdrive path,
         shrunk to minimize comp_out capacitance (the tprop-defining node)
  - INV1 5V pair as a stage is replaced by the dual pull-down + M6 reset
  (M6/M20/M21 and the whole front end unchanged)

Performance (tt): tprop 0.923ns @ INN=1V / 8.74uW (V4: 1.015ns / 8.75uW);
floor 0.61-0.67ns at INN>=1.5V; all 49 INN points 0.1-4.9V functional.

Run:
    .venv/Scripts/python.exe ota5t/comp_v2/build_comp_v2.py
"""
from virtuoso_bridge import VirtuosoClient
from virtuoso_bridge.virtuoso.schematic import (
    schematic_create_inst_by_master_name as inst,
    schematic_create_pin as pin,
)
from virtuoso_bridge.virtuoso.schematic.ops import schematic_label_instance_term
from virtuoso_bridge.virtuoso.schematic.params import set_instance_params

LIB, CELL = "test", "COMP_V2"
c = VirtuosoClient.from_env()

c.execute_skill(
    f'when(ddGetObj("{LIB}" "{CELL}") ddDeleteObj(ddGetObj("{LIB}" "{CELL}")))')

MOS = [
    ("pmos5v_mac", "M10", -6,  9),
    ("pmos5v_mac", "M11", -6,  3),
    ("pmos5v_mac", "M1",   0,  8),
    ("pmos5v_mac", "M0",   6,  8),
    ("nmos5v_mac", "M3",   0,  2),
    ("nmos5v_mac", "M2",   6,  2),
    ("nmos2v_mac", "M22", 12,  4),
    ("nmos2v_mac", "M9",  12, -2),
    ("nmos5v_mac", "MCL", 15,  8),
    ("pmos5v_mac", "M6",  18,  8),
    ("nmos5v_mac", "M5",  18,  2),
    ("nmos2v_mac", "M5B", 21,  2),
    ("pmos2v_mac", "M21", 24,  8),
    ("nmos2v_mac", "M20", 24,  2),
]

# name -> (D, G, S, B)
CONN = {
    "M0":  ("COMP_OUT", "net78",    "INP",  "V_BB"),
    "M1":  ("net78",    "net78",    "INN",  "V_BB"),
    "M10": ("V_BB",     "V_BB",     "INN",  "V_BB"),
    "M11": ("V_BB",     "V_BB",     "INP",  "V_BB"),
    "M2":  ("COMP_OUT", "V_BN",     "VSS",  "VSS"),
    "M3":  ("net78",    "V_BN",     "VSS",  "VSS"),
    "M9":  ("V_BN",     "N_EN",     "VSS",  "VSS"),
    "M22": ("COMP_VCM", "EN",       "V_BN", "VSS"),
    "MCL": ("COMP_OUT", "VDD",      "YC",   "VSS"),
    "M5":  ("MID",      "COMP_OUT", "VSS",  "VSS"),
    "M5B": ("MID",      "YC",       "VSS",  "VSS"),
    "M6":  ("MID",      "COMP_OUT", "VDD",  "VDD"),
    "M20": ("OUT",      "MID",      "VSS",  "VSS"),
    "M21": ("OUT",      "MID",      "VDD",  "VDD"),
}

with c.schematic.edit(LIB, CELL) as sch:
    for cell, name, x, y in MOS:
        sch.add(inst("tsmc18", cell, "symbol", name, x, y, "R0"))
    sch.add(inst("test_rect", "DBB1", "symbol", "I3", -12, 6, "R0"))

    for name, (d, g, s, b) in CONN.items():
        sch.add_net_label_to_transistor(name, drain_net=d, gate_net=g,
                                        source_net=s, body_net=b)
    sch.add(schematic_label_instance_term("I3", "IN1", "INP"))
    sch.add(schematic_label_instance_term("I3", "IN2", "INN"))
    sch.add(schematic_label_instance_term("I3", "OUT", "V_BB"))

    sch.add(pin("INP",      -16, 12, "R0", direction="input"))
    sch.add(pin("INN",      -16, 11, "R0", direction="input"))
    sch.add(pin("EN",        12,  9, "R0", direction="input"))
    sch.add(pin("N_EN",      12, -6, "R0", direction="input"))
    sch.add(pin("OUT",       28,  5, "R0", direction="output"))
    sch.add(pin("VDD",        6, 14, "R0", direction="inputOutput"))
    sch.add(pin("VSS",        6, -8, "R0", direction="inputOutput"))
    sch.add(pin("COMP_VCM",  16, 12, "R0", direction="inputOutput"))

print("[1] instances + labels + pins placed")

c.open_window(LIB, CELL, view="schematic")
print("[2] GUI window opened")

# CDF sizing (w = per-finger). Spectre-netlist equivalents in run_comp_v2.py.
SIZING = {
    "M0":  dict(w="500n", nf="4"),
    "M1":  dict(w="500n", nf="4"),
    "M10": dict(w="500n", simM="2"),
    "M11": dict(w="500n", simM="2"),
    "M2":  dict(w="220n"),
    "M3":  dict(w="220n"),
    "MCL": dict(w="220n"),
    "M5":  dict(w="220n"),
    "M5B": dict(w="220n", l="180n"),
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
