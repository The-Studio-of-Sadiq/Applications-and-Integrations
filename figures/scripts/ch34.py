"""Figures for Chapter 34 — Project: Autonomous Line-Following Robot.

Run from the repository root:  python figures/scripts/ch34.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402
from scipy.stats import norm  # noqa: E402
import schemdraw  # noqa: E402
import schemdraw.elements as elm  # noqa: E402

from figstyle import COLORS, INK, box, save, schematic, new_fig  # noqa: E402

schemdraw.use("matplotlib")

BLUE, ORANGE, GREEN, PINK, YELLOW, SKY = COLORS[:6]
RED = "#C62828"
GREY = "#777777"


def tint(c, a="30"):
    return c + a


def line(ax, pts, color=INK, lw=1.1, ls="-", head=True, both=False):
    """Poly-line through pts with an arrow head on the last segment."""
    xs, ys = zip(*pts)
    if len(pts) > 2:
        ax.plot(xs[:-1], ys[:-1], color=color, lw=lw, ls=ls, solid_capstyle="butt")
    if head:
        ax.annotate("", xy=pts[-1], xytext=pts[-2],
                    arrowprops=dict(arrowstyle="<|-|>" if both else "-|>", color=color, lw=lw,
                                    ls=ls, shrinkA=0, shrinkB=0, mutation_scale=10))
    else:
        ax.plot(xs[-2:], ys[-2:], color=color, lw=lw, ls=ls)


# ----------------------------------------------------------------------------
# Figure 34.1 — architecture
# ----------------------------------------------------------------------------
def fig_34_1():
    fig, ax = schematic(6.8, 5.0, xlim=(0, 18.2), ylim=(-0.3, 12.8))
    fs = 7.6
    # sensing (left)
    box(ax, 0.1, 8.6, 4.5, 2.4, "Reflectance array\n8 × QRE1113-class\npitch 9.5 mm, 3 mm high\n80 mm ahead of axle",
        fc=tint(GREEN), fontsize=7.2)
    box(ax, 0.1, 6.0, 4.5, 1.4, "IR LED switch\nAO3400, 160 mA", fc=tint(GREEN), fontsize=fs)
    box(ax, 0.1, 3.5, 4.5, 1.6, "2 × magnetic encoders\n12 CPR on motor shafts", fc=tint(GREEN), fontsize=fs)
    # MCU (centre)
    box(ax, 6.6, 3.5, 4.0, 7.5, "", fc=tint(BLUE))
    ax.text(8.6, 10.3, "STM32G431\n170 MHz M4F", ha="center", va="center", fontsize=8.2,
            weight="bold", color=INK)
    periph = ["ADC1 + DMA", "TIM6 1 kHz tick", "GPIO", "TIM3, TIM4\nencoder mode",
              "TIM1 PWM 20 kHz", "USART", "ADC (VBAT)"]
    for i, p in enumerate(periph):
        ax.text(8.6, 9.35 - i * 0.84, p, ha="center", va="center", fontsize=7.2, color=INK)
    # actuation (right)
    box(ax, 12.7, 8.6, 4.5, 2.4, "DRV8833 dual H-bridge\nlimit 1.33 A per channel\n(0.15 Ω sense)",
        fc=tint(ORANGE), fontsize=fs)
    box(ax, 12.7, 4.6, 4.5, 2.6, "2 × gearmotor 30:1\n6 V high-power\n32 mm wheels\ntrack 110 mm",
        fc=tint(ORANGE), fontsize=fs)
    # side peripherals (top)
    box(ax, 4.0, 11.6, 3.6, 1.05, "BLE UART module", fc=tint(PINK), fontsize=fs)
    box(ax, 9.6, 11.6, 3.6, 1.05, "IR start receiver", fc=tint(PINK), fontsize=fs)
    # power (bottom row)
    pw = [(0.1, "2S LiPo\n300 mAh"), (3.0, "reverse\nprotection\n(P-MOSFET)"), (5.9, "VM bus\n6.4–8.4 V"),
          (9.4, "buck 3.3 V\n1 A"), (12.9, "divider\n20 k / 10 k\n100 nF")]
    W = 2.6
    for x, t in pw:
        box(ax, x, 0.5, W, 1.6, t, fc=tint(YELLOW, "40"), fontsize=fs)
    line(ax, [(2.7, 1.3), (3.0, 1.3)], color=ORANGE)
    line(ax, [(5.6, 1.3), (5.9, 1.3)], color=ORANGE)
    line(ax, [(8.5, 1.3), (9.4, 1.3)], color=ORANGE)
    # VM bus to divider and to the DRV8833 VM pin, routed under the row
    line(ax, [(7.2, 0.5), (7.2, 0.1), (17.75, 0.1), (17.75, 9.8), (17.2, 9.8)], color=ORANGE)
    line(ax, [(14.2, 0.1), (14.2, 0.5)], color=ORANGE)
    ax.text(17.85, 5.5, "VM", ha="left", va="center", fontsize=7, color=ORANGE)
    # 3.3 V rail
    line(ax, [(9.9, 2.1), (9.9, 3.5)], color=ORANGE)
    ax.text(9.75, 2.9, "3.3 V", ha="right", va="center", fontsize=7, color=ORANGE)
    line(ax, [(9.9, 2.6), (2.35, 2.6), (2.35, 3.5)], color=ORANGE)
    ax.text(2.5, 2.65, "3.3 V to sensors, encoders, BLE", ha="left", va="bottom", fontsize=7,
            color=ORANGE)
    # divider to ADC
    line(ax, [(14.2, 2.1), (14.2, 3.05), (10.3, 3.05), (10.3, 3.5)], color=GREY)
    ax.text(12.3, 3.1, "VBAT → ADC", ha="center", va="bottom", fontsize=7, color=GREY)
    # signal arrows with interface labels
    line(ax, [(4.6, 9.8), (6.6, 9.8)])
    ax.text(5.6, 9.88, "8 analog\nlines", ha="center", va="bottom", fontsize=7)
    line(ax, [(6.6, 7.7), (5.6, 7.7), (5.6, 6.7), (4.6, 6.7)])
    ax.text(5.65, 7.8, "LED_EN", ha="center", va="bottom", fontsize=7)
    line(ax, [(2.35, 7.4), (2.35, 8.6)])
    ax.text(2.5, 8.0, "LED cathodes", ha="left", va="center", fontsize=7)
    line(ax, [(4.6, 4.3), (6.6, 4.3)])
    ax.text(5.6, 4.38, "A/B quad.\n×2", ha="center", va="bottom", fontsize=7)
    line(ax, [(10.6, 10.2), (12.7, 10.2)])
    ax.text(11.65, 10.28, "4 PWM\nAIN/BIN", ha="center", va="bottom", fontsize=7)
    line(ax, [(12.7, 9.0), (10.6, 9.0)])
    ax.text(11.65, 8.9, "nFAULT\n→ GPIO", ha="center", va="top", fontsize=7)
    line(ax, [(14.95, 8.6), (14.95, 7.2)])
    ax.text(15.1, 7.9, "AOUT, BOUT\n≤ 1.33 A", ha="left", va="center", fontsize=7)
    line(ax, [(5.8, 11.6), (5.8, 11.3), (7.3, 11.3), (7.3, 11.0)], both=True)
    ax.text(5.65, 11.42, "USART", ha="right", va="center", fontsize=7)
    line(ax, [(11.4, 11.6), (11.4, 11.3), (9.9, 11.3), (9.9, 11.0)])
    ax.text(11.55, 11.42, "GPIO", ha="left", va="center", fontsize=7)
    # section labels
    for x, t in [(2.35, "SENSING"), (14.95, "ACTUATION")]:
        ax.text(x, 12.1, t, ha="center", va="center", fontsize=8, color=GREY, weight="bold")
    ax.text(16.6, 2.0, "POWER", ha="center", va="center", fontsize=8, color=GREY, weight="bold")
    save(fig, "34", "fig-34-1-robot-architecture")


# ----------------------------------------------------------------------------
# Figure 34.2 — centroid transfer
# ----------------------------------------------------------------------------
XS = (np.arange(8) - 3.5) * 9.5


def centroid(y, sigma, w=19.0, thr=0.05):
    """Weighted centroid of Gaussian-footprint readings of a w-mm line at offset y (mm)."""
    n = norm.cdf((y + w / 2 - XS) / sigma) - norm.cdf((y - w / 2 - XS) / sigma)
    n = np.where(n < thr, 0.0, n)
    return (n * XS).sum() / n.sum()


def fig_34_2():
    fig, ax = new_fig(6.4, 4.2)
    y = np.linspace(-35, 35, 2801)
    e15 = np.array([centroid(v, 1.5) for v in y])
    e30 = np.array([centroid(v, 3.0) for v in y])
    ax.plot(y, y, ls="--", color=GREY, lw=1.0, label="ideal  $\\hat y = y$")
    ax.plot(y, e15, color=ORANGE, label="height 1.5 mm ($\\sigma$ ≈ 1.5 mm, P1)")
    ax.plot(y, e30, color=BLUE, label="height 3 mm ($\\sigma$ ≈ 3 mm, Rev A)")
    for s in (-33.25, 33.25):
        ax.axvline(s, color=GREY, ls=":", lw=1.0)
    ax.text(-32.6, -14, "outer sensors\n±33.25 mm", ha="left", va="center", fontsize=8, color=GREY)
    ax.set_xlim(-35, 35)
    ax.set_ylim(-35, 35)
    ax.set_xlabel("true line offset $y$ (mm)")
    ax.set_ylabel("estimated position $\\hat y$ (mm)")
    ax.legend(loc="upper left", fontsize=8)
    ax.grid(True, lw=0.5)
    # inset: error near centre
    ins = ax.inset_axes([0.62, 0.10, 0.34, 0.36])
    yi = np.linspace(-6, 6, 1201)
    ins.plot(yi, [centroid(v, 1.5) - v for v in yi], color=ORANGE, lw=1.3)
    ins.plot(yi, [centroid(v, 3.0) - v for v in yi], color=BLUE, lw=1.3)
    ins.axhline(0, color=GREY, lw=0.6)
    ins.set_xlim(-6, 6)
    ins.set_ylim(-2.5, 2.5)
    ins.set_xlabel("$y$ (mm)", fontsize=7, labelpad=1)
    ins.set_ylabel("error (mm)", fontsize=7, labelpad=1)
    ins.tick_params(labelsize=7)
    ins.set_facecolor("white")
    ins.set_title("error; P1 dead zone ±2 mm", fontsize=7, pad=2)
    save(fig, "34", "fig-34-2-centroid-transfer")


# ----------------------------------------------------------------------------
# Figure 34.3 — power entry, motor drive and sensor channel
# ----------------------------------------------------------------------------
def fig_34_3():
    fig, ax = plt.subplots(figsize=(6.8, 4.6))
    ax.axis("off")
    ax.set_aspect("equal")
    d = schemdraw.Drawing(canvas=ax, show=False)
    d.config(unit=2.0, fontsize=7.5, lw=1.0)

    def gnd(x, y):
        d.add(elm.Ground().at((x, y)))

    def txt(x, y, t, ha="left", va="center", fs=7.2, color=INK, **kw):
        ax.text(x, y, t, ha=ha, va=va, fontsize=fs, color=color, **kw)

    G, T = 8.5, 13.0                  # ground level and VM rail of the power section
    # --- battery, switch, reverse protection --------------------------------------
    d += elm.Battery().up().at((0, G)).to((0, 11.0))
    gnd(0, G)
    d += elm.Line().up().at((0, 11.0)).to((0, T))
    d += elm.Switch().right().at((0, T)).to((2.0, T))
    q = elm.PFet().theta(-90).anchor("drain").at((2.0, T))
    d += q
    gx, gy = q.absanchors["gate"]
    sx = q.absanchors["source"][0]
    d += elm.Line().down().at((gx, gy)).to((gx, 10.6))
    d += elm.Dot().at((gx, 10.6))
    d += elm.Resistor().down().at((gx, 10.6)).to((gx, G))
    gnd(gx, G)
    xz = sx + 0.9
    d += elm.Line().right().at((gx, 10.6)).to((xz, 10.6))
    d += elm.Zener().up().at((xz, 10.6)).to((xz, T))
    d += elm.Line().right().at((sx, T)).to((xz, T))
    d += elm.Dot().at((xz, T))
    # VM rail
    XR = 22.6
    d += elm.Line().right().at((xz, T)).to((XR, T))
    # bulk and HF capacitors
    for x in (6.6, 8.8):
        d += elm.Dot().at((x, T))
        d += elm.Capacitor().down().at((x, T)).to((x, G))
        gnd(x, G)
    # battery divider
    xd = 11.0
    d += elm.Dot().at((xd, T))
    d += elm.Resistor().down().at((xd, T)).to((xd, 10.75))
    d += elm.Dot().at((xd, 10.75))
    d += elm.Resistor().down().at((xd, 10.75)).to((xd, G))
    gnd(xd, G)
    d += elm.Line().right().at((xd, 10.75)).to((xd + 1.7, 10.75))
    d += elm.Dot().at((xd + 1.7, 10.75))
    d += elm.Capacitor().down().at((xd + 1.7, 10.75)).to((xd + 1.7, G))
    gnd(xd + 1.7, G)
    d += elm.Line().up().at((xd + 1.7, 10.75)).to((xd + 1.7, 11.9))
    # buck regulator
    xb = 15.6
    d += elm.Dot().at((xb, T))
    d += elm.Line().down().at((xb, T)).to((xb, 11.6))
    gnd(xb, 9.8)
    d += elm.Inductor().right().at((xb + 1.0, 10.7)).to((xb + 3.0, 10.7))
    xn = xb + 3.0
    d += elm.Dot().at((xn, 10.7))
    d += elm.Capacitor().down().at((xn, 10.7)).to((xn, G))
    gnd(xn, G)
    d += elm.Line().right().at((xn, 10.7)).to((xn + 2.0, 10.7))
    d += elm.Dot().at((xn + 1.2, 10.7))
    d += elm.ResistorIEC().up().at((xn + 1.2, 10.7)).to((xn + 1.2, 12.3))

    # --- DRV8833 (drawn as a box) ------------------------------------------------
    X0, X1, Y0, Y1 = 12.8, 17.4, 0.6, 6.6
    d += elm.Line().up().at((14.8, Y1)).to((14.8, 7.4))
    d += elm.Line().right().at((14.8, 7.4)).to((XR, 7.4))
    d += elm.Line().up().at((XR, 7.4)).to((XR, T))
    left = [("AIN1", 6.0, "TIM1_CH1"), ("AIN2", 5.2, "TIM1_CH2"), ("BIN1", 4.4, "TIM1_CH3"),
            ("BIN2", 3.6, "TIM1_CH4")]
    for name, y, lab in left:
        d += elm.Line().left().at((X0, y)).to((11.6, y))
    d += elm.Line().left().at((X0, 2.2)).to((10.4, 2.2))
    d += elm.Dot().at((12.2, 2.2))
    d += elm.Resistor().down().at((12.2, 2.2)).to((12.2, 0.2))
    for y0, y1 in ((6.0, 4.4), (3.2, 1.6)):
        d += elm.Line().right().at((X1, y0)).to((19.0, y0))
        d += elm.Line().right().at((X1, y1)).to((19.0, y1))
        d += elm.Motor().down().at((19.0, y0)).to((19.0, y1))
    for x in (13.8, 16.2):
        d += elm.Resistor().down().at((x, Y0)).to((x, -1.2))
        gnd(x, -1.2)

    # --- sensor channel -------------------------------------------------------------
    xl, xp, top = 1.5, 6.0, 6.3
    d += elm.Vdd().at((xl, top))
    d += elm.Resistor().down().at((xl, top)).to((xl, 4.6))
    d += elm.LED().down().at((xl, 4.6)).to((xl, 2.9))
    d += elm.Dot().at((xl, 2.9))
    d += elm.Line().right().at((xl, 2.9)).to((xl + 1.0, 2.9))
    d += elm.Line().down().at((xl, 2.9)).to((xl, 2.6))
    m = elm.NFet().theta(0).reverse().anchor("drain").at((xl, 2.6))
    d += m
    mg = m.absanchors["gate"]
    ms = m.absanchors["source"]
    gnd(*ms)
    d += elm.Line().left().at(mg).to((mg[0] - 0.7, mg[1]))
    d += elm.Vdd().at((xp, top))
    d += elm.Resistor().down().at((xp, top)).to((xp, 4.6))
    d += elm.Dot().at((xp, 4.6))
    d += elm.Line().right().at((xp, 4.6)).to((xp + 1.0, 4.6))
    d += elm.Line().down().at((xp, 4.6)).to((xp, 4.3))
    ph = elm.NpnPhoto().theta(0).anchor("collector").at((xp, 4.3))
    d += ph
    pe = ph.absanchors["emitter"]
    d += elm.Line().down().at(pe).to((xp, ms[1]))
    gnd(xp, ms[1])
    d.draw()

    # --- labels (matplotlib text for full control) -----------------------------------
    txt(-0.45, 9.75, "2S LiPo\n7.4 V\n300 mAh", ha="right")
    txt(1.0, T - 0.45, "SW1", ha="center", va="top")
    txt(2.75, T + 0.45, "Q1 P-MOSFET\nreverse protection", ha="center", va="bottom", fs=6.8)
    txt(gx + 0.35, 9.55, "10 k")
    txt(xz + 0.35, 11.8, "12 V\nZener")
    txt(12.9, T + 0.3, "VM bus 6.4–8.4 V", ha="center", va="bottom", fs=7.5, weight="bold")
    txt(6.95, 10.75, "47 µF\npolymer", fs=6.5)
    txt(9.15, 10.75, "100 nF", fs=6.5)
    txt(xd + 0.35, 11.55, "20 k")
    txt(xd + 0.35, 9.6, "10 k")
    txt(xd + 2.15, 9.6, "100\nnF", fs=6.8)
    txt(xd + 1.7, 12.05, "ADC_VBAT", ha="center", va="bottom", fs=6.8)
    ax.add_patch(Rectangle((xb - 1.0, 9.8), 2.0, 1.8, fc="white", ec=INK, lw=1.0, zorder=3))
    txt(xb, 10.7, "buck\n3.3 V\n1 A", ha="center", fs=7, zorder=4)
    txt(xb + 2.0, 11.15, "2.2 µH", ha="center", va="bottom")
    txt(xn + 0.35, 9.6, "22 µF")
    txt(xn + 2.05, 10.7, "+3.3 V", fs=7.2)
    txt(xn + 1.55, 11.5, "ferrite\nbead", fs=6.8)
    txt(xn + 1.2, 12.4, "VDDA", ha="center", va="bottom", fs=6.8)
    # DRV8833 box
    ax.add_patch(Rectangle((X0, Y0), X1 - X0, Y1 - Y0, fc="#FFF6EC", ec=INK, lw=1.2, zorder=3))
    txt(15.45, 5.2, "DRV8833", ha="center", fs=8, weight="bold", zorder=4)
    for name, y, lab in left:
        txt(X0 + 0.15, y, name, fs=6.5, zorder=4)
        txt(11.5, y, lab, ha="right", fs=6.8)
    txt(X0 + 0.15, 2.2, "nFAULT", fs=6.5, zorder=4)
    txt(10.3, 2.2, "GPIO", ha="right", fs=6.8)
    txt(11.85, 1.2, "10 k", ha="right", fs=6.8)
    txt(12.2, 0.05, "+3.3 V", ha="center", va="top", fs=6.8)
    for nm, y in (("AOUT1", 6.0), ("AOUT2", 4.4), ("BOUT1", 3.2), ("BOUT2", 1.6)):
        txt(X1 - 0.15, y, nm, ha="right", fs=6.5, zorder=4)
    txt(19.7, 5.2, "M1", fs=7.5)
    txt(19.7, 2.4, "M2", fs=7.5)
    txt(14.8, Y1 - 0.25, "VM", ha="center", va="top", fs=6.5, zorder=4)
    for x, nm in ((13.8, "AISEN"), (16.2, "BISEN")):
        txt(x, Y0 + 0.15, nm, ha="center", va="bottom", fs=6.5, zorder=4)
        txt(x + 0.35, -0.3, "0.15 Ω", fs=6.8)
    # sensor channel labels
    txt(xl + 0.35, 5.45, "100 Ω")
    txt(xl - 0.45, 3.75, "IR LED", ha="right", fs=6.8)
    txt(xl, top + 0.55, "+3.3 V", ha="center", va="bottom", fs=6.8)
    txt(xp, top + 0.55, "+3.3 V", ha="center", va="bottom", fs=6.8)
    txt(xl + 1.05, 2.9, "other 7\ncathodes", fs=6.5)
    txt(mg[0] - 0.75, mg[1], "LED_EN", ha="right", fs=6.8)
    txt(xl + 0.35, 1.85, "AO3400", fs=6.5)
    txt(xp + 0.35, 5.45, "10 k")
    txt(xp + 1.05, 4.6, "ADC_IN", fs=6.8)
    txt(xp + 0.35, 3.0, "photo-\ntransistor", fs=6.5)
    ax.add_patch(Rectangle((-2.9, -0.2), 11.2, 7.6, fill=False, ls="--", lw=0.8, ec=GREY))
    txt(-2.75, 0.0, "sensor channel ×8", va="bottom", fs=7.2, color=GREY)
    ax.set_xlim(-3.3, 23.4)
    ax.set_ylim(-2.2, 14.6)
    save(fig, "34", "fig-34-3-power-drive-sensor-schematic")


# ----------------------------------------------------------------------------
# Figure 34.4 — control cycle timing
# ----------------------------------------------------------------------------
def fig_34_4():
    fig, (a0, a1) = plt.subplots(2, 1, figsize=(6.8, 5.0), gridspec_kw=dict(height_ratios=[1, 3.1],
                                                                             hspace=0.45))
    rows = ["TIM6 tick", "LED_EN", "ADC busy", "CPU in ISR", "PWM update", "sensor out\n(white, V)"]
    ys = {r: len(rows) - 1 - i for i, r in enumerate(rows)}
    H = 0.6
    adc = [(0, 11.3, "LEDs off"), (91.3, 102.6, "LEDs on")]

    def digital(ax, y, segs, color, xmax):
        xs, vs = [0], [0]
        for a, b in segs:
            xs += [a, a, b, b]
            vs += [0, 1, 1, 0]
        xs.append(xmax)
        vs.append(0)
        ax.plot(xs, [y + H * v for v in vs], color=color, lw=1.3, drawstyle="default")
        for a, b in segs:
            ax.add_patch(Rectangle((a, y), b - a, H, color=color, alpha=0.18, lw=0))

    def pulses(ax, y, ts, color):
        for t in ts:
            ax.annotate("", xy=(t, y + H), xytext=(t, y), arrowprops=dict(arrowstyle="-|>", color=color,
                                                                          lw=1.3, mutation_scale=8))
        ax.plot([ts[0] - 1e3, ts[-1] + 1e3], [y, y], color=color, lw=1.0)

    # overview
    for ax, xmax in ((a0, 1000), (a1, 150)):
        pass
    ov = {"TIM6 tick": 3, "LED_EN": 2, "ADC busy": 1, "CPU in ISR": 0}
    pulses(a0, ov["TIM6 tick"], [0, 1000], INK)
    digital(a0, ov["LED_EN"], [(11.3, 102.6)], ORANGE, 1050)
    digital(a0, ov["ADC busy"], [(0, 11.3), (91.3, 102.6)], BLUE, 1050)
    digital(a0, ov["CPU in ISR"], [(102.6, 119)], GREEN, 1050)
    a0.set_xlim(-10, 1050)
    a0.set_ylim(-0.3, 3.9)
    a0.set_yticks([v + H / 2 for v in ov.values()])
    a0.set_yticklabels(list(ov.keys()), fontsize=7.5)
    a0.set_xlabel("time in cycle (µs)", fontsize=8.5, labelpad=1)
    a0.tick_params(labelsize=7.5)
    a0.add_patch(Rectangle((0, -0.25), 150, 4.05, fill=False, ec=GREY, ls="--", lw=0.8))
    a0.text(160, 3.25, "zoom below (0–150 µs)", fontsize=7.5, color=GREY, va="center")
    a0.text(1040, 0.3, "idle / background loop 881 µs\nCPU load in ISR ≈ 1.6 %", fontsize=7.5,
            ha="right", va="bottom", color=INK)
    a0.spines["left"].set_visible(False)
    a0.tick_params(axis="y", length=0)

    # zoom
    ax = a1
    pulses(ax, ys["TIM6 tick"], [0], INK)
    digital(ax, ys["LED_EN"], [(11.3, 102.6)], ORANGE, 150)
    digital(ax, ys["ADC busy"], [(0, 11.3), (91.3, 102.6)], BLUE, 150)
    for a, b, t in adc:
        ax.text((a + b) / 2, ys["ADC busy"] + H + 0.08, t, ha="center", va="bottom", fontsize=7,
                color=BLUE)
    digital(ax, ys["CPU in ISR"], [(102.6, 119)], GREEN, 150)
    ax.text(110.8, ys["CPU in ISR"] + H + 0.08, "position,\ncontrol, PWM", ha="center", va="bottom",
            fontsize=7, color=GREEN)
    pulses(ax, ys["PWM update"], [119], PINK)
    ax.text(121, ys["PWM update"] + 0.3, "new duty at 119 µs", fontsize=7, color=PINK, va="center")
    # analog trace: phototransistor output over white
    t = np.linspace(0, 150, 1501)
    tau = 13.0
    v = np.where(t < 11.3, 3.2, 0.3 + 2.9 * np.exp(-(t - 11.3) / tau))
    off = t >= 102.6
    v_at = 0.3 + 2.9 * np.exp(-(102.6 - 11.3) / tau)
    v[off] = 3.2 - (3.2 - v_at) * np.exp(-(t[off] - 102.6) / tau)
    y0 = ys["sensor out\n(white, V)"]
    ax.plot(t, y0 + v / 3.2 * 0.7, color=RED, lw=1.3)
    ax.text(1, y0 + 0.74, "3.2 V", fontsize=7, color=RED, va="bottom")
    ax.text(73, y0 + 0.3 / 3.2 * 0.7 + 0.04, "0.3 V", fontsize=7, color=RED, va="bottom")
    ax.annotate("", xy=(71.3, y0 + 0.5), xytext=(11.3, y0 + 0.5),
                arrowprops=dict(arrowstyle="<|-|>", color=GREY, lw=0.8, mutation_scale=7))
    ax.text(41.3, y0 + 0.52, "settled < 60 µs", fontsize=7, color=GREY, ha="center", va="bottom")
    # settle annotation
    ya = ys["LED_EN"] + H + 0.25
    ax.annotate("", xy=(91.3, ya), xytext=(11.3, ya),
                arrowprops=dict(arrowstyle="<|-|>", color=ORANGE, lw=0.9, mutation_scale=8))
    ax.text(51.3, ya + 0.04, "settle 80 µs (one-shot timer)", ha="center", va="bottom", fontsize=7.5,
            color=ORANGE)
    for xv in (11.3, 91.3, 102.6, 119):
        ax.axvline(xv, color=GREY, lw=0.5, ls=":", zorder=0)
    ax.set_xlim(-3, 150)
    ax.set_ylim(-0.3, len(rows) - 0.05)
    ax.set_yticks([ys[r] + H / 2 for r in rows])
    ax.set_yticklabels(rows, fontsize=8)
    ax.set_xticks([0, 11.3, 25, 50, 75, 91.3, 102.6, 119, 150])
    ax.set_xticklabels(["0", "11.3", "", "50", "", "91.3", "102.6", "119", "150"], fontsize=7.5)
    ax.set_xlabel("time after TIM6 tick (µs)")
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    save(fig, "34", "fig-34-4-control-cycle-timing")


# ----------------------------------------------------------------------------
# Figure 34.5 — steering damping
# ----------------------------------------------------------------------------
def worst_pole(v, L, kp, kd, tw, T, tf=0.002):
    """Least-damped closed-loop pole (damping, Hz) of the steering loop at speed v (m/s)."""
    P = np.poly1d
    plant_n, plant_d = P([L, v]), P([1, 0, 0])
    lag, dly_n, dly_d = P([tw, 1]), P([-T / 2, 1]), P([T / 2, 1])
    c_n, c_d = P([kp * tf + kd, kp]), P([tf, 1])
    r = (plant_d * lag * dly_d * c_d + plant_n * dly_n * c_n).r
    z = -r.real / np.abs(r)
    i = np.argmin(z)
    return z[i], abs(r[i].imag) / (2 * np.pi)


def fig_34_5():
    designs = [
        ("P1 prototype (30 mm, 60 ms, 12.5 ms; $K_p$ 250, $K_d$ 5)", ORANGE, "-",
         (0.030, 0.060, 0.0125), lambda v: (250, 5)),
        ("Rev A fixed (80 mm, 25 ms, 2 ms; $K_p$ 300, $K_d$ 8)", BLUE, "--",
         (0.080, 0.025, 0.002), lambda v: (300, 8)),
        ("Rev A scheduled ($K_d = 8\\,\\max(v,1)$)", GREEN, "-",
         (0.080, 0.025, 0.002), lambda v: (300, 8 * max(v, 1.0))),
    ]
    fig, ax = new_fig(6.4, 4.0)
    vv = np.linspace(0.2, 2.2, 401)
    ax.axhspan(-0.3, 0, color=RED, alpha=0.10, lw=0)
    ax.text(2.15, -0.25, "unstable", color=RED, ha="right", va="bottom", fontsize=9)
    ax.axhline(0.7, color=GREY, ls="--", lw=1.0)
    ax.text(0.22, 0.72, "target 0.7", color=GREY, fontsize=8.5, va="bottom")
    ax.axhline(0, color=INK, lw=0.6)
    for name, c, ls, (L, tw, T), g in designs:
        z = [worst_pole(v, L, *g(v), tw, T)[0] for v in vv]
        ax.plot(vv, z, color=c, ls=ls, label=name)
        pts = np.array([0.3, 0.6, 1.0, 1.5, 2.0])
        ax.plot(pts, [worst_pole(v, L, *g(v), tw, T)[0] for v in pts], "o", color=c, ms=4)
    ax.set_xlim(0.2, 2.2)
    ax.set_ylim(-0.3, 1.05)
    ax.set_xlabel("speed $v$ (m/s)")
    ax.set_ylabel("damping ratio of least-damped pole")
    ax.legend(loc="lower right", bbox_to_anchor=(1.0, 0.25), fontsize=7.6)
    ax.grid(True, lw=0.5)
    ax.annotate("weave at 0.6 m/s, 1.9 Hz", xy=(0.6, 0.0), xytext=(0.66, 0.42), fontsize=8,
                color=ORANGE, arrowprops=dict(arrowstyle="-|>", color=ORANGE, lw=0.8,
                                              mutation_scale=8))
    save(fig, "34", "fig-34-5-steering-damping")


# ----------------------------------------------------------------------------
# Figure 34.6 — lap speed profile
# ----------------------------------------------------------------------------
TRACK = [(2.0, 0), (np.pi * 0.25, 0.25), (1.5, 0), (np.pi / 2 * 0.10, 0.10), (1.0, 0),
         (np.pi / 2 * 0.30, 0.30), (np.pi / 2 * 0.30, 0.30), (2.5, 0), (np.pi * 0.50, 0.50),
         (1.2, 0), (np.pi / 2 * 0.15, 0.15), (np.pi / 2 * 0.15, 0.15), (0.0, 0)]
TRACK[-1] = (15.0 - sum(s for s, _ in TRACK), 0)
V_TOP, A_LAT, A_ACC, A_DEC, DS = 2.0, 6.0, 5.0, 6.0, 0.005


def _profile(vlim, laps=2):
    v = np.tile(vlim, laps)
    for i in range(1, v.size):
        v[i] = min(v[i], np.sqrt(v[i - 1] ** 2 + 2 * A_ACC * DS))
    for i in range(v.size - 2, -1, -1):
        v[i] = min(v[i], np.sqrt(v[i + 1] ** 2 + 2 * A_DEC * DS))
    return v[vlim.size:]


def _reactive(vlim, laps=2):
    v = np.tile(vlim, laps)
    for i in range(1, v.size):
        up = np.sqrt(v[i - 1] ** 2 + 2 * A_ACC * DS)
        dn = np.sqrt(max(v[i - 1] ** 2 - 2 * A_DEC * DS, 0))
        v[i] = min(v[i], up) if v[i] >= dn else dn
    return v[vlim.size:]


def fig_34_6():
    r = np.concatenate([np.full(int(round(s / DS)), rad) for s, rad in TRACK])
    s = (np.arange(r.size) + 0.5) * DS
    kap = np.where(r > 0, 1 / np.where(r > 0, r, 1), 0.0)
    vlim = np.where(r > 0, np.sqrt(A_LAT * np.where(r > 0, r, 1)), V_TOP).clip(max=V_TOP)
    lap = lambda v: np.sum(DS / v)  # noqa: E731
    v_c = np.full_like(vlim, vlim.min())
    v_r = _reactive(vlim)
    v_m = _profile(vlim)
    alat_r = v_r ** 2 * kap
    # representative telemetry: 5-10 % below the profile, scaled to the 9.42 s lap
    rng = np.random.default_rng(34)
    sm = np.arange(0.1, 15.0, 0.2)
    vm_s = np.interp(sm, s, v_m)
    fac = 0.925 + 0.02 * np.sin(2 * np.pi * sm / 3.1) + rng.normal(0, 0.006, sm.size)
    v_meas = vm_s * fac
    v_meas *= np.sum(0.2 / v_meas) / 9.42
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.8, 5.0), sharex=True,
                                 gridspec_kw=dict(height_ratios=[2.3, 1], hspace=0.08))
    a1.plot(s, v_c, color=GREY, lw=1.4, label=f"constant {vlim.min():.2f} m/s: {lap(v_c):.1f} s")
    a1.plot(s, v_r, color=ORANGE, lw=1.2, ls="--",
            label=f"reactive: {lap(v_r):.2f} s, peak $a_{{lat}}$ {alat_r.max():.0f} m/s² — infeasible")
    bad = alat_r > A_LAT * 1.02
    a1.fill_between(s, 0, 2.2, where=bad, color=RED, alpha=0.10, lw=0)
    a1.plot(s, v_m, color=BLUE, lw=1.8, label=f"mapped profile: {lap(v_m):.2f} s (peak {v_m.max():.1f} m/s)")
    a1.plot(sm, v_meas, "o", ms=2.6, color=INK, label="measured Rev A (telemetry): 9.42 s")
    # curve speed labels
    for rad in (0.25, 0.10, 0.30, 0.50, 0.15):
        n = 2 if rad in (0.30, 0.15) else 1
        L = [seg for seg, rr in TRACK if rr == rad][0]
        xc = _first(rad) + n * L / 2
        vc = np.sqrt(A_LAT * rad)
        below = rad == 0.10
        a1.text(xc, vc - 0.07 if below else vc + 0.04, f"{vc:.2f}", ha="center",
                va="top" if below else "bottom", fontsize=7.5, color=BLUE, weight="bold")
    a1.text(14.9, 2.12, "shaded: reactive exceeds 6 m/s² lateral", ha="right", va="center",
            fontsize=7.5, color=RED)
    a1.set_ylim(0, 2.2)
    a1.set_ylabel("speed (m/s)")
    a1.legend(loc="lower left", bbox_to_anchor=(0.0, -0.02), fontsize=7.3, ncol=2, columnspacing=1.0)
    a1.grid(True, lw=0.5)
    a2.fill_between(s, 0, kap, color=GREEN, alpha=0.3, lw=0, step="mid")
    a2.plot(s, kap, color=GREEN, lw=1.2)
    start = 0.0
    labels = {0.25: "180°\nR 0.25", 0.10: "90° R 0.10", 0.30: "S: 2×90°\nR 0.30",
              0.50: "180°\nR 0.50", 0.15: "2×90°\nR 0.15"}
    done = set()
    for L, rad in TRACK:
        if rad > 0 and rad not in done:
            done.add(rad)
            n = 2 if rad in (0.30, 0.15) else 1
            xc = start + n * L / 2
            ytxt = 1 / rad + 0.4 if rad != 0.10 else 9.0
            xt = xc + (0.95 if rad == 0.10 else 0)
            a2.text(xt, ytxt, labels[rad], ha="center" if rad != 0.10 else "left", va="bottom"
                    if rad != 0.10 else "center", fontsize=7)
        start += L
    a2.set_ylim(0, 12.5)
    a2.set_ylabel("|curvature| (1/m)")
    a2.set_xlabel("distance along track (m)")
    a2.set_xlim(0, 15)
    a2.grid(True, lw=0.5)
    save(fig, "34", "fig-34-6-lap-speed-profile")


def _first(rad):
    start = 0.0
    for L, r in TRACK:
        if r == rad:
            return start
        start += L
    return None


if __name__ == "__main__":
    fig_34_1()
    fig_34_2()
    fig_34_3()
    fig_34_4()
    fig_34_5()
    fig_34_6()
