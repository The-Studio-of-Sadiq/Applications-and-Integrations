"""Figures for Chapter 9 — Instrumentation Projects.

Run from the repository root:  python figures/scripts/ch09.py
"""
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


def line(ax, pts, color=INK, lw=1.1, ls="-", arrow_end=True):
    """Poly-line through pts with an arrow head on the last segment."""
    xs, ys = zip(*pts)
    if len(pts) > 2:
        ax.plot(xs[:-1], ys[:-1], color=color, lw=lw, ls=ls)
    if arrow_end:
        ax.annotate("", xy=pts[-1], xytext=pts[-2],
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, ls=ls,
                                    shrinkA=0, shrinkB=0, mutation_scale=10))
    else:
        ax.plot(xs[-2:], ys[-2:], color=color, lw=lw, ls=ls)


# ----------------------------------------------------------------------------
# Figure 9.1 — laboratory instrument suite
# ----------------------------------------------------------------------------
def fig_9_1():
    fig, ax = schematic(6.8, 5.0, xlim=(0, 17), ylim=(0, 12.5))
    # centre: instrument VLAN
    cx0, cx1 = 6.55, 10.45
    ax.add_patch(FancyBboxPatch((cx0, 0.6), cx1 - cx0, 11.3, boxstyle="round,pad=0.02,rounding_size=0.2",
                                fc="#F4F4F4", ec=GREY, lw=1.0, ls=(0, (4, 2))))
    ax.text(8.5, 11.5, "Instrument VLAN\n(no route to internet)", ha="center", va="center",
            fontsize=7.6, color=GREY, style="italic")
    box(ax, 6.85, 7.3, 3.3, 3.4,
        "Lab data server\n\ntime-series database\nwaveform archive\n(Ch. 8)\ntest automation\n(Python executive)",
        fc=BLUE + "22", fontsize=7.0)
    box(ax, 6.85, 4.7, 3.3, 1.9, "Instrument\nVLAN switch\n(PTP-aware)", fc="#E8E8E8", fontsize=7.6)
    box(ax, 6.85, 1.0, 3.3, 3.0, "PTP grandmaster\nGNSS-disciplined\n+ NTP service\n(same time base)",
        fc=YELLOW + "40", fontsize=7.4)
    line(ax, [(8.5, 6.6), (8.5, 7.3)], arrow_end=True)
    line(ax, [(8.5, 4.0), (8.5, 4.7)], arrow_end=True)

    left = [
        ("9.1 Thermocouple\nmonitors: 3 climatic\nchambers, 16 × type T", "MQTT", "NTP"),
        ("9.2 Bench energy meters\n12 outlets, 230 V 16 A\nclass 1", "MQTT", "NTP"),
        ("9.3 Speed meters\nsmall motor benches\n1024-line encoders", "MQTT 1 kHz", "NTP"),
        ("9.4 Power-quality logger\n400 V incoming board\n4 V + 4 I, Class S", "Modbus TCP", "NTP ±2 ms"),
    ]
    right = [
        ("9.5 Battery-module\nmonitor: 16s LFP 100 Ah\nshunt 100 µΩ", "MQTT", "PTP"),
        ("9.6 PT100 calibration rig\ndry block +\nreference PRT", "LXI SCPI", "NTP"),
        ("9.7 ATE station\nCh. 7 strain module", "LXI SCPI", "NTP"),
        ("9.8 Dynamometer DAQ\n(Ch. 8) link", "Ethernet\nfiles", "PTP"),
    ]
    ys = [9.6, 6.85, 4.1, 1.35]
    bh = 2.2
    for (txt, proto, tsrc), y in zip(left, ys):
        box(ax, 0.1, y, 4.3, bh, txt, fc=GREEN + "22", fontsize=7.0)
        yc = y + bh / 2
        line(ax, [(4.4, yc), (cx0, yc)], arrow_end=True)
        ax.text(5.48, yc + 0.12, proto, ha="center", va="bottom", fontsize=6.9)
        ax.text(5.48, yc - 0.12, tsrc, ha="center", va="top", fontsize=6.9, color=ORANGE)
    for (txt, proto, tsrc), y in zip(right, ys):
        box(ax, 12.6, y, 4.3, bh, txt, fc=PINK + "22", fontsize=7.0)
        yc = y + bh / 2
        line(ax, [(12.6, yc), (cx1, yc)], arrow_end=True)
        ax.text(11.52, yc + 0.12, proto, ha="center", va="bottom", fontsize=6.9)
        ax.text(11.52, yc - 0.12, tsrc, ha="center", va="top", fontsize=6.9, color=ORANGE)
    ax.text(0.1, 0.35, "Arrow labels: protocol (black) and time source (orange). Chamber set-points over Modbus TCP; "
            "cyclers and sources over SCPI.", fontsize=6.6, color=GREY, ha="left", va="center")
    save(fig, "09", "fig-9-1-lab-instrument-suite")


# ----------------------------------------------------------------------------
# Figure 9.2 — CJC error after lid closure
# ----------------------------------------------------------------------------
def fig_9_2():
    fig, ax = new_fig()
    t = np.linspace(0, 240, 600)
    a = 0.2 + 1.9 * (1 - np.exp(-t / 22.0))
    rng = np.random.default_rng(9)
    b = 0.03 * np.sin(2 * np.pi * t / 95) + 0.025 * rng.standard_normal(t.size)
    b = np.convolve(b, np.ones(15) / 15, mode="same")
    ax.axhspan(-1.0, 1.0, color=GREEN, alpha=0.07, lw=0)
    for yl in (-1.0, 1.0):
        ax.axhline(yl, color=INK, ls="--", lw=1.0)
    ax.text(236, 1.05, "T1 limit +1.0 °C", ha="right", va="bottom", fontsize=8.5)
    ax.text(236, -0.95, "T1 limit −1.0 °C", ha="right", va="bottom", fontsize=8.5)
    ax.axhline(0, color=GREY, lw=0.6)
    ax.plot(t, a, color=RED, label="A: original — thermistor on PCB near regulator")
    ax.plot(t, b, color=BLUE, label="B: PT1000 in aluminium isothermal block")
    ax.fill_between(t, -0.1, 0.1, color=BLUE, alpha=0.12, lw=0)
    e60 = 0.2 + 1.9 * (1 - np.exp(-60 / 22.0))
    ax.plot([60], [e60], "o", color=RED, ms=5)
    ax.annotate("t = 60 min: error ≈ 2.0 °C\ncell at 58 °C actual reads 60 °C\n→ test-abort alarm trips",
                xy=(60, e60), xytext=(95, 1.35), fontsize=8.3,
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.9))
    ax.text(150, 2.17, "→ 2.1 °C (τ ≈ 22 min)", fontsize=8.3, color=RED, va="bottom")
    ax.text(236, -0.14, "B within ±0.1 °C", fontsize=8.3, color=BLUE, va="top", ha="right")
    ax.set_xlim(0, 240)
    ax.set_ylim(-1.25, 2.5)
    ax.set_xticks(np.arange(0, 241, 30))
    ax.set_xlabel("Time after lid closure (min)")
    ax.set_ylabel("Reading error vs reference PRT (°C)")
    ax.legend(loc="lower right", bbox_to_anchor=(1.0, 0.40), fontsize=8.3)
    save(fig, "09", "fig-9-2-cjc-error-lid-closed")


# ----------------------------------------------------------------------------
# Figure 9.3 — speed-measurement methods
# ----------------------------------------------------------------------------
def fig_9_3():
    LINES, F_CLK, T_WIN, PITCH, M_MIN = 1024, 170e6, 1e-3, 0.01, 40
    rpm = np.logspace(np.log10(50), 4, 600)
    f_line = rpm / 60 * LINES
    m_rel = 1 / (f_line * T_WIN)
    t_clk = f_line / F_CLK
    t_rel = t_clk + 2 * PITCH
    lines = np.maximum(M_MIN, np.floor(f_line * T_WIN))
    win = np.maximum(T_WIN, lines / f_line)
    mt_q = 1 / (F_CLK * win)
    mt_p = 2 * PITCH / lines

    fig, ax = new_fig(6.4, 4.6)
    ax.axvspan(300, 6000, color=GREEN, alpha=0.08, lw=0)
    ax.text(1340, 2.2e-5, "S1 speed range\n300–6000 rpm", ha="center", fontsize=8.2, color=GREEN)
    ax.hlines(1e-3, 300, 6000, color=INK, ls="--", lw=1.1)
    ax.text(310, 1.12e-3, "S1: ±0.1 %", fontsize=8.3, va="bottom")
    ax.loglog(rpm, m_rel, color=ORANGE, label="M method (count in 1 ms)")
    ax.loglog(rpm, t_rel, color=PINK, label="T method (single interval, with pitch error)")
    ax.loglog(rpm, t_clk, color=PINK, ls="--", lw=1.3, label="T method, clock term alone")
    ax.loglog(rpm, mt_p, color=BLUE, label="M/T, pitch term (≥ 40 lines)")
    ax.loglog(rpm, mt_q, color=BLUE, ls=":", lw=1.6, label="M/T, clock quantization")
    ax.annotate("117 %", xy=(50, 1.17), xytext=(64, 0.42), fontsize=8, color=ORANGE,
                arrowprops=dict(arrowstyle="-", color=ORANGE, lw=0.7))
    ax.text(9500, 0.0059 * 0.8, "0.59 %", ha="right", va="top", fontsize=8, color=ORANGE)
    ax.annotate("2344 rpm: 40 lines in 1 ms", xy=(2344, 5e-4), xytext=(2500, 2.2e-3), fontsize=7.8,
                color=BLUE, arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=0.8))
    ax.text(10000, 1.18e-4 * 0.78, "0.012 %", ha="right", va="top", fontsize=8, color=BLUE)
    ax.set_xlim(50, 10000)
    ax.set_ylim(1e-6, 1.6)
    ax.set_xlabel("Shaft speed (rpm)")
    ax.set_ylabel("Relative speed error")
    ax.set_yticks([1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1])
    ax.set_yticklabels(["0.0001 %", "0.001 %", "0.01 %", "0.1 %", "1 %", "10 %", "100 %"])
    ax.grid(True, which="major", lw=0.5)
    from matplotlib.ticker import FixedLocator, NullFormatter
    ax.set_xticks([50, 100, 300, 1000, 3000, 10000])
    ax.set_xticklabels(["50", "100", "300", "1000", "3000", "10 000"])
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=2, fontsize=8)
    ax.set_title("1024-line encoder, 170 MHz capture clock, 1 % pitch error", fontsize=9.5)
    save(fig, "09", "fig-9-3-speed-method-resolution")


# ----------------------------------------------------------------------------
# Figure 9.4 — harmonic groups, fixed vs synchronized window
# ----------------------------------------------------------------------------
def _groups(x):
    X = 2 * np.abs(np.fft.rfft(x)) / len(x)
    g = {h: np.sqrt(X[10 * h] ** 2 + 0.5 * X[10 * h - 5] ** 2 + 0.5 * X[10 * h + 5] ** 2
                    + sum(X[10 * h + k] ** 2 for k in (-4, -3, -2, -1, 1, 2, 3, 4)))
         for h in range(1, 41)}
    thd = np.sqrt(sum(g[h] ** 2 for h in range(2, 41))) / g[1]
    return np.array([g[h] / g[1] for h in range(1, 41)]), thd


def fig_9_4():
    from scipy.interpolate import CubicSpline
    FS, N, f = 10_240, 2048, 49.8
    H = {1: 1.0, 5: 0.04, 7: 0.03, 11: 0.015}
    t = np.arange(int(1.1 * N)) / FS
    x = 325.27 * sum(a * np.sin(2 * np.pi * h * f * t + 0.3 * h) for h, a in H.items())
    gf, thd_f = _groups(x[:N])
    t_sync = np.arange(N) * (10 / f) / N
    gs, thd_s = _groups(CubicSpline(t, x)(t_sync))
    orders = np.arange(2, 14)
    true = np.array([H.get(h, 0.0) for h in orders])
    fixed = gf[orders - 1] * 100
    sync = gs[orders - 1] * 100

    fig, ax = new_fig()
    w = 0.38
    ax.bar(orders - w / 2, fixed, w, color=RED, label="Fixed 2048-sample window (200.0 ms)")
    ax.bar(orders + w / 2, sync, w, color=BLUE, label="Resampled to exactly 10 cycles (200.8 ms)")
    ax.hlines(true * 100, orders - w, orders + w, color=INK, lw=1.6, label="True value")
    for h, v in zip(orders, fixed):
        if h == 2:
            ax.text(h - w / 2, v - 0.08, f"{v:.2f}", ha="center", va="top", fontsize=6.9, color="white",
                    rotation=90)
        elif v > 0.2:
            ax.text(h - w / 2, max(v, H.get(h, 0) * 100) + 0.08, f"{v:.2f}", ha="center", va="bottom", fontsize=6.9, color=RED,
                    rotation=90)
    ax.hlines(2.0, 2 - 0.6, 2 + 0.6, color=INK, ls="--", lw=1.2)
    ax.text(2.65, 2.05, "EN 50160 limit\nfor order 2 (2 %)", fontsize=7.8, va="bottom", ha="left")
    ax.text(0.985, 0.97, f"THD (to H40)\nfixed window: {100 * thd_f:.2f} %\nsynchronized: {100 * thd_s:.2f} %"
            "\ntrue: 5.22 %", transform=ax.transAxes, ha="right", va="top", fontsize=8.3,
            bbox=dict(boxstyle="round,pad=0.35", fc="white", ec=GREY, lw=0.8))
    ax.set_xticks(orders)
    ax.set_xlim(1.4, 13.6)
    ax.set_ylim(0, 5)
    ax.set_xlabel("Harmonic order")
    ax.set_ylabel("Harmonic group (% of fundamental)")
    ax.legend(loc="upper left", bbox_to_anchor=(0.53, 0.72), fontsize=7.9)
    ax.set_title("49.8 Hz supply, 10.24 kSa/s, IEC 61000-4-7 harmonic groups", fontsize=9.5)
    save(fig, "09", "fig-9-4-harmonic-groups-sync")


# ----------------------------------------------------------------------------
# Figure 9.5 — PT100 calibration residuals
# ----------------------------------------------------------------------------
def fig_9_5():
    A0, B0 = 3.9083e-3, -5.775e-7
    true = (100.031, 3.9050e-3, -5.79e-7)

    def r_cvd(t, r0, a, b):
        return r0 * (1 + a * t + b * t * t)

    def t_from_r(r, r0, a, b):
        return (-a + np.sqrt(a * a - 4 * b * (1 - r / r0))) / (2 * b)

    tt = np.linspace(0, 125, 300)
    nom_err = 1e3 * (t_from_r(r_cvd(tt, *true), 100.0, A0, B0) - tt)
    tp = np.array([0, 25, 50, 75, 100, 125.0])
    res = np.array([11.1, -24.3, 9.4, 6.3, 1.0, -3.5])

    fig, ax = new_fig(6.4, 4.3)
    ax.axhspan(-75, 75, color=GREEN, alpha=0.06, lw=0)
    for yl in (-75, 75):
        ax.axhline(yl, color=INK, ls="--", lw=1.0)
    ax.text(37.5, 77, "C1: U ≤ 75 mK", ha="center", va="bottom", fontsize=8.3)
    ax.text(37.5, -73, "C1: −75 mK", ha="center", va="bottom", fontsize=8.3)
    ax.axhline(0, color=GREY, lw=0.6)
    ax.errorbar(tp, res, yerr=66, fmt="o", color=BLUE, ms=5, capsize=4, lw=1.2,
                label="Fit residual of individual CVD curve, ± U = 66 mK (k = 2)")
    ax.plot(tt, nom_err, color=ORANGE, label="Error if IEC 60751 nominal curve were used")
    for t0 in (0, 60, 125):
        e = np.interp(t0, tt, nom_err)
        ax.plot([t0], [e], "s", color=ORANGE, ms=4)
        ax.text(t0 + (2 if t0 < 120 else -1), e + (5 if t0 < 120 else 9), f"+{e:.0f} mK", fontsize=8,
                color=ORANGE, ha="left" if t0 < 120 else "center", va="bottom")
    ax.set_xlim(-5, 130)
    ax.set_ylim(-100, 100)
    ax.set_xticks(np.arange(0, 126, 25))
    ax.set_xlabel("Temperature (°C)")
    ax.set_ylabel("Temperature deviation (mK)")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=1, fontsize=8)
    save(fig, "09", "fig-9-5-pt100-calibration-residuals")


# ----------------------------------------------------------------------------
# Figure 9.6 — ATE test flow
# ----------------------------------------------------------------------------
def _diamond(ax, xc, yc, w, h, text, fc=YELLOW + "40", fontsize=7.4):
    ax.add_patch(Polygon([(xc - w / 2, yc), (xc, yc + h / 2), (xc + w / 2, yc), (xc, yc - h / 2)],
                         closed=True, fc=fc, ec=INK, lw=1.0))
    ax.text(xc, yc, text, ha="center", va="center", fontsize=fontsize)


def _term(ax, xc, yc, w, h, text, fontsize=7.4):
    ax.add_patch(FancyBboxPatch((xc - w / 2, yc - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.4",
                                fc="#E8E8E8", ec=INK, lw=1.0))
    ax.text(xc, yc, text, ha="center", va="center", fontsize=fontsize)


def fig_9_6():
    fig, ax = schematic(6.8, 5.0, xlim=(0, 17), ylim=(0, 12.5))
    fs = 7.0
    L, R, RX = 2.9, 9.6, 14.8          # column centres
    LW, RW = 5.2, 5.8                  # box widths

    def pbox(xc, yc, text, w, h=1.05, fc="#EEF3F8"):
        box(ax, xc - w / 2, yc - h / 2, w, h, text, fc=fc, fontsize=fs)

    # left column: set-up and supply checks
    lys = [11.65, 10.3, 8.95, 7.6]
    _term(ax, L, lys[0], LW, 1.05, "Start: load, clamp,\nscan serial number", fontsize=fs)
    pbox(L, lys[1], "Program firmware (SWD)\nverify CRC", LW)
    pbox(L, lys[2], "Power on; supply current\n150–220 mA", LW)
    pbox(L, lys[3], "Excitation ±2.5 V check\n4.998–5.002 V total", LW)
    for y0, y1 in zip(lys[:-1], lys[1:]):
        line(ax, [(L, y0 - 0.525), (L, y1 + 0.525)])
    dy = 6.05
    _diamond(ax, L, dy, 3.4, 1.5, "any FAIL?", fontsize=fs)
    line(ax, [(L, lys[3] - 0.525), (L, dy + 0.75)])
    pbox(L, 4.2, "Reject bin, fault code logged\n(also on a FAIL at\nany later step)", LW, h=1.3, fc=RED + "22")
    line(ax, [(L, dy - 0.75), (L, 4.85)])
    ax.text(L + 0.15, 5.1, "yes", fontsize=fs, ha="left", va="center")

    # right column: channel tests
    rys = [11.65, 10.15, 8.85, 7.55]
    pbox(R, rys[0], "All 8 channels: zero, ±1000,\n±3000 µε; gain limit ±0.10 %,\nguard band 0.02 %", RW, h=1.3)
    pbox(R, rys[1], "Noise record 10 s\n≤ 0.25 µε rms", RW)
    pbox(R, rys[2], "Shunt cal\n1000 µε ± 0.1 %", RW)
    pbox(R, rys[3], "DAC output (DMM)\n−10, 0, +10 V", RW)
    line(ax, [(R, rys[0] - 0.65), (R, rys[1] + 0.525)])
    for y0, y1 in zip(rys[1:-1], rys[2:]):
        line(ax, [(R, y0 - 0.525), (R, y1 + 0.525)])
    line(ax, [(L + 1.7, dy), (6.1, dy), (6.1, rys[0]), (R - RW / 2, rys[0])])
    ax.text(L + 1.85, dy + 0.1, "no", fontsize=fs, ha="left", va="bottom")
    _diamond(ax, R, dy, 3.9, 1.5, "any\nMARGINAL?", fontsize=fs)
    line(ax, [(R, rys[3] - 0.525), (R, dy + 0.75)])
    pbox(R, 4.2, "PASS: print label; write record\nto database (raw data +\nstation calibration IDs)", RW, h=1.3,
         fc=GREEN + "22")
    line(ax, [(R, dy - 0.75), (R, 4.85)])
    ax.text(R + 0.15, 5.1, "no", fontsize=fs, ha="left", va="center")
    _term(ax, R, 2.75, 2.4, 0.8, "End", fontsize=fs)
    line(ax, [(R, 4.2 - 0.65), (R, 3.15)])

    # retest branch
    _diamond(ax, RX, dy, 3.6, 1.5, "already\nretested?", fontsize=fs)
    line(ax, [(R + 1.95, dy), (RX - 1.8, dy)])
    ax.text((R + 1.95 + RX - 1.8) / 2, dy + 0.1, "yes", fontsize=fs, ha="center", va="bottom")
    pbox(RX, 8.6, "Retest once\n(retest counter + 1)", 3.6, h=1.05, fc=YELLOW + "30")
    line(ax, [(RX, dy + 0.75), (RX, 8.6 - 0.525)])
    ax.text(RX + 0.15, 7.45, "no", fontsize=fs, ha="left", va="center")
    line(ax, [(RX, 8.6 + 0.525), (RX, rys[0]), (R + RW / 2, rys[0])])
    pbox(RX, 3.75, "Engineering\nreview bin", 3.6, h=1.05, fc=ORANGE + "30")
    line(ax, [(RX, dy - 0.75), (RX, 3.75 + 0.525)])
    ax.text(RX + 0.15, 4.8, "yes (still\nmarginal)", fontsize=fs, ha="left", va="center")

    # side box: golden unit
    ax.add_patch(FancyBboxPatch((0.3, 0.3), 16.4, 1.4, boxstyle="round,pad=0.02,rounding_size=0.15",
                                fc="white", ec=GREY, lw=1.0, ls=(0, (4, 2))))
    ax.text(8.5, 1.0, "Station self-test: golden unit measured every 4 h, results trended to catch a drifting "
            "station;\nstation calibration IDs (bridge simulators, DMM) stored with every unit record",
            ha="center", va="center", fontsize=fs, color=INK)
    save(fig, "09", "fig-9-6-ate-test-flow")


if __name__ == "__main__":
    fig_9_1()
    fig_9_2()
    fig_9_3()
    fig_9_4()
    fig_9_5()
    fig_9_6()
