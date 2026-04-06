; build_ota.il
;
; 五管 OTA Schematic 构建脚本（SKILL 版本）
;
; 拓扑（NMOS 输入对，tsmc18 工艺）：
;   M1, M2 : NMOS 差分输入对   (nmos2v_mac)
;   M3, M4 : PMOS 电流镜负载   (pmos2v_mac)
;   M5     : NMOS 尾电流源     (nmos2v_mac)
;
; 端口：VIN+, VIN-, VDD, VSS, IBIAS, VOUT
;
; 调用方式（在 Virtuoso CIW 中）：
;   load("/path/to/build_ota.il")
;   BuildOTA("test" "OTA_test")
;
; 或通过 Python：
;   client.load_il("scripts/ota/build_ota.il")
;   client.execute_skill('BuildOTA("test" "OTA_test")')

procedure(BuildOTA(libName cellName)
  prog((cv nmosMaster pmosMaster
        M1 M2 M3 M4 M5)

    ; ── 打开（或新建）schematic cellview ──────────────────────────────────────
    cv = dbOpenCellViewByType(libName cellName "schematic" "schematic" "a")
    unless(cv
      return(sprintf(nil "ERROR: 无法打开 %s/%s/schematic" libName cellName)))

    ; ── 打开 master symbol ──────────────────────────────────────────────────
    nmosMaster = dbOpenCellView("tsmc18" "nmos2v_mac" "symbol")
    pmosMaster = dbOpenCellView("tsmc18" "pmos2v_mac" "symbol")
    unless(nmosMaster && pmosMaster
      return("ERROR: 找不到 tsmc18 中的 nmos2v_mac 或 pmos2v_mac"))

    ; ── 放置5个晶体管实例 ─────────────────────────────────────────────────────
    ;  布局：
    ;    M3(PMOS) @ (0,4)      M4(PMOS) @ (4,4)
    ;    M1(NMOS) @ (0,0)      M2(NMOS) @ (4,0)
    ;              M5(NMOS) @ (2,-4)

    M1 = dbCreateInst(cv nmosMaster "M1" '(0.0  0.0) "R0")
    M2 = dbCreateInst(cv nmosMaster "M2" '(4.0  0.0) "R0")
    M3 = dbCreateInst(cv pmosMaster "M3" '(0.0  4.0) "R0")
    M4 = dbCreateInst(cv pmosMaster "M4" '(4.0  4.0) "R0")
    M5 = dbCreateInst(cv nmosMaster "M5" '(2.0 -4.0) "R0")

    ; ── 给每个 terminal 打 net 标签（建立连接） ────────────────────────────────
    ; 说明：schCreateWireLabel 在 terminal 附近放一个 net 名称标签，
    ;       同名标签的 terminal 在 Virtuoso 中自动连接。

    ; M1 (NMOS 差分对，正输入)
    _OtaLabelTerm(cv M1 "G" "VIN+")
    _OtaLabelTerm(cv M1 "D" "vmirror")
    _OtaLabelTerm(cv M1 "S" "tail")
    _OtaLabelTerm(cv M1 "B" "VSS")

    ; M2 (NMOS 差分对，负输入)
    _OtaLabelTerm(cv M2 "G" "VIN-")
    _OtaLabelTerm(cv M2 "D" "VOUT")
    _OtaLabelTerm(cv M2 "S" "tail")
    _OtaLabelTerm(cv M2 "B" "VSS")

    ; M3 (PMOS 电流镜，二极管连接)
    _OtaLabelTerm(cv M3 "G" "vmirror")   ; Gate = Drain（二极管连接）
    _OtaLabelTerm(cv M3 "D" "vmirror")
    _OtaLabelTerm(cv M3 "S" "VDD")
    _OtaLabelTerm(cv M3 "B" "VDD")

    ; M4 (PMOS 电流镜，输出侧)
    _OtaLabelTerm(cv M4 "G" "vmirror")   ; Gate 镜像 M3
    _OtaLabelTerm(cv M4 "D" "VOUT")
    _OtaLabelTerm(cv M4 "S" "VDD")
    _OtaLabelTerm(cv M4 "B" "VDD")

    ; M5 (NMOS 尾电流源)
    _OtaLabelTerm(cv M5 "G" "IBIAS")
    _OtaLabelTerm(cv M5 "D" "tail")
    _OtaLabelTerm(cv M5 "S" "VSS")
    _OtaLabelTerm(cv M5 "B" "VSS")

    ; ── 添加顶层端口 ───────────────────────────────────────────────────────────
    ; 正确方式：schCreatePin 第2个参数传 iopin master（不能传 nil）
    ; 这样 pin 显示正确的名字（如 VSS），而不是 "iopin"
    let((pinMaster)
      pinMaster = dbOpenCellView("basic" "iopin" "symbol")
      schCreatePin(cv pinMaster "VIN+"  "inputOutput" nil '(-2.0  0.0) "R0")
      schCreatePin(cv pinMaster "VIN-"  "inputOutput" nil '( 6.0  0.0) "R0")
      schCreatePin(cv pinMaster "VDD"   "inputOutput" nil '( 2.0  7.0) "R0")
      schCreatePin(cv pinMaster "VSS"   "inputOutput" nil '( 2.0 -7.0) "R0")
      schCreatePin(cv pinMaster "IBIAS" "inputOutput" nil '(-2.0 -4.0) "R0")
      schCreatePin(cv pinMaster "VOUT"  "inputOutput" nil '( 6.0  4.0) "R0"))

    ; ── 保存 ────────────────────────────────────────────────────────────────────
    dbSave(cv)

    sprintf(nil "OTA构建完成: %s/%s  insts=%d nets=%d terms=%d"
            libName cellName
            length(cv~>instances)
            length(cv~>nets)
            length(cv~>terminals))))


; ── 辅助函数：在 terminal 处放置 net label（带 wire stub） ────────────────────
; 参数：cv = cellview, inst = instance, termName = terminal名, netName = net名
; 原理：找到 terminal 的 pin 图形中心，向外延伸 0.25 格，放 wire + label

procedure(_OtaLabelTerm(cv inst termName netName)
  prog((mterm mpin mfig localBBox localCtr ctr
        instBBox instCtr dx dy masterName isMos isPmos
        termNameUp localDir dirPt stubEnd mid)

    ; 找 terminal 对象
    mterm = car(setof(x inst~>master~>terminals x~>name == termName))
    unless(mterm return(nil))

    mpin = car(mterm~>pins)
    mfig = when(mpin car(mpin~>figs))
    unless(mfig return(nil))

    ; 计算 terminal 中心（转换到全局坐标）
    localBBox = mfig~>bBox
    localCtr  = list(
                  (xCoord(car(localBBox)) + xCoord(cadr(localBBox))) / 2.0
                  (yCoord(car(localBBox)) + yCoord(cadr(localBBox))) / 2.0)
    ctr = dbTransformPoint(localCtr inst~>transform)

    ; 对 MOS 管按 terminal 类型确定 stub 延伸方向
    masterName = lowerCase(inst~>master~>cellName)
    isMos  = rexMatchp("nch" masterName) || rexMatchp("nmos" masterName) ||
             rexMatchp("pch" masterName) || rexMatchp("pmos" masterName)
    isPmos = rexMatchp("pch" masterName) || rexMatchp("pmos" masterName)
    termNameUp = upperCase(termName)

    localDir = when(isMos
      cond(
        (termNameUp == "G" '(-0.25  0.0))
        (termNameUp == "D" if(isPmos '(0.0 -0.25) '(0.0  0.25)))
        (termNameUp == "S" if(isPmos '(0.0  0.25) '(0.0 -0.25)))
        (termNameUp == "B" '( 0.25  0.0))
        (t nil)))

    ; 如果不是 MOS 或未识别，则按几何方向延伸
    unless(localDir
      instBBox = dbTransformBBox(inst~>master~>bBox inst~>transform)
      instCtr  = list(
                   (xCoord(car(instBBox)) + xCoord(cadr(instBBox))) / 2.0
                   (yCoord(car(instBBox)) + yCoord(cadr(instBBox))) / 2.0)
      dx = xCoord(ctr) - xCoord(instCtr)
      dy = yCoord(ctr) - yCoord(instCtr)
      localDir = if(abs(dx) >= abs(dy)
                   list(if(dx >= 0 0.25 -0.25) 0.0)
                   list(0.0 if(dy >= 0 0.25 -0.25))))

    ; 计算 stub 终点
    dirPt   = dbTransformPoint(localDir inst~>transform)
    stubEnd = list(
                xCoord(ctr) + (xCoord(dirPt) - xCoord(dbTransformPoint('(0.0 0.0) inst~>transform)))
                yCoord(ctr) + (yCoord(dirPt) - yCoord(dbTransformPoint('(0.0 0.0) inst~>transform))))

    ; 画 wire stub
    schCreateWire(cv "route" "full" list(ctr stubEnd) 0 0 0 nil nil)

    ; 在中点放 label
    mid = list(
            (xCoord(ctr) + xCoord(stubEnd)) / 2.0
            (yCoord(ctr) + yCoord(stubEnd)) / 2.0)
    schCreateWireLabel(cv nil mid netName "centerCenter" "R0" "stick" 0.0625 nil)))
