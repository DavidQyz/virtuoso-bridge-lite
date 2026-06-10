# QC_rectifier_full — 8 通道核心

> 来源:figures/QC_rectifier_full.png(总体)、_symble.png(符号)、_gmDELSPI.png(GM+SPI)、
> _CH0.png(CH0 满血实例)、_CH1-7.png(通用通道+电极合并)、biasblock.png(全局 bias)
> 此层为 block-level,MOS 尺寸见各子模块 schematic。

---

## 1. 符号端口(QC_rectifier_full)

**顶部:** VDD、VDDL、SIN_P、SIN_N
**底部:** VSS
**左侧(输入):** CLK、DATA、DT_EN、I_BIAS_INPUT、IDAC_OTA_VB2
**右侧(输出):**
| 端口 | 位宽 | 说明 |
|------|------|------|
| CH0_P<7:0> / CH0_N<7:0> | 8+8 | CH0 满血:8 电极对全独立 |
| CH1_P<1:0> / CH1_N<1:0> | 2+2 | CH1 电极 4-by-4 合并 |
| CH2…CH7 _P<1:0> / _N<1:0> | 各 2+2 | 同上 |
| CH0_EN_BUFFED | 1 | CH0 的 Idle EN 缓冲输出(可观测) |
| DATA_SLICE<1:0> | 2 | 数字部分(data_inputV2)直接引出 |

> 注意符号上 CH0 是 `<7:0>`(8 位独立),CH1–7 是 `<1:0>`(已合并)。印证 CH0 满血、CH1–7 合并。

---

## 2. 内部实例清单

| 实例 | Cell | 数量 | 功能 |
|------|------|------|------|
| GM 块 | `GM`(+ DELAY 块) | 1 | SIN_P/SIN_N 半波处理 → 供电轨 |
| 数字 | `data_inputV2` (I8) | 1 | SPI 解码 → 配置总线 + DATA_SLICE |
| 全局 bias | `bias_block_V2` (I16) | 1 | I_BIAS_INPUT → 全部 bias 电压 |
| CH0 | `QC_rectifier_CH0` (I19) | 1 | 满血单通道,8 电极全引出 + EN |
| CH1–7 | `QC_rectifier` | 7 | 通用单通道,电极内部合并 |

---

## 3. GM + 数字 SPI 部分(_gmDELSPI.png)

```
SIN_P, SIN_N ──→ [GM]──(EN)──→ 半波供电轨(→ 各通道 SIN 输入)
                   ↑
DT_EN, I_EN ──→ [DELAY 块 (DELAY007?)] ──→ GM EN

CLK ─┐
DATA ─┼─→ [data_inputV2 (I8)] ──→ CHANNEL_NUMBER<7:0>
DT_EN ┘                          SW_NUMBER_GB<7:0>
                                 STIM_MODE_GB
                                 IDAC_GB<4:0>
                                 D_EN
                                 DATA_SLICE<1:0>  → 输出
                                 CH0_EN_BUFFED     → 输出
```

⚠️ GM 内部拓扑、DELAY 块作用待确认(见下方问题)。

---

## 4. 单通道实例化(配置总线扇出)

**CH0(_CH0.png,`QC_rectifier_CH0` I19):**
- 顶:VSS、SIN_P(=V_SIN)、VDDL
- 配置输入(左):CH_NUMBER←CHANNEL_NUMBER<0>、SW_NUMBER<7:0>←SW_NUMBER_GB、STIM_MODE←STIM_MODE_GB、IDAC<4:0>←IDAC_GB、D_EN
- **全局 bias 输入(底,白字 net 名):** IDAC_VB1、IDAC_VB2、IDAC_OTA_VB1、IDAC_OTA_VB2、COMP_VCM、PI_OTA_CLAMP、V_EN_REF
- **通道内本地生成(bias_local,非端口):** V_REF_OUT(75mV)、V_REF(45mV)
- 输出(右):V_OUT_P<7:0>→CH0_P<7:0>、V_OUT_N<7:0>→CH0_N<7:0>;CH0_EN_BUFFED

**CH1–7(_CH1-7.png,`QC_rectifier`):**
- 同样的配置/bias 输入,CH_NUMBER←CHANNEL_NUMBER<1..7>
- 输出 V_OUT_P<7:0>→CHx_P_PRE<7:0>,经合并网络:
  - CHx_P_PRE<7:4> → CHx_P<1>;CHx_P_PRE<3:0> → CHx_P<0>(4 电极并 1 pad)
  - N 侧同理 → CHx_N<1:0>

> **CH0 vs CH1–7 唯一区别:CH0 把 8 电极全独立引出**(+ EN 缓冲),CH1–7 把 8 电极 4-by-4 合并成 2 对 pad。核心电路相同。

---

## 5. 全局 Bias(biasblock.png,`bias_block_V2` I16)

- 输入:VSS、VDDL、**I_BIAS_INPUT**(片外电阻设定基准电流)
- 输出(分发到所有通道,白字 net):IDAC_VB1、IDAC_VB2、IDAC_OTA_VB1、IDAC_OTA_VB2、COMP_VCM、PI_OTA_CLAMP、V_EN_REF
  > 注:红字(COMP_VGM、PI_ERR_CLAMP 等)是 bias_block_V2 的内部 pin 名;白字才是对外 net 名。

> ✅ **两级 bias 架构:** 最初全部 bias 为全局(`bias_block_V2`),后来把 **V_REF_OUT(75mV)、V_REF(45mV)** 改为通道内 `bias_local` 本地生成(这两个是最敏感的低压基准,本地化减少长走线噪声)。
> 其余 bias(IDAC_VB1/2、IDAC_OTA_VB1/2、COMP_VCM、PI_OTA_CLAMP、V_EN_REF)仍由全局 bias_block_V2 分发。

---

## 6. SIN 功率分配(已确认)

- CH0–3:SIN_P 半波 | CH4–7:SIN_N 半波
- ✅ CH4–7 **复用同一 `QC_rectifier` cell,把 SIN_N 接到原本接 SIN_P 的引脚**(无需单独画 N 版通道)

---

## 7. 命名(已确认)

- `COMP_VCM`(不是 COMP_VGM/GOMP_VGM)
- `PI_OTA_CLAMP`(不是 PL_ERR_CLAMP/PI_ERR_CLAMP)

## 8. 仍待确认(后续介绍时补)

- GM 内部拓扑 + DELAY 块作用 + I_EN 来源 → **用户将在专门介绍 GM 时讲解**
- 两级 bias 的精确划分:哪些信号在全局 `bias_block_V2`、哪些在通道内 `bias_local` → 逐模块确认

---

## 9. 截图索引

| 文件 | 内容 |
|------|------|
| `./QC_rectifier_full.png` | 总体(8 通道 + bias + GM/数字布局) |
| `./QC_rectifier_full_symble.png` | 符号(端口) |
| `./QC_rectifier_full_gmDELSPI.png` | GM + DELAY + data_inputV2 |
| `./QC_rectifier_full_CH0.png` | CH0 满血实例 |
| `./QC_rectifier_full_CH1-7.png` | 通用通道 + 电极合并网络 |
| `./QC_rectifier_biasblock.png` | 全局 bias_block_V2 |

## 10. 状态
⏳ 从截图提取 — 待第 7 节问题确认。
