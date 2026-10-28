"""Figures for Chapter 33 — Engineering Simulation and Digital Twins.

Run from the repository root:  python figures/scripts/ch33.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle  # noqa: E402
from scipy.integrate import solve_ivp  # noqa: E402
from scipy.optimize import least_squares  # noqa: E402

from figstyle import COLORS, INK, box, save, schematic  # noqa: E402

BLUE, ORANGE, GREEN, PINK, YELLOW, SKY = COLORS[:6]
RED = "#C62828"
GREY = "#777777"

# ----------------------------------------------------------------------------
# Physics model of the pump set (pumpset.py of Section 33.2)
# ----------------------------------------------------------------------------
NR, TR = 1480.0, 238.7
H0, HS, KP, KS = 48.0, 20.0, 1793.0, 2391.0
QR, ETA_BEP, AH = 0.0818, 0.78, 1.387e-3
P_CU_R, P_FE_R, P_RT_R = 1000.0, 600.0, 636.0
PAR = dict(R1=0.035, C1=12e3, R2=0.0201, C2=120e3, tau_n=0.3)


def shaft_power(n, q):
    s = n / NR
    h = H0 * s**2 - KP * q**2
    qb = q / (QR * np.maximum(s, 1e-3))
    eta = np.maximum(ETA_BEP * (1.0 - (qb - 1.0)**2), 0.30)
    return h, 1000 * 9.81 * q * h / eta


def losses(n, p_shaft, tw):
    n = np.maximum(n, 1.0)
    t = p_shaft / (n * 2 * np.pi / 60)
    kt = (234.5 + tw) / (234.5 + 115.0)
    p_w = P_CU_R * (0.1 + 0.9 * (t / TR)**2) * kt
    p_f = P_FE_R * (n / NR)**1.6 + P_RT_R * (t / TR)**2
    return p_w, p_f


def rhs(t, x, n_ref, t_amb, p=PAR, foul=1.0):
    n, q, tw, tf = x
    h, ps = shaft_power(n, max(q, 0.0))
    dq = AH * (h - (HS + KS * q * abs(q)))
    pw, pf = losses(n, ps, tw)
    r2 = foul * p["R2"] / (0.25 + 0.75 * n / NR)
    dtw = (pw - (tw - tf) / p["R1"]) / p["C1"]
    dtf = (pf + (tw - tf) / p["R1"] - (tf - t_amb(t)) / r2) / p["C2"]
    return [(n_ref(t) - n) / p["tau_n"], dq, dtw, dtf]


def line(ax, pts, color=INK, lw=1.1, ls="-", arrow_end=False):
    xs, ys = zip(*pts)
    if not arrow_end:
        ax.plot(xs, ys, color=color, lw=lw, ls=ls, solid_capstyle="butt")
        return
    if len(pts) > 2:
        ax.plot(xs[:-1], ys[:-1], color=color, lw=lw, ls=ls)
    ax.annotate("", xy=pts[-1], xytext=pts[-2],
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, ls=ls,
                                shrinkA=0, shrinkB=0, mutation_scale=10))


# ----------------------------------------------------------------------------
# Figure 33.1 — pump-set model
# ----------------------------------------------------------------------------
def resistor_h(ax, x0, x1, y, n=6, amp=0.13):
    """Zig-zag resistor between x0 and x1 at height y (leads 20 % each side)."""
    L = x1 - x0
    a, b = x0 + 0.2 * L, x1 - 0.2 * L
    xs = [x0, a] + [a + (b - a) * (k + 0.5) / n for k in range(n)] + [b, x1]
    ys = [y, y] + [y + amp * (1 if k % 2 == 0 else -1) for k in range(n)] + [y, y]
    ax.plot(xs, ys, color=INK, lw=1.2)


def resistor_v(ax, x, y0, y1, n=6, amp=0.13):
    L = y1 - y0
    a, b = y0 + 0.2 * L, y1 - 0.2 * L
    ys = [y0, a] + [a + (b - a) * (k + 0.5) / n for k in range(n)] + [b, y1]
    xs = [x, x] + [x + amp * (1 if k % 2 == 0 else -1) for k in range(n)] + [x, x]
    ax.plot(xs, ys, color=INK, lw=1.2)


def cap_v(ax, x, ytop, ygnd):
    """Capacitor from a node at ytop down to a ground at ygnd."""
    ym = (ytop + ygnd) / 2
    ax.plot([x, x], [ytop, ym + 0.08], color=INK, lw=1.2)
    ax.plot([x - 0.25, x + 0.25], [ym + 0.08] * 2, color=INK, lw=1.6)
    ax.plot([x - 0.25, x + 0.25], [ym - 0.08] * 2, color=INK, lw=1.6)
    ax.plot([x, x], [ym - 0.08, ygnd], color=INK, lw=1.2)


def gnd(ax, x, y):
    for k, w in enumerate((0.28, 0.18, 0.08)):
        ax.plot([x - w, x + w], [y - 0.07 * k] * 2, color=INK, lw=1.1)


def isource_v(ax, x, ytop, ygnd):
    """Current source pointing up, from ground to node."""
    ym = (ytop + ygnd) / 2
    ax.add_patch(Circle((x, ym), 0.3, fc="white", ec=INK, lw=1.2))
    ax.annotate("", xy=(x, ym + 0.2), xytext=(x, ym - 0.2),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.1, mutation_scale=9))
    ax.plot([x, x], [ym + 0.3, ytop], color=INK, lw=1.2)
    ax.plot([x, x], [ym - 0.3, ygnd], color=INK, lw=1.2)


def fig_33_1():
    fig, ax = schematic(6.8, 5.0, xlim=(0, 16), ylim=(0.6, 11.4))
    # top row energy chain
    yb, hb = 8.7, 2.2
    blocks = [(0.05, 2.9, "VFD speed\nloop\n" + r"$\tau_n$ = 0.3 s", tint(BLUE)),
              (4.3, 3.0, "Motor\n37 kW\n1480 rpm", tint(ORANGE)),
              (8.65, 2.9, "Pump\n$H_0$ = 48 m", tint(GREEN)),
              (12.95, 3.0, "Rising main\n500 m DN300\nstatic head\n20 m", tint(SKY))]
    for x, w, t, fc in blocks:
        box(ax, x, yb, w, hb, t, fc=fc, fontsize=8.4)
    for (x0, w0, *_), (x1, *_), lab in zip(blocks[:-1], blocks[1:], ["$n$", "$T$", "$Q$"]):
        line(ax, [(x0 + w0, yb + hb / 2), (x1, yb + hb / 2)], arrow_end=True, lw=1.3)
        ax.text((x0 + w0 + x1) / 2, yb + hb / 2 + 0.12, lab, ha="center", va="bottom", fontsize=10)
    ax.text(14.45, yb - 0.2, r"$H = 20 + 2391\,Q^2$", ha="center", va="top", fontsize=8.2)
    ax.text(10.1, yb - 0.2, r"$H = 48\,(n/n_r)^2 - 1793\,Q^2$", ha="center", va="top", fontsize=8.2)
    # thermal network under the motor
    ax.text(0.2, 7.0, "Two-node motor thermal network (calibrated)", fontsize=9,
            weight="bold", ha="left", va="center")
    yt, yg = 5.3, 2.3          # node rail and ground
    xw, xf, xa = 4.6, 8.4, 12.8
    isource_v(ax, 1.3, yt, yg)
    gnd(ax, 1.3, yg)
    ax.text(0.85, (yt + yg) / 2, "$P_w$\n1000 W\nrated", ha="right", va="center", fontsize=8.2)
    ax.plot([1.3, xw], [yt, yt], color=INK, lw=1.2)
    cap_v(ax, 2.6, yt, yg)
    gnd(ax, 2.6, yg)
    ax.text(2.95, (yt + yg) / 2, "$C_1$\n11.2 kJ/K", ha="left", va="center", fontsize=8.2)
    resistor_h(ax, xw, xf, yt)
    ax.text((xw + xf) / 2, yt + 0.3, "$R_1$ = 0.037 K/W", ha="center", va="bottom", fontsize=8.4)
    for x in (xw, xf, xa):
        ax.add_patch(Circle((x, yt), 0.1, fc=INK, ec=INK, zorder=4))
    ax.text(xw + 0.1, yt - 0.25, "$T_w$", ha="left", va="top", fontsize=10)
    ax.text(xf - 0.1, yt - 0.25, "$T_f$", ha="right", va="top", fontsize=10)
    ax.text(xa - 0.1, yt - 0.25, "$T_a$", ha="right", va="top", fontsize=10)
    ax.plot([xf, 10.2], [yt, yt], color=INK, lw=1.2)
    cap_v(ax, 9.0, yt, yg)
    gnd(ax, 9.0, yg)
    ax.text(8.6, (yt + yg) / 2 - 0.25, "$C_2$\n131 kJ/K", ha="right", va="center", fontsize=8.2)
    isource_v(ax, 10.2, yt, yg)
    gnd(ax, 10.2, yg)
    ax.text(10.6, (yt + yg) / 2, "$P_f$\n1236 W", ha="left", va="center", fontsize=8.2)
    resistor_h(ax, 10.2, xa, yt)
    ax.text(11.5, yt + 0.3, r"$f\,R_2(n)$", ha="center", va="bottom", fontsize=9.5)
    ax.plot([xa, xa], [yt, yt - 1.15], color=INK, lw=1.2)
    ax.add_patch(Circle((xa, yt - 1.5), 0.35, fc="white", ec=INK, lw=1.2))
    ax.text(xa, yt - 1.5, "+\n−", ha="center", va="center", fontsize=7.5, linespacing=0.8)
    ax.plot([xa, xa], [yt - 1.85, yg], color=INK, lw=1.2)
    gnd(ax, xa, yg)
    ax.text(xa + 0.5, yt - 1.5, "ambient\n33–40 °C", ha="left", va="center", fontsize=8.2)
    ax.text(11.0, 1.15, r"$R_2(n) = \dfrac{0.021}{0.25 + 0.75\,n/n_r}$ K/W",
            ha="center", va="center", fontsize=9)
    ax.text(4.0, 1.15, "hot spot = $T_w$ + 10 K (class F)", ha="center", va="center", fontsize=8.4)
    # dashed couplings
    line(ax, [(6.8, yb), (6.8, 7.75), (11.5, 7.75), (11.5, yt + 0.95)], color=BLUE, lw=1.1,
         ls=(0, (4, 2)), arrow_end=True)
    ax.text(9.15, 7.62, "shaft fan ($n$)", color=BLUE, fontsize=8.4, ha="center", va="top",
            style="italic")
    ax.annotate("", xy=(1.45, yt + 0.12), xytext=(xw - 0.1, yt + 0.15),
                arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.1, ls=(0, (4, 2)),
                                connectionstyle="arc3,rad=0.45", mutation_scale=10))
    ax.text(2.95, 6.35, "copper $R(T)$", color=RED, fontsize=8.4, ha="center", va="bottom",
            style="italic")
    save(fig, "33", "fig-33-1-pump-set-model")


def tint(c, a="30"):
    return c + a


# ----------------------------------------------------------------------------
# Figure 33.2 — eight-hour simulation
# ----------------------------------------------------------------------------
STEPS = [(0, 1180), (3600, 1480), (10800, 1110), (14400, 1410), (21600, 1520)]


def n_ref(t):
    return [n for (ts, n) in STEPS if t >= ts][-1]


def t_amb(t):
    return 34.0 + 4.0 * np.sin(2 * np.pi * (t - 3600) / 86400)


def fig_33_2():
    x0 = [1180.0, 0.05, 70.0, 60.0]
    sols = {}
    for m in ("RK45", "BDF"):
        sols[m] = solve_ivp(rhs, (0, 8 * 3600), x0, method=m, args=(n_ref, t_amb),
                            rtol=1e-6, atol=[1e-3, 1e-7, 1e-4, 1e-4], dense_output=True)
        print(f"  {m}: steps {sols[m].t.size}")
    sol = sols["BDF"]
    th = np.arange(0, 8 * 3600 + 1, 10.0)
    y = sol.sol(th)
    hr = th / 3600
    for tc in (3, 4, 6, 8):
        k = np.argmin(abs(th - tc * 3600))
        print(f"  t={tc} h: Tw={y[2, k]:.1f} Tf={y[3, k]:.1f}")

    fig, axs = plt.subplots(3, 1, figsize=(6.8, 6.4), sharex=True,
                            gridspec_kw=dict(height_ratios=[1, 1.4, 1.2], hspace=0.12))
    ax = axs[0]
    ax.plot(hr, y[0], color=BLUE, label="speed")
    ax.set_ylabel("Speed (rpm)")
    ax.set_ylim(1000, 1600)
    for (ts, n), lab_dy in zip(STEPS, (-60, 25, -60, 25, 25)):
        ax.text(ts / 3600 + 0.08, n + lab_dy, f"{n}", fontsize=8, color=BLUE,
                va="bottom" if lab_dy > 0 else "top")
    a2 = ax.twinx()
    a2.spines["right"].set_visible(True)
    a2.plot(hr, t_amb(th), color=ORANGE, ls="--", lw=1.4)
    a2.set_ylabel("Ambient (°C)", color=ORANGE)
    a2.tick_params(axis="y", colors=ORANGE)
    a2.set_ylim(30, 40)
    a2.text(7.9, 37.0, "ambient", color=ORANGE, fontsize=8, ha="right", va="top")

    ax = axs[1]
    ax.plot(hr, y[2], color=RED, label="winding $T_w$")
    ax.plot(hr, y[3], color=GREEN, label="frame $T_f$")
    ax.axhline(145, color=INK, ls=":", lw=1.2)
    ax.text(0.1, 143, "145 °C class F average-winding limit", fontsize=8, va="top")
    for tc in (3, 4, 6, 8):
        k = np.argmin(abs(th - tc * 3600))
        ax.plot(hr[k], y[2, k], "o", color=RED, ms=3.5)
        ax.annotate(f"{y[2, k]:.1f}" if tc in (3, 8) else f"{y[2, k]:.0f}", (hr[k], y[2, k]),
                    xytext=(-4, 6), textcoords="offset points", ha="right", fontsize=7.8, color=RED)
        ax.plot(hr[k], y[3, k], "o", color=GREEN, ms=3.5)
        ax.annotate(f"{y[3, k]:.0f}", (hr[k], y[3, k]), xytext=(-4, 5),
                    textcoords="offset points", ha="right", fontsize=7.8, color=GREEN)
    ax.set_ylabel("Temperature (°C)")
    ax.set_ylim(50, 155)
    ax.legend(loc="center left", bbox_to_anchor=(0.0, 0.62), fontsize=8)

    ax = axs[2]
    for m, c in (("RK45", ORANGE), ("BDF", BLUE)):
        t = sols[m].t
        h = np.diff(t)
        ax.step(t[1:] / 3600, h, where="pre", color=c, lw=1.1,
                label=f"{m} ({t.size} steps)")
    ax.set_yscale("log")
    ax.set_ylim(0.01, 2000)
    ax.set_ylabel("Step size (s)")
    ax.set_xlabel("Time (h)")
    ax.set_xlim(0, 8)
    ax.legend(loc="lower left", bbox_to_anchor=(0.14, 0.0), fontsize=8)
    for ts, _ in STEPS[1:]:
        for a in axs:
            a.axvline(ts / 3600, color="#BBBBBB", lw=0.7, zorder=0)
    save(fig, "33", "fig-33-2-eight-hour-simulation")


# ----------------------------------------------------------------------------
# Figure 33.3 — heat-run calibration
# ----------------------------------------------------------------------------
def fig_33_3():
    DT = 10.0
    t = np.arange(0, 5 * 3600, DT)
    n = np.where(t < 3 * 3600, 1480.0, 1180.0)
    ps = np.where(t < 3 * 3600, 37.04e3, 17.32e3)
    ta = 25.0 + 0.0 * t

    def thermal(theta):
        r1, c1, r2, c2 = theta
        tw, tf, out = ta[0], ta[0], np.empty((t.size, 2))
        for k in range(t.size):
            pw, pf = losses(n[k], ps[k], tw)
            r2n = r2 / (0.25 + 0.75 * n[k] / NR)
            q12 = (tw - tf) / r1
            tw += DT * (pw - q12) / c1
            tf += DT * (pf + q12 - (tf - ta[k]) / r2n) / c2
            out[k] = tw, tf
        return out

    rng = np.random.default_rng(7)
    true = np.array([0.0372, 11.1e3, 0.0214, 131e3])
    meas = thermal(true)[::6] + rng.normal(0, 0.3, (t.size // 6, 2))
    res = lambda lg: (thermal(np.exp(lg))[::6] - meas).ravel()  # noqa: E731
    fit = least_squares(res, np.log([0.035, 12e3, 0.0201, 120e3]), x_scale=1.0)
    cal = thermal(np.exp(fit.x))
    des = thermal([0.035, 12e3, 0.0201, 120e3])
    r = fit.fun.reshape(-1, 2)
    rms = np.sqrt(np.mean(fit.fun**2))
    tm = t[::6] / 3600
    print("  calibrated:", np.exp(fit.x), "rms", rms)
    k3 = np.argmin(abs(t - 3 * 3600 + DT))
    print("  at 3 h design-cal Tw: %.2f  Tf: %.2f" % (des[k3, 0] - cal[k3, 0], des[k3, 1] - cal[k3, 1]))
    for hh in (1, 2, 3, 3.5, 5):
        k = min(int(hh * 3600 / DT) - 1, t.size - 1)
        print(f"  {hh} h: Tw {cal[k, 0]:.1f}  Tf {cal[k, 1]:.1f}")

    fig, axs = plt.subplots(2, 1, figsize=(6.6, 5.0), sharex=True,
                            gridspec_kw=dict(height_ratios=[2.6, 1], hspace=0.1))
    ax = axs[0]
    th = t / 3600
    sel = slice(0, None, 3)   # plot every 3rd logged point (3 min) for legibility
    ax.plot(tm[sel], meas[sel, 0], "o", ms=2.6, color=RED, alpha=0.75, label="measured winding (mean of 3 PT100)")
    ax.plot(tm[sel], meas[sel, 1], "s", ms=2.4, color=GREEN, alpha=0.75, label="measured frame PT100")
    ax.plot(th, cal[:, 0], color=RED, lw=1.4, label="calibrated model")
    ax.plot(th, cal[:, 1], color=GREEN, lw=1.4)
    ax.plot(th, des[:, 0], color=RED, lw=1.2, ls="--", label="design-value model")
    ax.plot(th, des[:, 1], color=GREEN, lw=1.2, ls="--")
    ax.axvline(3, color=GREY, lw=0.9)
    ax.text(3.05, 30, "1480 → 1180 rpm", fontsize=8.2, color=GREY, ha="left")
    ax.text(4.95, cal[-1, 0] + 6, "winding", color=RED, fontsize=8.4, ha="right")
    ax.text(4.95, cal[-1, 1] - 3, "frame", color=GREEN, fontsize=8.4, ha="right", va="top")
    ax.set_ylim(20, 115)
    ax.set_ylabel("Temperature (°C)")
    leg = ax.legend(loc="upper left", fontsize=7.8, ncol=2)
    for h in leg.legend_handles[2:]:
        h.set_color(INK)
    ax = axs[1]
    ax.plot(tm, r[:, 0], ".", ms=2.5, color=RED, label="winding")
    ax.plot(tm, r[:, 1], ".", ms=2.5, color=GREEN, label="frame")
    ax.axhline(0, color=INK, lw=0.8)
    ax.axvline(3, color=GREY, lw=0.9)
    ax.set_ylim(-1.4, 1.5)
    ax.set_ylabel("Residual (K)")
    ax.set_xlabel("Time (h)")
    ax.set_xlim(0, 5)
    ax.text(0.1, 1.25, f"calibrated model − measured, RMS {rms:.2f} K", fontsize=8.2, va="center")
    ax.legend(loc="lower right", fontsize=7.8, ncol=2)
    save(fig, "33", "fig-33-3-heat-run-calibration")


# ----------------------------------------------------------------------------
# Figure 33.4 — twin architecture
# ----------------------------------------------------------------------------
def fig_33_4():
    fig, ax = schematic(6.8, 5.0, xlim=(0, 18), ylim=(0, 12.6))

    def layer(y0, y1, name, fc):
        ax.add_patch(FancyBboxPatch((0.1, y0), 16.5, y1 - y0,
                                    boxstyle="round,pad=0.02,rounding_size=0.15",
                                    fc=fc, ec="#999999", lw=0.8))
        ax.text(0.65, (y0 + y1) / 2, name, ha="center", va="center", fontsize=8.4,
                weight="bold", rotation=90, linespacing=1.1)

    up = dict(color=BLUE, lw=1.3, arrow_end=True)
    # Plant
    layer(0.1, 3.05, "Plant\n×12", tint(GREY, "18"))
    box(ax, 1.4, 0.3, 1.8, 1.5, "VFD", fc="white", fontsize=8)
    box(ax, 3.5, 0.3, 4.9, 1.5, "Motor 37 kW\nframe PT100\n(lead unit: +3 winding)",
        fc="white", fontsize=7.4)
    box(ax, 8.7, 0.3, 3.6, 1.5, "Pump, flowmeter,\npressure\ntransmitter", fc="white", fontsize=7.4)
    box(ax, 12.6, 0.3, 3.7, 1.5, "Aspirated inlet\nambient PT100", fc="white", fontsize=7.4)
    box(ax, 3.5, 2.15, 12.8, 0.65, "PLC (sensor I/O)", fc=tint(GREY, "30"), fontsize=7.8)
    for x in (5.95, 10.5, 14.45):
        line(ax, [(x, 1.8), (x, 2.15)], **up)
    # Edge gateway
    layer(3.3, 5.3, "Edge\ngateway", tint(BLUE, "18"))
    box(ax, 1.4, 3.5, 3.3, 1.25, "Modbus TCP\nclient, 1 s", fc="white", fontsize=7.8)
    box(ax, 5.1, 3.5, 3.1, 1.25, "OPC UA\nclient", fc="white", fontsize=7.8)
    box(ax, 8.6, 3.5, 3.6, 1.25, "timestamp +\n7-day buffer", fc="white", fontsize=7.8)
    box(ax, 12.6, 3.5, 3.7, 1.25, "MQTT TLS\npublisher", fc="white", fontsize=7.8)
    line(ax, [(2.3, 1.8), (2.3, 3.5)], **up)
    line(ax, [(6.6, 2.8), (6.6, 3.5)], **up)
    line(ax, [(3.05, 4.75), (3.05, 5.05), (10.4, 5.05), (10.4, 4.75)], arrow_end=True)
    line(ax, [(8.2, 4.12), (8.6, 4.12)], arrow_end=True)
    line(ax, [(12.2, 4.12), (12.6, 4.12)], arrow_end=True)
    # Firewall
    ax.add_patch(Rectangle((0.1, 5.5), 16.5, 0.55, fc="#F2D7CF", ec=RED, lw=1.0, hatch="////"))
    ax.text(6.8, 5.775, "Firewall: IEC 62443 one-way conduit", ha="center",
            va="center", fontsize=7.8, color=INK, weight="bold",
            bbox=dict(fc="#FBEAE5", ec="none", pad=1.0))
    # Twin core
    layer(6.3, 9.85, "Twin\ncore", tint(GREEN, "18"))
    box(ax, 1.4, 6.8, 2.9, 1.35, "Ingestion,\nalignment,\nwatermark 2 s", fc="white", fontsize=7.6)
    box(ax, 4.6, 6.8, 2.4, 1.35, "EKF\nper unit", fc="white", fontsize=7.8)
    box(ax, 7.3, 6.8, 3.4, 1.35, "Model service\nL0 maps, L1\n(versioned FMU)", fc="white",
        fontsize=7.6)
    box(ax, 4.6, 8.45, 2.4, 1.15, "UQ service", fc="white", fontsize=7.8)
    box(ax, 7.3, 8.45, 3.4, 1.15, "Scenario runner", fc="white", fontsize=7.8)
    box(ax, 11.2, 6.8, 5.1, 2.8, "Historian\n+ model registry\n(parameter sets,\ndata hashes, R7)",
        fc=tint(YELLOW, "40"), fontsize=7.8)
    line(ax, [(4.3, 7.47), (4.6, 7.47)], arrow_end=True)
    line(ax, [(7.0, 7.47), (7.3, 7.47)], arrow_end=True)
    line(ax, [(5.8, 8.15), (5.8, 8.45)], arrow_end=True)
    line(ax, [(9.0, 8.15), (9.0, 8.45)], arrow_end=True)
    line(ax, [(10.7, 7.47), (11.2, 7.47)], arrow_end=True)
    line(ax, [(10.7, 9.02), (11.2, 9.02)], arrow_end=True)
    line(ax, [(14.4, 4.75), (14.4, 6.55), (2.85, 6.55), (2.85, 6.8)], **up)
    ax.text(14.6, 5.775, "MQTT/TLS", fontsize=7.4, color=BLUE, ha="left", va="center",
            bbox=dict(fc="#FBEAE5", ec="none", pad=0.6))
    # Applications
    layer(10.1, 12.45, "Apps\n(people)", tint(ORANGE, "20"))
    box(ax, 1.4, 10.4, 4.6, 1.6, "Operator\ndashboard", fc="white", fontsize=8.2)
    box(ax, 6.5, 10.4, 4.6, 1.6, "Maintenance\nwork orders", fc="white", fontsize=8.2)
    box(ax, 11.6, 10.4, 4.7, 1.6, "Engineering\nwhat-if studies", fc="white", fontsize=8.2)
    line(ax, [(5.4, 9.6), (5.4, 10.4)], **up)
    line(ax, [(2.85, 8.15), (2.85, 10.4)], **up)
    line(ax, [(9.0, 9.6), (9.0, 10.4)], **up)
    line(ax, [(13.75, 9.6), (13.75, 10.4)], **up)
    # no writes to plant
    ax.annotate("", xy=(17.15, 1.3), xytext=(17.15, 11.2),
                arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.2, ls=(0, (4, 2)),
                                mutation_scale=11))
    ax.plot([16.85, 17.45], [1.0, 1.5], color=RED, lw=2.2)
    ax.plot([16.85, 17.45], [1.5, 1.0], color=RED, lw=2.2)
    ax.text(17.55, 6.2, "no writes to plant (R8)", color=RED, fontsize=8, ha="center",
            va="center", rotation=90)
    save(fig, "33", "fig-33-4-twin-architecture")


# ----------------------------------------------------------------------------
# Figure 33.5 — fouling estimate
# ----------------------------------------------------------------------------
def fig_33_5():
    R1, C1, R2, C2, DT = 0.03725, 11.23e3, 0.02136, 130.7e3, 60.0
    day = np.arange(30 * 1440) * DT / 86400
    hod = (day % 1) * 24
    n = np.select([hod < 6, hod < 18], [1180.0, 1480.0], 1410.0)
    ps = np.select([hod < 6, hod < 18], [17.32e3, 37.04e3], 31.63e3)
    ta = 25 + 6 * np.sin(2 * np.pi * (hod - 9) / 24)
    foul = 1 + 0.30 * np.clip((day - 10) / 20, 0, 1)

    def step(tw, tf, g, k, p=(R1, C1, R2, C2, 1.0)):
        r1, c1, r2, c2, kl = p
        pw, pf = (kl * v for v in losses(n[k], ps[k], tw))
        a = 0.25 + 0.75 * n[k] / NR
        q12 = (tw - tf) / r1
        return tw + DT * (pw - q12) / c1, tf + DT * (pf + q12 - (tf - ta[k]) * g * a / r2) / c2, a

    rng = np.random.default_rng(3)
    PLANT = (0.0372, 11.1e3, 0.0214, 131e3, 1.03)
    xt, x = np.array([60.0, 50.0]), np.array([60.0, 50.0, 1.0])
    P, Q = np.diag([25.0, 1.0, 0.01]), np.diag([0.05, 0.01, 2e-7])
    Rm, est, err, sdf = 0.3**2, np.empty(day.size), np.empty(day.size), np.empty(day.size)
    for k in range(day.size):
        xt = np.array(step(*xt, 1 / foul[k], k, PLANT)[:2])
        tw, tf, a = step(*x, k)
        F = np.eye(3) + DT * np.array([[-1 / (R1 * C1), 1 / (R1 * C1), 0],
                                       [1 / (R1 * C2), -1 / (R1 * C2) - x[2] * a / (R2 * C2),
                                        -(x[1] - ta[k]) * a / (R2 * C2)],
                                       [0, 0, 0]])
        x, P = np.array([tw, tf, x[2]]), F @ P @ F.T + Q
        y = xt[1] + rng.normal(0, 0.3) - x[1]
        K = P[:, 1] / (P[1, 1] + Rm)
        x, P = x + K * y, P - np.outer(K, P[1, :])
        est[k], err[k] = 1 / x[2], x[0] - xt[0]
        sdf[k] = np.sqrt(P[2, 2]) / x[2]**2
    hit = lambda f: day[np.argmax(f >= 1.15)]  # noqa: E731
    base = 1.032
    print(f"  truth 1.15 day {hit(foul):.2f}; est day {hit(est):.2f}; ratio day {hit(est / base):.2f};"
          f" est day9 {est[9 * 1440]:.3f}, day30 {est[-1]:.3f}; err max {abs(err[1440:]).max():.2f}")

    fig, ax = plt.subplots(figsize=(6.8, 4.2))
    m = day >= 1.0
    ax.fill_between(day[m], (est - 2 * sdf)[m], (est + 2 * sdf)[m], color=BLUE, alpha=0.2, lw=0,
                    label="±2σ (EKF)")
    ax.plot(day[m], est[m], color=BLUE, lw=1.0, label="twin estimate $\\hat f$")
    ax.plot(day, foul, color=INK, lw=1.6, label="true fouling $f$")
    ax.axhline(1.15, color=ORANGE, ls="--", lw=1.2)
    ax.axhline(1.15 * base, color=RED, ls=":", lw=1.5)
    ax.text(0.3, 1.153, "absolute threshold 1.15", color=ORANGE, fontsize=8, va="bottom")
    ax.text(0.3, 1.15 * base + 0.003, "baseline-relative 1.15 × 1.032 = 1.187", color=RED,
            fontsize=8, va="bottom")
    for d, yv, lab, c, dy in ((hit(est), 1.15, "estimate\nday 17.5", ORANGE, 0.07),
                              (hit(foul), 1.15, "truth\nday 20.0", INK, -0.065),
                              (hit(est / base), 1.15 * base, "ratio alarm\nday 20.3", RED, 0.07)):
        ax.plot(d, yv, "o", color=c, ms=5, mfc="white", mew=1.4, zorder=5)
        ax.annotate(lab, (d, yv), xytext=(d + {"e": -1.6, "t": -1.6, "r": 1.4}[lab[0]], yv + dy),
                    fontsize=7.8, color=c, ha="center", va="center",
                    arrowprops=dict(arrowstyle="-", color=c, lw=0.8))
    ax.set_xlim(0, 30)
    ax.set_ylim(0.95, 1.40)
    ax.set_xlabel("Day")
    ax.set_ylabel("Fouling factor $f$ (–)")
    ax.legend(loc="lower right", fontsize=8)
    ax.text(26.5, 1.355, f"day 30: $\\hat f$ = {est[-1]:.3f}", fontsize=7.8, ha="right", color=BLUE)
    # inset
    ins = ax.inset_axes([0.08, 0.7, 0.36, 0.22])
    ins.plot(day[1440:], err[1440:], color=PINK, lw=0.5)
    ins.axhline(1.6, color=GREY, ls="--", lw=0.8)
    ins.axhline(-1.6, color=GREY, ls="--", lw=0.8)
    ins.set_ylim(-2.2, 2.2)
    ins.set_xlim(0, 30)
    ins.set_yticks([-1.6, 0, 1.6])
    ins.tick_params(labelsize=7)
    ins.set_title("winding-temperature estimate error (K) vs day", fontsize=7.5, pad=2)
    ins.set_facecolor("white")
    save(fig, "33", "fig-33-5-fouling-estimate")


# ----------------------------------------------------------------------------
# Figure 33.6 — hot-spot UQ
# ----------------------------------------------------------------------------
def fig_33_6():
    rng, N = np.random.default_rng(11), 20000
    X = {"R1": rng.normal(0.03725, 0.05 * 0.03725, N),
         "R2": rng.normal(0.02136, 0.05 * 0.02136, N),
         "kloss": rng.normal(1.0, 0.04, N),
         "foul": rng.normal(1.05, 0.03, N),
         "ta": rng.normal(40.0, 0.5, N),
         "dhs": rng.normal(10.0, 3.0, N)}

    def hot_spot(n):
        s = n / NR
        q = np.sqrt((H0 * s**2 - HS) / (KP + KS))
        ps = shaft_power(n, q)[1]
        tw = np.full(N, 120.0)
        for _ in range(30):
            pw, pf = losses(n, ps, tw)
            pw, pf = X["kloss"] * pw, X["kloss"] * pf
            tf = X["ta"] + (pw + pf) * X["foul"] * X["R2"] / (0.25 + 0.75 * s)
            tw = tf + pw * X["R1"]
        return tw + X["dhs"]

    from scipy.stats import gaussian_kde
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.8, 3.8), gridspec_kw=dict(width_ratios=[1.6, 1],
                                                                           wspace=0.45))
    xg = np.linspace(115, 185, 500)
    cols = [BLUE, GREEN, ORANGE]
    for (n, c) in zip((1480.0, 1500.0, 1520.0), cols):
        hs = hot_spot(n)
        p95, mu, pex = np.percentile(hs, 95), hs.mean(), np.mean(hs > 155)
        print(f"  {n:.0f}: mean {mu:.1f} p95 {p95:.1f} P {pex:.3f}")
        d = gaussian_kde(hs)(xg)
        a1.plot(xg, d, color=c, lw=1.6, label=f"{n:.0f} rpm: mean {mu:.1f}, P95 {p95:.1f} °C,"
                f" P(>155) = {pex:.3f}")
        dp = gaussian_kde(hs)(p95)[0]
        a1.plot([p95, p95], [0, dp], color=c, lw=1.2)
        a1.plot(p95, 0, marker="^", color=c, ms=6, clip_on=False)
        a1.fill_between(xg[xg > 155], d[xg > 155], color=c, alpha=0.18, lw=0)
    a1.axvline(155, color=RED, lw=1.4)
    a1.text(155.8, 0.071, "155 °C\nclass F\nhot-spot\nlimit", color=RED, fontsize=7.8, va="top")
    a1.set_xlim(115, 185)
    a1.set_ylim(0, 0.075)
    a1.set_xlabel("Steady hot-spot temperature at 40 °C (°C)")
    a1.set_ylabel("Probability density (1/K)")
    a1.legend(loc="upper center", bbox_to_anchor=(0.75, -0.2), fontsize=7.5, ncol=1)
    a1.text(116, 0.071, "▲ 95th percentile", fontsize=7.5, va="top", color=GREY)

    hs = hot_spot(1520.0)
    A = np.column_stack([(v - v.mean()) / v.std() for v in X.values()])
    src = np.linalg.lstsq(A, (hs - hs.mean()) / hs.std(), rcond=None)[0]
    share = dict(zip(X, 100 * src**2))
    labs = [("kloss", "loss model"), ("R2", "$R_2$"), ("dhs", "hot-spot\nallowance"), ("R1", "$R_1$"),
            ("foul", "fouling"), ("ta", "ambient")]
    vals = [share[k] for k, _ in labs]
    print("  shares", {k: round(v) for k, v in share.items()})
    yy = np.arange(len(labs))[::-1]
    a2.barh(yy, vals, color=BLUE, height=0.6)
    for yv, v in zip(yy, vals):
        a2.text(v + 1, yv, f"{v:.0f} %", va="center", fontsize=8)
    a2.set_yticks(yy)
    a2.set_yticklabels([lab for _, lab in labs], fontsize=8.2)
    a2.set_xlim(0, 55)
    a2.set_xlabel("Variance share at 1520 rpm (%)")
    save(fig, "33", "fig-33-6-hot-spot-uq")


if __name__ == "__main__":
    import sys as _s
    _only = _s.argv[1:]
    for _f in (fig_33_1, fig_33_2, fig_33_3, fig_33_4, fig_33_5, fig_33_6):
        if not _only or _f.__name__[-1] in _only:
            _f()
