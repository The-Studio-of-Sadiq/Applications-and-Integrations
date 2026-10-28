"""Figures for Chapter 18 — Industrial Control Architecture.

Run from the repository root:  python figures/scripts/ch18.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, Polygon  # noqa: E402

from figstyle import COLORS, INK, save, schematic  # noqa: E402

BLUE, ORANGE, GREEN, PINK, YELLOW, SKY = COLORS[:6]
RED = "#C62828"
GREY = "#777777"
NET = "#0072B2"
FIBRE = "#E69F00"


def tint(c, a="30"):
    return c + a


def line(ax, pts, color=INK, lw=1.1, ls="-", arrow_end=False, both=False, ms=10, z=2):
    xs, ys = zip(*pts)
    if not arrow_end and not both:
        ax.plot(xs, ys, color=color, lw=lw, ls=ls, solid_capstyle="butt", zorder=z)
        return
    if len(pts) > 2:
        ax.plot(xs[:-1], ys[:-1], color=color, lw=lw, ls=ls, zorder=z)
    ax.annotate("", xy=pts[-1], xytext=pts[-2],
                arrowprops=dict(arrowstyle="<|-|>" if both else "-|>", color=color, lw=lw,
                                ls=ls, shrinkA=0, shrinkB=0, mutation_scale=ms), zorder=z)


def rbox(ax, x, y, w, h, fc="#EEF3F8", ec=INK, lw=1.0, ls="-", z=3):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.1",
                                fc=fc, ec=ec, lw=lw, ls=ls, zorder=z))


def lbox(ax, x, y, w, h, text, fc="#EEF3F8", fs=6.6, bold=False, ec=INK, z=3):
    rbox(ax, x, y, w, h, fc=fc, ec=ec, z=z)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, linespacing=1.05,
            weight="bold" if bold else "normal", zorder=z + 1)


def firewall(ax, x, y, label):
    w, h = 1.0, 0.7
    ax.add_patch(Rectangle((x, y), w, h, fc="#F4C7C7", ec=INK, lw=0.9, zorder=3))
    for k in range(1, 3):
        ax.plot([x, x + w], [y + k * h / 3] * 2, color="#9E3B3B", lw=0.6, zorder=4)
    for k, row in enumerate(range(3)):
        off = 0.25 if k % 2 else 0.5
        ax.plot([x + off, x + off], [y + k * h / 3, y + (k + 1) * h / 3], color="#9E3B3B", lw=0.6,
                zorder=4)
    ax.text(x + w / 2, y - 0.08, label, ha="center", va="top", fontsize=6.6, weight="bold")


# ----------------------------------------------------------------------------
# Figure 18.1 — control architecture by ISA-95 level
# ----------------------------------------------------------------------------
def fig_18_1():
    fig, ax = schematic(6.8, 5.6, xlim=(0, 17), ylim=(0, 14.0))
    bands = [("Level 4", "enterprise", 12.5, 13.95, "#F3F3F3"),
             ("Level 3", "site DMZ", 10.6, 12.45, "#F8F1E4"),
             ("Level 2", "supervision", 7.9, 10.55, "#EAF2F8"),
             ("Level 1", "basic control", 2.3, 7.85, "#EAF5EE"),
             ("Level 0", "process", 0.0, 2.25, "#F7F7F7")]
    for name, sub, y0, y1, fc in bands:
        ax.add_patch(Rectangle((0, y0), 17, y1 - y0, fc=fc, ec="none", zorder=0))
        ax.text(0.12, y1 - 0.12, name, fontsize=7.2, weight="bold", va="top", color="#444444")
        ax.text(0.12, y1 - 0.55, sub, fontsize=6.4, va="top", color="#444444")

    # Level 4
    lbox(ax, 4.6, 12.85, 3.6, 0.8, "corporate network", fc="white")
    firewall(ax, 9.3, 12.9, "")
    ax.text(10.45, 13.25, "F1", fontsize=6.8, weight="bold", va="center")
    line(ax, [(8.2, 13.25), (9.3, 13.25)], color=NET)
    line(ax, [(9.8, 12.9), (9.8, 12.15)], color=NET)
    # Level 3 (DMZ between F1 and F2)
    line(ax, [(2.35, 12.15), (9.8, 12.15)], color=NET)
    lbox(ax, 3.6, 11.0, 2.6, 0.95, "historian\nreplica", fc="white")
    lbox(ax, 6.7, 11.0, 2.3, 0.95, "jump\nserver", fc="white")
    for xx in (4.9, 7.85):
        line(ax, [(xx, 12.15), (xx, 11.95)], color=NET)
    firewall(ax, 1.85, 11.0, "")
    ax.text(3.0, 11.35, "F2", fontsize=6.8, weight="bold", va="center")
    line(ax, [(2.35, 12.15), (2.35, 11.7)], color=NET)
    line(ax, [(2.35, 11.0), (2.35, 10.2)], color=NET)
    ax.text(10.4, 11.5, "data leave the control system only via\nthe replica; nothing at Level 4 "
            "queries\na Level 1 or Level 2 device", fontsize=6.0, color="#6A5200", style="italic",
            va="center")
    # Level 2
    ysn = 10.2
    line(ax, [(1.8, ysn), (13.1, ysn)], color=NET, lw=1.4)
    ax.text(6.0, ysn + 0.08, "supervisory network", fontsize=6.0, color=NET, va="bottom")
    l2 = [(1.8, 1.6, "SCADA\nserver A"), (3.7, 1.6, "SCADA\nserver B"), (5.6, 1.6, "operator\nclient 1"),
          (7.5, 1.6, "operator\nclient 2"), (9.4, 1.6, "engineering\nworkstation"),
          (11.3, 1.8, "telemetry\nfront end")]
    for x, w, t in l2:
        lbox(ax, x, 8.35, w, 1.1, t, fc="white", fs=5.9)
        line(ax, [(x + w / 2, ysn), (x + w / 2, 9.45)], color=NET)
    ax.text(3.5, 8.18, "redundant pair", fontsize=6.0, color=GREY, ha="center", va="top")
    # outstations at right
    xo = 14.1
    rbox(ax, xo, 3.0, 2.85, 7.3, fc="white", ec=GREY, ls=(0, (3, 2)), z=2)
    ax.text(xo + 1.42, 10.1, "8 outstations", fontsize=6.8, weight="bold", ha="center", va="top")
    ax.text(xo + 1.42, 9.7, "(compact PLC or RTU,\nlocal control, ≤ 25 km)", fontsize=5.9,
            ha="center", va="top")
    for k in range(8):
        yy = 8.45 - k * 0.68
        lbox(ax, xo + 0.3, yy, 2.25, 0.52, f"RTU {k + 1}", fc="#FFF8E6", fs=6.2)
    # radio / 4G link
    line(ax, [(12.2, 8.35), (12.2, 7.75), (xo + 0.3, 7.75)], color=PINK, lw=1.4, ls=(0, (4, 2)),
         arrow_end=True)
    ax.text(13.25, 7.6, "UHF radio\n9600 bit/s\nand 4G", fontsize=6.0, color="#8B3A6B",
            ha="center", va="top")
    # Level 1: MCP panel with PLC pair
    rbox(ax, 2.15, 5.65, 4.9, 1.95, fc="white", ec=INK, ls=(0, (4, 2)), z=2)
    ax.text(2.3, 7.5, "panel MCP", fontsize=6.4, weight="bold", va="top")
    lbox(ax, 2.35, 5.85, 1.7, 1.1, "PLC\nCPU A", fc=tint(GREEN, "40"), bold=True)
    lbox(ax, 5.0, 5.85, 1.8, 1.1, "PLC\nCPU B", fc=tint(GREEN, "40"), bold=True)
    line(ax, [(4.05, 6.4), (5.0, 6.4)], color=FIBRE, lw=1.6, both=True, ms=7)
    ax.text(4.53, 6.48, "sync\nfibre", fontsize=5.6, color="#8A6A00", ha="center", va="bottom")
    # PLC second interface to the supervisory network
    line(ax, [(5.45, 7.6), (5.45, ysn)], color=NET, lw=1.2, z=1)
    # PROFINET fibre ring
    ring_x0, ring_x1, ring_y0, ring_y1 = 1.35, 13.35, 3.05, 5.25
    ax.add_patch(FancyBboxPatch((ring_x0, ring_y0), ring_x1 - ring_x0, ring_y1 - ring_y0,
                                boxstyle="round,pad=0,rounding_size=0.5", fc="none", ec=FIBRE,
                                lw=2.0, zorder=1))
    ax.text(6.75, 5.05, "PROFINET fibre ring\nwith MRP", fontsize=6.4, color="#8A6A00",
            va="top", ha="left", weight="bold")
    line(ax, [(3.15, 5.85), (3.15, ring_y1)], color=FIBRE, lw=1.4)
    line(ax, [(5.9, 5.85), (5.9, ring_y1)], color=FIBRE, lw=1.4)
    drops = [(1.85, "RIO-1\nintake"), (3.95, "RIO-2\nfilters"), (6.05, "RIO-3\nchemicals"),
             (8.15, "RIO-4\nhigh-lift")]
    for x, t in drops:
        lbox(ax, x, 2.6, 1.75, 0.95, t, fc="white", z=4)
    lbox(ax, 10.45, 4.75, 2.75, 1.0, "6 VFDs\n3 intake + 3 high-lift", fc="white", z=4, fs=5.9)
    # hardwired relay chain beside RIO-4
    lbox(ax, 10.1, 3.35, 2.15, 0.95, "hardwired pump-\nprotection relays", fc="#F4C7C7", z=4,
         fs=5.5)
    line(ax, [(9.9, 3.45), (10.15, 3.45)], color=RED, lw=1.2)
    line(ax, [(11.15, 4.3), (11.15, 4.75)], color=RED, lw=1.2)
    ax.text(11.25, 4.52, "run permit", fontsize=5.4, color=RED, va="center")
    # timing annotations
    ax.text(7.5, 7.6, "PLC cycle 10 ms\nPROFINET update 4 ms\nring recovery ≤ 200 ms\n"
            "I/O watchdog 300 ms", fontsize=6.3, va="top", ha="left", color=INK,
            bbox=dict(fc="white", ec=GREY, lw=0.6, boxstyle="round,pad=0.25"))
    # Level 0 icons
    def transmitter(x, y, tag):
        ax.add_patch(Circle((x, y), 0.33, fc="white", ec=INK, lw=0.9, zorder=3))
        ax.text(x, y, tag, fontsize=5.4, ha="center", va="center", zorder=4)

    def valve(x, y):
        ax.add_patch(Polygon([(x - 0.35, y - 0.22), (x - 0.35, y + 0.22), (x + 0.35, y - 0.22),
                              (x + 0.35, y + 0.22)], closed=True, fc="white", ec=INK, lw=0.9, zorder=3))
        ax.plot([x, x], [y, y + 0.38], color=INK, lw=0.9, zorder=3)
        ax.add_patch(Rectangle((x - 0.17, y + 0.38), 0.34, 0.16, fc="white", ec=INK, lw=0.8, zorder=3))

    def motor(x, y):
        ax.add_patch(Circle((x, y), 0.35, fc="white", ec=INK, lw=0.9, zorder=3))
        ax.text(x, y, "M", fontsize=6.6, ha="center", va="center", weight="bold", zorder=4)

    icons = [(2.4, "t", "LT"), (3.05, "m", ""), (4.5, "v", ""), (5.15, "t", "FT"),
             (6.6, "t", "Cl"), (7.25, "m", ""), (8.7, "t", "PS"), (9.35, "v", ""),
             (12.4, "m", "")]
    for x, kind, tag in icons:
        if kind == "t":
            transmitter(x, 1.25, tag)
        elif kind == "v":
            valve(x, 1.15)
        else:
            motor(x, 1.25)
    for x, _ in drops:
        line(ax, [(x + 0.55, 2.6), (x + 0.55, 1.65)], color=GREY, lw=0.8)
        line(ax, [(x + 1.2, 2.6), (x + 1.2, 1.65)], color=GREY, lw=0.8)
    line(ax, [(12.4, 4.75), (12.4, 1.6)], color=GREY, lw=0.8, z=1)
    ax.text(12.6, 0.55, "high-lift pump", fontsize=5.8, ha="center", color="#444444")
    ax.text(14.2, 1.25, "transmitters, valves,\nmotors (Ch. 19, 20)", fontsize=6.2, va="center",
            color="#444444")
    save(fig, "18", "fig-18-1-wtw-control-architecture")


# ----------------------------------------------------------------------------
# Figure 18.2 — scan response timing
# ----------------------------------------------------------------------------
def fig_18_2():
    fig, ax = plt.subplots(figsize=(6.8, 4.1))
    rows = ["pressure switch", "DI module output", "PROFINET input\n(4 ms frames)",
            "PLC cycle (10 ms)", "PROFINET output\n(4 ms frames)", "DO output", "VFD torque"]
    n = len(rows)
    ys = {r: n - 1 - i for i, r in enumerate(rows)}
    hgt = 0.62

    def step(row, t_sw, hi_first, color=BLUE):
        y = ys[row]
        t = [0, t_sw, t_sw, 60]
        lo, hi = y - hgt / 2, y + hgt / 2
        v = [hi, hi, lo, lo] if hi_first else [lo, lo, hi, hi]
        ax.plot(t, v, color=color, lw=1.6)

    step(rows[0], 0.0, True)
    step(rows[1], 3.2, True)
    # PROFINET input frames
    y = ys[rows[2]]
    for tf in np.arange(-0.8, 60, 4.0):
        hit = abs(tf - 7.2) < 1e-6
        ax.add_patch(Rectangle((tf, y - hgt / 2), 0.5, hgt, fc=RED if hit else "#BBBBBB",
                               ec="none"))
    # PLC cycles
    y = ys[rows[3]]
    for k, ts in enumerate(np.arange(-2.8, 60, 10.0)):
        fc = "#EEEEEE"
        if abs(ts - 17.2) < 1e-6:
            fc = tint(GREEN, "60")
        ax.add_patch(Rectangle((ts, y - hgt / 2), 10, hgt, fc=fc, ec=GREY, lw=0.8))
        ax.plot([ts, ts], [y - hgt / 2, y + hgt / 2], color=INK, lw=1.0)
    yp = ys[rows[3]]
    ax.text(12.2, yp, "inputs read at 7.2,\nchange just missed", fontsize=6.0, ha="center",
            va="center", color="#555555", linespacing=1.0)
    ax.text(22.2, yp, "cycle that sees\nthe change", fontsize=6.0, ha="center", va="center",
            linespacing=1.0)
    ax.text(32.2, yp, "outputs written\nat 27.2", fontsize=6.0, ha="center", va="center",
            color="#555555", linespacing=1.0)
    # PROFINET output frames
    y = ys[rows[4]]
    for tf in np.arange(3.2 - 4 * 1, 60, 4.0):
        hit = abs(tf - 31.2) < 1e-6
        ax.add_patch(Rectangle((tf, y - hgt / 2), 0.5, hgt, fc=RED if hit else "#BBBBBB",
                               ec="none"))
    step(rows[5], 31.7, False)
    # VFD torque
    yv = ys[rows[6]]
    ax.plot([0, 31.7], [yv + hgt / 2] * 2, color=BLUE, lw=1.6)
    ax.add_patch(Rectangle((31.7, yv - hgt / 2), 18.3, hgt, fc=tint(ORANGE, "35"), ec="none"))
    ax.plot([31.7, 50, 50, 60], [yv + hgt / 2, yv + hgt / 2, yv - hgt / 2, yv - hgt / 2],
            color=BLUE, lw=1.6)
    ax.text(40.9, yv, "drive reacts 10–20 ms", fontsize=6.6, ha="center", va="center")
    # event markers
    events = [(0, 0, "0"), (3.2, 1, "3.2"), (7.2, 2, "7.2"), (17.2, 3, "17.2"), (27.2, 3, "27.2"),
              (31.2, 4, "31.2"), (31.7, 5, "31.7"), (50, 6, "≈ 50")]
    for t_e, ri, lab in events:
        y = ys[rows[ri]]
        ax.text(t_e + 0.3, y + hgt / 2 + 0.05, lab, fontsize=6.6, color=RED, ha="left", va="bottom")
    # causal arrows
    chain = [(0, 0, 3.2, 1), (3.2, 1, 7.2, 2), (7.7, 2, 17.2, 3), (27.2, 3, 31.2, 4),
             (31.7, 4, 31.7, 5), (31.7, 5, 31.7, 6)]
    for t0, r0, t1, r1 in chain:
        ax.annotate("", xy=(t1, ys[rows[r1]] + hgt / 2), xytext=(t0, ys[rows[r0]] - hgt / 2),
                    arrowprops=dict(arrowstyle="-|>", color=RED, lw=0.8, mutation_scale=7,
                                    shrinkA=0, shrinkB=0, ls=(0, (2, 1.5))))
    # brackets
    yb1, yb2, yb3 = -1.0, -1.65, -2.3

    def bracket(y, t1, text, color):
        ax.annotate("", xy=(t1, y), xytext=(0, y),
                    arrowprops=dict(arrowstyle="|-|", color=color, lw=1.0, mutation_scale=3,
                                    shrinkA=0, shrinkB=0))
        ax.text(t1 + 0.6, y, text, fontsize=7.2, va="center", color=color)

    bracket(yb1, 17.7, "typical 17.7 ms to DO", GREEN)
    bracket(yb2, 31.7, "worst case 31.7 ms to DO", RED)
    bracket(yb3, 50, "total ≈ 50 ms to torque off", INK)
    ax.text(60, -2.95, "R2 limit: 200 ms, four times the total (off this scale) →", fontsize=7.2,
            ha="right", va="center", color="#8A0000", weight="bold")
    ax.set_yticks([ys[r] for r in rows])
    ax.set_yticklabels(rows, fontsize=7.4)
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    ax.set_xlim(-1, 60)
    ax.set_ylim(-3.25, n - 0.25)
    ax.set_xticks(np.arange(0, 61, 10))
    ax.set_xlabel("time after the pressure switch opens (ms)")
    for xg in np.arange(0, 61, 10):
        ax.axvline(xg, color="#E8E8E8", lw=0.6, zorder=0)
    save(fig, "18", "fig-18-2-scan-response-timing")


# ----------------------------------------------------------------------------
# Figure 18.3 — alarm rate before and after rationalisation
# ----------------------------------------------------------------------------
def synth_alarms():
    """Synthetic 10-min alarm counts over 30 days matching Table 18.8."""
    rng = np.random.default_rng(18)
    n = 4320
    t = np.arange(n) / 144.0
    # before: diurnal base with chattering bursts
    diurnal = 1 + 0.35 * np.sin(2 * np.pi * (t - 0.3))
    before = np.minimum(rng.poisson(3.6 * diurnal), 10)
    # chattering / bad-actor episodes producing floods
    n_flood = round(0.111 * n)                       # 480 periods above 10
    idx = rng.choice(n, n_flood, replace=False)
    before[idx] = 11 + rng.gamma(1.6, 4.0, n_flood).astype(int)
    before[before > 83] = 83
    before[rng.choice(idx)] = 83
    # adjust total to 754 alarms/day x 30 days = 22 620 without changing the flood count
    target = 754 * 30
    calm = np.where(before <= 9)[0]
    diff = target - before.sum()
    while diff != 0:
        k = rng.choice(calm)
        if diff > 0 and before[k] < 9:
            before[k] += 1
            diff -= 1
        elif diff < 0 and before[k] > 0:
            before[k] -= 1
            diff += 1
    # after: sparse, six upsets
    after = rng.poisson(0.42, n)
    after[after > 4] = 4
    ups = np.round(np.array([3.2, 7.9, 12.6, 17.4, 22.1, 26.8]) * 144).astype(int)
    up_vals = np.array([61, 44, 52, 38, 57, 47])
    after[ups] = up_vals
    target = 77 * 30
    calm = np.setdiff1d(np.arange(n), ups)
    diff = target - after.sum()
    while diff != 0:
        k = rng.choice(calm)
        if diff > 0 and after[k] < 3:
            after[k] += 1
            diff -= 1
        elif diff < 0 and after[k] > 0:
            after[k] -= 1
            diff += 1
    return t, before, after, ups


def fig_18_3():
    t, before, after, ups = synth_alarms()
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.6, 4.6), sharex=True)
    for a, d, lab in ((a1, before, "Before rationalisation (1 800 configured alarms)"),
                      (a2, after, "After rationalisation (900 configured alarms)")):
        a.vlines(t, 0, d, color=GREY, lw=0.45)
        m = d.mean()
        flood = np.mean(d > 10) * 100
        a.axhline(10, color=RED, lw=1.0, label="flood threshold (> 10)")
        a.axhline(1, color=GREEN, lw=1.0, label="target average (1)")
        a.axhline(m, color=BLUE, ls=(0, (5, 3)), lw=1.2, label=f"mean {m:.2f}")
        a.set_ylim(0, 90)
        a.set_ylabel("alarms per 10 min")
        a.set_title(lab, fontsize=8.6, loc="left")
        a.legend(loc="upper left", ncol=3, fontsize=6.8, bbox_to_anchor=(0.0, 1.02),
                 handlelength=1.8, columnspacing=1.2)
        a.text(0.99, 0.80, f"max {d.max()}  ·  periods in flood {flood:.1f} %  ·  "
               f"{d.sum() / 30:.0f} alarms/day", transform=a.transAxes, ha="right", va="top",
               fontsize=7.2, bbox=dict(fc="white", ec="none", pad=1))
    for k in ups:
        a2.annotate("", xy=(t[k], after[k] + 1), xytext=(t[k], after[k] + 9),
                    arrowprops=dict(arrowstyle="-|>", color=ORANGE, lw=0.8, mutation_scale=6))
    a2.text(7.5, 72, "plant upsets: power dips trip every pump",
            fontsize=6.8, color="#9A5A00", ha="center")
    a2.set_xlim(0, 30)
    a2.set_xlabel("time (days), 4 320 ten-minute periods")
    fig.tight_layout(h_pad=0.6)
    save(fig, "18", "fig-18-3-alarm-rate-before-after")


# ----------------------------------------------------------------------------
# Figure 18.4 — panel temperature against heat load
# ----------------------------------------------------------------------------
def fig_18_4():
    k, A = 5.5, 1.4 * 0.8 * (2.0 + 0.6) + 1.8 * 0.6 * 2.0
    kA = k * A
    P = np.linspace(0, 600, 300)
    fig, ax = plt.subplots(figsize=(6.4, 3.9))
    cases = [(0, "sealed", RED), (62, "filter fan, 62 m³/h effective", BLUE),
             (120, "filter fan, 120 m³/h effective", GREEN)]
    for V, lab, c in cases:
        T = 40 + P / (kA + V / 3.1)
        G = kA + V / 3.1
        ax.plot(P, T, color=c, lw=1.8, label=f"{lab}: T = 40 + P / {G:.1f}")
        T239 = 40 + 239 / G
        ax.plot([239], [T239], "o", color=c, ms=5)
        if V == 120:
            ax.text(246, T239 - 0.3, f"{T239:.1f} °C", fontsize=7.4, color=c, va="top", ha="left")
        else:
            ax.text(232, T239 + 0.3, f"{T239:.1f} °C", fontsize=7.4, color=c, va="bottom", ha="right")
    ax.axhline(45, color=INK, ls=(0, (5, 3)), lw=1.0)
    ax.text(595, 45.3, "R8: ≤ 45 °C inside", fontsize=7.4, ha="right", va="bottom")
    ax.axvline(239, color=GREY, ls=(0, (5, 3)), lw=1.0)
    ax.text(244, 69.5, "design load 239 W", fontsize=7.4, ha="left", va="center", color=GREY)
    ax.set_xlim(0, 600)
    ax.set_ylim(40, 80)
    ax.set_xlabel("heat load inside the panel P (W)")
    ax.set_ylabel("internal air temperature (°C)")
    ax.legend(fontsize=7.2, loc="upper left", bbox_to_anchor=(0.0, 1.0))
    ax.text(595, 64.0, f"2000 × 800 × 600 mm against a wall:\nA = {A:.2f} m², kA = {kA:.1f} W/K;"
            "\n40 °C ambient; fan adds V̇/3.1 W/K", fontsize=6.8, ha="right", va="bottom",
            color="#444444")
    save(fig, "18", "fig-18-4-panel-temperature-vs-load")


# ----------------------------------------------------------------------------
# Figure 18.5 — commissioning stages
# ----------------------------------------------------------------------------
def fig_18_5():
    fig, ax = schematic(6.8, 3.25, xlim=(0, 17.2), ylim=(0, 8.2))
    stages = [("Design\nfreeze", "I/O list,\ncause-and-\neffect matrix", "frozen design\nbaseline"),
              ("FAT", "simulated I/O,\nredundancy,\nnetwork tests", "FAT report"),
              ("Installation", "insulation\nresistance,\ncontinuity,\nearthing", "IR sheets"),
              ("SAT and\nloop checks", "491 loops,\n4/12/20 mA,\nvalves stroked", "loop sheets"),
              ("Cold com-\nmissioning", "water,\nsequences,\nloop tuning", "tuning\nrecords"),
              ("Performance\ntest", "7 to 30 days,\nall automatic\nfunctions", "performance\nreport"),
              ("Handover", "as-builts,\nbackups,\nspares, training", "handover\ncertificate")]
    w, g = 2.2, 0.25
    y0, h = 4.3, 3.1
    xs = [0.1 + i * (w + g) for i in range(len(stages))]
    cols = ["#F2F2F2", tint(BLUE, "22"), "#F2F2F2", tint(BLUE, "22"), "#F2F2F2", tint(BLUE, "22"),
            tint(GREEN, "35")]
    for x, (t, b, rec), fc in zip(xs, stages, cols):
        rbox(ax, x, y0, w, h, fc=fc)
        ax.text(x + w / 2, y0 + h - 0.15, t, ha="center", va="top", fontsize=6.6, weight="bold",
                linespacing=1.0)
        ax.text(x + w / 2, y0 + 0.15, b, ha="center", va="bottom", fontsize=5.8, linespacing=1.1)
        # record (document icon)
        ry = 2.3
        ax.add_patch(Polygon([(x + 0.12, ry), (x + w - 0.12, ry), (x + w - 0.12, ry + 0.95),
                              (x + w - 0.42, ry + 1.25), (x + 0.12, ry + 1.25)], closed=True,
                             fc="#FFFBEA", ec="#9A7A00", lw=0.9))
        ax.text(x + w / 2 - 0.08, ry + 0.6, rec, ha="center", va="center", fontsize=6.0,
                linespacing=1.0)
        line(ax, [(x + w / 2, y0), (x + w / 2, ry + 1.25)], color="#9A7A00", lw=0.8, arrow_end=True,
             ms=7)
    for i in range(len(xs) - 1):
        line(ax, [(xs[i] + w, y0 + h / 2), (xs[i + 1], y0 + h / 2)], lw=1.3, arrow_end=True, ms=9)
    ax.text(8.6, 7.75, "IEC 62381 stages; each produces a signed record",
            fontsize=7.2, ha="center", style="italic", color="#444444")
    # punch list box and feedback arrows
    px0, px1 = 2.6, 14.6
    rbox(ax, px0, 0.1, px1 - px0, 1.0, fc=tint(RED, "18"), ec=RED)
    ax.text((px0 + px1) / 2, 0.6, "punch list and change control: every deviation logged with owner "
            "and date,\nfixed, retested; open items carried to handover", fontsize=6.6, ha="center",
            va="center")
    for i in (1, 3, 5):
        x = xs[i] + w + g / 2
        line(ax, [(x, y0), (x, 1.1)], color=RED, lw=1.0, arrow_end=True, ls=(0, (3, 2)), ms=8)
    xh = xs[6] + 0.3
    line(ax, [(px1, 0.6), (xh, 0.6), (xh, 2.3)], color=RED, lw=1.0, arrow_end=True,
         ls=(0, (3, 2)), ms=8)
    save(fig, "18", "fig-18-5-commissioning-stages")


if __name__ == "__main__":
    fig_18_1()
    fig_18_2()
    fig_18_3()
    fig_18_4()
    fig_18_5()
