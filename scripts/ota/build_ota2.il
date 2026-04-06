; build_ota2.il
;
; 五管 OTA 独立构建脚本（完整版）
; 流程：放实例 → net label 连接 → 放 iopin symbol → dbCreateTerm 创建 port
;
; 调用：BuildOTA2("test" "OTA_test2")

procedure(BuildOTA2(libName cellName)
  prog((cv nmosMaster pmosMaster iopinMaster
        M1 M2 M3 M4 M5 pinMaster)

    ; 打开 cellview
    cv = dbOpenCellViewByType(libName cellName "schematic" "schematic" "a")
    unless(cv return(sprintf(nil "ERROR: 无法打开 %s/%s" libName cellName)))

    ; 打开 master symbol
    nmosMaster  = dbOpenCellView("tsmc18" "nmos2v_mac" "symbol")
    pmosMaster  = dbOpenCellView("tsmc18" "pmos2v_mac" "symbol")
    iopinMaster = dbOpenCellView("basic"  "iopin"      "symbol")
    unless(nmosMaster && pmosMaster && iopinMaster
      return("ERROR: 找不到所需 master"))

    ; ── 放置晶体管 ─────────────────────────────────────────────────────────────
    M1 = dbCreateInst(cv nmosMaster "M1" '(0.0    0.0   ) "R0")
    M2 = dbCreateInst(cv nmosMaster "M2" '(1.5    0.0   ) "R0")
    M3 = dbCreateInst(cv pmosMaster "M3" '(0.0    1.1875) "R0")
    M4 = dbCreateInst(cv pmosMaster "M4" '(1.5    1.1875) "R0")
    M5 = dbCreateInst(cv nmosMaster "M5" '(0.75  -1.25  ) "R0")

    ; ── net label 连接（wire stub + label，相同 label 自动成同一 net） ──────────
    _OtaLabelTerm(cv M1 "G" "VIN+")
    _OtaLabelTerm(cv M1 "D" "vmirror")
    _OtaLabelTerm(cv M1 "S" "tail")
    _OtaLabelTerm(cv M1 "B" "VSS")

    _OtaLabelTerm(cv M2 "G" "VIN-")
    _OtaLabelTerm(cv M2 "D" "VOUT")
    _OtaLabelTerm(cv M2 "S" "tail")
    _OtaLabelTerm(cv M2 "B" "VSS")

    _OtaLabelTerm(cv M3 "G" "vmirror")
    _OtaLabelTerm(cv M3 "D" "vmirror")
    _OtaLabelTerm(cv M3 "S" "VDD")
    _OtaLabelTerm(cv M3 "B" "VDD")

    _OtaLabelTerm(cv M4 "G" "vmirror")
    _OtaLabelTerm(cv M4 "D" "VOUT")
    _OtaLabelTerm(cv M4 "S" "VDD")
    _OtaLabelTerm(cv M4 "B" "VDD")

    _OtaLabelTerm(cv M5 "G" "IBIAS")
    _OtaLabelTerm(cv M5 "D" "tail")
    _OtaLabelTerm(cv M5 "S" "VSS")
    _OtaLabelTerm(cv M5 "B" "VSS")

    ; ── 用 schCreateWire 画显式连线 ───────────────────────────────────────────
    ; tail 节点：M1.S/M2.S 向下到 y=-0.6875，M5.D 向上到 y=-0.6875，横线汇聚
    schCreateWire(cv "route" "full" '((0.25 -0.1875) (0.25 -0.6875)) 0 0 0 nil nil)  ; M1.S 向下
    schCreateWire(cv "route" "full" '((1.75 -0.1875) (1.75 -0.6875)) 0 0 0 nil nil)  ; M2.S 向下
    schCreateWire(cv "route" "full" '((1.0  -1.0625) (1.0  -0.6875)) 0 0 0 nil nil)  ; M5.D 向上
    schCreateWire(cv "route" "full" '((0.25 -0.6875) (1.0  -0.6875)) 0 0 0 nil nil)  ; 左段横线
    schCreateWire(cv "route" "full" '((1.0  -0.6875) (1.75 -0.6875)) 0 0 0 nil nil)  ; 右段横线

    ; VDD 顶部连线：M3.S 和 M4.S 通过顶部横线相连
    schCreateWire(cv "route" "full" '((0.25  1.625 ) (1.75  1.625 )) 0 0 0 nil nil)  ; 顶部横线

    ; ── 用 schCreatePin 创建顶层端口 ──────────────────────────────────────────
    ; 正确方式：schCreatePin 第2个参数传 iopin master cellview（不能传 nil）
    ; schCreatePin 同时创建 pin symbol（显示正确名字）和 terminal
    pinMaster = dbOpenCellView("basic" "iopin" "symbol")
    schCreatePin(cv pinMaster "VDD"   "inputOutput" nil '(2.875 2.625 ) "R0")
    schCreatePin(cv pinMaster "VIN+"  "inputOutput" nil '(2.875 2.3125) "R0")
    schCreatePin(cv pinMaster "VIN-"  "inputOutput" nil '(2.875 2.0   ) "R0")
    schCreatePin(cv pinMaster "VOUT"  "inputOutput" nil '(2.875 1.625 ) "R0")
    schCreatePin(cv pinMaster "IBIAS" "inputOutput" nil '(2.875 1.3125) "R0")
    schCreatePin(cv pinMaster "VSS"   "inputOutput" nil '(2.875 1.0   ) "R0")

    ; ── 保存 ────────────────────────────────────────────────────────────────────
    dbSave(cv)

    return(sprintf(nil "完成: %s/%s  insts=%d nets=%d ports=%d"
      libName cellName
      length(cv~>instances)
      length(cv~>nets)
      length(cv~>terminals)))))
