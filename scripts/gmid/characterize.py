#!/usr/bin/env python3
"""
characterize.py
===============
用 Spectre DC 扫描生成 NMOS/PMOS 的 gm/ID 特征曲线，
保存到 gmid_nmos.json / gmid_pmos.json 供 size_ota.py 使用。

使用前：
  1. 确认 .env 中 VB_CADENCE_CSHRC 已设置
  2. 修改下面的 PDK_MODELS / PDK_SECTION 为实验室路径
  3. 运行: python scripts/gmid/characterize.py

输出文件：scripts/gmid/data/gmid_nmos.json, gmid_pmos.json
"""

from __future__ import annotations
import json
import os
import shutil
from pathlib import Path
from string import Template

# ── 配置 ──────────────────────────────────────────────────────────────────────
# 从 Virtuoso 导出的 netlist 的第一行 include 里复制这两个路径
PDK_MODELS   = "/opt/tsmc018rf/models/spectre/toplevel.scs"   # ← 修改
PDK_SECTION  = "TOP_TT"                                        # ← 修改 (tt/ss/ff)

VDD          = 1.8   # V
W_CHAR       = 10e-6  # 特征化宽度 10um (宽一些，电流大，误差小)

# 扫描不同沟道长度
L_LIST = [180e-9, 360e-9, 500e-9, 720e-9, 1e-6]  # m

SCRIPT_DIR = Path(__file__).parent
DATA_DIR   = SCRIPT_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# ── 辅助函数 ──────────────────────────────────────────────────────────────────

def _render_netlist(template_path: Path, out_path: Path, L: float) -> Path:
    """将 @@PDK_MODELS@@ 等占位符替换后写到 out_path"""
    text = template_path.read_text()
    text = text.replace("@@PDK_MODELS@@",  PDK_MODELS)
    text = text.replace("@@PDK_SECTION@@", PDK_SECTION)
    text = text.replace("W=10u",  f"W={W_CHAR:.6g}")
    text = text.replace("L=180n", f"L={L:.6g}")
    out_path.write_text(text)
    return out_path


def _run_one(sim, template: Path, work_subdir: Path, L: float) -> dict | None:
    """运行一次 DC 仿真，返回操作点数据字典"""
    work_subdir.mkdir(parents=True, exist_ok=True)
    nl = work_subdir / "tb.scs"
    _render_netlist(template, nl, L)

    result = sim.run_simulation(nl, {})
    if not result.ok:
        print(f"  [FAIL] L={L*1e9:.0f}nm  errors: {result.errors[:2]}")
        return None

    return result.data


def _extract_gmid_table(data: dict, L: float, mos_type: str) -> list[dict]:
    """
    从 Spectre 操作点结果里提取每个 VGS 点的 gm/ID、ID/W 等。

    Spectre 操作点信号名格式示例：
      M0:gm, M0:gds, M0:id, M0:cgg
    (有时前缀是 'dc_M0:gm' 取决于 Spectre 版本)
    """
    # 找信号名前缀
    prefix = ""
    for key in data.keys():
        if "gm" in key.lower() and "M0" in key:
            prefix = key.split(":")[0].replace("M0", "") + "M0"
            break

    def _get(suffix: str):
        for k in [f"{prefix}:{suffix}", f"M0:{suffix}", f"dc_M0:{suffix}"]:
            if k in data:
                return data[k]
        return []

    vgs_arr = data.get("dc_vgs", data.get("vgs", []))
    gm_arr  = _get("gm")
    id_arr  = _get("id")
    gds_arr = _get("gds")
    cgg_arr = _get("cgg")

    if not gm_arr or not id_arr:
        print(f"  [WARN] 找不到 gm/id 信号，可用 keys: {list(data.keys())[:10]}")
        return []

    rows = []
    for i, vgs in enumerate(vgs_arr):
        id_val  = abs(id_arr[i])  if i < len(id_arr)  else 0
        gm_val  = abs(gm_arr[i])  if i < len(gm_arr)  else 0
        gds_val = abs(gds_arr[i]) if i < len(gds_arr) else 0
        cgg_val = abs(cgg_arr[i]) if i < len(cgg_arr) else 0

        if id_val < 1e-15:  # 关断，跳过
            continue

        gmid    = gm_val  / id_val                       # V⁻¹
        id_over_w = id_val / W_CHAR                      # A/m
        av0     = gm_val  / gds_val if gds_val > 0 else 0  # 本征增益
        ft      = gm_val  / (2 * 3.14159 * cgg_val) if cgg_val > 0 else 0  # Hz

        rows.append({
            "vgs":        round(vgs, 4),
            "L_nm":       round(L * 1e9, 1),
            "ID_A":       id_val,
            "gm_S":       gm_val,
            "gds_S":      gds_val,
            "gmid":       gmid,         # gm/ID [V⁻¹]
            "id_over_w":  id_over_w,    # ID/W  [A/m]
            "av0":        av0,          # gm/gds (本征增益)
            "ft_Hz":      ft,           # 过渡频率
        })

    return rows


# ── 主程序 ────────────────────────────────────────────────────────────────────

def characterize(mos_type: str = "nmos"):
    """
    mos_type: "nmos" 或 "pmos"
    """
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    from virtuoso_bridge.spectre.runner import SpectreSimulator, spectre_mode_args

    sim = SpectreSimulator.from_env(
        spectre_args=spectre_mode_args("ax"),
        work_dir=DATA_DIR / f"sim_{mos_type}",
        output_format="psfascii",
    )

    template = SCRIPT_DIR / f"tb_gmid_{mos_type}.scs"
    all_rows: list[dict] = []

    for L in L_LIST:
        L_nm = round(L * 1e9, 0)
        print(f"[{mos_type.upper()}] L = {L_nm:.0f} nm ...")

        work_sub = DATA_DIR / f"sim_{mos_type}" / f"L{L_nm:.0f}n"
        raw = _run_one(sim, template, work_sub, L)
        if raw is None:
            continue

        rows = _extract_gmid_table(raw, L, mos_type)
        print(f"  → {len(rows)} operating points")
        all_rows.extend(rows)

    out_file = DATA_DIR / f"gmid_{mos_type}.json"
    with open(out_file, "w") as f:
        json.dump(all_rows, f, indent=2)
    print(f"\n保存到: {out_file}  ({len(all_rows)} 点)")
    return all_rows


if __name__ == "__main__":
    print("=" * 60)
    print("  gm/ID 特征化 — NMOS")
    print("=" * 60)
    characterize("nmos")

    print()
    print("=" * 60)
    print("  gm/ID 特征化 — PMOS")
    print("=" * 60)
    characterize("pmos")

    print("\n完成！下一步: python scripts/gmid/size_ota.py")
