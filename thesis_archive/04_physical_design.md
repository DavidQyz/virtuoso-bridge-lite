# 04 — 物理设计 (Layout / Floorplan / Pad Ring / Routing)

> 来源:channel_floorplan / channel_layout_assembly / pad_ring_plan / routing_checklist(已并入,⏳待核对)。
> 版图截图请放 `figures/` 并在此引用。

---

## 1. 通道内部 Layout 要点

- IDAC 匹配采用**共心(common-centroid)**摆放;二进制加权单元,回文式排列
- 金属方向:M1 横 / M2 竖 / M3 横 / M4 竖 / M5 横 / M6 竖(UTM)
- Guard ring:NMOS guard ring 在 P-well 内无需单独 substrate tap;PMOS guard ring 在 NWELL 需 N+ tap
- MIM cap:顶板 M6/CTM(内部节点连 DIFF/SD);底板 M5/CBM 经三层同步延伸引至 M6 外部布线。
  **CBM5 绝不能接触 OD/栅极。**

## 2. 单通道 Block 尺寸(裸面积)

| Cell | W×H (µm) | 面积 (µm²) | 备注 |
|------|----------|-----------|------|
| Co (MOS+MIM, 80pF) | 250×135 | 33,750 | ⚠️ 最大,占 44%,硬约束 |
| H_bridge_LVT_use ×8 | 91×27 (单) | 19,656 | 第二大,朝 pad ring |
| IDAC_new_V5 | 170×58.5 | 9,945 | 宽扁 2.9:1 |
| PI_controller | 121×60 | 7,260 | 宽扁 2:1 |
| bias_local | 51×50 | 2,550 | |
| Idle_controller | 33.5×30.7 | 1,028 | |
| Switch_assigner | 40×17.5 | 700 | 3 行标准单元 |
| IDAC_assigner | 28×16.5 | 462 | 3 行标准单元 |
| switchV8 | 19.3×19 | 367 | |
| comparator | 17×16.64 | 283 | |
| VCDL | 7.66×7.91 | 61 | |
| NAND | 4.74×4.44 | 21 | |
| **合计裸面积** | | **76,083** | ×1.3 走线 ≈ 99,000(~250×400µm) |

Co + 8×H_bridge 合计占 70%,决定 channel 整体形状。

## 3. 通道内 Floorplan(v2 已确认)

```
  ← 内侧(chip center)              外侧(pad ring)→
  ┌──────────────────────┬──────────────────┐
  │      Co (250×135)     │ H_br0..7 (2×4)    │  ← Row1
  ├──────────┬───────────┴──────────────────┤
  │IDAC_assi │ IDAC_new_V5 │ Switch_assigner │  ← Row2
  ├──────────┴──┬────┬────┬────┬────┬────┬───┤
  │ PI_ctrl     │bias│Idle│comp│VCDL│ND  │sw8│  ← Row3 控制带
  └─────────────┴────┴────┴────┴────┴────┴───┘
```
- H_bridge 朝外(bond wire 最短),Co 紧邻(Mp_out 走线短)
- IDAC_assigner 紧靠 IDAC(IDAC_PULSE 走线极短);Switch_assigner 在 H_bridge 正下方
- 控制带内→外:bias_local → PI → Idle → comparator → VCDL → NAND → switchV8

## 4. 顶层 Floorplan

- 8 通道 4 列 × 2 行矩阵,中心对称;上 4 通道模拟前端朝外、IDAC+Co 朝内;下 4 通道上下镜像
- data_inputV2 + bias 模块位于 die 右侧;GM 计划放 die 左侧(隔离 13.56MHz 功率与右侧数字/SPI)
- 中央水平间隙 = "信号高速公路":数字总线 + bias 线从右侧向左穿过,扇出各通道

## 5. Pad Ring(76 pad = 72 功能 + 4 corner)

2×2.5mm die,110µm pitch,~87×101µm pad。详见 `figures/padring规划.png`。

- **顶边(20):** VSS + CH0×16(8 对 VP/VN)+ Idle_EN + VDD + VDDH
- **左边(16):** VDD + CH1×4 + CH2×4 + SIN_P + SIN_N + CH3×4 + VSS
- **底边(20):** VDD + CH4×4 + CH5×4 + CH6×4 + CH7×4 + I_bias + I_current_bias + DATA_slice×2 + VSS
- **右边(16):** VSS + DATA_slice×10 + CLK + DATA + D_EN

关键:
- **CH0 完全可观测**:顶边引出 16 个独立电极 pad + 缓冲 Idle_EN 输出;CH1–7 各通道内部合并为 2 对 VP/VN
- **SIN_P/N 移至左边中间**,隔离 13.56MHz 功率线与右边 SPI 数字线(消串扰)
- 电极用 **bare pad(无 ESD)**:消除 ESD 钳位寄生电容,因电极电压由 H-bridge 受控故安全
- SIN_P/N 用 **5V IO pad**(VDDH 供 5V VDDPST 环);浮动 AC 对,ESD 二极管每半波轻微导通(整流器前端固有)

## 6. 顶层 Routing 策略

| 层 | 用途 |
|----|------|
| M6(UTM,40kÅ) | SIN_P/N 功率线 + GM 输出;VDDL/VSS 竖向 strap |
| M5 | VSS mesh + SIN_P 正下方屏蔽板 |
| M4 | 数字总线与 bias 线之间的 VSS 屏蔽板 |
| M3 | bias 线(横) |
| M2 | 竖向 via 通道 |
| M1 | 数字总线(横) |

- 数字总线 23 根,~0.8µm pitch ≈ 18µm 宽 + guard rail ≈ 22µm,中央 ~30µm 间隙够放
- **屏蔽板而非正交布线**:bias 和数字都从右向左走,方向锁死无法正交 → 层间分离 + 夹接地屏蔽板(via 处开槽)
- IR drop 非问题:10µm M6 走 900µm,350µA → ~0.5mV
- SIN 线宽选 5µm(EM 裕量 15×,IR ~4.5mV over 900µm)
- 单 via 够用(数字电流 nA–µA,EM 裕量 >1000×)

## 7. Wire Bond(TU Delft,Zu-yao Chang)

25µm Au 球焊;芯片 pad ≥100×100µm,pitch ≥110µm;PCB pad ≥450×150µm;键合角 >50°;
最大线长 6mm;不允许交叉;芯片 pad 材质 Al;PCB 表面 ENIG/ENEPIG。

## 8. 状态
⏳ 待核对 — 已并入原始笔记;待补版图截图(`figures/`)。
