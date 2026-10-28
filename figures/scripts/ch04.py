"""Figures for Chapter 4 — Prototyping and Verification.

Run from the repository root:  python figures/scripts/ch04.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Polygon, Rectangle  # noqa: E402

from figstyle import COLORS, INK, save, new_fig  # noqa: E402
from figstyle import schematic as _schematic  # noqa: E402

BLUE, ORANGE, GREEN, PINK, YELLOW, SKY = COLORS[:6]
RED = "#C62828"
GREY = "#888888"
DGREEN = "#1E8A4C"
C_PWR, C_DIG, C_NET = RED, "#1F5FA8", "#6A6A6A"


def schematic(*a, **k):
    """figstyle.schematic with the axes filling the figure (diagrams only)."""
    fig, ax = _schematic(*a, **k)
    fig.subplots_adjust(left=0.01, right=0.99, bottom=0.01, top=0.99)
    return fig, ax


def arr(ax, x0, y0, x1, y1, color=INK, lw=1.1, ls="-", both=False, ms=8, z=2):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="<|-|>" if both else "-|>",
                                 color=color, lw=lw, ls=ls, mutation_scale=ms, shrinkA=0,
                                 shrinkB=0, zorder=z))


def line(ax, pts, color=INK, lw=1.1, ls="-", z=1.5):
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=color, lw=lw, ls=ls, zorder=z, solid_capstyle="butt")


def rbox(ax, x, y, w, h, text, fc="white", ec=INK, lw=1.0, fs=7.6, ls="-", weight="normal",
         z=3, ha="center"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc=fc, ec=ec, lw=lw, ls=ls, zorder=z))
    if text:
        tx = x + w / 2 if ha == "center" else x + 0.25
        ax.text(tx, y + h / 2, text, ha=ha, va="center", fontsize=fs, weight=weight,
                zorder=z + 0.1, linespacing=1.15)


# ----------------------------------------------------------------------------
# Figure 4.1 — PM-4 architecture and bench rig
# ----------------------------------------------------------------------------
def fig_4_1():
    fig, ax = schematic(6.8, 6.0, xlim=(0, 20), ylim=(0, 17.6))
    # ---------------- top: PM-4 board
    ax.add_patch(FancyBboxPatch((0.15, 8.75), 19.7, 8.7, boxstyle="round,pad=0.02,rounding_size=0.25",
                                fc="#F8F8F8", ec=INK, lw=1.2, ls="--"))
    ax.text(0.4, 17.1, "PM-4 board (rev B)", fontsize=8.2, weight="bold", va="center")
    rows = [15.9, 14.6, 13.3, 12.0]
    rbox(ax, 0.4, 11.6, 1.7, 4.7, "12 V\nbus\ninput", fc="#FBEAEA", fs=7.6)
    for n, y in enumerate(rows):
        line(ax, [(2.1, y), (3.0, y)], color=C_PWR, lw=1.6)
        ax.add_patch(Rectangle((3.0, y - 0.17), 1.2, 0.34, fc="#F3C9C9", ec=INK, lw=0.9, zorder=3))
        line(ax, [(4.2, y), (17.9, y)], color=C_PWR, lw=1.6)
        rbox(ax, 17.9, y - 0.42, 1.8, 0.84, f"Server {n + 1}", fs=7.2, fc="#FBEAEA")
        # Kelvin taps
        line(ax, [(3.15, y + 0.17), (3.15, y + 0.78), (5.0, y + 0.78)], color=C_DIG, lw=0.9)
        line(ax, [(4.05, y + 0.17), (4.05, y + 0.42), (5.0, y + 0.42)], color=C_DIG, lw=0.9)
        rbox(ax, 5.0, y + 0.22, 2.3, 0.78, f"INA228  0x{0x40 + n:02X}", fs=6.9, fc="#E3EDF7")
        line(ax, [(7.3, y + 0.6), (8.3, y + 0.6)], color=C_DIG, lw=1.0)
    ax.text(3.6, rows[-1] - 0.3, "2 mΩ shunts", fontsize=6.6, ha="center", va="top")
    ax.text(5.05, rows[0] + 1.12, "Kelvin taps", fontsize=6.4, color=C_DIG, va="bottom")
    # I2C bus
    line(ax, [(8.3, rows[0] + 0.6), (8.3, 10.55)], color=C_DIG, lw=1.4)
    ax.text(8.45, 11.3, "I²C 400 kHz", fontsize=7, color=C_DIG, va="center")
    # lower row of the board
    yb, hb = 9.05, 1.5
    rbox(ax, 0.4, yb, 3.0, hb, "Buck 12 V → 3.3 V\n(powers all ICs)", fs=7.0, fc="#FBEAEA")
    line(ax, [(1.25, 11.6), (1.25, yb + hb)], color=C_PWR, lw=1.3)
    rbox(ax, 3.9, yb, 2.0, hb, "FRAM\n(added in\nrev B)", fs=6.8, ls="--", fc="white")
    rbox(ax, 6.6, yb, 3.3, hb, "STM32G071\nMCU", fs=7.6, fc="#DCE6F2", weight="bold")
    line(ax, [(8.3, 10.55), (8.3, yb + hb)], color=C_DIG, lw=1.4)
    arr(ax, 6.6, yb + hb / 2, 5.9, yb + hb / 2, color=C_DIG, both=True, lw=0.9, ls="--")
    rbox(ax, 10.6, yb, 2.6, hb, "RS-485\ntransceiver", fs=7.2)
    arr(ax, 9.9, yb + hb / 2, 10.6, yb + hb / 2, color=C_DIG, both=True, lw=0.9)
    rbox(ax, 13.9, yb, 2.6, hb, "Modbus RTU\n19.2 kbaud\nterminal", fs=6.9, fc="#EFEFEF")
    arr(ax, 13.2, yb + hb / 2, 13.9, yb + hb / 2, color=C_DIG, both=True, lw=0.9)
    rbox(ax, 17.0, yb, 2.7, hb, "SWD header\n+ USB-C\nservice port", fs=6.9, fc="#EFEFEF")
    line(ax, [(9.4, yb + hb), (9.4, 10.8), (18.35, 10.8), (18.35, yb + hb)], color=C_DIG, lw=0.9)
    # ---------------- bottom: bench rig
    ax.text(0.4, 8.2, "Verification rig", fontsize=8.2, weight="bold", va="center")
    ax.add_patch(FancyBboxPatch((8.9, 3.5), 4.9, 4.0, boxstyle="round,pad=0.02,rounding_size=0.2",
                                fc="#EAF4FB", ec=SKY, lw=1.1, ls="--"))
    ax.text(11.35, 7.2, "temperature chamber", fontsize=6.8, color="#3D7FA6", ha="center",
            style="italic")
    yr, hr = 4.4, 1.8
    rbox(ax, 0.3, yr, 3.2, hr, "Programmable DC\nsupply 0–30 V,\n20 A", fs=7.0)
    rbox(ax, 4.6, yr + 0.2, 3.2, hr - 0.4, "Reference shunt\n10 A / 100 mV\n(±0.01 %)", fs=6.9,
         fc="#FBEAEA")
    rbox(ax, 9.5, yr, 3.7, hr, "PM-4 channel\nunder test", fs=7.4, fc="#DCE6F2", weight="bold")
    rbox(ax, 14.7, yr, 3.4, hr, "DC electronic load\n0–30 A, CC mode", fs=7.0)
    yc = yr + hr / 2
    for x0, x1 in [(3.5, 4.6), (7.8, 9.5), (13.2, 14.7)]:
        arr(ax, x0, yc, x1, yc, color=C_PWR, lw=1.5)
    line(ax, [(16.4, yr), (16.4, 3.15), (1.9, 3.15), (1.9, yr)], color=C_PWR, lw=1.2)
    ax.text(9.2, 3.0, "return", fontsize=6.4, color=C_PWR, va="top", ha="center")
    # DMMs
    rbox(ax, 4.6, 6.6, 3.2, 1.0, "6½-digit DMM\n(shunt voltage)", fs=6.8)
    line(ax, [(5.4, yr + hr - 0.2), (5.4, 6.6)], color=INK, lw=0.8)
    line(ax, [(7.0, yr + hr - 0.2), (7.0, 6.6)], color=INK, lw=0.8)
    rbox(ax, 14.7, 6.6, 3.4, 1.0, "2nd DMM\n(bus voltage)", fs=6.8)
    line(ax, [(14.7, 7.1), (14.2, 7.1), (14.2, yc + 0.3), (13.2, yc + 0.3)], color=INK, lw=0.8)
    # thermocouple
    ax.plot([11.35], [yr + 0.25], marker="o", ms=4, color=ORANGE, zorder=5)
    ax.text(9.05, yr - 0.15, "thermocouple on shunt", fontsize=6.4, color=ORANGE, va="top")
    # PC and links
    rbox(ax, 7.4, 0.25, 4.4, 1.5, "PC: Python test script\n(limits file, results)", fs=7.0,
         fc="#E4F2EA")
    yl = 2.45
    line(ax, [(0.9, yl), (19.4, yl)], color=C_NET, lw=1.3)
    ax.text(1.15, yl - 0.12, "LAN: SCPI", fontsize=6.6, color=C_NET, va="top")
    for x in (1.0, 16.9):
        line(ax, [(x, yl), (x, yr)], color=C_NET, lw=1.0)
    line(ax, [(4.6, 7.1), (4.1, 7.1), (4.1, yl)], color=C_NET, lw=1.0)
    line(ax, [(18.1, 7.1), (19.4, 7.1), (19.4, yl)], color=C_NET, lw=1.0)
    line(ax, [(9.6, 1.75), (9.6, yl)], color=C_NET, lw=1.3)
    rbox(ax, 13.6, 0.25, 3.6, 1.5, "USB–RS-485\nadapter", fs=7.0)
    arr(ax, 11.8, 1.0, 13.6, 1.0, color=C_DIG, both=True, lw=0.9)
    ax.text(12.7, 1.15, "USB", fontsize=6.4, color=C_DIG, ha="center", va="bottom")
    line(ax, [(15.4, 1.75), (15.4, 2.9), (12.6, 2.9), (12.6, yr)], color=C_DIG, lw=1.0)
    ax.text(15.55, 2.0, "Modbus RTU", fontsize=6.6, color=C_DIG, va="center")
    save(fig, "04", "fig-4-1-pm4-architecture-and-rig")


# ----------------------------------------------------------------------------
# Figure 4.2 — calibration error
# ----------------------------------------------------------------------------
def fig_4_2():
    i_ref = np.array([0.5, 2.0, 4.0, 6.0, 8.0, 10.0])
    i_raw = np.array([0.5063, 2.0194, 4.0388, 6.0539, 8.0670, 10.0861])
    gain, offset = np.polyfit(i_ref, i_raw, 1)
    i_chk = np.array([1.0, 3.0, 5.0, 7.0, 9.0])
    r_chk = np.array([1.0105, 3.0282, 5.0422, 7.0616, 9.0782])
    err_after = ((r_chk - offset) / gain - i_chk) * 1e3
    err_before = (i_raw - i_ref) * 1e3
    I = np.linspace(0, 10, 101)
    tol = (0.005 * I + 0.010) * 1e3
    acc = tol - 0.8 * I
    fig, ax = new_fig(6.4, 4.0)
    ax.fill_between(I, -acc, acc, color=GREEN, alpha=0.10, lw=0)
    ax.plot(I, tol, color=INK, lw=1.2)
    ax.plot(I, -tol, color=INK, lw=1.2, label="R1 tolerance ±(0.5 % + 10 mA)")
    ax.plot(I, acc, color=DGREEN, lw=1.2, ls="--")
    ax.plot(I, -acc, color=DGREEN, lw=1.2, ls="--", label="guard-banded limit (−0.8 mA/A)")
    ax.plot(I, (gain - 1) * I * 1e3 + offset * 1e3, color=ORANGE, lw=0.8, ls=":")
    ax.plot(i_ref, err_before, "o", color=ORANGE, ms=6,
            label=f"before calibration (gain {100 * (gain - 1):.2f} %, offset {1e3 * offset:+.1f} mA)")
    ax.plot(i_chk, err_after, "D", color=BLUE, ms=5.5, label="after calibration (verification points)")
    for x, e in zip(i_chk, err_after):
        ax.text(x, e - 5.5, f"{e:+.2f}", fontsize=6.8, color=BLUE, ha="center", va="top")
    ax.annotate(f"{err_before[-1]:.0f} mA at 10 A:\noutside R1 (±60 mA)", (10, err_before[-1]),
                (7.2, 88), fontsize=7.5, color=RED, ha="right", va="center",
                arrowprops=dict(arrowstyle="-", color=RED, lw=0.7))
    ax.text(10.05, 60, "60", fontsize=7, va="center")
    ax.text(10.05, 52, "52", fontsize=7, va="center", color=DGREEN)
    ax.axhline(0, color=GREY, lw=0.6)
    ax.set_xlim(0, 10.6)
    ax.set_ylim(-80, 100)
    ax.set_xlabel("Reference current (A)")
    ax.set_ylabel("Channel-1 current error (mA)")
    ax.legend(loc="lower left", fontsize=7.2)
    save(fig, "04", "fig-4-2-calibration-error")


# ----------------------------------------------------------------------------
# Figure 4.3 — half-split diagnosis
# ----------------------------------------------------------------------------
def fig_4_3():
    fig, ax = schematic(6.8, 5.6, xlim=(0, 20), ylim=(0, 16.4))

    def diamond(x, y, s=0.55, label=""):
        ax.add_patch(Polygon([(x, y + s), (x + s, y), (x, y - s), (x - s, y)], closed=True,
                             fc="#FFE9A8", ec=INK, lw=0.9, zorder=4))
        ax.text(x, y, label, ha="center", va="center", fontsize=7, weight="bold", zorder=5)
    W = 12.0
    rbox(ax, 0.3, 14.4, W, 1.7, "", fc="#FBE3E3", ec=RED, lw=1.3)
    ax.text(0.6, 15.25, "Symptom: +3.0 % at 10 A on all channels of all boards\n"
            "(a gain error), rising a further 0.73 % over 45 °C of shunt temperature",
            fontsize=7.7, va="center", zorder=5)
    qs = [("Split 1: does the INA228 shunt-voltage register equal a DMM\n"
           "reading at the INA228 input pins?",
           "Yes (to 0.01 %): firmware and scaling\ncleared (I²C, register scaling, Modbus)"),
          ("Split 2: does the DMM at the INA228 input pins equal the DMM\n"
           "at the sense-trace taps on the shunt pads?",
           "Yes (20.60 mV both, at 10 A):\nRC filter and bias current cleared"),
          ("Split 3: does the DMM at the Kelvin test pads on the shunt body,\n"
           "divided by the reference current, equal 2 mΩ within 1 %?",
           "Yes (20.00 mV at 10 A):\nshunt part cleared")]
    ys = [11.6, 8.8, 6.0]
    hq = 1.8
    arr(ax, 6.3, 14.4, 6.3, ys[0] + hq)
    for k, ((q, a), y) in enumerate(zip(qs, ys)):
        rbox(ax, 0.3, y, W, hq, "", fc="#FFF6D6")
        diamond(1.05, y + hq / 2, label=f"Q{k + 1}")
        ax.text(1.85, y + hq / 2, q, fontsize=7.4, va="center", zorder=5)
        rbox(ax, 13.2, y, 6.5, hq, a, fc="#E4F2EA", ec=DGREEN, fs=7.2)
        arr(ax, 12.3, y + hq / 2, 13.2, y + hq / 2, color=DGREEN)
        ax.text(12.75, y + hq / 2 + 0.15, "yes", fontsize=6.8, color=DGREEN, ha="center",
                va="bottom")
        if k < 2:
            arr(ax, 6.3, y, 6.3, ys[k + 1] + hq)
            ax.text(6.45, y - 0.5, "split the remaining suspects again", fontsize=6.6,
                    va="center", color="#555555", style="italic")
    ax.text(6.45, ys[2] - 0.5, "all three splits pass, yet Kelvin pads read 20.00 mV, "
            "sense traces 20.60 mV", fontsize=6.6, va="center", color="#555555", style="italic")
    yb, hb = 0.3, 4.4
    boxes = [(0.3, "Hypothesis",
              "Sense taps at the pad edge\ninclude copper between the\npad edge and the resistive\n"
              "element: 20.60 mV vs\n20.00 mV at 10 A\n→ 60 µΩ in the sense loop", "#E3EDF7", INK),
             (7.0, "Intervention",
              "Cut the sense traces; wire\n0.1 mm enamelled wire to\nthe shunt body terminations\n"
              "→ error falls to +0.08 %.\nRestore the traces\n→ error returns.", "#E3EDF7", INK),
             (13.7, "Root cause",
              "Layout Kelvin-connection\nerror (60 µΩ copper,\n3930 ppm/°C, in the loop).\n"
              "Fix in the rev B\nfootprint: taps inside\nthe pads.", "#FBE3E3", RED)]
    for x, title, body, fc, ec in boxes:
        rbox(ax, x, yb, 6.0, hb, "", fc=fc, ec=ec, lw=1.2)
        ax.text(x + 3.0, yb + hb - 0.35, title, ha="center", va="top", fontsize=8, weight="bold",
                zorder=5)
        ax.text(x + 3.0, yb + hb - 1.0, body, ha="center", va="top", fontsize=7.1, zorder=5,
                linespacing=1.15)
    arr(ax, 3.3, ys[2], 3.3, yb + hb)
    arr(ax, 6.3, yb + hb / 2, 7.0, yb + hb / 2)
    arr(ax, 13.0, yb + hb / 2, 13.7, yb + hb / 2)
    save(fig, "04", "fig-4-3-half-split-diagnosis")


# ----------------------------------------------------------------------------
# Figure 4.4 — rev A vs rev B drift
# ----------------------------------------------------------------------------
def fig_4_4():
    R_sh, R_cu, a_sh, a_cu = 2000.0, 60.0, 50.0, 3930.0          # µΩ, ppm/°C
    a_eff_A = (R_cu * a_cu + R_sh * a_sh) / (R_sh + R_cu)          # 163 ppm/°C
    a_eff_B = a_sh
    T = np.linspace(25, 75, 101)
    Tm = np.array([25, 40, 55, 70])
    fig, ax = new_fig(6.4, 3.9)
    ax.axvspan(25, 70, color=GREY, alpha=0.10, lw=0)
    ax.text(47.5, 0.97, "operating range of shunt temperature (25–70 °C)", ha="center",
            va="top", fontsize=7.5, color="#555555")
    for a, c, lab in [(a_eff_A, RED, "rev A: copper in the sense loop"),
                      (a_eff_B, BLUE, "rev B: corrected Kelvin footprint")]:
        ax.plot(T, a * 1e-4 * (T - 25), color=c, lw=1.8,
                label=f"{lab} ({a * 1e-4:.4f} %/°C)")
        ax.plot(Tm, a * 1e-4 * (Tm - 25), "o", color=c, ms=5.5)
        ax.text(69.5, a * 1e-4 * 45 + 0.03, f"{a * 1e-4 * 45:.3f} % at 70 °C", fontsize=7.3,
                color=c, va="bottom", ha="right")
    ax.axhline(0.6, color=INK, ls="--", lw=1.0)
    ax.text(26, 0.615, "R1 limit at 10 A: 0.60 %", fontsize=7.5, va="bottom")
    ax.axhline(0.505, color=ORANGE, ls="--", lw=1.0)
    ax.text(26, 0.49, "drift allowance: 0.60 − 0.095 = 0.505 %",
            fontsize=7.5, va="top", color=ORANGE)
    ax.set_xlim(25, 75)
    ax.set_ylim(-0.1, 1.0)
    ax.set_xlabel("Shunt temperature (°C)")
    ax.set_ylabel("Current-reading error at 10 A (%)")
    ax.legend(loc="upper left", bbox_to_anchor=(0.0, 0.88), fontsize=7.6)
    ax.text(74.5, -0.08, "both calibrated at 25 °C; markers: chamber points", fontsize=6.8,
            ha="right", va="bottom", color="#555555", style="italic")
    save(fig, "04", "fig-4-4-revA-revB-drift")


# ----------------------------------------------------------------------------
# Figure 4.5 — nightly regression trend
# ----------------------------------------------------------------------------
def fig_4_5():
    rng = np.random.default_rng(4)
    b = np.arange(1, 31)
    pw = np.empty(30)
    pw[:17] = rng.uniform(305, 315, 17)
    pw[17] = 395
    pw[18:] = 312 + rng.uniform(-2.5, 2.5, 12)
    pw[18] = 312
    ie = rng.uniform(0.03, 0.07, 30)
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.4, 4.8), sharex=True,
                                 gridspec_kw=dict(hspace=0.12))
    a1.axhspan(260, 360, color=GREEN, alpha=0.10, lw=0)
    a1.axhline(310, color=DGREEN, lw=0.8, ls=":")
    for yv in (260, 360):
        a1.axhline(yv, color=DGREEN, lw=0.9, ls="--")
    a1.text(30.4, 362, "drift threshold\n310 ± 50 mW", fontsize=7, color=DGREEN, va="bottom",
            ha="right")
    a1.axhline(500, color=RED, lw=1.3)
    a1.text(0.8, 497, "R6 limit 500 mW", fontsize=7.5, color=RED, va="top")
    a1.plot(b, pw, "-o", color=BLUE, ms=3.5, lw=1.0)
    a1.plot([18], [395], "o", ms=9, mfc="none", mec=RED, mew=1.5)
    a1.annotate("build 18: DRIFT\nidle loop polls UART,\nstop mode lost (+85 mW)", (18, 395),
                (10.5, 440), fontsize=7.2, color=RED, ha="center", va="center",
                arrowprops=dict(arrowstyle="-", color=RED, lw=0.7))
    a1.annotate("build 19: fix\n(312 mW)", (19, pw[18]), (23.5, 430), fontsize=7.2, ha="center",
                va="center", arrowprops=dict(arrowstyle="-", lw=0.7))
    a1.set_ylim(250, 520)
    a1.set_ylabel("Supply power (mW)")
    a2.axhspan(-0.01, 0.11, color=GREEN, alpha=0.10, lw=0)
    for yv in (-0.01, 0.11):
        a2.axhline(yv, color=DGREEN, lw=0.9, ls="--")
    a2.text(30.4, 0.12, "drift threshold 0.05 ± 0.06 %", fontsize=7, color=DGREEN,
            va="bottom", ha="right")
    for yv in (0.6, -0.6):
        a2.axhline(yv, color=RED, lw=1.3)
    a2.text(0.8, 0.585, "R1 limit +0.60 %", fontsize=7.5, color=RED, va="top")
    a2.text(0.8, -0.585, "R1 limit −0.60 %", fontsize=7.5, color=RED, va="bottom")
    a2.plot(b, ie, "-o", color=BLUE, ms=3.5, lw=1.0)
    a2.set_ylim(-0.7, 0.7)
    a2.set_ylabel("Current error\nat 10 A (%)")
    a2.set_xlabel("Nightly build number")
    a2.set_xlim(0.5, 30.5)
    a2.set_xticks([1, 5, 10, 15, 18, 20, 25, 30])
    save(fig, "04", "fig-4-5-nightly-regression-trend")


if __name__ == "__main__":
    fig_4_1()
    fig_4_2()
    fig_4_3()
    fig_4_4()
    fig_4_5()
