"""
lookup.py
=========
Boris Murmann gm/ID 查找表的 Python 实现。
直接翻译自 look_up.m 和 look_upVGS.m (Rev. 20190422)

用法：
    from scripts.gmid.lookup import load_mat, look_up, look_upVGS

    nch = load_mat("path/to/180nch.mat")
    pch = load_mat("path/to/180pch.mat")

    # 在 gm/ID=15 处查 ID/W（电流密度），L=360nm
    jd = look_up(nch, 'ID_W', 'GM_ID', 15, L=360e-9)

    # 在 gm/ID=15 处查 VGS
    vgs = look_upVGS(nch, 'GM_ID', 15, VDS=0.9, VSB=0, L=360e-9)

依赖：numpy, scipy
    pip install numpy scipy
"""

from __future__ import annotations
import numpy as np
import scipy.io
import scipy.interpolate


# ── 数据加载 ──────────────────────────────────────────────────────────────────

def load_mat(path: str) -> dict:
    """
    加载 Boris Murmann 格式的 .mat 文件。
    返回字典，key 全大写（与 MATLAB 变量名对应）：
      L, VGS, VDS, VSB, W, ID, GM, GDS, CGG, CGS, CGD, CDD, ...
    """
    raw = scipy.io.loadmat(path, squeeze_me=False, struct_as_record=True)

    # 找顶层 struct（通常是 'nch' 或 'pch'）
    struct_key = None
    for k, v in raw.items():
        if not k.startswith('_') and hasattr(v, 'dtype') and v.dtype.names:
            struct_key = k
            break

    if struct_key is None:
        raise ValueError(f"找不到 MATLAB struct in {path}. Keys: {list(raw.keys())}")

    obj = raw[struct_key][0, 0]
    data = {}
    for name in obj.dtype.names:
        arr = np.squeeze(obj[name])
        data[name.upper()] = arr.astype(float)

    return data


# ── 核心查找函数 ───────────────────────────────────────────────────────────────

def look_up(data: dict, outvar: str,
            invar: str | None = None, inval=None,
            L=None, VGS=None, VDS=None, VSB=None,
            method: str = 'linear') -> np.ndarray:
    """
    Python 版 look_up。

    三种模式：
    (1) look_up(nch, 'ID',    L=..., VGS=..., VDS=..., VSB=...)
        → 直接查参数值
    (2) look_up(nch, 'GM_ID', L=..., VGS=..., VDS=..., VSB=...)
        → 查比值 GM/ID，在给定偏置点处
    (3) look_up(nch, 'ID_W', 'GM_ID', 15, L=...)
        → 交叉查找：给定 GM/ID=15，返回对应的 ID_W

    参数
    ----
    outvar : str
        输出变量，可以是 'GM', 'ID', 'GDS', 'CGG' 等，
        或比值字符串如 'GM_ID', 'GM_GDS', 'ID_W', 'GM_CGG'
    invar  : str, optional
        mode3 的输入比值，如 'GM_ID', 'GM_CGS', 'GM_CGG'
    inval  : float or array, optional
        mode3 的目标值
    L, VGS, VDS, VSB : float or array, optional
        偏置点；未指定时用默认值
    """
    # 默认偏置
    if L   is None: L   = float(data['L'].min())
    if VDS is None: VDS = float(data['VDS'].max()) / 2.0
    if VSB is None: VSB = 0.0
    if VGS is None: VGS = data['VGS']  # 整个 VGS 向量（mode 2/3 需要）

    L   = np.atleast_1d(np.asarray(L,   dtype=float))
    VDS = np.atleast_1d(np.asarray(VDS, dtype=float))
    VSB = np.atleast_1d(np.asarray(VSB, dtype=float))
    VGS = np.atleast_1d(np.asarray(VGS, dtype=float))

    # 解析输出变量
    def _parse_ratio(varstr: str):
        if '_' in varstr:
            num, den = varstr.split('_', 1)
            return data[num] / data[den]
        return data[varstr]

    ydata = _parse_ratio(outvar)

    # mode 3：交叉查找
    if invar is not None and inval is not None:
        xdata = _parse_ratio(invar)
        inval = np.atleast_1d(np.asarray(inval, dtype=float))

        # 在给定 L/VDS/VSB 下，沿 VGS 轴插值
        x_vgs = _interp4d(data, xdata, L, data['VGS'], VDS, VSB)  # shape: [nVGS]
        y_vgs = _interp4d(data, ydata, L, data['VGS'], VDS, VSB)

        x_vgs = x_vgs.ravel()
        y_vgs = y_vgs.ravel()

        # 如果 invar 是 GM_ID，从最大值向右搜（强反型侧）
        if invar.upper() in ('GM_ID',):
            idx_max = np.argmax(x_vgs)
            x_vgs = x_vgs[idx_max:]
            y_vgs = y_vgs[idx_max:]

        # 单调性检查后插值
        result = np.interp(inval, x_vgs[::-1], y_vgs[::-1])  # x_vgs 递减 → 翻转
        # 如果 x_vgs 本来就是递增（强反型右侧是递减），按实际方向
        if x_vgs[0] < x_vgs[-1]:
            result = np.interp(inval, x_vgs, y_vgs)
        return float(result[0]) if result.size == 1 else result

    # mode 1/2：直接插值
    out = _interp4d(data, ydata, L, VGS, VDS, VSB)
    if out.size == 1:
        return float(out.ravel()[0])
    return out.squeeze()


def _interp4d(data: dict, ydata: np.ndarray,
              L, VGS, VDS, VSB) -> np.ndarray:
    """沿 4 个轴做 RegularGridInterpolator 插值"""
    axes = (data['L'], data['VGS'], data['VDS'], data['VSB'])

    # 确保 ydata 是 4D
    if ydata.ndim == 3:
        # 没有 VSB 维度 → 扩展
        ydata = ydata[:, :, :, np.newaxis]

    interp = scipy.interpolate.RegularGridInterpolator(
        axes, ydata, method='linear', bounds_error=False, fill_value=np.nan)

    # 构建查询点（广播）
    pts = np.array(np.meshgrid(L, VGS, VDS, VSB, indexing='ij'))
    pts = pts.reshape(4, -1).T
    return interp(pts)


def look_upVGS(data: dict, ratio: str, ratio_val,
               L=None, VDS=None, VSB=None, method: str = 'pchip') -> float | np.ndarray:
    """
    给定 gm/ID 或 ID/W，查找对应的 VGS。

    用法：
        VGS = look_upVGS(nch, 'GM_ID', 15, VDS=0.9, VSB=0, L=360e-9)
        VGS = look_upVGS(nch, 'ID_W',  1e-4, VDS=0.9, L=360e-9)
    """
    if L   is None: L   = float(data['L'].min())
    if VDS is None: VDS = float(data['VDS'].max()) / 2.0
    if VSB is None: VSB = 0.0

    # 计算整个 VGS 向量上的 ratio 值
    vgs_vec    = data['VGS']
    ratio_vals = look_up(data, ratio, L=L, VGS=vgs_vec, VDS=VDS, VSB=VSB)

    # 对 GM_ID，限制在最大值右侧（强反型）
    if ratio.upper() == 'GM_ID':
        idx_max = int(np.argmax(ratio_vals))
        vgs_vec    = vgs_vec[idx_max:]
        ratio_vals = ratio_vals[idx_max:]

    ratio_vals = np.asarray(ratio_vals).ravel()
    vgs_vec    = np.asarray(vgs_vec).ravel()

    # 翻转使 ratio 单调递增，然后插值
    if ratio_vals[0] > ratio_vals[-1]:
        ratio_vals = ratio_vals[::-1]
        vgs_vec    = vgs_vec[::-1]

    target = np.atleast_1d(np.asarray(ratio_val, dtype=float))
    result = np.interp(target, ratio_vals, vgs_vec)
    return float(result[0]) if result.size == 1 else result
