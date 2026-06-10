# 技术存档总目录 — 8通道视觉皮层神经刺激ASIC

> 📋 **进度/回忆请先看 [`PROGRESS.md`](PROGRESS.md)** —— 每次重开会话从那里恢复上下文。

> **单一信息源(Single Source of Truth)。** 本存档是该芯片的完整技术档案,晶体管级。
> 用途:(1) 个人技术存档,可整体交接给其他项目/接手人;(2) 派生面试技术PPT的素材层。
> 数据只在此维护一处,PPT 是它的展示层,两者保持一致。

> **语言约定:** 电路术语用英文(comparator, headroom, cascode, current mirror...),说明用中文。
> 这样以后做英文PPT,术语可直接复用。

---

## 项目速览

| 项 | 值 |
|---|---|
| 芯片 | 8通道无线神经刺激ASIC,面向皮层视觉假体 |
| 工艺 | TSMC 180nm BCD Gen2,1P6M,MIM cap |
| Die | 2 × 2.5 mm |
| 通道 | 8 channel × 1:8 TDM = 64 电极 |
| 无线供电 | 13.56 MHz(SAR 上限 544 µW/mm²) |
| 刺激电流 | 0–75 µA(5-bit IDAC,5 µA 步进) |
| Headroom | 75 mV(PI 环路维持) |
| IDAC drain 钳位 V_REF | 45 mV(vs Cesc 250mV,↓82%) |
| 负载 | 20–70 kΩ,1–20 nF |
| Tapeout | 2026-05-20 提交 TSRI MPW;2026-05-29 final submission 确认 |
| 作者 / 导师 | 钱啸云 / Prof. Wouter Serdijn(TU Delft Bioelectronics) |
| 基线 | Varkevisser et al., TCAS-I 2025(2通道,0.18µm CMOS) |

---

## 文档结构与阅读顺序

```
thesis_archive/
├── 00_INDEX.md              ← 本文件:总目录 + 模块状态表
├── 01_system_overview.md    ← 顶层架构、信号流、规格表
├── 03_modules/              ← 每个 symbol 一个文件夹(md + symbol.png + schematic.png + sub/)
├── 04_physical_design.md    ← floorplan / pad ring / routing
├── 05_verification.md       ← DRC/LVS/PEX、后仿、tapeout
├── 06_vs_baseline.md        ← vs Cesc 逐项改进 + 论文对照
├── 10_integration/          ← 集成文档(模块怎么连、单通道、整系统)
│   ├── 10_1_module_interconnect.md
│   ├── 10_2_single_channel.md
│   └── 10_3_full_system.md
└── figures/                 ← 通用截图归档(波形/版图/系统图)
```

**建议阅读顺序:** 01(整体是什么)→ 10_2(单通道怎么工作)→ 03(逐模块细节)→ 10_1(连接关系)→ 10_3(整系统)→ 04/05(物理与验证)→ 06(贡献)。

---

## 模块每个文件夹的标准内容

```
03_modules/<module>/
├── <module>.md      ← 模组介绍(见下方模板)
├── symbol.png       ← symbol 截图
├── schematic.png    ← 内部电路原理图截图
└── sub/             ← 子模块(如有),每个子模块同样三件套结构,可继续嵌套
    └── <submodule>/
        ├── <submodule>.md
        ├── symbol.png
        └── schematic.png
```

**模组 md 模板:**
```
# 模块名 (cell name)
## 1. 接口 (pin 表: 名称 / 方向 / 功能)
## 2. 功能概述
## 3. 子模块清单 (列出 sub/ 内子模块 + 各自作用)
## 4. 内部拓扑 (晶体管级 / 子模块连接)
## 5. 关键设计点 / 取舍
## 6. vs Cesc (如有改进)
## 7. 状态
```

---

## 模块状态表

> 状态:🔲 待填(无素材) | ⏳ 待核对(已整理,等钱啸云确认) | ✅ 已确认

> ⚠️ **核对纪律:** 模拟电路截图可能被误读(管子类型/连接/镜像关系)。每个模块整理完为 ⏳,
> 必须经钱啸云核对后才能转 ✅。关键模块(IDAC / PI / comparator)尤其要逐一确认。

### 层次结构(已确立)
```
chip_top
├── PAD_RING_WITH_SEALBRING
└── QC_rectifier_full ────────────── 03_modules/QC_rectifier_full/  ✅符号
    ├── GM(半波分离,在内部)        🔲 待图(用户后续专门讲)
    ├── data_inputV2(SPI 解码)      🔲 待图
    ├── bias_block_V2(全局 bias)    ⏳ 符号已记
    ├── QC_rectifier_CH0(满血)      ⏳ 03_modules/QC_rectifier_CH0/  13/13 子模块符号已记
    └── QC_rectifier ×7(CH1–7,残血) 复用 CH0 核心,电极 4-by-4 合并
```

### 顶层
| 文档 | 状态 | 备注 |
|------|------|------|
| top_level | ⏳ | 符号/端口已记(✅ QC_rectifier_full + GM 在内、CH0 引出 EN/DATA_SLICE) |
| QC_rectifier_full | ⏳ | 5 类实例已记;两级 bias、SIN 4+4 分配已确认;GM/data_inputV2 内部待图 |
| 01_system_overview | ⏳ | 顶层架构已并入 |

### QC_rectifier_CH0 的 13 个子模块(03_modules/QC_rectifier_CH0/sub/)
| 子模块 | Cell | 状态 | 备注 |
|--------|------|------|------|
| comparator | comparator_new_4_for_use_nb (I123) | ⏳ 符号 | 内部 MOS 待图 |
| VCDL | VCDL_try_v4 (I133) | ⏳ 符号 | VB=V_C 闭环已确认;内部 MOS 待图 |
| NAND | ND2D1BWP7T (I132) | ✅ | 标准单元 |
| switchV8 | switchV8 (I98) | ⏳ 符号 | 互补 PMOS/NMOS 功率管待图 |
| Co | OUT_CAP_80p | ✅ | 无源 MOS+MIM 80pF |
| H_bridge | H_bridge_LVT_use ×8 (I83<7:0>) | ⏳ 符号 | 内部 MOS 待图 |
| Switch_assigner | Switch_assigner_V3 (I119) | ✅ | 标准单元 |
| PI_controller | PI_controller_EN_mid_pow_nb_V3 (I126) | ⏳ 符号 | 关键,内部 MOS+补偿待图 |
| Idle_controller | idle_controller_nb (I108) | ⏳ 符号 | 内部 MOS 待图 |
| IDAC | IDAC_new_V5_for_sys_nb (I105) | ⏳ 符号 | 关键,内部 MOS 待图 |
| IDAC_assigner | IDAC_assigner_V3 (I118) | ✅ | 标准单元 |
| bias_local | bias_local (I128) | ⏳ 符号 | 生成 V_REF_OUT(75mV)/V_REF(45mV);内部待图 |
| EN_buffer(CH0 专属) | BUFFD3BWP7T (I33) | ✅ | 标准单元,残血版无 |

> CH0 三条路径全部连通:相位控制(comparator→VCDL→NAND→switchV8)、能量/刺激(switchV8→Co→H_bridge×8→电极→V_headroom)、反馈(V_headroom→PI/Idle/IDAC,PI 经 V_C 回 VCDL)。
> 下一步:进各 ⏳ 模块内部晶体管级,补 MOS 尺寸。

### 集成 / 物理 / 验证
| 文档 | 状态 | 备注 |
|------|------|------|
| 04_physical_design | ⏳ | 已并入 floorplan/layout/padring/routing,待核对 |
| 05_verification | ⏳ | 已并入验证流程,待核对 |
| 06_vs_baseline | ⏳ | 已并入 vs Cesc 对照 + 基线论文数据,待核对 |
| 10_1_module_interconnect | ⏳ | 已并入 netlist,待逐模块补全后完善 |
| 10_2_single_channel | ⏳ | 已并入单通道原理,待核对 |
| 10_3_full_system | 🔲 | 待模块补全后撰写 |

---

## 来源文件

原始素材(并入本存档前)位于 `../thesis_ppt/`:
PROJECT_HANDOFF_CN.md、single_channel_operation.md、module_hierarchy.md、
channel_floorplan__1_.md、channel_layout_assembly__1_.md、pad_ring_plan.md、
routing_checklist.md、padring规划.png、TDM_revised.pptx、
TCAS-I_2025_Varkevisser_offi.pdf(基线论文)。
