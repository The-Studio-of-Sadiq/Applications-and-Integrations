"""Figures for Chapter 7 — Measurement and Signal Conditioning.

Run from the repository root:  python figures/scripts/ch07.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle, FancyBboxPatch  # noqa: E402
from scipy import signal  # noqa: E402
import warnings  # noqa: E402
import schemdraw  # noqa: E402
import schemdraw.elements as elm  # noqa: E402

from figstyle import COLORS, INK, box, arrow, save, schematic, new_fig  # noqa: E402

schemdraw.use("matplotlib")
warnings.filterwarnings("ignore", message=".*non-interactive.*")

BLUE, ORANGE, GREEN, PINK, YELLOW, SKY = COLORS[:6]
RED = "#C62828"
GREY = "#777777"

# Chapter numbers
FS_ADC, DEC = 32_000, 16
FC_AA = 2_000
GF = 2.0


def line(ax, pts, color=INK, lw=1.1, ls="-", arrow_end=False):
    xs, ys = zip(*pts)
    if not arrow_end:
        ax.plot(xs, ys, color=color, lw=lw, ls=ls, solid_capstyle="butt")
        return
    if len(pts) > 2:
        ax.plot(xs[:-1], ys[:-1], color=color, lw=lw, ls=ls)
    ax.annotate("", xy=pts[-1], xytext=pts[-2],
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, ls=ls,
                                shrinkA=0, shrinkB=0, mutation_scale=10))


# ----------------------------------------------------------------------------
# Figure 7.1 — module architecture
# ----------------------------------------------------------------------------
def fig_7_1():
    fig, ax = schematic(6.8, 5.0, xlim=(0, 18), ylim=(-0.2, 13.0))
    fs = 6.6
    # stack of 8 quarter-bridge channels
    for i in range(3, -1, -1):
        ax.add_patch(FancyBboxPatch((0.15 + 0.12 * i, 4.2 + 0.12 * i), 2.0, 3.8,
                                    boxstyle="round,pad=0.02,rounding_size=0.12",
                                    fc="#F4F4F4" if i else "#FFFFFF", ec=INK, lw=0.9))
    ax.text(1.15, 6.1, "8 × quarter\nbridge\n\n350 Ω gauge\nGF 2.0\n\n5 m, 3-wire,\nshielded\ncable",
            ha="center", va="center", fontsize=fs, linespacing=1.15)
    ax.text(0.95, 8.75, "specimen", ha="center", fontsize=fs, color=GREY, style="italic")

    # isolated domain
    ax.add_patch(Rectangle((2.55, 0.6), 9.85, 11.6, fill=False, ec=BLUE, lw=1.2, ls=(0, (5, 3))))
    ax.text(2.7, 11.75, "isolated domain (floats at rig potential)", fontsize=fs + 0.6,
            color=BLUE, va="center", weight="bold")

    # per-channel signal row with shadows (x8)
    row_y, row_h = 5.0, 2.1
    blocks = [(2.8, 1.4, "RFI\nfilter\nRC, C0G", "#FFFFFF"),
              (4.5, 1.5, "In-amp\nINA828\nclass\nG = 501", "#EEF3F8"),
              (6.3, 2.1, "Sallen-Key\nButterworth\n2nd order\n2 kHz", "#EEF3F8")]
    for x, w, t, fc in blocks:
        for k in (2, 1):
            ax.add_patch(FancyBboxPatch((x + 0.1 * k, row_y + 0.1 * k), w, row_h,
                                        boxstyle="round,pad=0.02,rounding_size=0.12",
                                        fc="#F4F4F4", ec=GREY, lw=0.7))
        box(ax, x, row_y, w, row_h, t, fc=fc, fontsize=fs)
    ax.text(5.35, 4.5, "× 8 channels", ha="center", fontsize=fs, color=GREY, style="italic")
    box(ax, 8.7, 4.55, 2.85, 3.0, "8-ch simultaneous\n18-bit SAR ADC\nAD7606C-18 class\n±5 V FS, 32 kSa/s\nper channel",
        fc="#E6F2EC", fontsize=fs - 0.4)
    arrow(ax, 2.4, 6.05, 2.8, 6.05)
    arrow(ax, 4.2, 6.05, 4.5, 6.05)
    arrow(ax, 6.0, 6.05, 6.3, 6.05)
    arrow(ax, 8.4, 6.05, 8.7, 6.05)
    arrow(ax, 11.55, 6.05, 11.8, 6.05)

    # excitation and reference
    box(ax, 2.8, 8.9, 3.8, 1.6, "Excitation ±2.5 V\n−2.5 V by inverting\nbuffer from the ref", fc="#FFF4E0",
        fontsize=fs)
    box(ax, 8.7, 8.9, 2.85, 1.6, "2.5 V reference\nADR4525 class\n2 ppm/K", fc="#FFF4E0", fontsize=fs)
    arrow(ax, 8.7, 9.7, 6.6, 9.7)
    ax.text(7.65, 9.55, "ratiometric", ha="center", va="top", fontsize=fs - 0.3, color=ORANGE)
    arrow(ax, 10.6, 8.9, 10.6, 7.55)
    ax.text(10.7, 8.2, "REF", ha="left", va="center", fontsize=fs)
    line(ax, [(2.8, 9.7), (1.9, 9.7), (1.9, 8.38)], arrow_end=True, color=ORANGE)
    ax.text(1.0, 9.85, "±2.5 V\nexcitation", ha="center", va="bottom", fontsize=fs, color=ORANGE)

    # ground / shield / strap
    ax.text(1.15, 3.75, "shield → iso GND\nat module only", ha="center", va="top", fontsize=fs,
            color=GREEN)
    gx, gy = 4.0, 1.5
    line(ax, [(gx, 2.4), (gx, gy)], color=GREEN)
    for k, hw in enumerate((0.35, 0.23, 0.11)):
        line(ax, [(gx - hw, gy - 0.13 * k), (gx + hw, gy - 0.13 * k)], color=GREEN, lw=1.3)
    ax.text(gx + 0.45, 1.6, "iso GND", fontsize=fs, color=GREEN, va="center")
    line(ax, [(gx, 2.4), (1.2, 2.4), (1.2, 1.55)], color=GREEN, lw=1.6)
    ax.add_patch(Rectangle((0.25, 1.0), 1.9, 0.55, fc="#DDDDDD", ec=INK, lw=0.8, hatch="////"))
    ax.text(1.2, 0.65, "rig frame", ha="center", va="center", fontsize=fs)
    ax.text(2.6, 2.5, "one strap", ha="center", va="bottom", fontsize=fs, color=GREEN)

    # barrier
    bx = 12.4
    ax.plot([bx, bx], [0.45, 12.4], color=INK, lw=3.2, zorder=0.5)
    ax.text(bx, 12.45, "isolation barrier, 1.5 kV rms (functional)", fontsize=fs, ha="center", va="bottom")
    box(ax, 11.8, 5.35, 1.2, 1.4, "digital\nisolator", fc="#FFFFFF", fontsize=fs - 0.6)
    box(ax, 11.7, 0.85, 1.4, 1.5, "iso\nDC–DC\n1 W", fc="#FFFFFF", fontsize=fs - 0.4)
    ax.text(bx, 0.15, "≈ 25 pF total across the barrier", ha="center", va="center", fontsize=fs,
            color=GREY)
    ax.text(bx, 4.95, "SPI 20 MHz", ha="center", va="center", fontsize=fs,
            bbox=dict(fc="white", ec="none", pad=0.6))
    line(ax, [(11.7, 1.6), (10.0, 1.6), (10.0, 4.55)], arrow_end=True, color=ORANGE)
    ax.text(10.1, 3.0, "isolated\nsupply", fontsize=fs, color=ORANGE, va="center")

    # MCU side
    box(ax, 13.45, 3.9, 4.45, 4.7, "", fc="#F3EEF6")
    ax.text(15.67, 8.15, "MCU (Cortex-M7 class)", ha="center", va="center", fontsize=fs + 0.3, weight="bold")
    box(ax, 13.7, 6.05, 3.95, 1.6, "FIR 255 taps, ↓16\n→ 2 kSa/s (logging)", fc="white", fontsize=fs)
    box(ax, 13.7, 4.15, 3.95, 1.6, "IIR 4th order, 1 kHz\n32 kSa/s (control path)", fc="white", fontsize=fs)
    arrow(ax, 13.0, 6.05, 13.45, 6.05)
    box(ax, 13.7, 10.1, 3.95, 1.3, "DAQ system (Ch. 8)", fc="#EEF3F8", fontsize=fs)
    arrow(ax, 15.67, 8.6, 15.67, 10.1)
    ax.text(15.8, 9.35, "Ethernet", ha="left", va="center", fontsize=fs)
    box(ax, 13.45, 1.75, 2.0, 1.5, "16-bit DAC\n±10 V", fc="#EEF3F8", fontsize=fs)
    box(ax, 15.9, 1.75, 2.0, 1.5, "servo\ncontroller", fc="#EEF3F8", fontsize=fs)
    arrow(ax, 14.45, 3.9, 14.45, 3.25)
    ax.text(14.58, 3.58, "SPI", ha="left", va="center", fontsize=fs)
    arrow(ax, 15.45, 2.5, 15.9, 2.5)
    line(ax, [(18.0, 1.05), (13.1, 1.05)], arrow_end=True, color=ORANGE)
    ax.text(17.95, 0.6, "system 5 V", fontsize=fs, ha="right", va="center", color=ORANGE)
    save(fig, "07", "fig-7-1-strain-module-architecture")


# ----------------------------------------------------------------------------
# Figure 7.2 — uncertainty contributions
# ----------------------------------------------------------------------------
BUDGET = [
    ("Shunt-cal resistor", "g", 0.05),
    ("Lead-resistance correction", "g", 0.014),
    ("Gain drift after calibration", "g", 0.06),
    ("Excitation ratio residual", "g", 0.01),
    ("Completion-network tracking", "o", 2.5),
    ("In-amp offset drift", "o", 1.6),
    ("Thermal EMF", "o", 0.4),
    ("Random noise (Type A)", "o", 0.3),
    ("Residual 50 Hz", "o", 0.2),
]


def contributions(eps):
    r3 = np.sqrt(3)
    out = []
    for name, k, v in BUDGET:
        if name.startswith(("Random", "Residual")):
            u = v
        elif k == "g":
            u = v / r3 / 100 * eps
        else:
            u = v / r3
        out.append(u)
    return np.array(out)


def fig_7_2():
    fig, ax = new_fig(6.4, 3.9)
    u3k, u100 = contributions(3000), contributions(100)
    names = [b[0] for b in BUDGET]
    y = np.arange(len(names))[::-1]
    h = 0.38
    ax.barh(y + h / 2, u3k, h, color=BLUE, label="at 3000 µε")
    ax.barh(y - h / 2, u100, h, color="#9CC3E0", label="at 100 µε")
    for yy, a, b in zip(y, u3k, u100):
        ax.text(a + 0.02, yy + h / 2, f"{a:.2f}", va="center", fontsize=7.5)
        ax.text(b + 0.02, yy - h / 2, f"{b:.2f}", va="center", fontsize=7.5, color=GREY)
    uc3k = np.sqrt(np.sum(u3k ** 2))
    uc100 = np.sqrt(np.sum(u100 ** 2))
    ax.axvline(uc3k, color=BLUE, ls="--", lw=1.1)
    ax.axvline(uc100, color="#5E9CC8", ls="--", lw=1.1)
    ax.text(uc3k + 0.02, 8.75, f"combined u at 3000 µε\n= {uc3k:.3f} µε (U = {2 * uc3k:.2f})",
            fontsize=7.5, color=BLUE, va="top")
    ax.text(uc100 - 0.02, 8.75, f"combined u at 100 µε\n= {uc100:.2f} µε (U = {2 * uc100:.2f})",
            fontsize=7.5, color="#3C7FB0", va="top", ha="right")
    ax.set_yticks(y)
    ax.set_yticklabels(names, fontsize=8.5)
    ax.set_xlim(0, 2.6)
    ax.set_ylim(-0.7, 9.0)
    ax.set_xlabel("standard uncertainty (µε)")
    ax.legend(loc="lower right", fontsize=8.5)
    ax.text(1.72, 6.0, "gain terms (top four)\nscale with reading;\noffset terms do not",
            ha="right", fontsize=7.5, color=GREY, style="italic")
    save(fig, "07", "fig-7-2-uncertainty-contributions")


# ----------------------------------------------------------------------------
# Figure 7.3 — quarter-bridge front end (schemdraw)
# ----------------------------------------------------------------------------
def fig_7_3():
    fig, ax = plt.subplots(figsize=(6.8, 4.4))
    ax.set_aspect("equal")
    ax.axis("off")
    d = schemdraw.Drawing(canvas=ax, show=False)
    d.config(fontsize=7.6, unit=2.5, lw=1.0)

    # gauge on the specimen
    d += elm.Resistor().at((0, 6)).to((0, 3)).label("$R_g$\n350 Ω\ngauge", loc="top", ofst=0.25)
    d += elm.Dot().at((0, 6))
    d += elm.Dot().at((0, 3))
    # L1 to +2.5 V
    d += elm.Resistor().at((0, 6)).to((5, 6)).label("L1 0.67 Ω", ofst=0.1)
    d += elm.Line().at((5, 6)).to((7, 6))
    d += elm.Vdd().at((7, 6)).label("+2.5 V", fontsize=7.6)
    # L3 sense
    d += elm.Resistor().at((0, 3)).to((5, 3)).label("L3 0.67 Ω (sense)", loc="bottom", ofst=0.1)
    d += elm.Line().at((5, 3)).to((10, 3))
    # L2 to completion arm
    d += elm.Line().at((0, 3)).to((0, 0))
    d += elm.Resistor().at((0, 0)).to((5, 0)).label("L2 0.67 Ω", ofst=0.1)
    d += elm.Line().at((5, 0)).to((7, 0))
    d += elm.Dot().at((7, 0))
    d += elm.Resistor().at((7, 0)).to((7, -4)).label("$R_c$ 350 Ω\nfoil\nnetwork", loc="top", ofst=0.15)
    d += elm.Line().at((7, 0)).to((9, 0))
    d += elm.Switch().at((9, 0)).to((9, -1.6)).label("K1\nreed", loc="bottom", ofst=0.1)
    d += elm.Resistor().at((9, -1.6)).to((9, -4)).label("$R_s$ 175.0 kΩ\n0.05 %", loc="bottom", ofst=0.1)
    d += elm.Line().at((9, -4)).to((7, -4))
    d += elm.Dot().at((7, -4))
    d += elm.Vss().at((7, -4)).label("−2.5 V", fontsize=7.6)

    # RFI filter
    d += elm.Resistor().at((10, 3)).to((12.6, 3)).label("100 Ω", ofst=0.1)
    d += elm.Resistor().at((10, 0.5)).to((12.6, 0.5)).label("100 Ω", loc="bottom", ofst=0.1)
    d += elm.Line().at((12.6, 3)).to((15.2, 3))
    d += elm.Line().at((12.6, 0.5)).to((15.2, 0.5))
    d += elm.Dot().at((13.2, 3))
    d += elm.Dot().at((13.2, 0.5))
    d += elm.Capacitor().at((13.2, 3)).to((13.2, 0.5)).label("10 nF\nC0G", loc="bottom", ofst=0.15)
    d += elm.Dot().at((14.4, 3))
    d += elm.Dot().at((14.4, 0.5))
    d += elm.Capacitor().at((14.4, 3)).to((14.4, 4.6)).label("1 nF", loc="bottom", ofst=0.1)
    d += elm.Ground().at((14.4, 4.6)).theta(180)
    d += elm.Capacitor().at((14.4, 0.5)).to((14.4, -1.1)).label("1 nF", loc="top", ofst=0.1)
    d += elm.Ground().at((14.4, -1.1))

    # in-amp
    op = elm.Opamp(leads=True, flip=True).right().at((15.6, 2.4)).anchor("in2")
    d += op
    d += elm.Line().at((15.2, 3)).to((15.2, op.absanchors["in2"][1]))
    d += elm.Line().at((15.2, op.absanchors["in2"][1])).to(op.absanchors["in2"])
    d += elm.Line().at((15.2, 0.5)).to((15.2, op.absanchors["in1"][1]))
    d += elm.Line().at((15.2, op.absanchors["in1"][1])).to(op.absanchors["in1"])
    cx, cy = op.absanchors["center"]
    # RG across the gain pins on the top edge
    p1, p2 = op.absanchors["vd"], op.absanchors["n2"]
    yt = cy + 2.0
    d += elm.Line().at(p1).to((p1[0], yt))
    d += elm.Line().at(p2).to((p2[0], cy + 1.35))
    d += elm.Line().at((p2[0], cy + 1.35)).to((p1[0] + 2.4, cy + 1.35))
    d += elm.Line().at((p1[0] + 2.4, cy + 1.35)).to((p1[0] + 2.4, yt))
    d += elm.Resistor(scale=0.6).at((p1[0], yt)).to((p1[0] + 2.4, yt)).label("$R_G$ 100 Ω", ofst=0.1)
    out = op.absanchors["out"]
    d += elm.Line().at(out).to((out[0] + 1.2, out[1])).linewidth(1.0)
    d += elm.Arrow().at((out[0] + 1.2, out[1])).to((out[0] + 1.2, out[1] - 1.9))
    d.add(elm.Label().at((out[0] + 1.2, out[1] - 2.6)).label("to 2 kHz\nAA filter", fontsize=7.6))

    # completion half-bridge (1 kΩ / 1 kΩ)
    xb = 23.4
    d += elm.Vdd().at((xb, 6.5)).label("+2.5 V", fontsize=7.6)
    d += elm.Resistor().at((xb, 6.5)).to((xb, 3)).label("1 kΩ\nfoil", loc="bottom", ofst=0.15)
    d += elm.Resistor().at((xb, 3)).to((xb, -0.5)).label("1 kΩ\nfoil", loc="bottom", ofst=0.15)
    d += elm.Vss().at((xb, -0.5)).label("−2.5 V", fontsize=7.6)
    d += elm.Dot().at((xb, 3))
    d += elm.Line().at((xb, 3)).to((xb - 1.2, 3))
    d += elm.Line().at((xb - 1.2, 3)).to((xb - 1.2, -2.0))
    d += elm.Line().at((xb - 1.2, -2.0)).to((10, -2.0))
    d += elm.Line().at((10, -2.0)).to((10, 0.5))
    d.draw()

    # cable shield and annotations (matplotlib)
    ax.add_patch(Rectangle((0.9, -0.9), 2.7, 8.1, fill=False, ec=GREY, lw=1.0, ls=(0, (4, 3))))
    ax.text(2.25, 7.45, "5 m shielded cable, 26 AWG", ha="center", fontsize=7.6, color=GREY)
    gx, gy = 3.6, -0.9
    ax.plot([gx, gx], [gy, gy - 0.5], color=GREEN, lw=1.0)
    for k, hw in enumerate((0.4, 0.26, 0.12)):
        ax.plot([gx - hw, gx + hw], [gy - 0.5 - 0.17 * k] * 2, color=GREEN, lw=1.2)
    ax.text(1.8, -2.0, "shield to iso GND at\nmodule end only;\nopen at gauge end", ha="center",
            va="top", fontsize=7.4, color=GREEN)
    ax.text(-0.9, 1.5, "specimen", rotation=90, va="center", ha="center", fontsize=7.4, color=GREY, style="italic")
    ax.text(18.6, 5.0, "INA828 class\nG = 1 + 50 kΩ/$R_G$ = 501", ha="center", va="bottom", fontsize=7.4)
    ax.text(11.3, 4.2, "RFI filter", ha="center", fontsize=7.6, weight="bold", color=BLUE)
    ax.text(14.4, 5.85, "iso GND", ha="center", fontsize=7.0, color=INK)
    ax.text(7.0, 4.1, "bridge output\n(sense node)", ha="center", fontsize=7.0, color=GREY)
    ax.set_xlim(-1.5, 25.6)
    ax.set_ylim(-5.4, 8.2)
    save(fig, "07", "fig-7-3-quarter-bridge-3wire")


# ----------------------------------------------------------------------------
# Figure 7.4 — bridge errors
# ----------------------------------------------------------------------------
def fig_7_4():
    fig, ax = new_fig(6.4, 3.8)
    eps = np.linspace(-3000, 3000, 601)
    x = GF * eps * 1e-6
    vr = (x / 4) / (1 + x / 2)
    eps_lin = 4 * vr / GF * 1e6
    err_nl = eps_lin - eps
    RL, RG = 0.67, 350.0
    err_lead = -RL / (RG + RL) * eps
    ax.axhspan(-0.1, 0.1, color=GREEN, alpha=0.35, lw=0)
    ax.plot(eps, err_nl, color=BLUE, lw=2.0, label="quarter-bridge nonlinearity, linear formula")
    ax.plot(eps, err_lead, color=ORANGE, lw=1.8, ls="--", label="3-wire lead desensitization (−0.19 %)")
    ax.plot([], [], color=GREEN, alpha=0.35, lw=6, label="after firmware correction (±0.1 µε)")
    ax.axhline(0, color=INK, lw=0.6)
    ax.set_xlim(-3000, 3000)
    ax.set_ylim(-12, 12)
    ax.set_xlabel("strain ε (µε)")
    ax.set_ylabel("reading error (µε)")
    ax.annotate(f"−{-err_nl[-1]:.1f} µε", xy=(3000, err_nl[-1]), xytext=(2350, -11.2),
                fontsize=8, color=BLUE, arrowprops=dict(arrowstyle="-", color=BLUE, lw=0.7))
    ax.annotate(f"−{-err_nl[0]:.1f} µε", xy=(-3000, err_nl[0]), xytext=(-2900, -11.2),
                fontsize=8, color=BLUE, arrowprops=dict(arrowstyle="-", color=BLUE, lw=0.7))
    ax.annotate(f"−{-err_lead[-1]:.1f} µε", xy=(3000, err_lead[-1]), xytext=(2350, -3.6),
                fontsize=8, color=ORANGE, arrowprops=dict(arrowstyle="-", color=ORANGE, lw=0.7))
    ax.annotate(f"+{err_lead[0]:.1f} µε", xy=(-3000, err_lead[0]), xytext=(-2700, 8.0),
                fontsize=8, color=ORANGE, arrowprops=dict(arrowstyle="-", color=ORANGE, lw=0.7))
    ax.text(600, 10.9, "2-wire connection: a 10 K cable-temperature\nchange shifts the zero by 75 µε (off scale)",
            fontsize=7.8, va="top", ha="left", bbox=dict(fc="#FBEAEA", ec=RED, lw=0.8, pad=3))
    ax.legend(loc="lower center", fontsize=7.8, bbox_to_anchor=(0.5, 0.02))
    save(fig, "07", "fig-7-4-bridge-errors")


# ----------------------------------------------------------------------------
# Figure 7.5 — filter chain
# ----------------------------------------------------------------------------
def design_fir():
    return signal.remez(255, [0, 200, 800, FS_ADC / 2], [1, 0], weight=[1, 3], fs=FS_ADC)


def fig_7_5():
    fir = design_fir()
    b_a, a_a = signal.butter(2, 2 * np.pi * FC_AA, analog=True)
    f = np.logspace(1, 5, 6000)
    _, ha = signal.freqs(b_a, a_a, worN=2 * np.pi * f)
    fm = np.mod(f, FS_ADC)
    _, hf = signal.freqz(fir, worN=fm, fs=FS_ADC)
    da = 20 * np.log10(np.abs(ha))
    df = 20 * np.log10(np.maximum(np.abs(hf), 1e-12))
    dc = da + df
    fig, ax = new_fig(6.6, 4.2)
    base = f <= FS_ADC / 2
    ax.semilogx(f[base], df[base], color=BLUE, lw=0.8, label="255-tap FIR at 32 kSa/s")
    ax.semilogx(f[~base], df[~base], color=BLUE, lw=0.6, alpha=0.3)
    ax.semilogx(f, da, color=ORANGE, lw=1.6, ls="--", label="analog 2nd-order Butterworth, 2 kHz")
    ax.semilogx(f, dc, color=INK, lw=2.2, label="cascade (input to logged stream)")
    ax.set_xlim(10, 1e5)
    ax.set_ylim(-120, 5)
    ax.set_xlabel("input frequency (Hz)")
    ax.set_ylabel("magnitude (dB)")
    marks = [(200, "200 Hz"), (800, "800 Hz"), (1800, "1.8 kHz"), (4000, "4 kHz"),
             (16000, "16 kHz"), (31800, "31.8 kHz")]
    trans = ax.get_xaxis_transform()
    for fx, t in marks:
        ax.axvline(fx, color=GREY, lw=0.6, ls=":")
        ax.text(fx, 1.015, t, transform=trans, fontsize=6.6, color=GREY, ha="center", va="bottom")
    ax.text(0.995, 0.97, "800 Hz: FIR stopband edge\n1.8 kHz: folds into 0–200 Hz at 2 kSa/s\n"
            "4 kHz: drive switching\n16 kHz: ADC Nyquist\n31.8 kHz: folds into 0–200 Hz at 32 kSa/s",
            transform=ax.transAxes, ha="right", va="top", fontsize=6.6, color=GREY, linespacing=1.3,
            bbox=dict(fc="white", ec="none", pad=1))
    a318 = 20 * np.log10(abs(signal.freqs(b_a, a_a, worN=[2 * np.pi * 31800])[1][0]))
    ax.plot(31800, a318, "o", color=ORANGE, ms=4)
    ax.annotate(f"−{-a318:.1f} dB", xy=(31800, a318), xytext=(40000, -35), fontsize=7.5, color=ORANGE,
                arrowprops=dict(arrowstyle="-", color=ORANGE, lw=0.7))
    stop = -20 * np.log10(np.abs(signal.freqz(fir, worN=np.linspace(800, 16000, 4000), fs=FS_ADC)[1]).max())
    ax.axhline(-stop, xmin=0, xmax=1, color=BLUE, lw=0.6, ls="--")
    ax.text(12, -stop + 1.5, f"FIR stopband ≤ −{stop:.1f} dB from 800 Hz to 16 kHz", fontsize=7.5, color=BLUE)
    ax.legend(loc="lower left", fontsize=7.4)
    # inset: passband ripple
    ins = ax.inset_axes([0.08, 0.36, 0.33, 0.28])
    fp = np.linspace(0.5, 200, 800)
    _, hfp = signal.freqz(fir, worN=fp, fs=FS_ADC)
    _, hap = signal.freqs(b_a, a_a, worN=2 * np.pi * fp)
    ins.plot(fp, 20 * np.log10(np.abs(hfp)), color=BLUE, lw=0.9)
    ins.plot(fp, 20 * np.log10(np.abs(hfp * hap)), color=INK, lw=1.4)
    ins.set_xlim(0, 200)
    ins.set_ylim(-0.003, 0.003)
    ins.set_yticks([-0.003, 0, 0.003])
    ins.set_xticks([0, 100, 200])
    ins.tick_params(labelsize=6.5)
    ins.set_title("passband ripple (dB), 0–200 Hz", fontsize=7)
    ins.set_facecolor("white")
    save(fig, "07", "fig-7-5-filter-chain-response")


# ----------------------------------------------------------------------------
# Figure 7.6 — rig spectrum before and after
# ----------------------------------------------------------------------------
def fig_7_6():
    rng = np.random.default_rng(7)
    fir = design_fir()
    T = 60.0
    n32 = int(T * FS_ADC)
    fs_log = FS_ADC // DEC
    t = np.arange(n32 // DEC) / fs_log

    def logged_noise(asd):
        """White noise of input ASD (µε/√Hz) at 32 kSa/s, FIR-filtered, decimated by 16."""
        w = rng.standard_normal(n32) * asd * np.sqrt(FS_ADC / 2)
        y = signal.fftconvolve(w, fir, mode="same")
        return y[::DEC]

    # before: white floor 0.02, low-frequency wander, mains lines
    wander = rng.standard_normal(t.size)
    bw, aw = signal.butter(1, 1.5, fs=fs_log)
    wander = signal.lfilter(bw, aw, wander)
    wander *= 0.6 / np.std(wander)
    before = logged_noise(0.02) + wander
    for fl, rms in ((50, 4.9), (150, 1.2), (250, 0.5)):
        before += np.sqrt(2) * rms * np.sin(2 * np.pi * fl * t + rng.uniform(0, 6.28))
    after = logged_noise(7.8e-9 / 2.5e-6)
    after += np.sqrt(2) * 0.2 * np.sin(2 * np.pi * 50 * t + 1.0)

    nper = 8192
    f, pb = signal.welch(before, fs_log, window="hann", nperseg=nper)
    _, pa = signal.welch(after, fs_log, window="hann", nperseg=nper)
    enbw = 1.5 * fs_log / nper
    fig, ax = new_fig(6.4, 3.9)
    m = f >= 1
    ax.loglog(f[m], np.sqrt(pb[m]), color=ORANGE, lw=1.0, label="before fixes")
    ax.loglog(f[m], np.sqrt(pa[m]), color=BLUE, lw=1.0, label="after fixes")
    r2 = 1 / np.sqrt(432)
    ax.axhline(r2, color=RED, ls="--", lw=1.1)
    ax.text(1.1, r2 * 1.25, f"R2 limit: 1 µε rms over 432 Hz ENBW ≈ {r2:.3f} µε/√Hz", color=RED, fontsize=7.6)
    ax.set_xlim(1, 1000)
    ax.set_ylim(1e-4, 10)
    ax.set_xlabel("frequency (Hz)")
    ax.set_ylabel("amplitude spectral density (µε/√Hz)")
    for fl, rms in ((50, 4.9), (150, 1.2), (250, 0.5)):
        pk = np.sqrt(pb[np.argmin(abs(f - fl))])
        ax.text(fl, pk * 1.35, f"{fl} Hz\n{rms} µε rms", ha="center", fontsize=7.2, color=ORANGE)
    pk = np.sqrt(pa[np.argmin(abs(f - 50))])
    ax.annotate("50 Hz residual\n0.2 µε rms", xy=(50, pk), xytext=(14, 0.15), fontsize=7.2, color=BLUE,
                arrowprops=dict(arrowstyle="-", color=BLUE, lw=0.7))
    ax.text(150, 0.0045, "floor 0.0031 µε/√Hz\n(0.065 µε rms in 432 Hz)", fontsize=7.2, color=BLUE,
            ha="center", va="bottom")
    ax.text(1.1, 0.33, "low-frequency\nwander", fontsize=7.2, color=ORANGE)
    ax.text(0.8, 0.02, f"60 s at 2 kSa/s, Welch, Hann, {nper} points (ENBW {enbw:.2f} Hz);\n"
            "lines read as rms over the bin", transform=ax.transAxes, ha="right", va="bottom",
            fontsize=6.8, color=GREY)
    ax.legend(loc="lower left", fontsize=8)
    save(fig, "07", "fig-7-6-rig-spectrum-before-after")


if __name__ == "__main__":
    fig_7_1()
    fig_7_2()
    fig_7_3()
    fig_7_4()
    fig_7_5()
    fig_7_6()
