"""Figures for Chapter 5 — Engineering Documentation.

Run from the repository root:  python figures/scripts/ch05.py
"""
import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle, Polygon, FancyBboxPatch  # noqa: E402
import schemdraw  # noqa: E402
import schemdraw.elements as elm  # noqa: E402

from figstyle import COLORS, INK, box, save, schematic, new_fig  # noqa: E402

schemdraw.use("matplotlib")
warnings.filterwarnings("ignore", message=".*non-interactive.*")

BLUE, ORANGE, GREEN, PINK, YELLOW, SKY = COLORS[:6]
RED = "#C62828"
GREY = "#777777"
NOTE = "#5A5A5A"


def line(ax, pts, color=INK, lw=1.1, ls="-", arrow_end=False, both=False, zorder=2):
    """Poly-line through pts with optional arrow head(s) on the last segment."""
    xs, ys = zip(*pts)
    if not arrow_end and not both:
        ax.plot(xs, ys, color=color, lw=lw, ls=ls, solid_capstyle="butt", zorder=zorder)
        return
    if len(pts) > 2:
        ax.plot(xs[:-1], ys[:-1], color=color, lw=lw, ls=ls, zorder=zorder)
    ax.annotate("", xy=pts[-1], xytext=pts[-2],
                arrowprops=dict(arrowstyle="<|-|>" if both else "-|>", color=color, lw=lw,
                                ls=ls, shrinkA=0, shrinkB=0, mutation_scale=10), zorder=zorder)


def port(ax, x, y, text, direction="out", fs=7.0, align="left"):
    """Hierarchical-sheet port flag; (x, y) is the end touching the wire."""
    w, h = 0.27 * len(text) + 0.5, 0.62
    if align == "right":   # flag extends to the left of x
        x = x - w - 0.3
    if direction == "out":
        pts = [(x, y - h / 2), (x + w, y - h / 2), (x + w + 0.3, y), (x + w, y + h / 2), (x, y + h / 2)]
    else:  # bidirectional
        pts = [(x, y), (x + 0.3, y - h / 2), (x + w, y - h / 2), (x + w + 0.3, y),
               (x + w, y + h / 2), (x + 0.3, y + h / 2)]
    ax.add_patch(Polygon(pts, closed=True, fc="#F4F4F4", ec=INK, lw=0.9, zorder=3))
    ax.text(x + (w + 0.3) / 2, y, text, ha="center", va="center", fontsize=fs, family="monospace",
            zorder=4)


# ----------------------------------------------------------------------------
# Figure 5.1 — PM-4 rev B channel sheet
# ----------------------------------------------------------------------------
def fig_5_1():
    fig, ax = plt.subplots(figsize=(6.8, 5.0))
    d = schemdraw.Drawing(canvas=ax, show=False)
    d.config(fontsize=7.5, lw=1.0)

    yS = 11.6            # shunt (power) line
    xP, xN = 3.0, 8.6    # Kelvin tap columns (IN+ / IN-)
    xVB = 0.6            # VBUS pin column
    xVS = 11.0           # VS pin column
    yB = 9.0             # R9 branch node
    yC = 5.0             # C3 node
    ub, ut = -1.2, 3.0   # U1 box bottom / top
    ul, ur = -0.6, 12.4  # U1 box left / right

    # --- power path J1 -> R1 -> J2
    d.add(elm.Line().endpoints((-2.0, yS), (xP, yS)))
    d.add(elm.Resistor().endpoints((xP, yS), (xN, yS)))
    d.add(elm.Line().endpoints((xN, yS), (xN + 4.6, yS)))
    # --- sense P (net tie drawn separately)
    d.add(elm.Line().endpoints((xP, yS), (xP, yB)))
    d.add(elm.Dot().at((xP, yB)))
    d.add(elm.Resistor().endpoints((xP, yB), (xP, yC)))
    d.add(elm.Dot().at((xP, yC)))
    d.add(elm.Line().endpoints((xP, yC), (xP, ut)))
    # --- VBUS via R9
    d.add(elm.Line().endpoints((xP, yB), (xVB, yB)))
    d.add(elm.Resistor().endpoints((xVB, yB), (xVB, ut)))
    # --- sense N
    d.add(elm.Line().endpoints((xN, yS), (xN, yB)))
    d.add(elm.Resistor().endpoints((xN, yB), (xN, yC)))
    d.add(elm.Dot().at((xN, yC)))
    d.add(elm.Line().endpoints((xN, yC), (xN, ut)))
    # --- C3 differential
    d.add(elm.Capacitor().endpoints((xP, yC), (xN, yC)))
    # --- VS and C4
    d.add(elm.Vdd().at((xVS, 7.4)))
    d.add(elm.Line().endpoints((xVS, 7.4), (xVS, ut)))
    d.add(elm.Dot().at((xVS, 5.8)))
    d.add(elm.Line().endpoints((xVS, 5.8), (xVS + 1.8, 5.8)))
    d.add(elm.Capacitor().endpoints((xVS + 1.8, 5.8), (xVS + 1.8, 3.8)))
    d.add(elm.Ground().at((xVS + 1.8, 3.8)))
    # --- GND, A0, A1 at the bottom
    xg, xa0, xa1 = 1.6, 4.4, 6.4
    for x in (xg, xa0, xa1):
        d.add(elm.Line().endpoints((x, ub), (x, ub - 1.0)))
    d.add(elm.Line().endpoints((xa0, ub - 1.0), (xa1, ub - 1.0)))
    d.add(elm.Dot().at((5.4, ub - 1.0)))
    d.add(elm.Ground().at((xg, ub - 1.0)))
    d.add(elm.Ground().at((5.4, ub - 1.0)))
    # --- right side pins
    pins_r = [("SDA", 2.1), ("SCL", 0.9), ("ALERT", -0.3)]
    for name, y in pins_r:
        d.add(elm.Line().endpoints((ur, y), (ur + 1.2, y)))
    d.draw()
    for ln in ax.lines:          # close hairline gaps where wire segments meet
        ln.set_solid_capstyle("round")
        ln.set_solid_joinstyle("round")

    # U1 body and pin names
    ax.add_patch(Rectangle((ul, ub), ur - ul, ut - ub, fc="#EEF3F8", ec=INK, lw=1.2, zorder=1))
    ax.text(5.9, 0.75, "U1  INA228\n20-bit power monitor", ha="center", va="center", fontsize=8,
            weight="bold", zorder=4)
    for x, n in [(xVB, "VBUS"), (xP, "IN+"), (xN, "IN−"), (xVS, "VS")]:
        ax.text(x, ut - 0.15, n, ha="center", va="top", fontsize=7, zorder=4)
    for x, n in [(xg, "GND"), (xa0, "A0"), (xa1, "A1")]:
        ax.text(x, ub + 0.15, n, ha="center", va="bottom", fontsize=7, zorder=4)
    for n, y in pins_r:
        ax.text(ur - 0.15, y, n, ha="right", va="center", fontsize=7, zorder=4)

    # ports
    port(ax, ur + 1.2, 2.1, "I2C_SDA", "bi")
    port(ax, ur + 1.2, 0.9, "I2C_SCL", "bi")
    port(ax, ur + 1.2, -0.3, "CH1_ALERT", "out")
    ax.text(ur + 1.3, -0.95, "open-drain;\npull-up on top sheet", fontsize=6.5, color=NOTE,
            ha="left", va="top", style="italic")

    # power-path terminals and labels
    port(ax, -2.0, yS, "V12_BUS", "bi", align="right")
    ax.plot([-2.0], [yS], "o", ms=5, mfc="white", mec=INK, zorder=5)
    ax.text(-2.0, yS + 0.4, "J1-1", fontsize=7, ha="center", va="bottom")
    ax.plot([xN + 4.6], [yS], "o", ms=5, mfc="white", mec=INK, zorder=5)
    ax.text(xN + 4.6, yS + 0.4, "J2-1 (load)", fontsize=7, ha="center", va="bottom")
    ax.text((xP + xN) / 2, yS + 0.65, "R1  2 mΩ 1 % 50 ppm/°C 3 W 2512", ha="center", va="bottom",
            fontsize=7.2)
    for x in (xP, xN):
        ax.plot([x], [yS], "o", ms=3.5, color=INK, zorder=5)
    # net ties: bow-tie on each sense tap, just below the shunt pad
    for x, n, side in [(xP, "NT1", -1), (xN, "NT2", 1)]:
        yt = yS - 0.75
        ax.add_patch(Polygon([(x - 0.3, yt + 0.25), (x + 0.3, yt + 0.25), (x, yt)], closed=True,
                             fc=INK, ec=INK, zorder=5))
        ax.add_patch(Polygon([(x - 0.3, yt - 0.25), (x + 0.3, yt - 0.25), (x, yt)], closed=True,
                             fc=INK, ec=INK, zorder=5))
        ax.text(x + side * 0.45, yt, n, fontsize=6.8, ha="left" if side > 0 else "right", va="center")
    # TP13 Kelvin pads on R1 body
    for x in (xP + 1.1, xN - 1.1):
        ax.plot([x], [yS - 0.45], "s", ms=4, mfc="white", mec=INK, zorder=5)
    ax.text((xP + xN) / 2, yS - 0.7, "TP13 Kelvin pads", fontsize=6.5, ha="center", va="top")
    # Kelvin note
    ax.text(-5.3, 14.0, "Kelvin: sense taps at resistive\nelement, see D-004 §3",
            fontsize=7, color=RED, ha="left", va="center", style="italic",
            bbox=dict(boxstyle="round,pad=0.25", fc="#FFF5F5", ec=RED, lw=0.8))
    line(ax, [(0.9, 13.5), (xP - 0.35, yS - 0.6)], color=RED, lw=0.8, arrow_end=True)
    # sense nets and test points
    for x, net, tp in [(xP, "CH1_SENSE_P", "TP11"), (xN, "CH1_SENSE_N", "TP12")]:
        ax.text(x + 0.2, 9.8, net, fontsize=6.5, family="monospace", ha="left", va="center")
        ax.plot([x, x + 0.5], [9.0, 9.0], color=INK, lw=0.9)
        ax.plot([x], [9.0], "o", ms=3.5, color=INK, zorder=5)
        ax.plot([x + 0.65], [9.0], "o", ms=5, mfc="white", mec=INK, zorder=5)
        ax.text(x + 1.0, 9.0, tp, fontsize=6.5, va="center")
    # component labels
    ax.text(xP + 0.55, 7.0, "R5\n10 Ω 0.1 %", fontsize=7, va="center")
    ax.text(xN + 0.55, 7.0, "R6\n10 Ω 0.1 %", fontsize=7, va="center")
    ax.text(xVB - 0.55, 6.0, "R9\n0 Ω", fontsize=7, va="center", ha="right")
    ax.text((xP + xN) / 2, yC + 0.55, "C3 100 nF C0G", fontsize=7, ha="center", va="bottom")
    ax.text(xVS + 0.35, 7.55, "+3V3", fontsize=7, ha="left", va="center")
    ax.text(xVS + 2.3, 4.8, "C4\n100 nF X7R", fontsize=7, va="center")
    ax.text(xVS + 2.3, 4.0, "place within 3 mm of U1", fontsize=6.5, color=RED, style="italic",
            ha="left", va="top")
    ax.text(6.0, ub - 1.85, "A1 = A0 = GND → 0x40 (CH1)", fontsize=6.8, va="center", ha="left",
            color=NOTE)

    # address table
    tx, ty = -5.5, -0.2
    rows = [("Ch", "A1", "A0", "addr"), ("1", "GND", "GND", "0x40"), ("2", "GND", "VS", "0x41"),
            ("3", "GND", "SDA", "0x42"), ("4", "GND", "SCL", "0x43")]
    cw = [0.75, 1.3, 1.3, 1.4]
    rh = 0.68
    for i, r in enumerate(rows):
        x = tx
        for j, c in enumerate(r):
            ax.add_patch(Rectangle((x, ty - i * rh), cw[j], rh, fc="#EEEEEE" if i == 0 else "white",
                                   ec=INK, lw=0.6))
            ax.text(x + cw[j] / 2, ty - i * rh + rh / 2, c, fontsize=6.3, ha="center", va="center",
                    weight="bold" if i == 0 else None)
            x += cw[j]
    ax.text(tx, ty + rh + 0.2, "Address straps\nper instance", fontsize=6.8, va="bottom")

    # title block
    bx, by, bw, bh = 8.0, -6.1, 10.5, 2.0
    ax.add_patch(Rectangle((bx, by), bw, bh, fc="white", ec=INK, lw=1.0))
    ax.plot([bx, bx + bw], [by + bh / 2, by + bh / 2], color=INK, lw=0.6)
    ax.plot([bx + 3.6, bx + 3.6], [by, by + bh], color=INK, lw=0.6)
    ax.plot([bx + 7.0, bx + 7.0], [by, by + bh / 2], color=INK, lw=0.6)
    ax.text(bx + 0.2, by + 0.75 * bh, "PM4-SCH", fontsize=8, weight="bold", va="center")
    ax.text(bx + 3.8, by + 0.75 * bh, "Channel sheet (1 of 4 instances)", fontsize=7, va="center")
    ax.text(bx + 0.2, by + 0.25 * bh, "Rev B", fontsize=7.5, va="center", weight="bold")
    ax.text(bx + 3.8, by + 0.25 * bh, "ECO-0012", fontsize=7, va="center")
    ax.text(bx + 7.2, by + 0.25 * bh, "Sheet 3 of 6", fontsize=7, va="center")

    ax.set_xlim(-5.6, 18.7)
    ax.set_ylim(-6.3, 14.9)
    ax.set_aspect("equal")
    ax.axis("off")
    save(fig, "05", "fig-5-1-channel-schematic")


# ----------------------------------------------------------------------------
# Figure 5.2 — PM-4 block diagram
# ----------------------------------------------------------------------------
def fig_5_2():
    fig, ax = schematic(6.8, 5.0, xlim=(0, 18.2), ylim=(0, 12.5))
    E = "#B71C1C"   # energy flow
    tag = dict(fontsize=6.6, color=NOTE, style="italic")

    def blk(x, y, w, h, title, sub, ref, fc):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.15",
                                    fc=fc, ec=INK, lw=1.0, zorder=2))
        ax.text(x + w / 2, y + h - 0.3, title, ha="center", va="top", fontsize=8, weight="bold", zorder=3)
        if sub:
            ax.text(x + w / 2, y + h - 0.85, sub, ha="center", va="top", fontsize=7, zorder=3,
                    linespacing=1.25)
        ax.text(x + w - 0.12, y + 0.12, ref, ha="right", va="bottom", zorder=3, **tag)

    # blocks
    blk(0.2, 7.6, 2.8, 2.4, "Input J1", "12 V bus\n10.8–13.2 V", "sheet 2", "#F6E9E9")
    # channels stack
    for k in range(3, -1, -1):
        ax.add_patch(FancyBboxPatch((4.4 + 0.18 * k, 7.6 + 0.18 * k), 4.2, 2.4,
                                    boxstyle="round,pad=0.02,rounding_size=0.15",
                                    fc="#EAF2EA", ec=INK, lw=0.9, zorder=2))
    ax.text(6.5, 9.6, "Channel 1–4", ha="center", va="top", fontsize=8, weight="bold", zorder=3)
    ax.text(6.5, 9.05, "shunt 2 mΩ + INA228\n(four instances)", ha="center", va="top", fontsize=7,
            zorder=3)
    ax.text(8.5, 7.72, "sheet 3", ha="right", va="bottom", zorder=3, **tag)
    blk(13.4, 7.6, 3.4, 2.4, "Outputs J2", "4 × 10 A\nto servers", "sheet 2", "#F6E9E9")
    blk(0.2, 2.9, 3.6, 3.4, "Power", "buck 4.5–36 V\n→ 3.3 V\n47 µF hold-up\nbrown-out\ncomparator",
        "sheet 2", "#FFF4E0")
    # MCU with firmware modules
    ax.add_patch(FancyBboxPatch((5.0, 2.0), 5.4, 4.3, boxstyle="round,pad=0.02,rounding_size=0.15",
                                fc="#EEF3F8", ec=INK, lw=1.0, zorder=2))
    ax.text(7.7, 6.0, "MCU STM32G071", ha="center", va="top", fontsize=8, weight="bold", zorder=3)
    mods = ["drv_ina228", "energy_acc", "modbus_rtu", "cal_store", "alarm"]
    for i, m in enumerate(mods):
        yy = 5.2 - i * 0.6
        ax.add_patch(Rectangle((5.6, yy - 0.25), 4.2, 0.5, fc="white", ec=GREY, lw=0.6, zorder=3))
        ax.text(7.7, yy, m, ha="center", va="center", fontsize=7, family="monospace", zorder=4)
    ax.text(10.28, 2.12, "sheet 4", ha="right", va="bottom", zorder=3, **tag)
    blk(5.6, 0.0, 3.4, 1.2, "FRAM 16 kbit", "", "sheet 4", "#F3EDF7")
    blk(12.6, 1.6, 4.2, 3.6, "Interface", "RS-485 transceiver\nESD protection\nUSB-C service",
        "sheet 5", "#E9F4F8")

    # energy flows (thick)
    line(ax, [(3.0, 8.9), (4.4, 8.9)], color=E, lw=3.0, arrow_end=True)
    ax.text(3.7, 9.3, "40 A max", ha="center", va="bottom", fontsize=6.8, color=E)
    line(ax, [(9.15, 8.9), (13.4, 8.9)], color=E, lw=3.0, arrow_end=True)
    ax.text(11.1, 9.05, "4 × 10 A", ha="center", va="bottom", fontsize=6.8, color=E)
    line(ax, [(1.5, 7.6), (1.5, 6.3)], color=E, lw=3.0, arrow_end=True)
    line(ax, [(3.8, 3.4), (5.0, 3.4)], color=E, lw=3.0, arrow_end=True)
    ax.text(4.4, 3.25, "3V3\n60 mA", ha="center", va="top", fontsize=6.5, color=E)

    # data flows (thin solid)
    line(ax, [(6.0, 7.6), (6.0, 6.3)], both=True)
    ax.text(5.85, 6.95, "I²C 400 kHz\n0x40–0x43", ha="right", va="center", fontsize=6.6)
    line(ax, [(7.2, 2.0), (7.2, 1.2)], both=True)
    ax.text(7.4, 1.6, "I²C 0x50", ha="left", va="center", fontsize=6.6)
    line(ax, [(10.4, 3.9), (12.6, 3.9)], both=True)
    ax.text(11.5, 4.0, "UART\n19.2 kbaud", ha="center", va="bottom", fontsize=6.6)
    line(ax, [(16.8, 3.4), (18.1, 3.4)], both=True)
    ax.text(17.45, 3.55, "bus", ha="center", va="bottom", fontsize=6.6)
    ax.text(14.7, 1.45, "RS-485 Modbus RTU 8E1\nregister map PM4-ICD rev C", ha="center", va="top",
            fontsize=6.6)
    # control (dashed)
    line(ax, [(7.6, 7.6), (7.6, 6.3)], ls=(0, (3, 2)), arrow_end=True)
    ax.text(7.75, 6.95, "ALERT ×4", ha="left", va="center", fontsize=6.6)
    line(ax, [(2.0, 2.9), (2.0, 2.4), (5.0, 2.4)], ls=(0, (3, 2)), arrow_end=True)
    ax.text(2.2, 2.25, "brown-out IRQ", ha="left", va="top", fontsize=6.6)

    # legend
    lx, ly = 0.2, 11.6
    line(ax, [(lx, ly), (lx + 1.0, ly)], color=E, lw=3.0)
    ax.text(lx + 1.2, ly, "energy", va="center", fontsize=7)
    line(ax, [(lx + 3.0, ly), (lx + 4.0, ly)])
    ax.text(lx + 4.2, ly, "data", va="center", fontsize=7)
    line(ax, [(lx + 5.6, ly), (lx + 6.6, ly)], ls=(0, (3, 2)))
    ax.text(lx + 6.8, ly, "control", va="center", fontsize=7)
    # title block corner
    ax.add_patch(Rectangle((13.4, 11.0), 3.4, 1.2, fc="white", ec=INK, lw=1.0))
    ax.text(15.1, 11.6, "PM4-BD  rev B", ha="center", va="center", fontsize=8, weight="bold")
    save(fig, "05", "fig-5-2-pm4-block-diagram")


# ----------------------------------------------------------------------------
# Figure 5.3 — rack wiring diagram
# ----------------------------------------------------------------------------
def fig_5_3():
    fig, ax = schematic(6.8, 5.0, xlim=(0, 20), ylim=(-4.4, 14.0))
    ax.set_aspect("auto")
    REDW, BLKW, GY = "#D32F2F", "#222222", "#2E7D32"

    # busbar (two horizontal bars)
    ax.add_patch(Rectangle((0.2, 11.55), 2.2, 0.5, fc="#C9A227", ec=INK, lw=0.8))
    ax.add_patch(Rectangle((0.2, 10.75), 2.2, 0.5, fc="#9E9E9E", ec=INK, lw=0.8))
    ax.text(1.3, 11.8, "+12 V", ha="center", va="center", fontsize=6.8)
    ax.text(1.3, 11.0, "0 V", ha="center", va="center", fontsize=6.8)
    ax.text(1.3, 10.5, "rack 12 V busbar", ha="center", va="top", fontsize=7)
    # fuse on + tap
    ax.add_patch(Rectangle((2.8, 11.55), 1.0, 0.5, fc="white", ec=INK, lw=0.9))
    ax.plot([2.8, 3.8], [11.8, 11.8], color=INK, lw=0.8)
    ax.text(3.3, 12.2, "fused tap 40 A", ha="center", va="bottom", fontsize=6.8)
    line(ax, [(2.4, 11.8), (2.8, 11.8)], color=REDW, lw=2.2)

    # PM-4 outline
    px, py, pw, ph = 6.0, 3.0, 4.0, 9.8
    ax.add_patch(Rectangle((px, py), pw, ph, fc="#F5F7FA", ec=INK, lw=1.2, ls=(0, (5, 2))))
    ax.text(px, py + ph + 0.15, "=R03+U12-PM4.1", ha="left", va="bottom", fontsize=7.2,
            family="monospace", weight="bold")

    def term(x, y, label, side="L"):
        ax.add_patch(Rectangle((x - 0.25, y - 0.22), 0.5, 0.44, fc="white", ec=INK, lw=0.8, zorder=3))
        ax.text(x + (0.4 if side == "L" else -0.4), y, label, fontsize=6.3, va="center",
                ha="left" if side == "L" else "right", zorder=3)

    # J1 on left side
    ax.text(px + 0.25, 12.35, "J1", fontsize=7, weight="bold", va="center")
    term(px, 11.8, "1 (+)")
    term(px, 11.0, "2 (−)")
    line(ax, [(3.8, 11.8), (px - 0.25, 11.8)], color=REDW, lw=2.2)
    line(ax, [(2.4, 11.0), (px - 0.25, 11.0)], color=BLKW, lw=2.2)
    ax.text(4.3, 10.8, "W1 AWG 10", ha="center", va="top", fontsize=6.6)

    # J2 on right side, 8 positions
    ax.text(px + pw - 0.25, 12.35, "J2", fontsize=7, weight="bold", va="center", ha="right")
    ys = [11.8 - 0.62 * i for i in range(8)]
    names = ["CH1+", "CH1−", "CH2+", "CH2−", "CH3+", "CH3−", "CH4+", "CH4−"]
    for i, (y, n) in enumerate(zip(ys, names)):
        term(px + pw, y, f"{i + 1} {n}", side="R")
    # servers
    for k in range(4):
        yp, ym = ys[2 * k], ys[2 * k + 1]
        sx, sy = 14.3, (yp + ym) / 2
        ax.add_patch(Rectangle((sx, ym - 0.3), 2.2, yp - ym + 0.6, fc="#EEF3F8", ec=INK, lw=0.9))
        ax.text(sx + 1.1, sy, f"Server {k + 1}\nPSU in", ha="center", va="center", fontsize=6.3)
        line(ax, [(px + pw + 0.25, yp), (sx, yp)], color=REDW, lw=1.6)
        line(ax, [(px + pw + 0.25, ym), (sx, ym)], color=BLKW, lw=1.6)
        ax.text(12.15, yp + 0.08, f"W{k + 2}", ha="center", va="bottom", fontsize=6.3)
    ax.text(10.6, 13.0, "W2–W5: AWG 14, max 1.4 m (D-007)", ha="left", va="center", fontsize=6.6)

    # J3 RS-485 bottom
    ax.text(px + 0.1, py + 0.55, "J3", fontsize=7, weight="bold", va="center", ha="left")
    j3 = ["A", "B", "GND", "SH"]
    jx = [px + 1.1 + 0.85 * i for i in range(4)]
    for x, n in zip(jx, j3):
        ax.add_patch(Rectangle((x - 0.22, py - 0.22), 0.44, 0.44, fc="white", ec=INK, lw=0.8, zorder=3))
        ax.text(x, py + 0.35, n, fontsize=6.2, ha="center", va="bottom")
    # cable to next PM-4
    ny = 1.3
    for x in jx:
        line(ax, [(x, py - 0.22), (x, ny + 0.3)], color=PINK if x != jx[3] else GREY, lw=1.1)
    ax.add_patch(Rectangle((px + 0.75, ny - 0.4), 0.85 * 3 + 0.7, 0.7, fc="none", ec=GREY,
                           lw=0.9, ls=(0, (3, 2))))
    line(ax, [(px + 0.75 + 0.85 * 3 + 0.7, ny), (13.6, ny)], color=PINK, lw=2.0)
    ax.text(11.65, ny + 0.2, "twisted pair 120 Ω,\nshielded", ha="center", va="bottom", fontsize=6.4)
    ax.text(11.65, ny - 0.3, "at master: bias 680 Ω\n(A to +3V3, B to GND)", ha="center", va="top",
            fontsize=6.2, color=NOTE)
    ax.add_patch(Rectangle((13.6, 0.3), 3.6, 1.8, fc="#F5F7FA", ec=INK, lw=1.0, ls=(0, (5, 2))))
    ax.text(15.4, 1.55, "next PM-4  J3", ha="center", va="center", fontsize=6.8)
    ax.text(15.4, 0.85, "last unit: 120 Ω\nterminator A–B", ha="center", va="center", fontsize=6.0)
    ax.text(px + 0.3, ny, "shield bonded\nthis end only", ha="right", va="center", fontsize=6.2,
            color=NOTE)

    # DIN rail and PE
    ax.add_patch(Rectangle((px - 0.4, 3.9), pw + 0.8, 0.35, fc="#BDBDBD", ec=INK, lw=0.6))
    ax.text(px + pw / 2, 4.07, "DIN rail", fontsize=6.2, ha="center", va="center")
    line(ax, [(px - 0.4, 4.07), (3.4, 4.07), (3.4, 3.2)], color=GY, lw=2.0)
    for i, w in enumerate((0.9, 0.6, 0.3)):
        ax.plot([3.4 - w / 2, 3.4 + w / 2], [3.2 - 0.18 * i, 3.2 - 0.18 * i], color=INK, lw=1.2)
    ax.text(2.8, 3.0, "rack PE", ha="right", va="center", fontsize=6.6)
    ax.text(4.5, 4.25, "6 mm² GN/YE", ha="center", va="bottom", fontsize=6.4, color=GY)

    # wire table inset
    tx, ty = 0.2, -0.75
    hdr = ["Wire", "From", "To", "Size", "Col.", "L", "Ferrule"]
    data = [["W1", "BUS F1", "J1-1/2", "AWG 10", "RD/BK", "site", "6 mm²"],
            ["W2", "J2-1/2", "SRV1", "AWG 14", "RD/BK", "1.4 m", "2.5 mm²"],
            ["W3", "J2-3/4", "SRV2", "AWG 14", "RD/BK", "1.4 m", "2.5 mm²"],
            ["W4", "J2-5/6", "SRV3", "AWG 14", "RD/BK", "1.4 m", "2.5 mm²"],
            ["W5", "J2-7/8", "SRV4", "AWG 14", "RD/BK", "1.4 m", "2.5 mm²"]]
    cw = [1.4, 2.6, 2.6, 2.4, 2.4, 2.0, 2.4]
    rh = 0.56
    x0 = 0.3
    ax.text(x0, ty + 0.15, "Wire table", fontsize=6.8,
            va="bottom", weight="bold")
    for i, r in enumerate([hdr] + data):
        x = x0
        for j, c in enumerate(r):
            ax.add_patch(Rectangle((x, ty - (i + 1) * rh), cw[j], rh,
                                   fc="#EEEEEE" if i == 0 else "white", ec=INK, lw=0.5))
            ax.text(x + cw[j] / 2, ty - (i + 0.5) * rh, c, fontsize=6.2, ha="center", va="center",
                    weight="bold" if i == 0 else None)
            x += cw[j]
    ax.text(x0 + sum(cw) + 0.3, ty - 1.5 * rh, "IEC 81346 terminal ID\ne.g. server 1 feed (+):",
            fontsize=6.2, va="top")
    ax.text(x0 + sum(cw) + 0.3, ty - 3.2 * rh, "=R03+U12-PM4.1:J2-1", fontsize=5.8, va="top",
            family="monospace")
    save(fig, "05", "fig-5-3-rack-wiring-diagram")


# ----------------------------------------------------------------------------
# Figure 5.4 — feed voltage drop versus length (calculation D-007)
# ----------------------------------------------------------------------------
def fig_5_4():
    I = 10.0                                    # A per output
    rho = 0.0172 * (1 + 0.00393 * 40)           # ohm mm^2/m at 60 C
    fixed = 30.0 + 4 * 1.0 * I                  # mV: PM-4 insertion + 4 contacts x 1 mOhm
    budget = 0.03 * 12_000                      # mV
    sizes = [("AWG 18", 0.823), ("AWG 16", 1.31), ("AWG 14", 2.08), ("AWG 12", 3.31)]
    L = np.linspace(0, 2.5, 200)
    fig, ax = new_fig(6.4, 3.9)
    cols = [PINK, ORANGE, BLUE, GREEN]
    for (name, A), c in zip(sizes, cols):
        slope = 2 * I * rho / A * 1e3          # mV per metre of one-way length
        drop = fixed + slope * L
        lw = 2.4 if name == "AWG 14" else 1.6
        ax.plot(L, drop, color=c, lw=lw)
        lmax = (budget - fixed) / slope
        ax.plot([lmax], [budget], "o", ms=3.5, color=c, zorder=4)
        lab = f"{name} ({A:.2f} mm²), {slope:.1f} mV/m"
        if name == "AWG 18":
            ax.text(1.0, fixed + slope * 1.0 + 15, lab, color=c, fontsize=7.5, ha="right", va="bottom")
        elif name == "AWG 16":
            ax.text(2.47, fixed + slope * 2.47 + 12, lab, color=c, fontsize=7.5, ha="right", va="bottom")
        elif name == "AWG 14":
            ax.text(2.45, fixed + slope * 2.45 + 18, lab, color=c, fontsize=7.5, ha="right", va="bottom")
        else:
            ax.text(2.48, 235, lab + "\nexceeds 2.5 mm² terminal capacity",
                    color=c, fontsize=7.5, ha="right", va="top")
    # AWG 12 excluded: hatched band along its line
    s12 = 2 * I * rho / 3.31 * 1e3
    ax.fill_between(L, fixed + s12 * L - 14, fixed + s12 * L + 14, facecolor="none",
                    edgecolor="#999999", hatch="////", lw=0.0)
    ax.axhline(budget, color=RED, ls="--", lw=1.1)
    ax.text(0.03, budget + 12, "3 % budget = 360 mV", color=RED, fontsize=8, va="bottom")
    ax.axvline(1.4, color=INK, ls=":", lw=1.1)
    ax.text(1.37, 885, "specified\nmaximum length\n1.4 m", fontsize=7.5, va="top", ha="right")
    d14 = fixed + 2 * I * rho / 2.08 * 1e3 * 1.4
    ax.plot([1.4], [d14], "s", ms=6, color=BLUE, zorder=5)
    ax.annotate(f"{d14:.0f} mV: {100 * (budget - d14) / budget:.0f} % margin", xy=(1.4, d14),
                xytext=(0.45, 22), fontsize=8, color=BLUE,
                arrowprops=dict(arrowstyle="-", color=BLUE, lw=0.8))
    ax.axhline(fixed, color=GREY, lw=0.8, ls="-.")
    ax.text(2.48, fixed - 8, "70 mV fixed (PM-4 30 mV + contacts 40 mV)", fontsize=7, color=GREY,
            ha="right", va="top")
    ax.set_xlim(0, 2.5)
    ax.set_ylim(0, 900)
    ax.set_xlabel("One-way cable length (m)")
    ax.set_ylabel("Total drop, busbar to server (mV)")
    ax.set_title("10 A per output, copper at 60 °C", fontsize=9, loc="left")
    ax.grid(True, lw=0.5)
    save(fig, "05", "fig-5-4-feed-voltage-drop")


# ----------------------------------------------------------------------------
# Figure 5.5 — BOM cost breakdown
# ----------------------------------------------------------------------------
def fig_5_5():
    # roll-up from the chapter's BOM with attrition (210: 2 %, 900: 5 %, others 1 %)
    bom = [("310", 4, 3.10, 2.35, "sem"), ("210", 4, 0.62, 0.38, "shu"), ("320", 1, 1.95, 1.42, "sem"),
           ("330", 1, 1.05, 0.78, "sem"), ("340", 1, 0.82, 0.58, "sem"), ("350", 1, 1.60, 1.18, "sem"),
           ("410", 2, 1.90, 1.45, "con"), ("410", 1, 0.70, 0.48, "con"), ("900", 1, 1.80, 1.10, "pas"),
           ("600", 1, 6.50, 1.85, "pcb"), ("610", 1, 3.40, 2.30, "enc"), ("700", 1, 9.00, 3.20, "asm"),
           ("700", 1, 4.00, 1.40, "asm")]
    attr = {"210": 0.02, "900": 0.05}
    cats = [("sem", "Semiconductors (INA228 ×4, MCU,\nRS-485, buck, FRAM)"), ("shu", "Shunts"),
            ("con", "Connectors"), ("pas", "Passives and TVS"), ("pcb", "PCB"), ("enc", "Enclosure"),
            ("asm", "Assembly and test")]
    tot = {k: [0.0, 0.0] for k, _ in cats}
    for ipn, q, c100, c1k, k in bom:
        f = 1 + attr.get(ipn, 0.01)
        tot[k][0] += q * c100 * f
        tot[k][1] += q * c1k * f
    cols = [BLUE, PINK, ORANGE, SKY, GREEN, "#999999", "#7B5EA7"]
    fig, ax = new_fig(6.4, 4.2)
    xs = [0, 1]
    bottoms = [0.0, 0.0]
    for (k, name), c in zip(cats, cols):
        v = tot[k]
        ax.bar(xs, v, 0.5, bottom=bottoms, color=c, ec="white", lw=0.8, label=name)
        for i in range(2):
            if v[i] > 1.5:
                ax.text(xs[i], bottoms[i] + v[i] / 2, f"{v[i]:.2f}", ha="center", va="center",
                        fontsize=7.5, color="white" if c not in (SKY, ORANGE) else INK)
            else:
                ax.text(xs[i] + 0.27, bottoms[i] + v[i] / 2, f"{v[i]:.2f}", ha="left", va="center",
                        fontsize=7, color=INK)
        bottoms = [bottoms[0] + v[0], bottoms[1] + v[1]]
    for i in range(2):
        if i == 0:
            ax.text(xs[i], bottoms[i] + 0.8, f"${bottoms[i]:.2f}", ha="center", va="bottom",
                    fontsize=9, weight="bold")
        else:
            ax.text(xs[i] - 0.28, bottoms[i] - 0.3, f"${bottoms[i]:.2f}", ha="right", va="top",
                    fontsize=9, weight="bold")
    ax.plot([-0.45, 1.45], [30, 30], color=RED, ls="--", lw=1.2, zorder=0.5)
    ax.text(0.3, 30.6, "R10 target $30.00\nat 1,000 pcs", color=RED, fontsize=8, va="bottom")
    margin = (30 - bottoms[1]) / 30 * 100
    ax.annotate("", xy=(1.3, 30), xytext=(1.3, bottoms[1]),
                arrowprops=dict(arrowstyle="<->", color=RED, lw=0.9, shrinkA=0, shrinkB=0))
    ax.text(1.33, (30 + bottoms[1]) / 2 - 1.5, f"{margin:.1f} %\nmargin", color=RED, fontsize=7.5,
            va="center")
    ax.set_xticks(xs, ["100 pcs", "1,000 pcs"])
    ax.set_xlim(-0.5, 1.55)
    ax.set_ylim(0, 55)
    ax.set_ylabel("Unit cost (USD), incl. attrition")
    h, lab = ax.get_legend_handles_labels()
    ax.legend(h[::-1], lab[::-1], loc="center left", bbox_to_anchor=(1.0, 0.5), fontsize=7.5)
    save(fig, "05", "fig-5-5-bom-cost-breakdown")


if __name__ == "__main__":
    fig_5_1()
    fig_5_2()
    fig_5_3()
    fig_5_4()
    fig_5_5()
