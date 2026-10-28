"""Figures for Chapter 31 — Engineering Software Architecture.

Run from the repository root:  python figures/scripts/ch31.py
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Polygon, Rectangle  # noqa: E402

from figstyle import COLORS, INK, box, new_fig, save, schematic  # noqa: E402

BLUE, ORANGE, GREEN, PINK, YELLOW, SKY = COLORS[:6]
RED = "#C62828"
GREY = "#777777"
AMBER = "#F2B33D"


def tint(c, a="30"):
    return c + a


def line(ax, pts, color=INK, lw=1.1, ls="-", arrow_end=False, ms=10):
    """Poly-line through pts with an optional arrow head on the last segment."""
    xs, ys = zip(*pts)
    if not arrow_end:
        ax.plot(xs, ys, color=color, lw=lw, ls=ls, solid_capstyle="butt")
        return
    if len(pts) > 2:
        ax.plot(xs[:-1], ys[:-1], color=color, lw=lw, ls=ls)
    ax.annotate("", xy=pts[-1], xytext=pts[-2],
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, ls=ls,
                                shrinkA=0, shrinkB=0, mutation_scale=ms))


def sch(w, h, xlim, ylim):
    """schematic() with the axes filling the figure, so drawing units use the full size."""
    fig, ax = schematic(w, h, xlim=xlim, ylim=ylim)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    return fig, ax


def rbox(ax, x, y, w, h, fc="white", ec=INK, lw=1.0, r=0.25, ls="-", z=1):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                                fc=fc, ec=ec, lw=lw, ls=ls, zorder=z))


# ----------------------------------------------------------------------------
# IEC 60364-5-52 subset and the sizing service (Listings 31.3 and 31.4)
# ----------------------------------------------------------------------------
SIZES = (16, 35, 70, 95, 120, 150, 185, 240)
CAP = dict(zip(SIZES, (100, 158, 246, 298, 346, 399, 456, 538)))
R20 = dict(zip(SIZES, (1.15, 0.524, 0.268, 0.193, 0.153, 0.124, 0.0991, 0.0754)))
AMB = {30: 1.00, 35: 0.96, 40: 0.91, 45: 0.87}
GRP = {1: 1.00, 2: 0.88, 3: 0.82, 4: 0.77, 6: 0.73, 9: 0.72}


def _row(table, x):
    return table[min(k for k in table if k >= x)]


def size_circuit(I_B, ambient_C, length_m=120.0, pf=0.85, grouped=4, vd_limit=5.0,
                 V=400.0, x_km=0.075):
    """Return (csa, Iz, vd, governed_by) or None when no size qualifies."""
    k = _row(AMB, ambient_C) * _row(GRP, grouped)
    sphi = math.sqrt(1 - pf ** 2)
    gov = "current"
    for csa in SIZES:
        Iz = CAP[csa] * k
        if Iz < I_B:
            continue
        r = R20[csa] * (1 + 0.00393 * (90.0 - 20))
        vd = 100 * math.sqrt(3) * I_B * length_m / 1000 * (r * pf + x_km * sphi) / V
        if vd <= vd_limit:
            return csa, Iz, vd, gov
        gov = "voltage drop"
    return None


# ----------------------------------------------------------------------------
# Figure 31.1 — layered architecture
# ----------------------------------------------------------------------------
def fig_31_1():
    fig, ax = sch(6.8, 5.0, xlim=(0, 17), ylim=(-1.3, 11.4))
    # rings (outer to inner)
    rbox(ax, 0.2, 0.0, 13.6, 11.2, fc="#F4F4F4", r=0.5)
    rbox(ax, 0.9, 2.2, 12.2, 6.8, fc=tint(SKY, "26"), r=0.45)
    rbox(ax, 1.6, 3.0, 10.8, 5.2, fc=tint(GREEN, "26"), r=0.4)
    rbox(ax, 4.3, 4.5, 5.4, 2.1, fc=tint(YELLOW, "55"), r=0.3, lw=1.3)
    # ring captions
    ax.text(0.55, 5.6, "Adapters", ha="center", va="center", fontsize=8, color=GREY,
            style="italic", rotation=90)
    ax.text(7.0, 5.95, "Domain model", ha="center", va="center", fontsize=9.5, weight="bold")
    ax.text(7.0, 5.1, "Installation · Circuit · Cable · Method\ninvariants and units",
            ha="center", va="center", fontsize=7.3, linespacing=1.3)
    # API band
    ax.text(1.65, 8.6, "Public API", ha="left", va="center", fontsize=8.5, weight="bold")
    ax.text(4.1, 8.6, "fc_api: size_circuit · open_project · SizingResult", ha="left",
            va="center", fontsize=7.0, family="monospace")
    # services band
    ax.text(1.85, 7.4, "Services", ha="left", va="center", fontsize=8.5, weight="bold")
    for i, t in enumerate(["size_circuit", "voltage drop", "protection check"]):
        x = 3.95 + i * 2.8
        rbox(ax, x, 6.85, 2.65, 1.1, fc="white", r=0.15)
        ax.text(x + 1.325, 7.4, t, ha="center", va="center", fontsize=7.3)
    # ports band
    ax.text(1.85, 3.75, "Ports", ha="left", va="center", fontsize=8.5, weight="bold")
    rbox(ax, 3.4, 3.2, 3.4, 1.1, fc="white", r=0.15)
    ax.text(5.1, 3.75, "Project repository", ha="center", va="center", fontsize=7.3)
    rbox(ax, 8.9, 3.2, 3.3, 1.1, fc="white", ec=BLUE, lw=1.4, r=0.15)
    ax.text(10.55, 3.75, "Standard protocol", ha="center", va="center", fontsize=7.3)

    # adapters (top and bottom bands)
    top = [("Desktop GUI", "Qt view + ProjectViewModel"), ("CLI", "feedercheck"),
           ("PDF report", "checking engineer")]
    bot = [("Project file", "JSON schema 3 +\nmigrations v1→v2→v3"), ("CSV/XLSX import", "load schedules"),
           ("IFC and CSV export", "BIM model, schedules")]
    bw, xs = 4.0, [1.05, 5.25, 9.45]
    for (name, sub), x in zip(top, xs):
        rbox(ax, x, 9.55, bw, 1.4, fc="white", r=0.15)
        ax.text(x + bw / 2, 10.55, name, ha="center", va="center", fontsize=8, weight="bold")
        ax.text(x + bw / 2, 9.95, sub, ha="center", va="center", fontsize=7.0)
        xa = x + bw / 2 + 0.9
        line(ax, [(xa, 9.55), (xa, 9.02)], arrow_end=True, lw=1.1, ms=8)
    for (name, sub), x in zip(bot, xs):
        rbox(ax, x, 0.2, bw, 1.45, fc="white", r=0.15)
        ax.text(x + bw / 2, 1.3, name, ha="center", va="center", fontsize=7.8, weight="bold")
        ax.text(x + bw / 2, 0.68, sub, ha="center", va="center", fontsize=7.0, linespacing=1.15)
        xa = x + bw / 2
        line(ax, [(xa, 1.65), (xa, 2.18)], arrow_end=True, lw=1.1, ms=8)
    ax.text(xs[2] + bw / 2 + 1.05, 9.28, "imports", ha="left", va="center", fontsize=7, color=INK)
    ax.text(xs[2] + bw / 2 + 0.15, 1.92, "imports", ha="left", va="center", fontsize=7, color=INK)

    # plug-ins outside, docked to the Standard port
    plugs = [("IEC 60364-5-52", "built-in"), ("BS 7671", "entry-point plug-in"),
             ("NEC 310.16", "entry-point plug-in")]
    for i, (name, sub) in enumerate(plugs):
        y = 5.6 - i * 1.75
        built = i == 0
        rbox(ax, 14.1, y, 2.85, 1.3, fc=tint(BLUE, "22") if built else "white", ec=BLUE,
             ls="-" if built else (0, (3, 2)), r=0.15)
        ax.text(15.525, y + 0.87, name, ha="center", va="center", fontsize=7.6, weight="bold")
        ax.text(15.525, y + 0.38, sub, ha="center", va="center", fontsize=6.7)
        line(ax, [(14.1, y + 0.65), (12.2, 3.75)], color=BLUE, arrow_end=True, lw=1.0, ms=8)
    ax.text(15.525, 7.85, "Plug-ins", ha="center", va="center", fontsize=8.5, weight="bold",
            color=BLUE)
    ax.text(15.525, 7.35, "implement Standard", ha="center", va="center", fontsize=7, color=BLUE)

    # forbidden arrow: Domain -> GUI, routed up the left side
    line(ax, [(4.3, 5.55), (1.3, 5.55), (1.3, 9.53)], color=RED, arrow_end=True, lw=1.4)
    mx, my = 1.3, 6.55
    ax.plot([mx - 0.28, mx + 0.28], [my - 0.28, my + 0.28], color=RED, lw=2.2)
    ax.plot([mx - 0.28, mx + 0.28], [my + 0.28, my - 0.28], color=RED, lw=2.2)
    ax.text(1.85, 5.95, "forbidden", ha="left", va="center", fontsize=7.6, color=RED,
            weight="bold")

    ax.text(0.2, -0.6, "All source dependencies point inward.  fc_domain imports only "
            "dataclasses and enum (checked by a test).", ha="left", va="center", fontsize=7.8,
            style="italic")
    save(fig, "31", "fig-31-1-feedercheck-architecture")


# ----------------------------------------------------------------------------
# Figure 31.2 — size staircase at 30 C and 40 C
# ----------------------------------------------------------------------------
def fig_31_2():
    I = np.arange(50.0, 400.01, 0.25)
    idx = {s: i for i, s in enumerate(SIZES)}

    def stair(amb):
        y = np.full(I.shape, np.nan)
        for j, i_b in enumerate(I):
            r = size_circuit(i_b, amb)
            if r:
                y[j] = idx[r[0]]
        return y

    y30, y40 = stair(30), stair(40)
    fig, ax = new_fig(6.4, 4.0)
    # shaded bands where the two staircases differ
    diff = ~(y30 == y40)
    start = None
    for j in range(len(I)):
        if diff[j] and start is None:
            start = I[j]
        if (not diff[j] or j == len(I) - 1) and start is not None:
            ax.axvspan(start, I[j], color=ORANGE, alpha=0.12, lw=0)
            start = None
    ax.step(I, y30, where="post", color=BLUE, ls="--", lw=1.8, label="30 °C ambient (2022 loader default)")
    ax.step(I, y40, where="post", color=INK, lw=1.8, label="40 °C ambient (actual plant room)")
    i_max = CAP[240] * _row(AMB, 40) * _row(GRP, 4)
    ax.plot([i_max], [idx[240]], marker="x", ms=9, mew=2, color=RED)
    ax.annotate(f"40 °C: no size in the 240 mm²" + chr(10) + f"subset above {i_max:.0f} A", xy=(i_max, idx[240]),
                xytext=(396, 4.1), fontsize=8, color=RED, ha="right", va="center",
                arrowprops=dict(arrowstyle="-", color=RED, lw=0.8, shrinkB=5))
    # incident marker
    ax.plot([300], [idx[150]], "o", mfc="white", mec=BLUE, ms=7, mew=1.6, zorder=5)
    ax.plot([300], [idx[185]], "o", color=INK, ms=7, zorder=5)
    ax.annotate("", xy=(300, idx[185] - 0.12), xytext=(300, idx[150] + 0.12),
                arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.5, mutation_scale=11))
    ax.text(56, 5.35, chr(10).join(["2023 incident at 300 A:", "150 mm² (30 °C default) is good",
                                    "for only 279.6 A at 40 °C;", "correct size 185 mm²"]),
            ha="left", va="center", fontsize=8, color=RED)
    ax.plot([203, 297], [5.55, 5.55], color=RED, lw=0.7)
    ax.set_yticks(range(len(SIZES)))
    ax.set_yticklabels([str(s) for s in SIZES])
    ax.set_ylim(-0.5, 7.5)
    ax.set_xlim(50, 400)
    ax.set_xlabel("Design current $I_B$ (A)")
    ax.set_ylabel("Conductor cross-section (mm²)")
    ax.grid(axis="y", color="#E6E6E6", lw=0.6)
    ax.legend(loc="upper left", fontsize=8.2)
    ax.text(392, 0.05, "Cu XLPE, method E (tray), 120 m\ngrouping factor 0.77 (4 circuits)\n"
            "power factor 0.85, VD limit 5 %\nshaded: sizes differ",
            ha="right", va="bottom", fontsize=7.8,
            bbox=dict(boxstyle="round,pad=0.4", fc="white", ec=GREY, lw=0.8))
    save(fig, "31", "fig-31-2-size-staircase")


# ----------------------------------------------------------------------------
# Figure 31.3 — project-file load pipeline
# ----------------------------------------------------------------------------
def _diamond(ax, cx, cy, w, h, text, fc="white", fs=8):
    ax.add_patch(Polygon([(cx - w / 2, cy), (cx, cy + h / 2), (cx + w / 2, cy), (cx, cy - h / 2)],
                         closed=True, fc=fc, ec=INK, lw=1.0))
    ax.text(cx, cy, text, ha="center", va="center", fontsize=fs)


def _term(ax, cx, cy, w, h, text, color, fs=7.8):
    ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h,
                                boxstyle=f"round,pad=0,rounding_size={h / 2}",
                                fc=tint(color, "26"), ec=color, lw=1.3))
    ax.text(cx, cy, text, ha="center", va="center", fontsize=fs, color=INK)


def _proc(ax, cx, cy, w, h, text, fs=8, fc="white", ec=INK, family=None):
    rbox(ax, cx - w / 2, cy - h / 2, w, h, fc=fc, ec=ec, r=0.12)
    ax.text(cx, cy, text, ha="center", va="center", fontsize=fs, family=family, linespacing=1.25)


def fig_31_3():
    fig, ax = sch(6.8, 5.0, xlim=(0, 17), ylim=(0.3, 12.8))
    cx = 8.0
    A = dict(arrow_end=True, lw=1.1, ms=9)
    # row 1: read -> parse
    _proc(ax, 3.4, 12.0, 4.4, 0.85, "Read text (UTF-8)")
    _proc(ax, cx, 12.0, 3.2, 0.85, "Parse JSON")
    line(ax, [(5.6, 12.0), (cx - 1.6, 12.0)], **A)
    # diamond 1
    d1y = 10.45
    line(ax, [(cx, 11.575), (cx, d1y + 0.7)], **A)
    _diamond(ax, cx, d1y, 4.2, 1.4, "schema key\npresent?")
    _proc(ax, 3.0, d1y, 3.0, 0.8, "version = 1", family="monospace", fs=7.8)
    _proc(ax, 13.0, d1y, 3.6, 0.8, "version = schema", family="monospace", fs=7.8)
    line(ax, [(cx - 2.1, d1y), (4.5, d1y)], **A)
    line(ax, [(cx + 2.1, d1y), (11.2, d1y)], **A)
    ax.text(cx - 2.35, d1y + 0.12, "no", ha="right", va="bottom", fontsize=7.8)
    ax.text(cx + 2.35, d1y + 0.12, "yes", ha="left", va="bottom", fontsize=7.8)
    # merge to diamond 2
    d2y = 8.45
    line(ax, [(3.0, d1y - 0.4), (3.0, 9.45), (cx - 0.05, 9.45)])
    line(ax, [(13.0, d1y - 0.4), (13.0, 9.45), (cx + 0.05, 9.45)])
    line(ax, [(cx, 9.45), (cx, d2y + 0.65)], **A)
    _diamond(ax, cx, d2y, 4.0, 1.3, "version > 3?")
    _term(ax, 13.4, d2y, 5.0, 0.9, "Refuse: file is newer\nthan program", RED, fs=7.6)
    line(ax, [(cx + 2.0, d2y), (10.9, d2y)], **A)
    ax.text(cx + 2.2, d2y + 0.12, "yes", ha="left", va="bottom", fontsize=7.8)
    ax.text(cx + 0.2, d2y - 0.85, "no", ha="left", va="center", fontsize=7.8)
    # migration loop box
    ly0, ly1 = 4.75, 7.35
    line(ax, [(cx, d2y - 0.65), (cx, ly1)], **A)
    rbox(ax, 3.7, ly0, 8.6, ly1 - ly0, fc=tint(SKY, "1E"), ec=BLUE, r=0.2, ls=(0, (4, 2)))
    ax.text(cx, 6.95, "while version < 3:  d = MIGRATIONS[version](d)", ha="center",
            va="center", fontsize=7.6, family="monospace", color=BLUE)
    _proc(ax, 5.9, 5.65, 3.9, 1.2, "v1 → v2\ncopy project ambient_C\ninto each circuit", fs=7.5)
    _proc(ax, 10.1, 5.65, 3.9, 1.2, "v2 → v3\nrecord standard\nIEC60364-5-52:2009", fs=7.5)
    line(ax, [(7.85, 5.65), (8.15, 5.65)], arrow_end=True, lw=1.0, ms=8)
    # loop-back arrow on the right edge of the loop box
    line(ax, [(12.3, 5.3), (12.75, 5.3), (12.75, 6.6), (12.3, 6.6)], color=BLUE, arrow_end=True,
         lw=1.0, ms=8)
    ax.text(12.9, 5.95, "repeat", ha="left", va="center", fontsize=7.2, color=BLUE)
    # side annotation on v1->v2
    ax.text(1.95, 4.45, "2022 loader used a\n30 °C default here\ninstead", ha="center",
            va="top", fontsize=7.4, color=RED, style="italic")
    line(ax, [(2.5, 4.5), (3.95, 5.2)], color=RED, arrow_end=True, lw=0.9, ms=7)
    # strict construction
    sy = 3.55
    line(ax, [(cx, ly0), (cx, sy + 0.42)], **A)
    _proc(ax, cx, sy, 5.4, 0.84, "Strict construction  Circuit(**fields)", fs=7.6)
    _term(ax, 13.9, sy, 4.4, 0.84, "TypeError: unknown\nor missing field", RED, fs=7.4)
    line(ax, [(cx + 2.7, sy), (11.7, sy)], **A)
    # domain validation
    vy = 2.25
    line(ax, [(cx, sy - 0.42), (cx, vy + 0.42)], **A)
    _proc(ax, cx, vy, 6.0, 0.84, "Domain validation  (__post_init__ ranges)", fs=7.4)
    _term(ax, 13.9, vy, 4.4, 0.84, "ValueError: circuit tag:\nout of range", RED, fs=7.4)
    line(ax, [(cx + 3.0, vy), (11.7, vy)], **A)
    # return
    gy = 0.95
    line(ax, [(cx, vy - 0.42), (cx, gy + 0.42)], **A)
    _term(ax, cx, gy, 5.6, 0.84, "Installation and standard key returned", GREEN, fs=7.8)
    save(fig, "31", "fig-31-3-file-load-pipeline")


# ----------------------------------------------------------------------------
# Figure 31.4 — GUI layout
# ----------------------------------------------------------------------------
def fig_31_4():
    W, H = 1280, 800
    fig, ax = plt.subplots(figsize=(6.8, 5.15))
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax.set_xlim(-70, W + 70)
    ax.set_ylim(H + 210, -8)   # y downward like screen pixels
    ax.set_aspect("equal")
    ax.axis("off")

    def rect(x, y, w, h, fc="white", ec="#888888", lw=0.8, **kw):
        ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec=ec, lw=lw, **kw))

    def txt(x, y, s, fs=6.6, **kw):
        kw.setdefault("ha", "left")
        kw.setdefault("va", "center")
        ax.text(x, y, s, fontsize=fs, color=kw.pop("color", INK), **kw)

    rect(0, 0, W, H, fc="#FAFAFA", ec=INK, lw=1.3)
    # title bar
    rect(0, 0, W, 30, fc="#DCE3EA", ec=INK, lw=1.0)
    txt(12, 15, "FeederCheck 4.2  —  hospital_2020.fcj *", fs=7.4, weight="bold")
    txt(W - 12, 15, "1280 × 800 px", fs=6.4, ha="right", color=GREY)
    # toolbar
    rect(0, 30, W, 38, fc="#F0F0F0")
    x = 10
    for b in ["Open", "Save", "Undo", "Redo", "Import CSV", "Export IFC", "Report"]:
        bw = 22 + 11.0 * len(b)
        ax.add_patch(FancyBboxPatch((x, 37), bw, 24, boxstyle="round,pad=0,rounding_size=4",
                                    fc="white", ec="#999999", lw=0.8))
        txt(x + bw / 2, 49, b, fs=6.8, ha="center")
        x += bw + 8

    # circuit table (left 62 %)
    tx, ty, tw, th = 8, 76, 852, 540
    rect(tx, ty, tw, th, fc="white", ec="#888888")
    txt(tx + 6, ty + 13, "Circuits", fs=7.2, weight="bold")
    cols = ["Tag", "I_B\n(A)", "Length\n(m)", "PF", "Meth.", "Amb.\n(°C)", "Grp.",
            "VD lim.\n(%)", "Cable\n(mm²)", "I_z\n(A)", "VD\n(%)", "Governed\nby"]
    widths = np.array([66, 46, 62, 48, 54, 52, 46, 64, 60, 60, 50, 132])
    widths = widths * (tw - 12) / widths.sum()
    xs = tx + 6 + np.concatenate([[0], np.cumsum(widths)])
    hy0, hy1 = ty + 26, ty + 66
    rect(tx + 6, hy0, tw - 12, hy1 - hy0, fc="#E8EDF2", ec="#AAAAAA", lw=0.6)
    for c, x0, w in zip(cols, xs[:-1], widths):
        txt(x0 + w / 2, (hy0 + hy1) / 2, c, fs=5.9, ha="center", weight="bold", linespacing=1.0)
    rows = [["SB-KIT", "300", "120", "0.85", "E", "40", "4", "5.0", "185", "319.5", "2.29", "current"],
            ["DB-L3", "95", "210", "0.95", "E", "40", "2", "3.0", "95", "238.6", "2.22", "voltage drop"]]
    rh = 26
    for r, row in enumerate(rows):
        y0 = hy1 + r * rh
        rect(tx + 6, y0, tw - 12, rh, fc=tint(BLUE, "22") if r == 0 else "white", ec="#CCCCCC", lw=0.5)
        for j, (v, x0, w) in enumerate(zip(row, xs[:-1], widths)):
            if j == 11 and r == 1:
                rect(x0 + 1, y0 + 2, w - 2, rh - 4, fc=AMBER, ec="none")
            txt(x0 + w / 2, y0 + rh / 2, v, fs=6.3, ha="center")
    for k in range(2, 16):
        y0 = hy1 + k * rh
        if y0 + rh > ty + th - 4:
            break
        rect(tx + 6, y0, tw - 12, rh, fc="white", ec="#EEEEEE", lw=0.4)
    txt(tx + 14, hy1 + 2 * rh + rh / 2, "+ add circuit", fs=6.4, color=GREY, style="italic")

    # property panel
    px, py, pw, ph = 868, 76, 404, 268
    rect(px, py, pw, ph, fc="white")
    txt(px + 8, py + 13, "Properties — SB-KIT", fs=7.2, weight="bold")
    fields = [("Tag", "SB-KIT", ""), ("Design current", "300", "A"), ("Length", "120", "m"),
              ("Power factor", "1.3", ""), (None, None, None), ("Method", "E (tray)", ""),
              ("Ambient", "40", "°C"), ("Grouped with", "4", "circ."), ("VD limit", "5.0", "%")]
    for k, (name, val, unit) in enumerate(fields):
        y = py + 38 + k * 25
        if name is None:
            ax.add_patch(FancyBboxPatch((px + 8, y - 10), pw - 16, 20,
                                        boxstyle="round,pad=0,rounding_size=3",
                                        fc="#FFFBE6", ec=RED, lw=0.8, zorder=6))
            txt(px + 14, y, "circuit SB-KIT: out of range: power_factor", fs=6.0,
                color=RED, zorder=7)
            continue
        txt(px + 10, y, name, fs=6.4)
        bad = name == "Power factor"
        rect(px + 180, y - 10, 130, 20, fc="#FFF5F5" if bad else "white",
             ec=RED if bad else "#AAAAAA", lw=1.6 if bad else 0.6)
        txt(px + 186, y, val, fs=6.4)
        txt(px + 318, y, unit, fs=6.4, color=GREY)

    # result panel
    qx, qy, qw, qh = 868, 352, 404, 264
    rect(qx, qy, qw, qh, fc="white")
    txt(qx + 8, qy + 13, "Result — SB-KIT", fs=7.2, weight="bold")
    hdr = ["Size\n(mm²)", "I_z\n(A)", "I_z ≥\n300 A", "VD\n(%)", "VD ≤\n5 %"]
    cxs = [qx + 45, qx + 125, qx + 205, qx + 285, qx + 360]
    for h_, c in zip(hdr, cxs):
        txt(c, qy + 42, h_, fs=5.9, ha="center", weight="bold", linespacing=1.0)
    k = _row(AMB, 40) * _row(GRP, 4)
    res = size_circuit(300, 40)
    for n, s in enumerate(SIZES):
        y = qy + 74 + n * 23.5
        Iz = CAP[s] * k
        ok_i = Iz >= 300
        chosen = s == res[0]
        evaluated = s <= res[0]
        if chosen:
            rect(qx + 8, y - 10.5, qw - 16, 21, fc=tint(GREEN, "30"), ec=GREEN, lw=0.9)
        col = INK if evaluated else "#AAAAAA"
        txt(cxs[0], y, str(s), fs=6.5, ha="center", color=col)
        txt(cxs[1], y, f"{Iz:.1f}", fs=6.5, ha="center", color=col)
        if evaluated:
            txt(cxs[2], y, "✓" if ok_i else "✗", fs=7.5, ha="center",
                color=GREEN if ok_i else RED, weight="bold")
            if ok_i:
                txt(cxs[3], y, f"{res[2]:.2f}", fs=6.5, ha="center")
                txt(cxs[4], y, "✓", fs=7.5, ha="center", color=GREEN, weight="bold")
            else:
                txt(cxs[3], y, "—", fs=6.5, ha="center", color=GREY)
                txt(cxs[4], y, "—", fs=6.5, ha="center", color=GREY)
        else:
            txt(cxs[2] - 30, y, "not evaluated", fs=6.0, ha="left", color="#AAAAAA", style="italic")

    # message list
    mx, my, mw, mh = 8, 624, W - 16, 132
    rect(mx, my, mw, mh, fc="white")
    txt(mx + 6, my + 13, "Messages", fs=7.2, weight="bold")
    msgs = [("error", RED, "circuit SB-KIT: out of range: power_factor  (edit rejected, model unchanged)"),
            ("info", BLUE, "opened hospital_2020.fcj: schema 1 migrated to 3, ambient_C = 40 °C copied to 2 circuits"),
            ("info", BLUE, "2 circuits sized with IEC60364-5-52:2009")]
    for n, (lvl, c, m) in enumerate(msgs):
        y = my + 40 + n * 26
        txt(mx + 14, y, lvl, fs=6.4, color=c, weight="bold")
        txt(mx + 84, y, m, fs=6.4)
    # status bar
    rect(0, 764, W, 36, fc="#E8EDF2", ec=INK, lw=0.8)
    status = ["standard IEC60364-5-52:2009", "schema 3", "unsaved changes", "undo depth 1"]
    x = 14
    for s in status:
        txt(x, 782, s, fs=6.4)
        x += 10.6 * len(s) + 40
        if s != status[-1]:
            ax.plot([x - 22, x - 22], [770, 794], color="#999999", lw=0.6)

    # view model box and binding arrows
    vx, vy, vw, vh = 410, 900, 460, 70
    ax.add_patch(FancyBboxPatch((vx, vy), vw, vh, boxstyle="round,pad=0,rounding_size=10",
                                fc=tint(YELLOW, "50"), ec=INK, lw=1.2))
    txt(vx + vw / 2, vy + 24, "ProjectViewModel", fs=8.5, ha="center", weight="bold")
    txt(vx + vw / 2, vy + 50, "no Qt import · undo stack · results · errors", fs=6.6, ha="center")
    ac = "#555555"
    # table: out of the left edge, down, into VM
    line(ax, [(tx, 340), (-45, 340), (-45, vy + 35), (vx, vy + 35)], color=ac, arrow_end=True,
         lw=0.8, ms=7)
    # property and result panels: out of the right edge
    line(ax, [(W - 8, 200), (W + 45, 200), (W + 45, vy + 35), (vx + vw, vy + 35)], color=ac,
         arrow_end=True, lw=0.8, ms=7)
    line(ax, [(W - 8, 480), (W + 45, 480)], color=ac, lw=0.8)
    # message list and status bar: straight down
    line(ax, [(380, H), (380, 840), (vx + 60, 840), (vx + 60, vy)], color=ac, arrow_end=True,
         lw=0.8, ms=7)
    line(ax, [(900, H), (900, 840), (vx + vw - 60, 840), (vx + vw - 60, vy)], color=ac,
         arrow_end=True, lw=0.8, ms=7)
    txt(-40, 860, "table", fs=6.2, color=ac)
    txt(W + 40, 860, "property and\nresult panels", fs=6.2, color=ac, ha="right")
    txt(372, 820, "messages", fs=6.2, color=ac, ha="right")
    txt(910, 820, "status bar", fs=6.2, color=ac)
    save(fig, "31", "fig-31-4-gui-layout")


# ----------------------------------------------------------------------------
# Figure 31.5 — latency scaling
# ----------------------------------------------------------------------------
def fig_31_5():
    n = np.array([100, 500, 1000, 2000, 5000])
    recalc = np.array([1.6, 8.5, 16.0, 33.2, 165.7])
    opn = np.array([1.7, 14.0, 17.4, 39.1, 148.2])
    sav = np.array([3.5, 21.9, 41.7, 72.0, 232.5])
    fig, ax = new_fig(6.4, 4.2)
    ax.loglog(n, recalc, "o-", color=BLUE, label="recalculate all")
    ax.loglog(n, opn, "s-", color=GREEN, label="open (read, migrate, construct)")
    ax.loglog(n, sav, "^-", color=ORANGE, label="save")
    nr = np.array([80, 6000])
    ax.loglog(nr, 16.0 * nr / 1000, ls="--", color=GREY, lw=1.1)
    ax.text(5600, 16.0 * 5600 / 1000 * 0.62, "slope 1\n(linear)", fontsize=7.8, color=GREY,
            ha="center", va="top")
    # budgets
    ax.axhline(1000, color=BLUE, ls=(0, (5, 3)), lw=1.1)
    ax.text(6500, 900, "R5 budget: recalculate 500 circuits ≤ 1000 ms", fontsize=7.8,
            color=BLUE, va="top", ha="right")
    ax.plot([500], [8.5], "o", ms=11, mfc="none", mec=BLUE, mew=1.2)
    ax.axhline(2000, color=GREEN, ls=(0, (5, 3)), lw=1.1)
    ax.text(6500, 1850, "R5 budget: open ≤ 2000 ms", fontsize=7.8, color=GREEN, va="top",
            ha="right")
    # old GUI and incremental edit
    ax.plot([3000], [3600], "D", color=RED, ms=7)
    ax.annotate("version 2: whole-table\nrebuild per keystroke, 3.6 s", xy=(3000, 3600),
                xytext=(1350, 3600), fontsize=7.8, color=RED, ha="right", va="center",
                arrowprops=dict(arrowstyle="-", color=RED, lw=0.8))
    ax.plot([3000], [1.0], "D", color=PINK, ms=7)
    ax.annotate("version 4: incremental edit\nper keystroke, about 1 ms", xy=(3000, 1.0),
                xytext=(2600, 1.9), fontsize=7.8, color=PINK, ha="right", va="bottom",
                arrowprops=dict(arrowstyle="-", color=PINK, lw=0.8))
    ax.set_xlim(80, 7000)
    ax.set_ylim(0.7, 6000)
    ax.set_xlabel("Number of circuits")
    ax.set_ylabel("Time (ms)")
    ax.grid(True, which="major", color="#E6E6E6", lw=0.6)
    ax.legend(loc="center left", bbox_to_anchor=(0.0, 0.62), fontsize=8)
    ax.text(0.03, 0.47, "measured: one run on a loaded\nworkstation, best of five",
            transform=ax.transAxes, ha="left", va="top", fontsize=7.6, style="italic", color=GREY)
    save(fig, "31", "fig-31-5-latency-scaling")


if __name__ == "__main__":
    fig_31_1()
    fig_31_2()
    fig_31_3()
    fig_31_4()
    fig_31_5()
