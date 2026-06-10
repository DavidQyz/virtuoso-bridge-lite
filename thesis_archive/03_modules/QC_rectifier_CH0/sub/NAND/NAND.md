# NAND — control pulse 生成

> Cell: `ND2D1BWP7T`(标准单元,实例 I132)
> 父模块:QC_rectifier_CH0。相位控制链第 3 级。
> 来源:../../QC_rectifier_CH0_compVCDLNAND.png(symbol 级)

---

## 1. 功能

把"直连"信号 V_IN 与"经 VCDL 延迟反相"的 V_OUT 做 NAND:
- V_IN 上升沿到、V_OUT 尚未翻转的 td 窗口内 → 输出低 → 产生**宽度 = td 的低有效 control pulse**
- 该脉冲 → switchV8 控制整流开关导通时间 → 决定每周期对 Co 的充电量

## 2. 接口

| Pin | 方向 | 连接 | 说明 |
|-----|------|------|------|
| A1 | IN | V_IN(comparator OUT,直连) | |
| A2 | IN | V_OUT(VCDL OUT,延迟) | |
| ZN | OUT | **V_AND_OUT** | → switchV8(整流开关控制) |
| VDDL / VSS | PWR | | 1.8V / 地 |

## 3. 关键点
- 标准单元(TSMC 7-track,BWP7T 库),非定制
- 脉冲宽度 = VCDL 延迟 td,由 PI 闭环动态调节

## 4. MOS 尺寸
标准单元(ND2D1BWP7T),尺寸由库固定,不自定义。

## 5. 状态
✅ symbol/接口已记(标准单元,无需内部图)。
