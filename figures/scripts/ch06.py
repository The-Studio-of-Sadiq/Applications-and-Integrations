"""Figures for Chapter 6 — Sensors and Transducers.

Run from the repository root:  python figures/scripts/ch06.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle  # noqa: E402

from figstyle import COLORS, INK, box, new_fig, save, schematic  # noqa: E402

BLUE, ORANGE, GREEN, PINK, YELLOW, SKY = COLORS[:6]
RED = "#C62828"
GREY = "#777777"


def line(ax, pts, color=INK, lw=1.1, ls="-", arrow_end=True, both=False):
    """Poly-line through pts with an arrow head on the last segment."""
    xs, ys = zip(*pts)
    if not arrow_end and not both:
        ax.plot(xs, ys, color=color, lw=lw, ls=ls, solid_capstyle="butt")
        return
    if len(pts) > 2:
        ax.plot(xs[:-1], ys[:-1], color=color, lw=lw, ls=ls)
    ax.annotate("", xy=pts[-1], xytext=pts[-2],
                arrowprops=dict(arrowstyle="<|-|>" if both else "-|>", color=color, lw=lw,
                                ls=ls, shrinkA=0, shrinkB=0, mutation_scale=9))


def lab(ax, x, y, s, ha="left", va="center", color=INK, fs=7.3, **kw):
    ax.text(x, y, s, ha=ha, va=va, fontsize=fs, color=color, **kw)


# ----------------------------------------------------------------------------
# Figure 6.1 — sensor architecture of the motor test bench
# ----------------------------------------------------------------------------
def fig_6_1():
    fig, ax = schematic(6.8, 5.0, xlim=(0, 17), ylim=(-0.15, 12.5))
    fs = 7.0
    sig_fs = 6.8

    # --- DAQ chassis and bench PC (top) ---
    ax.add_patch(FancyBboxPatch((0.2, 10.45), 12.85, 1.95, boxstyle="round,pad=0.02,rounding_size=0.15",
                                fc="#F4F6F8", ec=INK, lw=1.0))
    lab(ax, 0.4, 12.08, "DAQ system (Chapter 8)", fs=8, weight="bold")
    mods = [(0.35, 2.2, "RTD module\n24-bit"),
            (2.7, 2.2, "TC module\nwith CJC"),
            (5.05, 3.7, "Analog inputs\n0–10 V and 4–20 mA"),
            (8.9, 2.0, "Flange\ninterface"),
            (11.05, 1.85, "Counter /\nencoder")]
    for x, w, t in mods:
        box(ax, x, 10.6, w, 1.2, t, fc="#E3EDF7", fontsize=fs)
    box(ax, 13.6, 10.45, 3.2, 1.95, "Bench PC\ntiming card:\n10 MHz + PPS", fc="#FFF3D6", fontsize=7.2)
    line(ax, [(13.05, 11.4), (13.6, 11.4)], both=True)

    # --- Sensors around the DUT ---
    sens = [(0.35, 2.2, "6 × PT1000\nclass A\nin stator slots\n0.2 mA", "4-wire RTD", 1.45),
            (2.7, 2.2, "8 × type T TC\nbearings,\nhousing,\ncoolant in/out", "TC", 3.8),
            (5.0, 2.0, "IR thermopile\nvia end-cap\nwindow onto\nblack spot", "0–10 V", 6.0),
            (7.1, 1.9, "2 × pressure\n0–4 bar\ncoolant\nin / out", "4–20 mA", 8.05),
            (11.05, 1.85, "Optical tacho\nretro tape on\nDUT shaft", "TTL 1/rev", 11.5)]
    for x, w, t, sig, ax_x in sens:
        box(ax, x, 7.95, w, 1.5, t, fc="#E8F5EE", fontsize=6.2)
        line(ax, [(ax_x, 9.45), (ax_x, 10.6)])
        if sig.startswith("TTL"):
            lab(ax, ax_x - 0.1, 10.02, sig, ha="right", fs=sig_fs, color=BLUE)
        else:
            lab(ax, ax_x + 0.1, 10.02, sig, fs=sig_fs, color=BLUE)
    # mounting links to the DUT (dotted)
    for xs in (1.45, 3.8, 6.0, 8.05):
        xd = min(max(xs, 2.3), 5.1)
        ax.plot([xs, xd], [7.95, 7.0], color=GREEN, lw=0.9, ls=(0, (1, 1.5)))

    # --- Mechanical shaft line ---
    ax.plot([2.0, 15.0], [6.0, 6.0], color=INK, lw=2.4, zorder=0)
    box(ax, 2.0, 5.0, 3.4, 2.0, "DUT PMSM\n15 kW\n4 pole pairs", fc="#FBE3D6", fontsize=7.4)
    box(ax, 5.4, 5.35, 1.2, 1.3, "resolver\n(drive\nend)", fc="#FFF3D6", fontsize=6.0)
    for xc in (7.1, 12.55):
        ax.add_patch(Rectangle((xc, 5.6), 0.45, 0.8, fc="#DDDDDD", ec=INK, lw=0.9, hatch="////"))
        lab(ax, xc + 0.22, 5.5, "flexible\ncoupling", ha="center", va="top", fs=6.0)
    box(ax, 7.95, 4.95, 4.3, 2.1, "Torque flange 100 N·m\nclass 0.05, strain gauge\n"
        "digital out, 2 mV/V equiv.\n1024-pulse speed track", fc="#E3EDF7", fontsize=6.6)
    box(ax, 13.15, 5.0, 1.75, 2.0, "Load\nmachine\n30 kW\nregen.", fc="#F0F0F0", fontsize=6.6)
    box(ax, 14.9, 5.2, 1.6, 1.6, "4096-line\nencoder\n+ TMR\nangle", fc="#FFF3D6", fontsize=6.2)
    # flange and encoder to DAQ
    line(ax, [(9.9, 7.05), (9.9, 10.6)])
    lab(ax, 10.0, 7.5, "digital torque + speed track (RS-422)", fs=sig_fs, color=BLUE)
    line(ax, [(15.7, 6.8), (15.7, 9.95), (12.45, 9.95), (12.45, 10.6)])
    lab(ax, 14.1, 9.72, "RS-422 quadrature", ha="center", fs=sig_fs, color=BLUE)

    # --- Electrical power path (right to left) ---
    ey, eh = 1.85, 1.75
    box(ax, 11.8, ey, 2.0, eh, "DC supply\n800 V", fc="#F0F0F0", fontsize=7.2)
    box(ax, 8.55, ey, 2.75, eh, "DC link:\nfluxgate 100 A\n+ voltage input", fc="#E3EDF7", fontsize=6.6)
    box(ax, 5.3, ey, 2.75, eh, "DUT inverter\n(own closed-loop\nHall sensors\nfor control)", fc="#FBE3D6",
        fontsize=6.6)
    box(ax, 2.0, ey, 2.8, eh, "3 × fluxgate\n400 A, DS class\none per phase", fc="#E3EDF7", fontsize=6.6)
    pw = dict(color=ORANGE, lw=2.6)
    line(ax, [(11.8, 2.72), (11.3, 2.72)], **pw)
    line(ax, [(8.55, 2.72), (8.05, 2.72)], **pw)
    line(ax, [(5.3, 2.72), (4.8, 2.72)], **pw)
    line(ax, [(3.4, 3.6), (3.4, 5.0)], **pw)
    lab(ax, 3.55, 4.3, "3 phase cables", fs=sig_fs, color=ORANGE)
    # resolver sin/cos to inverter
    line(ax, [(6.0, 5.35), (6.0, 3.6)])
    lab(ax, 6.1, 4.6, "sin/cos", fs=sig_fs, color=BLUE)
    lab(ax, 7.4, 4.3, "orange: power  ·  blue: signal type  ·  green dotted: on DUT",
        fs=6.0, color=GREY)

    # --- Power analyser ---
    box(ax, 2.0, 0.0, 12.0, 1.1, "Power analyser — 6 channels, 0.03 % class", fc="#FFF3D6", fontsize=7.6)
    line(ax, [(3.4, 1.85), (3.4, 1.1)])
    lab(ax, 3.5, 1.47, "current output (×3)", fs=sig_fs, color=BLUE)
    line(ax, [(9.4, 1.85), (9.4, 1.1)])
    lab(ax, 9.3, 1.47, "current output", ha="right", fs=sig_fs, color=BLUE)
    line(ax, [(10.6, 1.85), (10.6, 1.1)])
    lab(ax, 10.7, 1.47, "voltage", fs=sig_fs, color=BLUE)
    line(ax, [(14.0, 0.55), (16.75, 0.55), (16.75, 10.45)], both=True, color=GREY)
    lab(ax, 16.5, 2.75, "Ethernet + 10 MHz + PPS", ha="center", va="center", fs=6.4, color=GREY, rotation=90)
    save(fig, "06", "fig-6-1-motor-bench-sensor-architecture")


# ----------------------------------------------------------------------------
# Figure 6.2 — RTD and thermocouple tolerance classes against R4
# ----------------------------------------------------------------------------
def fig_6_2():
    fig, ax = new_fig(6.4, 3.8)
    t = np.linspace(0, 180, 721)
    ta = t[t <= 150]
    ax.add_patch(Rectangle((0, 1.0), 150, 1.0, fc=RED, alpha=0.08, ec="none"))
    ax.text(8, 1.9, "fails R4", color=RED, fontsize=9, va="top")
    ax.plot(ta, 0.1 + 0.0017 * ta, color=GREEN)
    ax.plot(t, 0.15 + 0.002 * t, color=BLUE)
    ax.plot(t, 0.3 + 0.005 * t, color=SKY)
    ax.plot(t, np.maximum(0.5, 0.004 * t), color=ORANGE, ls="--")
    ax.plot(t, np.full_like(t, 1.5), color=PINK, ls="--")
    lf = dict(fontsize=8)
    ax.text(45, 0.165, "Pt class AA: 0.1 + 0.0017$t$ (to 150 °C)", color=GREEN, va="top", **lf)
    ax.text(10, 0.27, "Pt class A: 0.15 + 0.002$t$", color=BLUE, va="bottom", **lf)
    ax.text(100, 0.94, "Pt class B: 0.3 + 0.005$t$", color=SKY, va="top", ha="right", **lf)
    ax.text(62, 0.52, "type T class 1: max(0.5, 0.004$t$)", color=ORANGE, va="bottom", **lf)
    ax.text(40, 1.53, "type K class 1: 1.5", color=PINK, va="bottom", **lf)
    ax.plot([0, 150], [1.0, 1.0], color=INK, ls="--", lw=1.2)
    ax.text(3, 1.03, "R4 limit ±1.0 °C up to 150 °C", fontsize=8.5, va="bottom")
    ax.axvline(150, color=INK, ls=":", lw=1.0)
    for y, c in ((0.355, GREEN), (0.45, BLUE), (1.05, SKY), (0.6, ORANGE)):
        ax.plot(150, y, "o", color=c, ms=4)
    ax.annotate("0.36", (150, 0.355), (138, 0.25), fontsize=7.5, color=GREEN, ha="center")
    ax.annotate("0.45", (150, 0.45), (157, 0.36), fontsize=7.5, color=BLUE)
    ax.annotate("0.60", (150, 0.6), (157, 0.66), fontsize=7.5, color=ORANGE)
    ax.annotate("1.05", (150, 1.05), (157, 0.96), fontsize=7.5, color=SKY)
    ax.set_xlim(0, 180)
    ax.set_ylim(0, 2.0)
    ax.set_xlabel("Temperature $t$ (°C)")
    ax.set_ylabel("Tolerance (± °C)")
    ax.grid(True, lw=0.5)
    save(fig, "06", "fig-6-2-temperature-tolerance-classes")


# ----------------------------------------------------------------------------
# Figure 6.3 — M, T and M/T speed resolution
# ----------------------------------------------------------------------------
def fig_6_3():
    N, Tw, fc = 16384, 1e-3, 170e6
    fig, ax = new_fig(6.4, 3.8)
    n = np.logspace(0, np.log10(12000), 400)
    dM = 60 / (N * Tw)
    dT = n ** 2 * N / (60 * fc)
    dMT = n / (fc * Tw)
    ax.plot(n, np.full_like(n, dM), color=ORANGE, label=f"M-method  {dM:.2f} rpm")
    ax.plot(n, dT, color=BLUE, label=r"T-method  $n^2N/(60f_c)$")
    lo = n <= 10
    ax.plot(n[~lo], dMT[~lo], color=GREEN, label=r"M/T method  $n/(f_cT_w)$")
    ax.plot(n[lo], dMT[lo], color=GREEN, ls="--")
    ax.annotate("dashed: window\nextended below 10 rpm", (4, 4 / 170000), (1.25, 4e-4), fontsize=7.5,
                color=GREEN, arrowprops=dict(arrowstyle="-", color=GREEN, lw=0.8))
    ax.axhline(1.0, color=INK, ls="--", lw=1.1)
    ax.text(1.2, 1.15, "R2: 1 rpm", fontsize=8.5, va="bottom")
    n789 = np.sqrt(60 * fc / N)
    ax.plot(n789, 1.0, "o", color=BLUE, ms=5)
    ax.annotate(f"T-method crosses R2\nat {n789:.0f} rpm", (n789, 1.0), (60, 30), fontsize=8,
                color=BLUE, arrowprops=dict(arrowstyle="-", color=BLUE, lw=0.8))
    ax.plot(12000, dT[-1], "o", color=BLUE, ms=4)
    ax.annotate(f"{dT[-1]:.0f} rpm", (12000, dT[-1]), (2500, 300), fontsize=8, color=BLUE)
    ax.plot(12000, dMT[-1], "o", color=GREEN, ms=4)
    ax.annotate(f"{dMT[-1]:.2f} rpm", (12000, dMT[-1]), (2500, 0.15), fontsize=8, color=GREEN)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(1, 12000)
    ax.set_ylim(1e-5, 1e3)
    ax.set_xlabel("Speed $n$ (rpm)")
    ax.set_ylabel("Resolution (rpm)")
    ax.legend(loc="upper left", fontsize=8)
    ax.grid(True, which="major", lw=0.5)
    ax.text(0.99, 0.02, "$N$ = 16,384 counts/rev, $T_w$ = 1 ms, $f_c$ = 170 MHz",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=7.8, color=GREY)
    save(fig, "06", "fig-6-3-speed-resolution-methods")


# ----------------------------------------------------------------------------
# Figure 6.4 — efficiency uncertainty versus torque
# ----------------------------------------------------------------------------
def U_eta(T, n_rpm=3000, eta=0.94, T_fs=100.0, cls=0.05e-2, zero=0.01e-2, p_rel=0.04e-2, n_abs=0.1):
    """Expanded (k = 2) uncertainty of efficiency, in percentage points (Section 6.6)."""
    u_T = np.hypot(cls * T_fs, zero * T_fs) / np.sqrt(3)
    u_n = n_abs / np.sqrt(3)
    rel = np.sqrt((u_T / T) ** 2 + (u_n / n_rpm) ** 2 + p_rel ** 2)
    return 2 * 100 * eta * rel


def fig_6_4():
    fig, ax = new_fig(6.4, 3.8)
    T = np.linspace(1, 60, 5901)
    ax.axvspan(0, 20, color="#999999", alpha=0.15, lw=0)
    ax.text(13.5, 2.0, "outside R9 scope\n(T < 20 N·m)", ha="center", va="top", fontsize=8, color=GREY)
    for fs_, c in ((100, BLUE), (200, ORANGE)):
        u = U_eta(T, T_fs=fs_)
        ax.plot(T, u, color=c, label=f"{fs_} N·m flange, class 0.05")
        Tx = T[u <= 0.30].min()
        ax.plot([Tx, Tx], [0, 0.30], color=c, lw=1.0)
        ax.plot(Tx, 0.30, "o", color=c, ms=4.5)
        dx, ha = (-0.5, "right") if fs_ == 100 else (0.5, "left")
        ax.text(Tx + dx, 0.06, f"{Tx:.1f} N·m", color=c, fontsize=8, va="bottom", ha=ha)
        for Tp in (5, 10, 20, 35.8, 60):
            ax.plot(Tp, U_eta(Tp, T_fs=fs_), ".", color=c, ms=5)
    ax.axhline(0.30, color=INK, ls="--", lw=1.1)
    ax.text(59.5, 0.33, "R9: 0.30 pp", ha="right", fontsize=8.5)
    ax.axvline(35.8, color=INK, ls=":", lw=1.0)
    ax.text(36.3, 1.75, "rated torque\n35.8 N·m", fontsize=8)
    ax.set_xlim(0, 60)
    ax.set_ylim(0, 2.5)
    ax.set_xlabel("Shaft torque $T$ (N·m)")
    ax.set_ylabel(r"$U(\eta)$, $k$ = 2 (percentage points)")
    ax.legend(loc="upper right", bbox_to_anchor=(1.0, 0.98), fontsize=8.5)
    ax.text(0.99, 0.30, "3,000 rpm, η = 0.94\npower 0.04 %, speed 0.1 rpm",
            transform=ax.transAxes, ha="right", fontsize=7.8, color=GREY)
    save(fig, "06", "fig-6-4-efficiency-uncertainty-vs-torque")


# ----------------------------------------------------------------------------
# Figure 6.5 — torque-flange calibration deviations
# ----------------------------------------------------------------------------
def fig_6_5():
    G_LOCAL, ARM, T_FS = 9.78871, 1.0, 100.0
    mass = np.array([0, 2, 4, 6, 8, 10.0])
    torque = mass * G_LOCAL * ARM
    up = np.array([0.0, 0.39369, 0.78759, 1.18168, 1.57597, 1.97047])
    down = np.array([0.00012, 0.39419, 0.78819, 1.18228, 1.57637, 1.97047])
    mean = (up + down) / 2
    k, z = np.polyfit(torque, mean, 1)
    span = k * T_FS
    d_up = (up - (k * torque + z)) / span * 100
    d_dn = (down - (k * torque + z)) / span * 100
    lin = np.max(np.abs(mean - (k * torque + z))) / span * 100
    hys = np.max(np.abs(down - up)) / span * 100

    fig, ax = new_fig(6.4, 3.8)
    ax.axhspan(-0.05, 0.05, color=GREEN, alpha=0.07, lw=0)
    for y in (0.05, -0.05):
        ax.axhline(y, color=GREEN, ls="--", lw=1.1)
    ax.text(99, 0.052, "class 0.05", color=GREEN, ha="right", va="bottom", fontsize=8.5)
    ax.text(99, -0.052, "class 0.05", color=GREEN, ha="right", va="top", fontsize=8.5)
    ax.axhline(0, color=INK, lw=0.9)
    ax.text(23, 0.0012, "best-fit line of mean", ha="center", va="bottom", fontsize=7.5, color=GREY)
    ax.plot(torque, d_up, "-o", color=BLUE, ms=6, lw=1.2, label="increasing")
    ax.plot(torque, d_dn, "--o", color=ORANGE, ms=6, lw=1.2, mfc="white", mew=1.4, label="decreasing")
    i = int(np.argmax(np.abs(down - up)))
    for j in (i, i + 1):
        if abs(abs(d_dn[j] - d_up[j]) - hys) < 0.002:
            ax.annotate("", (torque[j], d_dn[j]), (torque[j], d_up[j]),
                        arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.9, mutation_scale=8))
    ax.text(45, -0.029, "max up–down difference\n0.030 % FS (39–59 N·m)",
            ha="center", va="top", fontsize=7.8)
    ax.text(99, -0.047, f"linearity {lin:.3f} % FS\nhysteresis {hys:.3f} % FS\n"
            f"zero return {1e3 * (down[0] - up[0]):.2f} µV/V\nsensitivity {k * 1e3:.3f} µV/V per N·m",
            fontsize=7.8, va="bottom", ha="right",
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=GREY, lw=0.7))
    ax.set_xlim(-2, 102)
    ax.set_ylim(-0.06, 0.06)
    ax.set_xticks(np.round(torque, 2))
    ax.set_xticklabels([f"{t:.2f}" if t else "0" for t in torque])
    ax.set_xlabel("Applied torque (N·m)")
    ax.set_ylabel("Deviation from best-fit line (% FS)")
    ax.legend(loc="upper left", fontsize=8.5, ncol=2)
    save(fig, "06", "fig-6-5-torque-calibration-deviation")


if __name__ == "__main__":
    fig_6_1()
    fig_6_2()
    fig_6_3()
    fig_6_4()
    fig_6_5()
