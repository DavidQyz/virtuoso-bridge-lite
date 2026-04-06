#!/usr/bin/env python3
"""
size_ota.py
===========
用 gm/ID 方法设计 5 管 OTA 的晶体管尺寸。

OTA 拓扑：
    M1/M2  — NMOS 差分输入对（共享尾电流 M5）
    M3/M4  — PMOS 电流镜负载（M3 二极管接法）
    M5     — NMOS 尾电流源

  VDD ──┬─────────────┐
        │             │
       M3(pch)       M4(pch)  ← 电流镜负载
    (diode)|         |
        ├─────────────┤
        │             │
       M1(nch)       M2(nch)  ← 差分输入对
    VIN+│             │VIN-
        └──── M5 ─────┘       ← 尾电流源
            (nch) IBIAS

性能规格（在脚本顶部修改）：
    GBW   — 增益带宽积 (Hz)
    CL    — 负载电容 (F)
    DC增益目标
    电源电压

使用：
    python scripts/gmid/size_ota.py

依赖：
    pip install numpy scipy
    把 180nch.mat / 180pch.mat 放到任意位置，在下面设置路径
"""

from __future__ import annotations
import sys
from pathlib import Path
import numpy as np

# 把 scripts/gmid/ 加入路径
sys.path.insert(0, str(Path(__file__).parent))
from lookup import load_mat, look_up, look_upVGS


# ═══════════════════════════════════════════════════════════════════════════════
#  1. 配置：数据文件路径 + 性能规格
# ═══════════════════════════════════════════════════════════════════════════════

# ← 修改为 .mat 文件的实际路径
NMOS_MAT = r"C:\Users\qianx\Desktop\TUDelft\Y2\Q3\gm_id\第一次作业\180nch.mat"
PMOS_MAT = r"C:\Users\qianx\Desktop\TUDelft\Y2\Q3\gm_id\第一次作业\180pch.mat"

# 工艺参数
VDD = 1.8    # V
Lmin = 180e-9  # 最小沟道长度 (m)

# 性能规格
GBW  = 10e6   # 增益带宽积 (Hz)，例如 10 MHz
CL   = 1e-12  # 负载电容 (F)，例如 1 pF
A0_dB = 40    # 直流增益目标 (dB)，例如 40 dB → A0 ≈ 100

# 设计选择（gm/ID 工作点）
GMID_INPUT = 15   # 差分对 gm/ID [V⁻¹]，通常 10~18，值越大越省电
GMID_TAIL  = 12   # 尾电流管 gm/ID，速度要求低一些
GMID_LOAD  = 12   # PMOS 负载 gm/ID

# VDS 偏置点（查表时用，通常取 VDD/2）
VDS_N = VDD / 2
VDS_P = VDD / 2


# ═══════════════════════════════════════════════════════════════════════════════
#  2. 加载查找表
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("  5T OTA gm/ID 定尺寸")
    print("=" * 60)

    try:
        nch = load_mat(NMOS_MAT)
        pch = load_mat(PMOS_MAT)
    except Exception as e:
        print(f"[错误] 无法加载 .mat 文件: {e}")
        print("  请检查 NMOS_MAT / PMOS_MAT 路径设置")
        return

    print(f"NMOS 数据: L={nch['L']*1e9} nm")
    print(f"PMOS 数据: L={pch['L']*1e9} nm")
    print()

    # ─── 3. 从规格推导 gm ────────────────────────────────────────────────────
    # GBW = gm1 / (2π·CL)  →  gm1
    gm1 = 2 * np.pi * GBW * CL
    A0  = 10 ** (A0_dB / 20)
    print(f"规格：GBW={GBW/1e6:.1f} MHz，CL={CL*1e12:.1f} pF，A0={A0:.0f} ({A0_dB} dB)")
    print(f"→ 需要 gm1 = {gm1*1e3:.3f} mS")
    print()

    # ─── 4. 差分输入对 M1/M2（NMOS） ─────────────────────────────────────────
    # 每支输入管电流（尾电流 Itail 被 M1/M2 平分）
    ID1 = gm1 / GMID_INPUT
    Itail = 2 * ID1

    print(f"差分对 M1/M2（NMOS，gm/ID={GMID_INPUT} V⁻¹）：")
    print(f"  gm1  = {gm1*1e3:.3f} mS")
    print(f"  ID1  = {ID1*1e6:.2f} µA  →  Itail = {Itail*1e6:.2f} µA")

    # 从 gm/ID 反查沟道长度（本征增益 gm/gds 决定增益，需要足够长的 L）
    # A0 由 (gm·ron) 决定，ron = 1/(gds_n + gds_p)
    # 粗估：选 L 使得 gm_n/gds_n ≥ 2·A0（留余量给并联的 pmos）
    needed_av = 2 * A0   # gm/gds 目标（NMOS 单管需满足此值）

    # 在各个 L 处查 gm/gds
    L_vec = nch['L']
    av_nch = np.array([
        look_up(nch, 'GM_GDS', 'GM_ID', GMID_INPUT, L=Lv, VDS=VDS_N)
        for Lv in L_vec
    ])
    print(f"  NMOS gm/gds @ gm/ID={GMID_INPUT}:")
    for Lv, av in zip(L_vec, av_nch):
        print(f"    L={Lv*1e9:.0f} nm → gm/gds = {av:.1f}")

    # 选满足增益的最小 L
    L1 = float(L_vec[av_nch >= needed_av][0]) if any(av_nch >= needed_av) else float(L_vec[-1])
    print(f"  → 选 L1 = {L1*1e9:.0f} nm（满足 gm/gds ≥ {needed_av:.0f}）")

    # 从 ID_W 查宽度
    JD1 = look_up(nch, 'ID_W', 'GM_ID', GMID_INPUT, L=L1, VDS=VDS_N)
    W1  = ID1 / JD1
    print(f"  JD1  = {JD1*1e3:.3f} mA/m  →  W1 = {W1*1e6:.3f} µm")
    VGS1 = look_upVGS(nch, 'GM_ID', GMID_INPUT, VDS=VDS_N, VSB=0, L=L1)
    print(f"  VGS1 = {VGS1:.3f} V")
    print()

    # ─── 5. PMOS 负载 M3/M4 ──────────────────────────────────────────────────
    # M3/M4 流过相同 ID（= ID1）
    ID3 = ID1

    print(f"PMOS 负载 M3/M4（pch，gm/ID={GMID_LOAD} V⁻¹）：")

    L_vec_p = pch['L']
    av_pch = np.array([
        look_up(pch, 'GM_GDS', 'GM_ID', GMID_LOAD, L=Lv, VDS=VDS_P)
        for Lv in L_vec_p
    ])
    print(f"  PMOS gm/gds @ gm/ID={GMID_LOAD}:")
    for Lv, av in zip(L_vec_p, av_pch):
        print(f"    L={Lv*1e9:.0f} nm → gm/gds = {av:.1f}")

    L3 = float(L_vec_p[av_pch >= needed_av][0]) if any(av_pch >= needed_av) else float(L_vec_p[-1])
    print(f"  → 选 L3 = {L3*1e9:.0f} nm")

    JD3 = look_up(pch, 'ID_W', 'GM_ID', GMID_LOAD, L=L3, VDS=VDS_P)
    W3  = ID3 / JD3
    VGS3 = look_upVGS(pch, 'GM_ID', GMID_LOAD, VDS=VDS_P, VSB=0, L=L3)
    print(f"  JD3 = {JD3*1e3:.3f} mA/m  →  W3 = {W3*1e6:.3f} µm")
    print(f"  VGS3(= -VSG3) = {VGS3:.3f} V  →  VSG3 = {VDD-VGS3:.3f} V")
    print()

    # ─── 6. 尾电流源 M5（NMOS） ───────────────────────────────────────────────
    ID5 = Itail
    print(f"尾电流源 M5（nch，gm/ID={GMID_TAIL} V⁻¹，ID={ID5*1e6:.2f} µA）：")

    L5 = L1  # 通常与输入对相同 L
    JD5 = look_up(nch, 'ID_W', 'GM_ID', GMID_TAIL, L=L5, VDS=VDS_N)
    W5  = ID5 / JD5
    VGS5 = look_upVGS(nch, 'GM_ID', GMID_TAIL, VDS=VDS_N, VSB=0, L=L5)
    print(f"  L5   = {L5*1e9:.0f} nm")
    print(f"  JD5  = {JD5*1e3:.3f} mA/m  →  W5 = {W5*1e6:.3f} µm")
    print(f"  VGS5 = {VGS5:.3f} V  (IBIAS 电压)")
    print()

    # ─── 7. 验证增益 ─────────────────────────────────────────────────────────
    gm1_check = GMID_INPUT * ID1
    gds1 = look_up(nch, 'GDS', 'GM_ID', GMID_INPUT, L=L1, VDS=VDS_N) * ID1  # 近似
    # 用 gm/gds 比值反算 gds
    av1  = look_up(nch, 'GM_GDS', 'GM_ID', GMID_INPUT, L=L1, VDS=VDS_N)
    av3  = look_up(pch, 'GM_GDS', 'GM_ID', GMID_LOAD,  L=L3, VDS=VDS_P)
    # 输出阻抗 rout = ron // rop = 1/(gds_n + gds_p)
    # A0 = gm1 * rout = gm1 / (gds_n + gds_p)
    # gds_n = gm1/av1，gds_p = ID3*GMID_LOAD/av3
    gds_n  = gm1_check / av1
    gds_p  = GMID_LOAD * ID3 / av3
    A0_est = gm1_check / (gds_n + gds_p)
    print(f"增益验证：")
    print(f"  gm1   = {gm1_check*1e3:.3f} mS")
    print(f"  av(n) = {av1:.0f}，av(p) = {av3:.0f}")
    print(f"  A0 估算 = {A0_est:.0f} ({20*np.log10(A0_est):.1f} dB)  (目标 {A0_dB} dB)")
    print()

    # ─── 8. 汇总 ─────────────────────────────────────────────────────────────
    print("=" * 60)
    print("  最终尺寸汇总（nf=1，可乘以 nf 得到 finger 数）")
    print("=" * 60)
    print(f"  M1/M2 (nch)  W = {W1*1e6:.2f} µm   L = {L1*1e9:.0f} nm   VGS = {VGS1:.3f} V")
    print(f"  M3/M4 (pch)  W = {W3*1e6:.2f} µm   L = {L3*1e9:.0f} nm   VSG = {VDD-VGS3:.3f} V")
    print(f"  M5    (nch)  W = {W5*1e6:.2f} µm   L = {L5*1e9:.0f} nm   VGS = {VGS5:.3f} V (IBIAS)")
    print(f"  Itail = {Itail*1e6:.2f} µA")
    print()

    # 建议取整到合理 grid（0.05 µm 或按 PDK 规则）
    def round_w(w_m, grid=0.05e-6):
        return max(grid, round(w_m / grid) * grid)

    W1r = round_w(W1); W3r = round_w(W3); W5r = round_w(W5)
    print("  取整后（0.05 µm grid）：")
    print(f"  M1/M2  W = {W1r*1e6:.2f} µm")
    print(f"  M3/M4  W = {W3r*1e6:.2f} µm")
    print(f"  M5     W = {W5r*1e6:.2f} µm")

    return {
        "M1_W": W1r, "M1_L": L1, "M1_VGS": VGS1,
        "M2_W": W1r, "M2_L": L1,
        "M3_W": W3r, "M3_L": L3,
        "M4_W": W3r, "M4_L": L3,
        "M5_W": W5r, "M5_L": L5, "M5_VGS": VGS5,
        "Itail_uA": Itail * 1e6,
        "A0_dB_est": 20 * np.log10(A0_est),
    }


if __name__ == "__main__":
    result = main()
