"""Figures for Chapter 2 — System Architecture.

Run from the repository root:  python figures/scripts/ch02.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch  # noqa: E402

from figstyle import COLORS, INK, box, save, new_fig  # noqa: E402
from figstyle import schematic as _schematic  # noqa: E402


def schematic(*a, **k):
    """figstyle.schematic with the axes filling the figure (diagrams only)."""
    fig, ax = _schematic(*a, **k)
    fig.subplots_adjust(left=0.01, right=0.99, bottom=0.01, top=0.99)
    return fig, ax

BLUE, ORANGE, GREEN, PINK, YELLOW, SKY = COLORS[:6]
RED = "#C62828"
GREY = "#888888"
LIGHT = "#F2F2F2"
PURPLE = "#7B3FA0"
C_PWR, C_DIG, C_RF, C_HUM, C_NET = RED, "#1F5FA8", PURPLE, "#1E8A4C", "#777777"


def arr(ax, x0, y0, x1, y1, color=INK, lw=1.1, ls="-", both=False, ms=9, rad=0.0, z=2,
        style=None):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1),
                                 arrowstyle=style or ("<|-|>" if both else "-|>"), color=color,
                                 lw=lw, ls=ls, mutation_scale=ms, shrinkA=0, shrinkB=0,
                                 connectionstyle=f"arc3,rad={rad}", zorder=z))


def poly(ax, pts, color=INK, lw=1.1, ls="-", end=True, both=False, z=2):
    xs, ys = zip(*pts)
    ax.plot(xs[:-1], ys[:-1], color=color, lw=lw, ls=ls, zorder=z, solid_capstyle="butt")
    ax.plot(xs[-2:], ys[-2:], color=color, lw=lw, ls=ls, zorder=z)
    if end or both:
        arr(ax, *pts[-2], *pts[-1], color=color, lw=lw, both=both, z=z + 0.1)


def rbox(ax, x, y, w, h, text, fc="white", ec=INK, lw=1.0, fs=8, ls="-", weight="normal",
         color=INK, z=3, rs=0.15):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.02,rounding_size={rs}",
                                fc=fc, ec=ec, lw=lw, ls=ls, zorder=z))
    if text:
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
                weight=weight, color=color, zorder=z + 0.1, linespacing=1.15)


# ----------------------------------------------------------------------------
# Figure 2.1 — function tree
# ----------------------------------------------------------------------------
def fig_2_1():
    tree = [
        ("F1 Sense", [("F1.1 Couple to\nload simulant", "R1, R6, R10"),
                      ("F1.2 Convert", "R1, R2"), ("F1.3 Validate", "R1")]),
        ("F2 Evaluate", [("F2.1 Count alarm\ndurations", "R3, R6"),
                         ("F2.2 Daily\nstatistics", "R4")]),
        ("F3 Annunciate", [("F3.1 Display", "R8"), ("F3.2 Sound\nand flash", "R3"),
                           ("F3.3 Acknowledge", "R3")]),
        ("F4 Record", [("F4.1 Store", "R2, R7"), ("F4.2 Protect\nintegrity", "R7, R13")]),
        ("F5 Communicate", [("F5.1 Report", "R4, R13"), ("F5.2 Push alarm", "R4, R13"),
                            ("F5.3 Configuration\nand firmware", "R10, R13"),
                            ("F5.4 Network\ntime", "R9")]),
        ("F6 Supply energy", [("F6.1 Store", "R5"), ("F6.2 Buffer\npulses", "R5"),
                              ("F6.3 Monitor\nbattery", "R5")]),
        ("F7 Keep time", []),
        ("F8 Supervise", [("F8.1 Watchdog", "R3"), ("F8.2 Self-test", "R3"),
                          ("F8.3 Report\nfaults", "R4")]),
    ]
    safety = {"F2.1 Count alarm\ndurations", "F3.2 Sound\nand flash"}
    fig, ax = schematic(6.8, 4.9, xlim=(0, 20), ylim=(0.75, 15.2))
    rows = len(tree)
    ys = [13.0 - i * 1.72 for i in range(rows)]
    bh = 1.38
    # root
    ry = (ys[0] + ys[-1]) / 2
    rbox(ax, 0.05, ry - 1.6, 2.55, 3.2 + bh, "F0\nMonitor\nvaccine\ntempera-\nture and\nreport",
         fc="#DCE6F2", fs=7.8, weight="bold")
    busx = 2.85
    ax.plot([2.6, busx], [ry + bh / 2] * 2, color=INK, lw=1.0, zorder=1)
    ax.plot([busx, busx], [ys[-1] + bh / 2, ys[0] + bh / 2], color=INK, lw=1.0, zorder=1)
    lx0, lw_, gap = 6.6, 3.15, 0.22
    for (name, leaves), y in zip(tree, ys):
        ax.plot([busx, 3.05], [y + bh / 2] * 2, color=INK, lw=1.0, zorder=1)
        rbox(ax, 3.05, y, 3.25, bh, name, fc="#EEF3F8", fs=7.5, weight="bold")
        if name.startswith("F7"):
            ax.text(6.6, y + bh / 2, "leaf function itself: R2, R9", va="center", fontsize=6.9,
                    color=C_DIG, style="italic")
        if leaves:
            xend = lx0 + (len(leaves) - 1) * (lw_ + gap) + lw_ / 2
            ax.plot([6.3, xend], [y + bh / 2] * 2, color=INK, lw=1.0, zorder=1)
        for j, (leaf, req) in enumerate(leaves):
            x = lx0 + j * (lw_ + gap)
            hi = leaf in safety
            rbox(ax, x, y, lw_, bh, "", fc="#FBE3E3" if hi else "white",
                 ec=RED if hi else INK, lw=1.8 if hi else 0.9)
            ax.text(x + lw_ / 2, y + bh * 0.62, leaf, ha="center", va="center", fontsize=7.6,
                    zorder=4, linespacing=1.1)
            ax.text(x + lw_ / 2, y + 0.2, req, ha="center", va="center", fontsize=6.9,
                    color=C_DIG, style="italic", zorder=4)
    # legend
    rbox(ax, 6.55, 14.45, 0.9, 0.5, "", fc="#FBE3E3", ec=RED, lw=1.8)
    ax.text(7.6, 14.7, "safety-relevant path (R3): F2.1 → F3.2", va="center", fontsize=8)
    ax.text(14.2, 14.7, "R1…R13: requirements served (Table 2.1)", va="center", fontsize=8,
            color=C_DIG, style="italic")
    save(fig, "02", "fig-2-1-ccm1-function-tree")


# ----------------------------------------------------------------------------
# Figure 2.2 — physical architecture
# ----------------------------------------------------------------------------
def fig_2_2():
    fig, ax = schematic(6.8, 5.0, xlim=(0, 20.4), ylim=(0.2, 15.0))
    # refrigerator and probe
    ax.add_patch(FancyBboxPatch((0.1, 2.9), 3.75, 10.3, boxstyle="round,pad=0.02,rounding_size=0.2",
                                fc="#EAF4FB", ec=SKY, lw=1.0, ls="--"))
    ax.text(1.97, 12.7, "refrigerator", ha="center", fontsize=7.5, color="#3D7FA6",
            style="italic")
    rbox(ax, 0.35, 7.3, 3.25, 4.9, "Probe assembly\n\nTMP117-class\nsensor potted\nin a 10 mL\nglycol–water\nvial",
         fc="white", fs=7.6)
    ax.text(1.97, 6.9, "IF1: I²C 100 kHz\n+ ALERT + 3.0 V\n+ GND, ESD\nprotection;\n1.5 m cable,\n"
            "0.6 mm flat section\nat the door seal", ha="center", va="top", fontsize=6.9,
            color=C_DIG, linespacing=1.12)
    # enclosure
    ex0, ey0, ex1, ey1 = 5.05, 0.45, 14.25, 14.3
    ax.add_patch(FancyBboxPatch((ex0, ey0), ex1 - ex0, ey1 - ey0,
                                boxstyle="round,pad=0.02,rounding_size=0.25", fc="#F7F7F7",
                                ec=INK, lw=1.3, ls="--"))
    ax.text(ex0 + 0.25, ey1 - 0.4, "main board in IP54 enclosure", fontsize=7.8, style="italic",
            va="center")
    # blocks
    sx, sy, sw, sh = 8.6, 5.4, 3.5, 4.2
    rbox(ax, sx, sy, sw, sh, "Cellular SiP\n\nCortex-M33\nLTE-M / NB-IoT\nmodem · RTC\nwatchdog\ncrypto",
         fc="#DCE6F2", fs=7.6, lw=1.4)
    rbox(ax, 6.2, 11.0, 2.1, 1.7, "2 MB SPI\nNOR flash", fs=7.4)
    rbox(ax, 8.9, 11.0, 2.2, 1.7, "2.9 in\ne-paper", fs=7.4)
    rbox(ax, 12.45, 11.0, 1.55, 1.7, "flex\nLTE\nantenna", fs=7.0)
    rbox(ax, 12.6, 7.4, 1.4, 1.1, "eSIM", fs=7.4)
    rbox(ax, 12.6, 3.7, 1.4, 2.4, "buzzer,\nLEDs,\nbutton", fs=6.9)
    rbox(ax, 5.35, 4.9, 2.1, 1.5, "load\nswitch", fs=7.4, fc="#FBEAEA")
    rbox(ax, 5.35, 0.75, 2.9, 1.6, "2 × ER14505\n+ PTC fuse", fs=7.4, fc="#FBEAEA")
    rbox(ax, 8.9, 0.75, 1.9, 1.6, "EDLC\n0.47 F", fs=7.4, fc="#FBEAEA")
    rbox(ax, 11.4, 0.75, 2.6, 1.6, "470 µF\npolymer", fs=7.4, fc="#FBEAEA")
    # power
    ry = 3.0
    ax.plot([6.8, 12.7], [ry, ry], color=C_PWR, lw=1.8, zorder=2)
    ax.plot([6.8, 6.8], [2.35, ry], color=C_PWR, lw=1.8, zorder=2)
    ax.text(6.65, 2.68, "IF2", color=C_PWR, fontsize=7.5, weight="bold", ha="right",
            va="center")
    for x in (9.85, 12.7):
        ax.plot([x, x], [2.35, ry], color=C_PWR, lw=1.4, zorder=2)
    arr(ax, 10.35, ry, 10.35, sy, color=C_PWR, lw=1.6)
    ax.text(10.5, 4.2, "3.6 V rail\n(no regulator)", color=C_PWR, fontsize=6.8, va="center")
    arr(ax, 6.4, ry, 6.4, 4.9, color=C_PWR, lw=1.4)
    # switched rail to flash and display (hops over IF1)
    yh = 8.4
    ax.plot([5.75, 5.75], [6.4, yh - 0.22], color=C_PWR, lw=1.4)
    ax.plot([5.75, 5.75, 10.0], [yh + 0.22, 13.3, 13.3], color=C_PWR, lw=1.4)
    arr(ax, 7.25, 13.3, 7.25, 12.7, color=C_PWR, lw=1.4)
    arr(ax, 10.0, 13.3, 10.0, 12.7, color=C_PWR, lw=1.4)
    ax.text(5.9, 7.35, "switched\nrail", color=C_PWR, fontsize=6.6, va="center")
    # EN
    arr(ax, sx, 5.65, 7.45, 5.65, color=C_DIG, lw=1.0)
    ax.text(8.0, 5.8, "EN", color=C_DIG, fontsize=6.6, ha="center", va="bottom")
    # IF1
    arr(ax, 3.6, yh, sx, yh, color=C_DIG, both=True, lw=1.5, z=4)
    ax.text(4.45, yh + 0.15, "IF1", color=C_DIG, fontsize=7.5, weight="bold", ha="center",
            va="bottom")
    # IF4, IF3
    poly(ax, [(sx, 9.15), (7.6, 9.15), (7.6, 11.0)], color=C_DIG, both=True, lw=1.1)
    ax.text(7.45, 10.1, "IF4 SPI\n8 MHz", color=C_DIG, fontsize=6.8, ha="right", va="center")
    arr(ax, 9.6, sy + sh, 9.6, 11.0, color=C_DIG, both=True)
    ax.text(9.75, 10.3, "IF3 SPI\n4 MHz", color=C_DIG, fontsize=6.8, ha="left", va="center")
    # RF and eSIM
    arr(ax, 11.7, sy + sh, 12.9, 11.0, color=C_RF, lw=1.5, both=True)
    arr(ax, sx + sw, 7.95, 12.6, 7.95, color=C_DIG, both=True)
    arr(ax, sx + sw, 4.9, 12.6, 4.9, color=C_DIG, both=True)
    # right side
    rbox(ax, 15.1, 11.2, 3.6, 1.8, "Cellular network\nLTE-M / NB-IoT", fs=7.6, fc=LIGHT)
    arr(ax, 14.0, 12.1, 15.1, 12.1, color=C_RF, lw=1.5, both=True)
    ax.text(14.55, 12.25, "IF5", color=C_RF, fontsize=7.5, weight="bold", ha="center",
            va="bottom")
    rbox(ax, 15.1, 5.6, 5.2, 3.8, "Cloud service\n\nintake · alarm engine\ndashboard · SMS",
         fs=7.8, fc="#E8EEF5")
    arr(ax, 16.9, 11.2, 16.9, 9.4, color=C_NET, lw=1.5, both=True)
    ax.text(17.05, 10.3, "IF6 MQTT/TLS\n(QoS 1)", color=C_NET, fontsize=7, ha="left",
            va="center")
    rbox(ax, 15.1, 0.75, 2.9, 1.6, "Officer\nphones", fs=7.6, fc=LIGHT)
    arr(ax, 16.55, 5.6, 16.55, 2.35, color=C_NET, lw=1.5)
    ax.text(16.7, 3.6, "IF8 SMS,\napp push", color=C_NET, fontsize=7, ha="left", va="center")
    rbox(ax, 18.5, 0.75, 1.8, 1.6, "Nurse", fs=7.6, fc=LIGHT)
    poly(ax, [(14.0, 4.9), (19.4, 4.9), (19.4, 2.35)], color=C_HUM, lw=1.5, both=True)
    ax.text(18.0, 5.05, "IF7", color=C_HUM, fontsize=7.5, weight="bold", ha="center",
            va="bottom")
    # legend
    lx, ly = 0.3, 2.35
    for i, (c, t) in enumerate([(C_PWR, "power"), (C_DIG, "digital"), (C_RF, "RF"),
                                (C_HUM, "human"), (C_NET, "network")]):
        xx = lx + (i % 2) * 2.3
        yy = ly - (i // 2) * 0.62
        ax.plot([xx, xx + 0.6], [yy, yy], color=c, lw=1.8)
        ax.text(xx + 0.75, yy, t, va="center", fontsize=7.2)
    save(fig, "02", "fig-2-2-ccm1-physical-architecture")


# ----------------------------------------------------------------------------
# Figure 2.3 — data flow
# ----------------------------------------------------------------------------
def fig_2_3():
    fig, ax = schematic(6.8, 5.0, xlim=(0, 20.4), ylim=(0, 15.0))
    W, H = 4.4, 2.75
    fs = 7.0

    def B(x, y, title, body, fc="white", w=W, h=H):
        rbox(ax, x, y, w, h, "", fc=fc, fs=fs)
        ax.text(x + w / 2, y + h - 0.32, title, ha="center", va="top", fontsize=7.6,
                weight="bold", zorder=4)
        ax.text(x + w / 2, y + h - 0.95, body, ha="center", va="top", fontsize=fs, zorder=4,
                linespacing=1.15)
    # row 1 (left to right)
    y1 = 11.6
    B(0.1, y1, "Sensor conversion", "1 per 60 s, 16-bit\n0.0078 °C LSB", fc="#EEF3F8")
    B(5.25, y1, "Validate", "range −40 to +60 °C\nrate < 2 K/min\nI²C status", fc="#EEF3F8")
    B(10.4, y1 - 0.5, "Alarm evaluation", "counters; 60-sample ring\nfor moving mean", fc="#EEF3F8",
      h=1.75)

    B(10.4, y1 + 1.6, "Statistics", "daily min / max / mean", fc="#EEF3F8", h=1.6)
    B(15.6, y1 - 0.4, "Record builder", "1 per 300 s, 8 B:\n4 B time, 2 B temp.\n(0.01 °C), 1 B flags,\n1 B battery",
      fc="#EEF3F8", w=4.7, h=3.4)
    arr(ax, 4.5, y1 + H / 2, 5.25, y1 + H / 2)
    arr(ax, 9.65, y1 + 2.0, 10.4, y1 + 2.3)
    arr(ax, 9.65, y1 + 0.8, 10.4, y1 + 0.3)
    arr(ax, 14.8, y1 + 2.3, 15.6, y1 + 2.0)
    arr(ax, 14.8, y1 + 0.3, 15.6, y1 + 0.6)
    # row 2 (right to left)
    y2 = 6.6
    B(15.6, y2, "RAM page buffer", "256 B = 32 records\n≈ 2.7 h", fc="#FFF4E0", w=4.7)
    B(10.4, y2, "SPI NOR flash ring", "2 MB ≈ 910 days\nat 2304 B/day", fc="#FFF4E0")
    B(5.25, y2, "Uplink queue", "hourly reports batched;\nalarm messages\nsent at once", fc="#FFF4E0")
    B(0.1, y2, "Hourly report", "12 records + 24 B header\n= 120 B binary payload;\nalarm messages",
      fc="#FFF4E0")
    arr(ax, 17.95, y1 - 0.4, 17.95, y2 + H)
    arr(ax, 15.6, y2 + H / 2, 14.8, y2 + H / 2)
    arr(ax, 10.4, y2 + H / 2, 9.65, y2 + H / 2)
    arr(ax, 5.25, y2 + H / 2, 4.5, y2 + H / 2)
    poly(ax, [(11.0, y1 - 0.5), (11.0, 10.55), (7.45, 10.55), (7.45, y2 + H)], color=RED,
         ls="--", lw=1.0)
    ax.text(7.6, 10.2, "alarm messages (immediate)", color=RED, fontsize=6.7, va="center",
            bbox=dict(fc="white", ec="none", pad=0.2))
    # row 3
    y3 = 1.2
    B(0.1, y3, "MQTT / TLS over LTE-M", "≈ 400 B per connection\nwith TLS session\nresumption", fc="#E8F4EC")
    B(5.25, y3, "Cloud store", "records and alarms\nby device and seq", fc="#E8F4EC")
    B(10.4, y3, "Cloud services", "dashboard · alarm engine\n· SMS / app to officers", fc="#E8F4EC")
    B(15.6, y3, "Back to the device", "configuration record;\nfirmware image\n(up to 400 kB in flash)",
      fc="#EEF3F8", w=4.7)
    arr(ax, 2.3, y2, 2.3, y3 + H)
    arr(ax, 4.5, y3 + H / 2 + 0.3, 5.25, y3 + H / 2 + 0.3)
    arr(ax, 9.65, y3 + H / 2, 10.4, y3 + H / 2)
    # side path config/firmware (cloud back to device)
    arr(ax, 14.8, y3 + 0.7, 15.6, y3 + 0.7, color=C_NET, lw=1.1, ls="--")
    # loss points
    def loss(x, y, t, ha="left"):
        ax.plot([x], [y], marker="X", ms=9, color=RED, mec="white", mew=0.6, zorder=6)
        ax.text(x + (0.3 if ha == "left" else -0.3), y, t, color=RED, fontsize=6.8, ha=ha,
                va="center", zorder=6, bbox=dict(fc="white", ec="none", pad=0.3))
    loss(15.95, y2 - 0.4, "power loss: up to 31 records\n(flushed on low battery)", ha="left")
    loss(2.3, 5.1, "radio outage: queue\nholds 30 days", ha="left")
    loss(5.6, y3 - 0.45, "duplicate deliveries (QoS 1)\nfiltered by seq", ha="left")
    ax.text(0.1, 14.75, "device", fontsize=7.5, style="italic", color="#555555")
    ax.text(5.3, 4.5, "network and cloud", fontsize=7.5, style="italic", color="#555555")
    save(fig, "02", "fig-2-3-ccm1-data-flow")


# ----------------------------------------------------------------------------
# Figure 2.4 — energy budget
# ----------------------------------------------------------------------------
def fig_2_4():
    SPM = 30 * 86400
    items = [("LTE-M hourly report", 0.125, 720, True),
             ("LTE-M tracking-area update", 0.10, 60, True),
             ("e-paper partial refresh", 2.4e-3, 4320, False),
             ("alarm events", 0.375 + 1.8, 4, False),
             ("sleep floor (SiP PSM + RTC)", None, 3.0e-6, False),
             ("supercapacitor leakage", None, 1.5e-6, False),
             ("TMP117", None, 0.43e-6, False),
             ("MCU wake (1/min)", 15e-6, 43200, False),
             ("firmware update", 3.6, 2 / 12, False),
             ("e-paper full refresh", 12e-3, 30, False)]
    good = np.array([(n if q is None else q * n / SPM) for _, q, n, _ in items]) * 1e6
    edge = np.array([g * (4 if lte else 1) for g, (_, _, _, lte) in zip(good, items)])
    usable = 5.2 * 0.85 * (1 - 3 * 0.03) * 0.90
    tg, te = good.sum(), edge.sum()
    fig, ax = new_fig(6.6, 4.2)
    y = np.arange(len(items))[::-1]
    h = 0.38
    ax.barh(y + h / 2, good, height=h, color=BLUE, label="good coverage (×1)")
    ax.barh(y - h / 2, edge, height=h, color=ORANGE, label="cell edge (×4 on LTE-M lines)")
    for yi, g, e, it in zip(y, good, edge, items):
        ax.text(g * 1.08, yi + h / 2, f"{g:.2f}", va="center", fontsize=7)
        if it[3]:
            ax.text(e * 1.08, yi - h / 2, f"{e:.2f}", va="center", fontsize=7, color=ORANGE)
    ax.set_xscale("log")
    ax.set_xlim(0.1, 200)
    ax.set_xticks([0.1, 1, 10, 100])
    ax.set_xticklabels(["0.1", "1", "10", "100"])
    ax.set_yticks(y)
    ax.set_yticklabels([it[0] for it in items], fontsize=8)
    ax.axvline(137.7, color=RED, ls="--", lw=1.2)
    ax.text(128, 2.55, "SP6 allocation\n137.7 µA\n(3-year target)", color=RED,
            fontsize=7.5, ha="right", va="top")
    ax.set_xlabel("Average current (µA, log scale)")
    ax.legend(loc="lower right", fontsize=7.8, bbox_to_anchor=(1.0, 0.0))
    ax.text(4.5, 4.35, f"total, good coverage: {tg:.1f} µA → {usable * 1e6 / tg / 8766:.1f} years",
            fontsize=8, color=BLUE, bbox=dict(fc="white", ec=BLUE, lw=0.8), va="center")
    ax.text(4.5, 3.45, f"total, cell edge: {te:.1f} µA → {usable * 1e6 / te / 8766:.1f} years",
            fontsize=8, color=ORANGE, bbox=dict(fc="white", ec=ORANGE, lw=0.8), va="center")
    ax.set_ylim(-0.7, len(items) - 0.3)
    save(fig, "02", "fig-2-4-energy-budget")


# ----------------------------------------------------------------------------
# Figure 2.5 — state machines
# ----------------------------------------------------------------------------
def fig_2_5():
    fig, ax = schematic(6.8, 5.2, xlim=(0, 20.4), ylim=(0, 15.6))
    S = dict(fc="#EEF3F8", fs=7.3, weight="bold", rs=0.35)

    def st(x, y, w, h, name, sub=None, **kw):
        k = dict(S)
        k.update(kw)
        rbox(ax, x, y, w, h, "", fc=k["fc"], ec=k.get("ec", INK), lw=k.get("lw", 1.0),
             rs=k["rs"])
        if sub:
            ax.text(x + w / 2, y + h - 0.3, name, ha="center", va="top", fontsize=k["fs"],
                    weight="bold", zorder=4)
            ax.text(x + w / 2, y + 0.2, sub, ha="center", va="bottom", fontsize=6.5, zorder=4,
                    linespacing=1.1)
        else:
            ax.text(x + w / 2, y + h / 2, name, ha="center", va="center", fontsize=k["fs"],
                    weight="bold", zorder=4)

    def lab(x, y, t, ha="center", va="center", c=INK):
        ax.text(x, y, t, fontsize=6.6, ha=ha, va=va, color=c, zorder=6, linespacing=1.1,
                bbox=dict(fc="white", ec="none", pad=0.25))
    # panel frames
    ax.add_patch(Rectangle((0.05, 3.0), 12.0, 12.5, fc="none", ec=GREY, lw=0.8))
    ax.text(0.3, 15.15, "Device machine (samples, evaluates, annunciates, records)",
            fontsize=7.6, weight="bold", va="center")
    ax.add_patch(Rectangle((13.6, 3.0), 6.75, 12.5, fc="none", ec=GREY, lw=0.8))
    ax.text(13.85, 15.15, "Communication machine", fontsize=7.6, weight="bold", va="center")
    # device states
    st(0.4, 13.0, 2.3, 1.1, "BOOT")
    st(3.6, 13.0, 2.8, 1.1, "SELF_TEST")
    st(3.6, 10.6, 2.8, 1.1, "FAULT", fc="#FBE3E3", ec=RED)
    st(8.2, 13.0, 3.2, 1.1, "NORMAL", fc="#E4F2EA")
    st(8.8, 10.6, 2.8, 1.1, "SAMPLE")
    st(5.2, 8.6, 2.9, 1.1, "EVALUATE")
    st(4.6, 5.7, 4.4, 1.9, "ALARM_ACTIVE", "buzzer 0.5 s every 10 s,\nred LED, enqueue alarm",
       fc="#FBE3E3", ec=RED)
    st(4.6, 3.3, 4.4, 1.6, "ACKNOWLEDGED", "buzzer silent 30 min", fc="#FFF1DC")
    st(0.4, 8.6, 3.2, 1.1, "SENSOR_FAULT", fc="#FBE3E3", ec=RED)
    arr(ax, 2.7, 13.55, 3.6, 13.55)
    arr(ax, 6.4, 13.55, 8.2, 13.55)
    lab(7.3, 13.85, "pass", va="bottom")
    arr(ax, 5.0, 13.0, 5.0, 11.7)
    lab(5.0, 12.35, "fail")
    arr(ax, 10.6, 13.0, 10.6, 11.7)
    lab(10.6, 12.35, "60 s tick")
    arr(ax, 8.8, 11.0, 7.3, 9.7)
    arr(ax, 7.4, 9.7, 8.6, 13.0, rad=-0.25)
    lab(7.75, 12.3, "no alarm\nchange", ha="left", c="#444444")
    arr(ax, 6.65, 8.6, 6.65, 7.6)
    lab(6.65, 8.12, "alarm bit set")
    arr(ax, 5.2, 9.15, 3.6, 9.15)
    lab(4.4, 9.55, "5 invalid\nsamples", va="bottom")
    arr(ax, 5.6, 5.7, 5.6, 4.9)
    lab(5.6, 5.3, "button")
    arr(ax, 8.0, 4.9, 8.0, 5.7)
    lab(8.0, 5.3, "30 min, condition\nstill true")
    # cleared -> NORMAL via right-hand bus
    poly(ax, [(9.0, 6.65), (11.75, 6.65), (11.75, 13.55), (11.4, 13.55)], color=GREEN, lw=1.1)
    poly(ax, [(9.0, 4.1), (11.75, 4.1), (11.75, 6.65)], color=GREEN, lw=1.1, end=False)
    lab(11.6, 9.0, "condition cleared\n(0.3 °C hysteresis);\nenqueue clear", ha="right", c=GREEN)
    # communication states
    st(14.3, 13.0, 3.0, 1.1, "PSM_SLEEP", fc="#E4F2EA")
    st(14.3, 9.8, 3.0, 1.1, "CONNECTING")
    st(14.3, 6.6, 3.0, 1.1, "SENDING")
    st(14.3, 3.4, 3.0, 1.1, "BACKOFF", fc="#FFF1DC")
    arr(ax, 15.8, 13.0, 15.8, 10.9)
    lab(15.8, 11.95, "alarm queued or\nhourly timer")
    arr(ax, 15.8, 9.8, 15.8, 7.7)
    lab(15.8, 8.75, "connected")
    # acknowledged -> PSM_SLEEP
    poly(ax, [(17.3, 7.15), (18.0, 7.15), (18.0, 13.3), (17.3, 13.3)], color=GREEN, lw=1.1)

    def vlab(x, y, t, c=INK):
        ax.text(x, y, t, fontsize=6.5, ha="center", va="center", color=c, rotation=90,
                zorder=6, bbox=dict(fc="white", ec="none", pad=0.25))
    vlab(18.0, 10.2, "acknowledged", c=GREEN)
    # failures -> BACKOFF
    arr(ax, 15.2, 6.6, 15.2, 4.5)
    lab(15.2, 5.55, "failure")
    poly(ax, [(14.3, 10.1), (13.95, 10.1), (13.95, 4.0), (14.3, 4.0)], color=INK, lw=1.1)
    vlab(13.95, 7.0, "failure")
    # retry
    poly(ax, [(17.3, 3.95), (19.0, 3.95), (19.0, 10.35), (17.3, 10.35)], color=INK, lw=1.1)
    vlab(19.0, 7.2, "retry after 30, 90, 180 s")
    # give up
    poly(ax, [(16.6, 3.4), (16.6, 3.15), (19.95, 3.15), (19.95, 13.8), (17.3, 13.8)], color=INK,
         lw=1.1)
    vlab(19.95, 8.6, "after 3 failures (5 min): message retained")
    # queue coupling
    rbox(ax, 12.2, 7.3, 1.35, 2.3, "", fc="#FFF8D6", ec=INK, lw=0.9, rs=0.05)
    for yy in (7.9, 8.5, 9.1):
        ax.plot([12.2, 13.55], [yy, yy], color=INK, lw=0.6, zorder=4)
    ax.text(12.875, 7.1, "message\nqueue", ha="center", va="top", fontsize=6.6, weight="bold")
    arr(ax, 9.0, 7.1, 12.2, 7.6, color=INK, ls="--", lw=1.0)
    arr(ax, 13.55, 9.4, 14.3, 13.2, color=INK, ls="--", lw=1.0, rad=-0.15)
    ax.text(12.875, 10.0, "only\ncoupling", ha="center", va="bottom", fontsize=6.6,
            style="italic")
    # hardware path
    ax.add_patch(Rectangle((0.05, 0.1), 20.3, 2.5, fc="#FDF2F2", ec=RED, lw=0.8, ls="--"))
    ax.text(0.3, 2.25, "independent hardware path (no firmware)", fontsize=7.2, color=RED,
            weight="bold", va="center")
    rbox(ax, 2.5, 0.4, 5.2, 1.3, "sensor ALERT at −3.0 °C", fs=7.3)
    rbox(ax, 9.6, 0.4, 2.6, 1.3, "latch", fs=7.3)
    rbox(ax, 14.1, 0.4, 3.4, 1.3, "buzzer driver", fs=7.3)
    arr(ax, 7.7, 1.05, 9.6, 1.05, color=RED)
    arr(ax, 12.2, 1.05, 14.1, 1.05, color=RED)
    save(fig, "02", "fig-2-5-ccm1-state-machines")


# ----------------------------------------------------------------------------
# Figure 2.6 — trade-study weight sensitivity
# ----------------------------------------------------------------------------
def fig_2_6():
    w = np.array([0.25, 0.15, 0.20, 0.10, 0.15, 0.15])
    scores = {"LTE-M": [4, 4, 5, 5, 3, 4], "NB-IoT": [3, 5, 5, 3, 4, 4],
              "LoRaWAN": [5, 5, 1, 4, 2, 4], "2G GSM": [5, 2, 5, 5, 4, 1]}
    we = np.linspace(0, 0.5, 201)

    def score(s, x):
        s = np.asarray(s, float)
        others = np.delete(w, 1)
        so = np.delete(s, 1)
        return (so @ others) / others.sum() * (1 - x) + s[1] * x
    fig, ax = new_fig(6.4, 3.9)
    ax.axvspan(0.10, 0.20, color=GREY, alpha=0.13, lw=0)
    ax.text(0.15, 3.03, "range argued\nin workshop", ha="center", va="bottom", fontsize=7.5,
            color="#555555", zorder=5, bbox=dict(fc="#EFEFEF", ec="none", pad=0.4))
    cols = {"LTE-M": BLUE, "NB-IoT": ORANGE, "LoRaWAN": GREEN, "2G GSM": PINK}
    for n, s in scores.items():
        v = score(s, we)
        ax.plot(we, v, color=cols[n], lw=1.9)
        dy = {"LoRaWAN": 0.035, "LTE-M": -0.03}.get(n, 0.0)
        ax.text(0.505, v[-1] + dy, f"{n} {v[-1]:.2f}", color=cols[n], fontsize=8, va="center")
        ax.text(0.004, v[0] + (0.035 if n != "2G GSM" else -0.045), f"{v[0]:.2f}", color=cols[n],
                fontsize=7.5, va="center", ha="left")
        ax.plot([0.15], [score(s, 0.15)], "o", ms=3.5, color=cols[n])
    ax.axvline(0.15, color=INK, ls="--", lw=1.0)
    ax.text(0.152, 4.47, "agreed weight 0.15", fontsize=7.8, va="top")
    a = score(scores["LTE-M"], 0) - score(scores["LTE-M"], 1) * 0
    l0, l1 = score(scores["LTE-M"], 0.0), score(scores["LTE-M"], 0.5)
    n0, n1 = score(scores["NB-IoT"], 0.0), score(scores["NB-IoT"], 0.5)
    xc = (n0 - l0) / ((l1 - l0) / 0.5 - (n1 - n0) / 0.5)
    yc = score(scores["LTE-M"], xc)
    ax.plot([xc], [yc], "D", ms=7, mfc="white", mec=INK, mew=1.3, zorder=5)
    ax.annotate(f"rank reversal\nw = {xc:.2f}, score {yc:.2f}", (xc, yc), (0.31, 4.38),
                fontsize=7.8, arrowprops=dict(arrowstyle="-", lw=0.7))
    ax.set_xlim(0, 0.5)
    ax.set_ylim(3.0, 4.5)
    ax.set_xlabel("Weight on energy per message (other weights renormalised)")
    ax.set_ylabel("Weighted score (1–5 scale)")
    del a
    save(fig, "02", "fig-2-6-trade-weight-sensitivity")


if __name__ == "__main__":
    fig_2_1()
    fig_2_2()
    fig_2_3()
    fig_2_4()
    fig_2_5()
    fig_2_6()
