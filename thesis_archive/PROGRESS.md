# 📋 进度表 — 技术存档 & 面试 PPT

> **每次重开会话先读这个文件**,就能回忆进度。Claude 也会在每次会话末尾更新它。
> 配套总目录见 `00_INDEX.md`;单通道权威口径见 `10_integration/10_2_single_channel.md`。
> 最后更新:**2026-06-09**

---

## 🎯 总目标

1. 构建完整**个人技术存档**(`thesis_archive/`)作为单一信息源 —— 可整体交接给其他项目
2. 在此基础上**派生面试技术 PPT**

## 📍 当前阶段

**自顶向下建模块文档** —— symbol 级已基本完成(top → full → CH0 全 13 子模块),
**下一步:进各模块内部晶体管级,补每个 MOS 的 W/L。**

---

## ✅ 进度总览

| 层 | symbol/接口 | 内部 MOS 尺寸 | 备注 |
|----|:-----------:|:-------------:|------|
| top_level | ✅ | — | 端口 + 两大块 |
| QC_rectifier_full | ✅ | — | 5 类实例 + 两级 bias + SIN 4+4 |
| QC_rectifier_CH0(单通道) | ✅ 13/13 | 🔲 | 三条路径全连通 |
| GM | 🔲 | 🔲 | 在 full 内部,用户要专门讲 |
| data_inputV2 | 🔲 | 🔲 | SPI 解码 |
| bias_block_V2(全局) | ⏳ | 🔲 | 符号已记 |
| CH1–7(残血版) | ⏳ | — | 复用 CH0,电极合并,差异待补 |

---

## 📦 CH0 子模块 checklist(13 个)

> ✅=完成 ⏳=symbol已记/待内部 🔲=没开始 | 第二列 = 内部晶体管级 MOS 尺寸

| 子模块 | symbol/接口 | 内部 MOS | Cell |
|--------|:-----------:|:--------:|------|
| comparator | ✅ | ✅ | comparator_new_4_for_use_nb (I123) |
| VCDL | ✅ | ⏳ | VCDL_try_v4 (I133);M2 PMOS W 待确认 |
| NAND | ✅ | — | ND2D1BWP7T (标准单元) |
| switchV8 | ✅ | ✅ | switchV8 (I98) |
| Co | ✅ | — | OUT_CAP_80p (无源) |
| H_bridge ×8 | ✅ | ✅ | H_bridge_LVT_use (I83<7:0>) |
| Switch_assigner | ✅ | — | Switch_assigner_V3 (I119,标准单元) |
| PI_controller | ✅ | ✅ | PI_controller_EN_mid_pow_nb_V3 (I126) |
| Idle_controller | ✅ | ✅ | idle_controller_nb (I108);OTA=ota_paperV4_nb_V2 |
| IDAC | ✅ | ✅ | IDAC_new_V5_for_sys_nb (I105) |
| IDAC_assigner | ✅ | — | IDAC_assigner_V3 (I118,标准单元) |
| bias_local | ✅ | ⏳ | bias_local (I128);PMOS 镜 W/L 待大图确认 |
| EN_buffer(CH0专属) | ✅ | — | BUFFD3BWP7T (I33,标准单元) |

**内部 MOS 待补的模拟模块(6个):** comparator、VCDL、switchV8、H_bridge、PI、Idle、IDAC、bias_local
(标准单元/无源的不需要补)

---

## 🔜 下一步(按优先级)

1. **🥇 IDAC 内部** —— 最大贡献点(45mV↓82%),面试/答辩重点,最需你本人在场确认
2. **🥈 PI_controller 内部** —— 闭环核心 + 补偿网络
3. switchV8 内部(互补 PMOS/NMOS 功率管)
4. comparator / Idle / bias_local / H_bridge 内部
5. **GM、data_inputV2** 两块(QC_rectifier_full 级)
6. 收尾:CH1–7 残血差异、`10_3` 整系统、04/05/06 核对转 ✅

---

## 🔒 已锁定的关键事实(别再纠结)

- **读图约定:** 白字=全局 net 名(权威),红字=内部 pin 名
- **三个电压点:** 基线 250mV / V_REF 45mV(↓82%,CV headline)/ headroom 75mV(PI 工作点)—— 不同节点,别混
- **两级 bias:** 全局 bias_block_V2 + 通道内 bias_local(只生成 V_REF_OUT 75mV / V_REF 45mV)
- **SIN 分配:** CH0–3→SIN_P,CH4–7→SIN_N
- **闭环:** PI→V_C→VCDL(VB,td)→NAND(pulse)→switchV8→Co→V_headroom→回PI;13.56MHz 采样,带宽<6.78MHz
- **CV 不用改** —— 45mV↓82% 保留

---

## 📒 会话日志

### 2026-06-08
- 搭好 thesis_archive 骨架 + 自顶向下建模块文档
- top_level(2图)、QC_rectifier_full(6图)、QC_rectifier_CH0 全 13 子模块(7图)symbol 级完成
- 确立读图约定、两级 bias、SIN 4+4、CH0/CH1–7 差异、命名(COMP_VCM/PI_OTA_CLAMP/VB=V_C)
- 单通道工作原理对外定稿(`10_2`),用户逐条核对全部正确
- 敲定三个电压点辨析(250/45/75mV),CV 维持 45mV↓82%
- 截图归档:figures/ 15 张,模块文件夹自包含
- CH0 文档加第 7 节「工作原理(对外讲解版)」,图文混排(7 张图嵌入叙述)
- `10_2` 开头加「信号流程图(增强版 Mermaid)」—— 四色路径,比原 PPT 补全 bias_local/双输入/8×TDM/互补NMOS/闭环/中心节点
  - ⚠️ VS Code 看 Mermaid 需装插件「Markdown Preview Mermaid Support」;GitHub 自动渲染
- 🔜 待办:数字配置流程图(对应原 slide 2 更新版)单出一张

### 2026-06-09
- **单通道流程图重做**:放弃 Mermaid(dagre 曲线、子图发散),改**手绘 SVG** `figures/single_channel_flow.svg`
  - 复刻原 PPT 风格:网格对齐 + 真·横平竖直(直角走线)+ 三色功能(🟢Power/🔵Control/🟣Enable-Idle)+ 顶/底专用反馈通道 + 柔和投影
  - 优点:VS Code 直接预览(无需插件)、粘进 PPT 是**矢量可编辑**、GitHub 也渲染
  - 细节:OUTCAP(原 Co,80pF)挂在 Mp_out 节点中点;PI 上移让 Idle 一条横线喂 PI+Comp;
    **IDAC 控流可视化** = 电流源符号 `I_stim 0–155 µA` + `code<4:0>` 数字输入 + 框内 `5-bit`
  - 用户逐项核对定稿;已嵌入 `10_2_single_channel.md`(第0节)和 `QC_rectifier_CH0.md`(7.2);删除 Mermaid 草稿
  - 装了 MPE 插件 `shd101wyy.markdown-preview-enhanced`(Mermaid 预览闪退问题的替代),但 SVG 本身不依赖它
- 🔜 待办(未变):数字配置流程图(原 slide 2 更新版)单出一张;各模拟模块内部 MOS 尺寸(优先 IDAC)

### 2026-06-09(续)
- **IDAC 内部 OTA(ota_paperV4_nb_V2)完整文档化**
  - 全部 ~20 只晶体管尺寸记录完毕:输入对(M1/M2)、尾电流镜(M3/M4/M53/M54)、折叠 NMOS cascode(M5–M8/M23/M24)、自偏置 PMOS 负载(M9–M12)、本地 VB1/VB2 生成(M14/M16/M17/M19/M20/M21)、EN 开关(M27)
  - 工作原理七步讲解(PMOS 输入对必要性、折叠 cascode 信号传递、自偏置 PMOS PSRR 原理、VB1/VB2 本地生成、EN 关断、闭环稳态)
  - 拆分为独立子模块:`sub/IDAC/sub/ota_paperV4_nb_V2/ota_paperV4_nb_V2.md`;IDAC.md Section 4.4 改为指针
- 🔜 **待存截图:**`figures/OTA_IDAC_right.png`(右侧 NMOS cascode + PMOS 负载)、`figures/OTA_IDAC_bias.png`(VB1/VB2 bias 生成)
- 🔜 **下一模块:**PI\_controller 内部 MOS 尺寸

### 2026-06-09(续2)
- **PI\_controller OTA 全部晶体管记录完毕**
  - 输入对:M1/M2(1µm/800nm/8f total,同 IDAC OTA)
  - 参考电流:M37/M40(W=2µm,IDAC OTA 的 2×,尾电流翻倍 → PI OTA 更快)
  - 尾电流镜:M3(1µm/1µm/6f);EN 开关:M18(685nm/180nm PMOS)
  - VB1/VB2 生成:M17(1f)/M21/M20(≈400nm/1µm)/M14(2f,vs IDAC 1f)/M16/M19(≈300nm/6µm)
  - 折叠路径:M23(gate=EN)/M24(gate=N\_EN)双路控制;M5/M6(520nm/1µm,vs IDAC 230nm)
  - NMOS cascode:M7/M8(340nm/1µm/2f,vs IDAC 220nm/1f)
  - PMOS 自偏置负载:M9/M10/M11/M12 四管同尺寸(1.2µm/800nm/2f,vs IDAC 340nm)
  - PI OTA 与 IDAC OTA 同拓扑,整体电流约 2×,PMOS 负载宽约 3.5×
- ✅ PI\_controller 内部 MOS 尺寸全部完成
- ✅ **comparator** 内部 MOS 全记:M0/M1(PMOS5V 500nm/500nm/4f 输入)+ M2/M3(NMOS5V CG 220nm/600nm)+ M8(EN 开关)+ INV1(M6/M5 5V 非对称)+ INV2(M21/M20 2V 非对称)
- ✅ **Idle\_controller** 完成:OTA = ota\_paperV4\_nb\_V2(同 IDAC),指针已记;buffer 链为标准单元
- ✅ **switchV8** 完成:PMOS 2µm/500nm/5f(×5=10µm effective)+ 互补 NMOS 2µm/500nm/3f;注意设计笔记值与电路图不符,以电路图为准
- ✅ **bias\_local** 完成:PMOS 电流镜 + poly 电阻链生成 75mV/45mV;工作原理已记
- ✅ **工作原理补全**:comparator / VCDL / Idle\_controller / switchV8 / bias\_local 均已加"工作原理(对外讲解版)"章节,嵌入图片,风格同 IDAC
- 🔜 **下一模块:** H\_bridge(最后一个模拟模块)

### 2026-06-10
- ✅ **H\_bridge** 全部完成(延续上一会话)
  - 结构:4 管 LVT 5V(PMOS 高侧 Q1/Q2 + NMOS 低侧 Q3/Q4)+ Level Shifter + 逻辑解码 + buffer fan-out
  - MOS 尺寸确认:PMOS/NMOS 均 W=2µm / L=1.6µm / fingers=8 / totalM=8,有效宽度 16µm
  - 对称 sizing → 双相正/反向电荷等量 → 安全神经刺激;L=1.6µm 长沟道抑制 7 个未选通桥漏电
  - 工作原理四步:TDM 选通 / 双相极性控制 / LVT 必要性 / 上下游节点连接
- ✅ **CH0 全部模拟模块收尾** —— comparator / VCDL / switchV8 / H\_bridge / PI\_controller / Idle\_controller / bias\_local 内部结构 + MOS 尺寸 + 工作原理全部文档化
- ⏳ **两个小尾巴待大图确认:**
  - VCDL M2(PMOS)W 值
  - bias\_local PMOS 电流镜 W/L
- 🔜 **下一步(下次会话):** GM、data\_inputV2、CH1–7 差异、`10_3` 整系统整合文档

### (下次填这里)
