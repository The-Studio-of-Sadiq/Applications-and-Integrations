"""Figures for Chapter 21 — Industrial Communication and Safety.

Run from the repository root:  python figures/scripts/ch21.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

from figstyle import COLORS, INK, box, save, schematic, new_fig  # noqa: E402

BLUE, ORANGE, GREEN, PINK, YELLOW, SKY = COLORS[:6]
RED = "#C62828"
GREY = "#777777"


def line(ax, pts, color=INK, lw=1.2, ls="-", arrow_end=False, both=False, z=2):
    xs, ys = zip(*pts)
    if not arrow_end and not both:
        ax.plot(xs, ys, color=color, lw=lw, ls=ls, solid_capstyle="butt", zorder=z)
        return
    if len(pts) > 2:
        ax.plot(xs[:-1], ys[:-1], color=color, lw=lw, ls=ls, zorder=z)
    ax.annotate("", xy=pts[-1], xytext=pts[-2],
                arrowprops=dict(arrowstyle="<|-|>" if both else "-|>", color=color, lw=lw,
                                ls=ls, shrinkA=0, shrinkB=0, mutation_scale=10), zorder=z)


def dline(ax, pts, color=RED, z=2):
    """Double line (safety wiring): thick coloured stroke with a white core.

    The core is drawn at a higher z-order than every stroke, so T-junctions merge cleanly."""
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=color, lw=3.6, solid_capstyle="projecting", solid_joinstyle="miter",
            zorder=z)
    ax.plot(xs, ys, color="white", lw=1.4, solid_capstyle="projecting", solid_joinstyle="miter",
            zorder=z + 0.5)


def rbox(ax, x, y, w, h, text="", fc="#EEF3F8", ec=INK, fs=8, lw=1.0, ls="-", z=3,
         weight="normal", ha="center", va="center", tx=None, ty=None):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc=fc, ec=ec, lw=lw, ls=ls, zorder=z))
    if text:
        ax.text(x + w / 2 if tx is None else tx, y + h / 2 if ty is None else ty, text,
                ha=ha, va=va, fontsize=fs, color=INK, zorder=z + 0.5, weight=weight,
                linespacing=1.2)


# ----------------------------------------------------------------------------
# Figure 21.1 — palletiser cell architecture
# ----------------------------------------------------------------------------
def fig_21_1():
    fig, ax = schematic(6.8, 5.6, xlim=(0, 17), ylim=(-0.1, 13.9))
    # Level 3
    rbox(ax, 3.2, 12.2, 10.6, 1.5,
         "Plant operations network (Level 3)\nhistorian  ·  engineering station  ·  jump host",
         fc="#ECECEC", fs=8.3)
    rbox(ax, 5.7, 10.65, 5.6, 0.95, "Cell firewall  (conduit C1)", fc="#FBE3D6", ec=ORANGE,
         fs=8.3, weight="bold")
    line(ax, [(8.5, 12.2), (8.5, 11.6)], lw=1.6)
    # cell zone
    ax.add_patch(FancyBboxPatch((0.15, 0.05), 16.7, 10.2, boxstyle="round,pad=0,rounding_size=0.3",
                                fc="none", ec=GREY, lw=1.0, ls=(0, (5, 3)), zorder=1))
    ax.text(16.6, 9.95, "Cell zone", fontsize=8.5, color=GREY, style="italic", va="top", ha="right")
    # PLC and switch
    rbox(ax, 0.9, 8.05, 4.6, 1.7, "F-PLC (SIL 3 / PL e)\nstandard task 10 ms\nsafety task 20 ms",
         fc="#DCE8F5", fs=7.8, weight="normal")
    rbox(ax, 7.0, 8.25, 4.6, 1.3, "Managed switch SW1\nprio 6 · storm control 1 %",
         fc="#DCE8F5", fs=7.8)
    line(ax, [(8.5, 10.65), (8.5, 9.55)], lw=1.6)
    line(ax, [(5.5, 8.9), (7.0, 8.9)], lw=1.6)
    # device row
    names = ["Remote I/O\nET1", "F-I/O ET2\nF-DI · F-DQ", "VFD1\n7.5 kW", "VFD2\n2.2 kW",
             "VFD3\n2.2 kW", "Gantry\ncontroller", "Compressor\ncontroller"]
    w, g, x0, yd, hd = 2.1, 0.25, 0.6, 5.0, 1.25
    xs = [x0 + i * (w + g) for i in range(7)]
    fcs = ["#EEF3F8", "#FCE4E4", "#EEF3F8", "#EEF3F8", "#EEF3F8", "#E6F4EC", "#FFF4D6"]
    for x, n, fc in zip(xs, names, fcs):
        rbox(ax, x, yd, w, hd, n, fc=fc, fs=7.1)
    # PROFINET star from SW1 via a trunk
    ytr = 7.15
    line(ax, [(9.3, 8.25), (9.3, ytr)], lw=1.6)
    line(ax, [(xs[0] + w / 2, ytr), (xs[5] + w / 2, ytr)], lw=1.6)
    for x in xs[:6]:
        line(ax, [(x + w / 2, ytr), (x + w / 2, yd + hd)], lw=1.6)
    ax.text(9.1, ytr + 0.12, "PROFINET RT, 4 ms update (star from SW1)",
            fontsize=7.3, va="bottom", ha="right")
    # Modbus TCP to compressor (separate SW1 port)
    line(ax, [(11.6, 8.6), (xs[6] + w / 2, 8.6), (xs[6] + w / 2, yd + hd)], lw=1.6, color=ORANGE)
    ax.text(xs[6] + w / 2 - 0.15, 8.75, "Modbus TCP", fontsize=7.3, color=ORANGE, ha="right",
            va="bottom")
    # STO from F-DQ (double lines)
    ysto = 4.45
    dline(ax, [(xs[1] + 1.55, yd), (xs[1] + 1.55, ysto), (xs[4] + w / 2, ysto),
               (xs[4] + w / 2, yd)])
    for x in xs[2:4]:
        dline(ax, [(x + w / 2, ysto), (x + w / 2, yd)])
    ax.text(xs[2] + w / 2 + 1.2, ysto - 0.2, "STO from F-DQ", fontsize=7.3, color=RED, ha="center",
            va="top")
    # safety devices on ET2
    ysd = 3.75
    sd = [("Light curtain\ntype 4, 30 mm\nOSSD1/OSSD2", 0.5, 2.6),
          ("Door switches\nD1, D2 (coded)", 3.3, 2.35),
          ("E-stops\nES1 to ES3", 5.85, 1.75)]
    dline(ax, [(xs[1] + 0.45, yd), (xs[1] + 0.45, ysd)])
    dline(ax, [(sd[0][1] + sd[0][2] / 2, ysd), (sd[2][1] + sd[2][2] / 2, ysd)])
    for txt, x, ww in sd:
        dline(ax, [(x + ww / 2, ysd), (x + ww / 2, 3.15)])
        rbox(ax, x, 1.95, ww, 1.2, txt, fc="#FCE4E4", ec=RED, fs=7.2)
    # CANopen under gantry
    ycan = 3.75
    gx = xs[5] + w / 2
    line(ax, [(gx, yd), (gx, ycan)], ls=(0, (4, 2)), lw=1.5, color=GREEN)
    line(ax, [(10.9, ycan), (16.6, ycan)], ls=(0, (4, 2)), lw=1.5, color=GREEN)
    for xe in (10.9, 16.6):
        ax.add_patch(Rectangle((xe - 0.12, ycan - 0.35), 0.24, 0.7, fc="white", ec=GREEN, lw=1.1,
                               zorder=4))
    ax.text(10.9, ycan + 0.45, "120 Ω", fontsize=6.8, ha="center", color=GREEN)
    ax.text(16.5, ycan + 0.45, "120 Ω", fontsize=6.8, ha="center", color=GREEN)
    for i, ax_name in enumerate("XYZ"):
        cx = 11.6 + i * 1.75
        line(ax, [(cx + 0.75, ycan), (cx + 0.75, 3.15)], ls=(0, (4, 2)), lw=1.5, color=GREEN)
        rbox(ax, cx, 2.35, 1.5, 0.8, f"Servo {ax_name}", fc="#E6F4EC", fs=7.4)
    ax.text(13.75, 2.1, "CANopen 1 Mbit/s, 18 m, terminated both ends", fontsize=7.2,
            ha="center", va="top", color=GREEN)
    # RS-485 meter chain from the PLC
    ym = 0.45
    line(ax, [(0.9, 8.6), (0.32, 8.6), (0.32, ym + 0.4), (0.9, ym + 0.4)], ls=":", lw=1.8,
         color=PINK)
    for i in range(6):
        mx = 0.9 + i * 1.45
        rbox(ax, mx, ym, 1.15, 0.8, f"M{11 + i}", fc="#F7E6F0", fs=7.4)
        if i < 5:
            line(ax, [(mx + 1.15, ym + 0.4), (mx + 1.45, ym + 0.4)], ls=":", lw=1.8, color=PINK)
    ax.text(0.9, ym + 0.95, "RS-485 Modbus RTU, 19,200 baud 8E1, unit IDs 11 to 16",
            fontsize=7.2, color=PINK, ha="left", va="bottom")
    # legend
    lx, ly = 10.75, 0.35
    ax.add_patch(Rectangle((lx - 0.15, ly - 0.2), 6.1, 1.45, fc="white", ec=GREY, lw=0.6, zorder=3))
    items = [("PROFINET", dict(color=INK, lw=1.6)), ("CANopen", dict(color=GREEN, lw=1.5, ls=(0, (4, 2)))),
             ("RS-485", dict(color=PINK, lw=1.8, ls=":")), ("Safety wiring", None)]
    for i, (lab, kw) in enumerate(items):
        xx = lx + (i % 2) * 2.95
        yy = ly + 0.85 - (i // 2) * 0.6
        if kw is None:
            dline(ax, [(xx, yy), (xx + 0.9, yy)], z=4)
        else:
            ax.plot([xx, xx + 0.9], [yy, yy], zorder=4, **kw)
        ax.text(xx + 1.05, yy, lab, fontsize=7.2, va="center", zorder=4)
    save(fig, "21", "fig-21-1-palletiser-cell-architecture")


# ----------------------------------------------------------------------------
# Figure 21.2 — Modbus RTU poll cycle
# ----------------------------------------------------------------------------
def transaction_ms(baud, n_req=8, n_resp=85, turnaround=20.0):
    tc = 11.0 / baud * 1e3                      # 8E1: 11 bits per character
    gap = 3.5 * tc if baud <= 19200 else 1.75   # Modbus: fixed 1.75 ms gap above 19,200 baud
    return (n_req + n_resp) * tc + 2 * gap + turnaround, n_req * tc, gap


def fig_21_2():
    n = np.arange(1, 13)
    fig, ax = new_fig(6.4, 4.0)
    styles = {9600: BLUE, 19200: ORANGE, 38400: GREEN}
    for baud, c in styles.items():
        t, _, _ = transaction_ms(baud)
        ax.plot(n, n * t / 1e3, color=c, marker="o", ms=3.5,
                label=f"{baud:,} baud healthy ({t:.1f} ms/meter)")
    t19, treq, gap = transaction_ms(19200)
    for retries, ls, lab in ((3, "--", "3 retries"), (1, ":", "1 retry")):
        dead = (retries + 1) * (200 + treq + gap)
        y = ((n - 1) * t19 + dead) / 1e3
        ax.plot(n, y, color=ORANGE, ls=ls, lw=1.8,
                label=f"19,200 baud, one dead meter, 200 ms timeout, {lab}")
    ax.axhline(1.0, color=RED, lw=1.2)
    ax.text(0.6, 1.02, "R7 limit, 1 s", color=RED, fontsize=8.3, ha="left", va="bottom")
    ax.axvline(6, color=GREY, lw=0.8, ls=(0, (2, 2)))
    ax.text(6.1, 1.55, "cell: 6 meters", fontsize=8, color=GREY, va="bottom")
    for yv, txt in ((0.464, "0.464 s (healthy)"), (0.800, "0.80 s (1 retry)"), (1.213, "1.21 s (3 retries)")):
        ax.plot(6, yv, "o", color=INK, ms=4, zorder=5)
        if yv < 0.5:
            ax.annotate(txt, xy=(6, yv), xytext=(6.7, 0.13), fontsize=7.8,
                        arrowprops=dict(arrowstyle="-", color=INK, lw=0.7))
        else:
            ax.text(6.15, yv - 0.035, txt, fontsize=7.8, ha="left", va="top")
    ax.set_xlim(0.5, 12.5)
    ax.set_ylim(0, 2.5)
    ax.set_xticks(n)
    ax.set_xlabel("Number of meters on the bus")
    ax.set_ylabel("Poll-cycle time (s)")
    ax.grid(True, axis="y")
    ax.legend(fontsize=7.6, loc="upper left")
    save(fig, "21", "fig-21-2-modbus-poll-cycle")


# ----------------------------------------------------------------------------
# Figure 21.3 — SF1 stopping-performance chain
# ----------------------------------------------------------------------------
def fig_21_3():
    fig, axs = plt.subplots(5, 1, figsize=(6.8, 5.0), sharex=True,
                            gridspec_kw=dict(height_ratios=[2.2, 0.8, 0.8, 0.8, 1.6], hspace=0.18))
    ax = axs[0]
    bars = [("Light curtain OFF\n15 ms", 0, 15, BLUE),
            ("F-DI + PROFINET + F-CPU + PROFIsafe\n(worst case, one fault) 75 ms", 15, 90, ORANGE),
            ("F-DQ + STO\n10 ms", 90, 100, PINK),
            ("Gantry mechanical stop  300 ms", 100, 400, GREEN)]
    for i, (lab, t0, t1, c) in enumerate(bars):
        y = 3 - i
        ax.barh(y, t1 - t0, left=t0, height=0.62, color=c, alpha=0.85, edgecolor=INK, lw=0.6)
        if i == 3:
            ax.text((t0 + t1) / 2, y, lab, ha="center", va="center", fontsize=7.8, color="white",
                    weight="bold")
        else:
            ax.text(t1 + 6, y, lab, ha="left", va="center", fontsize=7.6, linespacing=1.1)
    ax.set_ylim(-0.6, 3.6)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_title("Total stopping performance T = 15 + 75 + 10 + 300 = 400 ms", fontsize=9.5)
    # digital traces
    t = np.linspace(0, 520, 2081)
    traces = [("OSSD1", 15), ("OSSD2", 15), ("STO out", 90)]
    for a, (name, tf) in zip(axs[1:4], traces):
        y = np.where(t < tf, 1.0, 0.0)
        a.plot(t, y, color=RED if name.startswith("STO") else BLUE, lw=1.6, drawstyle="steps-post")
        a.set_ylim(-0.25, 1.35)
        a.set_yticks([0, 1])
        a.set_yticklabels(["0 V", "24 V"], fontsize=7)
        a.set_ylabel(name, rotation=0, ha="right", va="center", fontsize=8.5, labelpad=6)
    axs[3].text(95, 0.55, "drives in safe torque off", fontsize=7.5, color=RED, va="center")
    # speed
    a = axs[4]
    v = np.where(t < 100, 1.2, np.clip(1.2 * (400 - t) / 300, 0, None))
    a.plot(t, v, color=GREEN, lw=1.8)
    a.set_ylim(0, 1.45)
    a.set_yticks([0, 0.6, 1.2])
    a.set_ylabel("Gantry\nspeed\n(m/s)", rotation=0, ha="right", va="center", fontsize=8.5,
                 labelpad=6)
    a.set_xlabel("Time from beam interruption (ms)")
    a.set_xlim(0, 520)
    for k, a2 in enumerate(axs):
        a2.axvline(482.5, color=RED, ls="--", lw=1.1)
        a2.axvline(400, color=GREY, ls=":", lw=0.9)
    axs[0].text(478, 3.35, "max T for 900 mm\n= 482.5 ms", color=RED, fontsize=7.6, ha="right",
                va="center")
    a.annotate("", xy=(482.5, 1.15), xytext=(400, 1.15),
               arrowprops=dict(arrowstyle="<|-|>", color=RED, lw=1.0, mutation_scale=9,
                               shrinkA=0, shrinkB=0))
    a.text(441, 1.2, "margin\n82.5 ms", fontsize=7.6, color=RED, ha="center", va="bottom")
    a.text(260, 0.95, "standstill at 400 ms", fontsize=7.6, color=GREEN)
    save(fig, "21", "fig-21-3-sf1-response-chain")


# ----------------------------------------------------------------------------
# Figure 21.4 — ISO 13855 safety distance
# ----------------------------------------------------------------------------
def s_min(T_s, d):
    C = 8 * (d - 14)
    s1 = 2000 * T_s + C
    s2 = np.maximum(1600 * T_s + C, 500)
    return np.where(s1 <= 500, np.maximum(s1, 100), s2)


def fig_21_4():
    T = np.linspace(0.1, 0.6, 1001)
    fig, ax = new_fig(6.4, 4.0)
    ax.plot(T * 1e3, s_min(T, 14), color=BLUE, label="d = 14 mm (finger)")
    ax.plot(T * 1e3, s_min(T, 30), color=ORANGE, label="d = 30 mm (installed curtain)")
    ax.axhline(900, color=INK, ls="--", lw=1.1)
    ax.text(105, 912, "installed distance 900 mm", fontsize=8.3, va="bottom")
    pts = [(400, 768, "design\nT = 400 ms, S = 768 mm", GREEN, (300, 1010)),
           (482.5, 900, "limit\nT = 482.5 ms", RED, (505, 760)),
           (475, 888, "laser-scanner alternative\nT = 475 ms, S = 888 mm", PINK, (430, 1070))]
    for x, y, lab, c, xyt in pts:
        ax.plot(x, y, "o", color=c, ms=6, zorder=5)
        ax.annotate(lab, xy=(x, y), xytext=xyt, fontsize=7.8, color=c,
                    arrowprops=dict(arrowstyle="-", color=c, lw=0.8))
    ax.text(215, 250, "K = 2000 mm/s\n(while S ≤ 500 mm)", fontsize=7.8, color=GREY)
    ax.text(530, 600, "K = 1600 mm/s", fontsize=7.8, color=GREY, ha="center")
    ax.set_xlim(100, 600)
    ax.set_ylim(0, 1200)
    ax.set_xlabel("Total stopping performance T (ms)")
    ax.set_ylabel("Minimum safety distance S (mm)")
    ax.grid(True)
    ax.legend(loc="lower right", fontsize=8.3)
    save(fig, "21", "fig-21-4-safety-distance")


# ----------------------------------------------------------------------------
# Figure 21.5 — IEC 62443 zones and conduits
# ----------------------------------------------------------------------------
def zone(ax, x, y, w, h, title, fc, ec, fs=8.3):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.25",
                                fc=fc, ec=ec, lw=1.4, zorder=1))
    ax.text(x + 0.2, y + h - 0.15, title, fontsize=fs, weight="bold", va="top", ha="left",
            color=ec, zorder=2)


def fig_21_5():
    fig, ax = schematic(6.8, 5.6, xlim=(0, 17), ylim=(0, 14))
    zone(ax, 3.0, 12.4, 11.0, 1.4, "Z1 Enterprise   SL-T 1", "#F2F2F2", GREY)
    ax.text(8.5, 12.8, "office IT, ERP, internet", fontsize=7.8, ha="center", va="center")
    rbox(ax, 6.6, 11.15, 3.8, 0.8, "C2 · DMZ", fc="#FBE3D6", ec=ORANGE, fs=7.8, weight="bold")
    line(ax, [(8.5, 12.4), (8.5, 11.95)], lw=1.4, both=True)
    zone(ax, 3.0, 8.15, 11.0, 2.55, "Z2 Plant operations   SL-T 2", "#EAF1FA", BLUE)
    line(ax, [(8.5, 11.15), (8.5, 10.7)], lw=1.4, both=True)
    rbox(ax, 3.4, 8.4, 3.0, 1.35, "Historian", fc="white", fs=7.8)
    rbox(ax, 7.0, 8.4, 3.0, 1.35, "Engineering\nstation", fc="white", fs=7.8)
    rbox(ax, 10.6, 8.4, 3.0, 1.35, "Jump host\nMFA, named\naccounts", fc="white", fs=7.4)
    # C1
    rbox(ax, 0.4, 6.0, 12.0, 1.9, "", fc="#FBE3D6", ec=ORANGE)
    ax.text(0.6, 7.72, "C1 · cell firewall: allow-list, default deny",
            fontsize=7.2, va="top", ha="left", weight="bold", zorder=5)
    ax.text(0.6, 7.32, "OPC UA, TCP 4840, read-only role: from historian only\n"
            "S7 engineering, TCP 102: from jump host only, in a maintenance window\n"
            "everything else dropped and logged",
            fontsize=7.2, va="top", ha="left", zorder=5, linespacing=1.3)
    line(ax, [(4.9, 8.4), (4.9, 7.9)], color=BLUE, lw=1.4, arrow_end=True)
    line(ax, [(12.1, 8.4), (12.1, 7.9)], color=BLUE, lw=1.4, arrow_end=True)
    line(ax, [(11.0, 6.0), (11.0, 5.75)], color=BLUE, lw=1.4, arrow_end=True)
    # Z3 with Z4 inside
    zone(ax, 0.3, 0.3, 12.2, 5.45, "Z3 Cell control   SL-T 2", "#EEF6EE", GREEN)
    items = [("F-PLC", 0.6, 3.55), ("HMI", 2.9, 3.55), ("SW1\nmanaged", 5.2, 3.55),
             ("Remote I/O\nET1", 7.5, 3.55), ("VFD1 to 3", 9.8, 3.55),
             ("Gantry +\nCANopen", 0.6, 1.95), ("Compressor\nModbus TCP", 2.9, 1.95)]
    for txt, x, y in items:
        rbox(ax, x, y, 2.15, 1.1, txt, fc="white", fs=7.2)
    ax.text(0.6, 0.95, "Modbus TCP 502 never\nleaves Z3", fontsize=6.9, style="italic",
            color=GREEN, va="center")
    zone(ax, 5.4, 0.55, 6.85, 2.7, "Z4 Safety (inside Z3)", "#FCE4E4", RED, fs=8)
    ax.text(8.82, 1.85, "F-I/O ET2 · light curtain\ndoor switches D1, D2 · E-stops ES1-ES3",
            fontsize=7.3, ha="center", va="center", zorder=3)
    ax.text(8.82, 0.9, "PROFIsafe only (black channel)", fontsize=7.3, ha="center",
            va="center", style="italic", color=RED, zorder=3)
    # Z5
    BR = "#9A6B00"
    zone(ax, 13.0, 0.3, 3.8, 4.4, "Z5 Maintenance\nVLAN", "#FFF4D6", BR, fs=7.8)
    rbox(ax, 13.4, 1.0, 3.0, 1.3, "Laptop port", fc="white", fs=7.8)
    # C3 laptop -> jump host
    line(ax, [(16.1, 2.3), (16.1, 9.07), (13.6, 9.07)], color=BR, lw=1.5, arrow_end=True)
    ax.text(15.95, 6.6, "C3: routed\nonly to\njump host", fontsize=7.3, color=BR,
            ha="right", va="center")
    # removed path laptop -> SW1
    line(ax, [(13.4, 1.65), (12.75, 1.65), (12.75, 5.25), (6.3, 5.25), (6.3, 4.65)], color=GREY,
         lw=1.3, ls=(0, (3, 2)), arrow_end=True, z=5)
    cx, cy = 12.75, 3.0
    ax.plot([cx - 0.3, cx + 0.3], [cy - 0.3, cy + 0.3], color=RED, lw=2.4, zorder=6)
    ax.plot([cx - 0.3, cx + 0.3], [cy + 0.3, cy - 0.3], color=RED, lw=2.4, zorder=6)
    ax.text(12.35, 5.13, "removed: laptop direct to SW1", fontsize=7.2, color=RED,
            ha="right", va="top", weight="bold", zorder=6)
    save(fig, "21", "fig-21-5-zones-and-conduits")



if __name__ == "__main__":
    fig_21_1()
    fig_21_2()
    fig_21_3()
    fig_21_4()
    fig_21_5()
