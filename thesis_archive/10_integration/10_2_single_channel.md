# 10_2 — 单通道完整工作原理 (QC_rectifier)

> 把各模块串成一个完整闭环的故事。模块级细节见 `../03_modules/`,纯连接关系见 `10_1_module_interconnect.md`。
> 来源:thesis_ppt/single_channel_operation.md(已并入,待核对晶体管级补充)。

---

## 0. 信号流程图(单通道,增强版)

> 在原 PPT「Analog Architecture Overview」基础上补全:OUTCAP 挂 Mp_out 节点、comparator 双输入、
> IDAC 控流(电流源 + 5-bit code)、闭合反馈环。手绘 SVG,VS Code 直接预览(无需插件),可直接粘进答辩 PPT(矢量可编辑)。

**路径配色:** 🟢 Power Path ┆ 🔵 Control Path ┆ 🟣 Enable / Idle

> 横向控制环主干布局(横平竖直,适合放 PPT):主信号链一条横干,反馈走顶/底专用通道。

![单通道信号流程图](../figures/single_channel_flow.svg)

**怎么读这张图(对外讲解顺序):**
1. 🟢 **能量**:SIN_p → switchV8 → Mp_out(Co 储能)→ 8×H-bridge 选 1 个电极 → 组织 → 回到 V_headroom → IDAC 定电流 → VSS
2. 🔵 **控制/相位**:comparator(SIN_p vs Mp_out)→ V_IN 分两路(直连 + VCDL 延迟)→ NAND 出宽度 td 的 pulse → 控制 switchV8 导通时长
3. 🔵 **反馈闭环**:V_headroom → PI(对比 75mV)→ Vc → VCDL 调 td → 调充电量 → 把 V_headroom 拉回 75mV(13.56MHz 采样,带宽 < 6.78MHz)
4. 🟣 **空载省电**:V_headroom > 200mV → Idle 关掉 comparator + PI,只留 IDAC
5. 🟠 **本地基准**:bias_local 生成 V_REF_OUT(75mV,给 PI)、V_REF(45mV,给 IDAC)

> **核心节点 V_headroom(黄色六边形)**:H-bridge 回流、IDAC、PI、Idle 四者交汇,是整个反馈环的被控量,稳态 75mV。

---

## 1. 概述

每个通道是**自适应调压整流器 + 精密电流刺激器**,核心思想:
- 从无线接收的半波 AC(SIN_p,13.56 MHz)取能
- 通过相位控制整流开关,自动把输出电容电压调到"刚好够用"
- 将精确电流经 H-bridge 送给选定电极
- 全程无需外部 compliance monitor

单通道支持:电流 0–75 µA(5 µA 步进,5-bit DAC)、负载 20–70 kΩ、电容 1–20 nF、
8 电极复用(H-bridge + SW 选择)、双相刺激(STIM_MODE 控制极性)。

### ⭐ 三个电压点辨析(对外口径,务必分清)

| 量 | 值 | 是什么 | 用途 |
|----|----|--------|------|
| **基线 headroom** | 250 mV | Varkevisser 基线 IDAC 所需余量 | 对比基准 |
| **V_REF**(IDAC 钳位) | **45 mV** | 我重新设计 IDAC 后,内部 OTA 钳位管 drain 所需的最小电压 | **改进 headline:45 vs 250 = ↓82%**(CV/答辩引用此) |
| **headroom**(工作点) | **75 mV** | PI 实际锁定的 I_STIM 节点电压(在 45mV 之上留余量) | 运行规格 |

> 一句话:**"↓82%"指我把 IDAC 需要的电压从 250mV 压到 45mV;75mV 是 PI 实际维持的工作 headroom(留了余量)。** 两者不是同一节点,别混。

---

## 2. 三条信号路径

### 2.1 能量路径(整流充电)
```
SIN_p(正半波 AC)
   ↓ [switchV8 导通时]
Mp_out 节点
   ├── Co(输出电容,MOS+MIM 叠加,同面积容值×2)← 储能
   └── V_SUPPLY → H_bridge_LVT_use
                     ↓ EN_SW 选电极,STIM_MODE 定极性
                V_out_p → 片外电极(负载 Ztissue)→ V_out_n
                     ↓
                I_STIM 节点(= V_headroom = Vfb)
                     ↓
                IDAC_new_V5(current sink)→ VSS
```
- **Mp_out**:整流开关输出,Co 稳定此节点
- **I_STIM = V_headroom**:IDAC 的 drain 端电压,整个反馈环的核心反馈信号,目标 75 mV

### 2.2 相位控制路径
```
SIN_p ──→ comparator(比较 SIN_p vs Mp_out)
              ↓ Vin(0/1)
   ┌──────────┴───────────┐
   │                      ↓
   │            VCDL(电流饥饿 INV,延迟 td)
   │                      ↓ Vin_delayed(反相)
   └──→ NAND ←────────────┘
            ↓ 低有效 pulse(width = td)
       switchV8(控制整流开关导通/截止)
```

### 2.3 反馈控制路径
```
V_headroom(I_STIM 节点)
   ├──→ PI 控制器(比较 V_headroom vs V_REF_OUT=75mV)
   │         ↓ Vc → VCDL 调 td → pulse 宽度 → Co 充电量 → V_headroom
   │
   └──→ Idle Controller(比较 V_headroom vs V_EN_REF=200mV)
             ↓ EN/nEN → 控制 comparator + PI 的开/关
```

---

## 3. 六步工作流程(适合 PPT 动画逐步展开)

1. **整流触发(comparator)** — 每个 SIN_p 正半波周期(73.8 ns)检测 SIN_p vs Mp_out:
   SIN_p>Mp_out → Vin=1 触发;SIN_p<Mp_out → 强制关断,防 Co 反向放电。
2. **脉冲生成(VCDL+NAND)** — Vin 上升沿 → 宽度 td 的低有效 pulse;td 由 PI 输出 Vc 决定
   (Vc↑→饥饿电流↑→td↓→pulse 窄→充电少→V_headroom↓)。
3. **整流充电(switchV8)** — pulse 期间开关导通,SIN_p 对 Co 充电:
   高压 PMOS 导通;低压自动切**互补 NMOS** 支路 → 低压效率提升 ~150%(vs Cesc 纯 PMOS)。
4. **电流刺激(H-bridge+IDAC)** — Co 电压驱动选定电极;EN_SW<7:0> one-hot 选 8 电极之一,
   STIM_MODE 设正/反极性(双相)。电流经负载回 I_STIM,IDAC 下拉至 VSS。
   IDAC 精度由内部 OTA 维持:钳位镜像管 drain 在 **V_REF=45 mV**(vs Cesc ~250mV,↓82%,主要效率点)。
5. **PI 控制** — 以 13.56 MHz 采样(每周期一次),积分项消除 Cesc 开环 OTA 的稳态误差,
   V_headroom 精确稳在 75 mV。环路带宽必须 < f_sw/2 = 6.78 MHz(奈奎斯特)。
6. **空载节能(Idle Controller)** — 负载切换使 V_headroom>200mV 时关闭 comparator+PI(停充电),
   IDAC 维持电流;V_headroom 回落 ≤200mV 后自动恢复。

---

## 4. 本地 bias 生成(bias_local)

两级 bias 架构(最初全局,后把最敏感的两个低压基准改为通道内 local):

**通道内 `bias_local` 本地生成**(避免长走线噪声耦合):
- **V_REF_OUT = 75 mV**(PI 参考 / headroom 目标)
- **V_REF = 45 mV**(IDAC drain 钳位)

**全局 `bias_block_V2` 分发(白字 net,经通道端口输入):**
- IDAC_VB1、IDAC_VB2、IDAC_OTA_VB1、IDAC_OTA_VB2、COMP_VCM、PI_OTA_CLAMP、**V_EN_REF(Idle 阈值)**
- 全局基准源自片外 **I_BIAS_INPUT**(电阻设定)

---

## 5. 状态
⏳ 待核对 — 已并入原始笔记;晶体管级细节随各模块 schematic 补全后回填。
