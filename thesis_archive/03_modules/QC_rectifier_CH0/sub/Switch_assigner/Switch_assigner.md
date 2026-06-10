# Switch_assigner_V3 — 电极选择 / 极性数字控制

> Cell: `Switch_assigner_V3`(实例 I119)
> 父模块:QC_rectifier_CH0。数字控制(驱动 H_bridge 阵列)。
> 来源:../../QC_rectifier_CH0_SWCAPHbridgeSWassign.png

---

## 1. 功能

数字模块。锁存配置位,输出控制 8 路 H_bridge:
- **哪个 H 桥导通**(EN_SW_PRE<7:0>,one-hot)
- **正向 / 反向导通模式**(STIM_MODE_PRE)

仅当本通道被寻址(CH_NUMBER 选中、D_EN 有效)时更新。

## 2. 接口

| Pin | 方向 | 连接 | 说明 |
|-----|------|------|------|
| SW_NUMBER<7:0> | IN | 全局 SW_NUMBER_GB | 电极选择码 |
| STIM_MODE | IN | 全局 STIM_MODE_GB | 极性 |
| CH_NUMBER | IN | 本通道编号 | 通道选通 |
| D_EN | IN | 全局 D_EN | 写使能 |
| EN_SW_PRE<7:0> | OUT | → H_bridge EN_SW<7:0> | one-hot 选电极 |
| STIM_MODE_PRE | OUT | → H_bridge STIM_MODE(POST) | 极性 |
| VDD/VDDL/VSS | PWR | | |

## 3. 关键点
- one-hot 编码保证任意时刻仅一个 H 桥导通(电极 TDM)
- 与 IDAC_assigner_V3 并列:前者管"选哪个电极+极性",后者管"电流多大"

## 4. MOS 尺寸
标准单元数字逻辑(3 行 standard cell,版图 40×17.5µm),尺寸由库固定。

## 5. 状态
✅ 接口已记(数字标准单元)。
