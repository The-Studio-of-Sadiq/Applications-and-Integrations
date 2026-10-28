"""Figures for Chapter 10 — Embedded-System Integration.

Run from the repository root:  python figures/scripts/ch10.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Circle  # noqa: E402
from scipy.integrate import solve_ivp  # noqa: E402

from figstyle import COLORS, INK, box, save, schematic  # noqa: E402

BLUE, ORANGE, GREEN, PINK, YELLOW, SKY = COLORS[:6]
RED = "#C62828"
GREY = "#777777"


def tint(c, a="30"):
    return c + a


def line(ax, pts, color=INK, lw=1.1, ls="-", arrow_end=False):
    """Poly-line through pts, optionally with an arrow head on the last segment."""
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
# Figure 10.1 — TRV architecture
# ----------------------------------------------------------------------------
def fig_10_1():
    fig, ax = schematic(6.8, 5.15, xlim=(0, 13.6), ylim=(-0.3, 10.0))
    fs = 7.6
    pw = tint(ORANGE, "28")
    # --- power column
    box(ax, 0.1, 8.8, 2.4, 1.0, "2 × AA alkaline\n2 × 1.0–1.6 V", fc=pw, fontsize=fs)
    box(ax, 0.1, 7.2, 2.4, 1.1, "P-MOSFET\nreverse polarity\n50 mΩ", fc=pw, fontsize=fs)
    box(ax, 0.1, 5.3, 2.4, 1.4, "VBAT rail\n2.0–3.2 V\n220 µF + 10 µF\n(no regulator)", fc=pw, fontsize=fs)
    arrow(ax, 1.3, 8.8, 1.3, 8.3)
    arrow(ax, 1.3, 7.2, 1.3, 6.7)
    box(ax, 0.1, 0.45, 2.4, 0.9, "Load switch\nEN = HALL_EN", fc=pw, fontsize=fs)
    # VBAT -> MCU
    arrow(ax, 2.5, 6.2, 3.6, 6.2)
    ax.text(3.05, 6.27, "VDD", ha="center", va="bottom", fontsize=7)
    # bus to bridge and load switch
    line(ax, [(2.5, 5.6), (2.75, 5.6), (2.75, 0.9)])
    line(ax, [(2.75, 2.4), (3.0, 2.4)], arrow_end=True)
    line(ax, [(2.75, 0.9), (2.5, 0.9)], arrow_end=True)
    ax.text(2.82, 4.4, "VM", fontsize=7, ha="left", rotation=90, va="center")
    # left notes
    ax.text(1.3, 3.9, "MCU runs from 1.7 V\nwith internal DC/DC:\nno regulator,\nno dropout", ha="center",
            va="center", fontsize=7, color=GREY)
    ax.text(1.3, 2.2, "Stall trip in hardware:\nSAADC LIMITH → PPI\n→ PWM0 STOP", ha="center",
            va="center", fontsize=7, color=RED)
    # --- MCU
    mx0, mx1, my0, my1 = 3.4, 9.6, 3.6, 8.6
    ax.add_patch(FancyBboxPatch((mx0, my0), mx1 - mx0, my1 - my0,
                                boxstyle="round,pad=0.02,rounding_size=0.15",
                                fc=tint(BLUE, "18"), ec=INK, lw=1.3))
    ax.text((mx0 + mx1) / 2, 8.33, "nRF52840-class SoC", ha="center", va="center",
            fontsize=8.5, weight="bold")
    ax.text((mx0 + mx1) / 2, 7.98, "Cortex-M4F 64 MHz · 1 MB / 256 kB · Zephyr",
            ha="center", va="center", fontsize=6.8)
    cw, ch, gx = 1.34, 0.7, 0.15
    cols = [3.6 + i * (cw + gx) for i in range(4)]
    rows = {"a": 6.95, "b": 5.95, "c": 4.95}
    cells = {
        ("a", 0): "802.15.4\nradio", ("a", 1): "RTC", ("a", 2): "WDT\n4 s", ("a", 3): "POF\n2.30 V",
        ("b", 0): "TWIM", ("b", 1): "SPIM", ("b", 2): "UARTE", ("b", 3): "PPI",
        ("c", 0): "PWM0\n20 kHz", ("c", 1): "SAADC\n12 bit", ("c", 2): "GPIOTE", ("c", 3): "TIMER\n600 /mm",
    }
    for (r, c), t in cells.items():
        fc = "white"
        if t.startswith(("SAADC", "PPI", "PWM0")):
            fc = tint(RED, "18")
        box(ax, cols[c], rows[r], cw, ch, t, fc=fc, fontsize=7)
    # GPIOTE -> TIMER
    arrow(ax, cols[2] + cw, rows["c"] + ch / 2, cols[3], rows["c"] + ch / 2)
    # --- bottom actuator chain
    act = tint(GREEN, "28")
    box(ax, 3.0, 1.9, 2.1, 1.0, "DRV8837-class\nH-bridge", fc=act, fontsize=fs)
    box(ax, 5.9, 1.9, 1.4, 1.0, "Gear\nmotor\n10 Ω", fc=act, fontsize=fs)
    box(ax, 8.1, 1.9, 2.4, 1.0, "150:1 gearbox,\n0.5 mm lead\nscrew", fc=act, fontsize=fs)
    box(ax, 11.1, 1.9, 2.4, 1.0, "Valve pin\n4.5 mm stroke", fc=act, fontsize=fs)
    box(ax, 3.0, 0.45, 2.1, 0.9, "1.0 Ω shunt\n55–263 mA", fc=act, fontsize=fs)
    box(ax, 5.9, 0.45, 1.4, 0.9, "Hall latch\n2.3 mA", fc=act, fontsize=fs)
    arrow(ax, 5.1, 2.4, 5.9, 2.4)
    arrow(ax, 7.3, 2.4, 8.1, 2.4)
    arrow(ax, 10.5, 2.4, 11.1, 2.4)
    arrow(ax, 4.05, 1.9, 4.05, 1.35)
    ax.text(4.12, 1.62, "GND return", fontsize=6.5, va="center")
    # PWM0 -> bridge
    arrow(ax, 4.3, rows["c"], 4.3, 2.9)
    ax.text(4.36, 4.25, "IN1, IN2\nnSLEEP", ha="left", va="center", fontsize=6.5)
    # shunt -> SAADC
    line(ax, [(5.1, 0.9), (5.5, 0.9), (5.5, rows["c"])], arrow_end=True)
    ax.text(5.58, 4.25, "AIN0\n≤ 263 mV", fontsize=6.5, va="center")
    # motor - hall coupling (magnet)
    line(ax, [(6.6, 1.9), (6.6, 1.35)], ls="--", color=GREY)
    ax.text(6.68, 1.62, "magnet", fontsize=6.3, va="center", color=GREY)
    # hall -> GPIOTE
    line(ax, [(7.3, 0.9), (7.55, 0.9), (7.55, rows["c"])], arrow_end=True)
    ax.text(7.63, 4.25, "hall edges\n133 /s", fontsize=6.5, va="center")
    # load switch -> hall
    line(ax, [(1.3, 0.45), (1.3, 0.12), (6.6, 0.12), (6.6, 0.45)], arrow_end=True)
    ax.text(3.9, 0.05, "switched VBAT: while moving + 60 ms", fontsize=6.5, va="top", ha="center")
    # --- right peripherals
    per = tint(PINK, "28")
    rx = 10.9
    items = [(7.3, "SHT40-class\nT/RH sensor", "I²C\n100 kHz", rows["b"] + 0.55),
             (6.1, "E-paper\ndisplay", "SPI\n4 MHz", None),
             (4.9, "2 buttons", "GPIO", None),
             (3.7, "UART + SWD\ntest pads", "1 Mbd /\n4 MHz", None)]
    for y, t, lab, _ in items:
        box(ax, rx, y, 2.6, 0.85, t, fc=per, fontsize=fs)
        yy = y + 0.42
        if y > 4.0:
            arrow(ax, mx1, yy, rx, yy, both=True)
        else:
            arrow(ax, mx1 - 0.0, yy, rx, yy, both=True)
        ax.text((mx1 + rx) / 2, yy + 0.06, lab, ha="center", va="bottom", fontsize=6.2)
    # --- radio uplink
    ax.plot([4.3, 4.3], [8.6, 9.25], color=INK, lw=1.1)
    ax.plot([4.05, 4.3, 4.55], [9.55, 9.25, 9.55], color=INK, lw=1.1)
    ax.plot([4.3, 4.3], [9.25, 9.6], color=INK, lw=1.1)
    ax.text(4.7, 9.05, "antenna", fontsize=6.5, va="center")
    box(ax, 6.0, 9.0, 2.7, 0.85, "Thread parent\nrouter", fc=tint(SKY, "30"), fontsize=fs)
    box(ax, 10.9, 9.0, 2.6, 0.85, "Building hub", fc=tint(SKY, "30"), fontsize=fs)
    arrow(ax, 4.9, 9.42, 6.0, 9.42, both=True)
    ax.text(5.45, 9.5, "802.15.4", fontsize=6.3, ha="center", va="bottom")
    arrow(ax, 8.7, 9.42, 10.9, 9.42, both=True)
    ax.text(9.8, 9.5, "CoAP; poll 5 s", fontsize=6.5, ha="center", va="bottom")
    save(fig, "10", "fig-10-1-trv-architecture")


def arrow(ax, x0, y0, x1, y1, color=INK, both=False):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="<|-|>" if both else "-|>", color=color, lw=1.1,
                                shrinkA=0, shrinkB=0, mutation_scale=10))


# ----------------------------------------------------------------------------
# Figure 10.2 — power path and actuator interface (schemdraw)
# ----------------------------------------------------------------------------
def fig_10_2():
    import schemdraw
    import schemdraw.elements as elm
    schemdraw.use("matplotlib")
    d = schemdraw.Drawing(show=False)
    d.config(fontsize=8, unit=2.5, lw=1.1)
    T = []          # (x, y, text, ha, va) placed after drawing, in drawing units
    PL = 7.5        # pin-label size

    def term(pt, direction, length, text, ha):
        ln = d.add(getattr(elm.Line().at(pt), direction)(length))
        d.add(elm.Dot(open=True).at(ln.end))
        off = -0.3 if ha == "right" else 0.3
        T.append((ln.end[0] + off, ln.end[1], text, ha, "center"))

    # ---- power path
    d.add(elm.BatteryDouble().up().at((0, 0)))
    T.append((-0.7, 1.25, "2 × AA\n2.0–3.2 V", "right", "center"))
    d.add(elm.Ground().at((0, 0)))
    d.add(elm.Line().up(0.5).at((0, 2.5)))
    q1 = d.add(elm.PFet().theta(0).anchor("drain").at((0, 3.0)))
    T.append((-0.5, 3.75, "Q1\nP-MOSFET\n50 mΩ", "right", "center"))
    gx = q1.gate[0] + 0.6
    d.add(elm.Line().at(q1.gate).right(0.6))
    d.add(elm.Line().down().toy(0.4))
    d.add(elm.Ground())
    rail_y = 5.6
    d.add(elm.Line().at(q1.source).up().toy(rail_y))
    T.append((0.2, rail_y + 0.25, "VBAT", "left", "bottom"))
    xc1, xc2 = 3.4, 7.4
    d.add(elm.Line().at((0, rail_y)).right().tox(xc1))
    d.add(elm.Dot())
    d.add(elm.Capacitor(polar=True).down())
    T.append((xc1 + 0.6, rail_y - 1.25, "220 µF", "left", "center"))
    d.add(elm.Ground())
    d.add(elm.Line().at((xc1, rail_y)).right().tox(xc2))
    d.add(elm.Dot())
    d.add(elm.Capacitor().down())
    T.append((xc2 + 0.6, rail_y - 1.25, "10 µF", "left", "center"))
    d.add(elm.Ground())

    # ---- H-bridge
    ic = elm.Ic(size=(6.4, 5.0), pins=[
        elm.IcPin("VM", side="T", pos=0.3, lblsize=PL), elm.IcPin("VCC", side="T", pos=0.7, lblsize=PL),
        elm.IcPin("IN1", side="L", pos=0.8, lblsize=PL), elm.IcPin("IN2", side="L", pos=0.55, lblsize=PL),
        elm.IcPin("nSLEEP", side="L", pos=0.25, lblsize=PL),
        elm.IcPin("OUT1", side="R", pos=0.8, lblsize=PL), elm.IcPin("OUT2", side="R", pos=0.3, lblsize=PL),
        elm.IcPin("GND", side="B", pos=0.5, lblsize=PL)], leadlen=0.6)
    ic = d.add(ic.theta(0).anchor("center").at((14.0, 0.5)))
    T.append((ic.absanchors["OUT2"][0] + 0.3, ic.absanchors["OUT2"][1] - 1.1, "DRV8837-class\nH-bridge", "left", "center"))
    for p in ("VM", "VCC"):
        d.add(elm.Line().at(ic.absanchors[p]).up().toy(rail_y))
        d.add(elm.Dot())
    d.add(elm.Line().at((xc2, rail_y)).right().tox(ic.absanchors["VCC"][0]))
    for p, t in (("IN1", "PWM0 ch0, 20 kHz"), ("IN2", "PWM0 ch1, 20 kHz"), ("nSLEEP", "GPIO MOT_EN")):
        term(ic.absanchors[p], "left", 1.0, t, "right")
    # motor
    o1, o2 = ic.absanchors["OUT1"], ic.absanchors["OUT2"]
    xm = o1[0] + 1.2
    d.add(elm.Line().at(o1).right().tox(xm))
    d.add(elm.Motor().down().toy(o2[1]))
    d.add(elm.Line().left().tox(o2[0]))
    T.append((xm + 0.7, (o1[1] + o2[1]) / 2, "M\n10 Ω gear\nmotor", "left", "center"))
    # shunt and RC filter
    g = ic.absanchors["GND"]
    d.add(elm.Line().at(g).down(0.5))
    sn = d.add(elm.Dot())
    d.add(elm.Resistor().down())
    T.append((g[0] + 0.5, sn.center[1] - 1.25, "R_S 1.0 Ω\n0.25 W", "left", "center"))
    d.add(elm.Ground())
    d.add(elm.Resistor().at(sn.center).left())
    T.append((sn.center[0] - 1.25, sn.center[1] + 0.45, "1 kΩ", "center", "bottom"))
    rcn = d.add(elm.Dot())
    d.add(elm.Capacitor().down())
    T.append((rcn.center[0] - 0.5, rcn.center[1] - 1.25, "10 nF", "right", "center"))
    d.add(elm.Ground())
    term(rcn.center, "left", 1.0, "SAADC AIN0\ngain 1, 0.6 V ref", "right")

    # ---- battery divider (lower left)
    bx, by = 1.5, -7.8
    d.add(elm.Vdd().at((bx, by)))
    T.append((bx, by + 0.6, "VBAT", "center", "bottom"))
    d.add(elm.Resistor().down().at((bx, by)))
    T.append((bx - 0.45, by - 1.25, "1 MΩ", "right", "center"))
    dn = d.add(elm.Dot())
    d.add(elm.Resistor().down())
    T.append((bx - 0.45, by - 3.75, "1 MΩ", "right", "center"))
    q2 = d.add(elm.NFet().theta(0).anchor("drain"))
    T.append((bx - 0.4, q2.center[1] if hasattr(q2, "center") else by - 5.75, "Q2", "right", "center"))
    d.add(elm.Ground().at(q2.source))
    term(q2.gate, "right", 0.6, "GPIO BATT_EN", "left")
    d.add(elm.Line().at(dn.center).right(1.5))
    cn = d.add(elm.Dot())
    d.add(elm.Capacitor().down())
    T.append((cn.center[0] + 0.45, cn.center[1] - 1.25, "100 nF", "left", "center"))
    d.add(elm.Ground())
    term(cn.center, "right", 0.9, "AIN1", "left")

    # ---- hall latch with load switch
    hx, hy = 10.0, -7.8
    d.add(elm.Vdd().at((hx, hy)))
    T.append((hx, hy + 0.6, "VBAT", "center", "bottom"))
    ls = elm.Ic(size=(3.0, 2.2), pins=[elm.IcPin("IN", side="T", pos=0.5, lblsize=PL),
                                       elm.IcPin("EN", side="L", pos=0.5, lblsize=PL),
                                       elm.IcPin("OUT", side="B", pos=0.5, lblsize=PL)], leadlen=0.5)
    ls = d.add(ls.theta(0).anchor("IN").at((hx, hy)))
    T.append((hx + 1.9, ls.absanchors["EN"][1], "load switch", "left", "center"))
    term(ls.absanchors["EN"], "left", 0.8, "GPIO HALL_EN", "right")
    hl = elm.Ic(size=(3.0, 2.2), pins=[elm.IcPin("VDD", side="T", pos=0.5, lblsize=PL),
                                       elm.IcPin("OUT", side="R", pos=0.5, lblsize=PL),
                                       elm.IcPin("GND", side="B", pos=0.5, lblsize=PL)], leadlen=0.5)
    hl = d.add(hl.theta(0).anchor("VDD").at((hx, ls.absanchors["OUT"][1] - 0.6)))
    T.append((hx + 1.9, hl.absanchors["OUT"][1] - 0.75, "hall latch", "left", "center"))
    d.add(elm.Line().at(ls.absanchors["OUT"]).to(hl.absanchors["VDD"]))
    d.add(elm.Ground().at(hl.absanchors["GND"]))
    term(hl.absanchors["OUT"], "right", 0.6, "GPIOTE", "left")

    # ---- SHT40 with pull-ups
    sx, sy = 18.8, -7.8
    d.add(elm.Vdd().at((sx + 0.75, sy)))
    T.append((sx + 0.75, sy + 0.6, "VBAT", "center", "bottom"))
    d.add(elm.Line().at((sx, sy)).right(1.5))
    for xx in (sx, sx + 1.5):
        d.add(elm.Resistor().down().at((xx, sy)))
    T.append((sx - 0.45, sy - 1.25, "10 kΩ", "right", "center"))
    T.append((sx + 1.95, sy - 1.25, "10 kΩ", "left", "center"))
    sh = elm.Ic(size=(3.2, 3.2), pins=[elm.IcPin("SDA", side="L", pos=0.7, lblsize=PL),
                                       elm.IcPin("SCL", side="L", pos=0.3, lblsize=PL),
                                       elm.IcPin("VDD", side="T", pos=0.5, lblsize=PL),
                                       elm.IcPin("GND", side="B", pos=0.5, lblsize=PL)], leadlen=0.5)
    sh = d.add(sh.theta(0).anchor("SDA").at((sx + 3.2, sy - 3.4)))
    T.append((sh.absanchors["VDD"][0] + 2.0, sh.absanchors["SDA"][1] - 0.45, "SHT40-\nclass\nT/RH", "left", "center"))
    for xx, nm in ((sx, "SDA"), (sx + 1.5, "SCL")):
        y = sh.absanchors[nm][1]
        d.add(elm.Line().at((xx, sy - 2.5)).down().toy(y))
        d.add(elm.Dot())
        d.add(elm.Line().right().tox(sh.absanchors[nm][0]))
    for xx, nm in ((sx, "SDA"), (sx + 1.5, "SCL")):
        y = sh.absanchors[nm][1]
        if nm == "SCL":
            d.add(elm.Line().at((xx, y)).left().tox(sx))
        term((sx, y), "left", 0.8, "TWIM " + nm, "right")
    d.add(elm.Line().at(sh.absanchors["VDD"]).up(0.4))
    d.add(elm.Vdd())
    T.append((sh.absanchors["VDD"][0], sh.absanchors["VDD"][1] + 1.0, "VBAT", "center", "bottom"))
    d.add(elm.Ground().at(sh.absanchors["GND"]))

    fig, ax = plt.subplots(figsize=(6.8, 5.0))
    ax.axis("off")
    d.draw(show=False, canvas=ax)
    for x, y, t, ha, va in T:
        ax.text(x, y, t, ha=ha, va=va, fontsize=8, color=INK)
    ax.set_aspect("equal")
    ax.autoscale()
    ax.text(0.99, 0.99,
            "Motor current\nrunning 55–90 mA\nstall 177–263 mA\nthreshold 130 mA\n= 130 mV on R_S\n= SAADC code 887",
            transform=ax.transAxes, ha="right", va="top", fontsize=7.5,
            bbox=dict(boxstyle="round,pad=0.4", fc="#F6F6F6", ec=GREY, lw=0.8))
    save(fig, "10", "fig-10-2-trv-interface-circuit")


# ----------------------------------------------------------------------------
# Figure 10.3 — valve state machine
# ----------------------------------------------------------------------------
def fig_10_3():
    fig, ax = schematic(6.8, 5.0, xlim=(0, 13.6), ylim=(0, 10.0))
    S = {"BOOT": (1.4, 8.4), "HOMING": (6.6, 8.4), "SAFE": (11.8, 8.4),
         "IDLE": (3.2, 4.4), "MOVING": (10.0, 4.4), "LOCKOUT": (3.2, 1.0)}
    W, H = 2.3, 1.0
    fcs = {"SAFE": tint(RED, "25"), "LOCKOUT": tint(ORANGE, "30"), "BOOT": "#EEEEEE"}
    for n, (x, y) in S.items():
        ax.add_patch(FancyBboxPatch((x - W / 2, y - H / 2), W, H,
                                    boxstyle="round,pad=0.02,rounding_size=0.35",
                                    fc=fcs.get(n, tint(BLUE, "22")), ec=INK, lw=1.3))
        ax.text(x, y, n, ha="center", va="center", fontsize=9.5, weight="bold")
    # initial pseudo-state
    ax.add_patch(Circle((1.4, 9.75), 0.13, color=INK))
    ax.annotate("", xy=(1.4, 8.9), xytext=(1.4, 9.62),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.1, mutation_scale=10))
    ax.text(1.6, 9.75, "power-on / any reset", fontsize=7.5, va="center")

    def tr(p0, p1, text, tx, ty, rad=0.0, ha="center", color=INK):
        ax.add_patch(FancyArrowPatch(p0, p1, connectionstyle=f"arc3,rad={rad}",
                                     arrowstyle="-|>", mutation_scale=11, color=color, lw=1.1))
        ax.text(tx, ty, text, fontsize=7.3, ha=ha, va="center", color=color,
                bbox=dict(fc="white", ec="none", pad=0.6))

    W2, H2 = W / 2, H / 2
    # BOOT -> HOMING
    tr((1.4 + W2, 8.4), (6.6 - W2, 8.4), "retained RAM and\njournal both invalid", 4.0, 9.05)
    # BOOT -> IDLE
    tr((1.6, 8.4 - H2), (2.9, 4.4 + H2), "retained or journalled\nposition valid\n(≈ 0.4 s, R8)", 1.05, 6.4, ha="center")
    # HOMING -> IDLE
    tr((6.2, 8.4 - H2), (3.8, 4.4 + H2), "stall or encoder\ntimeout:\nset zero", 5.65, 6.35)
    # HOMING -> SAFE / SAFE -> HOMING
    tr((6.6 + W2, 8.55), (11.8 - W2, 8.55), "40 s timeout", 9.2, 9.0)
    tr((11.8 - W2, 8.2), (6.6 + W2, 8.2), "remote reset or\n10 s button hold", 9.2, 7.65)
    # IDLE -> MOVING / MOVING -> IDLE
    tr((3.2 + W2, 4.65), (10.0 - W2, 4.65), "setpoint outside ±30 counts\nand loaded battery OK", 6.6, 5.25)
    tr((10.0 - W2, 4.15), (3.2 + W2, 4.15), "target reached, or\nexpected end-stop stall", 6.6, 3.55)
    # MOVING self loop
    ax.add_patch(FancyArrowPatch((10.0 + W2, 4.6), (10.0 + W2 - 0.05, 4.2),
                                 connectionstyle="arc3,rad=-2.2", arrowstyle="-|>",
                                 mutation_scale=11, color=INK, lw=1.1))
    ax.text(11.9, 3.35, "unexpected stall:\nback off, retry\n(max 2 retries)", fontsize=7.3, ha="center", va="center")
    # MOVING -> SAFE
    tr((10.4, 4.4 + H2), (11.6, 8.4 - H2), "retries exhausted\nor move timeout", 12.0, 6.4, ha="center")
    # IDLE <-> LOCKOUT
    tr((2.9, 4.4 - H2), (2.9, 1.0 + H2), "loaded battery\n< 2.10 V", 1.5, 2.7)
    tr((3.5, 1.0 + H2), (3.5, 4.4 - H2), "battery\nreplaced", 4.55, 2.7)
    # note
    ax.text(9.2, 1.05,
            "POF warning (2.30 V) only defers flash writes\nand new motor starts; it never resets.\n"
            "LOCKOUT and SAFE exit only on an external event.",
            ha="center", va="center", fontsize=7.5,
            bbox=dict(boxstyle="round,pad=0.4", fc="#F6F6F6", ec=GREY, lw=0.8))
    save(fig, "10", "fig-10-3-valve-state-machine")


# ----------------------------------------------------------------------------
# Figure 10.4 — motor current during a closing move ending at the end stop
# ----------------------------------------------------------------------------
def motor_move():
    I_S = 255.0       # mA, stall current (fresh cells, 0 C)
    TAU = 0.010       # s, mechanical time constant
    t_imp, t_trip = 1.490, 1.4955

    def duty(t):
        return np.clip(0.3 + 0.7 * t / 0.030, 0.3, 1.0)

    def iload(t):
        return 55.0 + 35.0 * np.clip((t - 0.05) / (t_imp - 0.05), 0, 1) ** 2

    # e = back-EMF as a fraction of the supply; i = (D - e) * I_S
    def f(t, y):
        e = y[0]
        i = (duty(t) - e) * I_S
        return [(i - iload(t)) / (TAU * I_S)]

    t1 = np.linspace(0, t_imp, 30001)
    sol = solve_ivp(f, (0, t_imp), [0.0], t_eval=t1, max_step=2e-4)
    e = sol.y[0]
    i_run = (duty(t1) - e) * I_S
    i0 = i_run[-1]
    tau_s = 5.0e-3 / np.log((I_S - i0) / (I_S - 130.0))   # reach 130 mA 5.0 ms after impact
    t2 = np.linspace(t_imp, t_trip, 400)
    i2 = I_S - (I_S - i0) * np.exp(-(t2 - t_imp) / tau_s)
    t3 = np.linspace(t_trip, 1.6, 4000)
    i3 = i2[-1] * np.exp(-(t3 - t_trip) / 0.04e-3)
    t = np.concatenate([t1, t2[1:], t3[1:]])
    i = np.concatenate([i_run, i2[1:], i3[1:]])
    # hall edges: 133 per second at running speed, proportional to speed
    speed = np.concatenate([e / e[-1], np.zeros(len(t2) - 1 + len(t3) - 1)])
    cum = np.cumsum(speed) * (t[1] - t[0]) * 133.0
    n = np.floor(cum[:len(t1)]).astype(int)
    edges = list(t1[np.nonzero(np.diff(n))[0] + 1])
    edges += [t_imp + 0.0035, t_imp + 0.0090, t_imp + 0.0165]  # three coasting edges
    return t, i, np.array(edges), t_imp, t_trip


def fig_10_4():
    t, i, edges, t_imp, t_trip = motor_move()
    fig, (ax, axh) = plt.subplots(2, 1, figsize=(6.8, 4.6), sharex=True,
                                  gridspec_kw=dict(height_ratios=[3.2, 1], hspace=0.12))
    ax.axvspan(0, 0.05, color=GREY, alpha=0.18, lw=0)
    ax.text(0.058, 295, "blanking 0–50 ms", fontsize=7.5, va="top", color=GREY)
    ax.plot(t, i, color=BLUE, lw=1.4)
    ax.axhline(130, ls="--", color=RED, lw=1.1)
    ax.text(0.55, 126, "stall threshold 130 mA (130 mV, code 887)", color=RED, fontsize=8, va="top")
    ax.axhline(255, ls=":", color=GREY, lw=0.9)
    ax.text(1.58, 259, "stall current 255 mA (fresh cells, 0 °C)", color=GREY, fontsize=7.5,
            va="bottom", ha="right")
    ax.text(0.75, 47, "running 55 → 90 mA as the pin compresses the spring", fontsize=7.5,
            ha="center", va="top", color=BLUE)
    ip = i[(t > 0) & (t < 0.05)].max()
    tp = t[(t < 0.05)][np.argmax(i[(t < 0.05)])]
    ax.annotate(f"soft start, peak {ip:.0f} mA", xy=(tp, ip), xytext=(0.10, 185), fontsize=7.5,
                arrowprops=dict(arrowstyle="-", color=INK, lw=0.7))
    ax.set_xlim(0, 1.6)
    ax.set_ylim(0, 300)
    ax.set_ylabel("Motor current (mA)")
    # inset
    axi = ax.inset_axes([0.40, 0.58, 0.32, 0.27])
    m = (t >= 1.485) & (t <= 1.52)
    axi.plot(t[m], i[m], color=BLUE, lw=1.4)
    axi.axhline(130, ls="--", color=RED, lw=1.0)
    axi.axvline(t_imp, color=GREY, lw=0.8)
    axi.axvline(t_trip, color=RED, lw=0.8)
    axi.set_xlim(1.488, 1.52)
    axi.set_ylim(0, 160)
    axi.set_xticks([1.49, 1.50, 1.51, 1.52])
    axi.set_xticklabels(["1.49", "1.50", "1.51", "1.52"], fontsize=7)
    axi.set_yticks([0, 50, 100, 150])
    axi.tick_params(labelsize=7)
    axi.text(t_trip + 0.0007, 100, "PPI trip at 1.4955 s;\n0 mA within 0.2 ms", fontsize=6.5, ha="left",
             va="center", color=RED)
    axi.annotate("", xy=(t_trip, 25), xytext=(t_imp, 25),
                 arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.8, mutation_scale=7,
                                 shrinkA=0, shrinkB=0))
    axi.text(t_trip + 0.0007, 25, "impact 1.490 s → trip:\n5.5 ms ≤ 20 ms (R3)", fontsize=6.5, va="center")
    for s in ("top", "right"):
        axi.spines[s].set_visible(True)
    ax.indicate_inset_zoom(axi, edgecolor=GREY, lw=0.6)
    # hall edges as latch output
    lvl, tt, yy = 0, [0.0], [0]
    for te in edges:
        tt += [te, te]
        yy += [lvl, 1 - lvl]
        lvl = 1 - lvl
    tt.append(1.6)
    yy.append(lvl)
    axh.plot(tt, yy, color=GREEN, lw=0.6)
    axh.set_ylim(-0.2, 1.9)
    axh.set_yticks([0, 1])
    axh.set_ylabel("Hall\nlatch")
    axh.text(0.3, 1.55, "133 edges/s at speed", fontsize=7.5, color=GREEN, va="center")
    axh.annotate("edges stop at impact,\n+ 3 coasting edges", xy=(1.50, 1.0), xytext=(1.44, 1.55),
                 fontsize=7, color=GREEN, va="center", ha="right",
                 arrowprops=dict(arrowstyle="-", color=GREEN, lw=0.6))
    axh.set_xlabel("Time from motor start (s)")
    save(fig, "10", "fig-10-4-motor-current-stall")


# ----------------------------------------------------------------------------
# Figure 10.5 — battery life against valve moves per day
# ----------------------------------------------------------------------------
DAY = 86400.0
LOADS = [("sleep floor", 3.0e-6, DAY, 1), ("temperature read", 1.7e-3, 6e-3, 1440),
         ("Thread data poll", 5.5e-3, 3.5e-3, DAY / 5), ("status report", 6.0e-3, 18e-3, 288),
         ("valve moves", 70e-3, 1.5, 48), ("weekly exercise", 70e-3, 40.6, 1 / 7),
         ("display updates", 3.0e-3, 2.0, 10)]


def life_years(moves):
    ua = {n: i * t * k / DAY * 1e6 for n, i, t, k in LOADS}
    other = sum(v for n, v in ua.items() if n != "valve moves")
    mv = 70e-3 * 1.5 / DAY * 1e6
    i_sd = 2500 * 0.02 / 8760 * 1e3
    return 0.8 * 2500 / ((other + np.asarray(moves) * mv + i_sd) / 1e3) / 8760, ua


def fig_10_5():
    n = np.linspace(2, 100, 400)
    L, ua = life_years(n)
    fig, ax = plt.subplots(figsize=(6.4, 3.9))
    ax.axvspan(60, 100, color=ORANGE, alpha=0.12, lw=0)
    ax.text(80, 0.25, "above control-team limit\n(≤ 60 moves/day)", ha="center", va="bottom",
            fontsize=8, color="#9A4A00")
    ax.plot(n, L, color=BLUE)
    pts = [12, 24, 48, 72, 96]
    Lp, _ = life_years(pts)
    ax.plot(pts, Lp, "o", color=BLUE, ms=4)
    for x, y in zip(pts, Lp):
        if x != 48:
            ax.text(x + 1.5, y + 0.12, f"{y:.2f}", fontsize=7.5, color=BLUE)
    ax.axhline(2.0, ls="--", color=RED, lw=1.1)
    ax.text(1.5, 1.93, "R4: 2.0 years", color=RED, fontsize=8, ha="left", va="top")
    ax.axhline(2.5, ls=":", color=RED, lw=1.2)
    ax.text(1.5, 2.57, "R4 + 25 % margin: 2.5 years", color=RED, fontsize=8, ha="left", va="bottom")
    L48, _ = life_years(48)
    ax.plot([48], [L48], "s", color=ORANGE, ms=7, zorder=5)
    ax.annotate(f"design point\n48 moves/day, {L48:.2f} years", xy=(48, L48), xytext=(22, 0.6),
                fontsize=8, arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.8))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 8)
    ax.set_xlabel("Average valve moves per day")
    ax.set_ylabel("Predicted battery life (years)")
    # inset pie of the 71.1 uA load
    total = sum(ua.values())
    parts = [("moves", ua["valve moves"]), ("weekly\nexercise", ua["weekly exercise"]),
             ("Thread\npolls", ua["Thread data poll"]), ("sleep\nfloor", ua["sleep floor"]),
             ("other", ua["temperature read"] + ua["status report"] + ua["display updates"])]
    axp = fig.add_axes([0.38, 0.47, 0.24, 0.36])
    cols = [BLUE, SKY, GREEN, GREY, YELLOW]
    wedges, _ = axp.pie([p[1] for p in parts], colors=cols, startangle=90, counterclock=False,
                        wedgeprops=dict(ec="white", lw=0.8))
    labs = [f"{p[0]} {p[1] / total * 100:.0f} %" for p in parts]
    axp.legend(wedges, labs, loc="center left", bbox_to_anchor=(1.0, 0.5), fontsize=7,
               handlelength=1.0, labelspacing=0.5)
    axp.set_title(f"load at 48 moves/day: {total:.1f} µA", fontsize=8)
    save(fig, "10", "fig-10-5-life-vs-moves")


# ----------------------------------------------------------------------------
# Figure 10.6 — battery rail during homing, Rev A vs Rev B (0 C, 1.25 V/cell)
# ----------------------------------------------------------------------------
def rail_trace(t, starts, stalls, stops, i_peak_ss, i_run, i_stall, r=1.70, voc=2.50):
    """Rail = Voc - I*R with a battery current built from soft start, running and stall phases."""
    i = np.zeros_like(t)
    for t0, ts, te in zip(starts, stalls, stops):
        m = (t >= t0) & (t < te)
        tau = t[m] - t0
        # soft start: duty ramps over 30 ms; battery current peaks then settles
        ss = i_peak_ss * np.exp(-((tau - 0.02) / 0.015) ** 2)
        run = i_run * (1 - np.exp(-tau / 0.03))
        ib = np.maximum(ss, run)
        st = t[m] >= ts
        ib[st] = i_run + (i_stall - i_run) * (1 - np.exp(-(t[m][st] - ts) / 0.004))
        i[m] = ib
    return voc - i * 1e-3 * r


def fig_10_6():
    t = np.linspace(0, 3.0, 30001)
    # Rev A: full-duty homing; stall resets the MCU via the POF handler, 0.4 s boot, repeat
    va = rail_trace(t, starts=[0.10, 1.42, 2.42], stalls=[1.0, 2.0, 3.0],
                    stops=[1.018, 2.018, 3.1], i_peak_ss=47, i_run=70, i_stall=193)
    # Rev B: half duty, battery current ~ D^2 of the motor current; encoder-timeout stop
    vb = rail_trace(t, starts=[0.10], stalls=[1.352], stops=[1.40],
                    i_peak_ss=30, i_run=29, i_stall=48)
    fig, ax = plt.subplots(figsize=(6.6, 3.9))
    ax.axhline(2.30, ls="--", color=ORANGE, lw=1.1)
    ax.axhline(2.10, ls="--", color=PINK, lw=1.1)
    ax.axhline(1.70, ls="--", color=GREY, lw=1.1)
    ax.text(2.98, 2.305, "2.30 V POF warning", color=ORANGE, fontsize=7.5, ha="right", va="bottom")
    ax.text(0.03, 2.105, "2.10 V loaded-rail lockout (Rev B)", color=PINK, fontsize=7.5, ha="left", va="bottom")
    ax.text(2.98, 1.705, "1.7 V hardware brownout reset", color=GREY, fontsize=7.5, ha="right", va="bottom")
    ax.plot(t, va, color=RED, lw=1.3, label="Rev A: POF handler resets, homing repeats")
    ax.plot(t, vb, color=BLUE, lw=1.5, label="Rev B: half-duty homing, encoder-timeout stop")
    for ts in (1.0, 2.0):
        ax.annotate("stall → POF\n→ reset", xy=(ts + 0.012, 2.175), xytext=(ts - 0.33, 2.02),
                    fontsize=7.3, color=RED, arrowprops=dict(arrowstyle="-|>", color=RED, lw=0.8))
        ax.annotate("", xy=(ts + 0.42, 2.535), xytext=(ts + 0.02, 2.535),
                    arrowprops=dict(arrowstyle="<|-|>", color=RED, lw=0.8, mutation_scale=7,
                                    shrinkA=0, shrinkB=0))
        ax.text(ts + 0.22, 2.545, "0.4 s boot", fontsize=7, color=RED, ha="center", va="bottom")
    ax.text(0.5, 2.365, "2.38 V running", fontsize=7.3, color=RED, ha="center", va="top")
    ax.text(0.5, 2.462, "2.45 V running", fontsize=7.3, color=BLUE, ha="center", va="bottom")
    ax.annotate("min 2.17 V", xy=(1.017, 2.172), xytext=(1.12, 2.205), fontsize=7.3, color=RED,
                arrowprops=dict(arrowstyle="-", color=RED, lw=0.6))
    ax.annotate("encoder timeout,\ndip to 2.42 V, then idle", xy=(1.39, 2.415), xytext=(1.12, 1.96),
                fontsize=7.3, color=BLUE, arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=0.8))
    ax.set_xlim(0, 3.0)
    ax.set_ylim(1.6, 2.62)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Battery rail (V)")
    ax.legend(loc="lower left", fontsize=7.8, bbox_to_anchor=(0.0, 0.12))
    ax.text(0.01, 0.99, "0 °C, emulated battery 2 × 1.25 V, 1.70 Ω", transform=ax.transAxes,
            fontsize=7.5, va="top", color=GREY)
    save(fig, "10", "fig-10-6-rail-dip-rev-a-b")


if __name__ == "__main__":
    fig_10_1()
    fig_10_2()
    fig_10_3()
    fig_10_4()
    fig_10_5()
    fig_10_6()
