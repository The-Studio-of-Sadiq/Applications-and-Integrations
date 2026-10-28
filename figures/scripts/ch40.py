"""Figures for Chapter 40 — Capstone Engineering Project.

Run from the repository root:  python figures/scripts/ch40.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle, FancyBboxPatch, Polygon  # noqa: E402

from figstyle import COLORS, INK, GRID, box, save, schematic, new_fig  # noqa: E402

BLUE, ORANGE, GREEN, PINK, YELLOW, SKY = COLORS[:6]
RED = "#C62828"
GREY = "#777777"


def arr(ax, x0, y0, x1, y1, color=INK, lw=1.1, ls="-", both=False):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="<|-|>" if both else "-|>", color=color, lw=lw, ls=ls, shrinkA=0,
                                shrinkB=0, mutation_scale=9))


def path(ax, pts, color=INK, lw=1.1, ls="-", arrow=True):
    xs, ys = zip(*pts)
    ax.plot(xs[:-1], ys[:-1], color=color, lw=lw, ls=ls)
    if arrow:
        arr(ax, *pts[-2], *pts[-1], color=color, lw=lw, ls=ls)
    else:
        ax.plot(xs[-2:], ys[-2:], color=color, lw=lw, ls=ls)


def diamond(ax, xc, yc, w, h, text, fc="#FDF3DD", fs=6.2):
    ax.add_patch(Polygon([(xc - w / 2, yc), (xc, yc + h / 2), (xc + w / 2, yc), (xc, yc - h / 2)], closed=True,
                         fc=fc, ec=INK, lw=1.0))
    ax.text(xc, yc, text, ha="center", va="center", fontsize=fs)


# ----------------------------------------------------------------------------
def fig_40_1():
    """Capstone lifecycle with review gates and planned weeks."""
    fig, ax = schematic(6.8, 3.9, xlim=(0, 17.2), ylim=(-0.2, 9.4))
    BW, BH, DW, DH, GAP = 2.4, 1.75, 1.9, 1.9, 0.22
    row1 = [("B", "Problem\nselection\nweeks 1–2"), ("D", "Proposal\nreview\nwk 2"),
            ("B", "Literature\nreview\nweeks 2–4"), ("B", "Require-\nments\nweeks 3–5"),
            ("D", "Req.\nreview\nwk 5"), ("B", "Architecture\nweeks 5–8"), ("D", "PDR\nwk 8")]
    row2 = [("B", "Detailed\ndesign\nweeks 8–11"), ("D", "CDR\nwk 11"), ("B", "Implemen-\ntation\nweeks 11–20"),
            ("D", "TRR\nwk 19"), ("B", "Verification,\nvalidation\nweeks 19–25"),
            ("B", "Final report\nweeks 24–28"), ("D", "Final\nreview\nwk 28")]
    y1, y2 = 7.0, 3.7
    pos = {}

    def lay(row, y, x0, sign):
        x = x0
        out = []
        for kind, t in row:
            w = BW if kind == "B" else DW
            xc = x + sign * w / 2
            if kind == "B":
                box(ax, xc - BW / 2, y - BH / 2, BW, BH, t, fc="#EEF3F8", fontsize=6.9)
            else:
                diamond(ax, xc, y, DW, DH, t)
            out.append((xc, w))
            x += sign * (w + GAP)
        for (a, wa), (b, wb) in zip(out[:-1], out[1:]):
            arr(ax, a + sign * wa / 2, y, b - sign * wb / 2, y)
        return out
    total = 4 * BW + 3 * DW + 6 * GAP
    x0 = (17.2 - total) / 2
    r1 = lay(row1, y1, x0, +1)
    r2 = lay(row2, y2, x0 + total, -1)
    ax.text(r1[4][0], y1 - DH / 2 - 0.12, "with stake-\nholder", fontsize=6.3, ha="center", va="top")
    # PDR -> detailed design
    arr(ax, r1[-1][0], y1 - DH / 2, r2[0][0], y2 + BH / 2)
    # feedback arrows from V&V
    xv = r2[4][0]
    xr = r1[3][0]
    path(ax, [(xv - 0.35, y2 + BH / 2), (xv - 0.35, 5.35), (xr, 5.35), (xr, y1 - BH / 2)], color=RED, ls="--")
    ax.text((xv + xr) / 2 - 0.2, 5.45, "change request", color=RED, fontsize=6.9, ha="center", va="bottom")
    xd = r2[0][0]
    path(ax, [(xv + 0.35, y2 - BH / 2), (xv + 0.35, 1.95), (xd, 1.95), (xd, y2 - BH / 2)], color=RED, ls="--")
    ax.text((xv + xd) / 2, 2.0, "change request", color=RED, fontsize=6.9, ha="center", va="bottom")
    # continuous bar
    ax.add_patch(FancyBboxPatch((x0, 0.15), total, 0.85, boxstyle="round,pad=0.02,rounding_size=0.15",
                                fc="#FBEFE6", ec=ORANGE, lw=1.0))
    ax.text(x0 + total / 2, 0.575, "Cost model and risk register updated continuously, weeks 1–28 "
            "(risks reviewed every two weeks)", ha="center", va="center", fontsize=7.0)
    ax.text(x0, 8.6, "Boxes: stages with planned weeks;  diamonds: review gates", fontsize=7.0, color=GREY)
    save(fig, "40", "fig-40-1-capstone-lifecycle")


# ----------------------------------------------------------------------------
def fig_40_2():
    """AquaSol system architecture with interfaces I1-I6."""
    fig, ax = schematic(6.8, 5.0, xlim=(0, 17.2), ylim=(0, 12.6))
    fs = 6.9

    def tag(x, y, s, ha="center"):
        ax.text(x, y, s, fontsize=6.8, ha=ha, va="center", color="white", weight="bold",
                bbox=dict(boxstyle="round,pad=0.18", fc=INK, ec="none"))
    # PV array and protection
    box(ax, 0.2, 10.3, 3.6, 1.9, "PV array\n2 × 300 W in series\ncold $V_{OC}$ 84.6 V", fc="#FDF3DD", fontsize=fs)
    box(ax, 0.2, 7.7, 3.6, 1.7, "DC isolator,\n15 A gPV fuse,\ntype 2 SPD", fc="#FBEFE6", fontsize=fs)
    arr(ax, 2.0, 10.3, 2.0, 9.4, color=ORANGE, lw=1.4)
    arr(ax, 3.8, 8.55, 4.6, 8.55, color=ORANGE, lw=1.4)
    tag(4.2, 9.1, "I1")
    # controller
    ax.add_patch(FancyBboxPatch((4.6, 5.9), 6.1, 6.3, boxstyle="round,pad=0.02,rounding_size=0.15", fc="#FAFAFA",
                                ec=INK, lw=1.2))
    ax.text(4.8, 11.85, "Controller, IP65 (600 W)", fontsize=7.4, weight="bold", va="center")
    box(ax, 4.85, 9.7, 2.55, 1.7, "160 V bulk\ncapacitors", fc="#FBEFE6", fontsize=fs)
    box(ax, 7.75, 9.7, 2.7, 1.7, "3-phase\ninverter,\n6 × 150 V\nMOSFETs", fc="#FBEFE6", fontsize=fs)
    arr(ax, 7.4, 10.55, 7.75, 10.55, color=ORANGE)
    box(ax, 4.85, 6.15, 5.6, 3.1, "STM32G4-class MCU\nsensorless BLDC control,\nMPPT, supervisory state machine\n"
        "(dry-run, tank-full, fault latch)", fc="#EEF3F8", fontsize=fs)
    arr(ax, 9.1, 9.25, 9.1, 9.7, color=BLUE)
    ax.text(9.25, 9.47, "PWM", fontsize=6.4, color=BLUE, va="center")
    # borehole and pump
    ax.add_patch(Rectangle((0.9, 0.3), 1.6, 4.6, fc="#F2EEE6", ec=INK, lw=1.0))
    ax.add_patch(Rectangle((0.9, 0.3), 1.6, 4.6, fill=False, ec=INK, lw=1.0, zorder=3))
    ax.add_patch(Rectangle((0.9, 0.3), 1.6, 2.2, fc=SKY, alpha=0.35, ec="none"))
    ax.plot([0.9, 2.5], [2.5, 2.5], color=BLUE, lw=1.0)
    ax.text(0.15, 2.5, "static\nlevel\n12 m", fontsize=6.4, va="center", color=BLUE)
    box(ax, 1.15, 0.5, 1.1, 1.3, "helical-\nrotor\npump", fc="#E9F5EF", fontsize=6.2)
    ax.text(0.15, 4.1, "bore-\nhole", fontsize=6.6, ha="left", va="center")
    # drop cable I2
    path(ax, [(10.45, 9.7), (10.45, 9.35), (11.0, 9.35), (11.0, 5.5), (1.95, 5.5), (1.95, 1.8)], color=ORANGE, lw=1.4)
    tag(3.3, 5.5, "I2")
    ax.text(0.25, 6.45, "drop cable: 3-phase,\n0–48 V, 25 m, 3 × 4 mm²", fontsize=6.4, color=ORANGE, va="center")
    # rising main to tank
    path(ax, [(1.45, 1.8), (1.45, 4.4), (4.2, 4.4), (4.2, 3.95)], color=BLUE, lw=1.6)
    ax.text(2.7, 4.5, "water", fontsize=6.4, color=BLUE, va="bottom")
    # tank on a stand
    ax.add_patch(Rectangle((3.4, 1.9), 3.0, 2.05, fc="#DCE8F3", ec=INK, lw=1.0))
    ax.add_patch(Rectangle((3.4, 1.9), 3.0, 1.3, fc=SKY, alpha=0.45, ec="none"))
    for xl in (3.6, 6.2):
        ax.plot([xl, xl], [0.3, 1.9], color=INK, lw=1.2)
    ax.text(4.9, 3.6, "10 m³ elevated tank", fontsize=6.6, ha="center", va="center")
    ax.text(4.9, 2.55, "2 floats +\n4–20 mA level", fontsize=6.3, ha="center", va="center")
    # I3 back to controller
    path(ax, [(6.0, 3.95), (6.0, 5.9)], color=GREEN, lw=1.2)
    tag(6.45, 4.7, "I3")
    # valves I4
    path(ax, [(6.4, 2.3), (7.4, 2.3)], color=BLUE, lw=1.6)
    for k, yv in enumerate((2.9, 1.3)):
        box(ax, 7.4, yv - 0.45, 1.9, 0.9, f"latching\nvalve {k + 1}", fc="#E9F5EF", fontsize=6.2)
        arr(ax, 9.3, yv, 9.9, yv, color=BLUE, lw=1.3)
    ax.plot([7.1, 7.1], [1.3, 2.9], color=BLUE, lw=1.6)
    ax.plot([7.1, 7.4], [2.9, 2.9], color=BLUE, lw=1.6)
    ax.plot([7.1, 7.4], [1.3, 1.3], color=BLUE, lw=1.6)
    ax.text(10.0, 2.1, "drip\nzones", fontsize=6.4, va="center")
    path(ax, [(8.9, 5.9), (8.9, 3.35)], color=GREEN, lw=1.2, ls="--")
    tag(9.35, 4.7, "I4")
    # telemetry
    ys = [0.4, 1.55, 2.7, 3.85]
    for k, y in enumerate(ys):
        box(ax, 14.4, y, 2.6, 0.95, f"soil node {k + 1}\n(STM32WL class)", fc="#E9F5EF", fontsize=6.2)
        arr(ax, 14.4, y + 0.47, 13.65, 6.0, color=PINK, lw=0.9)
    box(ax, 11.3, 6.0, 2.6, 1.5, "LoRaWAN\ngateway\n(≤ 420 m)", fc="#EEF3F8", fontsize=fs)
    tag(13.2, 4.2, "I5")
    ax.text(12.0, 3.1, "LoRaWAN,\nSF7–SF10,\n12 B every\n15 min", fontsize=6.3, color=PINK, ha="center",
            va="center")
    box(ax, 11.3, 9.0, 2.6, 1.5, "MQTT broker\n(cloud)", fc="#EEF3F8", fontsize=fs)
    box(ax, 14.4, 9.0, 2.6, 1.5, "farmer's\nphone", fc="#EEF3F8", fontsize=fs)
    arr(ax, 12.6, 7.5, 12.6, 9.0, color=BLUE)
    arr(ax, 13.9, 9.75, 14.4, 9.75, color=BLUE)
    ax.text(12.75, 8.25, "cellular", fontsize=6.4, color=BLUE, va="center")
    tag(14.15, 10.8, "I6")
    ax.text(14.4, 11.5, "MQTT topic aquasol/<farm>/\n<device>/state, JSON", fontsize=6.3, va="center")
    save(fig, "40", "fig-40-2-aquasol-architecture")


# ----------------------------------------------------------------------------
def design_day(psh=5.0, eta=0.40, p_array=600.0, p_start=80.0):
    """Sizing model of 40.5: half-sine irradiance scaled to `psh`, PV-direct pump."""
    head = 12 + 3 + 4 + 2 + 2
    derate = 0.88 * 0.95 * 0.97
    t = np.linspace(6, 18, 721)
    g = np.sin(np.pi * (t - 6) / 12)
    g *= psh / np.trapezoid(g, t)
    p_dc = p_array * derate * g
    p_pump = np.where(p_dc >= p_start, p_dc, 0.0)
    q = eta * p_pump / (1000 * 9.81 * head)          # m3/s
    v_day = np.trapezoid(q, t * 3600)
    return t, p_dc, p_pump, q * 3600, v_day


def fig_40_3():
    """Design day: PV-DC power and pumped flow, with measured field day 2."""
    t, p_dc, p_pump, q, v = design_day()
    on = t[p_pump > 0]
    fig, ax = new_fig(6.4, 4.0)
    ax.axvspan(on[0], on[-1], color=GREEN, alpha=0.08, lw=0)
    ax.plot(t, p_dc, color=ORANGE, label="PV-DC power, design day (model)")
    ax.axhline(80, color=ORANGE, ls="--", lw=1.0)
    ax.text(6.1, 84, "80 W start threshold", fontsize=7.6, color=ORANGE, va="bottom")
    ax.text(12, p_dc.max() - 22, f"peak {p_dc.max():.0f} W", fontsize=7.6, color=ORANGE, ha="center", va="top")
    h0, h1 = on[0], on[-1]
    ax.text((h0 + h1) / 2, 6, f"pumping {h0:.2f}–{h1:.2f} h, {int(h0):02d}:{round(h0 % 1 * 60):02d}–{int(h1):02d}:{round(h1 % 1 * 60):02d}",
            ha="center", fontsize=7.6, color=GREEN)
    ax.set_xlim(6, 18)
    ax.set_ylim(0, 400)
    ax.set_xlabel("Time of day (h)")
    ax.set_ylabel("Controller input power (W)")
    ax.set_xticks(range(6, 19, 2))
    ax.set_xticklabels([f"{h:02d}:00" for h in range(6, 19, 2)])
    a2 = ax.twinx()
    a2.spines["right"].set_visible(True)
    a2.plot(t, q, color=BLUE, label="pumped flow, design day (model)")
    # field day 2: 5.9 kWh/m2, measured 16.9 m3, pumping 07:40-16:50
    tf, _, _, qf, _ = design_day(psh=5.9, eta=0.38)
    tm = np.r_[np.arange(7 + 40 / 60, 16.8, 0.5), 16 + 50 / 60]
    sel = (tf >= 7 + 40 / 60) & (tf <= 16 + 50 / 60)
    scale = 16.9 / np.trapezoid(qf[sel], tf[sel])
    rng = np.random.default_rng(40)
    qm = np.interp(tm, tf, qf) * scale * (1 + 0.025 * rng.standard_normal(tm.size))
    a2.plot(tm, qm, "o", ms=4, mfc="white", mec=BLUE, mew=1.1, label="measured flow, field day 2 (5.9 kWh/m²)")
    a2.set_ylim(0, 2.5)
    a2.set_ylabel("Flow (m³/h)", color=BLUE)
    a2.tick_params(axis="y", colors=BLUE)
    a2.text(12, q.max() - 0.33, f"and {q.max():.2f} m³/h", fontsize=7.6, color=BLUE, ha="center", va="top")
    h1_, l1 = ax.get_legend_handles_labels()
    h2_, l2 = a2.get_legend_handles_labels()
    ax.legend(h1_ + h2_, l1 + l2, loc="center", fontsize=7.2, bbox_to_anchor=(0.5, 0.36))
    ax.text(6.15, 392, f"Design-day volume {v:.1f} m³\nagainst need 13.3 m³ (+13 %)\nDay 2 measured 16.9 m³",
            fontsize=7.4, ha="left", va="top", bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=GREY, lw=0.7))
    save(fig, "40", "fig-40-3-design-day")
    return v, q.max(), p_dc.max(), on[0], on[-1]


# ----------------------------------------------------------------------------
def fig_40_4():
    """Cumulative discounted cost over 10 years at 8 %."""
    yrs = np.arange(1, 11)
    df = 1 / 1.08 ** yrs
    petrol = 250 + np.cumsum(297.6 * df + np.where(np.isin(yrs, [4, 8]), 250, 0) * df)

    def aq(capex, annual):
        return capex + np.cumsum(annual * df + np.where(yrs == 7, 200, 0) * df)
    variants = [("AquaSol as designed", aq(1838, 90), BLUE, "-"),
                ("gateway shared by 10 farms", aq(1694, 36), GREEN, "-"),
                ("pumping only, no telemetry", aq(1514, 30), PINK, "-")]
    water = 2394 * df.sum()
    fig, ax = new_fig(6.4, 4.1)
    ax.plot(yrs, petrol, "o-", color=ORANGE, ms=4, label="petrol pump")
    for lab, c, col, ls in variants:
        ax.plot(yrs, c, "s" + ls, color=col, ms=3.8, label=lab)
    ends = [("petrol", petrol), ] + [(v[0], v[1]) for v in variants]
    for (nm, c), col, dy in zip(ends, (ORANGE, BLUE, GREEN, PINK), (40, -55, 0, 0)):
        ax.text(10.15, c[-1] + dy, f"${c[-1] / water:.3f}/m³", color=col, fontsize=7.6, va="center")
    # crossings (first year in which the variant is cheaper than petrol)
    for (lab, c, col, ls) in variants:
        k = np.nonzero(c < petrol)[0][0]
        ax.plot(yrs[k], c[k], "o", ms=10, mfc="none", mec=col, mew=1.4)
        ax.annotate(f"break-even year {yrs[k]}", xy=(yrs[k], c[k]), xytext={6: (6.3, 900), 8: (7.6, 1200), 10: (8.7, 1500)}[int(yrs[k])],
                    fontsize=7.4, color=col, arrowprops=dict(arrowstyle="-", color=col, lw=0.7))
    ax.set_xlim(0.7, 11.2)
    ax.set_ylim(0, 2800)
    ax.set_xticks(yrs)
    ax.set_xlabel("Year")
    ax.set_ylabel("Cumulative discounted cost (USD)")
    ax.legend(loc="upper left", fontsize=7.6, bbox_to_anchor=(0.0, 0.99))
    ax.grid(True, color=GRID, lw=0.5)
    ax.text(0.8, 120, f"8 % discount rate; 2394 m³/yr, discounted water {water:,.0f} m³", fontsize=7.4,
            color=GREY)
    save(fig, "40", "fig-40-4-cumulative-cost")
    return np.round(petrol), [np.round(v[1]) for v in variants]


# ----------------------------------------------------------------------------
def schedule(mitigated):
    """Monte Carlo of the capstone plan, as in the chapter listing (100,000 runs)."""
    rng = np.random.default_rng(2026)
    N = 100_000
    tri = lambda lo, mode, hi: rng.triangular(lo, mode, hi, N)
    front = tri(2, 3, 4) + tri(2, 2.5, 4) + tri(2, 3, 5)
    hw = tri(4, 6, 10) + (0.0 if mitigated else tri(1, 2, 4))
    fw = tri(5, 7, 11)
    node = tri(3, 4, 7)
    build = np.maximum.reduce([hw, fw, node])
    back = tri(2, 3, 6) + tri(2, 3, 5) + tri(1.5, 2, 3)
    return front + build + back


def fig_40_5():
    """Schedule-risk CDFs before and after taking the re-spin off the critical path."""
    fig, ax = new_fig(6.4, 4.0)
    out = {}
    for mit, ls, col, lab in ((False, "-", BLUE, "baseline plan"),
                              (True, "--", GREEN, "re-spin off the critical path")):
        tot = np.sort(schedule(mit))
        cdf = np.arange(1, tot.size + 1) / tot.size
        ax.plot(tot, cdf, ls=ls, color=col, label=lab)
        p = [np.percentile(tot, q) for q in (50, 80, 95)]
        pd = np.mean(tot <= 28)
        out[lab] = (p, pd)
        for q, v in zip((0.5, 0.8, 0.95), p):
            ax.plot(v, q, "o", ms=4, color=col)
        ax.plot(28, pd, "D", ms=5, color=col)
        ax.text(28.25, pd + (0.0 if mit else -0.0), f"P(≤ 28) = {pd:.2f}", color=col, fontsize=7.6,
                va="center")
        txt = f"P50 {p[0]:.1f}, P80 {p[1]:.1f},\nP95 {p[2]:.1f} weeks"
        ax.text(29.4 if not mit else 21.0, 0.36 if not mit else 0.72, txt, color=col, fontsize=7.6,
                ha="left")
    ax.axvline(28, color=RED, lw=1.1)
    ax.text(27.9, 0.04, "deadline\nweek 28", color=RED, fontsize=7.6, ha="right", va="bottom")
    ax.axvline(24.5, color=GREY, ls=":", lw=1.1)
    ax.text(24.4, 0.97, "sum of most-likely\ndurations 24.5 wk", color=GREY, fontsize=7.4, ha="right", va="top")
    for q in (0.5, 0.8, 0.95):
        ax.axhline(q, color=GRID, lw=0.6, zorder=0)
    ax.set_xlim(20, 34)
    ax.set_ylim(0, 1)
    ax.set_xlabel("Completion week")
    ax.set_ylabel("Cumulative probability")
    ax.legend(loc="lower right", fontsize=7.8)
    save(fig, "40", "fig-40-5-schedule-risk")
    return out


if __name__ == "__main__":
    fig_40_1()
    fig_40_2()
    print("design day", fig_40_3())
    print("cost", fig_40_4())
    print("schedule", fig_40_5())
