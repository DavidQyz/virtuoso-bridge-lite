# 10_1 — 模块间连接关系 (Netlist)

> 每条 net 从哪个模块的哪个 pin 到哪个模块的哪个 pin。这是"谁连谁"的权威清单。
> 工作原理见 `10_2_single_channel.md`。来源:thesis_ppt/channel_layout_assembly__1_.md(已并入,待逐模块核对)。

---

## 1. 相位控制环路

```
V_ein ───────────────────────────────────→ switchV8(输入 AC)
V_ein ─→ comparator_newV4 (I123)            switchV8 输出 → Mp_out
Mp_out → comparator_newV4 (I123)                  ↓ cap(Co)并联至 VSS
         ↓ Vin
VCDL_tryc_v4 (I133)  IN: Vin(comparator OUT), Vb(PI 输出 Vc)  OUT: VOUT
         ↓
#ND2D1BWP7T (I132) NAND  IN1: Vin(直连 comparator), IN2: VOUT(VCDL)
         ↓ Vand_out → switchV8(控制整流开关 DSL 端)
```

## 2. 反馈控制环路

```
V_headroom(I_STIM 节点)
  ├─→ Idle_controller_nb (I108): V_HEADROOM 输入
  │      IN: V_EN_REF(bias), EN/nEN(comparator)   OUT: EN, nEN → comparator & PI(开/关)
  └─→ PI_controller_EN_mid_pos_nb_V3: 负输入端
         IN+: V_REF_OUT(bias_local, 75mV), IN: EN/nEN(Idle)
         OUT: Vc(=PL_OTA_CLAMP)→ VCDL Vb
```

## 3. 刺激路径

```
Mp_out(=V_SUPPLY)
  └─→ H_bridge_LVT_use
        IN: V_SUPPLY, EN_SW_PRE<7:0>(Switch_assigner I119), STIM_MODE(Switch_assigner)
        OUT: V_cout_p<7:0>→电极P, V_cout_n<7:0>→电极N, TO_CM→V_headroom(经 I83<7:0> bus)
                ↓
        IDAC_new_V5_for_sys_nb (I165)
          IN: D<4:0>(=IDAC_ch1<4:0>, IDAC_assigner I118), V_REF(bias_local 45mV),
              IDAC bias(IDAC_VB1/2, IDAC_OTA_VB1/2, GOMP_VGM)
          OUT: I_STIM(=V_headroom 节点)→ VSS
```

## 4. 数字配置路径

```
全局总线(来自 data_inputV2):
  IDAC<4:0>, CH_number, d_EN → IDAC_assigner_V3 (I118)
        OUT: IDAC_PULSE<4:0>=IDAC_ch1<4:0> → IDAC_new_V5 D<4:0>
  SW_number<7:0>, Stim_mode, CH_NUMBER, d_EN → Switch_assigner_V3 (I119)
        OUT: EN_SW_PRE<7:0> → H_bridge EN_SW;  STIM_MODE_PRE → H_bridge STIM_MODE
```

## 5. Bias 分配

```
bias_local (I128)
  IN: IDAC_VB2, IDAC_VB1(全局 bias)
  OUT: V_REF_OUT(75mV)→PI IN+;  V_REF(45mV)→IDAC;  IDAC_OTA_VB1/VB2→IDAC OTA;
       GOMP_VGM→IDAC cascode;  V_EN_REF(200mV)→Idle_controller
```

---

## 6. 关键 Net 走线属性(来自 routing_checklist)

| Net | 起点 → 终点 | 层 | 优先级/要求 |
|-----|------------|-----|------|
| V_C | PI_controller → VCDL Vb | M3 | ⚠️ 最高:直接控制 pulse 宽度 |
| MP_OUT | switchV8 → Co + H_bridge V_SUPPLY + comparator INN | M6 | 寄生等效增加 Co,长短无所谓 |
| V_HEADROOM (I_STIM) | H_bridge TO_CM → IDAC + PI + Idle | M4 | 模拟敏感,100fF 验证鲁棒 |
| V_SIN | 外部 → switchV8 + comparator INP | M3/M6 | 外部强驱动,13.56MHz RF |
| V_REF_OUT (75mV) | bias_local → PI IN+ | M3 | 模拟敏感 |
| V_REF (45mV) | bias_local → IDAC | M3 | 模拟敏感 |
| V_EN_REF (200mV) | bias_local → Idle | M3 | 模拟敏感 |

---

## 7. 状态
⏳ 待核对 — net 级连接已并入;各模块内部 pin 对应关系随 schematic 截图补全。
