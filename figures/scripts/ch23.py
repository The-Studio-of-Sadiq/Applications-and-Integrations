"""Figures for Chapter 23 — Battery Energy Systems.

Run from the repository root:  python figures/scripts/ch23.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle  # noqa: E402

from figstyle import COLORS, INK, save, schematic, new_fig  # noqa: E402

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
                arrowprops=dict(arrowstyle="<|-|>" if both else "-|>", color=color, lw=lw, ls=ls,
                                shrinkA=0, shrinkB=0, mutation_scale=9), zorder=z)


def rbox(ax, x, y, w, h, text="", fc="#EEF3F8", ec=INK, fs=7.4, lw=1.0, z=3, weight="normal"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.1",
                                fc=fc, ec=ec, lw=lw, zorder=z))
    if text:
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=INK,
                zorder=z + 0.5, weight=weight, linespacing=1.15)


# ----------------------------------------------------------------------------
# Figure 23.1 — cabinet architecture
# ----------------------------------------------------------------------------
def fig_23_1():
    fig, ax = schematic(6.8, 5.6, xlim=(0, 17), ylim=(0, 14))
    HV = "#B03A2E"
    # module column: 15 modules in series, MSD between M8 and M9
    mx, mw, mh, pitch = 0.35, 2.75, 0.56, 0.72
    ys = []
    y = 12.1
    for k in range(15):
        if k == 8:
            y -= 0.45                                   # room for the service disconnect
        ys.append(y)
        y -= pitch
    xl = 1.0                                            # x of the series links
    for k, yk in enumerate(ys):
        rbox(ax, mx, yk, mw, mh, f"M{k + 1}  16S · 51.2 V", fc="#E6F4EC", fs=6.4)
        rbox(ax, 3.3, yk + 0.06, 0.8, mh - 0.12, "AFE", fc="#FFF4D6", fs=6.0)
        if k < 14:
            nxt = ys[k + 1]
            line(ax, [(xl, yk), (xl, nxt + mh)], color=HV, lw=1.6, z=2)
    ymsd = (ys[7] + ys[8] + mh) / 2
    rbox(ax, xl - 0.32, ymsd - 0.17, 0.64, 0.34, "", fc="white", ec=HV, lw=1.0, z=4)
    ax.plot([xl - 0.18, xl + 0.18], [ymsd - 0.08, ymsd + 0.08], color=HV, lw=1.0, zorder=5)
    ax.text(xl + 0.45, ymsd, "MSD", fontsize=6.4, va="center", color=HV, weight="bold")
    # rack + / - leads
    line(ax, [(xl, ys[0] + mh), (xl, 13.45), (11.9, 13.45), (11.9, 12.35)], color=HV, lw=2.0)
    line(ax, [(xl, ys[-1]), (xl, 0.3), (11.9, 0.3), (11.9, 0.85)], color=HV, lw=2.0)
    ax.text(xl + 0.15, 13.55, "rack +", fontsize=6.8, color=HV, va="bottom")
    ax.text(xl + 0.15, 0.2, "rack −", fontsize=6.8, color=HV, va="top")
    # daisy chain ring
    line(ax, [(3.7, ys[0] + mh - 0.06), (3.7, ys[-1] + 0.06)], color=BLUE, lw=1.1, ls=(0, (3, 2)))
    line(ax, [(3.7, ys[0] + mh - 0.06), (3.7, 13.0), (5.3, 13.0), (5.3, 7.9)], color=BLUE, lw=1.1,
         ls=(0, (3, 2)))
    line(ax, [(3.7, ys[-1] + 0.06), (3.7, 0.75), (5.3, 0.75), (5.3, 5.3)], color=BLUE, lw=1.1,
         ls=(0, (3, 2)))
    ax.text(5.08, 10.4, "isolated daisy chain (ring)", fontsize=6.3, color=BLUE, va="center",
            ha="center", rotation=90)
    # HW comparator chain
    line(ax, [(4.25, ys[0] + mh / 2), (4.25, ys[-1] + mh / 2)], color=RED, lw=1.4)
    for yk in ys:
        line(ax, [(4.1, yk + mh / 2), (4.25, yk + mh / 2)], color=RED, lw=1.0)
    line(ax, [(4.25, ys[-1] + mh / 2), (4.25, 1.3), (9.95, 1.3), (9.95, 4.6)], color=RED, lw=1.4,
         arrow_end=True)
    ax.text(7.6, 1.75, "HW comparator chain\n3.75 V / 2.50 V, no software", fontsize=6.2,
            color=RED, va="center", ha="center")
    # module note
    ax.text(8.4, 12.2, "module: 16 × 280 Ah LFP, 51.2 V, 14.3 kWh\nAFE: 16 ch, 4 NTC, 150 mA balancing\n"
            "MSD: manual service disconnect", fontsize=6.2, ha="center", va="center", color=GREY,
            style="italic")
    # BMU, EMS, cooling
    rbox(ax, 5.0, 5.3, 3.4, 2.6, "BMU\nprotection, SoC,\nSoP, SoH,\nlimits", fc="#DCE8F5", fs=7.0,
         weight="normal")
    rbox(ax, 6.0, 10.1, 2.6, 1.0, "EMS", fc="white", fs=7.0)
    line(ax, [(7.3, 7.9), (7.3, 10.1)], color=BLUE, lw=1.1, ls=(0, (3, 2)), both=True)
    ax.text(7.42, 9.0, "Modbus\nTCP", fontsize=6.3, color=BLUE, va="center")
    rbox(ax, 5.95, 2.25, 3.2, 1.6, "Liquid cooling\nchiller, pump, cold\nplates under modules",
         fc="#E8F1FB", fs=6.4)
    line(ax, [(7.0, 5.3), (7.0, 3.85)], color=BLUE, lw=1.1, ls=(0, (3, 2)), both=True)
    ax.text(7.12, 4.55, "CAN", fontsize=6.3, color=BLUE, va="center")
    # coil supply and drivers
    rbox(ax, 9.25, 4.6, 1.4, 1.9, "Coil\nsupply +\ndrivers", fc="white", fs=6.4)
    line(ax, [(8.4, 5.9), (9.25, 5.9)], color=INK, lw=1.0, arrow_end=True)
    # HV switchgear (vertical on the + side, then negative side)
    rbox(ax, 11.2, 11.35, 1.4, 1.0, "Fuse 250 A\n1000 V DC\n20 kA", fc="#FBE3D6", ec=ORANGE, fs=5.9)
    line(ax, [(11.9, 11.35), (11.9, 10.6)], color=HV, lw=2.0)
    rbox(ax, 11.3, 9.6, 1.2, 0.8, "K1", fc="white", ec=HV, fs=7)
    line(ax, [(11.9, 10.6), (11.9, 10.4)], color=HV, lw=2.0)
    line(ax, [(11.9, 9.6), (11.9, 8.2), (14.6, 8.2)], color=HV, lw=2.0)
    # precharge branch in parallel with K1
    line(ax, [(11.9, 10.6), (13.6, 10.6), (13.6, 10.35)], color=HV, lw=1.3)
    rbox(ax, 13.1, 9.75, 1.0, 0.6, "K3", fc="white", ec=HV, fs=6.6)
    line(ax, [(13.6, 9.75), (13.6, 9.55)], color=HV, lw=1.3)
    rbox(ax, 13.15, 8.85, 0.9, 0.7, "100 Ω", fc="white", ec=HV, fs=6.3)
    line(ax, [(13.6, 8.85), (13.6, 8.2)], color=HV, lw=1.3)
    ax.text(14.15, 9.85, "precharge", fontsize=6.3, color=HV, va="center")
    # negative side
    rbox(ax, 11.2, 0.85, 1.4, 1.0, "Shunt 50 µΩ\nisol. 24-bit", fc="white", ec=HV, fs=5.9)
    line(ax, [(11.9, 1.85), (11.9, 2.6)], color=HV, lw=2.0)
    rbox(ax, 11.3, 2.6, 1.2, 0.8, "K2", fc="white", ec=HV, fs=7)
    line(ax, [(11.9, 3.4), (11.9, 4.6), (14.6, 4.6)], color=HV, lw=2.0)
    # PCS
    rbox(ax, 14.6, 3.9, 2.25, 5.0, "PCS\n100 kW\nDC input\n600-950 V\nDC link\n3 mF",
         fc="#ECECEC", fs=6.8)
    # IMD
    rbox(ax, 13.05, 5.7, 1.1, 1.0, "IMD", fc="white", fs=6.6)
    line(ax, [(13.6, 6.7), (13.6, 8.2)], color=INK, lw=0.9)
    line(ax, [(13.6, 5.7), (13.6, 4.6)], color=INK, lw=0.9)
    line(ax, [(14.15, 6.2), (14.4, 6.2), (14.4, 5.55)], color=INK, lw=0.9)
    for k, wdt in enumerate((0.36, 0.24, 0.12)):
        ax.plot([14.4 - wdt / 2, 14.4 + wdt / 2], [5.55 - k * 0.1] * 2, color=INK, lw=0.9)
    ax.text(12.95, 6.2, "to\nchassis", fontsize=5.8, ha="right", va="center")
    # coil connections
    for (xk, yk) in ((11.3, 10.0), (11.3, 3.0)):
        line(ax, [(10.65, 5.55 if yk < 5 else 6.2), (10.95, 5.55 if yk < 5 else 6.2), (10.95, yk),
                  (xk, yk)], color=GREY, lw=0.9, ls=(0, (1.5, 1.5)))
    line(ax, [(10.95, 6.2), (10.95, 10.95), (13.6, 10.95), (13.6, 10.35)], color=GREY, lw=0.9,
         ls=(0, (1.5, 1.5)))
    # CAN to PCS
    line(ax, [(8.4, 7.4), (14.6, 7.4)], color=BLUE, lw=1.1, ls=(0, (3, 2)), arrow_end=True)
    ax.text(8.6, 7.5, "CAN 500 kbit/s: limits every 1 s", fontsize=6.2, color=BLUE, va="bottom")
    # legend
    lg = [(HV, "-", 2.0, "HV path"), (BLUE, (0, (3, 2)), 1.1, "communication"),
          (RED, "-", 1.4, "HW protection"), (GREY, (0, (1.5, 1.5)), 0.9, "coil drive")]
    for k, (c, ls, lw, lab) in enumerate(lg):
        yy = 2.9 - k * 0.42
        ax.plot([13.2, 13.9], [yy, yy], color=c, ls=ls, lw=lw)
        ax.text(14.0, yy, lab, fontsize=6.4, va="center")
    save(fig, "23", "fig-23-1-cabinet-architecture")


# ----------------------------------------------------------------------------
# Figure 23.2 — parallel racks (the listing of Section 23.3)
# ----------------------------------------------------------------------------
def simulate_parallel():
    soc_pts = np.array([0, 5, 10, 20, 30, 50, 70, 90, 95, 100]) / 100
    ocv_pts = np.array([2.80, 3.10, 3.20, 3.25, 3.28, 3.30, 3.32, 3.34, 3.37, 3.45])
    ocv = lambda soc: 240 * np.interp(soc, soc_pts, ocv_pts)  # noqa: E731
    A = dict(Q=280 * 0.93, R=0.075 * 1.25, soc=0.95)
    B = dict(Q=280 * 1.00, R=0.075, soc=0.95)
    P, dt = 200e3, 1.0
    ga, gb = 1 / A["R"], 1 / B["R"]
    log = []
    while True:
        ea, eb = ocv(A["soc"]), ocv(B["soc"])
        s = ea * ga + eb * gb
        V = (s + np.sqrt(s * s - 4 * (ga + gb) * P)) / (2 * (ga + gb))
        ia, ib = (ea - V) * ga, (eb - V) * gb
        if V / 240 < 2.90 or min(A["soc"], B["soc"]) <= 0:
            break
        log.append((A["soc"], B["soc"], ia, ib))
        A["soc"] -= ia * dt / 3600 / A["Q"]
        B["soc"] -= ib * dt / 3600 / B["Q"]
    return np.array(log), dt


def fig_23_2():
    log, dt = simulate_parallel()
    t = np.arange(len(log)) * dt / 3600
    sa, sb, ia, ib = log.T
    fig, ax = new_fig(6.6, 4.3)
    ax.plot(t, ia, color=ORANGE, lw=2, label="rack A current, aged (93 % capacity, 94 mΩ)")
    ax.plot(t, ib, color=BLUE, lw=2, label="rack B current, new (100 %, 75 mΩ)")
    ax.axhline(140, color=RED, ls="--", lw=1.1)
    ax.text(0.03, 141.5, "per-rack limit 140 A (0.5C): exceeded by B from the start", color=RED,
            fontsize=7.4, va="bottom", bbox=dict(fc="white", ec="none", pad=0.5))
    ax.set_ylim(0, 200)
    ax.set_yticks(range(0, 181, 20))
    ax.set_xlim(0, t[-1])
    ax.set_xlabel("Time (h)")
    ax.set_ylabel("Rack current (A)")
    ax.text(0.02, ia[0] - 3, f"{ia[0]:.0f} A", color=ORANGE, fontsize=7.6, va="top")
    ax.text(0.02, ib[0] - 3, f"{ib[0]:.0f} A", color=BLUE, fontsize=7.6, va="top")
    ka = np.argmax(ia)
    ax.annotate(f"A peaks at {ia[ka]:.0f} A ({ia[ka] / (ia[ka] + ib[ka]) * 100:.1f} % share)\n"
                f"at {t[ka]:.2f} h, SoC 10 % breakpoint of the OCV table;\n"
                f"at cut-off A {ia[-1]:.0f} A, B {ib[-1]:.0f} A",
                xy=(t[ka], ia[ka]), xytext=(0.62, 160), fontsize=7.2, color=ORANGE,
                arrowprops=dict(arrowstyle="-", color=ORANGE, lw=0.7))
    ax2 = ax.twinx()
    ax2.spines["right"].set_visible(True)
    ax2.plot(t, sa * 100, color=ORANGE, ls="--", lw=1.2, label="SoC A")
    ax2.plot(t, sb * 100, color=BLUE, ls="--", lw=1.2, label="SoC B")
    ax2.set_ylim(0, 100)
    ax2.set_ylabel("State of charge (%)")
    gap = (sb - sa) * 100
    kg = np.argmax(np.abs(gap))
    ax2.annotate(f"largest SoC gap {abs(gap[kg]):.1f} points at {t[kg]:.2f} h\n"
                 f"(SoC ≈ {sa[kg] * 100:.0f} %, end of the flat plateau)",
                 xy=(t[kg], (sa[kg] + sb[kg]) * 50), xytext=(0.62, 9), fontsize=7.2,
                 arrowprops=dict(arrowstyle="-", color=INK, lw=0.7))
    share = (ib / (ia + ib)).max()
    worst = (np.maximum(ia, ib) / (ia + ib)).max()
    ax.text(0.03, 75, f"start: B share {share * 100:.1f} % → {140 / share:.0f} A\n"
            f"worst: A share {worst * 100:.1f} % → limit {140 / worst:.0f} A,\nnot 280 A",
            fontsize=7.6, bbox=dict(fc="white", ec=GREY, lw=0.6))
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, fontsize=7.0, loc="upper center", ncol=2,
              bbox_to_anchor=(0.5, 1.17))
    save(fig, "23", "fig-23-2-parallel-rack-sharing")
    return t[-1], ia[0], ib[0], ia[-1], ib[-1], sa[-1], sb[-1], share, t[kg], gap[kg]


# ----------------------------------------------------------------------------
# Figure 23.3 — SoC error growth
# ----------------------------------------------------------------------------
def fig_23_3():
    d = np.linspace(0, 27.999, 2801)
    tw = np.mod(d, 7)
    hall_rate = (12.8 - 1.0) / 7
    shunt_rate = (2.4 - 1.0) / 7
    hall = 1.0 + hall_rate * tw
    shunt = 1.0 + shunt_rate * tw
    hall_nr = 1.0 + hall_rate * d
    fig, ax = new_fig(6.4, 4.3)
    ax.axhspan(0, 5, color=GREEN, alpha=0.10, zorder=0)
    ax.axhline(5, color=GREEN, lw=1.2)
    ax.text(27.8, 5.15, "R5: ±5 %", color=GREEN, fontsize=8, ha="right", va="bottom")
    m = hall_nr <= 15.5
    ax.plot(d[m], hall_nr[m], color=RED, ls=":", lw=1.8,
            label="Hall sensor, no weekly full charge (original EMS)")
    ax.plot(d, hall, color=RED, lw=1.6, label="Hall sensor, weekly reset")
    ax.plot(d, shunt, color=BLUE, lw=1.8, label="isolated shunt, weekly reset")
    for k in range(1, 4):
        ax.axvline(7 * k, color=GREY, lw=0.6, ls=(0, (2, 3)))
    ax.text(7.2, 12.2, "12.8 %", fontsize=7.6, color=RED, va="center")
    ax.text(7.1, 2.4, "2.4 %", fontsize=7.6, color=BLUE, va="center")
    ax.text(0.4, 14.7, "Hall offset 0.15 A:\n0.15 × 24 / 280\n= 1.29 % per day;\n"
            f"{hall_rate:.2f} % per day with\ngain and SoH terms", fontsize=7.0, color=RED,
            va="top")
    ax.text(8.5, 14.9, "clipped", fontsize=7, color=RED, va="top", ha="left")
    ax.set_xlim(0, 28)
    ax.set_ylim(0, 15)
    ax.set_xticks(range(0, 29, 7))
    ax.set_xlabel("Time (days); full-charge recalibration on days 0, 7, 14, 21")
    ax.set_ylabel("Worst-case SoC error (%)")
    ax.legend(fontsize=7.4, loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=2)
    save(fig, "23", "fig-23-3-soc-error-growth")


# ----------------------------------------------------------------------------
# Figure 23.4 — current limits against temperature
# ----------------------------------------------------------------------------
def ccl(T):
    return np.select([T < 0, T < 10, T < 15, T <= 45, T <= 55], [0, 0.1, 0.25, 0.5, 0.2], 0.0)


def dcl(T):
    return np.select([T < -10, T <= 50, T <= 55], [0.3, 0.5, 0.2], 0.0)


def fig_23_4():
    T = np.linspace(-20, 65, 8501)
    fig, ax = new_fig(6.4, 3.9)
    ax.axvspan(15, 45, color=GREEN, alpha=0.10, zorder=0)
    ax.text(32, 0.78, "normal operating window\n15-45 °C", ha="center", va="top", fontsize=7.8,
            color=GREEN)
    ax.plot(T, ccl(T), color=BLUE, lw=2, label="CCL, charge (evaluated on coldest cell)")
    ax.plot(T, dcl(T), color=ORANGE, lw=2, ls="--",
            label="DCL, discharge (evaluated on hottest cell)")
    ax.axhline(0.47, xmin=(15 + 20) / 85, xmax=(45 + 20) / 85, color=INK, lw=0.8, ls=":")
    ax.plot(25, 0.47, "o", color=INK, ms=5, zorder=5)
    ax.annotate("100 kW operating point\n0.47C, 130 A", xy=(25, 0.47), xytext=(-2, 0.66),
                fontsize=7.4, arrowprops=dict(arrowstyle="-", color=INK, lw=0.7))
    for tv, lab in ((55, "55 °C software trip"), (60, "60 °C")):
        ax.axvline(tv, color=RED, ls=":", lw=1.2)
        ax.text(tv + 0.6, 0.93 if tv == 55 else 0.75, lab, fontsize=7.2, color=RED, rotation=90,
                va="top")
    ax.set_xlim(-20, 65)
    ax.set_ylim(0, 1.0)
    ax.set_xlabel("Cell temperature (°C): minimum for CCL, maximum for DCL")
    ax.set_ylabel("Current limit (C-rate)")
    ax2 = ax.twinx()
    ax2.spines["right"].set_visible(True)
    ax2.set_ylim(0, 280)
    ax2.set_ylabel("Current limit (A, 280 Ah cells)")
    ax.legend(fontsize=7.4, loc="upper left")
    save(fig, "23", "fig-23-4-current-limits-vs-temperature")


# ----------------------------------------------------------------------------
# Figure 23.5 — precharge sequence
# ----------------------------------------------------------------------------
def fig_23_5():
    V0, R, C = 864.0, 100.0, 3e-3
    tau = R * C
    t = np.linspace(0, 2.5, 5001)
    t_k2, t_k3, t_k1, t_k3o = 0.05, 0.10, 1.25, 1.35
    vlink = np.where(t < t_k3, 0, V0 * (1 - np.exp(-(t - t_k3) / tau)))
    vlink = np.where(t >= t_k1, V0, vlink)
    ipre = np.where((t >= t_k3) & (t < t_k1), V0 / R * np.exp(-(t - t_k3) / tau), 0)
    t95 = t_k3 + 3 * tau
    t20 = t_k3 + tau * np.log(V0 / 20)
    fig, axs = plt.subplots(5, 1, figsize=(6.6, 5.0), sharex=True,
                            gridspec_kw=dict(height_ratios=[0.55, 0.55, 0.55, 2.0, 1.4],
                                             hspace=0.15))
    for a, (name, ton, toff, c) in zip(axs[:3], (("K2 (main −)", t_k2, 9, INK),
                                                 ("K3 (precharge)", t_k3, t_k3o, ORANGE),
                                                 ("K1 (main +)", t_k1, 9, BLUE))):
        y = ((t >= ton) & (t < toff)).astype(float)
        a.plot(t, y, color=c, lw=1.6, drawstyle="steps-post")
        a.fill_between(t, 0, y, step="post", color=c, alpha=0.12)
        a.set_ylim(-0.2, 1.4)
        a.set_yticks([0, 1])
        a.set_yticklabels(["open", "closed"], fontsize=6.8)
        a.set_ylabel(name, rotation=0, ha="right", va="center", fontsize=8, labelpad=4)
        a.text(ton + 0.02, 1.05, f"{ton:.2f} s", fontsize=6.8, va="bottom", color=c)
    axs[1].text(t_k3o + 0.02, 0.35, f"opens {t_k3o:.2f} s", fontsize=6.8, color=ORANGE)
    a = axs[3]
    a.plot(t, vlink, color=BLUE, lw=1.8)
    a.axhline(V0, color=GREY, lw=0.7, ls=":")
    a.axhline(V0 - 20, color=GREY, lw=0.7, ls=":")
    a.text(2.48, V0 + 12, "rack 864 V", fontsize=7, ha="right", va="bottom", color=GREY)
    a.plot(t95, 0.95 * V0, "o", color=BLUE, ms=4)
    a.annotate(f"95 % at {t95:.2f} s", xy=(t95, 0.95 * V0), xytext=(0.62, 560), fontsize=7.2,
               arrowprops=dict(arrowstyle="-", color=INK, lw=0.6))
    a.plot(t20, V0 - 20, "o", color=RED, ms=4)
    a.annotate(f"within 20 V (844 V)\nat {t20:.2f} s → close K1", xy=(t20, V0 - 20),
               xytext=(1.45, 520), fontsize=7.2,
               arrowprops=dict(arrowstyle="-", color=INK, lw=0.6))
    a.set_ylim(0, 1000)
    a.set_ylabel("DC-link\nvoltage (V)", fontsize=8.5)
    a.text(0.35, 150, f"τ = 100 Ω × 3 mF = {tau:.1f} s", fontsize=7.4)
    a = axs[4]
    a.plot(t, ipre, color=ORANGE, lw=1.8)
    a.set_ylim(0, 10.5)
    a.set_ylabel("Precharge\ncurrent (A)", fontsize=8.5)
    a.text(t_k3 + 0.03, 8.9, f"peak {V0 / R:.1f} A", fontsize=7.2, va="center")
    a.text(0.75, 6.2, f"resistor energy ½CV² = {0.5 * C * V0**2 / 1e3:.1f} kJ\n"
           f"peak power V²/R = {V0**2 / R / 1e3:.1f} kW", fontsize=7.4)
    a.set_xlabel("Time (s)")
    a.set_xlim(0, 2.5)
    for ax_ in axs:
        ax_.axvline(2.1, color=RED, ls="--", lw=1.1)
    axs[3].text(2.08, 280, "precharge timeout:\nfault if link not\nwithin 20 V", fontsize=7,
                color=RED, ha="right", va="center")
    save(fig, "23", "fig-23-5-precharge-sequence")
    return t95, t20


# ----------------------------------------------------------------------------
# Figure 23.6 — capacity fade projection
# ----------------------------------------------------------------------------
def fade(t_yr, kT, efc_per_yr=365):
    return kT * (2.0 * np.sqrt(t_yr) + 0.00204 * efc_per_yr * t_yr)


def fig_23_6():
    t = np.linspace(0, 15, 1501)
    fig, ax = new_fig(6.4, 4.2)
    cases = [(1.0, "uniform 25 °C", INK, "-"), (1.49, "warm module 31 °C (×1.49), original", RED, "--"),
             (1.22, "redesign, 3 K spread (×1.22)", BLUE, "-")]
    out = {}
    for kT, lab, c, ls in cases:
        E = 200 * (1 - fade(t, kT) / 100)
        ax.plot(t, E, color=c, ls=ls, lw=1.8, label=lab)
        e10 = 200 * (1 - fade(10, kT) / 100)
        out[kT] = e10
        ax.plot(10, e10, "o", color=c, ms=4, zorder=5)
        if kT == 1.49:
            ax.text(9.8, e10 - 2.2, f"{e10:.0f} kWh", color=c, fontsize=7.4, va="center",
                    ha="right")
        else:
            ax.text(10.2, e10 + (1.2 if kT == 1.0 else 0.5), f"{e10:.0f} kWh", color=c,
                    fontsize=7.4, va="center")
    Er = 200 * (1 - fade(t, 1.22) / 100)
    ax.fill_between(t, Er - 4, Er + 4, color=BLUE, alpha=0.12, lw=0)
    ax.text(0.2, 142, "shaded: maintenance alarm band, ±2 points around the redesign projection",
            fontsize=7.2, color=BLUE)
    ax.axhline(160, color=INK, ls="--", lw=1.0)
    ax.text(0.2, 160.6, "R1: 160 kWh in year 10", fontsize=7.8, va="bottom")
    ax.axvline(10, color=GREY, ls=":", lw=0.8)
    ax.plot(0, 200, "s", color=RED, ms=6, zorder=6)
    tm = 14 / 12
    ax.plot(tm, 181, "s", color=RED, ms=6, zorder=6, label="measured, original cabinet")
    ax.annotate(f"181 kWh at 14 months\n(model {200 * (1 - fade(tm, 1.0) / 100):.0f} kWh;"
                " SoC offset +\nwarm-module fade)", xy=(tm, 181), xytext=(1.8, 147.5), fontsize=7.2,
                color=RED, arrowprops=dict(arrowstyle="-", color=RED, lw=0.7))
    ax.set_xlim(0, 15)
    ax.set_ylim(140, 205)
    ax.set_xlabel("Time in service (years)")
    ax.set_ylabel("Usable energy (kWh)")
    ax.legend(fontsize=7.3, loc="upper right")
    top = ax.secondary_xaxis("top", functions=(lambda x: x * 365, lambda e: e / 365))
    top.set_xlabel("Equivalent full cycles (365 per year)", fontsize=8.5)
    save(fig, "23", "fig-23-6-capacity-fade-projection")
    return out


if __name__ == "__main__":
    fig_23_1()
    print("23.2:", [round(float(x), 3) for x in fig_23_2()])
    fig_23_3()
    fig_23_4()
    print("23.5 t95, t20:", fig_23_5())
    print("23.6 year-10:", fig_23_6())
