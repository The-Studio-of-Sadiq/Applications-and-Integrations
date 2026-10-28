"""Figures for Chapter 16 — Drones and Aerial Robotics.

Run from the repository root:  python figures/scripts/ch16.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle, FancyBboxPatch  # noqa: E402
from scipy.optimize import brentq  # noqa: E402

from figstyle import COLORS, INK, box, save, schematic, new_fig  # noqa: E402

BLUE, ORANGE, GREEN, PINK, YELLOW, SKY = COLORS[:6]
RED = "#C62828"
GREY = "#777777"


def tint(c, a="30"):
    return c + a


def line(ax, pts, color=INK, lw=1.1, ls="-", arrow_end=False, both=False, ms=10):
    xs, ys = zip(*pts)
    if not arrow_end and not both:
        ax.plot(xs, ys, color=color, lw=lw, ls=ls, solid_capstyle="butt")
        return
    if len(pts) > 2:
        ax.plot(xs[:-1], ys[:-1], color=color, lw=lw, ls=ls)
    ax.annotate("", xy=pts[-1], xytext=pts[-2],
                arrowprops=dict(arrowstyle="<|-|>" if both else "-|>", color=color, lw=lw,
                                ls=ls, shrinkA=0, shrinkB=0, mutation_scale=ms))


# ----------------------------------------------------------------------------
# Propulsion model of Sections 16.2-16.4 and 16.9 (listing in Section 16.9)
# ----------------------------------------------------------------------------
RHO, G = 1.225, 9.81
D, CT, CP = 13 * 0.0254, 0.105, 0.042
KV, RM, I0 = 320.0, 0.15, 0.5
KT = 60 / (2 * np.pi * KV)
ETA_ESC, P_AUX, M_DRY = 0.95, 10.0, 1.422


def point_T(T):
    n = np.sqrt(T / (CT * RHO * D ** 4))
    I = CP * RHO * n ** 2 * D ** 5 / (2 * np.pi) / KT + I0
    return n, I, n * 60 / KV + I * RM


def point_V(Vm):
    def f(n):
        return n * 60 / KV + (CP * RHO * n ** 2 * D ** 5 / (2 * np.pi) / KT + I0) * RM - Vm
    n = brentq(f, 1e-3, 500)
    I = CP * RHO * n ** 2 * D ** 5 / (2 * np.pi) / KT + I0
    return n, I, CT * RHO * n ** 2 * D ** 4


def p_hover(m):
    n, I, V = point_T(m * G / 4)
    return 4 * V * I / ETA_ESC + P_AUX


# ----------------------------------------------------------------------------
# Figure 16.1 — architecture
# ----------------------------------------------------------------------------
def fig_16_1():
    fig, ax = schematic(6.8, 5.0, xlim=(0, 17.4), ylim=(-0.2, 12.9))
    E, C, Dt = RED, BLUE, GREY
    # energy source
    box(ax, 0.1, 10.9, 3.3, 1.7, "Battery\n6S2P Li-ion\n21.6 V, 9 Ah", fc=tint(RED, "1A"),
        fontsize=7.2)
    box(ax, 0.1, 7.9, 3.3, 2.2, "Power board\n0.5 mΩ shunt\n+ voltage divider",
        fc=tint(RED, "1A"), fontsize=7.0)
    line(ax, [(1.75, 10.9), (1.75, 10.1)], arrow_end=True, color=E, lw=1.8)
    # ESCs and motors in a row
    xs = [4.3, 7.5, 10.7, 13.9]
    dirs = ["CCW", "CCW", "CW", "CW"]
    for k, (x, dr) in enumerate(zip(xs, dirs)):
        box(ax, x, 9.25, 2.9, 1.25, f"ESC{k + 1} 30 A\n2 × 220 µF", fc="#FBE3D6",
            fontsize=6.8)
        box(ax, x, 11.3, 2.9, 1.35, f"M{k + 1} 4114 320 Kv\n13x4.4, {dr}", fc="#F3E6D6",
            fontsize=6.6)
        line(ax, [(x + 1.45, 10.5), (x + 1.45, 11.3)], arrow_end=True, color=E, lw=1.5)
        line(ax, [(x + 0.75, 8.6), (x + 0.75, 9.25)], arrow_end=True, color=E, lw=1.5)
        line(ax, [(x + 2.15, 8.05), (x + 2.15, 9.25)], arrow_end=True, color=C, lw=1.2)
    ax.text(xs[0] + 1.3, 10.9, "3-phase", fontsize=6.2, color=E, ha="right", va="center")
    line(ax, [(3.4, 8.6), (xs[-1] + 0.75, 8.6)], color=E, lw=1.8)
    ax.text(4.3, 8.45, "18–25 V, up to 16 A per ESC", fontsize=6.6, color=E, va="top")
    # flight controller
    fx0, fy0, fw, fh = 4.3, 1.0, 6.3, 5.9
    ax.add_patch(FancyBboxPatch((fx0, fy0), fw, fh, boxstyle="round,pad=0.02,rounding_size=0.15",
                                fc=tint(BLUE, "1E"), ec=INK, lw=1.2))
    ax.text(fx0 + fw / 2, fy0 + fh - 0.45, "Flight controller\nSTM32H743, 480 MHz", fontsize=7.4,
            ha="center", va="center", weight="bold")
    subs = ["ICM-42688-P (SPI)", "BMI088 (SPI)", "BMP390 (I²C)", "microSD logger"]
    for i, t in enumerate(subs):
        ax.add_patch(Rectangle((fx0 + 0.4, fy0 + 3.6 - i * 0.85), fw - 0.8, 0.65, fc="white",
                               ec=GREY, lw=0.7))
        ax.text(fx0 + fw / 2, fy0 + 3.6 - i * 0.85 + 0.325, t, fontsize=6.8, ha="center",
                va="center")
    line(ax, [(fx0 + 3.0, fy0 + fh), (fx0 + 3.0, 8.05)], color=C, lw=1.2)
    line(ax, [(xs[0] + 2.15, 8.05), (xs[-1] + 2.15, 8.05)], color=C, lw=1.2)
    ax.text(fx0 + 3.15, 7.35, "bidirectional DShot600 + eRPM\ngyro → thrust < 1.5 ms",
            fontsize=6.6, color=C, va="center")
    # regulators
    box(ax, 0.1, 5.4, 3.3, 1.1, "Reg. 5 V, 3 A", fc=tint(RED, "1A"), fontsize=7.0)
    box(ax, 0.1, 3.7, 3.3, 1.1, "Reg. 12 V, 1 A", fc=tint(RED, "1A"), fontsize=7.0)
    line(ax, [(1.75, 7.9), (1.75, 6.5)], arrow_end=True, color=E, lw=1.3)
    line(ax, [(3.0, 7.9), (3.0, 7.2), (3.65, 7.2), (3.65, 4.25), (3.4, 4.25)], arrow_end=True,
         color=E, lw=1.3)
    line(ax, [(3.4, 5.95), (fx0, 5.95)], arrow_end=True, color=E, lw=1.3)
    line(ax, [(1.75, 3.7), (1.75, 0.5), (12.6, 0.5), (12.6, 1.0)], arrow_end=True, color=E, lw=1.3)
    ax.text(7.5, 0.55, "12 V to gimbal", fontsize=6.6, color=E, va="bottom", ha="center")
    line(ax, [(3.4, 9.0), (3.9, 9.0), (3.9, 4.3), (fx0, 4.3)], arrow_end=True, color=Dt, lw=1.0,
         ls=(0, (3, 2)))
    ax.text(3.75, 3.6, "V, I\nsense", fontsize=6.2, color=Dt, ha="right", va="top")
    # data peripherals on the right
    per = [(5.6, "GNSS u-blox M10 +\nRM3100 compass\non 120 mm mast", "UART, I²C", 1.35),
           (4.0, "ELRS receiver\nCRSF 150 Hz", "UART", 1.0),
           (2.6, "MAVLink\ntelemetry radio", "UART", 1.0),
           (1.0, "Gimbal + camera", "UART", 1.0)]
    for y, t, bus, h in per:
        box(ax, 12.0, y, 5.2, h, t, fc="#F2F2F2", fontsize=6.6)
        yc = y + h / 2
        line(ax, [(fx0 + fw, yc), (12.0, yc)], both=True, color=Dt, lw=1.0)
        ax.text(11.9, yc + 0.08, bus, fontsize=6.2, color=Dt, ha="right", va="bottom")
    # legend
    for i, (c, t) in enumerate([(E, "energy"), (C, "control"), (Dt, "data")]):
        ax.plot([11.6 + i * 1.95, 12.1 + i * 1.95], [0.25, 0.25], color=c, lw=2)
        ax.text(12.2 + i * 1.95, 0.25, t, fontsize=6.8, va="center")
    save(fig, "16", "fig-16-1-quadcopter-architecture")


# ----------------------------------------------------------------------------
# Figure 16.2 — thrust stand
# ----------------------------------------------------------------------------
def fig_16_2():
    thr = np.linspace(1, 100, 300)
    Tg, Pb = [], []
    for u in thr:
        n, I, T = point_V(u / 100 * 21.6)
        Tg.append(T / G * 1000)
        Pb.append(u / 100 * 21.6 * I / ETA_ESC)
    Tg, Pb = np.array(Tg), np.array(Pb)
    pts = np.array([20, 40, 50, 60, 80, 100])
    Tp, Pp = [], []
    for u in pts:
        n, I, T = point_V(u / 100 * 21.6)
        Tp.append(T / G * 1000)
        Pp.append(u / 100 * 21.6 * I / ETA_ESC)
    Tp, Pp = np.array(Tp), np.array(Pp)

    fig, ax = new_fig(6.4, 4.0)
    ax2 = ax.twinx()
    ax2.spines["right"].set_visible(True)
    ax.plot(thr, Tg, color=BLUE, lw=1.6, label="thrust (model)")
    ax.errorbar(pts, Tp, yerr=0.02 * Tp, fmt="o", color=BLUE, ms=4, capsize=2.5, lw=1,
                label="thrust, measured ±2 %")
    ax2.plot(thr, Pb, color=ORANGE, lw=1.6, label="battery-side power (model)")
    ax2.errorbar(pts, Pp, yerr=0.02 * Pp, fmt="s", color=ORANGE, ms=4, capsize=2.5, lw=1,
                 label="power, measured ±2 %")
    ax.axvline(56, color=GREY, ls="--", lw=1)
    ax.text(55, 1650, "hover 56 %\n585 gf, 58 W", fontsize=7.6, ha="right", va="top")
    ax.axhline(1170, color=GREY, ls="--", lw=1)
    ax.text(57, 1190, "T/W = 2 (1170 gf per motor)", fontsize=7.4, va="bottom", ha="left")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 1800)
    ax2.set_ylim(0, 300)
    ax.set_xlabel("throttle (%)")
    ax.set_ylabel("thrust (gf)", color=BLUE)
    ax2.set_ylabel("battery-side power (W)", color=ORANGE)
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, fontsize=7.0, loc="upper left", bbox_to_anchor=(0.02, 0.6))
    ins = ax2.inset_axes([0.09, 0.69, 0.27, 0.25])
    m = thr >= 10
    ins.plot(thr[m], Tg[m] / Pb[m], color=GREEN, lw=1.3)
    for u in (20, 50, 100):
        n, I, T = point_V(u / 100 * 21.6)
        st = (T / G * 1000) / (u / 100 * 21.6 * I / ETA_ESC)
        ins.plot(u, st, "o", color=GREEN, ms=3.5)
        ins.text(u + (3 if u < 100 else -3), st + 0.6, f"{st:.1f}", fontsize=6.5,
                 ha="left" if u < 100 else "right", va="bottom")
    ins.set_xlim(0, 105)
    ins.set_ylim(0, 22)
    ins.tick_params(labelsize=6.5)
    ins.set_xlabel("throttle (%)", fontsize=6.5, labelpad=1)
    ins.set_title("specific thrust (gf/W)", fontsize=7)
    for sp in ("top", "right"):
        ins.spines[sp].set_visible(True)
    ax.set_title("4114 320 Kv motor, 13x4.4 propeller, 21.6 V", fontsize=9)
    save(fig, "16", "fig-16-2-thrust-stand")


# ----------------------------------------------------------------------------
# Figure 16.3 — IMU vibration spectrum
# ----------------------------------------------------------------------------
def fig_16_3():
    f = np.linspace(0, 500, 5001)

    def spectrum(lines, floor, width=1.2):
        y = np.full_like(f, floor)
        for f0, a in lines:
            y = np.maximum(y, a / (1 + ((f - f0) / width) ** 2))
        # gentle floor ripple so it does not look like a ruler
        rng = np.random.default_rng(int(floor * 1e4))
        return y * np.exp(rng.normal(0, 0.12, f.size)) * (y <= floor * 1.01) + \
            y * (y > floor * 1.01)
    hard = spectrum([(61.3, 4.0), (122.6, 1.2), (183.9, 0.5), (245.2, 0.3)], 0.05)
    soft = spectrum([(61.3, 0.35), (122.6, 0.12), (183.9, 0.025), (245.2, 0.015)], 0.005)
    fig, ax = new_fig(6.4, 3.9)
    ax.axvspan(0, 15, color="#DDDDDD", lw=0)
    ax.text(16, 0.0013, "control bandwidth\n0–15 Hz", fontsize=7.2, color=GREY, va="bottom")
    ax.semilogy(f, hard, color=RED, lw=1.0, label="hard mount, unbalanced propeller")
    ax.semilogy(f, soft, color=BLUE, lw=1.0, label="20 Hz soft mount, balanced propellers")
    ax.axhline(3.0, color=INK, ls="--", lw=0.9)
    ax.axhline(4.0, color=GREY, ls="--", lw=0.9)
    ax.text(495, 3.0 * 0.92, "3 g: R7 limit", fontsize=7.2, ha="right", va="top")
    ax.text(495, 4.0 * 1.06, "4 g: old ±4 g range", fontsize=7.2, ha="right", va="bottom",
            color=GREY)
    for f0, a, lab in [(61.3, 4.0, "61 Hz rotor"), (122.6, 1.2, "123 Hz blade pass"),
                       (183.9, 0.5, "184 Hz"), (245.2, 0.3, "245 Hz")]:
        ax.text(f0 + 4, a * 1.05, lab, fontsize=6.8, color=RED, va="bottom")
    ax.text(65, 0.35 * 1.1, "0.35 g", fontsize=6.8, color=BLUE, va="bottom")
    ax.text(127, 0.12 * 1.1, "0.12 g", fontsize=6.8, color=BLUE, va="bottom")
    ax.set_xlim(0, 500)
    ax.set_ylim(1e-3, 10)
    ax.set_xlabel("frequency (Hz)")
    ax.set_ylabel("vertical acceleration amplitude (g)")
    ax.legend(fontsize=7.4, loc="upper right", bbox_to_anchor=(1.0, 0.8))
    save(fig, "16", "fig-16-3-imu-vibration-spectrum")


# ----------------------------------------------------------------------------
# Figure 16.4 — cascaded flight control
# ----------------------------------------------------------------------------
def fig_16_4():
    fig, ax = schematic(6.8, 3.7, xlim=(-0.2, 23.6), ylim=(-0.4, 12.2))
    blocks = [("position P\n50 Hz\nBW 0.1 Hz", "#E8EEF6"),
              ("velocity\nPID\n50 Hz", "#E8EEF6"),
              ("thrust\nvector \u2192\nattitude", "#F2F2F2"),
              ("angle P\n250 Hz\nK 6.5 s\u207b\u00b9", "#E2F0E8"),
              ("rate PID\n1 kHz\nfc 8.8 Hz", "#E2F0E8"),
              ("mixer +\ndesatu-\nration", "#F2F2F2"),
              ("DShot\n600", "#F2F2F2"),
              ("ESCs +\nmotors\n\u03c4 45 ms", "#FBE3D6"),
              ("airframe\nJ 0.038\nkg m\u00b2", "#FBE3D6")]
    x0, w, gap, yb, h = 1.7, 2.1, 0.25, 7.2, 2.6
    xc = []
    for i, (t, fc) in enumerate(blocks):
        x = x0 + i * (w + gap)
        box(ax, x, yb, w, h, t, fc=fc, fontsize=6.0)
        xc.append(x + w / 2)
        if i:
            line(ax, [(x - gap, yb + h / 2), (x, yb + h / 2)], arrow_end=True, ms=8)
    ax.text(0.75, yb + h / 2, "position\nset-\npoint", fontsize=6.4, ha="center", va="center")
    line(ax, [(1.3, yb + h / 2), (x0, yb + h / 2)], arrow_end=True, ms=8)
    xr = x0 + 9 * (w + gap) - gap
    line(ax, [(xr, yb + h / 2), (xr + 0.4, yb + h / 2)], color=INK)
    # collective thrust from the velocity loop into the mixer
    line(ax, [(xc[1], yb + h), (xc[1], 11.1), (xc[5], 11.1), (xc[5], yb + h)], arrow_end=True,
         color=ORANGE, lw=1.1, ls=(0, (4, 2)), ms=8)
    ax.text((xc[1] + xc[5]) / 2, 11.2, "collective thrust from the velocity loop", fontsize=6.6,
            color=ORANGE, ha="center", va="bottom")
    # feedback paths
    fb = [(5.4, "gyro 8 kHz, LPF 80 Hz,\nRPM notches 61 and 123 Hz", [4], BLUE),
          (3.2, "EKF attitude, 200 Hz", [3], GREEN),
          (1.0, "EKF velocity and position\n(GNSS 10 Hz, baro)", [1, 0], GREY)]
    xR = xr + 0.4
    for y, t, targets, c in fb:
        line(ax, [(xR, yb + h / 2), (xR, y)], color=c, lw=1.1) if y == 5.4 else None
        bx0, bx1 = xc[targets[-1]] - 0.9, xR - 0.6
        bw = min(bx1 - bx0, 7.6)
        bxs = xR - 0.6 - bw
        box(ax, bxs, y - 0.65, bw, 1.3, t, fc=tint(c, "18"), fontsize=6.4)
        line(ax, [(xR, y), (bxs + bw, y)], arrow_end=True, color=c, lw=1.1, ms=8)
        for tg in targets:
            line(ax, [(bxs, y) if tg == targets[0] else (bxs, y), (xc[tg], y), (xc[tg], yb)],
                 arrow_end=True, color=c, lw=1.1, ms=8)
    ax.plot([xR, xR], [yb + h / 2, 1.0], color=INK, lw=1.1)
    ax.text(xR + 0.1, 6.2, "sensors", fontsize=6.4, rotation=90, va="center")
    save(fig, "16", "fig-16-4-cascaded-flight-control")


# ----------------------------------------------------------------------------
# Figure 16.5 — rate-loop Bode (listing in Section 16.8)
# ----------------------------------------------------------------------------
def fig_16_5():
    J, Tmax, tau_m, Td = 0.038, 5.0, 0.045, 1.5e-3
    Kp, Ki, Kd, fD = 0.6, 2.0, 0.016, 40.0
    f = np.logspace(np.log10(0.1), 2.7, 20000)
    w = 2 * np.pi * f
    s = 1j * w

    def lpf2(fc):
        wc = 2 * np.pi * fc
        return wc ** 2 / (s ** 2 + np.sqrt(2) * wc * s + wc ** 2)

    def notch(f0, q=3.0):
        w0 = 2 * np.pi * f0
        return (s ** 2 + w0 ** 2) / (s ** 2 + w0 / q * s + w0 ** 2)
    C = Kp + Ki / s + Kd * s / (1 + s / (2 * np.pi * fD))
    P = (Tmax / J) / (s * (tau_m * s + 1)) * np.exp(-s * Td)
    cases = [("LPF 80 Hz", lpf2(80), BLUE), ("LPF 25 Hz", lpf2(25), RED),
             ("LPF 80 Hz + notches 61/123 Hz", lpf2(80) * notch(61) * notch(123), GREEN)]
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.6, 5.0), sharex=True)
    res = []
    for name, gy, c in cases:
        L = C * P * gy
        mag = 20 * np.log10(np.abs(L))
        ph = np.degrees(np.unwrap(np.angle(L)))
        ic = np.argmin(np.abs(np.abs(L) - 1))
        if ph[ic] > 0:
            ph -= 360
        pm = 180 + ph[ic]
        x = np.where((np.sign(L.imag[:-1]) != np.sign(L.imag[1:])) & (L.real[:-1] < 0))[0]
        k = x[np.argmax(np.abs(L[x]))]
        gm = -20 * np.log10(np.abs(L[k]))
        ms = 20 * np.log10(np.max(np.abs(1 / (1 + L))))
        res.append((name, f[ic], pm, gm, f[k], ms, c))
        a1.semilogx(f, mag, color=c, lw=1.4, label=name)
        a2.semilogx(f, ph, color=c, lw=1.4)
    a1.axhline(0, color=INK, lw=0.7)
    a1.axvline(8.8, color=GREY, lw=0.7, ls=":")
    a1.text(9.3, 30, "crossover 8.8 Hz", fontsize=7.2, color=GREY)
    a1.set_ylim(-40, 40)
    a1.set_ylabel("|L| (dB)")
    a1.legend(fontsize=7.4, loc="lower left")
    a2.axhline(-180, color=INK, lw=0.8, ls="--")
    a2.axvline(8.8, color=GREY, lw=0.7, ls=":")
    for name, fc, pm, gm, f180, ms, c in res:
        a2.plot([fc, fc], [-180, -180 + pm], color=c, lw=2.2, alpha=0.6)
        a1.plot([f180, f180], [-gm, 0], color=c, lw=2.2, alpha=0.6)
        a1.plot(f180, -gm, "o", color=c, ms=3.5)
    txt = "\n".join(f"{n.split(' +')[0] if '+' not in n else 'LPF 80 + notches'}: PM {pm:.1f}°, "
                    f"GM {gm:.1f} dB at {f180:.1f} Hz, Ms {ms:.1f} dB"
                    for n, fc, pm, gm, f180, ms, c in res)
    a2.text(0.012, 0.04, txt, transform=a2.transAxes, fontsize=7.0, va="bottom", ha="left",
            bbox=dict(boxstyle="round,pad=0.35", fc="white", ec=GREY, lw=0.6))
    a2.set_ylim(-360, -90)
    a2.set_yticks([-360, -270, -180, -90])
    a2.set_ylabel("phase of L (°)")
    a2.set_xlabel("frequency (Hz)")
    a2.set_xlim(0.5, 200)
    fig.tight_layout(h_pad=0.6)
    save(fig, "16", "fig-16-5-rate-loop-bode")
    return res


# ----------------------------------------------------------------------------
# Figure 16.6 — endurance versus pack mass
# ----------------------------------------------------------------------------
def fig_16_6():
    mb = np.linspace(0.2, 3.0, 281)

    def endurance(m, e):
        return np.array([0.8 * e * mi / p_hover(M_DRY + mi) * 60 for mi in np.atleast_1d(m)])

    def tw(m, vc):
        n, I, T = point_V(0.98 * vc * 6)
        return 4 * T / ((M_DRY + m) * G)
    fig, ax = new_fig(6.4, 4.0)
    for e, vc, c, name in [(154, 3.5, ORANGE, "LiPo, 154 Wh/kg"), (211, 3.2, BLUE, "Li-ion 21700, 211 Wh/kg")]:
        t = endurance(mb, e)
        mx = brentq(lambda m: tw(m, vc) - 2, 0.2, 3.0)
        ok = mb <= mx
        ax.plot(mb[ok], t[ok], color=c, lw=2, label=name)
        ax.plot(mb[~ok], t[~ok], color=c, lw=1.6, ls="--")
        tmx = endurance(mx, e)[0]
        ax.plot([mx, mx], [0, tmx], color=c, ls=":", lw=1.2)
        ax.plot(mx, tmx, "o", color=c, ms=4)
        right = c == ORANGE
        ax.text(mx + 0.04 if right else mx - 0.04, 1.5, f"T/W = 2 at floor:\n{mx:.2f} kg, {tmx:.1f} min", fontsize=7,
                color=c, va="bottom", ha="left" if right else "right")
    ax.axhline(25, color=GREY, ls="--", lw=1)
    ax.text(2.98, 25.4, "25 min", fontsize=7.4, color=GREY, ha="right", va="bottom")
    for m, t, lab, c, dx, dy in [(0.72, 24.7, "LiPo 5000", ORANGE, 0.05, -2.8),
                                 (1.12, 31.4, "LiPo 8000", ORANGE, 0.06, -3.2),
                                 (0.92, 38.4, "Li-ion 6S2P (chosen)", BLUE, -0.05, 2.0)]:
        ax.plot(m, t, "D", color=c, ms=6, mec=INK, mew=0.8, zorder=5)
        ax.text(m + dx, t + dy, f"{lab}\n{m:.2f} kg, {t:.1f} min", fontsize=7, color=c,
                ha="left" if dx > 0 else "right", va="center")
    ax.set_xlim(0.2, 3.0)
    ax.set_ylim(0, 55)
    ax.set_xlabel("battery-pack mass (kg)")
    ax.set_ylabel("hover endurance to 80 % DoD (min)")
    ax.legend(fontsize=7.6, loc="upper left")
    ax.text(2.98, 15.0, "dry mass 1.422 kg\ndashed: T/W < 2 at the loaded floor", fontsize=7,
            ha="right", color=GREY)
    save(fig, "16", "fig-16-6-endurance-vs-pack-mass")


if __name__ == "__main__":
    fig_16_1()
    fig_16_2()
    fig_16_3()
    fig_16_4()
    fig_16_5()
    fig_16_6()
