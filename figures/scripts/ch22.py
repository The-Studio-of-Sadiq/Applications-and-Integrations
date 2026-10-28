"""Figures for Chapter 22 — Solar PV System Design.

Run from the repository root:  python figures/scripts/ch22.py
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
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# Chosen module (Section 22.3) and the inverter window (Section 22.5)
MOD = dict(Voc=49.8, Vmp=41.9, Isc=14.0, Imp=13.13, b_voc=-0.0026, b_vmp=-0.0034, a_isc=0.00046)


def line(ax, pts, color=INK, lw=1.2, ls="-", arrow_end=False, z=2):
    xs, ys = zip(*pts)
    if not arrow_end:
        ax.plot(xs, ys, color=color, lw=lw, ls=ls, solid_capstyle="butt", zorder=z)
        return
    if len(pts) > 2:
        ax.plot(xs[:-1], ys[:-1], color=color, lw=lw, ls=ls, zorder=z)
    ax.annotate("", xy=pts[-1], xytext=pts[-2],
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, ls=ls, shrinkA=0,
                                shrinkB=0, mutation_scale=10), zorder=z)


def rbox(ax, x, y, w, h, text="", fc="#EEF3F8", ec=INK, fs=7.8, lw=1.0, z=3, weight="normal",
         ha="center", va="center", tx=None, ty=None):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc=fc, ec=ec, lw=lw, zorder=z))
    if text:
        ax.text(x + w / 2 if tx is None else tx, y + h / 2 if ty is None else ty, text, ha=ha,
                va=va, fontsize=fs, color=INK, zorder=z + 0.5, weight=weight, linespacing=1.2)


# ----------------------------------------------------------------------------
# Single-diode-shaped explicit I-V model (used for Figures 22.4 and 22.6)
# ----------------------------------------------------------------------------
class ExplicitIV:
    """I = Isc [1 - C1 (exp(V / (C2 Voc)) - 1)], fitted through (Voc, Isc, Vmp, Imp)."""

    def __init__(self, Voc, Isc, Vmp, Imp):
        self.Voc, self.Isc = Voc, Isc
        self.C2 = (Vmp / Voc - 1) / np.log(1 - Imp / Isc)
        self.C1 = (1 - Imp / Isc) * np.exp(-Vmp / (self.C2 * Voc))

    def v_of_i(self, i):
        """Voltage at current i (i <= Isc); NaN where i > Isc."""
        arg = 1 + (1 - np.asarray(i) / self.Isc) / self.C1
        with np.errstate(invalid="ignore", divide="ignore"):
            return np.where(arg > 0, self.C2 * self.Voc * np.log(arg), np.nan)

    def i_of_v(self, v):
        return np.clip(self.Isc * (1 - self.C1 * (np.exp(np.asarray(v) / (self.C2 * self.Voc)) - 1)),
                       0, None)


# ----------------------------------------------------------------------------
# Figure 22.1 — architecture and single-line diagram
# ----------------------------------------------------------------------------
def fig_22_1():
    fig, ax = schematic(6.8, 5.4, xlim=(0, 17), ylim=(0, 13.5))
    PW, DATA = INK, BLUE
    # sensors and array
    rbox(ax, 0.2, 11.7, 3.6, 1.2, "POA reference cell\nPt1000 on module", fc="#E8F1FB", fs=7.0)
    rbox(ax, 0.2, 8.95, 3.0, 1.5, "String S1\n10 × 550 W\nM1 to M10", fc="#FFF4D6", fs=7.2)
    rbox(ax, 0.2, 6.65, 3.0, 1.5, "String S2\n10 × 550 W\nM11 to M20", fc="#FFF4D6", fs=7.2)
    ax.text(0.2, 6.3, "roof array 11.0 kWp\neach string: 2 × 6 mm²\nH1Z2Z2-K, 25 m one-way",
            fontsize=6.7, ha="left", va="top", color=GREY, style="italic")
    # inverter
    ax.add_patch(FancyBboxPatch((6.2, 3.9), 5.0, 7.75, boxstyle="round,pad=0,rounding_size=0.25",
                                fc="#F3F7FB", ec=INK, lw=1.3, zorder=1))
    ax.text(8.7, 11.45, "Hybrid inverter 10 kW, 3-phase\nwith integrated DC isolator",
            fontsize=7.2, ha="center", va="top", weight="bold", zorder=2)
    rbox(ax, 6.4, 9.0, 2.2, 1.4, "MPPT1\n200-850 V\n16 A", fc="white", fs=6.9)
    rbox(ax, 6.4, 6.7, 2.2, 1.4, "MPPT2\n200-850 V\n16 A", fc="white", fs=6.9)
    rbox(ax, 6.4, 4.1, 2.2, 1.9, "Battery\nport DC-DC\n150-600 V\n25 A", fc="white", fs=6.9)
    rbox(ax, 9.0, 6.7, 2.0, 2.3, "DC link\n+ 3-phase\nbridge", fc="white", fs=6.9)
    rbox(ax, 9.0, 4.1, 2.0, 2.05, "Insulation\nmonitor\nRCMU\ngrid relay", fc="white", fs=6.8)
    line(ax, [(8.6, 9.7), (9.5, 9.7), (9.5, 9.0)], color=PW, lw=1.4)
    line(ax, [(8.6, 7.4), (9.0, 7.4)], color=PW, lw=1.4)
    line(ax, [(8.6, 5.05), (8.8, 5.05), (8.8, 6.4), (9.4, 6.4), (9.4, 6.7)], color=PW, lw=1.4)
    # string cables with SPDs
    for yc in (9.7, 7.4):
        line(ax, [(3.2, yc), (6.4, yc)], color=PW, lw=1.8, arrow_end=True)
        ax.text(4.35, yc + 0.1, "6 mm², 25 m", fontsize=6.5, ha="center", va="bottom")
        line(ax, [(5.4, yc), (5.4, yc - 0.45)], color=PW, lw=1.0)
        rbox(ax, 4.6, yc - 1.05, 1.6, 0.6, "DC SPD T2", fc="#FBE3D6", ec=ORANGE, fs=6.5)
    ax.text(5.4, 6.2, "U$_{CPV}$ 600 V\nper string", fontsize=6.5, ha="center", va="top",
            color=ORANGE)
    # battery
    rbox(ax, 6.2, 0.2, 5.0, 2.0,
         "LFP battery 10.24 kWh\n4 × 2.56 kWh modules\n204.8 V nominal, BMS", fc="#E6F4EC", fs=7.0)
    line(ax, [(7.5, 2.2), (7.5, 4.1)], color=PW, lw=1.8)
    rbox(ax, 6.55, 2.75, 1.9, 0.85, "DC breaker\n32 A", fc="white", fs=6.5, z=4)
    line(ax, [(10.3, 2.2), (10.3, 4.1)], color=DATA, lw=1.2, ls=(0, (4, 2)))
    ax.text(10.45, 3.15, "CAN\n(BMS limits)", fontsize=6.5, color=DATA, va="center")
    # AC side
    line(ax, [(11.0, 8.0), (12.55, 8.0)], color=PW, lw=1.8, arrow_end=True)
    ax.text(11.88, 8.1, "5 × 6 mm²\n30 m", fontsize=6.2, ha="center", va="bottom")
    rbox(ax, 12.55, 6.7, 2.15, 2.6, "Sub-board\n20 A MCB\nRCD type A\n30 mA*\nAC SPD T2",
         fc="white", fs=6.7)
    line(ax, [(14.7, 8.0), (15.0, 8.0)], color=PW, lw=1.8, arrow_end=True)
    rbox(ax, 15.0, 6.7, 1.85, 2.6, "Main\nincomer\nexport\nmeter\n(CT)", fc="white", fs=6.7)
    line(ax, [(15.92, 9.3), (15.92, 9.9)], color=PW, lw=1.8)
    rbox(ax, 15.0, 9.9, 1.85, 1.2, "Grid\n400 V 3-ph", fc="#ECECEC", fs=6.8)
    line(ax, [(15.92, 6.7), (15.92, 6.1), (11.2, 6.1)], color=DATA, lw=1.2, ls=(0, (4, 2)),
         arrow_end=True)
    ax.text(13.6, 6.18, "Modbus: export limit 10 kW", fontsize=6.4, color=DATA, ha="center",
            va="bottom")
    # EPS / backup
    line(ax, [(11.2, 4.6), (12.3, 4.6)], color=PW, lw=1.8, arrow_end=True)
    ax.text(11.75, 4.72, "EPS", fontsize=6.6, ha="center", va="bottom")
    rbox(ax, 12.3, 3.9, 1.9, 1.4, "Backup\nboard", fc="white", fs=6.8)
    line(ax, [(14.2, 4.6), (14.55, 4.6)], color=PW, lw=1.8, arrow_end=True)
    rbox(ax, 14.55, 3.55, 2.35, 2.1, "Server room\n+ emergency\nlighting\n1.2 kW", fc="#FCE4E4",
         fs=6.6)
    # monitoring
    rbox(ax, 12.3, 11.9, 4.55, 1.0, "Monitoring gateway", fc="#E8F1FB", fs=7.0)
    line(ax, [(3.8, 12.4), (12.3, 12.4)], color=DATA, lw=1.2, ls=(0, (4, 2)), arrow_end=True)
    line(ax, [(12.9, 11.9), (12.9, 10.5), (11.2, 10.5)], color=DATA, lw=1.2, ls=(0, (4, 2)))
    ax.text(13.05, 11.05,"inverter and\nbattery data", fontsize=6.3, color=DATA, va="center")
    # legend and footnote
    ax.plot([12.3, 13.2], [1.9, 1.9], color=PW, lw=1.8)
    ax.text(13.35, 1.9, "power flow", fontsize=7, va="center")
    ax.plot([12.3, 13.2], [1.3, 1.3], color=DATA, lw=1.2, ls=(0, (4, 2)))
    ax.text(13.35, 1.3, "data", fontsize=7, va="center")
    ax.text(12.3, 0.55, "* or as the inverter declares", fontsize=6.4, color=GREY, va="center")
    save(fig, "22", "fig-22-1-school-pv-architecture")


# ----------------------------------------------------------------------------
# Figure 22.2 — monthly resource, yield and consumption
# ----------------------------------------------------------------------------
GHI = np.array([60, 80, 125, 150, 185, 205, 220, 195, 150, 105, 70, 55])
POA = np.array([79, 98, 141, 157, 185, 200, 217, 201, 165, 125, 92, 75])


def monthly_pr():
    """Monthly PR, 0.86 in January falling to 0.80 in July.

    Shape w = ((1 + cos)/2)^p, with p solved so that the annual sum is the model's 15,800 kWh."""
    from scipy.optimize import brentq
    m = np.arange(12)
    base = (1 + np.cos(2 * np.pi * m / 12)) / 2

    def pr(p):
        return 0.80 + 0.06 * base ** p

    p = brentq(lambda p: (11.0 * POA * pr(p)).sum() - 15800, 0.05, 5)
    return pr(p)


def fig_22_2():
    pr = monthly_pr()
    e_ac = 11.0 * POA * pr
    load = np.array([2300, 2300, 2200, 2000, 2200, 2200, 1300, 900, 2200, 2200, 2300, 1900])
    x = np.arange(12)
    fig, ax = new_fig(6.6, 4.0)
    ax.axvspan(5.5, 7.5, color="#F2F2F2", zorder=0)
    ax.text(6.5, 262, "school holiday,\nexport-limited", ha="center", va="top", fontsize=7.4,
            color=GREY)
    ax.bar(x - 0.19, GHI, 0.38, color=SKY, label="GHI (kWh/m²)", zorder=2)
    ax.bar(x + 0.19, POA, 0.38, color=YELLOW, label="POA, 15° south (kWh/m²)", zorder=2)
    ax.set_ylim(0, 250)
    ax.set_ylabel("Monthly irradiation (kWh/m²)")
    ax.set_xticks(x)
    ax.set_xticklabels(MONTHS)
    ax2 = ax.twinx()
    ax2.spines["right"].set_visible(True)
    ax2.plot(x, e_ac, color=ORANGE, marker="o", ms=4, lw=2,
             label=f"Predicted AC energy, 11.0 × POA × PR ({e_ac.sum():,.0f} kWh/yr)")
    ax2.plot(x, load, color=INK, ls="--", marker="s", ms=3.2, lw=1.5,
             label=f"School consumption ({load.sum():,.0f} kWh/yr)")
    ax2.set_ylim(0, 3000)
    ax2.set_ylabel("Monthly energy (kWh)")
    for k in (0, 6):
        ax2.annotate(f"PR {pr[k]:.2f}", xy=(x[k], e_ac[k]), xytext=(x[k] + 0.35, e_ac[k] + 330),
                     fontsize=7.4, color=ORANGE,
                     bbox=dict(fc="white", ec="none", pad=0.6),
                     arrowprops=dict(arrowstyle="-", color=ORANGE, lw=0.7))
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, fontsize=7.4, loc="upper center", ncol=2,
              bbox_to_anchor=(0.5, -0.1))
    ax.set_ylim(0, 265)
    ax.set_yticks(range(0, 251, 50))
    ax2.set_ylim(0, 3180)
    ax2.set_yticks(range(0, 3001, 500))
    save(fig, "22", "fig-22-2-monthly-resource-and-yield")
    return e_ac.sum()


# ----------------------------------------------------------------------------
# Figure 22.3 — string voltage window
# ----------------------------------------------------------------------------
def fig_22_3():
    T = np.linspace(-20, 80, 201)
    voc = MOD["Voc"] * (1 + MOD["b_voc"] * (T - 25))
    vmp = MOD["Vmp"] * (1 + MOD["b_vmp"] * (T - 25))
    fig, ax = new_fig(6.4, 4.2)
    ax.axhspan(200, 850, color=GREEN, alpha=0.12, zorder=0)
    ax.text(79, 835, "MPPT window 200-850 V", fontsize=7.8, color=GREEN, ha="right", va="top")
    ax.axhline(1000, color=RED, lw=1.6)
    ax.text(79, 1012, "1,000 V maximum DC input", fontsize=8, color=RED, ha="right", va="bottom")
    ax.axhline(320, color=INK, lw=1.0, ls=":")
    ax.text(79, 312, "320 V: 5 kW per tracker", fontsize=7.6, ha="right", va="top")
    for n, c in ((20, ORANGE), (10, BLUE)):
        ax.plot(T, n * voc, color=c, lw=2, label=f"$V_{{OC}}$, {n} modules")
        ax.plot(T, n * vmp, color=c, lw=2, ls="--", label=f"$V_{{mp}}$, {n} modules")
    for tv, lab in ((-15, "record low\n−15 °C"), (75, "hot roof\n75 °C")):
        ax.axvline(tv, color=GREY, ls="--", lw=1.0)
        ax.text(tv + (1 if tv < 0 else -1), 70, lab, fontsize=7.6, color=GREY, va="bottom", ha="left" if tv < 0 else "right")
    # key points
    pts = [(-15, 20 * MOD["Voc"] * (1 + MOD["b_voc"] * -40), "1,099.6 V", (-14, 1130)),
           (-15, 10 * MOD["Voc"] * (1 + MOD["b_voc"] * -40), "549.8 V", (-13.5, 575)),
           (75, 20 * MOD["Vmp"] * (1 + MOD["b_vmp"] * 50), "695.5 V", (64, 640)),
           (75, 10 * MOD["Vmp"] * (1 + MOD["b_vmp"] * 50), "347.8 V", (64, 380))]
    for x, y, lab, xyt in pts:
        ax.plot(x, y, "o", color=INK, ms=3.5, zorder=5)
        ax.text(*xyt, lab, fontsize=7.6)
    t_cross = 25 + (1000 / (20 * MOD["Voc"]) - 1) / MOD["b_voc"]
    ax.plot(t_cross, 1000, "o", color=RED, ms=8, mfc="none", mew=2, zorder=6)
    ax.annotate(f"original design ({t_cross:.1f} °C):\nover the limit at any colder\ncell temperature",
                xy=(t_cross, 1000), xytext=(30, 1085), fontsize=7.6, color=RED,
                arrowprops=dict(arrowstyle="-", color=RED, lw=0.8))
    ax.set_xlim(-20, 80)
    ax.set_ylim(0, 1200)
    ax.set_xlabel("Cell temperature (°C)")
    ax.set_ylabel("String voltage (V)")
    ax.legend(fontsize=7.6, loc="lower center", bbox_to_anchor=(0.5, 0.0), ncol=2)
    save(fig, "22", "fig-22-3-string-voltage-window")


# ----------------------------------------------------------------------------
# Figure 22.4 — P&O tracking through a shading event
# ----------------------------------------------------------------------------
def string_pv(k_shade, n_shaded=4, n_sub=30, v_bypass=-0.5):
    """P-V curve of a 10-module string (30 bypass-protected substrings).

    Operating condition of a winter morning: module MPP 40.5 V, 9.4 A (string MPP 405 V,
    3.81 kW unshaded). n_shaded substrings receive k_shade of the irradiance."""
    sub = ExplicitIV(Voc=49.5 / 3, Isc=9.95, Vmp=40.5 / 3, Imp=9.4)
    sub_s = ExplicitIV(Voc=49.5 / 3 - 0.35, Isc=9.95 * k_shade, Vmp=40.5 / 3 - 0.35,
                       Imp=9.4 * k_shade)
    i = np.linspace(0, 9.95, 20000)
    vu = sub.v_of_i(i)
    vs = np.where(i < sub_s.Isc, sub_s.v_of_i(np.minimum(i, sub_s.Isc * 0.99999)), v_bypass)
    vs = np.maximum(vs, v_bypass)
    v = (n_sub - n_shaded) * vu + n_shaded * vs
    order = np.argsort(v)
    v, i = v[order], i[order]
    return v, v * i


def fig_22_4():
    rng = np.random.default_rng(4)
    v0, p0 = string_pv(1.0, n_shaded=0)
    v1, p1 = string_pv(0.60)
    P = lambda v, sh: np.interp(v, v1, p1) if sh else np.interp(v, v0, p0)  # noqa: E731
    dt = 0.1
    t = np.arange(0, 1200, dt)
    # tracker state, exactly as mppt.c
    V_MIN, V_MAX, V_SCAN_HI, V_STEP, P_DB, SCAN_PERIOD, SCAN_POINTS = 200, 850, 520, 2.0, 5.0, 9000, 24
    st = dict(v_ref=405.0, p_prev=0.0, dir=1.0, best_v=0.0, best_p=0.0, ticks=0, k=0, scanning=False)
    vref, ptrk, pav = np.empty_like(t), np.empty_like(t), np.empty_like(t)
    for n, tk in enumerate(t):
        sh = tk >= 300
        v = st["v_ref"]
        p = P(v, sh) + rng.normal(0, 0.5)
        vref[n], ptrk[n] = v, P(v, sh)
        pav[n] = (p1 if sh else p0).max()
        if st["scanning"]:
            if p > st["best_p"]:
                st["best_p"], st["best_v"] = p, v
            st["k"] += 1
            if st["k"] < SCAN_POINTS:
                st["v_ref"] = V_MIN + (V_SCAN_HI - V_MIN) * st["k"] / (SCAN_POINTS - 1)
            else:
                st["scanning"] = False
                st["v_ref"], st["p_prev"] = st["best_v"], st["best_p"]
            continue
        st["ticks"] += 1
        if st["ticks"] >= SCAN_PERIOD:
            st.update(v_ref=V_MIN, scanning=True, best_v=st["v_ref"], best_p=0.0, k=0, ticks=0,
                      p_prev=0.0)
            continue
        if p - st["p_prev"] < -P_DB:
            st["dir"] = -st["dir"]
        st["p_prev"] = p
        st["v_ref"] = min(max(st["v_ref"] + st["dir"] * V_STEP, V_MIN), V_MAX)
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.6, 4.8), sharex=True,
                                 gridspec_kw=dict(hspace=0.12))
    a1.plot(t, vref, color=BLUE, lw=0.8)
    a1.set_ylim(200, 520)
    a1.set_ylabel("Voltage reference (V)")
    a1.axvline(300, color=GREY, ls=":", lw=1)
    a1.axvline(900, color=GREY, ls=":", lw=1)
    vb, ve = vref[(t > 200) & (t < 300)], vref[(t > 600) & (t < 900)]
    a1.text(20, 470, f"P&O around {vb.mean():.0f} V\n(±{(vb.max() - vb.min()) / 2:.0f} V)",
            fontsize=7.6)
    a1.text(310, 470, "two modules shaded by a stack:\nP&O stays on the local maximum"
            f" near {ve.mean():.0f} V", fontsize=7.6)
    a1.annotate("global scan 200-520 V in 2.4 s", xy=(900, 300), xytext=(560, 240), fontsize=7.6,
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.8, mutation_scale=8))
    vg = vref[(t > 905) & (t < 1200)].mean()
    a1.text(925, 300, f"new reference\n≈ {vg:.0f} V", fontsize=7.6, va="top")
    a2.plot(t, pav / 1e3, color=INK, ls="--", lw=1.3, label="available MPP power (global)")
    a2.plot(t, ptrk / 1e3, color=ORANGE, lw=1.4, label="tracked power")
    m = (t >= 300) & (t <= 905)
    a2.fill_between(t[m], ptrk[m] / 1e3, pav[m] / 1e3, color=RED, alpha=0.18, lw=0)
    lost = np.sum((pav[m] - ptrk[m])) * dt / 3.6e6
    a2.text(600, 3.95, f"energy lost to local maximum: {lost * 1e3:.0f} Wh in 10 min",
            ha="center", va="center", fontsize=7.6, color=RED)
    a2.text(310, 1.85, f"local max {ptrk[(t > 400) & (t < 900)].mean() / 1e3:.1f} kW",
            fontsize=7.6)
    a2.text(1195, 3.45, f"global max {p1.max() / 1e3:.1f} kW", fontsize=7.6, ha="right")
    a2.text(912, 0.9, "scan", fontsize=7.2, color=GREY)
    a2.set_ylim(0, 4.6)
    a2.set_ylabel("String S2 power (kW)")
    a2.set_xlabel("Time (s)")
    a2.set_xlim(0, 1200)
    a2.legend(fontsize=7.4, loc="lower left", ncol=2)
    save(fig, "22", "fig-22-4-mppt-trace")
    return v1[np.argmax(p1)], p1.max(), p0.max(), v0[np.argmax(p0)]


# ----------------------------------------------------------------------------
# Figure 22.5 — loss waterfall
# ----------------------------------------------------------------------------
LOSSES = [("near shading", 0.015), ("soiling", 0.020), ("IAM", 0.025), ("low irradiance", 0.010),
          ("temperature", 0.050), ("module quality\nand LID", 0.010), ("mismatch", 0.010),
          ("DC cabling", 0.003), ("inverter\nconversion", 0.024), ("clipping", 0.002),
          ("AC cabling", 0.005), ("availability", 0.010)]


def fig_22_5():
    E = 11.0 * 1734
    steps = []
    for name, f in LOSSES:
        dE = E * f
        steps.append((name, E, dE))
        E -= dE
    fig, ax = new_fig(6.8, 4.2)
    labels = ["nominal, 11.0 kWp × 1734"] + [s[0].replace(chr(10), " ") for s in steps] + ["AC energy"]
    ax.bar(0, 11.0 * 1734, color=BLUE, width=0.7)
    ax.text(0, 17000, f"{11.0 * 1734:,.0f} kWh", ha="center", va="center", rotation=90, fontsize=8, color="white", weight="bold")
    for k, (name, top, dE) in enumerate(steps, start=1):
        ax.bar(k, dE, bottom=top - dE, color=RED if dE > 400 else ORANGE, width=0.7)
        ax.text(k, top + 90, f"−{dE:.0f}", ha="center", fontsize=7.2)
        ax.plot([k - 0.35 - 0.3, k + 0.35], [top, top], color=GREY, lw=0.6)
    kend = len(steps) + 1
    ax.plot([kend - 1.35, kend - 0.35], [E, E], color=GREY, lw=0.6)
    ax.bar(kend, E, color=GREEN, width=0.7)
    ax.text(kend, E + 120, f"{E:,.0f}", ha="center", fontsize=7.6, weight="bold")
    ax.axhline(15000, color=INK, ls="--", lw=1.0)
    ax.text(0.45, 15060, "R1: 15,000 kWh", fontsize=7.8, va="bottom")
    pr = E / (11.0 * 1734)
    ax.text(5.0, 12900, f"PR = {pr:.3f}\nspecific yield {E / 11.0:,.0f} kWh/kWp", fontsize=8.5,
            ha="center", bbox=dict(fc="white", ec=GREY, lw=0.6))
    ax.set_xticks(range(kend + 1))
    ax.set_xticklabels(labels, rotation=40, ha="right", fontsize=7.4, rotation_mode="anchor")
    ax.set_ylim(12000, 19800)
    ax.set_ylabel("Energy, first year (kWh; axis from 12,000)")

    save(fig, "22", "fig-22-5-loss-waterfall")
    return E, pr


# ----------------------------------------------------------------------------
# Figure 22.6 — commissioning I-V curves
# ----------------------------------------------------------------------------
def fig_22_6():
    G, Tc, dT = 0.82, 38.0, 13.0
    dv_irr = 0.46                                   # V per module, ln(0.82) term (Section 22.11)
    voc = 10 * (MOD["Voc"] * (1 + MOD["b_voc"] * dT) - dv_irr)
    isc = MOD["Isc"] * G * (1 + MOD["a_isc"] * dT)
    vmp = 10 * (MOD["Vmp"] * (1 + MOD["b_vmp"] * dT) - dv_irr)
    imp = MOD["Imp"] * G * (1 + MOD["a_isc"] * dT)
    exp_iv = ExplicitIV(voc, isc, vmp, imp)
    v = np.linspace(0, voc, 600)
    i_exp = exp_iv.i_of_v(v)
    rng = np.random.default_rng(22)
    s1 = 475.1 / voc
    s2 = 460.2 / voc                                # one of 30 substrings shorted: V scales ~29/30
    v_s1 = np.linspace(0, 475.1, 400)
    v_s2 = np.linspace(0, 460.2, 400)
    i_s1 = np.clip(exp_iv.i_of_v(v_s1 / s1) + rng.normal(0, 0.03, v_s1.size), 0, None)
    i_s2 = np.clip(exp_iv.i_of_v(v_s2 / s2) + rng.normal(0, 0.03, v_s2.size), 0, None)
    fig, ax = new_fig(6.6, 4.2)
    ax.plot(v, i_exp, color=INK, ls="--", lw=1.4, zorder=4,
            label=f"expected, 820 W/m², 38 °C ($V_{{OC}}$ {voc:.1f} V, $I_{{SC}}$ {isc:.1f} A)")
    ax.plot(v_s1, i_s1, color=BLUE, lw=1.5, label="S1 measured ($V_{OC}$ 475.1 V)")
    ax.plot(v_s2, i_s2, color=RED, lw=1.5, label="S2 measured ($V_{OC}$ 460.2 V)")
    p_e = v * i_exp
    k = np.argmax(p_e)
    ax.plot(v[k], i_exp[k], "o", color=INK, ms=4, zorder=5)
    ax.annotate(f"expected MPP\n{v[k]:.0f} V, {i_exp[k]:.1f} A", xy=(v[k], i_exp[k]),
                xytext=(300, 8.6), fontsize=7.4, ha="center",
                arrowprops=dict(arrowstyle="-", color=INK, lw=0.7))
    p2 = v_s2 * exp_iv.i_of_v(v_s2 / s2)
    k2 = np.argmax(p2)
    ax.plot(v_s2[k2], i_s2[k2], "o", color=RED, ms=4, zorder=5)
    ax.annotate(f"S2: one substring missing,\nshorted bypass diode in M14\n"
                f"(−{voc - 460.2:.1f} V at $V_{{OC}}$, MPP {v_s2[k2]:.0f} V)",
                xy=(440, 6.0), xytext=(255, 4.0), fontsize=7.6, color=RED,
                arrowprops=dict(arrowstyle="-", color=RED, lw=0.8))
    ax.set_xlim(0, 500)
    ax.set_ylim(0, 13)
    ax.set_xlabel("String voltage (V)")
    ax.set_ylabel("Current (A)")
    ax.legend(fontsize=7.4, loc="upper left", bbox_to_anchor=(0.0, 0.86))
    # inset: power curves
    ins = ax.inset_axes([0.08, 0.1, 0.34, 0.36])
    ins.plot(v, p_e / 1e3, color=INK, ls="--", lw=1.0, zorder=4)
    ins.plot(v_s1, v_s1 * i_s1 / 1e3, color=BLUE, lw=1.0)
    ins.plot(v_s2, v_s2 * i_s2 / 1e3, color=RED, lw=1.0)
    ins.set_xlim(300, 480)
    ins.set_ylim(2.5, 4.6)
    drop = 1 - p2.max() / p_e.max()
    ins.set_title(f"P-V: S2 MPP {drop * 100:.1f} % lower", fontsize=7.2, pad=2)
    ins.tick_params(labelsize=6.5)
    ins.set_xlabel("V", fontsize=6.8, labelpad=1)
    ins.set_ylabel("kW", fontsize=6.8, labelpad=1)
    save(fig, "22", "fig-22-6-commissioning-iv-curves")
    return v[k], i_exp[k], v_s2[k2], drop


if __name__ == "__main__":
    fig_22_1()
    print("annual AC (fig 22.2):", round(fig_22_2()))
    fig_22_3()
    print("22.4 global MPP V, P; unshaded P, V:", [round(float(x), 1) for x in fig_22_4()])
    print("22.5 E, PR:", fig_22_5())
    print("22.6 MPP V, I; S2 MPP V; drop:", [round(float(x), 3) for x in fig_22_6()])
