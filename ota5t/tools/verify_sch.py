from virtuoso_bridge import VirtuosoClient
c = VirtuosoClient.from_env()
LIB, CELL = "test", "OTA_5T"

# net -> connected instance terminals
r = c.execute_skill(f'''
let((cv)
  cv=dbOpenCellViewByType("{LIB}" "{CELL}" "schematic" "schematic" "r")
  mapcar(lambda((n)
    list(n~>name sort(mapcar(lambda((it) strcat(it~>inst~>name "." it~>name)) n~>instTerms) 'alphalessp)))
    cv~>nets))
''', timeout=25)
print("=== NET CONNECTIVITY ===")
print(r.output)

# instance sizes (w,l,fingers)
r2 = c.execute_skill(f'''
let((cv)
  cv=dbOpenCellViewByType("{LIB}" "{CELL}" "schematic" "schematic" "r")
  mapcar(lambda((i) list(i~>name i~>cellName i~>w i~>l)) cv~>instances))
''', timeout=25)
print("\n=== INSTANCE SIZES (name cell w l) ===")
print(r2.output)

# schCheck status
r3 = c.execute_skill(f'''
let((cv n) cv=dbOpenCellViewByType("{LIB}" "{CELL}" "schematic" "schematic" "a")
  n=schCheck(cv) sprintf(nil "schCheck warnings/errors: %L" n))
''', timeout=25)
print("\n=== schCheck ===")
print(r3.output)
