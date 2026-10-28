"""Figures for Chapter 37 — Project: Closed-Loop Motor Drive.

Run from the repository root:  python figures/scripts/ch37.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle, FancyBboxPatch  # noqa: E402
from scipy.optimize import brentq  # noqa: E402
import schemdraw  # noqa: E402
import schemdraw.elements as elm  # noqa: E402

from figstyle import COLORS, INK, GRID, box, save, schematic, new_fig  # noqa: E402

schemdraw.use("matplotlib")

BLUE, ORANGE, GREEN, PINK, YELLOW, SKY = COLORS[:6]
RED = "#C62828"
GREY = "#777777"

# Motor and load (Table 37.2)
RS_HOT, RS, LS, PSI, P, KT, J = 0.11, 0.085, 0.25e-3, 0.0160, 4, 0.096, 1.49e-4
TC, BV = 0.020, 18e-6  # Coulomb friction N*m, viscous N*m*s
I_PK = 39.8


def line(ax, pts, color=INK, lw=1.1, ls="-", arrow_end=True):
    """Poly-line through pts with an arrow head on the last segment."""
    xs, ys = zip(*pts)
    if len(pts) > 2:
        ax.plot(xs[:-1], ys[:-1], color=color, lw=lw, ls=ls, solid_capstyle="butt")
    if arrow_end:
        ax.annotate("", xy=pts[-1], xytext=pts[-2],
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, ls=ls,
                                    shrinkA=0, shrinkB=0, mutation_scale=9))
    else:
        ax.plot(xs[-2:], ys[-2:], color=color, lw=lw, ls=ls)


# ----------------------------------------------------------------------------
def fig_37_1():
    """Drive architecture with cascaded loops."""
    fig, ax = schematic(6.8, 5.2, xlim=(0, 17.4), ylim=(-1.3, 12.3))
    fs = 7.0
    pw = "#FBEFE6"   # power path tint
    ct = "#EEF3F8"   # control tint
    mc = "#E9F5EF"   # measurement tint

    # --- top row: power path
    y0, h = 9.8, 2.0
    w, gap = 2.65, 0.26
    xs = [0.1 + i * (w + gap) for i in range(6)]
    labels = ["48 V supply\n600 W\n(cannot sink\ncurrent)",
              "DC link\n990 µF +\nbrake chopper\n2.7 Ω, 50 W",
              "MOSFET bridge\n6 × 100 V\n2.5 mΩ\n3 shunts 1 mΩ",
              "PMSM\n400 W, 48 V\n4 pole pairs",
              "10:1 belt\nand gear",
              "Index table\n24 nests,\n15° per index"]
    for x, t in zip(xs, labels):
        box(ax, x, y0, w, h, t, fc=pw, fontsize=fs)
    for a, b in zip(xs[:-1], xs[1:]):
        line(ax, [(a + w, y0 + h / 2), (b, y0 + h / 2)], lw=1.6, color=ORANGE)
    ax.text(0.1, 12.1, "Power path", fontsize=fs + 0.6, color=ORANGE, weight="bold", va="center")

    # gate driver under bridge, encoder under motor, receivers beside it
    mh = 1.45
    my = 7.85
    gx = xs[2]
    box(ax, gx, my, w, mh, "Gate driver,\n3 CSAs 20 V/V,\n$V_{DS}$ monitor", fc=pw, fontsize=fs)
    line(ax, [(gx + w / 2, my + mh), (gx + w / 2, y0)], color=ORANGE)
    ax.text(gx + w / 2 + 0.12, (my + mh + y0) / 2, "gates", fontsize=6.6, va="center")
    ex = xs[3]
    box(ax, ex, my, w, mh, "Encoder\n2500 lines\nA, B, Z diff.", fc=mc, fontsize=fs)
    ax.plot([ex + w / 2] * 2, [y0, my + mh], color=GREEN, lw=1.1)
    ax.text(ex + w / 2 + 0.12, (my + mh + y0) / 2, "shaft", fontsize=6.6, va="center")
    rx = xs[4]
    box(ax, rx, my, w, mh, "RS-422\nreceivers,\n120 Ω", fc=mc, fontsize=fs)
    line(ax, [(ex + w, my + mh / 2), (rx, my + mh / 2)], color=GREEN)

    # --- MCU box
    mx0, my0, mx1, my1 = 0.1, 0.55, 17.3, 7.35
    ax.add_patch(FancyBboxPatch((mx0, my0), mx1 - mx0, my1 - my0,
                                boxstyle="round,pad=0.02,rounding_size=0.2", fc="#FAFAFA", ec=INK, lw=1.2))
    ax.text(mx0 + 0.2, my1 - 0.32, "MCU (STM32G474 class)", fontsize=fs + 0.4, weight="bold",
            va="center")

    # forward chain row
    fy, fh, fw, fg = 4.55, 1.45, 1.95, 0.42
    fx = [0.35 + i * (fw + fg) for i in range(7)]
    ftxt = ["Speed ref.\nfrom CAN", "Speed PI\n4 kHz", "Notch\n240 Hz",
            "d, q current\nPIs 20 kHz\n($i_d^*$ = 0)", "Inverse\nPark", "SVPWM", "PWM timer\ncentre-\naligned"]
    for x, t in zip(fx, ftxt):
        box(ax, x, fy, fw, fh, t, fc=ct, fontsize=fs)
    for a, b in zip(fx[:-1], fx[1:]):
        line(ax, [(a + fw, fy + fh / 2), (b, fy + fh / 2)], color=BLUE)
    ax.text(fx[3] - fg / 2, fy - 0.08, "$i_q^*$", fontsize=7, ha="center", va="top", color=BLUE)
    # PWM timer -> gate driver
    xp = fx[6] + fw / 2
    line(ax, [(xp, fy + fh), (xp, 6.75), (gx + w - 0.35, 6.75), (gx + w - 0.35, my)], color=BLUE)
    ax.text(xp - 0.15, 6.83, "6 PWM", fontsize=6.6, ha="right", va="bottom", color=BLUE)

    # feedback row
    by, bh = 2.65, 1.25
    box(ax, fx[3], by, fw, bh, "Park", fc=mc, fontsize=fs)
    box(ax, fx[4], by, fw, bh, "Clarke", fc=mc, fontsize=fs)
    box(ax, fx[5], by, fw, bh, "ADC ×2\nat counter\nzero", fc=mc, fontsize=fs)
    line(ax, [(fx[5], by + bh / 2), (fx[4] + fw, by + bh / 2)], color=GREEN)
    line(ax, [(fx[4], by + bh / 2), (fx[3] + fw, by + bh / 2)], color=GREEN)
    line(ax, [(fx[3] + fw / 2, by + bh), (fx[3] + fw / 2, fy)], color=GREEN)
    ax.text(fx[3] + fw / 2 + 0.12, (by + bh + fy) / 2, "$i_d, i_q$", fontsize=6.8, va="center", color=GREEN)
    # current-sense amps -> ADC (right side of ADC)
    xs_ = gx + 1.0
    line(ax, [(xs_, my), (xs_, 6.35), (fx[5] + fw + fg / 2, 6.35), (fx[5] + fw + fg / 2, by + bh / 2 + 0.25),
              (fx[5] + fw, by + bh / 2 + 0.25)], color=GREEN)
    ax.text(xs_ - 0.12, 6.28, "phase currents", fontsize=6.4, ha="right", va="top", color=GREEN)

    cy, chh = 0.85, 1.3
    box(ax, fx[1], cy, fw, chh, "M/T speed\nestimator", fc=mc, fontsize=fs)
    qx, qw = fx[5], fx[6] + fw - fx[5]
    box(ax, qx, cy, qw, chh, "Quadrature timer\n+ edge-timestamp\ntimer (170 MHz)", fc=mc, fontsize=fs)
    # receivers -> timers
    xr = 16.85
    line(ax, [(rx + w / 2, my), (rx + w / 2, 7.05), (xr, 7.05), (xr, cy + chh / 2), (qx + qw, cy + chh / 2)],
         color=GREEN)
    ax.text(xr - 0.12, 3.3, "A, B, Z", fontsize=6.6, ha="right", va="center", color=GREEN, rotation=90)
    line(ax, [(qx, cy + chh / 2), (fx[1] + fw, cy + chh / 2)], color=GREEN)
    ax.text((fx[1] + fw + qx) / 2, cy + chh / 2 + 0.08, "count and edge times", fontsize=6.6, ha="center",
            va="bottom", color=GREEN)
    line(ax, [(fx[1] + fw / 2, cy + chh), (fx[1] + fw / 2, fy)], color=GREEN)
    ax.text(fx[1] + fw / 2 + 0.12, 3.3, "ω", fontsize=7.5, va="center", color=GREEN)
    # electrical angle to Park and inverse Park (dashed)
    xa = fx[4] - fg / 2
    ax.plot([qx + 0.35, qx + 0.35, xa, xa], [cy + chh, 2.35, 2.35, 4.3], color=GREEN, lw=1.0, ls="--")
    line(ax, [(xa, 4.3), (fx[4] + 0.5, 4.3), (fx[4] + 0.5, fy)], color=GREEN, ls="--")
    line(ax, [(xa, by + 0.3), (fx[3] + fw, by + 0.3)], color=GREEN, ls="--")
    ax.text(qx - 0.5, 2.25, "θe", fontsize=7.5, color=GREEN, va="top")

    # --- protection bar
    ax.add_patch(Rectangle((0.1, -1.25), 17.2, 1.55, fc="#FDECEC", ec=RED, lw=1.0))
    ax.text(0.3, 0.0, "Protection, in hardware:", fontsize=fs, color=RED, weight="bold", va="center")
    items = ["60 A comparator → PWM\nbreak input (< 1 µs)",
             "bus comparator → chopper\non 58 V, off 56 V",
             "STO, 2 channels → gate-\ndriver supply and enable"]
    for k, t in enumerate(items):
        ax.text(0.3 + k * 5.75, -0.75, t, fontsize=fs, color=RED, va="center")
    save(fig, "37", "fig-37-1-drive-architecture")


# ----------------------------------------------------------------------------
def _speed_limit(vbus, iq):
    """Highest speed (rpm) at which current iq fits the voltage limit, id = 0, hot winding."""
    vm = 0.95 * vbus / np.sqrt(3)

    def f(rpm):
        we = P * rpm * 2 * np.pi / 60
        return np.hypot(RS_HOT * iq + we * PSI, we * LS * iq) - vm
    return brentq(f, 1.0, 8000.0)


def fig_37_2():
    """Torque-speed envelope at three bus voltages with duty points."""
    fig, ax = new_fig(6.4, 4.0)
    ax.add_patch(Rectangle((0, 0), 3000, 1.273, fc=GREEN, alpha=0.13, ec="none"))
    ax.text(150, 0.62, "continuous operation\n(≤ 1.27 N·m, ≤ 3000 rpm)", fontsize=8, color=GREEN, va="center")
    for vbus, c, dy in ((48, BLUE, 0.0), (46, PINK, 0.0), (44, ORANGE, 0.0)):
        iq = np.linspace(I_PK, 1e-4, 300)
        n = np.array([_speed_limit(vbus, i) for i in iq])
        nn = np.concatenate(([0.0], n))
        tt = np.concatenate(([KT * I_PK], KT * iq))
        ax.plot(nn, tt, color=c, lw=1.8, label=f"voltage limit, {vbus} V bus")
        yl = {48: 3.0, 46: 2.35, 44: 1.7}[vbus]
        xl = np.interp(yl, tt[::-1], nn[::-1])
        ax.plot(n[0], KT * I_PK, "o", ms=3.5, color=c)
    ax.annotate("corners 2570 / 2710 / 2850 rpm", xy=(2710, 3.82), xytext=(1150, 4.25), fontsize=8,
                arrowprops=dict(arrowstyle="-", color=GREY, lw=0.8))
    ax.axhline(3.82, xmax=0, color=INK)
    ax.text(60, 3.9, "current limit 3.82 N·m (39.8 A)", fontsize=8, va="bottom")
    ax.axhline(1.273, color=INK, ls="--", lw=1.0)
    ax.text(1900, 1.31, "1.27 N·m continuous rating", fontsize=8, va="bottom")
    # index duty cycle: triangular profile 0 -> 1670 rpm -> 0
    nacc = np.linspace(0, 1670, 7)
    ax.plot(nacc, np.full_like(nacc, 1.75), "o-", color=RED, ms=4, lw=1.2, label="index move, acceleration")
    ax.plot(nacc, np.full_like(nacc, 1.71), "o", mfc="white", mec=RED, ms=4.5, lw=0,
            label="index move, deceleration (braking)")
    ax.axhline(0.96, xmax=1670 / 4000, color=RED, lw=1.0, ls=":")
    ax.plot([1670], [0.96], "s", color=RED, ms=5, label="RMS torque of index cycle, 0.96 N·m")
    ax.text(1250, 2.0, "1.75 N·m to 1670 rpm", fontsize=8, color=RED, ha="center")
    ax.set_xlim(0, 4000)
    ax.set_ylim(0, 4.5)
    ax.set_xlabel("Motor speed (rpm)")
    ax.set_ylabel("Torque (N·m)")
    ax.text(2330, 2.45, "voltage limit:\n95 % modulation,\n$i_d=0$, hot winding\n(0.11 Ω)", fontsize=7.8,
            ha="center", color=GREY)
    ax.legend(loc="upper left", fontsize=7.6, bbox_to_anchor=(0.0, 0.83))
    save(fig, "37", "fig-37-2-torque-speed-envelope")


# ----------------------------------------------------------------------------
def fig_37_3():
    """One inverter leg with shunt amplifier, gate driver, DC link and brake chopper."""
    fig, ax = plt.subplots(figsize=(6.8, 4.6))
    ax.set_aspect("equal")
    ax.axis("off")
    d = schemdraw.Drawing(canvas=ax, show=False)
    d.config(fontsize=7.4, lw=1.1)
    TOP, BOT = 13.6, 0.0
    fs = 7.2

    def wire(*pts, color=INK):
        for a, b in zip(pts[:-1], pts[1:]):
            d.add(elm.Line(color=color).at(a).to(b))

    def dot(p):
        d.add(elm.Dot(radius=0.09).at(p))

    def txt(x, y, s, **kw):
        kw.setdefault("fontsize", fs)
        kw.setdefault("va", "center")
        ax.text(x, y, s, color=kw.pop("color", INK), **kw)

    # rails
    wire((0.3, TOP), (26.2, TOP))
    wire((0.3, BOT), (26.2, BOT))
    txt(0.3, TOP + 0.45, "DC link +: 48 V nominal", va="bottom")
    txt(0.3, BOT - 0.4, "power ground", va="top")

    # bus divider
    XD = 0.9
    dot((XD, TOP))
    d.add(elm.Resistor().at((XD, TOP)).to((XD, 9.6)))
    wire((XD, 9.6), (XD, 7.4))
    d.add(elm.Resistor().at((XD, 7.4)).to((XD, 3.8)))
    wire((XD, 3.8), (XD, BOT))
    dot((XD, BOT))
    dot((XD, 8.5))
    wire((XD, 8.5), (1.9, 8.5))
    txt(XD + 0.4, 11.6, "100 kΩ")
    txt(XD + 0.4, 5.6, "6.2 kΩ")
    txt(2.0, 8.5, "→ ADC\n$V_{bus}$", ha="left")

    # DC-link capacitors
    for x, lab, pol in ((3.2, "3 × 330 µF\n80 V hybrid\npolymer", True), (6.9, "4 × 4.7 µF\n100 V X7R\nat the leg", False)):
        dot((x, TOP))
        wire((x, TOP), (x, 11.6))
        d.add(elm.Capacitor(polar=pol).at((x, 11.6)).to((x, 9.6)))
        wire((x, 9.6), (x, BOT))
        dot((x, BOT))
        txt(x + 0.35, 10.6, lab, ha="left", fontsize=6.7)

    # half bridge (gate on the right)
    XL = 10.6
    dot((XL, TOP))
    wire((XL, TOP), (XL, 10.0))
    qh = d.add(elm.NFet().theta(0).at((XL, 10.0)).anchor("drain"))
    wire(qh.source, (XL, 7.0))
    dot((XL, 7.0))
    wire((XL, 7.0), (XL, 6.0))
    ql = d.add(elm.NFet().theta(0).at((XL, 6.0)).anchor("drain"))
    wire(ql.source, (XL, 4.2))
    dot((XL, 4.2))
    d.add(elm.Resistor().at((XL, 4.2)).to((XL, 1.2)))
    dot((XL, 1.2))
    wire((XL, 1.2), (XL, BOT))
    dot((XL, BOT))
    txt(XL - 0.35, 8.75, "Q$_H$"+"\n"+"100 V"+"\n"+"2.5 mΩ", ha="right", fontsize=6.7)
    txt(XL - 0.35, 5.25, "Q$_L$", ha="right")
    txt(XL - 0.35, 2.7, "1 mΩ\n2512\nshunt", ha="right")
    # switch node to motor (left)
    wire((XL, 7.0), (8.6, 7.0))
    txt(8.5, 7.0, "to motor\nphase A", ha="right", fontsize=6.7)

    # gate driver box
    GX0, GX1, GY0, GY1 = 14.4, 18.4, 0.9, 11.6
    ax.add_patch(Rectangle((GX0, GY0), GX1 - GX0, GY1 - GY0, fc="#F4F4F4", ec=INK, lw=1.2, zorder=1))
    txt(16.95, 7.7, "Gate\ndriver\n(DRV8353\nclass)", ha="center", fontsize=6.9)
    txt(16.95, 4.7, "$V_{DS}$\nmonitor\n0.6 V", ha="center", fontsize=6.9)
    pins_l = {"BST": 11.0, "GH": qh.gate[1], "SH": 7.0, "GL": ql.gate[1], "SP": 3.2, "SN": 1.5}
    for nm, y in pins_l.items():
        txt(GX0 + 0.12, y, nm, ha="left", fontsize=6.4)
    pins_r = {"nFAULT": 10.8, "ENABLE": 9.8, "SO": 3.2}
    for nm, y in pins_r.items():
        txt(GX1 - 0.12, y, nm, ha="right", fontsize=6.4)
    # VDRAIN sense to bus
    wire((17.6, GY1), (17.6, TOP))
    dot((17.6, TOP))
    txt(17.75, 12.5, "$V_{DRAIN}$", ha="left", fontsize=6.4)

    # gate resistors
    for gy in (qh.gate[1], ql.gate[1]):
        wire(qh.gate if gy == qh.gate[1] else ql.gate, (12.3, gy))
        d.add(elm.Resistor(scale=0.6).at((12.3, gy)).to((13.9, gy)))
        wire((13.9, gy), (GX0, gy))
        txt(13.1, gy - 0.4, "4.7 Ω on\n2.2 Ω off", ha="center", va="top", fontsize=6.2)
    # SH to switch node
    wire((GX0, 7.0), (XL, 7.0))
    # bootstrap: 12 V -> diode -> BST; 1 uF from BST to switch node
    XB = 13.95
    wire((GX0, 11.0), (XB, 11.0))
    dot((XB, 11.0))
    d.add(elm.Diode(scale=0.7).at((XB, 12.6)).to((XB, 11.0)))
    txt(XB, 12.75, "12 V", ha="center", va="bottom", fontsize=6.6)
    d.add(elm.Capacitor(scale=0.6).at((XB, 11.0)).to((XB, 10.15)))
    wire((XB, 10.15), (XB, 7.0))
    dot((XB, 7.0))
    txt(XB - 0.25, 10.55, "1 µF", ha="right", fontsize=6.4)
    # Kelvin lines from shunt
    wire((XL, 4.2), (11.9, 4.2), (11.9, 3.2), (GX0, 3.2), color=GREEN)
    wire((XL, 1.2), (11.9, 1.2), (11.9, 1.5), (GX0, 1.5), color=GREEN)
    dot((XL, 4.2))
    txt(12.1, 2.35, "Kelvin lines", ha="left", fontsize=6.4, color=GREEN)

    # right side: SO -> RC -> ADC, nFAULT, ENABLE
    wire((GX1, 3.2), (18.8, 3.2))
    d.add(elm.Resistor(scale=0.6).at((18.8, 3.2)).to((20.4, 3.2)))
    dot((20.4, 3.2))
    d.add(elm.Capacitor(scale=0.5).at((20.4, 3.2)).to((20.4, 2.0)))
    d.add(elm.Ground(lead=False).at((20.4, 2.0)))
    wire((20.4, 3.2), (21.2, 3.2))
    txt(19.6, 3.65, "100 Ω", ha="center", va="bottom", fontsize=6.4)
    txt(20.6, 2.4, "1 nF", ha="left", fontsize=6.4)
    txt(21.3, 3.2, "→ ADC", ha="left", fontsize=6.6)
    txt(18.6, 4.6, "CSA: 20 V/V,\nref 1.65 V", ha="left", fontsize=6.4)
    wire((GX1, 10.4), (19.4, 10.4))
    txt(19.5, 10.4, "→ MCU", ha="left", fontsize=6.6)
    wire((GX1, 9.2), (19.4, 9.2))
    txt(19.5, 9.2, "← STO", ha="left", fontsize=6.6)

    # brake chopper: resistor bus -> drain, freewheel diode across resistor, MOSFET to ground
    XC = 23.6
    dot((XC, TOP))
    d.add(elm.Resistor().at((XC, TOP)).to((XC, 10.6)))
    wire((XC, 10.6), (XC, 9.4))
    dot((XC, 9.4))
    wire((XC, TOP), (25.4, TOP))
    dot((25.4, TOP))
    wire((25.4, 9.4), (25.4, 10.4))
    d.add(elm.Diode().at((25.4, 10.4)).to((25.4, 12.6)))
    wire((25.4, 12.6), (25.4, TOP))
    wire((XC, 9.4), (25.4, 9.4))
    qb = d.add(elm.NFet().theta(0).reverse().at((XC, 9.4)).anchor("drain"))
    wire(qb.source, (XC, BOT))
    dot((XC, BOT))
    wire(qb.gate, (21.9, qb.gate[1]))
    txt(21.8, qb.gate[1], "comparator", ha="right", fontsize=6.4)
    txt(XC - 0.35, 12.1, "2.7 Ω\n50 W", ha="right")
    txt(25.7, 11.5, "free-\nwheel", ha="left", fontsize=6.4)
    txt(XC + 0.35, 8.0, "Q$_{BR}$\n100 V", ha="left")
    txt(23.9, 4.6, "Brake chopper\non at 58 V,\noff at 56 V;\nfirmware trip\n(bridge off)\nat 62 V", ha="left",
        fontsize=6.8, color=RED)
    d.draw()
    ax.set_xlim(-0.2, 27.4)
    ax.set_ylim(-1.0, 14.6)
    save(fig, "37", "fig-37-3-power-stage")


# ----------------------------------------------------------------------------
def fig_37_4():
    """Centre-aligned PWM, ADC sampling and control-loop timing over two periods."""
    T = 50.0
    t = np.linspace(0, 2 * T, 4001)
    cnt = 4250 * (1 - np.abs(((t / T) % 1) * 2 - 1))   # 0 at t=0, peak at T/2
    fig, axs = plt.subplots(5, 1, figsize=(6.6, 4.8), sharex=True,
                            gridspec_kw=dict(height_ratios=[1.6, 0.55, 0.55, 0.55, 1.5], hspace=0.12))
    a0 = axs[0]
    a0.plot(t, cnt, color=INK, lw=1.3)
    for dd, c in ((0.70, BLUE), (0.50, PINK), (0.30, ORANGE)):
        a0.axhline(4250 * (1 - dd), color=c, lw=0.7, ls=":")
    a0.set_ylim(0, 6300)
    a0.set_yticks([0, 4250])
    a0.set_ylabel("counter", fontsize=8.5)
    for te in (0, T, 2 * T):
        a0.axvline(te, color=GREY, lw=0.6, ls="--")
    for ax in axs[1:4]:
        for te in (0, T, 2 * T):
            ax.axvline(te, color=GREY, lw=0.6, ls="--")
    a0.annotate("", xy=(T, 5000), xytext=(0, 5000), arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.8, mutation_scale=7))
    a0.text(T / 2, 5100, "$T_s$ = 50 µs (20 kHz)", fontsize=7.4, ha="center", va="bottom")
    a0.text(26.0, 4250, "peak 4250", fontsize=7.2, ha="left", va="center")
    a0.text(T + 0.8, 5650, "update event at counter = 0:"+"\n"+"preloaded compares become active", fontsize=7.0, ha="left", va="center")
    for k, (dd, c, nm) in enumerate(((0.70, BLUE, "A"), (0.50, PINK, "B"), (0.30, ORANGE, "C"))):
        ax = axs[k + 1]
        g = (cnt >= 4250 * (1 - dd)).astype(float)
        ax.fill_between(t, 0, g, step=None, color=c, alpha=0.35, lw=0)
        ax.plot(t, g, color=c, lw=1.2)
        ax.set_ylim(-0.15, 1.25)
        ax.set_yticks([])
        ax.set_ylabel(f"G$_{{H}}$ {nm}", rotation=0, ha="right", va="center", fontsize=8.5)
        ax.text(T / 2, 0.5, f"{int(dd * 100)} %", ha="center", va="center", fontsize=7.6)
        ax.spines["left"].set_visible(False)
    for ax in axs[1:4]:
        for x0, x1 in ((0, 7.5), (42.5, 57.5), (92.5, 100)):
            ax.axvspan(x0, x1, color=GREY, alpha=0.12, lw=0)
    axs[1].text(T, 1.12, "all low sides on (000)", fontsize=6.6, color=GREY, ha="center", va="bottom")
    a4 = axs[4]
    a4.set_ylim(0, 4.2)
    a4.set_yticks([])
    a4.spines["left"].set_visible(False)
    a4.set_ylabel("CPU", rotation=0, ha="right", va="center", fontsize=8.5)
    for t0 in (0, T):
        a4.broken_barh([(t0, 1.2)], (3.0, 0.8), color=GREEN)
        a4.broken_barh([(t0 + 1.2, 5.8)], (3.0, 0.8), color=BLUE)
    a4.broken_barh([(7.0, 2.1)], (1.8, 0.8), color=PINK)
    a4.text(1.0, 3.95, "ADC 1.2 µs", fontsize=7, color=GREEN, va="bottom")
    a4.text(8.0, 3.4, "FOC ISR 5.8 µs (Clarke, Park, PIs,\ninv. Park, SVPWM)", fontsize=7, color=BLUE,
            va="center")
    a4.text(9.7, 2.2, "speed loop 2.1 µs (every 5th period)", fontsize=7, color=PINK, va="center")
    # write to preload, effective at next update
    a4.annotate("", xy=(T, 1.1), xytext=(7.0, 1.1),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.9, mutation_scale=8))
    a4.text(28, 1.2, "new duties in preload, active at next update", fontsize=7, ha="center", va="bottom")
    # total delay
    a4.annotate("", xy=(75, 0.35), xytext=(0, 0.35),
                arrowprops=dict(arrowstyle="<|-|>", color=RED, lw=1.0, mutation_scale=8))
    a4.text(37, 0.45, "sample → mean of applied voltage: 1.5 $T_s$ = 75 µs", fontsize=7.2, color=RED,
            ha="center", va="bottom")
    a4.axvline(75, ymax=0.3, color=RED, lw=0.8, ls=":")
    # ADC trigger markers
    for te in (0, T):
        a0.annotate("", xy=(te, 0), xytext=(te, 1500),
                    arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=1.2, mutation_scale=9))
    a4.text(58.5, 3.4, "← ADC trigger at counter zero (000):"+"\n"+"   0.25 µs sample, ≥ 1.5 µs after"+"\n"+"   low-side turn-on", fontsize=6.9, color=GREEN, va="center")
    a4.set_xlim(-2, 102)
    a4.set_xticks(np.arange(0, 101, 10))
    a4.set_xlabel("Time (µs)")
    save(fig, "37", "fig-37-4-pwm-adc-timing")


# ----------------------------------------------------------------------------
F = np.logspace(0, 4.5, 20000)
S = 2j * np.pi * F


def _loops():
    R, L, Kt, Jm = 0.085, 0.25e-3, 0.096, 1.5e-4
    wc_i = 2 * np.pi * 1500
    Gi = (L * wc_i + R * wc_i / S) / (R + L * S) * np.exp(-1.5 / 20e3 * S)
    Ti = Gi / (1 + Gi)
    Tsw = 1 / 4e3
    Teq = 1 / wc_i + Tsw + 1 / (2 * np.pi * 2000)
    Hm = 1 / (1 + S / (2 * np.pi * 2000)) * np.exp(-Tsw * S)

    def Gw(a):
        wc = 1 / (a * Teq)
        return (Jm * wc / Kt) * (1 + 1 / (a * a * Teq * S)) * Ti * Kt / (Jm * S) * Hm
    return Gw


def _bq(fc, zz, zp):
    w = 2 * np.pi * fc
    return (S ** 2 + 2 * zz * w * S + w ** 2) / (S ** 2 + 2 * zp * w * S + w ** 2)


def _cross(G):
    mag = 20 * np.log10(np.abs(G))
    idx = np.nonzero(np.diff(np.sign(mag)))[0]
    return F[idx], 180 + np.degrees(np.angle(G[idx]))


def fig_37_5():
    """Speed-loop open-loop response: rigid model, measured with belt, with notch."""
    Gw = _loops()
    model = Gw(3.0)
    belt = _bq(150, 0.025, 0.10) * _bq(240, 0.30, 0.06)       # -12 dB dip, +14 dB peak
    notch = _bq(240, 0.015, 0.15)                             # -20 dB, 240 Hz
    meas = model * belt
    meas_n = Gw(3.2) * belt * notch
    sel = (F >= 10) & (F <= 2000)
    f = F[sel]
    fig, (am, ap) = plt.subplots(2, 1, figsize=(6.4, 5.0), sharex=True,
                                 gridspec_kw=dict(hspace=0.1, height_ratios=[1.15, 1]))
    curves = [(model, BLUE, "-", "rigid-body model ($a$ = 3)"),
              (meas, ORANGE, "-", "measured on machine, belt ($a$ = 3)"),
              (meas_n, GREEN, "--", "measured, 240 Hz notch, $a$ = 3.2")]
    for G, c, ls, lab in curves:
        g = G[sel]
        am.semilogx(f, 20 * np.log10(np.abs(g)), color=c, ls=ls, label=lab)
        ph = np.degrees(np.unwrap(np.angle(g)))
        ph -= 360 * np.round((ph[0] - (-180)) / 360)  # anchor the branch near -180 deg at 10 Hz
        ap.semilogx(f, ph, color=c, ls=ls)
    am.axhline(0, color=INK, lw=0.7)
    am.set_ylim(-40, 40)
    am.set_ylabel("Magnitude (dB)")
    am.legend(loc="lower left", fontsize=7.6)
    am.grid(True, which="both", color=GRID, lw=0.5)
    ap.grid(True, which="both", color=GRID, lw=0.5)
    fc0, pm0 = _cross(model)
    fcn, pmn = _cross(meas_n)
    fcb, _ = _cross(meas)
    am.plot([fc0[0]], [0], "o", color=BLUE, ms=4)
    am.plot([fcn[0]], [0], "o", color=GREEN, ms=4)
    am.annotate("antiresonance\n150 Hz (−12 dB)", xy=(150, 20 * np.log10(abs(meas[np.argmin(abs(F - 150))]))),
                xytext=(30, -12), fontsize=7.4, color=ORANGE,
                arrowprops=dict(arrowstyle="-", color=ORANGE, lw=0.7))
    i240 = np.argmin(abs(F - 240))
    am.annotate("resonance 240 Hz:\n+14 dB above model,\nloop gain > 0 dB", xy=(240, 20 * np.log10(abs(meas[i240]))),
                xytext=(330, 22), fontsize=7.4, color=ORANGE,
                arrowprops=dict(arrowstyle="-", color=ORANGE, lw=0.7))
    am.annotate(f"crosses 0 dB again\nnear {fcb[-1]:.0f} Hz", xy=(fcb[-1], 0), xytext=(520, 3), fontsize=7.4,
                color=ORANGE, arrowprops=dict(arrowstyle="-", color=ORANGE, lw=0.7))
    am.annotate(f"with notch: {20 * np.log10(abs(meas_n[i240])):.0f} dB", xy=(240, 20 * np.log10(abs(meas_n[i240]))),
                xytext=(420, -35), fontsize=7.4, color=GREEN,
                arrowprops=dict(arrowstyle="-", color=GREEN, lw=0.7))
    ap.axhline(-180, color=INK, lw=0.7)
    ap.set_ylim(-360, -45)
    ap.set_yticks([-360, -315, -270, -225, -180, -135, -90, -45])
    ap.set_ylabel("Phase (deg)")
    ap.set_xlabel("Frequency (Hz)")
    ap.set_xlim(10, 2000)
    for fcx, pm, c, txt, xt in ((fc0[0], pm0[0], BLUE, "model", (14, -330)),
                                 (fcn[0], pmn[0], GREEN, "with notch", (14, -275))):
        ph = -180 + pm
        ap.plot([fcx, fcx], [-180, ph], color=c, lw=2.2)
        ap.plot(fcx, ph, "o", color=c, ms=4)
        ap.annotate(f"{txt}: {ph:.1f}° at {fcx:.0f} Hz\nPM {pm:.1f}°", xy=(fcx, ph), xytext=xt, fontsize=7.6,
                    color=c, arrowprops=dict(arrowstyle="-", color=c, lw=0.7))
    save(fig, "37", "fig-37-5-speed-loop-bode")
    return fc0[0], pm0[0], fcn[0], pmn[0]


# ----------------------------------------------------------------------------
def _load_step(Teq, a=3.0, J_=1.5e-4, dt=1e-6, t_end=0.045):
    """Euler simulation of the speed loop with lumped lag Teq (text listing, 37.5)."""
    Kp = J_ / (KT * a * Teq)
    Ti = a * a * Teq
    w0 = 1000 * 2 * np.pi / 60
    iq0 = (TC + BV * w0) / KT
    w = xi = 0.0
    iq = 0.0
    n = int(t_end / dt)
    ws, iqs = np.empty(n), np.empty(n)
    for k in range(n):
        xi += Kp / Ti * (-w) * dt
        iq += (np.clip(Kp * (-w) + xi, -I_PK - iq0, I_PK - iq0) - iq) * dt / Teq
        w += (KT * iq - 1.273) / J_ * dt
        ws[k], iqs[k] = w, iq
    t = np.arange(1, n + 1) * dt
    return t, 1000 + ws * 60 / (2 * np.pi), iq0 + iqs


def fig_37_6():
    """Load-step response at 1000 rpm, simulation against measurement."""
    Teq = 1 / (2 * np.pi * 1500) + 1 / 4e3 + 1 / (2 * np.pi * 2000)
    ts, ns, iqs = _load_step(Teq)
    tm, nm, iqm = _load_step(Teq * 1.09)           # measured: slightly more delay on the machine
    rng = np.random.default_rng(37)
    # measured log at 20 kHz, decimated to 0.25 ms for display
    sel = slice(0, None, 250)
    tmd, nmd, iqmd = tm[sel], nm[sel] + rng.normal(0, 0.8, nm[sel].size), iqm[sel] + rng.normal(0, 0.25, nm[sel].size)
    pre = np.arange(-5e-3, 0, 2.5e-4)
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.4, 4.8), sharex=True, gridspec_kw=dict(hspace=0.1))
    a1.axhspan(990, 1010, color=GREEN, alpha=0.12, lw=0)
    a1.axhline(880, color=RED, ls="--", lw=1.0)
    a1.text(30, 884, "R4 limit: dip ≤ 120 rpm", color=RED, fontsize=7.8, va="bottom", ha="center")
    a1.text(25, 1011, "±10 rpm band", color=GREEN, fontsize=7.6, va="bottom", ha="center")
    a1.plot(np.r_[pre, ts] * 1e3, np.r_[np.full(pre.size, 1000), ns], color=BLUE, label="simulation")
    a1.plot(np.r_[pre, tmd] * 1e3, np.r_[1000 + rng.normal(0, 0.8, pre.size), nmd], ".", ms=3, color=ORANGE,
            label="measured (drive log)")
    # metrics
    def metrics(t, n):
        k = np.argmin(n)
        rec = t[np.nonzero(np.abs(n - 1000) > 10)[0][-1] + 1]
        return t[k], n[k], rec, n.max()
    tk, nk, rec, nmax = metrics(ts, ns)
    tkm, nkm, recm, nmaxm = metrics(tm, nm)
    a1.annotate(f"sim. dip {nk:.0f} rpm at {tk * 1e3:.1f} ms", xy=(tk * 1e3, nk), xytext=(7, 900), fontsize=7.6,
                color=BLUE, arrowprops=dict(arrowstyle="-", color=BLUE, lw=0.7))
    a1.annotate(f"meas. dip {nkm:.0f} rpm at {tkm * 1e3:.1f} ms", xy=(tkm * 1e3, nkm), xytext=(7, 916), fontsize=7.6,
                color=ORANGE, arrowprops=dict(arrowstyle="-", color=ORANGE, lw=0.7))
    for r, c, y in ((rec, BLUE, 960), (recm, ORANGE, 945)):
        a1.plot([r * 1e3] * 2, [990, y], color=c, lw=0.8, ls=":")
    a1.text(rec * 1e3 + 0.4, 962, f"within 10 rpm: {rec * 1e3:.1f} ms (sim.)", fontsize=7.4, color=BLUE)
    a1.text(recm * 1e3 + 0.4, 947, f"{recm * 1e3:.1f} ms (meas.)", fontsize=7.4, color=ORANGE)
    a1.set_ylim(870, 1030)
    a1.set_ylabel("Speed (rpm)")
    a1.legend(loc="center right", fontsize=7.8)
    a1.axvline(0, color=GREY, lw=0.6)
    a1.text(0.3, 1022, "1.27 N·m load step at t = 0", fontsize=7.6, color=GREY)
    iq0 = (TC + BV * 1000 * 2 * np.pi / 60) / KT
    a2.plot(np.r_[pre, ts] * 1e3, np.r_[np.full(pre.size, iq0), iqs], color=BLUE)
    a2.plot(np.r_[pre, tmd] * 1e3, np.r_[iq0 + rng.normal(0, 0.25, pre.size), iqmd], ".", ms=3, color=ORANGE)
    iss = (1.273 + TC + BV * 1000 * 2 * np.pi / 60) / KT
    a2.axhline(iss, color=INK, lw=0.7, ls="--")
    a2.text(28, iss - 1.6, f"{iss:.1f} A = (1.27 N·m + friction)/$K_t$", fontsize=7.6, ha="center", va="top")
    kpk = np.argmax(iqs)
    a2.annotate(f"peak {iqs[kpk]:.1f} A at {ts[kpk] * 1e3:.1f} ms", xy=(ts[kpk] * 1e3, iqs[kpk]), xytext=(9, 18.3),
                fontsize=7.6, arrowprops=dict(arrowstyle="-", color=INK, lw=0.7))
    a2.text(-4.8, iq0 + 0.6, f"{iq0:.1f} A", fontsize=7.6)
    a2.set_ylim(0, 20)
    a2.set_ylabel("$i_q$ (A)")
    a2.set_xlabel("Time from load step (ms)")
    a2.set_xlim(-5, 40)
    a2.axvline(0, color=GREY, lw=0.6)
    save(fig, "37", "fig-37-6-load-step-response")
    return (nk, tk, rec, nmax, iqs[kpk], ts[kpk]), (nkm, tkm, recm, nmaxm)


if __name__ == "__main__":
    fig_37_1()
    fig_37_2()
    fig_37_3()
    fig_37_4()
    print("bode", fig_37_5())
    print("step", fig_37_6())
