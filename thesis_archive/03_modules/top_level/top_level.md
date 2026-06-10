# Top Level — 芯片顶层

> 来源:figures/Top_level_with_pads.png(含 pad cells)、figures/Top_level_with_pads_1.png(无 pad cells,端口更清晰)
> 此为 block-level 原理图,无单独 MOS 尺寸标注;MOS 尺寸见各子模块 schematic。

---

## 1. 顶层实例化清单

| 实例 | Cell | 功能 |
|------|------|------|
| pad ring inst | `PAD_RING_WITH_SEALBRING` | 全部 IO pad + ESD + seal ring;左侧连 bond wire |
| core inst | `QC_rectifier_full` | 8 通道核心:GM + 8×单通道整流 + 刺激 + 数字配置 |

顶层本身无额外逻辑,仅连接两大块。**GM 在 `QC_rectifier_full` 内部,顶层看不到。**

---

## 2. 顶层端口(外部 bond wire 侧)

从 `Top_level_with_pads.png` 左侧 pad cells 读取:

**数字 IO(右侧 SPI 边):**
| Port | 方向 | 说明 |
|------|------|------|
| PAD_CLK | IN | SPI 时钟 |
| PAD_DATA | IN | SPI 数据输入 |
| PAD_DT_EN | IN | SPI 使能(D_EN) |
| DATA_SLICE<1:0> | OUT | 输出缓冲数据(to FPGA) |

**模拟 Bias:**
| Port | 方向 | 说明 |
|------|------|------|
| I_BIAS_INPUT | IN | 全局电流 bias 输入(片外电阻) |
| IDAC_OTA_VB2 | IN | IDAC OTA bias 电压(片外可选) |

**RF 功率:**
| Port | 方向 | 说明 |
|------|------|------|
| SIN_P | IN | 13.56 MHz 差分功率正 |
| SIN_N | IN | 13.56 MHz 差分功率负 |

**电极输出(8 通道):**
| Port | 说明 |
|------|------|
| CH0_P<...>, CH0_N<...> | **CH0 = 满血版**:8 电极对全部独立引出(顶边)+ EN 信号引出 |
| CH1_P/N … CH7_P/N | CH1–7:每通道 8 电极**四个一组**合并到一个 pad → 每通道 2×P + 2×N |

**电极合并规则:** CH1–7 内 8 个电极,P 侧 4 个合并、N 侧 4 个合并(实际是 4-by-4 并到 pad),仅 CH0 保留全部独立可观测。

**电源:**
| Net | 说明 |
|------|------|
| VDD | 1.8V 数字/模拟电源 |
| VSS | 地 |
| VDDH | 5V,供 SIN_P/N 的 5V IO pad 环 |

---

## 3. 两大块之间的关键连线

从 `Top_level_with_pads_1.png` 中间走线读取:

| Net | PAD_RING 侧 | QC_rectifier 侧 | 说明 |
|-----|-------------|-----------------|------|
| CLK | PAD_CLK(buffered) | CLK | SPI 时钟 |
| DATA | PAD_DATA(buffered) | DATA | SPI 数据 |
| DT_EN / dt_en | PAD_DT_EN(buffered) | DT_EN | SPI 使能 |
| I_BIAS_INPUT | pad | BIIAS / I_BIAS_INPUT | 全局 bias |
| IDAC_OTA_VB2 | pad | IDAC_OTA_VB2 | IDAC OTA bias |
| EN_BUFF_BUFFED | QC → PAD_RING | pad out | CH0 的 Idle_EN 缓冲输出(可观测) |
| PAD_DATA_SLICE<1:0> | QC → PAD_RING | DATA_SLICE out | **直接从数字部分(data_inputV2)引出**,非 CH0 |
| SIN_P / SIN_N | pad | SIN_P/N per channel | RF 功率,每通道共享 |
| CH*_P/N | QC electrode out → PAD_RING | H-bridge output | 电极驱动 |

---

## 4. 层次关系图

```
chip_top
├── PAD_RING_WITH_SEALBRING
│   ├── ~72 个 IO pad cells(含 ESD、5V pad、bare pad)
│   └── seal ring
└── QC_rectifier_full
    ├── data_inputV2        (SPI → 配置总线)
    ├── bias_global         (I_BIAS → 各通道 bias)
    ├── GM                  (SIN_P/N 半波分离,在此层内部,⚠️ 拓扑待确认)
    └── QC_rectifier ×8     (单通道,见 03_modules/QC_rectifier/)
        ├── switchV8
        ├── comparator_newV4
        ├── VCDL_tryc_v4
        ├── NAND (ND2D1BWP7T)
        ├── PI_controller_EN_mid_pos_nb_V3
        ├── Idle_controller_nb
        ├── bias_local
        ├── IDAC_new_V5
        ├── IDAC_assigner_V3
        ├── H_bridge_LVT_use
        ├── Switch_assigner_V3
        └── Co (MOS+MIM, 80pF)
```

---

## 5. 已确认

- ✅ 核心 cell 名 = `QC_rectifier_full`
- ✅ GM 在 `QC_rectifier_full` 内部,top-level 看不到
- ✅ DATA_SLICE / EN_BUFF_BUFFED 从 **CH0** 专门引出(CH0 = 完全可观测通道)

- ✅ DATA_SLICE 直接从数字部分(data_inputV2)引出,非 CH0
- ✅ **SIN 功率分配:CH0–3 用 SIN_P,CH4–7 用 SIN_N**(GM 半波分离的体现)
- ✅ 电极合并:CH0 全独立引出 + EN;CH1–7 各 4 电极一组并到 pad

待下一层确认:
- [ ] `QC_rectifier_full` 内部:GM、data_inputV2、bias_global、8×QC_rectifier 的精确实例名与连接
- [ ] GM 如何从 SIN_P/N 生成两组半波供电轨

---

## 6. 截图索引

| 文件 | 内容 |
|------|------|
| `./Top_level_with_pads.png` | 含 pad cells 全视图 |
| `./Top_level_with_pads_1.png` | 无 pad cells,端口/走线更清晰 |

## 7. 状态
⏳ 从截图提取 — 待核对精确 cell 名和 GM 位置。
