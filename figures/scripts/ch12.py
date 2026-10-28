"""Figures for Chapter 12 — Edge Computing and Embedded AI.

Run from the repository root:  python figures/scripts/ch12.py
"""
import math
import sys
from pathlib import Path

import numpy as np
from scipy.stats import binom

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figstyle import COLORS, INK, arrow, box, new_fig, save, schematic  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle  # noqa: E402

BLUE, RED, GREEN, PINK, ORANGE, SKY = COLORS[:6]
GREY = "#777777"


def _line(ax, pts, color=INK, ls="-", lw=1.1, head=True):
    """Polyline through pts with an arrowhead on the last segment."""
    xs, ys = zip(*pts)
    ax.plot(xs[:-1] + (xs[-1],), ys[:-1] + (ys[-1],), color=color, ls=ls, lw=lw,
            solid_capstyle="butt")
    if head:
        ax.annotate("", xy=pts[-1], xytext=pts[-2],
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, shrinkA=0, shrinkB=0,
                                    mutation_scale=10))


# ---------------------------------------------------------------- 12.1
def fig_12_1():
    fig, ax = schematic(6.8, 5.0, xlim=(0, 18.4), ylim=(0, 13.5))
    fs = 7.6
    # sensors
    ax.text(1.8, 12.75, "Sensors on the\nbearing housing", ha="center", va="center",
            fontsize=8, weight="bold")
    box(ax, 0.1, 9.4, 3.4, 2.4, "IIS3DWB-class\naccelerometer\n3 axes, 26.7 kHz\nSPI, FIFO + DMA",
        fc="#E8F1FA", fontsize=fs)
    box(ax, 0.1, 6.9, 3.4, 1.8, "LIS3MDL-class\nmagnetometer\nstray flux, 1 kHz",
        fc="#E8F1FA", fontsize=fs)
    box(ax, 0.1, 4.75, 3.4, 1.45, "TMP117-class\ntemperature\nsensor via stud",
        fc="#E8F1FA", fontsize=fs)
    # MCU frame
    fx0, fx1, fy0, fy1 = 4.1, 14.35, 2.3, 13.3
    ax.add_patch(FancyBboxPatch((fx0, fy0), fx1 - fx0, fy1 - fy0,
                                boxstyle="round,pad=0.02,rounding_size=0.2", fc="#FAFAFA", ec=INK, lw=1.3))
    ax.text((fx0 + fx1) / 2, 12.85, "STM32U5-class MCU", ha="center", va="center",
            fontsize=8.2, weight="bold")
    ax.text((fx0 + fx1) / 2, 12.3, "Cortex-M33 160 MHz, 2 MB flash, 786 kB SRAM",
            ha="center", va="center", fontsize=7.6)
    c1x, c2x, cw = 4.45, 9.65, 4.4
    rows = [10.6, 9.05, 7.5, 5.95, 4.55]
    bh = 1.05
    col1 = ["capture buffer 196.6 kB", "scale and self-check\n(1 g gravity test)",
            "Welch FFT 8192 points\n× 4 frames × 3 axes", "192 log band energies",
            "envelope demodulation\n2–6 kHz"]
    for y, t in zip(rows, col1):
        box(ax, c1x, y, cw, bh, t, fc="#EEF3F8", fontsize=fs)
    for i in range(4):
        arrow(ax, c1x + cw / 2, rows[i], c1x + cw / 2, rows[i + 1] + bh)
    box(ax, c2x, rows[4], cw, bh, "speed estimate\nfrom flux and 1× peak", fc="#EEF3F8", fontsize=fs)
    box(ax, c2x, rows[3], cw, bh, "8 scalar features\n(incl. temperature rise)", fc="#EEF3F8", fontsize=fs)
    box(ax, c2x, rows[2], cw, bh, "200-feature vector", fc="#EEF3F8", fontsize=fs)
    hw = 2.1
    box(ax, c2x, rows[1], hw, bh, "int8 MLP\n(6 classes)", fc="#FCEBDD", fontsize=fs)
    box(ax, c2x + cw - hw, rows[1], hw, bh, "int8 auto-\nencoder", fc="#FCEBDD", fontsize=fs)
    box(ax, c2x, rows[0], cw, bh, "k-of-n temporal vote\n→ decision", fc="#E3F4EC", fontsize=fs)
    gx = (c1x + cw + c2x) / 2
    arrow(ax, c1x + cw, rows[4] + bh / 2, c2x, rows[4] + bh / 2)
    arrow(ax, c2x + cw / 2, rows[4] + bh, c2x + cw / 2, rows[3])
    arrow(ax, c2x + cw / 2, rows[3] + bh, c2x + cw / 2, rows[2])
    _line(ax, [(c1x + cw, rows[3] + 0.7), (gx, rows[3] + 0.7), (gx, rows[2] + 0.5), (c2x, rows[2] + 0.5)])
    mx, ax_ = c2x + hw / 2, c2x + cw - hw / 2
    for xx in (mx, ax_):
        arrow(ax, xx, rows[2] + bh, xx, rows[1])
        arrow(ax, xx, rows[1] + bh, xx, rows[0])
    ax.text(mx + 0.12, rows[1] + bh + 0.25, "class", fontsize=6.6, va="center", ha="left")
    ax.text(ax_ + 0.12, rows[1] + bh + 0.25, "score", fontsize=6.6, va="center", ha="left")
    # ISO branch
    box(ax, c1x, 2.55, c2x + cw - c1x, 0.9,
        "ISO 20816 velocity RMS 10–1000 Hz → severity zone" + chr(10) + "(fallback, always computed)",
        fc="#FFF4D6", fontsize=fs)
    _line(ax, [(c1x, rows[1] + 0.5), (4.27, rows[1] + 0.5), (4.27, 3.45)], color="#9A6B00", ls="--")
    # sensor links
    arrow(ax, 3.5, rows[0] + 0.5, c1x, rows[0] + 0.5)
    ax.text(3.97, rows[0] + 0.62, "SPI", fontsize=6.6, ha="center", va="bottom")
    yfl, yte = 3.85, 4.2
    _line(ax, [(3.5, 7.4), (3.8, 7.4), (3.8, yfl), (c2x + 1.3, yfl), (c2x + 1.3, rows[4])], color=PINK)
    ax.text(8.0, yfl - 0.07, "flux (I²C)", fontsize=6.8, color=PINK, ha="center", va="top")
    _line(ax, [(3.5, 5.1), (3.65, 5.1), (3.65, yte), (gx, yte), (gx, rows[3] + 0.3),
               (c2x, rows[3] + 0.3)], color=ORANGE)
    ax.text(6.9, yte + 0.05, "temperature (I²C)", fontsize=6.8, color="#A86F00", ha="center", va="bottom")
    # right column
    rx = 14.85
    box(ax, rx, 8.4, 3.45, 3.6, "SX1262-class\nLoRaWAN radio\n\n11-byte message\nhourly or on\nstate change",
        fc="#E3F4EC", fontsize=fs)
    arrow(ax, c2x + cw, rows[0] + 0.5, rx, rows[0] + 0.5)
    _line(ax, [(c2x + cw, 3.0), (16.6, 3.0), (16.6, 8.4)], color="#9A6B00", ls="--")
    ax.text(16.75, 5.7, "severity\nzone", fontsize=6.8, color="#9A6B00", ha="left")
    box(ax, rx, 0.15, 3.45, 1.75, "AA Li-SOCl₂ cell\n2.6 Ah + hybrid\npulse capacitor",
        fc="#F2F2F2", fontsize=fs)
    # flash
    ax.text(c1x, 1.95, "flash", fontsize=7, color=GREY, va="bottom")
    box(ax, c1x, 0.2, cw, 1.6, "14-day feature log\n(2016 cycles × 200 B)",
        fc="#F3E8F0", fontsize=fs)
    box(ax, c2x, 0.2, cw, 1.6, "signed model blob slot\n(schema hash, version)",
        fc="#F3E8F0", fontsize=fs)
    wx = 14.2
    _line(ax, [(c2x + cw, 1.0), (wx, 1.0), (wx, rows[1] + 0.5), (c2x + cw, rows[1] + 0.5)],
          color=PINK, ls=":")
    ax.text(wx - 0.12, 2.05, "weights", fontsize=6.6, color=PINK, ha="right", va="center")
    save(fig, "12", "fig-12-1-edge-node-pipeline")


# ---------------------------------------------------------------- 12.2
def fig_12_2():
    fig, ax = new_fig(6.4, 3.6)
    labels = ["accelerometer while capturing",
              "raw capture averaged over\n10-min cycle (196.6 kB)",
              "200-byte feature vector\nper cycle",
              "11-byte message per hour"]
    vals = [26_667 * 3 * 16, 196_608 * 8 / 600, 200 * 8 / 600, 11 * 8 / 3600]
    txt = ["1,280,000 bit/s", "2,621 bit/s", "2.7 bit/s", "0.024 bit/s"]
    y = np.arange(4)[::-1]
    cols = [GREY, GREY, BLUE, GREEN]
    ax.barh(y, vals, left=0.01, color=cols, height=0.55)
    ax.set_xscale("log")
    ax.set_xlim(0.01, 1e7)
    ax.set_yticks(y, labels, fontsize=8.5)
    for yi, v, t in zip(y, vals, txt):
        if v > 1e5:
            ax.text(v / 1.4, yi, t, va="center", ha="right", fontsize=8.5, color="white")
        else:
            ax.text(v * 1.4, yi, t, va="center", ha="left", fontsize=8.5)
    ax.axvline(48, ls="--", color=RED, lw=1.3)
    ax.text(62, 2.5, "48 bit/s: LoRaWAN EU868 SF7 legal\naverage (1 % duty cycle)",
            color=RED, fontsize=7.5, va="center")
    ax.axvline(0.15, ls=":", color=PINK, lw=1.6)
    ax.text(0.165, 1.5, "0.15 bit/s: fair use\n(30 s/day, 11-byte SF9)",
            color=PINK, fontsize=7.5, va="center")
    ax.set_ylim(-0.75, 3.75)
    ax.annotate("", xy=(0.024, -0.33), xytext=(1.28e6, -0.33),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.0))
    ax.text(3000, -0.43, "reduction 52 million×", fontsize=8.5, ha="center", va="top")
    ax.set_xlabel("data rate (bit/s)")
    save(fig, "12", "fig-12-2-data-rate-by-stage")


# ---------------------------------------------------------------- 12.3
def fig_12_3():
    fr = 39.20
    bpfo = 3.58 * fr
    f = np.arange(0, 600, 0.5)
    rng = np.random.default_rng(12)

    def floor():
        n = rng.normal(0, 1.6, f.size)
        n = np.convolve(n, np.ones(5) / 5, mode="same") * 1.6
        return -10 + n

    def peaks(centres_amps, width=1.0):
        lin = np.zeros_like(f)
        for c, a in centres_amps:
            lin += 10 ** (a / 10) * np.exp(-0.5 * ((f - c) / width) ** 2)
        return lin

    healthy_lin = 10 ** (floor() / 10) + peaks([(fr, 2.0), (2 * fr, -4.0)])
    pk = [(fr, 3.0)]
    for h in range(1, 5):
        c = h * bpfo
        a = 11 - 1.0 * (h - 1)
        pk += [(c, a), (c - fr, a - 9), (c + fr, a - 9)]
    fault_lin = 10 ** (floor() / 10) + peaks(pk)
    fig, ax = new_fig(6.6, 4.0)
    ax.axvspan(138, 143, color=GREEN, alpha=0.25, lw=0)
    ax.axvspan(175, 180, fc="none", ec=GREY, ls="--", lw=1.0, hatch="///", alpha=0.6)
    ax.plot(f, 10 * np.log10(healthy_lin), color=GREY, lw=1.0, label="healthy")
    ax.plot(f, 10 * np.log10(fault_lin), color=RED, lw=1.1, label="outer-race defect")
    for h in range(1, 5):
        c = h * bpfo
        ax.text(c, 11 - (h - 1) + 2.0, f"{c:.1f}", ha="center", fontsize=7.8, color=RED)
    ax.text(fr, 6.5, "1×\n39.2", ha="center", fontsize=7.5, color=INK)
    ax.annotate("feature band from\nfused speed 138–143 Hz", xy=(139, -14.0), xytext=(62, -17.3),
                fontsize=7.5, color="#006B4E", ha="center", va="center",
                arrowprops=dict(arrowstyle="-", color="#006B4E", lw=0.8))
    ax.annotate("band at nameplate speed\n49.5 Hz: 175–180 Hz (wrong)", xy=(180, -14.0), xytext=(272, -17.3),
                fontsize=7.5, color=GREY, ha="center", va="center",
                arrowprops=dict(arrowstyle="-", color=GREY, lw=0.8))
    ax.annotate("sidebands ±39.2 Hz", xy=(bpfo * 2 + fr, 1.5), xytext=(345, 6.0), fontsize=7.5,
                arrowprops=dict(arrowstyle="-", color=INK, lw=0.7), va="center")
    ax.set_xlim(0, 600)
    ax.set_ylim(-20, 30)
    ax.set_xlabel("frequency (Hz)")
    ax.set_ylabel("envelope amplitude (dB re 1 mg)")
    ax.legend(loc="upper left", fontsize=8)
    # inset: flux and vibration near 1x
    ins = ax.inset_axes([0.36, 0.72, 0.40, 0.26])
    fi = np.linspace(30, 50, 801)
    flux = -40 + 40 * np.exp(-0.5 * ((fi - 40.0) / 0.12) ** 2)
    vib = -30 + 22 * np.exp(-0.5 * ((fi - 39.2) / 0.15) ** 2) + 16 * np.exp(-0.5 * ((fi - 45.5) / 0.3) ** 2)
    ins.axvspan(38.4, 40.0, color=GREEN, alpha=0.2, lw=0)
    ins.plot(fi, flux, color=PINK, lw=1.0, label="flux")
    ins.plot(fi, vib, color=BLUE, lw=1.0, label="vibration")
    ins.set_xlim(30, 50)
    ins.set_ylim(-42, 5)
    ins.set_yticks([])
    ins.set_xticks([30, 35, 40, 45, 50])
    ins.tick_params(labelsize=6.5)
    ins.set_xlabel("Hz", fontsize=6.5, labelpad=1)
    ins.text(40.25, 1.0, "flux 40.00", fontsize=6.3, color=PINK, ha="left", va="top")
    ins.text(38.9, -6.5, "1× 39.20", fontsize=6.3, color=BLUE, ha="right")
    ins.text(37.9, -24, "search\n38.4–40.0", fontsize=5.8, color="#006B4E", ha="right", va="center")
    ins.text(46.0, -13, "other peak", fontsize=5.8, color=BLUE, ha="left")
    save(fig, "12", "fig-12-3-envelope-spectrum-bpfo")


# ---------------------------------------------------------------- 12.4
def fig_12_4():
    p, r, n, N = 0.02, 0.9, 6, 52_560
    k = np.arange(1, 7)
    fa = N * binom.sf(k - 1, n, p)
    fa[0] = N * p                      # k = 1 is the single-window classifier
    det = binom.sf(k - 1, n, r)
    fig, ax = new_fig(6.4, 3.9)
    ax.axvspan(3.7, 4.3, color=GREEN, alpha=0.15, lw=0)
    ax.text(4.0, 2e-3, "chosen", ha="center", color="#006B4E", fontsize=8.5)
    ax.semilogy(k, fa, "o-", color=BLUE)
    ax.set_ylim(1e-6, 1e4)
    ax.axhline(1, ls="--", color=GREY, lw=1.0)
    ax.text(2.0, 1.4, "R2: 1 per year", fontsize=8, color=GREY, ha="center", va="bottom")
    lab = ["1051", "299", "8.0", "0.12", "0.001", "3×10⁻⁶"]
    for ki, v, t in zip(k, fa, lab):
        ax.text(ki - 0.1, v * 0.5, t, color=BLUE, fontsize=8, ha="right", va="top")
    ax.set_xlabel("k (windows of the last n = 6 that must agree)")
    ax.set_ylabel("false alarms per node-year", color=BLUE)
    ax.tick_params(axis="y", colors=BLUE)
    ax2 = ax.twinx()
    ax2.spines["right"].set_visible(True)
    ax2.plot(k, det, "s-", color=ORANGE)
    ax2.set_ylim(0.5, 1.04)
    ax2.set_ylabel("detection probability within 1 h", color="#A86F00")
    ax2.tick_params(axis="y", colors="#A86F00")
    dl = ["1.000", "0.99995", "0.9987", "0.984", "0.886", "0.531"]
    for ki, v, t in zip(k, det, dl):
        ax2.text(ki + 0.08, v + 0.012, t, color="#A86F00", fontsize=8, ha="left", va="bottom")
    ax.set_xlim(0.7, 6.6)
    ax.set_xticks(k)
    ax.text(0.75, 1.5e-6, "p_FP = 0.02, recall = 0.9 per window, 52,560 windows/yr;\n"
            "independence assumed (optimistic): field data in Table 12.8",
            fontsize=7.5, color=INK, va="bottom")
    save(fig, "12", "fig-12-4-k-of-n-voting")


# ---------------------------------------------------------------- 12.5
def fig_12_5():
    sleep = 5e-6
    fig, axs = plt.subplots(1, 3, figsize=(6.8, 3.8), sharey=True,
                            gridspec_kw=dict(width_ratios=[5, 1.3, 2.6], wspace=0.06))
    a1, a2, a3 = axs
    t = np.linspace(-0.1, 1.6, 6801)
    acc = np.where((t >= 0) & (t < 1.28), 1.7e-3, 0)
    mag = np.where((t >= 0.15) & (t < 1.15), 0.4e-3, 0)
    tp0, tp1 = 1.28, 1.28 + 0.0875
    proc = np.where((t >= tp0) & (t < tp1), 4.5e-3, 0)
    tot = sleep + acc + mag + proc
    a1.fill_between(t, 1e-6, np.where(acc > 0, 1.7e-3, 1e-6), color=BLUE, alpha=0.18, lw=0)
    a1.fill_between(t, 1e-6, np.where(proc > 0, 4.5e-3, 1e-6), color=ORANGE, alpha=0.35, lw=0)
    a1.plot(t, tot, color=INK, lw=1.2)
    a1.plot(t[mag > 0], mag[mag > 0], color=PINK, lw=1.0, ls="--")
    a1.set_yscale("log")
    a1.set_ylim(1e-6, 1e-1)
    a1.set_xlim(-0.1, 1.6)
    a1.text(0.62, 1.3e-3, "accelerometer settle + capture\n1.7 mA × 1.28 s = 2.18 mC",
            ha="center", va="top", fontsize=7.5, color=BLUE)
    a1.text(0.55, 2.6e-4, "magnetometer 0.4 mA × 1.0 s", ha="center", va="top", fontsize=7.5, color=PINK)
    a1.annotate("processing 87 ms at 4.5 mA\n(0.39 mC): FFT 81 %,\nnetwork 0.5 %",
                xy=(1.31, 2e-4), xytext=(0.75, 5e-5), fontsize=7.5, color="#A86F00", ha="center",
                arrowprops=dict(arrowstyle="-", color="#A86F00", lw=0.8))
    a1.text(0.0, 6.5e-6, "sleep 5 µA", fontsize=7.5, va="bottom")
    a1.set_xlabel("analysis burst, t (s)")
    a1.set_ylabel("supply current (A)")
    # middle: sleep to the 600 s mark
    tm = np.array([1.6, 600, 600, 3600])
    a2.plot([1.6, 3600], [sleep, sleep], color=INK, lw=1.2)
    a2.set_xscale("log")
    a2.set_xlim(1.6, 3600)
    a2.axvline(600, color=GREY, ls=":", lw=1.0)
    a2.text(600, 1.5e-2, "600 s:\nnext\ncycle", fontsize=7, ha="center", color=GREY)
    a2.set_xticks([10, 600])
    a2.set_xticklabels(["10", "600"])
    a2.set_xlabel("t (s, log)")
    # uplink
    tu = np.linspace(-0.2, 2.5, 5401)
    tx = np.where((tu >= 0) & (tu < 0.206), 45e-3, 0)
    rx = np.where(((tu >= 1.206) & (tu < 1.236)) | ((tu >= 2.206) & (tu < 2.236)), 5e-3, 0)
    a3.fill_between(tu, 1e-6, np.where(tx > 0, 45e-3, 1e-6), color=GREEN, alpha=0.25, lw=0)
    a3.plot(tu, sleep + tx + rx, color=INK, lw=1.2)
    a3.set_xlim(-0.2, 2.5)
    a3.text(0.24, 5e-2, "SF9 TX 206 ms\n45 mA, 9.3 mC", fontsize=7.5, color="#006B4E", va="bottom")
    a3.text(1.72, 1.2e-2, "RX1, RX2\n≈30 ms at 5 mA", fontsize=7.5, ha="center", va="bottom")
    a3.set_xlabel("hourly uplink, t (s)")
    for a in (a2, a3):
        a.spines["left"].set_visible(False)
        a.tick_params(axis="y", left=False)
    # break marks
    d = 0.015
    for a, sides in ((a1, [1]), (a2, [0, 1]), (a3, [0])):
        for s in sides:
            a.plot([s - d, s + d], [-d * 2, d * 2], transform=a.transAxes, color=INK, lw=1, clip_on=False)
    a1.text(0.55, 2.5e-2, "average 12.6 µA;\nprocessing 0.66 µA of it", fontsize=8, ha="center",
            bbox=dict(fc="white", ec=GREY, lw=0.8, boxstyle="round,pad=0.3"))
    save(fig, "12", "fig-12-5-cycle-current-profile")


# ---------------------------------------------------------------- 12.6
def fig_12_6():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.8, 3.8), sharey=True,
                                 gridspec_kw=dict(wspace=0.12))
    x = np.array([0, 1])
    w = 0.34
    nn = [100.0, 69.3]
    ce = [96.5, 83.3]
    b1 = a1.bar(x - w / 2, nn, w, color=RED, label="1-NN (memorises)")
    b2 = a1.bar(x + w / 2, ce, w, color=BLUE, label="class centroid (averages)")
    for bars in (b1, b2):
        for b in bars:
            a1.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.6, f"{b.get_height():.1f}",
                    ha="center", fontsize=8)
    a1.set_xticks(x, ["random windows", "held-out pumps"])
    a1.set_ylim(50, 112)
    a1.set_ylabel("accuracy / macro recall (%)")
    a1.set_title("synthetic listing (accuracy)", fontsize=9.5)
    a1.legend(loc="upper right", fontsize=7.5, bbox_to_anchor=(1.0, 1.02))
    a1.annotate("ranking\nreverses", xy=(1 + w / 2, 85.5), xytext=(0.5, 92), fontsize=8, ha="center",
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.9))
    a1.annotate("", xy=(1 - w / 2, 71.5), xytext=(0.45, 90),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.9))
    cnn = [98.9, 89.6]
    mlp = [97.1, 92.4]
    c1 = a2.bar(x - w / 2, cnn, w, color=PINK, label="CNN")
    c2 = a2.bar(x + w / 2, mlp, w, color=GREEN, label="feature MLP")
    a2.errorbar([1 - w / 2, 1 + w / 2], [cnn[1], mlp[1]], yerr=1.8, fmt="none", ecolor=INK,
                capsize=3, lw=1)
    for bars in (c1, c2):
        for i, b in enumerate(bars):
            a2.text(b.get_x() + b.get_width() / 2, b.get_height() + (2.4 if i == 1 else 0.6),
                    f"{b.get_height():.1f}", ha="center", fontsize=8)
    a2.axhline(90, ls="--", color=GREY, lw=1.0)
    a2.text(0.5, 89.4, "R1: 90 %", fontsize=8, color=GREY, va="top", ha="center")
    a2.set_xticks(x, ["random split", "grouped 5-fold\nby pump"])
    a2.set_title("project models (macro recall)", fontsize=9.5)
    a2.legend(loc="upper left", fontsize=7.5)
    a2.annotate("ranking\nreverses", xy=(1 + w / 2, 96.8), xytext=(1.0, 104), fontsize=8, ha="center",
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.9))
    save(fig, "12", "fig-12-6-split-leakage")


if __name__ == "__main__":
    fig_12_1()
    fig_12_2()
    fig_12_3()
    fig_12_4()
    fig_12_5()
    fig_12_6()
