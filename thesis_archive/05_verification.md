# 05 — 验证与 Tapeout

> 来源:PROJECT_HANDOFF 第 10–11 节 + routing_checklist(已并入,⏳待核对)。

---

## 1. 工具链

- **EDA:** Cadence Virtuoso Layout XL;ADE Assembler / Maestro;Calibre DRC/LVS/PEX
- **PEX:** Calibre **RCC 模式**(捕获层间耦合电容)。后仿:High Precision Analog preset + 高"内部网络最大频率"
  + 对敏感模块(IDAC、PI、bias_local、comparator、VCDL、switchV8)设 **Instance Preservation = Selected**,
  防 APS 优化过度压缩关键寄生。Default preset 对模拟过于激进。
- **全芯片仿真:** XPS MS(CPU 无法占满,电路依赖链限制,正常)
- **Monte Carlo:** mont.lib(片间全局工艺变化)+ mismatch.lib(片内随机失配);工艺角 4–6σ;SS 角 = NMOS/PMOS Vth 均偏高
- **Transient Noise:** Fmax 25 MHz,保守模式
- **DRC:** 日常层次化,最终 tapeout 平坦化;offgrid 警告可接受

## 2. DRC 问题处理 / 豁免

| 规则 | 处理 |
|------|------|
| NBL.R.1 | 主 DRC deck 打开 SubToGround 开关(Jim/TSMC 建议);全芯片衬底接地,无需 NBL 隔离的 HV 器件 |
| DV.R.2 | 豁免:无 HV 器件,全低压(1.8V);该规则针对 HV 混合设计 |
| OD2.O.2 | 来自 Foundry 标准 IO pad cell PVDD1ANA → 豁免(注明 Library/Cell) |
| RES.HV.R.1a/1b/1d | rppolyhri3k 被误判 HV poly 电阻 → Jim 确认可 waive |
| PO.R.4 | Floating gate(外部 bias 输入)→ block-level 正常,全芯片 LVS 消失 |
| DOD.R.1 | 缺 dummy OD → tapeout 前统一 dummy fill |
| LVS VSSH/VSS | runset 设 Virtual Connect 解决 |

真实 LVS short 案例:CH1_N<1>/CH2_N<1>/CH3_N<1> 经未标记多边形与 VSS 短接(游离金属桥接电极 N 网络到 VSS guard ring)。

## 3. 后仿状态

| 项目 | 状态 |
|------|------|
| 单 channel 后仿(含寄生) | ✅ 可运行 |
| V_HEADROOM 寄生验证 | ✅ 100fF 无影响 |
| 后仿结果验证 | ⏳ 等结果 |

PI 在 13.56MHz 采样系统中的稳定性:环路交越频率必须 < f_sw/2 = 6.78MHz;补偿电容大小关键(缩小 ~6 倍即失稳)。

## 4. Tapeout 与当前状态

- **2026-05-20 提交** TSRI MPW(via Muse Semi,项目号 M17940;Jim Quinn / Vaibhav Dubey)。
  金属选项 1p6m_4X1U40KA;TSMC 制造网格 5nm。最终提交应用 SubToGround 开关 + 命名豁免。
- **2026-05-29 final submission 确认**,芯片进入制造。
- DRC/LVS 关闭完成;后仿完成。
- **进行中:**
  - PCB 设计(FR-4 在 13.56MHz 足够;CMOD S7 FPGA 驱动数字输入)
  - Wire bonding(TU Delft,Zu-yao Chang)
  - 裸 die 发货 TU Delft EEMCS 16 楼,40 颗,不分批
  - 论文写作;求职

## 5. 测量方法(继承自 Cesc)

- RF 变压器做 AC 耦合输入;切换 EN 信号的差分 P_on − P_off 功率测量;47Ω 采样电阻
- 回片后 die 定向:正面(有源面)有金属图案+彩虹干涉色,背面灰色硅;靠不对称 pad ring 定向;真空吸笔,正面朝上

## 6. 状态
⏳ 待核对。
