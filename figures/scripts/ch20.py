"""Figures for Chapter 20 — Industrial Motor Control.

Run from the repository root:  python figures/scripts/ch20.py
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle  # noqa: E402

from figstyle import COLORS, INK, save, schematic  # noqa: E402

BLUE, ORANGE, GREEN, PINK, YELLOW, SKY = COLORS[:6]
RED = "#C62828"
GREY = "#777777"
SAFE = "#D4A000"


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


def rbox(ax, x, y, w, h, fc="#EEF3F8", ec=INK, lw=1.0, ls="-", z=3, r=0.08):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.01,rounding_size={r}",
                                fc=fc, ec=ec, lw=lw, ls=ls, zorder=z))


def lbox(ax, x, y, w, h, text, fc="#EEF3F8", fs=6.0, ec=INK, bold=False, z=3):
    rbox(ax, x, y, w, h, fc=fc, ec=ec, z=z)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, linespacing=1.0,
            weight="bold" if bold else "normal", zorder=z + 1)


def motor(ax, x, y, text, r=0.48):
    ax.add_patch(Circle((x, y), r, fc="white", ec=INK, lw=1.1, zorder=4))
    ax.text(x, y + 0.08, "M", ha="center", va="center", fontsize=7.4, weight="bold", zorder=5)
    ax.text(x, y - 0.24, "3~", ha="center", va="center", fontsize=4.8, zorder=5)
    ax.text(x, y - r - 0.12, text, ha="center", va="top", fontsize=6.0, linespacing=1.0)


def contact(ax, x, y, w=0.36, nc=False, color=INK, lw=1.0, z=4):
    """Horizontal contact symbol centred at (x, y) on a horizontal wire."""
    ax.plot([x - w, x - w / 2], [y, y], color=color, lw=lw, zorder=z)
    ax.plot([x + w / 2, x + w], [y, y], color=color, lw=lw, zorder=z)
    if nc:
        ax.plot([x - w / 2, x + w / 2 + 0.05], [y, y + 0.22], color=color, lw=lw, zorder=z)
        ax.plot([x + w / 2, x + w / 2], [y, y + 0.28], color=color, lw=lw, zorder=z)
    else:
        ax.plot([x - w / 2, x + w / 2], [y, y + 0.22], color=color, lw=lw, zorder=z)


# ----------------------------------------------------------------------------
# Figure 20.1 — MCC single-line diagram
# ----------------------------------------------------------------------------
def fig_20_1():
    fig, ax = schematic(6.8, 5.4, xlim=(0, 17), ylim=(-0.2, 13.3))
    # sources
    tx, gx = 3.2, 7.0
    for dy in (0.0, -0.55):
        ax.add_patch(Circle((tx, 12.6 + dy), 0.42, fc="none", ec=INK, lw=1.1, zorder=3))
    ax.text(tx - 0.6, 12.35, "630 kVA\n11/0.4 kV\nuk 6 %", fontsize=6.2, ha="right", va="center")
    ax.add_patch(Circle((gx, 12.3), 0.5, fc="white", ec=INK, lw=1.1, zorder=3))
    ax.text(gx, 12.3, "G", fontsize=8, ha="center", va="center", weight="bold", zorder=4)
    ax.text(gx + 0.65, 12.3, "400 kVA standby\ngenerator, x″d 0.15", fontsize=6.2, ha="left",
            va="center")
    lbox(ax, 4.1, 10.8, 2.0, 0.6, "changeover", fs=6.2)
    line(ax, [(tx, 11.63), (tx, 11.1), (4.1, 11.1)])
    line(ax, [(gx, 11.8), (gx, 11.1), (6.1, 11.1)])
    line(ax, [(5.1, 10.8), (5.1, 10.4)])
    lbox(ax, 4.45, 9.8, 1.3, 0.6, "incomer\n400 A", fs=5.8)
    yb = 9.3
    line(ax, [(5.1, 9.8), (5.1, yb)])
    ax.plot([0.15, 16.85], [yb, yb], color=INK, lw=4.0, solid_capstyle="butt", zorder=3)
    ax.text(16.85, yb + 0.2, "busbar 400 A, Icw 25 kA for 1 s;\nprospective Ik 15.2 kA (transformer)",
            fontsize=6.2, ha="right", va="bottom")
    ax.text(0.15, yb + 0.2, "MCC 400 V, 50 Hz, TN-S", fontsize=6.4, ha="left", va="bottom",
            weight="bold")
    cols = [1.15, 3.45, 5.75, 8.05, 10.35, 12.65, 14.95]
    w = 1.7
    y1, y2 = 8.2, 7.2      # first and second device rows (box bottoms)
    hb = 0.6
    ym = 3.4               # motor centre

    def dev(x, y, text, fc="#F5F5F5", h=hb, fs=5.8, ww=w):
        lbox(ax, x - ww / 2, y, ww, h, text, fc=fc, fs=fs)

    def wire(x, ya, yb_):
        line(ax, [(x, ya), (x, yb_)], lw=1.0)

    for x in cols:
        wire(x, yb, y1 + hb)
    # F1 feeder: MPCB + VFD
    x = cols[0]
    dev(x, y1, "MPCB")
    wire(x, y1, 7.8)
    dev(x, 6.6, "VFD 7.5 kW", fc=tint(BLUE, "25"), h=1.2, fs=6.0)
    wire(x, 6.6, ym + 0.48)
    motor(ax, x, ym, "F1 feeder\n7.5 kW")
    # C1: fuses + reactor + HD VFD with chopper and resistor
    x = cols[1]
    dev(x, y1, "fuses")
    wire(x, y1, y2 + hb)
    dev(x, y2, "reactor 3 %")
    wire(x, y2, 6.9)
    dev(x, 4.9, "VFD 75 kW\nheavy\nduty,\n+ brake\nchopper", fc=tint(BLUE, "25"), h=2.0, fs=5.6)
    wire(x, 4.9, ym + 0.48)
    motor(ax, x, ym, "C1 incline\n75 kW")
    ax.add_patch(Rectangle((x + 0.55, ym - 0.3), 0.3, 0.55, fc="#DDDDDD", ec=INK, lw=0.8, zorder=4))
    ax.text(x + 0.92, ym + 0.35, "brake", fontsize=5.2, ha="left", va="bottom")
    line(ax, [(x + 0.6, 4.9), (x + 0.6, 4.55)], lw=0.9)
    ax.add_patch(Rectangle((x + 0.45, 4.2), 0.3, 0.35, fc="white", ec=INK, lw=0.9, zorder=4))
    ax.text(x + 0.82, 4.37, "18 Ω", fontsize=5.4, ha="left", va="center")
    # C2: MPCB + line contactor + soft starter with bypass
    x = cols[2]
    dev(x, y1, "MPCB")
    wire(x, y1, y2 + hb)
    dev(x, y2, "line contactor", fs=5.1)
    wire(x, y2, 6.8)
    dev(x, 5.4, "soft\nstarter\n22 kW\n4.5 In, cl. 20", fc=tint(GREEN, "30"), h=1.4, fs=5.2)
    bx = x - w / 2 - 0.22
    line(ax, [(x, 6.95), (bx, 6.95), (bx, 5.2), (x, 5.2)], lw=0.9)
    ax.text(bx + 0.04, 7.05, "bypass", fontsize=5.0, ha="left", va="bottom")
    wire(x, 5.4, ym + 0.48)
    motor(ax, x, ym, "C2 transfer\n22 kW")
    # C3: MPCB + K1 + K2
    x = cols[3]
    dev(x, y1, "MPCB")
    wire(x, y1, y2 + hb)
    dev(x, y2, "K1", fc=tint(SAFE, "35"))
    wire(x, y2, 6.8)
    dev(x, 6.2, "K2", fc=tint(SAFE, "35"))
    wire(x, 6.2, ym + 0.48)
    ax.text(x + 0.1, 5.6, "in series", fontsize=5.4, ha="left", va="center")
    motor(ax, x, ym, "C3 stockpile\n11 kW DOL")
    # D1: MPCB + reversing pair
    x = cols[4]
    dev(x, y1, "MPCB")
    wire(x, y1, 7.8)
    lbox(ax, x - w / 2, 6.6, 0.78, 1.2, "KF\nfwd", fs=5.6)
    lbox(ax, x + w / 2 - 0.78, 6.6, 0.78, 1.2, "KR\nrev", fs=5.6)
    ax.plot([x - 0.07, x + 0.07], [7.2, 7.2], color=RED, lw=2.0, zorder=5)
    ax.text(x, 6.5, "mechanical +\nelectrical\ninterlock", fontsize=5.2, ha="center", va="top",
            color=RED)
    wire(x, 5.6, ym + 0.48)
    motor(ax, x, ym, "D1 diverter\n1.5 kW rev.")
    # X1: MPCB + star-delta
    x = cols[5]
    dev(x, y1, "MPCB")
    wire(x, y1, 7.8)
    for k, lab in enumerate(("KM", "KY", "KΔ")):
        lbox(ax, x - w / 2 + k * 0.59, 6.6, 0.52, 1.2, lab, fs=5.8)
    ax.text(x, 6.5, "star–delta", fontsize=5.4, ha="center", va="top")
    wire(x, 6.05, ym + 0.48)
    motor(ax, x, ym, "X1 dust fan\n30 kW")
    # P1: MPCB + contactor
    x = cols[6]
    dev(x, y1, "MPCB")
    wire(x, y1, y2 + hb)
    dev(x, y2, "contactor")
    wire(x, y2, ym + 0.48)
    motor(ax, x, ym, "P1 sump\n4 kW DOL")
    # control section
    yc = -0.1
    lbox(ax, 0.3, yc, 3.0, 1.0, "safety relay", fc=tint(SAFE, "35"), fs=6.4, bold=True)
    lbox(ax, 3.7, yc, 2.0, 1.0, "24 V DC\nsupply", fc="#F2F2F2", fs=6.0)
    lbox(ax, 6.1, yc, 2.4, 1.0, "PLC", fc=tint(BLUE, "18"), fs=6.4, bold=True)
    ax.text(8.8, yc + 0.5, "hardwired I/O to contactors, MPCB auxiliaries\nand belt-speed sensors "
            "(not drawn)", fontsize=5.6, va="center", color="#444444")
    # safety: STO, SS1 and brake to the C1 VFD
    xs1 = 2.45
    line(ax, [(xs1, yc + 1.0), (xs1, 5.9), (cols[1] - w / 2, 5.9)], color=SAFE, lw=1.3,
         ls=(0, (4, 2)), arrow_end=True, ms=7)
    ax.text(2.05, 4.3, "STO ×2,\nSS1,\nbrake", fontsize=5.0, color="#8A6A00", ha="right",
            va="center")
    # safety: K1, K2 coils
    yl = 1.35
    xk = cols[3] + w / 2 + 0.3
    line(ax, [(3.0, yc + 1.0), (3.0, yl), (xk, yl), (xk, 6.5), (cols[3] + w / 2, 6.5)], color=SAFE,
         lw=1.1, ls=(0, (4, 2)), arrow_end=True, ms=6)
    line(ax, [(xk, 7.5), (cols[3] + w / 2, 7.5)], color=SAFE, lw=1.1, ls=(0, (4, 2)),
         arrow_end=True, ms=6)
    line(ax, [(xk, 6.5), (xk, 7.5)], color=SAFE, lw=1.1, ls=(0, (4, 2)))
    ax.text(xk + 0.08, 5.0, "K1, K2\ncoils", fontsize=5.2, color="#8A6A00", ha="left", va="center")
    # PROFINET
    yp = 1.8
    pn = dict(color=BLUE, lw=1.1, ls=(0, (2, 1.5)))
    line(ax, [(7.3, yc + 1.0), (7.3, yp)], **pn)
    line(ax, [(0.12, yp), (6.95, yp)], **pn)
    line(ax, [(0.12, yp), (0.12, 7.2), (cols[0] - w / 2, 7.2)], arrow_end=True, ms=6, **pn)
    line(ax, [(2.15, yp), (2.15, 5.3), (cols[1] - w / 2, 5.3)], arrow_end=True, ms=6, **pn)
    line(ax, [(6.95, yp), (6.95, 6.1), (cols[2] + w / 2, 6.1)], arrow_end=True, ms=6, **pn)
    ax.text(3.3, yp + 0.06, "PROFINET", fontsize=5.6, color=BLUE, va="bottom")
    save(fig, "20", "fig-20-1-mcc-single-line")


# ----------------------------------------------------------------------------
# Figure 20.2 — overload curves against the C2 soft start
# ----------------------------------------------------------------------------
KT = 1.15


def tau_cls(cls):
    return 0.8 * cls / math.log(7.2 ** 2 / (7.2 ** 2 - KT ** 2))


def fig_20_2():
    k = np.logspace(np.log10(1.16), 1, 600)
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    cols = {10: RED, 20: BLUE, 30: GREEN}
    for cls, c in cols.items():
        tau = tau_cls(cls)
        for th0, ls, lab in ((0.0, "-", "cold"), (1.0, "--", "hot")):
            t = tau * np.log((k ** 2 - th0) / (k ** 2 - KT ** 2))
            ax.plot(k, t, color=c, ls=ls, lw=1.6,
                    label=f"class {cls}, {lab} (τ = {tau:.0f} s)")
    # start markers (current limit, start time)
    starts = [(4.0, 4.9, "4.0 × In, normal: 4.9 s", "o", ORANGE),
              (4.0, 12.1, "4.0 × In, cold belt: 12.1 s", "s", ORANGE),
              (4.5, 2.7, "4.5 × In, normal: 2.7 s", "o", PINK),
              (4.5, 4.1, "4.5 × In, cold belt: 4.1 s", "s", PINK)]
    for kk, ts, lab, mk, c in starts:
        ax.plot([kk], [ts], mk, color=c, ms=7, mec=INK, mew=0.7, zorder=6)
        ax.plot([1.0, kk], [ts, ts], color=c, lw=0.6, ls=":", zorder=1)
    ax.annotate("12.1 s start lies above the\nclass 10 hot curve (6.7 s): trips",
                xy=(4.0, 12.1), xytext=(5.6, 30), fontsize=7, color=RED,
                arrowprops=dict(arrowstyle="-", color=RED, lw=0.7))
    ax.annotate("4.1 s start lies below the\nclass 20 hot curve (10.5 s): chosen",
                xy=(4.5, 4.1), xytext=(2.05, 1.75), fontsize=7, color=BLUE,
                arrowprops=dict(arrowstyle="-", color=BLUE, lw=0.7))
    ax.text(1.05, 4.9 * 1.05, "4.9", fontsize=6.4, color=ORANGE, va="bottom")
    ax.text(1.05, 12.1 * 1.05, "12.1", fontsize=6.4, color=ORANGE, va="bottom")
    ax.text(1.05, 2.7 * 0.95, "2.7", fontsize=6.4, color="#9A3A7A", va="top")
    ax.text(1.05, 4.1 * 0.95, "4.1", fontsize=6.4, color="#9A3A7A", va="top")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(1, 10)
    ax.set_ylim(1, 1000)
    from matplotlib.ticker import FixedLocator, NullFormatter
    ax.xaxis.set_major_locator(FixedLocator([1, 1.5, 2, 3, 4, 5, 7, 10]))
    ax.set_xticklabels(["1", "1.5", "2", "3", "4", "5", "7", "10"])
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.set_yticks([1, 10, 100, 1000])
    ax.set_yticklabels(["1", "10", "100", "1000"])
    ax.set_xlabel("current, multiple of overload setting (soft-starter limit × In)")
    ax.set_ylabel("time (s)")
    h, l = ax.get_legend_handles_labels()
    from matplotlib.lines import Line2D
    h += [Line2D([], [], marker="o", ls="", color=ORANGE, mec=INK, mew=0.7, ms=6),
          Line2D([], [], marker="o", ls="", color=PINK, mec=INK, mew=0.7, ms=6),
          Line2D([], [], marker="s", ls="", color="white", mec=INK, mew=0.7, ms=6)]
    l += ["start at 4.0 × In", "start at 4.5 × In", "square: cold belt (0.65 Tn)"]
    ax.legend(h, l, fontsize=6.4, loc="upper right", ncol=1)
    ax.text(1.03, 1.08, "hot: relay at its running state (θ₀ = 1); trip at θ = 1.15²",
            fontsize=6.4, color="#444444", ha="left")
    save(fig, "20", "fig-20-2-overload-curves-vs-start")


# ----------------------------------------------------------------------------
# Figure 20.3 — feed-rate loop
# ----------------------------------------------------------------------------
K, TAU, THETA = 3.0, 2.0, 12.0
DT, TS = 0.05, 0.5


def simulate(kc, ti, t_end=240.0):
    n = int(t_end / DT)
    delay = int(THETA / DT)
    u_hist = np.full(n + delay, 250.0 / K)
    y, yf, integ, u = 250.0, 250.0, 250.0 / K, 250.0 / K
    out = np.empty(n)
    uo = np.empty(n)
    for k in range(n):
        t = k * DT
        sp = 250.0 if t < 20 else 200.0
        dist = 0.0 if t < 130 else -0.15
        if k % int(TS / DT) == 0:
            e = sp - yf
            integ = np.clip(integ + kc * e * TS / ti, 0, 100)
            u = np.clip(kc * e + integ, 0, 100)
        u_hist[k + delay] = u
        y += DT / TAU * (K * (1 + dist) * u_hist[k] - y)
        yf += DT / 1.0 * (y - yf)
        out[k] = yf
        uo[k] = u
    return out, uo


def fig_20_3():
    t = np.arange(int(240 / DT)) * DT
    kc0 = 2.0 / (3.0 * 24.0)
    y1, u1 = simulate(kc0, 2.0)
    y2, u2 = simulate(2 * kc0, 2.0)
    sp = np.where(t < 20, 250.0, 200.0)
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.6, 4.9), sharex=True,
                                 gridspec_kw=dict(height_ratios=[1.7, 1]))
    a1.fill_between(t, sp * 0.98, sp * 1.02, color=GREEN, alpha=0.15, lw=0, label="±2 % band")
    a1.plot(t, sp, color=INK, lw=1.0, ls=(0, (5, 3)), label="setpoint")
    a1.plot(t, y2, color=ORANGE, lw=1.3, label="aggressive, Kc × 2")
    a1.plot(t, y1, color=BLUE, lw=1.8, label="SIMC, τc = θ = 12 s")
    a1.axvline(130, color=GREY, lw=0.8, ls=":")
    a1.text(128, 262, "bulk density −15 %", fontsize=7, color=GREY, va="center", ha="right")
    a1.text(21, 262, "setpoint 250 → 200 t/h", fontsize=7, color=GREY, va="center")
    # metrics
    w = (t >= 20) & (t < 130)
    settle = t[w][np.abs(y1[w] - 200) > 4][-1] - 20
    d = t >= 130
    rec = t[d][np.abs(y1[d] - 200) > 4][-1] - 130
    a1.annotate(f"SIMC settles in {settle:.0f} s,\nundershoot {200 - y1[w].min():.1f} t/h",
                xy=(20 + settle, 200), xytext=(64, 236), fontsize=7, color=BLUE,
                arrowprops=dict(arrowstyle="-", color=BLUE, lw=0.7))
    a1.annotate(f"aggressive: undershoot\n{200 - y2[w].min():.0f} t/h, oscillates",
                xy=(t[w][np.argmin(y2[w])], y2[w].min()), xytext=(66, 150), fontsize=7,
                color="#9A5A00", arrowprops=dict(arrowstyle="-", color=ORANGE, lw=0.7))
    a1.annotate(f"dip to {y1[d].min():.0f} t/h,\nrecovers in {rec:.0f} s",
                xy=(t[d][np.argmin(y1[d])], y1[d].min()), xytext=(185, 152), fontsize=7,
                color=BLUE, arrowprops=dict(arrowstyle="-", color=BLUE, lw=0.7))
    a1.annotate("", xy=(142, 186), xytext=(130, 186),
                arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.8, mutation_scale=6))
    a1.text(136, 188, "12 s\ndelay", fontsize=6.4, ha="center", va="bottom")
    a1.set_ylim(140, 270)
    a1.set_ylabel("tonnage at weigher (t/h)")
    a1.legend(fontsize=6.6, loc="upper right", ncol=2, bbox_to_anchor=(1.0, 1.02))
    a2.plot(t, u2, color=ORANGE, lw=1.1)
    a2.plot(t, u1, color=BLUE, lw=1.6)
    for v, lab, yy in ((250 / 3, "83.3 %", 250 / 3), (200 / 3, "66.7 %", 200 / 3),
                       (200 / 3 / 0.85, "78.4 %", 200 / 3 / 0.85)):
        a2.axhline(v, color="#CCCCCC", lw=0.6, zorder=0)
        a2.text(241, yy, lab, fontsize=6.6, va="center", color="#444444")
    a2.set_ylim(50, 100)
    a2.set_xlim(0, 240)
    a2.set_ylabel("feeder speed (%)")
    a2.set_xlabel("time (s)")
    fig.align_ylabels([a1, a2])
    fig.tight_layout(h_pad=0.5)
    save(fig, "20", "fig-20-3-feed-rate-loop-response")


# ----------------------------------------------------------------------------
# Figure 20.4 — emergency-stop circuit
# ----------------------------------------------------------------------------
def fig_20_4():
    fig, ax = schematic(6.8, 5.1, xlim=(0, 17.4), ylim=(1.3, 13.0))
    y1, y2 = 10.9, 10.1
    x0 = 0.5
    devs = [f"PC{i}" for i in range(1, 9)] + ["ES1", "ES2"]
    dx = 0.92
    for k, n in enumerate(devs):
        xc = x0 + 0.5 + k * dx
        contact(ax, xc, y1, nc=True)
        contact(ax, xc, y2, nc=True)
        ax.plot([xc, xc], [y2 + 0.3, y1 + 0.3], color=GREY, lw=0.6, ls=(0, (2, 1.5)), zorder=3)
        ax.text(xc, y1 + 0.42, n, fontsize=5.4, ha="center", va="bottom",
                color=RED if n.startswith("ES") else INK)
    xe = x0 + 0.5 + (len(devs) - 1) * dx + 0.36
    for yy, lab in ((y1, "CH1"), (y2, "CH2")):
        line(ax, [(x0, yy), (x0 + 0.14, yy)])
        for k in range(len(devs) - 1):
            xa = x0 + 0.5 + k * dx + 0.36
            line(ax, [(xa, yy), (xa + dx - 0.72, yy)])
        line(ax, [(xe, yy), (10.0, yy)])
        ax.text(x0 - 0.05, yy, lab, fontsize=6.0, ha="right", va="center")
    ax.text(4.9, 12.1, "dual-channel series chain: 8 pull-cord switches (4 per side,\n"
            "IEC 60947-5-5) + 2 E-stop buttons; latching, positive-opening NC",
            fontsize=5.9, ha="center", va="center")
    # safety relay
    sx, sy, sw, sh = 10.0, 5.6, 3.3, 7.0
    rbox(ax, sx, sy, sw, sh, fc=tint(SAFE, "30"), ec=INK, lw=1.2)
    ax.text(sx + sw / 2, sy + sh - 0.12, "safety relay", fontsize=7.6, weight="bold", ha="center",
            va="top")
    ax.text(sx + sw / 2, sy + sh - 0.62, "monitors CH1/CH2,\nlatches; manual reset", fontsize=5.6,
            ha="center", va="top")
    ax.text(sx + 0.1, y1, "S11–S12", fontsize=5.2, va="center")
    ax.text(sx + 0.1, y2, "S21–S22", fontsize=5.2, va="center")
    outs = [(9.3, "13–14 instantaneous"), (8.6, "37–38 delayed 3.0 s"), (7.9, "47–48 delayed 3.0 s"),
            (7.2, "57–58 delayed 3.0 s")]
    for yy, lab in outs:
        ax.text(sx + sw - 0.1, yy, lab, fontsize=5.2, ha="right", va="center")
    ax.text(sx + 0.1, 6.6, "23–24 instantaneous", fontsize=5.2, va="center")
    ax.text(sx + 0.1, 9.72, "aux: status", fontsize=5.2, va="center", color=GREY)
    ax.text(sx + 0.1, 5.85, "Y1–Y2 feedback", fontsize=5.2, va="center", color=GREEN)
    # reset button
    line(ax, [(sx + 2.4, sy), (sx + 2.4, 5.0)])
    ax.add_patch(Rectangle((sx + 2.15, 4.55), 0.5, 0.45, fc="#4A90D9", ec=INK, lw=0.8, zorder=4))
    ax.text(sx + 2.4, 4.45, "reset (manual,\nin sight of belt)", fontsize=5.4, ha="center", va="top")
    # VFD C1
    vx, vy, vw, vh = 14.3, 6.6, 2.9, 4.4
    rbox(ax, vx, vy, vw, vh, fc=tint(BLUE, "25"), ec=INK, lw=1.2)
    ax.text(vx + vw / 2, vy + vh - 0.12, "VFD C1 75 kW", fontsize=7.0, weight="bold", ha="center",
            va="top")
    vin = [(9.3, "SS1 request"), (8.6, "STO1"), (7.9, "STO2"), (7.2, "SBC (brake)")]
    for yy, lab in vin:
        line(ax, [(sx + sw, yy), (vx, yy)], color=SAFE, lw=1.4, arrow_end=True, ms=7)
        ax.text(vx + 0.1, yy, lab, fontsize=5.4, va="center")
    ax.text(vx + vw / 2, 10.05, "SS1: 2.5 s ramp;\nramp monitor →\nSTO + brake at once",
            fontsize=5.2, ha="center", va="center", color="#1B4F8A")
    # brake resistor
    ax.add_patch(Rectangle((vx + 0.3, 5.0), 1.1, 0.5, fc="white", ec=INK, lw=0.9, zorder=3))
    ax.text(vx + 0.85, 5.25, "18 Ω", fontsize=5.8, ha="center", va="center", zorder=4)
    line(ax, [(vx + 0.85, vy), (vx + 0.85, 5.5)])
    ax.text(vx + 0.85, 4.9, "brake resistor\n(chopper)", fontsize=5.2, ha="center", va="top")
    # motor with spring brake
    line(ax, [(vx + 2.1, vy), (vx + 2.1, 3.38)])
    motor(ax, vx + 2.1, 2.9, "C1 75 kW +\nspring brake")
    ax.add_patch(Rectangle((vx + 2.6, 2.65), 0.3, 0.5, fc="#DDDDDD", ec=INK, lw=0.8, zorder=4))
    line(ax, [(vx + vw, 7.2), (vx + 2.75 + 0.3, 7.2), (vx + 2.75 + 0.3, 3.15), (vx + 2.9, 3.15)],
         color=SAFE, lw=0.9, ls=(0, (3, 2)))
    # C3 contactors
    cx = 6.0
    ax.text(cx, 8.75, "400 V bus", fontsize=5.4, ha="center", va="bottom")
    lbox(ax, cx - 0.8, 8.0, 1.6, 0.6, "MPCB", fs=6.0)
    line(ax, [(cx, 8.0), (cx, 7.3)])
    lbox(ax, cx - 0.8, 6.7, 1.6, 0.6, "K1", fc=tint(SAFE, "35"), fs=6.4, bold=True)
    line(ax, [(cx, 6.7), (cx, 6.0)])
    lbox(ax, cx - 0.8, 5.4, 1.6, 0.6, "K2", fc=tint(SAFE, "35"), fs=6.4, bold=True)
    line(ax, [(cx, 5.4), (cx, 3.38)])
    motor(ax, cx, 2.9, "C3 11 kW\n(category 0)")
    # coils driven from the safety relay instantaneous output 23-24
    line(ax, [(sx, 6.6), (8.4, 6.6), (8.4, 7.0), (cx + 0.8, 7.0)], color=SAFE, lw=1.2,
         arrow_end=True, ms=6)
    line(ax, [(8.4, 6.6), (8.4, 5.7), (cx + 0.8, 5.7)], color=SAFE, lw=1.2, arrow_end=True, ms=6)
    ax.text(8.5, 6.15, "K1, K2 coils", fontsize=5.4, color="#8A6A00", va="center")
    # mirror contacts in the feedback loop
    yf, yg = 4.6, 4.0
    xa, xb = sx + 0.4, sx + 0.7
    line(ax, [(xa, sy), (xa, yf), (9.0, yf)], color=GREEN, lw=1.1)
    contact(ax, 8.6, yf, nc=True, color=GREEN)
    line(ax, [(8.24, yf), (7.76, yf)], color=GREEN, lw=1.1)
    contact(ax, 7.4, yf, nc=True, color=GREEN)
    line(ax, [(7.04, yf), (6.6, yf), (6.6, yg), (xb, yg), (xb, sy)], color=GREEN, lw=1.1)
    ax.text(8.6, yf + 0.38, "K1", fontsize=5.4, ha="center", color=GREEN)
    ax.text(7.4, yf + 0.38, "K2", fontsize=5.4, ha="center", color=GREEN)
    ax.text(8.6, yg - 0.15, "mirror contacts (NC, IEC 60947-4-1 Annex F):\na welded K1 or K2 "
            "blocks the reset", fontsize=5.4, color=GREEN, ha="center", va="top")
    # status to the standard PLC
    ys = 9.72
    lbox(ax, 0.4, 8.75, 3.0, 1.1, "standard PLC input\nSTATUS ONLY", fc=tint(BLUE, "18"), fs=6.0)
    line(ax, [(sx, ys), (5.06, ys)], color=GREY, lw=0.9)
    contact(ax, 4.7, ys, nc=False, color=GREY)
    line(ax, [(4.34, ys), (3.4, ys)], color=GREY, lw=0.9, arrow_end=True, ms=6)
    ax.text(4.7, ys - 0.2, "status contact", fontsize=5.4, ha="center", va="top", color=GREY)
    ax.text(1.9, 8.6, "the E-stop does not pass\nthrough the PLC program", fontsize=5.4,
            ha="center", va="top", color="#444444", style="italic")
    save(fig, "20", "fig-20-4-estop-circuit")


# ----------------------------------------------------------------------------
# Figure 20.5 — C1 stopping speed
# ----------------------------------------------------------------------------
def fig_20_5():
    v0 = 2.5
    t = np.linspace(0, 10, 2001)
    a_l, a_e = 20.8 / 22.1, 6.0 / 17.1
    a_b = (250 * (2 * math.pi * 1480 / 60) / v0 + 6000) / 17070     # spring brake + resistance
    cases = [("category 0, loaded (20.8 kN on 22.1 t)", np.maximum(v0 - a_l * t, 0), RED, "-"),
             ("category 0, empty (6 kN on 17.1 t)", np.maximum(v0 - a_e * t, 0), ORANGE, "-"),
             ("category 1, 2.5 s ramp + brake chopper", np.maximum(v0 - 1.0 * t, 0), BLUE, "-"),
             ("ramp not followed: STO at 0.3 s, spring brake",
              np.where(t < 0.3, v0, np.maximum(v0 - a_b * (t - 0.3), 0)), GREEN, "--")]
    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    for lab, v, c, ls in cases:
        tz = t[np.argmax(v <= 0)]
        ax.plot(t, v, color=c, ls=ls, lw=1.8, label=f"{lab}: stopped at {tz:.2f} s")
    ax.plot([7.4], [0.0], "v", color=ORANGE, ms=8, mec=INK, mew=0.6, zorder=6, clip_on=False)
    ax.text(7.4, 0.12, "measured\n7.4 s", fontsize=6.8, color="#9A5A00", ha="center", va="bottom")
    ax.plot([3.0], [0.0], "^", color=BLUE, ms=7, mec=INK, mew=0.6, zorder=6, clip_on=False)
    ax.text(3.05, 0.1, "delayed STO\nand brake 3.0 s", fontsize=6.4, color=BLUE, ha="left",
            va="bottom")
    ax.axvline(4.0, color=INK, ls=(0, (5, 3)), lw=1.0)
    ax.text(4.08, 2.52, "R4: stopped within 4.0 s", fontsize=7.2, va="top")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 2.6)
    ax.set_xlabel("time after E-stop demand (s)")
    ax.set_ylabel("belt speed (m/s)")
    ax.legend(fontsize=6.6, loc="upper right", bbox_to_anchor=(1.0, 0.88))
    # inset: regenerated power, empty belt, category 1
    ai = fig.add_axes([0.70, 0.27, 0.24, 0.19])
    tt = np.linspace(0, 2.5, 200)
    F = 17070 * 1.0 - 6000
    P = F * (v0 - tt) / 1e3
    E = F * v0 ** 2 / 2 / 1.0 / 1e3
    ai.fill_between(tt, 0, P, color=BLUE, alpha=0.2, lw=0)
    ai.plot(tt, P, color=BLUE, lw=1.4)
    ai.set_xlim(0, 3)
    ai.set_ylim(0, 32)
    ai.tick_params(labelsize=6, length=2, pad=1)
    ai.set_xlabel("t (s)", fontsize=6, labelpad=1)
    ai.set_ylabel("kW", fontsize=6, labelpad=1)
    ai.text(1.0, 30.0, f"regenerated, cat. 1 empty:\n{P[0]:.1f} kW → 0, {E:.0f} kJ", fontsize=5.8,
            va="top")
    save(fig, "20", "fig-20-5-c1-stopping-speed")


if __name__ == "__main__":
    fig_20_1()
    fig_20_2()
    fig_20_3()
    fig_20_4()
    fig_20_5()
