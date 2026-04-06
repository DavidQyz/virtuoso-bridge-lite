#!/usr/bin/env python3
"""
scan_gmid.py
============
自动化扫描 NMOS/PMOS 的 gm/ID 特征数据，输出与
Matlab_GmId_GUI_ByZJJ 工具包格式相同的 CSV 文件。

扫描方式（与 PDF Readme 一致）：
  主扫描：Vg 从 0 → 1.8V，步长 0.01V
  参数扫描：ll 从 200n 到 2.4u（16 个长度）
  输出8个参数：Cdd_Cgg, Cgd_Cgg, ft, gm_gds, gm_Id, Id_W, Vdsat, Vgs_Vth
  Vds扫描：Vd 0.2→0.65（步长0.05），Vg 0→1.8（步长0.05）
  输出2个参数：gm_Id, gm_gds

使用方法：
  1. 先确认 PDK_MODELS_PATH（VM 上的 scs 文件路径）
  2. 确保虚拟机已启动，bridge 已连接（uv run virtuoso-bridge start）
  3. 运行: uv run python scripts/gmid/scan_gmid.py

输出：scripts/gmid/data/tsmc018/ 文件夹，内含与原始工具包格式相同的 CSV 文件
"""

from __future__ import annotations
import os
import csv
import math
from pathlib import Path

# ════════════════════════════════════════════════════════════════════════════
#  配置区（根据实际情况修改）
# ════════════════════════════════════════════════════════════════════════════

# VM 上 PDK 模型文件路径（从 Virtuoso 导出的 netlist 第一行 include 里复制）
PDK_MODELS_PATH = "/opt/tsmc018rf/models/spectre/toplevel.scs"   # ← 修改为实际路径
PDK_SECTION     = "TT"                                            # ← tt/ss/ff/...

VDD  = 1.8   # V
W_CH = 1e-6  # 特征化宽度 1µm（与 PDF 中 w=1u 一致）

# 沟道长度扫描向量（与 PDF 一致：200n 到 2.4u）
LL_LIST = [
    2e-7, 3e-7, 4e-7, 5e-7, 6e-7, 7e-7, 8e-7, 9e-7,
    1e-6, 1.2e-6, 1.4e-6, 1.6e-6, 1.8e-6, 2e-6, 2.2e-6, 2.4e-6
]

# 主扫描：Vg 0→1.8V，步长 0.01V
VG_START = 0.0
VG_STOP  = 1.8
VG_STEP  = 0.01

# Vds 扫描：Vd 0.2→0.65，步长 0.05
VD_START = 0.2
VD_STOP  = 0.65
VD_STEP  = 0.05

# Vds 扫描时 Vg 步长改为 0.05
VG_STEP_VDS = 0.05

# 固定 Vd（主扫描用，取 VDD/2）
VD_MAIN = VDD / 2

OUT_DIR = Path(__file__).parent / "data" / "tsmc018"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ════════════════════════════════════════════════════════════════════════════
#  Netlist 生成
# ════════════════════════════════════════════════════════════════════════════

def _nmos_netlist(ll: float, vd: float, vg_start: float, vg_stop: float,
                  vg_step: float) -> str:
    return f"""// NMOS gm/ID characterization  ll={ll:.3g}  Vd={vd}
simulator lang=spectre
global 0
include "{PDK_MODELS_PATH}" section={PDK_SECTION}

parameters Vg=0

MN0 (Vdn Vgn 0 0) nch l={ll:.6g} w={W_CH:.6g} m=1 fingers=1
vgn (Vgn 0) vsource type=dc dc=Vg
vdn (Vdn 0) vsource type=dc dc={vd}

dc1 dc param=Vg start={vg_start} stop={vg_stop} step={vg_step}
save MN0:oppoint
saveOptions options save=selected
"""

def _pmos_netlist(ll: float, vd: float, vg_start: float, vg_stop: float,
                  vg_step: float) -> str:
    # PMOS：source 接 VDD，gate 从 VDD 扫到 0（Vg 代表 gate 电位）
    return f"""// PMOS gm/ID characterization  ll={ll:.3g}  Vd={vd}
simulator lang=spectre
global 0
include "{PDK_MODELS_PATH}" section={PDK_SECTION}

parameters Vg={VDD}

MP0 (Vdp Vgp vdd vdd) pch l={ll:.6g} w={W_CH:.6g} m=1 fingers=1
vgp (Vgp 0)  vsource type=dc dc=Vg
vdp (Vdp 0)  vsource type=dc dc={VDD - vd}
vdd (vdd 0)  vsource type=dc dc={VDD}

dc1 dc param=Vg start={VDD - vg_start} stop={VDD - vg_stop} step=-{vg_step}
save MP0:oppoint
saveOptions options save=selected
"""

# ════════════════════════════════════════════════════════════════════════════
#  结果提取
# ════════════════════════════════════════════════════════════════════════════

def _extract_oppoint(data: dict, mos_type: str) -> dict[str, list]:
    """
    从 Spectre result.data 里提取操作点参数。
    返回 dict，key 是参数名，value 是按 Vg 排列的列表。

    Spectre 操作点信号名可能是 "MN0:gm" 或 "dc_MN0:gm" 等，这里自动探测前缀。
    """
    inst = "MN0" if mos_type == "nmos" else "MP0"

    def _find(suffix: str) -> list:
        for prefix in ["", "dc_"]:
            key = f"{prefix}{inst}:{suffix}"
            if key in data:
                return list(data[key])
        # 备选：信号名不含实例名
        for k, v in data.items():
            if suffix in k.lower():
                return list(v)
        return []

    vg_raw   = data.get("dc_Vg", data.get("Vg", []))
    id_raw   = _find("id")
    gm_raw   = _find("gm")
    gds_raw  = _find("gds")
    cgg_raw  = _find("cgg")
    cgd_raw  = _find("cgd")
    cdd_raw  = _find("cdd")
    vdsat_raw= _find("vdsat")
    vth_raw  = _find("vth")

    rows = []
    for i, vg in enumerate(vg_raw):
        def g(arr):
            return arr[i] if i < len(arr) else float("nan")

        id_   = abs(g(id_raw))
        gm_   = abs(g(gm_raw))
        gds_  = abs(g(gds_raw))
        cgg_  = abs(g(cgg_raw))
        cgd_  = abs(g(cgd_raw))
        cdd_  = abs(g(cdd_raw))
        vdsat = g(vdsat_raw)
        vth   = g(vth_raw)

        # PMOS：Vg 在 netlist 里是 VDD→0 扫描，X 轴转成 VSG = VDD - Vg
        x = (VDD - float(vg)) if mos_type == "pmos" else float(vg)

        rows.append({
            "x":       x,
            "gm_Id":   gm_ / id_  if id_ > 1e-15 else float("nan"),
            "gm_gds":  gm_ / gds_ if gds_ > 0   else float("nan"),
            "Id_W":    id_ / W_CH,
            "ft":      gm_ / (2 * math.pi * cgg_) if cgg_ > 0 else float("nan"),
            "Cdd_Cgg": cdd_ / cgg_ if cgg_ > 0 else float("nan"),
            "Cgd_Cgg": cgd_ / cgg_ if cgg_ > 0 else float("nan"),
            "Vdsat":   abs(vdsat) if mos_type == "pmos" else vdsat,
            "Vgs_Vth": abs(x - vth),
        })

    return rows

# ════════════════════════════════════════════════════════════════════════════
#  CSV 输出（与 GmId_GUI 格式完全一致）
# ════════════════════════════════════════════════════════════════════════════

PARAMS_MAIN = ["Cdd_Cgg", "Cgd_Cgg", "ft", "gm_gds", "gm_Id", "Id_W", "Vdsat", "Vgs_Vth"]
PARAMS_VDS  = ["gm_Id", "gm_gds"]

def _write_csv(out_path: Path, param: str, mos_prefix: str,
               ll_list: list, all_rows: list[list[dict]]):
    """
    写一个 CSV 文件。
    all_rows[i] = 第 i 个 L 的行列表（每行含 x + param）
    """
    header = []
    for ll in ll_list:
        header.append(f"{mos_prefix}_{param} (ll={ll:.6g}) X")
        header.append(f"{mos_prefix}_{param} (ll={ll:.6g}) Y")

    n_rows = max(len(r) for r in all_rows)

    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for i in range(n_rows):
            row = []
            for rows in all_rows:
                if i < len(rows):
                    row.append(rows[i]["x"])
                    row.append(rows[i].get(param, ""))
                else:
                    row.extend(["", ""])
            writer.writerow(row)

    print(f"  → {out_path.name}")


def _write_vds_csv(out_path: Path, param: str, mos_prefix: str,
                   vd_list: list, ll_list: list,
                   vds_data: list[list[list[dict]]]):
    """
    写 Vds 扫描的 CSV。
    vds_data[vd_idx][ll_idx] = 该 Vd/L 组合的行列表
    """
    header = []
    for vd in vd_list:
        for ll in ll_list:
            header.append(f"{mos_prefix}_{param} (Vd={vd:.2f}, ll={ll:.6g}) X")
            header.append(f"{mos_prefix}_{param} (Vd={vd:.2f}, ll={ll:.6g}) Y")

    n_rows = max(
        len(rows)
        for vd_group in vds_data
        for rows in vd_group
        if rows
    )

    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for i in range(n_rows):
            row = []
            for vd_group in vds_data:
                for rows in vd_group:
                    if i < len(rows):
                        row.append(rows[i]["x"])
                        row.append(rows[i].get(param, ""))
                    else:
                        row.extend(["", ""])
            writer.writerow(row)

    print(f"  → {out_path.name}")

# ════════════════════════════════════════════════════════════════════════════
#  主流程
# ════════════════════════════════════════════════════════════════════════════

def scan_one_type(sim, mos_type: str, work_base: Path):
    """
    扫描 nmos 或 pmos 全套参数，保存 CSV。
    """
    prefix = "nch18" if mos_type == "nmos" else "pch18"
    nl_fn  = _nmos_netlist if mos_type == "nmos" else _pmos_netlist

    print(f"\n{'='*60}")
    print(f"  {mos_type.upper()} 主扫描（{len(LL_LIST)} 个 L，Vg 步长 {VG_STEP}V）")
    print(f"{'='*60}")

    # ── 主扫描：对每个 L 跑一次 DC ───────────────────────────────────────
    main_data: list[list[dict]] = []   # [ll_idx][row]

    for ll in LL_LIST:
        ll_nm = round(ll * 1e9)
        print(f"  L = {ll_nm} nm ...", end=" ", flush=True)

        nl_path = work_base / f"{mos_type}_L{ll_nm}n_main.scs"
        nl_path.write_text(nl_fn(ll, VD_MAIN, VG_START, VG_STOP, VG_STEP))

        result = sim.run_simulation(nl_path, {})
        if not result.ok:
            print(f"FAIL: {result.errors[:1]}")
            main_data.append([])
            continue

        rows = _extract_oppoint(result.data, mos_type)
        print(f"{len(rows)} pts")
        main_data.append(rows)

    # 写 8 个主 CSV
    print(f"\n  写出 CSV ...")
    for param in PARAMS_MAIN:
        _write_csv(OUT_DIR / f"{prefix}_{param}.csv",
                   param, prefix, LL_LIST, main_data)

    # ── Vds 扫描：对每个 (Vd, L) 跑一次，Vg 步长 0.05 ───────────────────
    vd_list = []
    v = VD_START
    while v <= VD_STOP + 1e-9:
        vd_list.append(round(v, 4))
        v += VD_STEP

    print(f"\n  {mos_type.upper()} Vds 扫描（{len(vd_list)} 个 Vd × {len(LL_LIST)} 个 L）")

    vds_data: list[list[list[dict]]] = []  # [vd_idx][ll_idx][row]

    for vd in vd_list:
        ll_group: list[list[dict]] = []
        for ll in LL_LIST:
            ll_nm = round(ll * 1e9)
            print(f"  Vd={vd:.2f}  L={ll_nm}nm ...", end=" ", flush=True)

            nl_path = work_base / f"{mos_type}_L{ll_nm}n_Vd{int(vd*100)}.scs"
            nl_path.write_text(nl_fn(ll, vd, VG_START, VG_STOP, VG_STEP_VDS))

            result = sim.run_simulation(nl_path, {})
            if not result.ok:
                print(f"FAIL")
                ll_group.append([])
                continue

            rows = _extract_oppoint(result.data, mos_type)
            print(f"{len(rows)} pts")
            ll_group.append(rows)

        vds_data.append(ll_group)

    for param in PARAMS_VDS:
        _write_vds_csv(OUT_DIR / f"Vds_{prefix}_{param}.csv",
                       param, prefix, vd_list, LL_LIST, vds_data)


def main():
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    from virtuoso_bridge.spectre.runner import SpectreSimulator, spectre_mode_args

    work_base = Path(__file__).parent / "data" / "sim_runs"
    work_base.mkdir(parents=True, exist_ok=True)

    sim = SpectreSimulator.from_env(
        spectre_args=spectre_mode_args("ax"),
        work_dir=work_base,
        output_format="psfascii",
    )

    print(f"输出目录：{OUT_DIR}")

    scan_one_type(sim, "nmos", work_base)
    scan_one_type(sim, "pmos", work_base)

    print(f"\n完成！CSV 文件在：{OUT_DIR}")
    print("下一步：把这些 CSV 放到 MOS_GmId_GUI/tsmc018/ 即可用于 MATLAB GUI")


if __name__ == "__main__":
    main()
