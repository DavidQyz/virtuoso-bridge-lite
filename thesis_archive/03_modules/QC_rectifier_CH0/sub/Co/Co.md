# Co (OUT_CAP_80p) — 输出储能电容

> Cell: `OUT_CAP_80p`(80 pF)
> 父模块:QC_rectifier_CH0。能量路径储能元件。
> 来源:../../QC_rectifier_CH0_SWCAPHbridgeSWassign.png

---

## 1. 功能

整流输出储能电容,稳定 MP_OUT 节点电压。switchV8 每周期对它充电,
H_bridge 从它取能驱动电极。

- **MOS + MIM 叠加**:同面积容值 ×2(vs Cesc 单一 MOS 或 MIM)
- 80 pF;版图最大单元(250×135µm,占 channel ~44%,硬面积约束)

## 2. 接口

| Pin | 连接 | 说明 |
|-----|------|------|
| V_POS | **MP_OUT** | 整流输出节点(switchV8 VOUT + H_bridge V_SUPPLY) |
| V_NEG | VSS | 地 |

## 3. 关键点
- MP_OUT 寄生电容只会"等效增大 Co",故该 net 走线长短不敏感
- 容值 + 调压整流共同决定 ripple:容值越大 ripple 越小,但面积代价高

## 4. MOS 尺寸
无源电容(MOS+MIM 叠层),非晶体管。版图尺寸 250×135µm。

## 5. 状态
✅ 接口/参数已记。
