# 01 — 系统总览

> 顶层架构、信号流、规格表。模块级细节见 `03_modules/`,连接关系见 `10_integration/`。

---

## 1. 芯片解决的问题

因眼球下游损伤(如视神经损伤)失明的患者,可通过直接刺激视觉皮层的电极阵列部分恢复视觉:
每个电极注入精确电流脉冲可引发一个 phosphene(光幻视/感知到的亮点),足够多电极即可"绘制"粗糙图像。

两个硬约束:
1. **功率必须无线穿颅传输** — 经颅有线连接有感染风险,功率以 13.56 MHz 交流磁场链路传入;
   该链路弱耦合(穿皮肤+颅骨),可用功率受 SAR 上限 **544 µW/mm²** 限制,源端阻抗高。
2. **电流必须精确且安全** — 组织刺激需精确控制电流(电荷平衡关乎安全),覆盖一定范围的未知组织阻抗,
   且不能依赖笨重的外部 compliance monitor。

**架构解答(继承自 Cesc,本工作改进):** 每个通道是一个**自适应调压整流器**。
整流器用相位控制开关把输出电容充到"刚好够用"的电压来维持电流源合规——目标是电流 sink 两端一个
小的固定 **headroom(75 mV)**。反馈环持续调节整流导通相位保持 headroom 恒定,几乎不浪费电压。

---

## 2. 顶层系统架构

8 通道刺激器,每通道经 1:8 TDM 连 8 个电极 → 8 × 8 = 64 电极。

```
  13.56 MHz 无线链路(片外 LC 谐振 / RF 变压器)
        │  SIN_P, SIN_N(浮动差分 AC 对——非信号+地)
        ▼
  ┌──────────────────────────────────────────────┐
  │  GM — 片上半波 / 极性分离器                    │
  │  4 通道收 SIN_P 半波,另 4 通道收 SIN_N 半波   │
  └──────────────────────────────────────────────┘
        │                          │
   (送 4 通道)                 (送另 4 通道)
        ▼                          ▼
  ┌───────────────┐  ×8 个相同通道(QC_rectifier)
  │  QC_rectifier │  = 调压整流器 + 精密电流 sink + 相位控制环 + PI 环 + 空载控制
  └───────────────┘
        │ V_out_P / V_out_N → 片外电极(组织负载)
        ▼
  H-bridge → 每通道 8 电极(EN_SW one-hot 选择,STIM_MODE 控制极性)

  数字侧:外部 SPI(CLK/DATA/D_EN)→ data_inputV2 → 扇出配置到全部 8 通道
```

**SIN_P / SIN_N 关键说明:** 二者是**浮动 AC 源的两个端子**(无线链路次级线圈两端),都不接 VSS。
GM 利用两个半波:不丢弃负半波,而是把两种极性分别路由到两组各 4 通道,使总可用充电功率约翻倍。
每通道内部整流仍是单端(通道输出电容 Co 的 NEG 端接 VSS)。

---

## 3. 主要规格

| 参数 | 数值 |
|---|---|
| 工艺 | TSMC 180 nm BCD Gen2,1P6M,MIM cap(CBM@M5 / CTM@M6),40 kÅ 厚 M6(UTM) |
| Die 尺寸 | 2 × 2.5 mm |
| 有效面积(8 通道) | ~0.79–0.96 mm²(估算,见 04) |
| 通道数 | 8 |
| 电极数 | 64(每通道 1:8 TDM) |
| 无线供电频率 | 13.56 MHz(SAR 上限 544 µW/mm²) |
| 每通道刺激电流 | 0–75 µA,5 µA 步进(5-bit IDAC) |
| 负载阻抗范围 | 20–70 kΩ |
| 负载电容 | 1–20 nF |
| 刺激方式 | 双相(STIM_MODE 选 H-bridge 极性) |
| 调压 headroom(电流 sink) | 75 mV(PI 环路维持) |
| IDAC drain 钳位(V_REF) | 45 mV |
| Idle 阈值(V_EN_REF) | 200 mV |
| 每通道功耗 | 正常 ~20 µW,最大 ~70–80 µW(随输出功率变化) |
| 总核心电流(8 通道) | ~350 µA,来自 1.8 V VDDL |
| 配置帧 | 每通道 1.25 µs,8 通道共 10 µs(SPI 10 MHz) |
| 电极脉冲 | 每电极 100 µs,完整 1:8 TDM 周期 ~1 ms |

---

## 4. 关键工作点速查

| 节点 | 数值 | 说明 |
|---|---|---|
| Mp_out | V_electrode + V_headroom | 随负载自动跟踪 |
| V_headroom(I_STIM) | 75 mV(稳态) | PI 控制器维持 |
| IDAC drain(V_REF) | 45 mV | OTA 钳位 |
| V_EN_REF | 200 mV | Idle Controller 阈值 |
| V_REF_OUT | 75 mV | PI 参考(bias_local 本地生成) |
| f_sw = SIN_p | 13.56 MHz | = 控制环路更新率 |
| PI 环路带宽 | < 6.78 MHz | 奈奎斯特(f_sw/2) |
| VCDL 延迟范围 | 10 ns – 170 ps | 最小延迟 170 ps(Cesc:800 ps) |

---

## 5. 模块层级(顶层)

> 完整层级随各模块 schematic 截图补全;以下为当前已知结构(来自 module_hierarchy 笔记)。

```
顶层(QC_rectifier_full)
├── data_inputV2(数字配置)
│   ├── SPI_V2(12-bit 移位寄存器 + CLK/输出门控)
│   ├── DEL1BWP7T_Z ×2
│   └── 3bit_decoder_EN ×2
├── GM(半波/极性分离器)← layout 中待放置,放 die 左侧
└── QC_rectifier ×8(每通道一个)
    ├── comparator_newV4_for_use_nb
    ├── VCDL_tryc_v4
    ├── NAND / 脉冲逻辑
    ├── switchV8(CMLS level shifter + 互补 NMOS 支路)
    ├── PI_controller(补偿电容 C1/C2,Rz)
    ├── IDAC_new_V5(精密电流 sink + 内部 OTA)
    ├── Idle_controller
    ├── H_bridge_LVT_use(×8 → 8 电极)
    ├── Co(MOS + MIM 叠加,~80 pF;NEG 接 VSS)
    ├── bias_local(V_REF_OUT 75mV,V_REF 45mV)
    ├── IDAC_assigner_V3(本地 5-bit 寄存器)
    └── Switch_assigner_V3(本地开关 + stim_mode 寄存器)
```

标准单元:TSMC BWP7T 系列。Pad 库:tpd018bcdnv5_6lm160a(Universal Analog I/O);电源/IO pad cell:PVDD1ANA。
