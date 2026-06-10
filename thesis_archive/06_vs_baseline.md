# 06 — vs 基线 (Varkevisser, TCAS-I 2025)

> 贡献叙事主线:每一行是相对 Cesc 2 通道芯片的具体可量化改进。这是面试/答辩"我的贡献"锚点。
> 来源:PROJECT_HANDOFF 第 8 节 + 基线论文(已并入,⏳待核对)。

---

## 1. 基线论文速览

**Varkevisser et al., "Autonomous Output Supply Scaling for Efficient Multichannel Electrical Stimulation", IEEE TCAS-I 2025.**
(thesis_ppt/TCAS-I_2025_Varkevisser_offi.pdf,14 页)

| 项 | 基线值 |
|---|---|
| 工艺 | 0.18 µm CMOS |
| 通道 | 2(原型) |
| I-DAC | 4-bit,20–95 µA,LSB 5µA,+20µA offset 支路;wide-swing cascode |
| Co | 40 pF(ripple ΔVo 175mV @ 95µA) |
| Vfb(headroom)设计范围 | 100–200 mV |
| 最大输出电压 | 5 V(5V 晶体管) |
| **输出驱动效率** | **>80%(电流 95µA,负载 30–70kΩ);比固定电压供电 ↑4.3 倍** |
| 脉冲 | 100 µs 脉冲,1 µs 间隔(支持 TDM) |
| 核心思路 | 用电流源 headroom 电压 Vfb 作整流相位控制节点(免高阻分压器、免 compliance monitor、单 Vref 全通道共用) |

**最强对标数字:基线输出驱动效率 >80%,vs 固定供电 4.3×。** 你若有自己的效率后仿/测试数据,即对标此。

---

## 2. 逐项改进对照

| 改进点 | Cesc(基线) | 本工作 | 效果 |
|---|---|---|---|
| 误差放大器 | 开环 OTA | **PI 控制器** | 消除稳态 headroom 误差 |
| IDAC headroom | 250 mV | **45 mV**(V_REF 钳位) | ↓82% 电压浪费 → 效率提升 |
| 空载处理 | 无 | **Idle Controller** | 高→低负载切换效率优化 |
| Level shifter | 交叉耦合(上升/下降不对称,毛刺) | **CMLS 架构** | 干净方波,边沿对称 |
| 整流开关 | 纯 PMOS | **新增互补 NMOS 支路** | 低压效率 ↑~150% |
| VCDL 最小延迟 | 800 ps | **170 ps**(范围 33ns→10ns,800ps→170ps) | ↓79%,支持快速 TDM 切换 |
| 输出电容 Co | MOS 或 MIM | **MOS + MIM 叠加** | 同面积容值 ×2 |
| 通道数 | 2 | **8(+ 1:8 TDM → 64 电极)** | 完整规模扩展 + 顶层集成 |

---

## 3. 补充设计洞察(答辩备用)

- **PI 在 13.56MHz 采样系统的稳定性:** 环路交越 < f_sw/2 = 6.78MHz;补偿电容缩小 ~6 倍即失稳
- **超低 headroom IDAC(核心贡献):** V_REF(IDAC 钳位)= 45mV(vs 基线 250mV,↓82%);
  PI 实际维持工作 headroom = 75mV(45mV + 余量);最低稳定输出 5µA。
  关键:输出电容 + 调压整流器在负载端吸收高压,电流镜本身独立工作在低 headroom。
  > 详见 10_2「三个电压点辨析」:↓82% 用 45mV 算,75mV 是工作点,别混。
- **WPT 源端模型:** 弱耦合穿颅链路 Voc ≈ 7.5V,R_source ≈ 50kΩ,短路电流受限 ~150µA(可输送电流硬上限);
  多通道同时加载 → SIN_p 下沉 ∝ I_total × R_source(解释"为什么效率重要")

---

## 4. ⚠️ 待你确认
- [ ] 本工作自己的**峰值效率 %** 及 vs Cesc 的对比数字(最强单一结果,有后仿/测试数据吗?)
- [ ] 电流范围本工作 0–75µA(5-bit)vs Cesc 20–95µA(4-bit)—— 这个差异要不要在叙事里解释?

## 5. 状态
⏳ 待核对。
