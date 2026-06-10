# PI_controller_EN_mid_pow_nb_V3 — PI 控制器(闭环核心)

> Cell: `PI_controller_EN_mid_pow_nb_V3`(实例 I126)
> 父模块:QC_rectifier_CH0。反馈环核心(误差 → 控制电压)。

---

## 1. 功能

闭环控制器。比较 **V\_headroom(V\_FB)** 与参考 **V\_REF\_OUT(75 mV)**,输出控制电压 **V\_C** 给 VCDL:
- V\_headroom > 75mV → V\_C↑ → VCDL 延迟 td↓ → pulse 变窄 → 充电少 → V\_headroom↓
- V\_headroom < 75mV → V\_C↓ → td↑ → pulse 变宽 → 充电多 → V\_headroom↑
- 稳态:积分项消除开环 OTA 的稳态误差,V\_headroom 精确 = 75 mV

闭环路径:**PI → V\_C → VCDL → NAND → switchV8 → Co → V\_headroom → 回 PI**。
以 13.56 MHz 采样(每周期一次);环路带宽必须 < f\_sw/2 = **6.78 MHz**(奈奎斯特)。

---

## 2. 接口

![PI controller symbol](../../../figures/PI_controller_symble.png)

| Pin | 方向 | 连接 | 说明 |
|-----|------|------|------|
| V\_FB | IN | **V\_HEADROOM** 节点 | 反馈量(被控) |
| V\_REF\_OUT | IN | 75 mV(bias\_local) | 参考(headroom 目标) |
| V\_C | OUT | → VCDL 控制脚 | 控制电压 |
| EN, N\_EN | IN | idle\_controller 输出 | 空载时关闭 PI |
| PI\_OTA\_CLAMP | IN | 全局 bias | OTA 钳位偏置 |
| IDAC\_OTA\_VB1, IDAC\_OTA\_VB2 | IN | 全局 bias | OTA 参考电流偏置 |
| VDDL / VSS | PWR | | |

---

## 3. 内部结构 — 无源网络 + OTA

![PI controller schematic](../../../figures/PI_controller.png)

### 3.1 无源补偿网络(R-C)

| 元件 | 值 | 位置 | 作用 |
|------|----|------|------|
| R3 | 20 kΩ | 输入端(V\_FB → OTA 反相输入) | 决定 P 增益分母 |
| R5 | 1 MΩ | 反馈通路(OTA 输出 → 反相输入,与 C0 串联) | 决定 P 增益分子 |
| C0 | 515 fF | 与 R5 串联 | 产生积分零点(PI 零点) |
| C4 | 33 fF | V\_C 输出节点(对 VSS) | 高频噪声滤波极点 |

**补偿网络拓扑:**

```
V_FB ──[R3]──┬── OTA(−)
             │
    OTA(+) ← V_REF_OUT (75mV)
             │
    OTA OUT ──┬──[R5]──[C0]──┘  (串联反馈 → PI 零点)
              │
             [C4]
              │
             VSS
              │
             V_C (= OTA OUT)
```

### 3.2 OTA(误差放大器)

拓扑与 IDAC 内部 `ota_paperV4_nb_V2` **基本相同**:PMOS 差分输入对 + 折叠 cascode + 自偏置 PMOS 负载 + 单端输出。

**关键差异(与 IDAC OTA 对比):**
参考 NMOS M37/M40 的 W=**2µm**(IDAC OTA M54/M53 为 W=1µm),宽度翻倍 → 参考电流翻倍 → 尾电流翻倍 → **PI OTA 带宽更高**。
PI 需在 13.56 MHz 采样周期内调节 V\_C,对速度要求高于 IDAC OTA(后者只需低频钳位 45mV)。

**差分输入对 + 参考电流 + 尾电流镜(M22/M29/M36/M41 为 dummy,不计):**

| 管 | 类型 | W | L | fingers | totalM | gate / 功能 |
|----|------|---|---|---------|--------|------------|
| M1 | PMOS pch\_mac | 1 µm | 800 nm | 2 | 8 | VIN\_P 正向输入(差分对) |
| M2 | PMOS pch\_mac | 1 µm | 800 nm | 2 | 8 | VIN\_N 反向输入(差分对) |
| M4 | PMOS pch\_mac | 2.8 µm | 1 µm | 4 | 4 | gate=net3(二极管接),建立参考节点 |
| M3 | PMOS pch\_mac | 1 µm | 1 µm | 6 | 6 | gate=net21,镜像 → 差分对尾电流 |
| M18 | PMOS pch\_mac | 685 nm | 180 nm | 1 | 1 | gate=EN,EN 开关(PMOS) |
| M37 | NMOS nch\_mac | 2 µm | 8 µm | 1 | 1 | gate=IDAC\_OTA\_VB2,参考 NMOS 堆上管 |
| M40 | NMOS nch\_mac | 2 µm | 8 µm | 1 | 1 | gate=IDAC\_OTA\_VB1,参考 NMOS 堆下管 |

> M1/M2 尺寸与 IDAC OTA 相同(totalM=8);M37/M40 比 IDAC OTA 对应管(M54/M53, W=1µm)宽一倍。

**本地 VB1/VB2 生成(M38 为 dummy):**

| 管 | 类型 | W | L | fingers | totalM | 功能 |
|----|------|---|---|---------|--------|------|
| M17 | PMOS pch\_mac | 2.8 µm | 1 µm | 1 | 1 | gate=net3,PMOS 镜像 → 注入 VB2 电流 |
| M21 | NMOS nch\_mac | ≈400 nm | 1 µm | 1 | 1 | gate=drain=Vb2,二极管 NMOS(上) |
| M20 | NMOS nch\_mac | ≈400 nm | 1 µm | 1 | 1 | gate=drain=net025,二极管 NMOS(下) |
| M14 | PMOS pch\_mac | 2.8 µm | 1 µm | 2 | 2 | gate=net3,PMOS 镜像 → 注入 VB1 电流(2f,IDAC OTA M14 为 1f) |
| M16 | NMOS nch\_mac | ≈300 nm | 6 µm | 1 | 1 | gate=drain=Vb1,超长管上半段 |
| M19 | NMOS nch\_mac | ≈300 nm | 6 µm | 1 | 1 | gate=Vb1; drain=net031; src=VSS,超长管下半段 |

> M16+M19 等效 L=12µm(IDAC OTA 为 15.6µm);M14 为 2f(IDAC OTA 为 1f)→ VB1 电流加倍,与整体 2× 尾电流设计一致。
> M21/M20 的 W≈400nm、M16/M19 的 W≈300nm 由图中 M38(dummy, w=300n 可清晰读出)对比推断;L 均与 IDAC OTA 不同。

**折叠路径 EN 开关 + 电流限制 NMOS:**

| 管 | 类型 | W | L | fingers | totalM | gate / 功能 |
|----|------|---|---|---------|--------|------------|
| M23 | NMOS nch\_mac | ≈220 nm | 180 nm | 1 | 1 | gate=EN,折叠路径使能开关 |
| M24 | NMOS nch\_mac | 220 nm | 180 nm | 1 | 1 | gate=N\_EN,折叠路径使能开关(互补) |
| M5 | NMOS nmos2v\_mac | 520 nm | 1 µm | 1 | 1 | gate=Vb1,折叠电流限制(M1 支路) |
| M6 | NMOS nmos2v\_mac | 520 nm | 1 µm | 1 | 1 | gate=Vb1,折叠电流限制(M2 支路) |

> M23/M24 用 EN 和 N\_EN 两路分控(IDAC OTA 两管同用 EN),与 PI symbol 接口一致。
> M5/M6 W=520nm vs IDAC OTA 230nm,约 2× 宽,与整体 2× 电流一致。

**NMOS cascode + PMOS 自偏置负载(M11/M12 为 dummy 待确认):**

| 管 | 类型 | W | L | fingers | totalM | gate / 功能 |
|----|------|---|---|---------|--------|------------|
| M7 | NMOS nmos2v\_mac | 340 nm | 1 µm | 2 | 2 | gate=Vb2,NMOS cascode(左支路) |
| M8 | NMOS nmos2v\_mac | 340 nm | 1 µm | 2 | 2 | gate=Vb2,NMOS cascode(右支路);drain=**OUT** |
| M9  | PMOS pmos2v\_mac | 1.2 µm | 800 nm | 2 | 2 | gate=net012,自偏置 cascode 下层 |
| M10 | PMOS pmos2v\_mac | 1.2 µm | 800 nm | 2 | 2 | gate=net012,cascode 输出;drain=**OUT** |
| M11 | PMOS pmos2v\_mac | 1.2 µm | 800 nm | 2 | 2 | gate=drain=net013(二极管接),建立 net013 |
| M12 | PMOS pmos2v\_mac | 1.2 µm | 800 nm | 2 | 2 | gate=net013,cascode 上层;drain=net024 |

> M9/M10/M11/M12 四管尺寸完全一致(1.2µm/800nm/2f),标准自偏置 PMOS cascode 结构。
> vs IDAC OTA 对应管(W=340nm, 2f):W 扩大约 3.5×,与 2× 电流 + 更高输出阻抗需求对应。
> M7/M8 vs IDAC OTA(W=220nm, 1f):W=340nm, 2f,有效截面约 3×。

---

## 4. 传递函数与关键参数

反馈阻抗 Z\_f = R5 + 1/(sC0),输入阻抗 Z\_i = R3:

**H(s) = −Z\_f/Z\_i = −(R5/R3) × (1 + 1/(s·R5·C0))**

| 参数 | 公式 | 值 |
|------|------|----|
| **P 增益 Kp** | R5 / R3 | 1MΩ / 20kΩ = **50** |
| **PI 零点频率 fz** | 1 / (2π·R5·C0) | 1/(2π×1MΩ×515fF) ≈ **309 kHz** |
| **输出极点 fp** | 1 / (2π·Rout·C4) | 高频(>10 MHz),不影响环路 |

**fz = 309 kHz 的设计依据:**

这是一个 **13.56 MHz 采样系统**,PI 每个 RF 周期采样一次。奈奎斯特频率为 f\_sw/2 = **6.78 MHz**,环路带宽必须严格低于此值,否则采样域中相位裕度不足、无法收敛。

fz = 309 kHz ≈ f\_Nyquist / 22,给环路留出了约 **22× 的频率裕量**。若 fz 设得太高(接近 6.78 MHz),离散域中等效相位延迟使闭环失稳。

> **C0 演化记录(设计笔记):** 6.37 pF → 100 fF → **515 fF(最终)**。最终值在采样稳定性与过渡响应之间取得平衡。

---

## 5. 工作原理(对外讲解版)

**一句话:** OTA 把 V\_headroom 与 75 mV 的误差放大并积分,输出 V\_C 连续调整 VCDL 的延迟时间,把 headroom 精确锁在 75 mV。

**P 通路(快速响应):**
误差信号经 R3 → OTA → R5 放大 50 倍。headroom 偏离 → V\_C 立即响应 → VCDL 调整 → 充电量修正。响应发生在每个 13.56 MHz 周期内。

**I 通路(消除稳态误差):**
R5 与 C0 串联构成积分反馈。低频时(< 309 kHz)C0 阻抗主导,等效纯积分器 → 稳态误差趋零 → V\_headroom 精确等于 V\_REF\_OUT = 75 mV,不随负载或工艺角漂移。

**EN 关断:**
N\_EN=1(空载)时 OTA 关断,V\_C 保持不变(由 C0 保持电荷),VCDL 停止调节;恢复后 PI 自动从当前 V\_C 值重新积分。

---

## 6. 状态
✅ symbol/接口已记。
✅ 无源补偿网络值(R3/R5/C0/C4)已记。
✅ 传递函数与 fz 设计依据记录完毕。
✅ OTA 全部晶体管已记(M1–M24 + M37/M40,共 ~22 管,dummy 已排除)。