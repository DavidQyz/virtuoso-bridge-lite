from virtuoso_bridge import VirtuosoClient
from virtuoso_bridge.virtuoso.schematic import ops

LIB, CELL = "test", "OTA_5T"

# show generated SKILL for each op type
print("=== INST ===")
print(ops.schematic_create_inst_by_master_name("tsmc18", "nch_mac", "symbol", "M1", 0, 0, "R0"))
print("=== PIN (input) ===")
print(ops.schematic_create_pin("VINP", -5, 0, "R0", direction="input"))
print("=== label term (single) ===")
try:
    print(ops.schematic_label_instance_term("M1", "G", "VINP"))
except Exception as e:
    print("err:", e)

# test instance creation alone
c = VirtuosoClient.from_env()
c.execute_skill(f'when(ddGetObj("{LIB}" "{CELL}") ddDeleteObj(ddGetObj("{LIB}" "{CELL}")))')
inst = ops.schematic_create_inst_by_master_name("tsmc18", "nch_mac", "symbol", "M1", 0, 0, "R0")
skill = (f'let((cv) cv=dbOpenCellViewByType("{LIB}" "{CELL}" "schematic" "schematic" "a") '
         f'{inst} schCheck(cv) dbSave(cv) sprintf(nil "%L" cv~>instances))')
r = c.execute_skill(skill, timeout=30)
print("\n=== place M1 ===")
print("status:", r.status, "| out:", r.output, "| err:", r.errors[:2])

# now test add_net_label_to_transistor via the editor's method generator
# (inspect what the editor does)
print("\n=== editor add_net_label_to_transistor source signature ===")
import inspect
from virtuoso_bridge.virtuoso.schematic.editor import SchematicEditor
print([m for m in dir(SchematicEditor) if not m.startswith("__")])
