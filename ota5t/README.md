# ota5t — tsmc18 模拟器件设计工作区

通过 virtuoso-bridge 在远程 Virtuoso/Spectre（IC618 + Spectre 18.1，tsmc18 BCD gen2）
上做的器件设计。**一个器件一个文件夹**，每个文件夹自包含：构建/仿真脚本、电路图
（YAML 权威源 + SVG/PNG）、表征数据与图、开发文档（README：尺寸/原理/性能）。

## 器件索引

| 文件夹 | 器件 | Virtuoso cell | 关键指标 | 文档 |
|---|---|---|---|---|
| [ota_5t/](ota_5t/) | 五管 OTA | test/OTA_5T ✅ | A0=39.6dB, GBW=16.9MHz, PM=87°, 36.8µW | [README](ota_5t/README.md) |
| [fc_ota/](fc_ota/) | 折叠共源共栅 PMOS 输入 OTA | （netlist 级） | A0=74.5dB, GBW=22.3MHz, PM=78°, ≈3.3µW, Vcm=0.3V | [README](fc_ota/README.md) |
| [comp_cg/](comp_cg/) | 共栅比较器（0-5V 输入） | test/COMP_CG ✅ | tprop=1.015ns@INN=1V, 全范围 0.74-2.77ns, 7-24µW | [README](comp_cg/README.md) |
| [comp_v2/](comp_v2/) | 双阈值比较器（V4 提速版） | test/COMP_V2 ✅ | tprop=0.923ns@INN=1V（−9%）, 高端 −27%, 功耗持平 | [README](comp_v2/README.md) |

## 目录约定

```
<device>/
  build_*.py        # Virtuoso schematic 构建脚本（net label 连接 + CDF sizing）
  run_*/ *_characterize.py   # Spectre testbench 与表征
  *_schematic.yaml  # 电路图权威源（改图先改 YAML 再渲染，不要手改 SVG）
  *.svg / *.png     # 电路图 + 表征图
  *.json            # 表征数据（图与 README 的数据源）
  <sim dirs>/       # Spectre psfascii 原始输出
  README.md         # 开发文档：尺寸表 / 工作原理 / 性能报告 / 复现命令
tools/
  render_schematic.py   # 通用 YAML→SVG/PNG 渲染器（输出落在 YAML 同目录）
  sch_explore.py / dbg_sch.py / verify_sch.py   # Virtuoso 侧调试工具
```

## 通用工作流

```powershell
# 0) bridge 在线（探活 / 启动见根目录与记忆中的启动清单）
uv run virtuoso-bridge status

# 1) 构建 schematic（写 test 库）
.venv/Scripts/python.exe ota5t/<device>/build_*.py

# 2) 表征（远程 Spectre，psfascii 回传本地解析）
.venv/Scripts/python.exe ota5t/<device>/<characterize>.py

# 3) 出图
.venv/Scripts/python.exe ota5t/tools/render_schematic.py ota5t/<device>/<x>_schematic.yaml
.venv/Scripts/python.exe ota5t/<device>/<figs>.py
```

## 工艺速查（tsmc18 BCD gen2）

| | 1.8V 核心管 | 5V 厚栅管 |
|---|---|---|
| Virtuoso cell | nmos2v_mac / pmos2v_mac | nmos5v_mac / pmos5v_mac |
| Spectre model | nch_mac / pch_mac | nch_5_mac / pch_5_mac |
| 默认 L | 180n | nmos 600n / pmos 500n |
| 最小单指 W | 220n | 220n |

模型库：`c018bcd_gen2_v1d6_usage.scs`，section `pre_simu` + `tt_lib`。

**手写 Spectre netlist 注意**：`w` = 总宽（宏内部按 w/nf 做 bin 检查），CDF instance
里存的是单指宽；`multi` 对应 CDF 的 simM。详见 comp_cg/README §5。
