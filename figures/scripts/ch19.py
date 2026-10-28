"""Figures for Chapter 19 — Industrial Sensors and Actuators.

Run from the repository root:  python figures/scripts/ch19.py
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, Polygon, Ellipse  # noqa: E402
import schemdraw  # noqa: E402
import schemdraw.elements as elm  # noqa: E402

from figstyle import COLORS, INK, save, schematic  # noqa: E402

schemdraw.use("matplotlib")

BLUE, ORANGE, GREEN, PINK, YELLOW, SKY = COLORS[:6]
RED = "#C62828"
GREY = "#777777"
C_AI, C_DI, C_DO, C_IOL = BLUE, GREEN, ORANGE, "#8E44AD"


def tint(c, a="30"):
    return c + a


def line(ax, pts, color=INK, lw=1.1, ls="-", arrow_end=False, both=False, ms=9, z=2):
    xs, ys = zip(*pts)
    if not arrow_end and not both:
        ax.plot(xs, ys, color=color, lw=lw, ls=ls, solid_capstyle="butt", zorder=z)
        return
    if len(pts) > 2:
        ax.plot(xs[:-1], ys[:-1], color=color, lw=lw, ls=ls, zorder=z)
    ax.annotate("", xy=pts[-1], xytext=pts[-2],
                arrowprops=dict(arrowstyle="<|-|>" if both else "-|>", color=color, lw=lw,
                                ls=ls, shrinkA=0, shrinkB=0, mutation_scale=ms), zorder=z)


def rbox(ax, x, y, w, h, fc="#EEF3F8", ec=INK, lw=1.0, ls="-", z=3, r=0.1):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.02,rounding_size={r}",
                                fc=fc, ec=ec, lw=lw, ls=ls, zorder=z))


def bubble(ax, x, y, tag, sig, r=0.42, fs=5.6):
    """ISA-style instrument bubble with a coloured signal ring."""
    col = {"AI": C_AI, "DI": C_DI, "DO": C_DO, "IOL": C_IOL, "AO": C_AI}[sig]
    ax.add_patch(Circle((x, y), r, fc="white", ec=col, lw=1.6, zorder=5))
    ax.text(x, y, tag, ha="center", va="center", fontsize=fs, zorder=6, weight="bold")


# ----------------------------------------------------------------------------
# Figure 19.1 — CIP skid instrumentation
# ----------------------------------------------------------------------------
def fig_19_1():
    fig, ax = schematic(6.8, 5.4, xlim=(0, 17), ylim=(-0.2, 13.3))
    pipe = dict(color="#4A6A8A", lw=2.4, z=1)
    ys, yr = 9.55, 6.4
    # tanks, instruments on their left
    tanks = [("T1", "water"), ("T2", "caustic 1.5 %"), ("T3", "acid")]
    ty = [10.3, 7.6, 4.9]
    for (t, med), y in zip(tanks, ty):
        ax.add_patch(FancyBboxPatch((1.05, y), 1.9, 2.2, boxstyle="round,pad=0,rounding_size=0.35",
                                    fc=tint(SKY, "30"), ec=INK, lw=1.1, zorder=3))
        ax.text(2.0, y + 1.55, t, ha="center", fontsize=7.8, weight="bold", zorder=4)
        ax.text(2.0, y + 1.1, med, ha="center", fontsize=5.6, zorder=4)
        ax.text(2.0, y + 0.7, "2 m³", ha="center", fontsize=5.6, zorder=4)
        for yy, tag, sig, fs in ((y + 1.85, "LSHH", "DI", 4.6), (y + 1.0, "ZS", "DI", 5.6),
                                 (y + 0.15, "LT", "AI", 5.6)):
            bubble(ax, 0.47, yy, tag, sig, fs=fs)
            line(ax, [(0.89, yy), (1.05, yy)], color=GREY, lw=0.8)
        # supply stub from the tank bottom to the manifold
        line(ax, [(2.95, y + 0.35), (3.6, y + 0.35)], **pipe)
    ax.text(2.0, 12.85, "level 4–20 mA, fork switch LSHH,\nmanway switch ZS on each tank",
            fontsize=5.9, ha="center", va="center")
    line(ax, [(3.6, ty[2] + 0.35), (3.6, ty[0] + 0.35)], **pipe)
    line(ax, [(3.6, ys), (16.55, ys)], **pipe)
    ax.annotate("", xy=(16.98, ys), xytext=(16.5, ys),
                arrowprops=dict(arrowstyle="-|>", color="#4A6A8A", lw=2.0, mutation_scale=12))
    ax.text(16.95, ys + 0.3, "supply to\ncircuit", fontsize=6.0, ha="right", va="bottom")
    # P1 pump on VFD
    ax.add_patch(Circle((5.0, ys), 0.55, fc="white", ec=INK, lw=1.2, zorder=4))
    ax.add_patch(Polygon([(4.75, ys + 0.35), (4.75, ys - 0.35), (5.4, ys)], fc=INK, zorder=5))
    ax.text(5.0, ys - 0.72, "P1 7.5 kW", fontsize=6.3, ha="center", va="top", weight="bold")
    rbox(ax, 4.35, 10.75, 1.3, 0.7, fc="#F2F2F2")
    ax.text(5.0, 11.1, "VFD", fontsize=6.4, ha="center", va="center", zorder=5)
    line(ax, [(5.0, 10.75), (5.0, 10.1)], color=INK, lw=0.9)
    # PHE and steam valve
    ax.add_patch(Rectangle((6.55, ys - 0.75), 1.2, 1.5, fc="#F7E7D7", ec=INK, lw=1.1, zorder=4))
    for k in range(5):
        xx = 6.7 + k * 0.22
        ax.plot([xx, xx], [ys - 0.65, ys + 0.65], color="#9A6A3A", lw=0.7, zorder=5)
    ax.text(7.15, ys - 0.95, "plate heat\nexchanger", fontsize=5.9, ha="center", va="top")
    vx, vy = 7.15, 11.4
    ax.add_patch(Polygon([(vx - 0.35, vy - 0.2), (vx - 0.35, vy + 0.2), (vx + 0.35, vy - 0.2),
                          (vx + 0.35, vy + 0.2)], closed=True, fc="white", ec=INK, lw=0.9, zorder=4))
    line(ax, [(vx - 1.0, vy), (vx - 0.35, vy)], color="#9A6A3A", lw=1.6)
    line(ax, [(vx + 0.35, vy), (vx + 0.55, vy), (vx + 0.55, ys + 0.75)], color="#9A6A3A", lw=1.6)
    ax.text(vx - 0.85, vy + 0.12, "steam", fontsize=5.8, ha="center", va="bottom", color="#9A6A3A")
    line(ax, [(vx, vy + 0.2), (vx, vy + 0.4)], color=GREY, lw=0.8)
    bubble(ax, vx, vy + 0.82, "TCV", "AO", fs=5.0)
    ax.text(vx + 0.5, vy + 0.82, "positioner,\n4–20 mA from AO", fontsize=5.6, ha="left", va="center")
    # instruments on the supply line
    for x, tag, note in ((9.6, "FT", "magflow DN50"), (11.2, "PT", "0–6 bar"), (12.8, "TT1", "Pt100")):
        line(ax, [(x, ys), (x, ys + 0.55)], color=GREY, lw=0.8)
        bubble(ax, x, ys + 0.97, tag, "AI", fs=5.2)
        ax.text(x, ys + 1.5, note, fontsize=5.7, ha="center", va="bottom")
    # return line
    line(ax, [(16.55, yr), (4.0, yr)], **pipe)
    ax.annotate("", xy=(16.45, yr), xytext=(16.98, yr),
                arrowprops=dict(arrowstyle="-|>", color="#4A6A8A", lw=2.0, mutation_scale=12))
    ax.text(16.95, yr + 0.3, "return from\ncircuit, 40 m", fontsize=6.0, ha="right", va="bottom")
    ax.annotate("", xy=(4.0, 8.3), xytext=(4.0, yr),
                arrowprops=dict(arrowstyle="-|>", color="#4A6A8A", lw=2.0, mutation_scale=10))
    ax.text(4.12, 7.7, "to tank\nreturns", fontsize=5.6, ha="left", va="center")
    for x, tag, note in ((14.9, "TT2", "Pt100"), (13.0, "QT", "conductivity")):
        line(ax, [(x, yr), (x, yr + 0.55)], color=GREY, lw=0.8)
        bubble(ax, x, yr + 0.97, tag, "AI", fs=5.2)
        ax.text(x, yr + 1.5, note, fontsize=5.7, ha="center", va="bottom")
    vxr = 8.9
    line(ax, [(13.0, yr - 0.95), (vxr, yr - 0.95)], color=RED, lw=0.8, both=True, ms=6)
    ax.text(12.2, yr - 1.02, "9 m", fontsize=6.0, color=RED, ha="center", va="top")
    for xx in (13.0, vxr):
        line(ax, [(xx, yr - 0.25), (xx, yr - 1.1)], color=RED, lw=0.6)
    # return pump P2
    ax.add_patch(Circle((10.9, yr), 0.5, fc="white", ec=INK, lw=1.2, zorder=4))
    ax.add_patch(Polygon([(11.2, yr + 0.3), (11.2, yr - 0.3), (10.6, yr)], fc=INK, zorder=5))
    ax.text(10.9, yr + 0.62, "P2 3 kW,\ncontactor", fontsize=6.0, ha="center", va="bottom",
            weight="bold")
    for xx in (vxr, vxr - 1.3):
        ax.add_patch(Polygon([(xx - 0.3, yr - 0.18), (xx - 0.3, yr + 0.18), (xx + 0.3, yr - 0.18),
                              (xx + 0.3, yr + 0.18)], closed=True, fc="white", ec=INK, lw=0.9,
                             zorder=4))
    ax.text(vxr - 0.65, yr + 0.3, "return valves", fontsize=5.6, ha="center", va="bottom")
    line(ax, [(vxr - 1.3 + 0.0, yr), (vxr - 1.3, yr - 0.9)], **pipe)
    ax.text(vxr - 1.3, yr - 0.95, "drain", fontsize=5.8, ha="center", va="top")
    # valves and valve island block
    rbox(ax, 4.2, 3.0, 6.6, 1.55, fc=tint(C_IOL, "18"), ec=C_IOL)
    ax.text(7.5, 4.25, "24 sanitary valves, single-acting, spring return", fontsize=6.3,
            ha="center", va="center", weight="bold")
    ax.text(7.5, 3.62, "valve-top units (2-wire open/closed sensors, pilot);\n"
            "24-station valve island on one IO-Link port", fontsize=5.8, ha="center", va="center")
    # air supply
    rbox(ax, 11.6, 3.0, 2.6, 1.55, fc="#F2F2F2")
    ax.text(12.9, 4.15, "air 6 bar", fontsize=6.4, ha="center", weight="bold", zorder=5)
    ax.text(12.9, 3.55, "refrigerant dryer,\nISO 8573-1 [2:4:2]", fontsize=5.4, ha="center",
            va="center", zorder=5)
    line(ax, [(11.6, 3.77), (10.8, 3.77)], color="#4A8A4A", lw=1.6, arrow_end=True)
    bubble(ax, 14.75, 3.77, "PSL", "DI", fs=5.0)
    line(ax, [(14.2, 3.77), (14.33, 3.77)], color=GREY, lw=0.8)
    ax.text(15.25, 3.77, "4.8 bar", fontsize=5.8, va="center")
    # remote I/O
    rbox(ax, 0.25, 0.0, 16.5, 1.85, fc="#F7F7F7", ec=INK, z=0)
    ax.text(0.45, 1.62, "PLC remote I/O drop", fontsize=6.8, weight="bold", va="top")
    secs = [(2.9, "DI type 3", C_DI, "LSHH, ZS, PSL,\naux contacts"),
            (6.0, "DO 0.5 A", C_DO, "P2 contactor coil,\nprocess solenoids"),
            (9.1, "AI 250 Ω (+ AO)", C_AI, "LT, FT, PT, TT, QT;\nAO to TCV positioner"),
            (12.6, "IO-Link master", C_IOL, "valve island,\nvalve-top units")]
    for x, t, c, note in secs:
        rbox(ax, x, 0.2, 2.9, 1.15, fc=tint(c, "22"), ec=c, z=4)
        ax.text(x + 1.45, 1.1, t, fontsize=6.4, ha="center", va="center", weight="bold", zorder=5)
        ax.text(x + 1.45, 0.55, note, fontsize=5.4, ha="center", va="center", zorder=5)
    # signal routes, one lane each
    line(ax, [(0.2, 4.95), (0.2, 2.15), (3.6, 2.15), (3.6, 1.35)], color=C_DI, lw=1.3,
         arrow_end=True)
    ax.text(0.32, 3.0, "24 V DI", fontsize=5.6, color=C_DI, rotation=90, va="center")
    line(ax, [(0.47, ty[2] + 0.15 - 0.42), (0.47, 4.0), (0.75, 4.0), (0.75, 2.45), (10.0, 2.45),
              (10.0, 1.35)], color=C_AI, lw=1.3, arrow_end=True)
    ax.text(2.0, 2.52, "4–20 mA (LT ×3)", fontsize=5.6, color=C_AI, va="bottom")
    line(ax, [(16.2, yr - 0.3), (16.2, 2.45), (11.0, 2.45), (11.0, 1.35)], color=C_AI, lw=1.3,
         arrow_end=True)
    ax.text(16.1, 5.0, "4–20 mA", fontsize=5.6, color=C_AI, rotation=90, ha="right", va="center")
    line(ax, [(9.6, 3.0), (9.6, 2.75), (14.05, 2.75), (14.05, 1.35)], color=C_IOL, lw=1.3,
         arrow_end=True)
    ax.text(12.4, 2.7, "IO-Link", fontsize=5.6, color=C_IOL, va="top")
    line(ax, [(11.35, yr - 0.5), (11.35, 2.2), (7.45, 2.2), (7.45, 1.35)], color=C_DO, lw=1.3,
         arrow_end=True)
    ax.text(11.25, 5.05, "24 V DO", fontsize=5.6, color=C_DO, rotation=90, ha="right",
            va="center")
    line(ax, [(14.75, 3.35), (14.75, 1.98), (4.6, 1.98), (4.6, 1.35)], color=C_DI, lw=1.0,
         arrow_end=True, ls=(0, (3, 1.5)))
    # legend of signal colours
    lx, ly = 10.6, 12.85
    for i, (c, lab) in enumerate(((C_AI, "analogue 4–20 mA"), (C_DI, "discrete in"),
                                  (C_DO, "discrete out"), (C_IOL, "IO-Link"))):
        xx = lx + (i % 2) * 3.6
        yy = ly - (i // 2) * 0.55
        ax.add_patch(Circle((xx, yy), 0.17, fc="white", ec=c, lw=1.6, zorder=5))
        ax.text(xx + 0.3, yy, lab, fontsize=6.0, va="center")
    save(fig, "19", "fig-19-1-cip-skid-instrumentation")


# ----------------------------------------------------------------------------
# Figure 19.2 — field-side wiring
# ----------------------------------------------------------------------------
def fig_19_2():
    fig, ax = plt.subplots(figsize=(6.8, 4.4))
    ax.set_aspect("equal")
    ax.axis("off")
    d = schemdraw.Drawing(canvas=ax, show=False)
    d.config(fontsize=6.5, unit=1.5, lw=1.0)
    Y24, Y0 = 13.0, 1.0
    XR = 26.0
    fs = 5.6

    def wire(p, q, color=INK):
        d.add(elm.Line().at(p).to(q).color(color))

    def dot(p):
        d.add(elm.Dot().at(p))

    # supply rails and circuit protector
    wire((0.4, Y24), (1.6, Y24))
    ax.add_patch(Rectangle((1.6, Y24 - 0.45), 2.0, 0.9, fc=tint(RED, "20"), ec=INK, lw=1.0, zorder=3))
    ax.text(2.6, Y24, "ECP 2 A", fontsize=6.4, ha="center", va="center", weight="bold", zorder=4)
    ax.text(2.6, Y24 - 0.6, "electronic circuit\nprotector", fontsize=5.4, ha="center", va="top")
    wire((3.6, Y24), (XR, Y24))
    wire((0.4, Y0), (XR, Y0))

    ax.text(4.0, Y24 + 0.2, "+24 V (21.6 V minimum)", fontsize=6.3, va="bottom", color=RED)
    ax.text(0.4, Y0 - 0.2, "0 V", fontsize=6.3, va="top", color=BLUE)

    # DI module frame
    ax.add_patch(Rectangle((4.6, 2.2), 10.1, 2.4, fc="#F3F8F3", ec=GREEN, lw=1.0, zorder=0))
    ax.text(13.1, 3.4, "DI module\nIEC 61131-2\ntype 3,\nsinking", fontsize=fs, color="#1E6B45",
            va="center", ha="left")
    # (a) 3-wire PNP sensor
    xa = 6.0
    dot((xa - 0.5, Y24))
    wire((xa - 0.5, Y24), (xa - 0.5, 9.6), "#8B4513")
    ax.add_patch(Rectangle((xa - 0.9, 7.6), 1.8, 2.0, fc="white", ec=INK, lw=1.0, zorder=3))
    ax.text(xa, 8.6, "PNP\n3-wire\nsensor", fontsize=6.0, ha="center", va="center", zorder=4)
    wire((xa - 0.5, 7.6), (xa - 0.5, Y0), BLUE)
    dot((xa - 0.5, Y0))
    wire((xa + 0.5, 7.6), (xa + 0.5, 4.6))
    d.add(elm.Resistor().at((xa + 0.5, 4.6)).to((xa + 0.5, 2.6)))
    wire((xa + 0.5, 2.6), (xa + 0.5, Y0))
    dot((xa + 0.5, Y0))
    ax.text(xa, 10.4, "(a)", fontsize=7.4, ha="center", weight="bold")
    ax.text(xa + 0.62, 6.1, "output\n+24 V\nwhen on", fontsize=fs, va="center")
    ax.text(xa - 0.62, 6.1, "BU", fontsize=5.4, color=BLUE, ha="right")
    ax.text(xa - 0.62, 11.2, "BN", fontsize=5.4, color="#8B4513", ha="right")
    # (b) 2-wire valve-top sensor
    xb = 9.0
    dot((xb, Y24))
    wire((xb, Y24), (xb, 9.6))
    ax.add_patch(Rectangle((xb - 1.0, 7.6), 2.0, 2.0, fc="white", ec=INK, lw=1.0, zorder=3))
    ax.text(xb, 8.6, "2-wire\nvalve-top\nsensor", fontsize=5.8, ha="center", va="center", zorder=4)
    wire((xb, 7.6), (xb, 4.6))
    d.add(elm.Resistor().at((xb, 4.6)).to((xb, 2.6)))
    wire((xb, 2.6), (xb, Y0))
    dot((xb, Y0))
    ax.text(xb, 10.4, "(b)", fontsize=7.4, ha="center", weight="bold")
    ax.text(xb + 0.15, 6.1, "off: 0.8 mA\nresidual\n(type 3 limit\n1.5 mA);\non: 4.6 V drop",
            fontsize=fs, va="center")
    # (c) manway switch, NC positive opening
    xc = 12.3
    dot((xc, Y24))
    wire((xc, Y24), (xc, 9.8))
    d.add(elm.Switch(nc=True).at((xc, 9.8)).to((xc, 7.4)))
    wire((xc, 7.4), (xc, 4.6))
    d.add(elm.Resistor().at((xc, 4.6)).to((xc, 2.6)))
    wire((xc, 2.6), (xc, Y0))
    dot((xc, Y0))
    ax.add_patch(Circle((xc - 0.9, 8.6), 0.3, fc="white", ec=INK, lw=0.8, zorder=4))
    ax.annotate("", xy=(xc - 0.9, 8.38), xytext=(xc - 0.9, 8.85),
                arrowprops=dict(arrowstyle="-|>", lw=0.7, color=INK, mutation_scale=5), zorder=5)
    ax.text(xc, 10.4, "(c)", fontsize=7.4, ha="center", weight="bold")
    ax.text(xc + 0.3, 6.1, "manway switch,\npositive-opening\nNC contact,\ngold-flash",
            fontsize=fs, va="center")

    # DO module frame
    ax.add_patch(Rectangle((14.9, 9.9), 5.4, 2.5, fc="#FFF5EA", ec=ORANGE, lw=1.0, zorder=0))
    ax.text(15.05, 12.3, "DO module, 0.5 A per\nchannel (sourcing)", fontsize=fs, color="#9A5A00",
            va="top")
    # (d) solenoid with diode + Zener
    xd = 16.0
    dot((xd, Y24))
    wire((xd, Y24), (xd, 11.0))
    d.add(elm.Switch().at((xd, 11.0)).to((xd, 9.9)))
    wire((xd, 9.9), (xd, 8.6))
    dot((xd, 8.6))
    d.add(elm.Inductor2(loops=3).at((xd, 8.6)).to((xd, 5.6)))
    dot((xd, 5.6))
    wire((xd, 5.6), (xd, Y0))
    dot((xd, Y0))
    wire((xd, 8.6), (xd + 1.1, 8.6))
    d.add(elm.Diode().at((xd + 1.1, 7.1)).to((xd + 1.1, 8.6)))
    d.add(elm.Zener().at((xd + 1.1, 7.1)).to((xd + 1.1, 5.6)))
    wire((xd + 1.1, 5.6), (xd, 5.6))
    ax.text(xd - 0.4, 7.9, "solenoid\npilot 24 V,\n8 W, 72 Ω", fontsize=fs, ha="right", va="center")
    ax.text(xd + 1.4, 7.85, "D", fontsize=5.4, va="center")
    ax.text(xd + 1.4, 6.35, "ZD\n24 V", fontsize=5.4, va="center")
    ax.text(xd + 0.15, 4.3, "switch sees\n48.7 V;\nrelease\n2.9 ms", fontsize=5.4, va="center")
    ax.text(xd, 13.55, "(d)", fontsize=7.4, ha="center", weight="bold")
    # (e) interposing relay switching a 230 V contactor coil
    xe = 19.3
    dot((xe, Y24))
    wire((xe, Y24), (xe, 11.0))
    d.add(elm.Switch().at((xe, 11.0)).to((xe, 9.9)))
    wire((xe, 9.9), (xe, 9.2))
    ax.add_patch(Rectangle((xe - 0.45, 7.6), 0.9, 1.6, fc="white", ec=INK, lw=1.0, zorder=3))
    ax.plot([xe - 0.45, xe + 0.45], [7.6, 9.2], color=INK, lw=0.8, zorder=4)
    wire((xe, 7.6), (xe, Y0))
    dot((xe, Y0))
    ax.text(xe - 0.55, 8.4, "K10\nrelay", fontsize=5.4, ha="right", va="center")
    ax.text(xe, 13.55, "(e)", fontsize=7.4, ha="center", weight="bold")
    # 230 V side
    xl = 21.3
    ax.add_patch(Rectangle((20.55, 1.55), 2.6, 7.75, fc="#FBEEEE", ec=RED, lw=0.8, ls=(0, (3, 2)),
                           zorder=0))
    ax.text(21.85, 9.45, "230 V AC", fontsize=6.0, color=RED, ha="center", va="bottom", weight="bold")
    wire((xl, 8.9), (xl, 8.3))
    d.add(elm.Switch().at((xl, 8.3)).to((xl, 6.8)))
    ax.plot([xe + 0.45, xl - 0.3], [8.4, 7.55], color=INK, lw=0.7, ls=(0, (2, 2)), zorder=2)
    wire((xl, 6.8), (xl, 6.2))
    dot((xl, 6.2))
    ax.add_patch(Rectangle((xl - 0.45, 3.9), 0.9, 1.6, fc="white", ec=INK, lw=1.0, zorder=3))
    wire((xl, 6.2), (xl, 5.5))
    wire((xl, 3.9), (xl, 3.0))
    dot((xl, 3.0))
    wire((xl, 6.2), (xl + 1.2, 6.2))
    d.add(elm.Resistor().at((xl + 1.2, 6.2)).to((xl + 1.2, 4.6)))
    d.add(elm.Capacitor().at((xl + 1.2, 4.6)).to((xl + 1.2, 3.0)))
    wire((xl + 1.2, 3.0), (xl, 3.0))
    ax.text(xl, 9.0, "L", fontsize=6.0, ha="center", va="bottom")
    ax.text(xl, 2.85, "N", fontsize=6.0, ha="center", va="top")
    ax.text(xl, 4.7, "A1\n–\nA2", fontsize=5.0, ha="center", va="center", zorder=4)
    ax.text(21.85, 2.45, "contactor coil\nwith RC", fontsize=5.4, ha="center", va="top")
    ax.text(xl + 1.45, 4.6, "RC", fontsize=5.6, ha="left", va="center")
    # (f) 2-wire transmitter loop with display and AI
    xf = 24.6
    dot((xf, Y24))
    wire((xf, Y24), (xf, 11.25))
    ax.add_patch(Circle((xf, 10.6), 0.62, fc="white", ec=INK, lw=1.0, zorder=3))
    ax.annotate("", xy=(xf, 10.15), xytext=(xf, 11.05),
                arrowprops=dict(arrowstyle="-|>", lw=0.9, color=INK, mutation_scale=7), zorder=4)
    wire((xf, 9.98), (xf, 8.6))
    ax.add_patch(Rectangle((xf - 0.55, 7.2), 1.1, 1.4, fc="white", ec=INK, lw=1.0, zorder=3))
    ax.text(xf, 7.9, "disp-\nlay", fontsize=5.4, ha="center", va="center", zorder=4)
    wire((xf, 7.2), (xf, 4.4))
    ax.add_patch(Rectangle((xf - 0.9, 2.2), 1.8, 2.4, fc="#EEF3F8", ec=BLUE, lw=1.0, zorder=0))
    d.add(elm.Resistor().at((xf, 4.4)).to((xf, 2.6)))
    wire((xf, 2.6), (xf, Y0))
    dot((xf, Y0))
    ax.text(xf, 13.55, "(f)", fontsize=7.4, ha="center", weight="bold")
    ax.text(xf - 0.85, 2.3, "AI", fontsize=6.0, color=BLUE, va="bottom", ha="left")
    ax.text(xf - 0.75, 10.6, "PT\n2-wire", fontsize=5.4, va="center", ha="right")
    ax.text(xf + 0.75, 10.6, "≥ 12 V\nneeded;\n13.2 V\nleft", fontsize=5.4, va="center")
    ax.text(xf + 0.65, 7.9, "2.5 V", fontsize=5.4, va="center")
    ax.text(xf + 0.95, 3.4, "250 Ω\n5.5 V", fontsize=5.4, va="center")
    ax.text(xf + 0.15, 5.8, "cable\n18 Ω\n0.4 V", fontsize=5.4, va="center")
    ax.text(XR, 0.4, "loop (f) at 22 mA: 21.6 − 5.5 − 2.5 − 0.4 = 13.2 V ≥ 12 V: margin 1.2 V",
            fontsize=5.8, ha="right", va="top", color="#1B4F8A")
    d.draw(show=False)
    ax.set_xlim(0.2, 26.6)
    ax.set_ylim(-0.4, 14.1)
    save(fig, "19", "fig-19-2-field-interface-wiring")


# ----------------------------------------------------------------------------
# Figure 19.3 — temperature sensor tolerances
# ----------------------------------------------------------------------------
def fig_19_3():
    fig, ax = plt.subplots(figsize=(6.4, 3.9))
    t = np.linspace(-50, 600, 1301)
    curves = [("Pt100 class AA", lambda x: 0.1 + 0.0017 * np.abs(x), (-50, 250), BLUE, "-"),
              ("Pt100 class A", lambda x: 0.15 + 0.002 * np.abs(x), (-100, 450), GREEN, "-"),
              ("Pt100 class B", lambda x: 0.3 + 0.005 * np.abs(x), (-196, 600), ORANGE, "-"),
              ("type K class 1", lambda x: np.maximum(1.5, 0.004 * np.abs(x)), (-40, 1000), RED, "--"),
              ("type K class 2", lambda x: np.maximum(2.5, 0.0075 * np.abs(x)), (-40, 1200), PINK, "--")]
    for lab, f, (lo, hi), c, ls in curves:
        m = (t >= lo) & (t <= hi)
        ax.plot(t[m], f(t[m]), color=c, ls=ls, lw=1.8, label=lab)
        v = float(f(np.array(75.0)))
        ax.plot([75], [v], "o", color=c, ms=4.5, zorder=5)
    marks = [(0.2275, "0.23", BLUE), (0.30, "0.30", GREEN), (0.675, "0.68", ORANGE),
             (1.5, "1.5", RED), (2.5, "2.5", PINK)]
    for v, s, c in marks:
        dy = {"0.23": -0.1, "0.30": 0.1}.get(s, 0.0)
        ax.text(66, v + dy, s, color=c, fontsize=7, ha="right", va="center",
                bbox=dict(fc="white", ec="none", pad=0.3))
    ax.axvline(75, color=GREY, ls=(0, (5, 3)), lw=1.0)
    ax.text(78, 3.75, "CIP return\n75 °C", fontsize=7.4, color=GREY, va="center")
    ax.axhline(1.0, color=INK, ls=(0, (5, 3)), lw=1.0)
    ax.text(595, 1.05, "R1 limit: U95 ≤ 1.0 °C (whole measurement)", fontsize=7.4, ha="right",
            va="bottom")
    ax.text(255, 0.5, "AA ends\nat 250 °C", fontsize=6.6, color=BLUE, ha="left", va="top")
    ax.text(455, 0.95, "A ends\nat 450 °C", fontsize=6.6, color=GREEN, ha="left", va="top")
    ax.set_xlim(-50, 600)
    ax.set_ylim(0, 5)
    ax.set_xlabel("temperature t (°C)")
    ax.set_ylabel("tolerance ± (°C)")
    ax.legend(fontsize=7.2, loc="upper left", bbox_to_anchor=(0.27, 1.0), ncol=2)
    save(fig, "19", "fig-19-3-temperature-sensor-tolerances")


# ----------------------------------------------------------------------------
# Figure 19.4 — loop load lines
# ----------------------------------------------------------------------------
def fig_19_4():
    Vs, Vtx, Rc = 21.6, 12.0, 2 * 250 * 0.036
    cfgs = [("AI card 250 Ω + 18 Ω cable", 250 + Rc, 0.0, BLUE, "-"),
            ("card + loop display (2.5 V)", 250 + Rc, 2.5, GREEN, "-"),
            ("card + display + 2nd 250 Ω receiver (518 Ω)", 500 + Rc, 2.5, RED, "-"),
            ("fix: active splitter, 50 Ω input (68 Ω), 2.5 V", 50 + Rc, 2.5, PINK, "--")]
    I = np.linspace(0, 24, 400)
    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    ax.axvspan(3.8, 20.5, color="#E9F3E9", lw=0, zorder=0)
    ax.text(12.15, 21.3, "NE 43 valid band 3.8–20.5 mA", fontsize=7.2, ha="center", va="top",
            color="#2F6B3A")
    for x in (3.6, 21.0):
        ax.axvline(x, color="#2F6B3A", lw=0.8, ls=":")
    ax.text(3.5, 0.4, "≤ 3.6 mA\nfailure", fontsize=6.4, ha="right", va="bottom", color="#2F6B3A")
    ax.text(21.1, 0.4, "≥ 21 mA\nfailure", fontsize=6.4, ha="left", va="bottom", color="#2F6B3A")
    for lab, R, Vf, c, ls in cfgs:
        V = Vs - Vf - I * 1e-3 * R
        ax.plot(I, V, color=c, ls=ls, lw=1.8, label=lab)
        v22 = Vs - Vf - 22e-3 * R
        ax.plot([22], [v22], "o", color=c, ms=4.5, zorder=5)
    ax.axhline(Vtx, color=INK, ls=(0, (5, 3)), lw=1.0)
    ax.text(0.3, Vtx + 0.2, "transmitter lift-off 12 V (with HART)", fontsize=7.0, va="bottom")
    ax.axvline(22, color=GREY, lw=0.8)
    ax.text(22.15, 21.3, "design\n22 mA", fontsize=6.6, color=GREY, va="top")
    i_st = (Vs - Vtx - 2.5) / ((500 + Rc) * 1e-3)
    ax.plot([i_st], [Vtx], "s", color=RED, ms=5, zorder=6)
    ax.annotate(f"starves at {i_st:.1f} mA:\nreading frozen at {6 * (i_st - 4) / 16:.2f} bar",
                xy=(i_st, Vtx), xytext=(13.8, 6.2), fontsize=7.2, color=RED, ha="left",
                arrowprops=dict(arrowstyle="-", color=RED, lw=0.8))
    ax.annotate("", xy=(22.35, 12.0), xytext=(22.35, Vs - 2.5 - 22e-3 * (250 + Rc)),
                arrowprops=dict(arrowstyle="<|-|>", color=GREEN, lw=0.8, mutation_scale=5,
                                shrinkA=0, shrinkB=0))
    ax.annotate("1.2 V margin at 22 mA\n(design as drawn)", xy=(22.35, 12.6), xytext=(21.6, 10.6),
                fontsize=6.6, color=GREEN, ha="right", va="top",
                arrowprops=dict(arrowstyle="-", color=GREEN, lw=0.7))
    ax.set_xlim(0, 24)
    ax.set_ylim(0, 22)
    ax.set_xlabel("loop current (mA)")
    ax.set_ylabel("voltage at transmitter terminals (V)")
    ax.legend(fontsize=6.8, loc="lower left", bbox_to_anchor=(0.0, 0.08))
    ax.text(23.8, 4.4, "supply 21.6 V (24 V − 10 %)", fontsize=6.4, ha="right", va="center",
            color=GREY)
    save(fig, "19", "fig-19-4-loop-load-lines")


# ----------------------------------------------------------------------------
# Figure 19.5 — coil current decay
# ----------------------------------------------------------------------------
def fig_19_5():
    V, P, L = 24.0, 8.0, 0.5
    R = V ** 2 / P
    I0, Idrop = V / R, 0.30 * V / R
    tau = L / R
    t = np.linspace(0, 15e-3, 3001)
    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    for name, vc, c in (("diode only", 0.7, BLUE), ("diode + 24 V Zener", 24.7, GREEN),
                        ("TVS 48 V", 48.0, RED)):
        a = vc / R
        i = np.maximum((I0 + a) * np.exp(-t / tau) - a, 0.0)
        t_rel = tau * math.log((I0 + a) / (Idrop + a))
        ax.plot(t * 1e3, i * 1e3, color=c, lw=1.8,
                label=f"{name}: switch sees {V + vc:.1f} V, release {t_rel * 1e3:.2f} ms")
        ax.plot([t_rel * 1e3], [Idrop * 1e3], "o", color=c, ms=5, zorder=5)
        pos = {"TVS 48 V": (0.3, 70), "diode + 24 V Zener": (3.25, 106)}.get(
            name, (t_rel * 1e3 + 0.25, 72))
        ax.text(pos[0], pos[1], f"{t_rel * 1e3:.2f} ms", fontsize=7.2, color=c)
    ax.axhline(Idrop * 1e3, color=INK, ls=(0, (5, 3)), lw=1.0)
    ax.text(14.9, Idrop * 1e3 + 4, "armature dropout ≈ 100 mA (30 % of rated)", fontsize=7.2,
            ha="right", va="bottom")
    ax.text(14.9, 300, f"coil 72 Ω, 0.5 H: τ = {tau * 1e3:.1f} ms, I₀ = {I0 * 1e3:.0f} mA",
            fontsize=7.2, ha="right", color="#444444")
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 350)
    ax.set_xlabel("time after switch-off (ms)")
    ax.set_ylabel("coil current (mA)")
    ax.legend(fontsize=7.0, loc="upper right", bbox_to_anchor=(1.0, 0.82))
    save(fig, "19", "fig-19-5-coil-current-decay")


if __name__ == "__main__":
    fig_19_1()
    fig_19_2()
    fig_19_3()
    fig_19_4()
    fig_19_5()
