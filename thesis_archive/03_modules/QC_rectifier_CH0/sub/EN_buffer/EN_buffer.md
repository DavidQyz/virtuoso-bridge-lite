# EN_buffer — CH0 专属 EN 观测缓冲

> Cell: `BUFFD3BWP7T`(标准单元 buffer,实例 I33)
> 父模块:QC_rectifier_CH0。**仅 CH0 有,CH1–7(残血版)没有。**
> 来源:../../QC_rectifier_CH0_ENbuffer.png

---

## 1. 功能

把通道内的 **CH0_EN** 信号(idle_controller 的 EN,反映该通道整流环开/关状态)
经 buffer 驱动后输出到 pad → **CH0_EN_BUFFED**,供片外观测。

这是 CH0 作为"满血/完全可观测通道"的特色:可以在外部实时看到该通道何时进入 idle(空载关断)。
CH1–7 不引出此信号(节省 pad)。

## 2. 接口

| Pin | 方向 | 连接 | 说明 |
|-----|------|------|------|
| I | IN | CH0_EN(idle_controller EN) | 待缓冲的使能信号 |
| Z | OUT | **CH0_EN_BUFFED** → pad | 观测输出 |
| VDDL / VSS | PWR | | |

## 3. 关键点
- BUFFD3 = drive strength 3 的标准 buffer,足以驱动 pad + 片外负载
- 与电极全独立引出一起,构成 CH0 的完整可观测性(debug/measurement 通道)

## 4. MOS 尺寸
标准单元(BUFFD3BWP7T),尺寸由库固定。

## 5. 状态
✅ 接口已记(数字标准单元)。
