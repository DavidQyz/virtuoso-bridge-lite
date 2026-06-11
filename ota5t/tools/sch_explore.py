from virtuoso_bridge import VirtuosoClient

c = VirtuosoClient.from_env()
for cell in ("nch_mac", "pch_mac"):
    r = c.execute_skill(
        f'mapcar(lambda((t) t~>name) '
        f'dbOpenCellView("tsmc18" "{cell}" "symbol")~>terminals)')
    print(cell, "terminals:", r.output, "| status", r.status)

print("\nschematic attrs:",
      [m for m in dir(c.schematic) if not m.startswith("_")])

# test lib existing cells
r = c.execute_skill('mapcar(lambda((x) x~>name) ddGetObj("test")~>cells)')
print("\ntest lib cells:", r.output)
