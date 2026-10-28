"""Figures for Chapter 15 — Robot Electronics and Control.

Run from the repository root:  python figures/scripts/ch15.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle, FancyBboxPatch  # noqa: E402
import schemdraw  # noqa: E402
import schemdraw.elements as elm  # noqa: E402

from figstyle import COLORS, INK, box, save, schematic, new_fig  # noqa: E402

schemdraw.use("matplotlib")

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
# Figure 15.1 — architecture of the motor-control board
# ----------------------------------------------------------------------------
def fig_15_1():
    fig, ax = schematic(6.8, 5.0, xlim=(0, 17.4), ylim=(-0.1, 12.8))
    # MCU with internal peripherals
    mx0, my0, mw, mh = 6.6, 4.2, 4.8, 5.2
    ax.add_patch(FancyBboxPatch((mx0, my0), mw, mh, boxstyle="round,pad=0.02,rounding_size=0.15",
                                fc=tint(GREEN, "26"), ec=INK, lw=1.2))
    ax.text(mx0 + mw / 2, my0 + mh - 0.6, "MCU: STM32G474 class\n170 MHz Cortex-M4F",
            ha="center", va="center", fontsize=7.0, weight="bold")
    blocks = ["TIM1/8 PWM", "ADC1–4", "TIM3/4 encoder", "TIM2/5 capture",
              "FDCAN", "USART", "SPI", "I²C", "IWDG", "GPIO"]
    for k, t in enumerate(blocks):
        c, r = k % 2, k // 2
        bx = mx0 + 0.15 + c * 2.27
        by = my0 + mh - 1.62 - r * 0.7
        ax.add_patch(Rectangle((bx, by), 2.2, 0.58, fc="white", ec=GREY, lw=0.7))
        ax.text(bx + 1.1, by + 0.29, t, fontsize=6.1, ha="center", va="center")

    # motor channels on the left
    sto = dict(color=RED, lw=1.3, ls=(0, (4, 2)))
    for side, y0 in [("L", 7.3), ("R", 4.7)]:
        box(ax, 3.55, y0, 2.45, 1.6, "Gate driver\n60 V\n3 CSAs\nnFAULT", fc="#FBE3D6", fontsize=6.3)
        box(ax, 1.55, y0, 1.8, 1.6, "3-phase\nbridge\n6 × 60 V\n4.5 mΩ", fc="#FBE3D6",
            fontsize=6.5)
        box(ax, 0.05, y0, 1.3, 1.6, f"BLDC\nmotor\n{side}", fc="#F3E6D6", fontsize=6.7)
        line(ax, [(mx0, y0 + 1.25), (6.0, y0 + 1.25)], arrow_end=True, lw=1.0)
        line(ax, [(6.0, y0 + 0.8), (mx0, y0 + 0.8)], arrow_end=True, lw=0.9, color=RED)
        line(ax, [(3.55, y0 + 0.8), (3.35, y0 + 0.8)], arrow_end=True)
        line(ax, [(1.55, y0 + 0.8), (1.35, y0 + 0.8)], arrow_end=True)
        # feedback: Halls, encoder, brake
        line(ax, [(0.7, y0), (0.7, y0 - 0.42), (6.45, y0 - 0.42), (6.45, y0 + 0.35), (mx0, y0 + 0.35)],
             color=GREEN, lw=1.0, arrow_end=True)
        ax.text(0.85, y0 - 0.48, "Halls, encoder A B Z, brake",
                fontsize=6.1, color=GREEN, ha="left", va="top")
        # STO into the gate driver's ENABLE
        line(ax, [(6.2, y0 + 0.3), (6.0, y0 + 0.3)], arrow_end=True, ms=6, **sto)
    line(ax, [(13.0, 4.7), (12.3, 4.7), (12.3, 3.6), (6.2, 3.6), (6.2, 7.6)], **sto)

    # top row: computer, IMU, ToF
    box(ax, 6.6, 11.1, 4.8, 1.4, "Navigation computer\n(USART 1 Mbit/s)", fc=tint(BLUE, "26"),
        fontsize=7.8)
    line(ax, [(7.6, 11.1), (7.6, my0 + mh)], arrow_end=True, color=BLUE, lw=1.2)
    line(ax, [(9.0, my0 + mh), (9.0, 11.1)], arrow_end=True, color=GREEN, lw=1.2)
    line(ax, [(10.7, 11.1), (10.7, my0 + mh)], both=True, color=GREY, lw=1.0, ls=(0, (2, 1.5)))
    ax.text(7.5, 10.25, "cmd\n50 Hz", fontsize=6.4, color=BLUE, ha="right", va="center")
    ax.text(9.1, 10.25, "odometry,\nIMU 100 Hz", fontsize=6.4, color=GREEN, ha="left",
            va="center")
    ax.text(10.8, 10.25, "sync", fontsize=6.2, color=GREY, ha="left", va="center")
    box(ax, 0.3, 11.1, 4.6, 1.4, "IMU\n(ICM-42688 class)", fc="#F2F2F2", fontsize=7.4)
    line(ax, [(2.6, 11.1), (2.6, 9.15), (mx0, 9.15)], lw=1.0, both=True)
    ax.text(2.75, 10.0, "SPI 10 MHz", fontsize=6.4, va="center")
    box(ax, 12.6, 11.1, 4.6, 1.4, "4 cliff ToF sensors", fc="#F2F2F2", fontsize=7.4)
    line(ax, [(14.9, 11.1), (14.9, 10.0), (12.0, 10.0), (12.0, 9.1), (mx0 + mw, 9.1)], both=True,
         lw=1.0)
    ax.text(15.05, 10.5, "I²C 400 kHz", fontsize=6.4, va="center")

    # right: BMS, scanner, safety relay
    box(ax, 13.0, 7.95, 4.2, 1.1, "BMS", fc="#FFF3D6", fontsize=7.6)
    line(ax, [(mx0 + mw, 8.5), (13.0, 8.5)], both=True, lw=1.0)
    ax.text(12.2, 8.4, "FDCAN\n500 kbit/s", fontsize=6.0, ha="center", va="top")
    box(ax, 13.0, 6.3, 4.2, 1.1, "Safety laser scanner", fc=tint(RED, "18"), fontsize=7.4)
    line(ax, [(mx0 + mw, 6.85), (13.0, 6.85)], arrow_end=True, lw=1.0)
    ax.text(12.2, 6.75, "field\nselect", fontsize=6.0, ha="center", va="top")
    box(ax, 13.0, 4.1, 4.2, 1.3, "Safety relay\n(scanner OSSD in)", fc=tint(RED, "22"),
        fontsize=7.2)
    line(ax, [(15.1, 6.3), (15.1, 5.4)], arrow_end=True, color=RED, lw=1.1)
    ax.text(15.1, 4.0, "STO (red dashed): direct to both\ngate-driver ENABLE pins and the\n"
            "brake supply, bypassing the MCU", fontsize=6.3, color=RED, ha="center", va="top")
    ax.text(0.1, 3.45, "driver links: PWM in,\nnFAULT out (red),\nSTO in (red dashed)", fontsize=6.0,
            ha="left", va="top")

    # bottom: power path
    py, ph = 0.2, 1.4
    items = [(0.05, 2.1, "Battery\n25.6 V LFP"), (2.45, 1.4, "Fuse\n30 A"),
             (4.15, 1.6, "Ideal\ndiode"), (6.05, 3.5, "Motor bus\n940 µF + bus clamp"),
             (9.85, 2.2, "DC-DC 12 V\n→ computer"), (12.35, 2.2, "DC-DC 5 V\n→ sensors"),
             (14.85, 2.35, "LDO 3.3 V\n→ MCU")]
    for x, w, t in items:
        fc = "#FFF3D6" if "bus" not in t else "#FBE3D6"
        box(ax, x, py, w, ph, t, fc=fc, fontsize=6.7)
    for (x, w, _), (x2, _, _) in zip(items[:3], items[1:4]):
        line(ax, [(x + w, py + ph / 2), (x2, py + ph / 2)], arrow_end=True, color=ORANGE, lw=1.3)
    line(ax, [(3.95, py + ph / 2), (3.95, 2.0), (11.0, 2.0), (11.0, py + ph)], color=ORANGE,
         lw=1.1, arrow_end=True)
    line(ax, [(11.0, 2.0), (13.45, 2.0), (13.45, py + ph)], color=ORANGE, lw=1.1, arrow_end=True)
    line(ax, [(12.35 + 2.2, py + ph / 2), (14.85, py + ph / 2)], arrow_end=True, color=ORANGE,
         lw=1.1)
    line(ax, [(7.8, py + ph), (7.8, 2.8), (3.1, 2.8), (3.1, 4.7)], arrow_end=True, color=ORANGE,
         lw=1.1)
    ax.text(3.25, 2.9, "to both bridges", fontsize=6.2, color=ORANGE, va="bottom")
    save(fig, "15", "fig-15-1-mcb-architecture")


# ----------------------------------------------------------------------------
# Figure 15.2 — heading fusion (Listing 15.2)
# ----------------------------------------------------------------------------
def _fusion():
    rng = np.random.default_rng(7)
    dt, T = 0.01, 180.0
    t = np.arange(0, T, dt)
    r = np.zeros_like(t)
    turns = [(20, 1), (45, -1), (70, 1), (110, 1), (140, -1)]
    for t0, sgn in turns:
        r[(t >= t0) & (t < t0 + np.pi / 2 / 0.5)] = 0.5 * sgn
    moving = ~(((t >= 0) & (t < 5)) | ((t >= 90) & (t < 95)))
    wheel = 0.94 * r + moving * rng.normal(0, 0.002, t.size)
    bias = np.radians(0.30) + np.cumsum(rng.normal(0, np.radians(0.0001), t.size))
    gyro = r + bias + rng.normal(0, np.radians(0.02), t.size)
    b_est, n_still, est = 0.0, 0, []
    for k in range(t.size):
        still = not moving[k] and abs(wheel[k]) < 1e-3
        n_still = n_still + 1 if still else 0
        if n_still > 50:
            b_est += 0.02 * (gyro[k] - b_est)
        est.append(gyro[k] - b_est)

    def head(w):
        return np.degrees(np.cumsum(w) * dt)
    truth = head(r)
    return t, turns, head(wheel) - truth, head(gyro) - truth, head(np.array(est)) - truth


def fig_15_2():
    t, turns, e_w, e_g, e_f = _fusion()
    fig, ax = new_fig(6.6, 4.0)
    for a, b in [(0, 5), (90, 95)]:
        ax.axvspan(a, b, color="#DDDDDD", lw=0)
    ax.text(2.5, 45, "parked", fontsize=7.2, ha="center", rotation=90, color=GREY)
    ax.text(92.5, 45, "parked", fontsize=7.2, ha="center", rotation=90, color=GREY)
    ax.plot(t, e_g, color=RED, lw=1.6, label="raw gyro")
    ax.plot(t, e_w, color=ORANGE, lw=1.6, label="wheels only")
    ax.plot(t, e_f, color=BLUE, lw=1.6, label="gyro + standstill bias learning")
    ax.plot(t, t / 60, color=GREY, lw=1.0, ls="--", label="R5 limit ±1°/min")
    ax.plot(t, -t / 60, color=GREY, lw=1.0, ls="--")
    for t0, s in turns:
        ax.plot([t0 + 1.6, t0 + 1.6], [-13, -11.6], color=INK, lw=1.4)
        ax.text(t0 + 1.6, -11.4, "L" if s > 0 else "R", fontsize=7, ha="center", va="bottom")
    ax.text(150, -12.6, "← 90° turns", fontsize=7, ha="left", va="bottom")
    ax.text(178, e_g[-1] - 1.2, f"{e_g[-1]:+.1f}°", fontsize=7.6, color=RED, ha="right",
            va="top")
    ax.text(178, e_w[-1] + 0.6, f"{e_w[-1]:+.1f}°", fontsize=7.6, color=ORANGE, ha="right",
            va="bottom")
    ax.set_xlim(0, 180)
    ax.set_ylim(-13, 55)
    ax.set_xlabel("time (s)")
    ax.set_ylabel("heading error (°)")
    ax.legend(fontsize=7.6, loc="upper left", bbox_to_anchor=(0.05, 1.0))
    ins = ax.inset_axes([0.56, 0.42, 0.42, 0.34])
    ins.axvspan(0, 5, color="#DDDDDD", lw=0)
    ins.axvspan(90, 95, color="#DDDDDD", lw=0)
    ins.plot(t, e_f, color=BLUE, lw=1.0)
    ins.axhline(0.5, color=BLUE, lw=0.6, ls=":")
    ins.axhline(-0.5, color=BLUE, lw=0.6, ls=":")
    ins.set_xlim(0, 180)
    ins.set_ylim(-1, 1)
    ins.tick_params(labelsize=6.5)
    ins.set_title("fused heading error (°), zoom", fontsize=7)
    for sp in ("top", "right"):
        ins.spines[sp].set_visible(True)
    save(fig, "15", "fig-15-2-heading-fusion")


# ----------------------------------------------------------------------------
# Figure 15.3 — speed-loop step responses vs delay (Listing 15.4)
# ----------------------------------------------------------------------------
def _speed_step(delay_ms, w_ref=10.0, t_end=0.3, sub=20):
    Kt, J, B = 0.054, 2.72e-4, 2.0e-4
    tau_i, Ts = 160e-6, 1e-3
    wc = 2 * np.pi * 20
    Kp, Ki = J * wc / Kt, J * wc / Kt * wc / 4
    b_sp, I_max = 0.7, 10.5
    h = Ts / sub
    buf = [0.0] * delay_ms
    w = i = integ = 0.0
    tt, out = [0.0], [0.0]
    for k in range(int(t_end / Ts)):
        meas = buf.pop(0)
        buf.append(w)
        u = Kp * (b_sp * w_ref - meas) + integ
        if abs(u) < I_max:
            integ += Ki * (w_ref - meas) * Ts
        i_ref = np.clip(u, -I_max, I_max)
        for j in range(sub):
            i += h * (i_ref - i) / tau_i
            w += h * (Kt * i - B * w) / J
            tt.append(k * Ts + (j + 1) * h)
            out.append(w)
    pm = np.degrees(np.arctan(4)) - np.degrees(wc * (delay_ms * 1e-3 + Ts / 2 + tau_i))
    return np.array(tt), np.array(out), pm


def fig_15_3():
    fig = plt.figure(figsize=(6.6, 3.9))
    ax = fig.add_axes([0.09, 0.13, 0.62, 0.83])
    ax.axhspan(9.8, 10.2, color="#DDDDDD", lw=0)
    ax.axhline(10, color=INK, lw=0.9, ls="--")
    cols = [BLUE, GREEN, ORANGE, RED]
    pms = []
    for d, c in zip((1, 3, 6, 10), cols):
        t, y, pm = _speed_step(d)
        pms.append(pm)
        ax.plot(t * 1e3, y, color=c, lw=1.5 if d < 10 else 1.2, label=f"delay {d} ms")
    ax.set_xlim(0, 300)
    ax.set_ylim(-5, 25)
    ax.set_xlabel("time (ms)")
    ax.set_ylabel("motor speed (rad/s)")
    ax.legend(fontsize=7.8, loc="upper left", bbox_to_anchor=(1.02, 1.0))
    txt = "phase margin at 20 Hz crossover\n" + "\n".join(
        f"{d:>2d} ms: {pm:5.1f}°" for d, pm in zip((1, 3, 6, 10), pms))
    ax.text(1.04, 0.62, txt, transform=ax.transAxes, fontsize=7.2, ha="left", va="top",
            family="DejaVu Sans Mono",
            bbox=dict(boxstyle="round,pad=0.4", fc="white", ec=GREY, lw=0.7))
    ax.text(1.04, 0.2, "dashed: 10 rad/s reference\ngrey band: ±2 % (9.8–10.2)",
            transform=ax.transAxes, fontsize=7.2, ha="left", va="top", color=GREY)
    save(fig, "15", "fig-15-3-speed-step-delay")


# ----------------------------------------------------------------------------
# Figure 15.4 — one 1 ms control period
# ----------------------------------------------------------------------------
def _timing_rows(ax, t0, t1, zoom=False):
    rows = ["PWM carrier\n20 kHz", "ADC trigger", "FOC ISR\nL / R", "speed task", "IMU DMA\n+ fusion",
            "UART RX", "GPIO debug"]
    n = len(rows)
    ys = {r: n - 1 - i for i, r in enumerate(rows)}
    hgt = 0.6
    # carrier
    tt = np.arange(0, 1001, 0.5)
    tri = np.abs(((tt % 50) - 25) / 25)          # 0 at valley (t = 0, 50, ...), 1 at peak? invert
    car = 1 - tri                                # peak at 25 + 50k
    y0 = ys[rows[0]]
    ax.plot(tt, y0 + hgt * car, color=INK, lw=0.8)
    peaks = np.arange(25, 1000, 50)
    y1 = ys["ADC trigger"]
    for p in peaks:
        ax.plot([p, p], [y1, y1 + hgt], color=BLUE, lw=1.0)
    y2 = ys[rows[2]]
    for p in peaks:
        ax.add_patch(Rectangle((p + 0.3, y2), 4.2, hgt * 0.9, fc=ORANGE, ec="none"))
        ax.add_patch(Rectangle((p + 4.5, y2), 4.2, hgt * 0.9, fc=PINK, ec="none"))
    y3 = ys["speed task"]
    s0 = 25 + 0.3 + 4.2 + 5.0
    ax.add_patch(Rectangle((s0, y3), 18, hgt * 0.9, fc=GREEN, ec="none"))
    y4 = ys[rows[4]]
    ax.plot([300, 300], [y4, y4 + hgt], color=SKY, lw=1.2)
    ax.add_patch(Rectangle((300.5, y4), 9, hgt * 0.9, fc=SKY, ec="none"))
    y5 = ys["UART RX"]
    ax.add_patch(Rectangle((600, y5), 160, hgt * 0.9, fc="#BBBBBB", ec=INK, lw=0.5))
    y6 = ys["GPIO debug"]
    g = [(0, 0), (s0, 0), (s0, 1), (s0 + 18, 1), (s0 + 18, 0), (1000, 0)]
    gx, gy = zip(*g)
    ax.plot(gx, y6 + np.array(gy) * hgt * 0.9, color=INK, lw=1.0, drawstyle="default")
    ax.set_yticks([ys[r] + hgt / 2 for r in rows])
    ax.set_yticklabels(rows, fontsize=7.2)
    ax.set_xlim(t0, t1)
    ax.set_ylim(-0.3, n - 0.2)
    ax.tick_params(axis="y", length=0)
    for sp in ("left",):
        ax.spines[sp].set_visible(False)
    return ys, s0, hgt


def fig_15_4():
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.8, 5.6), gridspec_kw=dict(height_ratios=[1, 1]))
    ys, s0, hgt = _timing_rows(a1, 0, 1000)
    a1.set_xlabel("time in the 1 ms control period (µs)", fontsize=8.5)
    a1.text(305, ys["IMU DMA\n+ fusion"] + hgt + 0.05, "DMA complete ≈ 300 µs, fusion 9 µs",
            fontsize=6.8, va="bottom")
    a1.text(680, ys["UART RX"] + hgt + 0.05, "16-byte frame, 160 µs at 1 Mbit/s (asynchronous)",
            fontsize=6.8, va="bottom", ha="center")
    a1.annotate("parsed (30 µs) in the next\nspeed task, t ≈ 1034 µs",
                xy=(1000, ys["speed task"] + hgt / 2), xytext=(800, ys["speed task"] + 0.25),
                fontsize=6.8, ha="center", va="center",
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.8, mutation_scale=8))
    a1.add_patch(Rectangle((-5, -0.3), 105, len(ys) + 0.1, fc="none", ec=GREY, lw=0.8, ls="--"))
    a1.text(103, 6.75, "zoom below", fontsize=6.8, color=GREY, va="top")
    a1.set_title("20 PWM periods per speed-loop period; FOC ISRs 4.2 µs each (thin bars)",
                 fontsize=8.5)

    ys, s0, hgt = _timing_rows(a2, 0, 100)
    a2.set_xlabel("time (µs), first 100 µs of the period", fontsize=8.5)
    y2 = ys["FOC ISR\nL / R"]
    a2.text(27.2, y2 + hgt + 0.03, "L", fontsize=6.8, ha="center", va="bottom")
    a2.text(31.4, y2 + hgt + 0.03, "R", fontsize=6.8, ha="center", va="bottom")
    a2.text(s0 + 9, ys["speed task"] + hgt + 0.03, "speed loop, encoders, odometry: 18 µs",
            fontsize=6.8, ha="center", va="bottom")
    a2.annotate("encoder counters\nlatched at t = 0", xy=(0, ys["speed task"] + 0.3),
                xytext=(6, ys["speed task"] + 0.3), fontsize=6.8, va="center",
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.8, mutation_scale=8))
    a2.annotate("", xy=(s0, ys["GPIO debug"] + hgt + 0.15), xytext=(s0 - 5.4, ys["GPIO debug"] + hgt + 0.15),
                arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.7, mutation_scale=6))
    a2.text(s0 + 19, ys["GPIO debug"] + 0.25,
            "start 5 µs after the L ISR; worst-case jitter 0.8 µs", fontsize=6.8,
            va="center")
    a2.text(25, ys["PWM carrier\n20 kHz"] + hgt + 0.03, "peak → ADC trigger", fontsize=6.6,
            ha="center", va="bottom")
    fig.tight_layout(h_pad=1.2)
    save(fig, "15", "fig-15-4-control-period-timing")


# ----------------------------------------------------------------------------
# Figure 15.5 — power distribution (schematic)
# ----------------------------------------------------------------------------
def fig_15_5():
    fig, ax = plt.subplots(figsize=(6.8, 4.0))
    ax.set_aspect("equal")
    ax.axis("off")
    fs = 6.3
    d = schemdraw.Drawing(canvas=ax, show=False, fontsize=fs, lw=1.0)
    MRET, LRET = ORANGE, GREEN
    Y, YR, FEED, YB, YL = 17.0, 10.5, 8.6, 6.5, 3.0
    # --- battery and BMS (charge and discharge FETs back-to-back)
    d.add(elm.BatteryDouble().up().at((0, 12.0)).length(3))
    d.add(elm.Line().at((0, 15.0)).to((0, Y)))
    d.add(elm.Line().at((0, Y)).to((1, Y)))
    f1 = d.add(elm.NMos().theta(-90).at((1, Y)).anchor("source"))
    f2 = d.add(elm.NMos().theta(-90).flip().at(f1.drain).anchor("drain"))
    ax.text(-0.6, 13.5, "LFP 8S\n25.6 V nom.\n20.0–29.2 V\n30 Ah", fontsize=fs, ha="right",
            va="center")
    box(ax, -0.8, 18.4, 6.6, 1.2, "BMS, CAN to MCB", fc="#FFF3D6", fontsize=fs)
    for f in (f1, f2):
        d.add(elm.Line().at(f.gate).to((f.gate[0], 18.4)))
    ax.text(f1.gate[0], 16.25, "CHG", fontsize=fs, ha="center", va="top")
    ax.text(f2.gate[0], 16.25, "DSG", fontsize=fs, ha="center", va="top")
    # --- main fuse, TVS, ideal diode
    d.add(elm.Fuse().right().at(f2.source).length(2.5).label("30 A", loc="top"))
    n1 = (f2.source[0] + 2.5, Y)
    d.add(elm.Line().at(n1).to((8.3, Y)))
    d.add(elm.Dot().at(n1))
    d.add(elm.Dot().at((8.3, Y)))
    d.add(elm.DiodeTVS().down().at((8.3, Y)).to((8.3, YR)))
    ax.text(8.75, 13.7, "TVS\n36 V\nstand-\noff", fontsize=fs, ha="left", va="center")
    d.add(elm.Line().at((8.3, Y)).to((10.6, Y)))
    fi = d.add(elm.NMos().theta(-90).at((10.6, Y)).anchor("source"))
    box(ax, 8.4, 18.4, 6.0, 1.2, "ideal-diode ctrl", fc="#F2F2F2", fontsize=fs)
    d.add(elm.Line().at(fi.gate).to((fi.gate[0], 18.4)))
    ax.text(fi.gate[0] - 0.3, 17.55, "60 V", fontsize=fs, ha="right", va="bottom")
    xend = 31.0
    d.add(elm.Line().at(fi.drain).to((xend, Y)))
    ax.text(28.0, Y + 0.3, "motor bus", fontsize=7.2, weight="bold", ha="center", va="bottom")
    # --- bus capacitors and the star point
    xs = 16.0
    for x, lab, left in [(15.0, "2 × 470 µF\nlow-ESR", True),
                         (17.0, "4 × 4.7 µF\nceramic", False)]:
        d.add(elm.Dot().at((x, Y)))
        d.add(elm.Capacitor(polar=left).down().at((x, Y)).length(3.0))
        d.add(elm.Line().at((x, Y - 3.0)).to((x, 12.0)))
        d.add(elm.Line().at((x, 12.0)).to((xs, YR)))
        ax.text(x + (-0.45 if left else 0.45), 15.4, lab, fontsize=fs,
                ha="right" if left else "left", va="center")
    # --- gate drivers and bridges (one block)
    d.add(elm.Dot().at((24.3, Y)))
    d.add(elm.Line().at((24.3, Y)).to((24.3, 16.0)))
    box(ax, 21.6, 13.4, 5.4, 2.6, "gate drivers\nL and R\n+ bridges", fc="#FBE3D6", fontsize=fs)
    # --- bus clamp
    xc = 29.0
    d.add(elm.Dot().at((xc, Y)))
    d.add(elm.Resistor().down().at((xc, Y)).length(3.0))
    ax.text(xc + 0.6, 15.5, "15 Ω, 50 W\nAl-housed", fontsize=fs, ha="left", va="center")
    fq = d.add(elm.NMos().right().reverse().at((xc, Y - 3.0)).anchor("drain"))
    d.add(elm.Line().at(fq.source).to((xc, YR)))
    ax.text(xc - 0.4, fq.source[1] + 0.8, "60 V", fontsize=fs, ha="right", va="center")
    op = d.add(elm.Opamp(leads=True).left().anchor("out").at(fq.gate))
    ax.text(op.in1[0] + 0.3, op.in1[1], "ref", fontsize=fs - 0.3, ha="left", va="center")
    ax.text(op.in2[0] + 0.3, op.in2[1], "bus", fontsize=fs - 0.3, ha="left", va="center")
    ax.text(31.6, 11.4, "comparator\n33.0 V on\n32.0 V off", fontsize=fs, ha="center", va="top")
    # --- brake supply: MCU switch and safety-relay contact in series
    d.add(elm.Dot().at((19.0, Y)))
    d.add(elm.Line().at((19.0, Y)).to((19.0, 19.0)))
    d.add(elm.Switch().right().at((19.0, 19.0)).length(2.0))
    d.add(elm.Switch().right().at((21.0, 19.0)).length(2.0))
    ax.text(20.0, 18.75, "MCU", fontsize=fs, ha="center", va="top")
    ax.text(22.0, 19.65, "safety relay", fontsize=fs, ha="center", va="bottom")
    box(ax, 23.3, 18.4, 6.6, 1.2, "brakes L, R (24 V)", fc="#EEE0EE", fontsize=fs)
    ax.text(16.7, 19.0, "brake\nsupply", fontsize=fs, ha="center", va="center")
    # --- returns: battery and motor (orange) meet at the star
    ax.plot([0, 0, xs], [12.0, YR, YR], color=MRET, lw=1.8, zorder=1)
    ax.plot([xs, xc], [YR, YR], color=MRET, lw=1.8, zorder=1)
    ax.plot([24.3, 24.3], [13.4, YR], color=MRET, lw=1.8, zorder=1)
    ax.text(4.0, YR - 0.2, "battery return", fontsize=fs, color=MRET, va="top", ha="center")
    ax.text(26.2, YR - 0.2, "motor return", fontsize=fs, color=MRET, va="top", ha="center")
    ax.plot(xs, YR, "o", ms=8, mfc="white", mec=INK, mew=1.4, zorder=6)
    ax.text(xs + 0.5, YR + 0.35, "star", fontsize=fs + 0.3, ha="left", va="bottom", weight="bold")
    # --- converter branches from the fused node n1
    d.add(elm.Line().at(n1).to((n1[0], FEED)))
    d.add(elm.Dot().at((n1[0], FEED)))
    d.add(elm.Line().at((n1[0], FEED)).to((24.0, FEED)))
    d.add(elm.Line().at((n1[0], FEED)).to((n1[0], YB)))
    d.add(elm.Fuse().right().at((n1[0], YB)).length(2.0).label("3 A", loc="top"))
    d.add(elm.Inductor().right().at((n1[0] + 2.0, YB)).length(2.2).label("10 µH", loc="top"))
    xa = n1[0] + 4.2
    d.add(elm.Dot().at((xa, YB)))
    d.add(elm.Capacitor(polar=True).down().at((xa, YB)).to((xa, YL)))
    ax.text(xa + 0.4, 4.5, "220 µF", fontsize=fs, ha="left", va="center")
    d.add(elm.Line().at((xa, YB)).to((13.6, YB)))
    box(ax, 13.6, YB - 1.0, 6.4, 2.0, "DC-DC 12 V, 5 A\nbuck, 9–36 V in", fc="#FFF3D6",
        fontsize=fs)
    d.add(elm.Line().at((20.0, YB)).to((21.0, YB)))
    d.add(elm.Dot().at((21.0, YB)))
    d.add(elm.Capacitor(polar=True).down().at((21.0, YB)).to((21.0, YL)))
    ax.text(21.4, 4.5, "1000 µF\nhold-up", fontsize=fs, ha="left", va="center")
    d.add(elm.Line().at((21.0, YB)).to((22.0, YB)))
    ax.annotate("", xy=(23.0, YB), xytext=(22.0, YB),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.0, mutation_scale=8))
    ax.text(23.1, YB, "computer", fontsize=fs, ha="left", va="center")
    # 5 V and 3.3 V branch
    d.add(elm.Line().at((24.0, FEED)).to((27.0, FEED)))
    d.add(elm.Line().at((27.0, FEED)).to((27.0, YB)))
    d.add(elm.Fuse().right().at((27.0, YB)).length(1.8).label("2 A", loc="top"))
    box(ax, 28.8, YB - 0.8, 4.8, 1.6, "DC-DC 5 V\n3 A", fc="#FFF3D6", fontsize=fs)
    d.add(elm.Line().at((33.6, YB)).to((34.2, YB)))
    d.add(elm.Dot().at((34.2, YB)))
    ax.annotate("", xy=(35.4, YB), xytext=(34.2, YB),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.0, mutation_scale=8))
    ax.text(35.5, YB, "sensors", fontsize=fs, ha="left", va="center")
    d.add(elm.Line().at((34.2, YB)).to((34.2, 5.0)))
    box(ax, 30.4, 3.4, 4.6, 1.6, "LDO 3.3 V\n300 mA", fc="#FFF3D6", fontsize=fs)
    ax.annotate("", xy=(36.0, 4.2), xytext=(35.0, 4.2),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.0, mutation_scale=8))
    ax.text(36.1, 4.2, "MCU", fontsize=fs, ha="left", va="center")
    # --- logic return (green), its own trace to the star
    ax.plot([xa, 32.7], [YL, YL], color=LRET, lw=1.8, zorder=1)
    for x, yb in [(16.8, YB - 1.0), (29.2, YB - 0.8), (32.7, 3.4)]:
        ax.plot([x, x], [yb, YL], color=LRET, lw=1.8, zorder=1)
    ax.plot([12.4, 12.4, xs, xs], [YL, 9.6, 9.6, YR], color=LRET, lw=1.8, zorder=1)
    ax.text(21.0, YL - 0.3, "logic return: meets the motor return only at the star", fontsize=fs,
            color=LRET, va="top", ha="center")
    d.draw()
    ax.set_xlim(-5.2, 37.6)
    ax.set_ylim(1.6, 20.9)
    save(fig, "15", "fig-15-5-power-distribution")


# ----------------------------------------------------------------------------
# Figure 15.6 — bus voltage during regenerative braking
# ----------------------------------------------------------------------------
def _bus_sim(version):
    C = 940e-6
    dt = 2e-6
    t = np.arange(0, 0.4, dt)
    v = np.empty_like(t)
    ic = np.zeros_like(t)
    V = 29.2
    P0 = 37.0                      # W reaching the bus at the start of braking (text)
    enabled, clamp = True, False
    t_lock = None
    delay_on, pend = 0.33e-3, None
    for k, tk in enumerate(t):
        vel = 1.2 - 1.0 * tk if enabled or version == 2 else None
        p_regen = P0 * max(1.2 - 1.0 * tk, 0) / 1.2
        p_q = 0.6 + 29.0           # board quiescent + hotel loads (computer, sensors) on the bus
        if version == 1:
            if enabled and V >= 34.0:
                enabled, t_lock = False, tk
            if not enabled and t_lock is not None and tk - t_lock >= 0.1 - 1e-9:
                enabled = True     # auto-retry after 100 ms
            # coasting downhill increases speed, so the retry brakes harder
            p = (p_regen * (1.0 + 0.6 * (tk // 0.1))) if enabled else 0.0
            if V <= 29.2 and p - p_q < 0:
                V = 29.2           # battery discharge path holds the bus at the pack voltage
                v[k] = V
                continue
            V += (p - p_q) / (C * V) * dt
        else:
            if not clamp and V >= 33.0 and pend is None:
                pend = tk
            if pend is not None and tk - pend >= delay_on:
                clamp, pend = True, None
            if clamp and V <= 32.0:
                clamp = False
            pr = V * V / 15.0 if clamp else 0.0
            ic[k] = V / 15.0 if clamp else 0.0
            V += (p_regen - p_q - pr) / (C * V) * dt
            V = max(V, 29.2)       # battery discharge path holds the bus at the pack voltage
        v[k] = V
    return t, v, ic


def fig_15_6():
    t1, v1, _ = _bus_sim(1)
    t2, v2, i2 = _bus_sim(2)
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.6, 4.8), sharex=True,
                                 gridspec_kw=dict(height_ratios=[2.6, 1]))
    for y, lab, c in [(29.2, "29.2 V full battery", GREY), (33.0, "33 V clamp on", BLUE),
                      (34.0, "34 V R6 limit = pilot lockout", RED),
                      (36.0, "36 V MOSFET worst case (with overshoot)", INK)]:
        a1.axhline(y, color=c, lw=0.8, ls="--")
        a1.text(398, y + 0.12, lab, fontsize=7, color=c, ha="right", va="bottom", zorder=5,
                bbox=dict(boxstyle="square,pad=0.1", fc="white", ec="none", alpha=0.85))
    a1.plot(t1 * 1e3, v1, color=RED, lw=1.3, label="pilot board (lockout + auto-retry)")
    a1.plot(t2 * 1e3, v2, color=BLUE, lw=0.8, label="version 2 (33 V clamp, 15 Ω)")
    a1.set_ylim(28, 42)
    a1.set_ylabel("bus voltage (V)")
    a1.legend(fontsize=7.6, loc="upper left")
    a1.text(10, 37.6, "pilot: 29.2 → 34 V in ≈ 20 ms, driver lockout, wheels coast;\n"
            "auto-retry every 100 ms re-trips", fontsize=7.2, color=RED, va="center")
    ins = a1.inset_axes([0.64, 0.71, 0.34, 0.21])
    m = (t2 >= 0.1) & (t2 <= 0.11)
    ins.plot(t2[m] * 1e3, v2[m], color=BLUE, lw=1.0)
    ins.set_ylim(31.6, 33.8)
    ins.tick_params(labelsize=6.3)
    ins.set_title("version 2, 100–110 ms", fontsize=6.8)
    for sp in ("top", "right"):
        ins.spines[sp].set_visible(True)
    a2.plot(t2 * 1e3, i2, color=BLUE, lw=0.6)
    a2.set_ylim(0, 2.6)
    a2.set_ylabel("clamp\ncurrent (A)")
    a2.set_xlabel("time from start of braking (ms)")
    a2.set_xlim(0, 400)
    a2.text(398, 2.3, f"≈ {33.1 / 15:.1f} A peak (V/15 Ω), version 2 only", fontsize=7,
            ha="right", va="bottom")
    fig.tight_layout(h_pad=0.6)
    save(fig, "15", "fig-15-6-bus-voltage-regen")


if __name__ == "__main__":
    fig_15_1()
    fig_15_2()
    fig_15_3()
    fig_15_4()
    fig_15_5()
    fig_15_6()
