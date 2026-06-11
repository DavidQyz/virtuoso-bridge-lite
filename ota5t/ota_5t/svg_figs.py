#!/usr/bin/env python3
"""
Pure-Python SVG plots for the 5T OTA characterization (no matplotlib).
Reads ota5t/ota_5t/char_data.json -> writes ota5t_bode.svg, ota5t_psrr_cmrr.svg.
Run:  python ota5t/ota_5t/svg_figs.py
"""
from __future__ import annotations
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
D = json.loads((HERE / "char_data.json").read_text(encoding="utf-8"))


def _fmt_hz(f):
    for div, suf in ((1e9, "G"), (1e6, "M"), (1e3, "k"), (1, "")):
        if f >= div:
            v = f/div
            return (f"{v:.0f}{suf}" if abs(v-round(v)) < 1e-6 else f"{v:.1f}{suf}")
    return f"{f:g}"


def axes(x0, y0, w, h, xlim, ylim, curves, title, xlabel, ylabel,
         hlines=(), vlines=(), yticks=6, legend=True):
    """Render one log-x / linear-y axes block as SVG, return string."""
    lx0, lx1 = math.log10(xlim[0]), math.log10(xlim[1])
    y_lo, y_hi = ylim

    def px(f):
        return x0 + (math.log10(f) - lx0) / (lx1 - lx0) * w

    def py(v):
        v = max(y_lo, min(y_hi, v))
        return y0 + (y_hi - v) / (y_hi - y_lo) * h

    s = []
    # frame
    s.append(f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" '
             f'fill="white" stroke="#333" stroke-width="1"/>')
    # vertical decade grid + labels
    d = int(math.floor(lx0))
    while d <= math.ceil(lx1):
        f = 10.0**d
        if xlim[0] <= f <= xlim[1]:
            x = px(f)
            s.append(f'<line x1="{x:.1f}" y1="{y0}" x2="{x:.1f}" y2="{y0+h}" '
                     f'stroke="#e3e3e3" stroke-width="1"/>')
            s.append(f'<text x="{x:.1f}" y="{y0+h+14}" font-size="11" '
                     f'text-anchor="middle" fill="#444">{_fmt_hz(f)}</text>')
        d += 1
    # horizontal grid + y labels
    for k in range(yticks+1):
        v = y_lo + (y_hi-y_lo)*k/yticks
        y = py(v)
        s.append(f'<line x1="{x0}" y1="{y:.1f}" x2="{x0+w}" y2="{y:.1f}" '
                 f'stroke="#eee" stroke-width="1"/>')
        s.append(f'<text x="{x0-6}" y="{y+4:.1f}" font-size="11" '
                 f'text-anchor="end" fill="#444">{v:.0f}</text>')
    # reference h/v lines (dashed)
    for hv in hlines:
        y = py(hv)
        s.append(f'<line x1="{x0}" y1="{y:.1f}" x2="{x0+w}" y2="{y:.1f}" '
                 f'stroke="#999" stroke-width="1" stroke-dasharray="4 3"/>')
    for vv in vlines:
        x = px(vv)
        s.append(f'<line x1="{x:.1f}" y1="{y0}" x2="{x:.1f}" y2="{y0+h}" '
                 f'stroke="#c0392b" stroke-width="1" stroke-dasharray="4 3"/>')
    # curves
    for c in curves:
        pts = " ".join(f"{px(xx):.1f},{py(yy):.1f}"
                       for xx, yy in zip(c["x"], c["y"])
                       if xlim[0] <= xx <= xlim[1])
        s.append(f'<polyline points="{pts}" fill="none" '
                 f'stroke="{c["color"]}" stroke-width="2"/>')
    # titles
    s.append(f'<text x="{x0+w/2}" y="{y0-8}" font-size="13" '
             f'text-anchor="middle" fill="#111" font-weight="bold">{title}</text>')
    s.append(f'<text x="{x0+w/2}" y="{y0+h+30}" font-size="12" '
             f'text-anchor="middle" fill="#222">{xlabel}</text>')
    s.append(f'<text x="{x0-34}" y="{y0+h/2}" font-size="12" fill="#222" '
             f'text-anchor="middle" transform="rotate(-90 {x0-34} {y0+h/2})">{ylabel}</text>')
    # legend
    if legend and any(c.get("label") for c in curves):
        ly = y0 + 6
        for c in curves:
            if not c.get("label"):
                continue
            s.append(f'<line x1="{x0+w-150}" y1="{ly}" x2="{x0+w-128}" y2="{ly}" '
                     f'stroke="{c["color"]}" stroke-width="3"/>')
            s.append(f'<text x="{x0+w-123}" y="{ly+4}" font-size="11" '
                     f'fill="#222">{c["label"]}</text>')
            ly += 16
    return "\n".join(s)


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" font-family="Segoe UI, Arial, sans-serif">'
            f'<rect width="{w}" height="{h}" fill="white"/>{body}</svg>')


def main():
    f = D["freq"]
    m = D["metrics"]
    xlim = (1, 1e10)

    # ---------- Bode (mag + phase) ----------
    body = []
    body.append(f'<text x="360" y="22" font-size="15" text-anchor="middle" '
                f'font-weight="bold">5T OTA — open-loop differential gain (Bode)</text>')
    body.append(axes(70, 50, 600, 200, xlim, (-20, 50),
                     [dict(x=f, y=D["mag_db"], color="#1f77b4", label="|Adm|")],
                     f'A0 = {m["dc_gain"]:.1f} dB,  GBW = {m["ugf"]/1e6:.1f} MHz,'
                     f'  PM = {m["pm"]:.0f}deg',
                     "frequency (Hz)", "|Adm|  (dB)",
                     hlines=(0,), vlines=(m["ugf"],), yticks=7, legend=False))
    body.append(axes(70, 320, 600, 160, xlim, (-180, 0),
                     [dict(x=f, y=D["phase_deg"], color="#ff7f0e",
                           label="phase")],
                     "phase", "frequency (Hz)", "phase (deg)",
                     hlines=(-90,), vlines=(m["ugf"],), yticks=6, legend=False))
    (HERE / "ota5t_bode.svg").write_text(svg_doc(720, 520, "\n".join(body)),
                                         encoding="utf-8")

    # ---------- PSRR + CMRR ----------
    body2 = [f'<text x="360" y="22" font-size="15" text-anchor="middle" '
             f'font-weight="bold">5T OTA — PSRR(+) and CMRR vs frequency</text>']
    body2.append(axes(70, 50, 600, 300, xlim, (-20, 80),
                      [dict(x=f, y=D["psrr_db"], color="#2ca02c",
                            label=f'PSRR  (DC {m["psrr_dc"]:.0f} dB)'),
                       dict(x=f, y=D["cmrr_db"], color="#9467bd",
                            label=f'CMRR  (DC {m["cmrr_dc"]:.0f} dB)')],
                      "supply / common-mode rejection",
                      "frequency (Hz)", "rejection (dB)", yticks=5))
    (HERE / "ota5t_psrr_cmrr.svg").write_text(svg_doc(720, 400, "\n".join(body2)),
                                              encoding="utf-8")

    print("saved ota5t_bode.svg, ota5t_psrr_cmrr.svg")


if __name__ == "__main__":
    main()
