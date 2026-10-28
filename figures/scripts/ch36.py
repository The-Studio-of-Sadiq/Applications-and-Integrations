"""Figures for Chapter 36 — Project: Solar Battery System.

Run from the repository root:  python figures/scripts/ch36.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Patch  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

from figstyle import COLORS, INK, box, save, schematic  # noqa: E402

BLUE, ORANGE, GREEN, PINK, YELLOW, SKY = COLORS[:6]
RED = "#C62828"
GREY = "#777777"


def tint(c, a="30"):
    return c + a


def line(ax, pts, color=INK, lw=1.1, ls="-", arrow_end=False, both=False):
    xs, ys = zip(*pts)
    if not arrow_end and not both:
        ax.plot(xs, ys, color=color, lw=lw, ls=ls, solid_capstyle="butt")
        return
    if len(pts) > 2:
        ax.plot(xs[:-1], ys[:-1], color=color, lw=lw, ls=ls)
    ax.annotate("", xy=pts[-1], xytext=pts[-2],
                arrowprops=dict(arrowstyle="<|-|>" if both else "-|>", color=color, lw=lw,
                                ls=ls, shrinkA=0, shrinkB=0, mutation_scale=10))


# ----------------------------------------------------------------------------
# Load and PV model of Section 36.3
# ----------------------------------------------------------------------------
# (power W, first hour, last hour + 1, circuit)
BLOCKS = [(50, 0, 24, "critical"), (12, 0, 24, "critical"),          # fridge average, router
          (18, 18, 23, "critical"), (90, 18, 23, "comfort"),          # lighting: 2 critical, 10 comfort
          (18, 5, 6, "critical"), (90, 5, 6, "comfort"),
          (30, 19, 22, "critical"), (120, 10, 18, "comfort"),         # exam lamp, fans
          (90, 9, 15, "comfort"), (50, 16, 18, "comfort"),            # laptops, phone charging
          (375, 7, 8, "pump"), (150, 11, 12, "comfort"), (100, 14, 15, "comfort")]


def load_profile():
    p = {"critical": np.zeros(24), "comfort": np.zeros(24), "pump": np.zeros(24)}
    for w, a, b, c in BLOCKS:
        p[c][a:b] += w
    for c in p:
        p[c] *= 1.10
    p_ac = sum(p.values())
    return p, p_ac, p_ac / 0.92 + 15.0


def pv_day(h_poa, kwp=2.46, pr=0.794):
    s = np.clip(np.sin(np.pi * (np.arange(24) + 0.5 - 6) / 12), 0, None)
    return kwp * 1e3 * pr * h_poa * s / s.sum()


def simulate(e_nom, week, soc0=0.80, soc_min=0.10):
    _, _, p_dc = load_profile()
    soc, log, unserved, floor = soc0, [], 0.0, []
    for h_poa in week:
        for pv, ld in zip(pv_day(h_poa), p_dc):
            net = pv - ld
            de = net * 0.97 if net > 0 else net / 0.98
            new = soc + de / e_nom
            new = min(new, 1.0)
            at_floor = new < soc_min
            if at_floor:
                unserved += (soc_min - new) * e_nom
                new = soc_min
            floor.append(at_floor)
            soc = new
            log.append(soc)
    return np.array(log), unserved, np.array(floor)


# ----------------------------------------------------------------------------
# Figure 36.1 — architecture
# ----------------------------------------------------------------------------
def fig_36_1():
    fig, ax = schematic(6.8, 5.0, xlim=(0, 20), ylim=(0, 14.7))
    PW = dict(color=INK, lw=2.6, arrow_end=True)
    DL = dict(color=GREY, lw=1.1, ls=(0, (4, 2)))
    fs = 6.6
    y0, h = 10.0, 3.6
    # power chain, top row (left to right)
    box(ax, 0.1, y0, 2.7, h, "PV array\n6 × 410 W\n3S2P\n2.46 kWp\n$V_{oc}$ 118 V\ncold", fc=tint(YELLOW, "45"),
        fontsize=fs)
    box(ax, 3.25, y0, 2.9, h, "PV combiner\n\nDC isolator\n2-pole 32 A\n\nType 2\nPV SPD", fc="white",
        fontsize=fs)
    box(ax, 6.6, y0, 2.6, h, "MPPT\ncharge\ncontroller\n\n150 V\n60 A", fc=tint(BLUE, "30"), fontsize=fs)
    box(ax, 9.65, y0, 3.0, h, "48 V DC\nbusbar\n\nClass T fuse\n200 A\n\nbattery\nisolator",
        fc=tint(GREY, "25"), fontsize=fs)
    box(ax, 13.1, y0, 2.6, h, "Inverter-\ncharger\n\n48 V\n3 kVA", fc=tint(ORANGE, "30"), fontsize=fs)
    box(ax, 16.15, 7.6, 3.75, 6.0, "", fc="white")
    ax.text(18.03, 13.35, "AC distribution\nboard", ha="center", va="top", fontsize=fs, weight="bold")
    ax.text(18.03, 12.0, "RCD Type A 30 mA", ha="center", va="top", fontsize=6.3)
    mcbs = [(10.9, "MCB critical", RED), (9.85, "MCB comfort\n+ contactor", BLUE),
            (8.45, "MCB pump\n+ contactor", GREEN)]
    for y, t, c in mcbs:
        ax.text(16.4, y, t, fontsize=6.3, color=c, va="center")
    line(ax, [(2.8, 11.8), (3.25, 11.8)], **PW)
    line(ax, [(6.15, 11.8), (6.6, 11.8)], **PW)
    line(ax, [(9.2, 11.8), (9.65, 11.8)], **PW)
    line(ax, [(12.65, 11.8), (13.1, 11.8)], color=INK, lw=2.6, both=True)
    line(ax, [(15.7, 11.8), (16.15, 11.8)], **PW)
    # battery modules under the busbar
    for k in range(3):
        box(ax, 9.35 + k * 1.25, 6.6, 1.15, 2.4, "LFP\n51.2 V\n100 Ah\n\nBMS", fc=tint(GREEN, "35"),
            fontsize=5.2)
    ax.text(9.15, 7.8, "3 modules\nin parallel\n15.36 kWh", ha="right", va="center", fontsize=6.2)
    line(ax, [(11.15, y0), (11.15, 9.0)], color=INK, lw=2.6, both=True)
    # generator into AC-in
    box(ax, 13.6, 7.2, 2.1, 1.3, "generator\n(optional)", fc="white", fontsize=6.2)
    line(ax, [(14.65, 8.5), (14.65, y0)], color=INK, lw=1.8, arrow_end=True)
    ax.text(14.8, 9.25, "AC-in", fontsize=5.8, va="center")
    # loads
    loads = [(5.3, "vaccine fridge,\nlights, router\n(critical)", RED),
             (3.4, "fans, laptops\n(comfort)", BLUE),
             (1.5, "water pump\n(soft start)", GREEN)]
    for (yl, t, c), xf in zip(loads, (16.35, 16.6, 16.85)):
        box(ax, 17.1, yl, 2.8, 1.6, t, fc=tint(c, "18"), fontsize=6.0)
        line(ax, [(xf, 7.6), (xf, yl + 1.1), (17.1, yl + 1.1)], color=c, lw=1.8, arrow_end=True)
    # gateway and modem
    box(ax, 5.0, 0.6, 4.4, 2.4, "Gateway\nembedded Linux, ~3 W\nshedding logic", fc=tint(PINK, "30"),
        fontsize=fs)
    box(ax, 0.2, 0.9, 3.2, 1.8, "4G modem\n→ cloud\nMQTT broker", fc="white", fontsize=6.4)
    line(ax, [(5.0, 1.8), (3.4, 1.8)], arrow_end=True, **DL)
    # data links
    line(ax, [(7.0, y0), (7.0, 3.0)], both=True, **DL)
    ax.text(6.85, 6.2, "VE.Direct or\nModbus RTU", fontsize=5.8, color=GREY, ha="right", va="center")
    line(ax, [(11.15, 6.6), (11.15, 4.2), (8.2, 4.2), (8.2, 3.0)], both=True, **DL)
    ax.text(9.7, 4.3, "CAN 500 kbit/s (BMS)", fontsize=5.8, color=GREY, ha="center", va="bottom")
    line(ax, [(13.3, y0), (13.3, 3.6), (9.0, 3.6), (9.0, 3.0)], both=True, **DL)
    ax.text(11.2, 3.5, "serial / Modbus (inverter)", fontsize=5.8, color=GREY, ha="center", va="top")
    line(ax, [(9.4, 1.0), (16.1, 1.0), (16.1, 5.7), (17.1, 5.7)], **DL)
    ax.text(12.7, 0.9, "1-wire probe in vaccine fridge", fontsize=5.8, color=GREY, ha="center", va="top")
    line(ax, [(9.4, 2.2), (15.85, 2.2), (15.85, 9.6), (16.15, 9.6)], arrow_end=True, color=PINK, lw=1.0,
         ls=(0, (2, 2)))
    ax.text(12.7, 2.3, "shed contactors (comfort, pump)", fontsize=5.8, color=PINK, ha="center",
            va="bottom")
    # legend
    ax.add_line(Line2D([0.3, 1.2], [14.3, 14.3], color=INK, lw=2.6))
    ax.text(1.35, 14.3, "power", fontsize=6.6, va="center")
    ax.add_line(Line2D([2.6, 3.5], [14.3, 14.3], color=GREY, lw=1.1, ls=(0, (4, 2))))
    ax.text(3.65, 14.3, "data", fontsize=6.6, va="center")
    ax.add_line(Line2D([4.7, 5.6], [14.3, 14.3], color=PINK, lw=1.0, ls=(0, (2, 2))))
    ax.text(5.75, 14.3, "control", fontsize=6.6, va="center")
    save(fig, "36", "fig-36-1-system-architecture")


# ----------------------------------------------------------------------------
# Figure 36.2 — daily load and PV
# ----------------------------------------------------------------------------
def fig_36_2():
    p, p_ac, p_dc = load_profile()
    pv = pv_day(3.9)
    h = np.arange(24)
    print(f"  AC {p_ac.sum() / 1e3:.2f} kWh, DC {p_dc.sum() / 1e3:.2f} kWh, PV {pv.sum() / 1e3:.2f} kWh,"
          f" PV peak {pv.max():.0f} W, battery share {np.clip(p_dc - pv, 0, None).sum() / p_dc.sum():.2f}")
    fig, ax = plt.subplots(figsize=(6.8, 4.2))
    # step representation (hour slots)
    xs = np.repeat(np.arange(25), 2)[1:-1]
    st = lambda y: np.repeat(y, 2)  # noqa: E731
    direct = np.minimum(pv, p_dc)
    ax.fill_between(xs, 0, st(direct), color=YELLOW, alpha=0.25, lw=0, label="PV direct to load")
    ax.fill_between(xs, st(p_dc), st(np.maximum(pv, p_dc)), color=YELLOW, alpha=0.55, lw=0,
                    label="PV to battery (surplus)")
    ax.fill_between(xs, st(pv), st(np.maximum(pv, p_dc)), where=st(p_dc > pv), color=GREEN, alpha=0.22,
                    lw=0, label="battery to load")
    bottom = np.zeros(24)
    for c, col in (("critical", RED), ("comfort", BLUE), ("pump", GREEN)):
        ax.bar(h + 0.5, p[c], width=0.7, bottom=bottom, color=col, alpha=0.85,
               label=f"AC load: {c}")
        bottom += p[c]
    ax.plot(xs, st(p_dc), color=INK, lw=1.0, ls="--", label="DC load at battery bus")
    ax.plot(h + 0.5, pv, color=ORANGE, lw=2.0, marker="o", ms=3, label="PV DC output (3.9 kWh/m² day)")
    for x, lab in ((5.5, "187"), (7.5, "481"), (11.5, "464"), (14.5, "409"), (20.5, "220"), (2.5, "68")):
        k = int(x)
        ax.text(x, p_ac[k] + 12, lab, ha="center", va="bottom", fontsize=6.6, color=INK)
    ax.set_xlim(0, 24)
    ax.set_ylim(0, 1100)
    ax.set_xticks(range(0, 25, 3))
    ax.set_xlabel("Hour of day")
    ax.set_ylabel("Power (W)")
    ax.legend(loc="upper left", fontsize=6.8, ncol=1, bbox_to_anchor=(0.0, 1.0))
    ax.text(23.7, 1070, f"AC load {p_ac.sum() / 1e3:.2f} kWh/day\nDC load {p_dc.sum() / 1e3:.2f} kWh/day\n"
            f"PV {pv.sum() / 1e3:.1f} kWh/day", ha="right", va="top", fontsize=7.4,
            bbox=dict(fc="white", ec=GREY, lw=0.6, pad=3))
    save(fig, "36", "fig-36-2-daily-load-and-pv")


# ----------------------------------------------------------------------------
# Figure 36.3 — monthly yield vs demand
# ----------------------------------------------------------------------------
def fig_36_3():
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    poa = np.array([5.0, 5.6, 5.8, 5.6, 5.1, 4.1, 3.9, 4.1, 4.0, 4.8, 5.1, 4.9])
    yld = 2.46 * 0.794 * poa
    print("  yields", np.round(yld, 1))
    need, rec = 5.80, 5.80 * 1.2
    x = np.arange(12)
    fig, ax = plt.subplots(figsize=(6.6, 3.9))
    ax.bar(x, np.minimum(yld, need), width=0.7, color=BLUE, alpha=0.85, label="yield used by the load")
    ax.bar(x, yld - need, bottom=need, width=0.7, color=BLUE, alpha=0.3, hatch="///", edgecolor=BLUE,
           lw=0, label="surplus: battery refill, curtailed\nor deferrable loads")
    for xi, y in zip(x, yld):
        ax.text(xi, y + 0.15, f"{y:.1f}", ha="center", va="bottom", fontsize=7.2)
    ax.axhline(need, color=INK, lw=1.6)
    ax.axhline(rec, color=INK, lw=1.2, ls="--")
    ax.text(11.5, need - 0.1, "PV energy\nneeded 5.80", ha="left", va="top", fontsize=7.2,
            clip_on=False)
    ax.text(11.5, rec + 0.1, "× 1.2 recovery\n= 6.96", ha="left", va="bottom", fontsize=7.2,
            clip_on=False)
    ax.bar(6, yld[6], width=0.7, fill=False, edgecolor=RED, lw=1.8)
    ax.annotate("design month\nJuly, 3.9 kWh/m²/day POA", (6, yld[6] + 0.6), xytext=(6, 10.4),
                ha="center", va="bottom", fontsize=7.2, color=RED,
                arrowprops=dict(arrowstyle="-|>", color=RED, lw=0.9, mutation_scale=8))
    ax.set_xticks(x)
    ax.set_xticklabels(months)
    ax.set_ylim(0, 14.6)
    ax.set_ylabel("Energy (kWh/day)")
    ax.set_title("2.46 kWp at $PR_{PV}$ = 0.794, 25° tilt south", fontsize=9)
    ax.legend(loc="upper left", fontsize=7, ncol=2)
    save(fig, "36", "fig-36-3-monthly-yield-vs-demand")


# ----------------------------------------------------------------------------
# Figure 36.4 — monsoon week SoC
# ----------------------------------------------------------------------------
def fig_36_4():
    week = [3.9, 1.6, 1.2, 2.0, 3.1, 4.4, 3.9]
    runs = [("3 modules, new (15.36 kWh)", 15.36e3, BLUE, "-"),
            ("3 modules at 80 % SoH (12.29 kWh)", 0.8 * 15.36e3, ORANGE, "-"),
            ("2 modules, new (10.24 kWh)", 10.24e3, RED, "-")]
    t = np.arange(1, 7 * 24 + 1)
    fig, ax = plt.subplots(figsize=(6.8, 4.0))
    floor2 = None
    for name, e, c, ls in runs:
        soc, uns, floor = simulate(e, week)
        k = int(np.argmin(soc))
        print(f"  {name}: min {soc.min() * 100:.1f} % at hour {k}, unserved {uns / 1e3:.2f} kWh")
        lab = name + (f", unserved {uns / 1e3:.2f} kWh" if uns > 0 else f", min {soc.min() * 100:.1f} %")
        ax.plot(np.r_[0, t], 100 * np.r_[0.8, soc], color=c, ls=ls, lw=1.6, label=lab)
        if uns > 0:
            floor2 = floor
        else:
            ax.plot(t[k], 100 * soc[k], "o", color=c, ms=4)
    for hh in np.flatnonzero(floor2):
        ax.axvspan(t[hh] - 1, t[hh], color=RED, alpha=0.18, lw=0)
    for y, lab, ls in ((30, "30 %: comfort shed", "--"), (20, "20 %: critical only", "--"),
                       (10, "10 %: BMS floor", ":")):
        ax.axhline(y, color=GREY, ls=ls, lw=1.0)
        ax.text(167, y + 0.8, lab, ha="right", va="bottom", fontsize=7, color=GREY)
    for d in range(8):
        ax.axvline(24 * d, color="#CCCCCC", lw=0.7, zorder=0)
    for d, hp in enumerate(week):
        ax.text(24 * d + 12, 103, f"{hp}", ha="center", va="bottom", fontsize=7.4)
    ax.text(-2, 103, "POA:", ha="right", va="bottom", fontsize=7.2)
    ax.text(84, 109.5, "daily POA irradiation (kWh/m²/day)", ha="center", va="bottom", fontsize=7.2,
            color=GREY)
    ax.set_xlim(0, 168)
    ax.set_ylim(0, 100)
    ax.set_xticks(range(0, 169, 24))
    ax.set_xlabel("Time (h)")
    ax.set_ylabel("State of charge (%)")
    ax.legend(loc="upper right", fontsize=7, bbox_to_anchor=(1.0, 0.99))
    save(fig, "36", "fig-36-4-monsoon-week-soc")


# ----------------------------------------------------------------------------
# Figure 36.5 — LFP charge profile on a clear day
# ----------------------------------------------------------------------------
def charge_day(soc0, R=0.006, AH=300.0, dt=1 / 60):
    """Clear-day MPPT charge of the 16S LFP bank: bulk, absorption at 55.2 V, float at 53.6 V."""
    soc_pts = np.array([0.00, 0.10, 0.20, 0.30, 0.40, 0.60, 0.80, 0.90, 0.94, 0.97, 1.00])
    ocv_pts = 16 * np.array([3.00, 3.17, 3.215, 3.243, 3.275, 3.300, 3.320, 3.335, 3.370, 3.420, 3.500])
    from scipy.interpolate import PchipInterpolator
    ocv_f = PchipInterpolator(soc_pts, ocv_pts)
    th =np.arange(6.0, 18.0 + 1e-9, dt)
    i_pv = 41.0 * np.clip(np.sin(np.pi * (th - 6) / 12), 0, None) - 1.2   # net of daytime load
    soc, mode, t_abs, t_fl, i_abs0 = soc0, "bulk", None, None, None
    V, I, M = [], [], []
    for t, ip in zip(th, i_pv):
        ocv = float(ocv_f(soc))
        if mode == "bulk":
            i, v = ip, ocv + R * ip
            if v >= 55.2:
                mode, t_abs, i_abs0 = "abs", t, ip
        if mode == "abs":
            i, v = min(ip, i_abs0 * np.exp(-(t - t_abs) / 0.47)), 55.2
            if i <= 6.0:
                mode, t_fl = "float", t
        if mode == "float":
            i, v = min(ip, 0.8 * np.exp(-(t - t_fl) / 1.0)), 53.6
        soc = min(soc + i * dt / AH, 1.0)
        V.append(v)
        I.append(i)
        M.append(mode)
    return th, np.array(V), np.array(I), np.array(M), t_abs, t_fl


def fig_36_5():
    lo, hi = 0.0, 0.6                                   # start SoC giving absorption at 13:30
    for _ in range(40):
        mid = (lo + hi) / 2
        t_abs = charge_day(mid)[4]
        if t_abs is None or t_abs > 13.5:
            lo = mid
        else:
            hi = mid
    th, V, I, M, t_ab, t_fl = charge_day(hi)
    print(f"  start SoC {hi:.3f}: V(06)={V[0]:.2f}  abs at {t_ab:.2f} h, float at {t_fl:.2f} h,"
          f" peak I {I.max():.1f} A, V(12)={V[np.argmin(abs(th - 12))]:.2f}")
    fig, ax = plt.subplots(figsize=(6.8, 4.0))
    a2 = ax.twinx()
    a2.spines["right"].set_visible(True)
    for (t0, t1, name, c) in ((6, t_ab, "Bulk", BLUE), (t_ab, t_fl, "Absorption", ORANGE),
                              (t_fl, 18, "Float", GREEN)):
        ax.axvspan(t0, t1, color=c, alpha=0.10, lw=0)
        ax.text((t0 + t1) / 2 if name != "Absorption" else t0 + 0.05, 55.93, name,
                ha="center" if name != "Absorption" else "left", va="top", fontsize=7.6, color=c,
                weight="bold")
    ax.plot(th, V, color=BLUE, lw=1.8)
    a2.plot(th, I, color=ORANGE, lw=1.6)
    ax.axhline(55.2, color=BLUE, lw=0.7, ls=":")
    ax.axhline(53.6, color=BLUE, lw=0.7, ls=":")
    ax.text(6.1, 55.25, "absorption 55.2 V", fontsize=6.8, color=BLUE, va="bottom")
    ax.text(17.9, 53.65, "float 53.6 V", fontsize=6.8, color=BLUE, va="bottom", ha="right")
    a2.axhline(6, color=ORANGE, lw=0.7, ls=":")
    a2.text(17.9, 6.6, "6 A tail (0.02C)", fontsize=6.8, color=ORANGE, ha="right", va="bottom")
    a2.axhline(0, color=GREY, lw=0.6)
    ax.annotate(f"{t_ab:.0f}:{(t_ab % 1) * 60:02.0f}", (t_ab, 55.2), xytext=(t_ab - 1.3, 54.6),
                fontsize=6.8, color=INK, arrowprops=dict(arrowstyle="-", lw=0.6))
    ax.annotate(f"{int(t_fl)}:{round((t_fl % 1) * 60):02d}", (t_fl, 53.6), xytext=(t_fl + 0.5, 53.0),
                fontsize=6.8, color=INK, arrowprops=dict(arrowstyle="-", lw=0.6))
    ax.text(9.0, 52.9, "LFP plateau", fontsize=7, color=BLUE, ha="center")
    ax.set_xlim(6, 18)
    ax.set_ylim(50, 56)
    a2.set_ylim(-10, 50)
    ax.set_xticks(range(6, 19, 2))
    ax.set_xticklabels([f"{h:02d}:00" for h in range(6, 19, 2)])
    ax.set_xlabel("Time of day")
    ax.set_ylabel("Battery voltage (V)", color=BLUE)
    a2.set_ylabel("Net charge current (A)", color=ORANGE)
    ax.tick_params(axis="y", colors=BLUE)
    a2.tick_params(axis="y", colors=ORANGE)
    hs = [Line2D([], [], color=BLUE, lw=1.8), Line2D([], [], color=ORANGE, lw=1.6)]
    ax.legend(hs, ["battery voltage", "net charge current"], loc="lower left", fontsize=7.4,
              bbox_to_anchor=(0.0, 0.0))
    save(fig, "36", "fig-36-5-lfp-charge-profile")


if __name__ == "__main__":
    _only = sys.argv[1:]
    for _f in (fig_36_1, fig_36_2, fig_36_3, fig_36_4, fig_36_5):
        if not _only or _f.__name__[-1] in _only:
            _f()
