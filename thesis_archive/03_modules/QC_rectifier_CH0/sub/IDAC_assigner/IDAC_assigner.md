# IDAC_assigner_V3 — 电流码数字分配

> Cell: `IDAC_assigner_V3`(实例 I118)
> 父模块:QC_rectifier_CH0。数字控制(给 IDAC 送电流码)。
> 来源:../../QC_rectifier_CH0_PIidleIDAC.png

---

## 1. 功能

数字模块。当本通道被寻址(CH_NUMBER 选中、D_EN 有效)时,锁存全局 IDAC<4:0> 电流码,
输出 IDAC_PULSE<4:0>(= IDAC_CH1<4:0>)给 IDAC 的 D<4:0>,决定本通道电流幅度。

与 `Switch_assigner_V3` 并列:此模块管"电流多大",后者管"选哪个电极 + 极性"。

## 2. 接口

| Pin | 方向 | 连接 | 说明 |
|-----|------|------|------|
| IDAC<4:0> | IN | 全局 IDAC_INPUT<4:0> | 5-bit 电流码 |
| CH_NUMBER | IN | 本通道编号 | 通道选通 |
| D_EN | IN | 全局 D_EN | 写使能 |
| IDAC_PULSE<4:0> | OUT | → IDAC D<4:0>(net IDAC_CH1<4:0>) | 本通道电流码 |
| VDDL / VSS | PWR | | |

## 3. 关键点
- IDAC_PULSE 走线极短(assigner 紧贴 IDAC,版图相邻)
- one-channel-at-a-time 配置:仅被寻址通道更新,其余保持

## 4. MOS 尺寸
数字标准单元(版图 28×16.5µm,3 行 standard cell),尺寸由库固定。

## 5. 状态
✅ 接口已记(数字标准单元)。
