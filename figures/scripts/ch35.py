"""Figures for Chapter 35 — Project: Smart Energy Monitor.

Run from the repository root:  python figures/scripts/ch35.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle  # noqa: E402
import schemdraw  # noqa: E402
import schemdraw.elements as elm  # noqa: E402

from figstyle import COLORS, INK, box, save, schematic  # noqa: E402

schemdraw.use("matplotlib")

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
# Figure 35.1 — architecture
# ----------------------------------------------------------------------------
def fig_35_1():
    fig, ax = schematic(6.8, 4.9, xlim=(0, 18), ylim=(0.3, 13.0))
    XB = 10.0                                     # isolation barrier
    ax.add_patch(Rectangle((0.1, 0.5), XB - 0.1, 12.0, fc=tint(ORANGE, "14"), ec="none", zorder=0))
    ax.add_patch(Rectangle((XB, 0.5), 17.9 - XB, 12.0, fc=tint(BLUE, "12"), ec="none", zorder=0))
    for dx in (-0.09, 0.09):
        ax.plot([XB + dx, XB + dx], [0.5, 12.5], color=RED, lw=1.6, zorder=1)
    ax.text(4.95, 12.15, "Mains side (referenced to N, treated as live)", ha="center", va="center",
            fontsize=7.8, weight="bold", color="#8A3B12")
    ax.text(14.0, 12.15, "SELV side (accessible)", ha="center", va="center", fontsize=8.2,
            weight="bold", color="#1D4F7A")
    ax.text(XB + 0.3, 11.1, "reinforced isolation · 8 mm creepage\n3 kV a.c. hipot", ha="left",
            va="center", fontsize=7.0, color=RED, zorder=3)
    fs = 6.9
    # mains side
    box(ax, 0.3, 8.6, 3.6, 2.4, "Voltage divider\n3 × 330 kΩ\n+ 2.10 kΩ\nfuse 0.5 A, MOV", fc="white",
        fontsize=fs)
    box(ax, 0.3, 5.2, 3.6, 2.8, "3 CT inputs\n100 A : 50 mA\nburden 9.98 Ω\nTVS 5 V", fc="white",
        fontsize=fs)
    box(ax, 4.4, 5.2, 1.2, 5.8, "", fc="white")
    ax.text(5.0, 8.1, "anti-alias RC: 1 k + 1 k, 4.7 nF C0G", rotation=90, ha="center", va="center",
            fontsize=fs)
    box(ax, 6.1, 5.2, 2.4, 5.8, "ADS131M04\n\n4 ch ΔΣ\n24-bit\n4 kSPS\n\nsimultaneous\nsampling",
        fc=tint(ORANGE, "30"), fontsize=fs)
    box(ax, 6.1, 3.3, 2.4, 1.3, "8.192 MHz\noscillator", fc="white", fontsize=fs)
    line(ax, [(7.3, 4.6), (7.3, 5.2)], arrow_end=True)
    ax.text(7.45, 4.9, "CLKIN", fontsize=6.2, va="center")
    line(ax, [(3.9, 9.8), (4.4, 9.8)], arrow_end=True)
    line(ax, [(3.9, 6.6), (4.4, 6.6)], arrow_end=True)
    line(ax, [(5.6, 9.8), (6.1, 9.8)], arrow_end=True)
    line(ax, [(5.6, 6.6), (6.1, 6.6)], arrow_end=True)
    ax.text(0.2, 11.6, "L, N", fontsize=7.4, weight="bold", va="center")
    line(ax, [(1.0, 11.6), (2.1, 11.6), (2.1, 11.0)], arrow_end=True)
    ax.text(0.3, 4.65, "3 × split-core CT\n(incomer, PV, EV)", fontsize=6.8, va="top")
    line(ax, [(1.0, 4.7), (1.0, 5.2)], arrow_end=True)
    # isolators straddling the barrier
    box(ax, 8.9, 7.3, 2.2, 3.0, "ISOW7741\n\nSPI: 3 fwd,\n1 back\n\n+ isolated\n3.3 V", fc="white",
        fontsize=6.8)
    box(ax, 8.9, 5.2, 2.2, 1.6, "ISO7710\n\nDRDY", fc="white", fontsize=6.8)
    line(ax, [(8.5, 9.6), (8.9, 9.6)], both=True)
    line(ax, [(8.9, 7.8), (8.5, 7.8)], arrow_end=True, color=GREEN)
    line(ax, [(8.5, 6.0), (8.9, 6.0)], arrow_end=True)
    # SELV side
    box(ax, 11.5, 5.2, 3.6, 5.0, "ESP32-S3\n\ncore 1: metrology\n(DRDY ISR,\nDMA SPI)\n\ncore 0: Wi-Fi,\n"
        "MQTT/TLS, logging", fc=tint(BLUE, "30"), fontsize=6.9)
    line(ax, [(11.1, 9.6), (11.5, 9.6)], both=True)
    line(ax, [(11.1, 6.0), (11.5, 6.0)], arrow_end=True)
    side = [(8.95, "FRAM 8 kB\nenergy\nregisters"), (7.05, "16 MB flash\n1 min\nrecords"),
            (5.2, "status\nLEDs"), (3.1, "USB service\nport")]
    for y, t in side:
        box(ax, 15.5, y, 2.3, 1.55, t, fc="white", fontsize=6.7)
    for y, b in ((9.7, True), (7.8, True), (5.95, False)):
        line(ax, [(15.1, y), (15.5, y)], both=b, arrow_end=not b)
    line(ax, [(15.5, 3.85), (13.6, 3.85), (13.6, 5.2)], both=True)
    # power path
    box(ax, 4.4, 1.0, 6.7, 1.5, "AC/DC module 230 V → 5 V, 3 W\n(reinforced, straddles barrier)",
        fc="white", fontsize=6.9)
    box(ax, 11.5, 1.0, 2.6, 1.5, "buck\n5 V → 3.3 V", fc="white", fontsize=6.9)
    ax.text(0.3, 1.75, "L, N (own fuse)", fontsize=6.8, va="center")
    line(ax, [(3.2, 1.75), (4.4, 1.75)], arrow_end=True)
    line(ax, [(11.1, 1.75), (11.5, 1.75)], arrow_end=True)
    line(ax, [(12.8, 2.5), (12.8, 5.2)], arrow_end=True, color=GREEN)
    ax.text(12.7, 2.75, "3.3 V", fontsize=6.4, color=GREEN, ha="right")
    save(fig, "35", "fig-35-1-energy-monitor-architecture")


# ----------------------------------------------------------------------------
# Figure 35.2 — analog front end
# ----------------------------------------------------------------------------
def fig_35_2():
    fig, ax = plt.subplots(figsize=(6.8, 5.0))
    ax.axis("off")
    ax.set_aspect("equal")
    d = schemdraw.Drawing(canvas=ax, show=False)
    d.config(unit=2.0, fontsize=7.2, lw=1.0)

    def txt(x, y, t, ha="left", va="center", fs=7.0, color=INK, **kw):
        ax.text(x, y, t, ha=ha, va=va, fontsize=fs, color=color, **kw)

    YL, YN, Y0N = 13.5, 8.0, 11.5           # L line, N rail, AIN0N line
    YT, YC, YS = 6.0, 3.0, 0.0              # CT tip, centre tap, sleeve
    XA = 14.0                               # ADC left edge
    # ---------------- voltage channel ----------------
    d += elm.Dot(open=True).at((0, YL)).label("L", loc="left")
    d += elm.Fuse().right().at((0, YL)).to((2.6, YL)).label("F1\n0.5 A F", loc="top")
    d += elm.Dot().at((2.6, YL))
    d += elm.RBoxVar().down().at((2.6, YL)).to((2.6, YN)).label("MOV\n275 V a.c.", loc="top", ofst=0.15)
    d += elm.Dot().at((2.6, YN))
    d += elm.Resistor().right().at((2.6, YL)).to((4.4, YL)).label("330 k", loc="top")
    d += elm.Resistor().right().at((4.4, YL)).to((6.2, YL)).label("330 k", loc="top")
    d += elm.Resistor().right().at((6.2, YL)).to((8.0, YL)).label("330 k", loc="top")
    d += elm.Dot().at((8.0, YL))
    d += elm.Resistor().down().at((8.0, YL)).to((8.0, YN)).label("2.10 k", loc="top", ofst=0.15)
    d += elm.Dot().at((8.0, YN))
    d += elm.Resistor().right().at((8.0, YL)).to((10.6, YL)).label("1 k", loc="top")
    d += elm.Dot().at((11.6, YL))
    d += elm.Line().right().at((10.6, YL)).to((XA, YL))
    d += elm.Capacitor().down().at((11.6, YL)).to((11.6, Y0N)).label("4.7 nF\nC0G", loc="bottom",
                                                                       ofst=0.15)
    d += elm.Dot().at((11.6, Y0N))
    d += elm.Line().left().at((XA, Y0N)).to((10.4, Y0N))
    d += elm.Resistor().down().at((10.4, Y0N)).to((10.4, YN)).label("1 k", loc="top", ofst=0.15)
    d += elm.Dot().at((10.4, YN))
    d += elm.Dot(open=True).at((0, YN)).label("N", loc="left")
    d += elm.Line().right().at((0, YN)).to((10.4, YN))
    d += elm.Line().down().at((5.2, YN)).to((5.2, YN - 0.6))
    d += elm.Ground().at((5.2, YN - 0.6))
    txt(4.9, YN - 0.75, "N = mains-side ground", fs=6.4, color=GREY, ha="right")
    # ---------------- CT channel ----------------
    d += elm.SourceI().up().at((0.0, YS)).to((0.0, YT)).label("CT\n2000 : 1", loc="top", ofst=0.2)
    d += elm.Line().right().at((0.0, YT)).to((1.6, YT))
    d += elm.Line().right().at((0.0, YS)).to((1.6, YS))
    d += elm.Dot(open=True).at((1.6, YT))
    d += elm.Dot(open=True).at((1.6, YS))
    txt(1.6, YS - 0.5, "J1 3.5 mm jack", ha="center", va="top", fs=6.4)
    d += elm.Line().right().at((1.6, YT)).to((7.6, YT))
    d += elm.Line().right().at((1.6, YS)).to((7.6, YS))
    d += elm.Dot().at((3.4, YT))
    d += elm.Dot().at((3.4, YS))
    d += elm.DiodeTVS().down().at((3.4, YT)).to((3.4, YS)).label("TVS\n5 V\nbidir.", loc="bottom",
                                                                  ofst=0.15)
    d += elm.Dot().at((6.2, YT))
    d += elm.Dot().at((6.2, YS))
    d += elm.Resistor().down().at((6.2, YT)).to((6.2, YC)).label("4.99 Ω", loc="top", ofst=0.15)
    d += elm.Resistor().down().at((6.2, YC)).to((6.2, YS)).label("4.99 Ω", loc="top", ofst=0.15)
    d += elm.Dot().at((6.2, YC))
    d += elm.Line().right().at((6.2, YC)).to((7.0, YC))
    d += elm.Line().down().at((7.0, YC)).to((7.0, YC - 0.5))
    d += elm.Ground().at((7.0, YC - 0.5))
    txt(7.3, YC + 0.1, "centre tap to\nCM reference", fs=6.2, color=GREY)
    d += elm.Resistor().right().at((7.6, YT)).to((10.2, YT)).label("1 k", loc="top")
    d += elm.Resistor().right().at((7.6, YS)).to((10.2, YS)).label("1 k", loc="bottom")
    d += elm.Line().right().at((10.2, YT)).to((XA, YT))
    d += elm.Line().right().at((10.2, YS)).to((XA, YS))
    d += elm.Dot().at((11.6, YT))
    d += elm.Dot().at((11.6, YS))
    d += elm.Capacitor().down().at((11.6, YT)).to((11.6, YS)).label("4.7 nF\nC0G", loc="bottom",
                                                                      ofst=0.15)
    txt(6.2, YT + 0.35, "burden 9.98 Ω", fs=6.4, color=GREY, ha="center", va="bottom")
    d.draw()

    # ---------------- ADC and isolators (drawn as boxes) ----------------
    X1, Yb, Yt = 17.8, -1.2, 14.6
    ax.add_patch(Rectangle((XA, Yb), X1 - XA, Yt - Yb, fc="#FFF6EC", ec=INK, lw=1.2, zorder=3))
    txt((XA + X1) / 2, 2.3, "ADS131M04\n4-ch ΔΣ\n24-bit", ha="center", fs=7.6, zorder=4)
    for y, n in ((YL, "AIN0P"), (Y0N, "AIN0N"), (YT, "AIN1P"), (YS, "AIN1N")):
        txt(XA + 0.15, y, n, fs=6.4, zorder=4)
    txt(XA + 0.15, 4.3, "AIN2, AIN3:\nPV, EV CTs\n(identical)", fs=5.8, color=GREY, zorder=4)
    right = [(12.6, "SCLK"), (11.6, "CS"), (10.6, "DIN"), (9.6, "DOUT"), (7.6, "DRDY")]
    XI = 19.9
    for y, n in right:
        txt(X1 - 0.15, y, n, ha="right", fs=6.4, zorder=4)
        ax.plot([X1, XI], [y, y], color=INK, lw=1.0)
        if n in ("DOUT", "DRDY"):
            ax.annotate("", xy=(XI, y), xytext=(XI - 0.8, y),
                        arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.0, mutation_scale=8))
        else:
            ax.annotate("", xy=(X1, y), xytext=(X1 + 0.8, y),
                        arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.0, mutation_scale=8))
    # isolator symbols at right edge
    for (y0, y1, name) in ((9.1, 13.4, "ISOW7741"), (6.5, 8.0, "ISO7710")):
        ax.add_patch(Rectangle((XI, y0), 1.8, y1 - y0, fc="white", ec=INK, lw=1.0, zorder=3))
        ax.plot([XI + 0.82, XI + 0.82], [y0 + 0.1, y1 - 0.1], color=RED, lw=1.0, zorder=4)
        ax.plot([XI + 0.98, XI + 0.98], [y0 + 0.1, y1 - 0.1], color=RED, lw=1.0, zorder=4)
        txt(XI + 0.9, y0 - 0.15, name, ha="center", va="top", fs=6.4)
    txt(XI + 1.95, 11.3, "to\nESP32-S3\n(SELV)", fs=6.2, color=GREY)
    # supply: isolated 3.3 V via ferrite bead to AVDD / DVDD
    d2 = schemdraw.Drawing(canvas=ax, show=False)
    d2.config(unit=2.0, fontsize=6.8, lw=1.0)
    d2 += elm.Line().up().at((15.0, Yt)).to((15.0, 15.6))
    d2 += elm.Line().up().at((16.4, Yt)).to((16.4, 15.6))
    d2 += elm.Line().right().at((15.0, 15.6)).to((16.4, 15.6))
    d2 += elm.Dot().at((16.4, 15.6))
    d2 += elm.RBox().right().at((16.4, 15.6)).to((19.0, 15.6)).label("FB", loc="top")
    d2 += elm.Line().right().at((19.0, 15.6)).to((21.3, 15.6))
    d2 += elm.Line().down().at((21.3, 15.6)).to((21.3, 13.4))
    # oscillator on CLKIN
    d2 += elm.Line().down().at((15.6, Yb)).to((15.6, -2.2))
    d2.draw()
    txt(15.0, Yt - 0.2, "AVDD", ha="center", va="top", fs=6.0, zorder=4)
    txt(16.4, Yt - 0.2, "DVDD", ha="center", va="top", fs=6.0, zorder=4)
    txt(21.45, 14.5, "isolated\n3.3 V", fs=6.2, color=GREEN)
    txt(15.75, Yb + 0.2, "CLKIN", ha="left", va="bottom", fs=6.0, zorder=4)
    ax.add_patch(Rectangle((14.1, -3.4), 3.0, 1.2, fc="white", ec=INK, lw=1.0, zorder=3))
    txt(15.6, -2.8, "8.192 MHz\nosc.", ha="center", fs=6.4, zorder=4)
    # annotations
    txt(12.9, YL + 0.75, "0.487 V rms\nat 230 V", fs=6.4, color=BLUE, ha="center")
    txt(12.9, YT + 0.75, "0.314 V rms\nat 63 A", fs=6.4, color=BLUE, ha="center")
    ax.set_xlim(-2.6, 23.4)
    ax.set_ylim(-3.8, 16.4)
    save(fig, "35", "fig-35-2-front-end-schematic")


# ----------------------------------------------------------------------------
# Figure 35.3 — distorted load waveforms (model of Section 35.3)
# ----------------------------------------------------------------------------
FS, F0 = 4000.0, 49.8
HARM = {1: (4.0, -60), 3: (1.6, -150), 5: (1.0, 120), 7: (0.48, 20)}


def fig_35_3():
    t = np.arange(0, 4.0, 1 / FS)
    w = 2 * np.pi * F0

    def volt(t):
        return 230 * np.sqrt(2) * (np.sin(w * t) + 0.03 * np.sin(5 * w * t))

    def curr(t, only=None):
        return sum(a * np.sqrt(2) * np.sin(h * w * t + np.radians(ph))
                   for h, (a, ph) in HARM.items() if only is None or h == only)

    v, i = volt(t), curr(t)
    zc = np.flatnonzero((v[:-1] < 0) & (v[1:] >= 0))
    n = zc[10] - zc[0]
    p = np.mean(v[:n] * i[:n])
    vr, ir = np.sqrt(np.mean(v[:n]**2)), np.sqrt(np.mean(i[:n]**2))
    k = np.arange(n)
    e = np.exp(-2j * np.pi * F0 * k / FS)
    s1 = (2 * np.mean(v[:n] * e) / np.sqrt(2)) * np.conj(2 * np.mean(i[:n] * e) / np.sqrt(2))
    # fine time grid for drawing, 0..40 ms
    tf = np.linspace(0, 0.040, 4001)
    vf, i_f = volt(tf), curr(tf)
    pf = vf * i_f
    print(f"  P={p:.2f} S={vr * ir:.1f} PF={p / vr / ir:.3f} P1={s1.real:.1f} Q1={s1.imag:.1f}"
          f" Ipk={abs(i_f).max():.2f} Vpk={vf.max():.1f} pmin={pf.min():.0f} pmax={pf.max():.0f}")
    ms = tf * 1e3
    fig, axs = plt.subplots(3, 1, figsize=(6.6, 5.6), sharex=True,
                            gridspec_kw=dict(hspace=0.12))
    zx = [x * 1e3 for x in np.arange(0, 0.041, 1 / F0)]
    for a in axs:
        for z in zx:
            a.axvline(z, color=GREY, lw=0.8, ls=(0, (2, 2)), zorder=0)
        a.axhline(0, color=INK, lw=0.6)
    ax = axs[0]
    ax.plot(ms, vf, color=BLUE)
    ax.plot(ms, 325.3 * np.sin(w * tf), color=BLUE, lw=0.8, ls="--", alpha=0.6)
    ax.set_ylabel("$v$ (V)")
    ax.set_ylim(-400, 400)
    ax.text(5.4, 345, f"325 V peak fundamental (dashed); with 3 % 5th harmonic {vf.max():.0f} V",
            fontsize=7.6, va="bottom", color=BLUE)
    ax = axs[1]
    ax.plot(ms, i_f, color=ORANGE, label="current $i$ (4.45 A rms)")
    ax.plot(ms, curr(tf, 1), color=ORANGE, lw=0.9, ls="--", label="fundamental, lagging 60°")
    ax.set_ylabel("$i$ (A)")
    ax.set_ylim(-9, 11.5)
    ax.legend(loc="upper center", fontsize=7.6, ncol=2)
    kpk = np.argmax(abs(i_f))
    ax.annotate(f"{abs(i_f[kpk]):.1f} A peak", (ms[kpk], i_f[kpk]), xytext=(8, 4),
                textcoords="offset points", fontsize=7.8, color=ORANGE)
    ax = axs[2]
    ax.fill_between(ms, pf / 1e3, 0, where=pf < 0, color=RED, alpha=0.25, lw=0,
                    label="power flowing back")
    ax.plot(ms, pf / 1e3, color=GREEN, lw=1.4, label="$p = v\\,i$")
    ax.axhline(p / 1e3, color=INK, lw=1.2, ls="--")
    ax.text(40.5, p / 1e3, f"mean\n{p:.2f} W", fontsize=7.6, va="center", ha="left")
    ax.set_ylabel("$p$ (kW)")
    ax.set_ylim(-1.5, 2.3)
    ax.set_xlabel("Time (ms) at 49.8 Hz; dotted verticals = rising voltage zero crossings")
    ax.set_xlim(0, 40)
    ax.legend(loc="upper left", fontsize=7.6, ncol=2)
    fig.text(0.5, 0.905, f"10-cycle window values:  P {p:.2f} W   S {vr * ir:.0f} VA   "
             f"PF {p / vr / ir:.3f}   P$_1$ {s1.real:.1f} W   Q$_1$ {s1.imag:.1f} var",
             fontsize=8, ha="center", va="bottom", bbox=dict(fc="white", ec=GREY, lw=0.6, pad=2.5))
    axs[0].annotate("10-cycle window\nboundary", (0, -330), xytext=(1.0, -330), fontsize=7,
                    color=GREY, va="center")
    save(fig, "35", "fig-35-3-distorted-load-waveforms")


# ----------------------------------------------------------------------------
# Figure 35.4 — calibration error vs current (model of Section 35.7)
# ----------------------------------------------------------------------------
def ct(i):
    return -0.005 - 0.015 * np.exp(-i / 1.0), np.radians(0.6 + 2.4 * np.exp(-i / 1.5))


def meter_s(i, phi, k_gain=1.0, delta=0.0, v=230.0):
    eps, lead = ct(i)
    s_m = v * i * (1.003 + eps) * np.exp(1j * (phi - lead))
    return k_gain * s_m * np.exp(1j * delta)


PHI_05 = np.arccos(0.5)


def calibrate(cal_i):
    cal_i = np.asarray(cal_i, float)
    k_tab = np.array([230 * i / abs(meter_s(i, 0.0)) for i in cal_i])
    d_tab = np.empty(cal_i.size)
    for n, i in enumerate(cal_i):
        e = meter_s(i, PHI_05, k_tab[n]).real / (230 * i * 0.5) - 1
        d_tab[n] = PHI_05 - np.arccos((1 + e) * 0.5)

    def corrected(i, phi):
        x = np.log(np.clip(i, cal_i[0], cal_i[-1]))
        return meter_s(i, phi, np.interp(x, np.log(cal_i), k_tab),
                       np.interp(x, np.log(cal_i), d_tab)).real
    return corrected


def fig_35_4():
    pts = {"PF 1": (0.0, BLUE), "PF 0.5L": (PHI_05, ORANGE), "PF 0.8C": (-np.arccos(0.8), GREEN)}
    c4 = calibrate([0.5, 2, 10, 40])
    c5 = calibrate([0.5, 2, 5, 10, 40])
    I = np.logspace(np.log10(0.3), np.log10(70), 600)
    fig, ax = plt.subplots(figsize=(6.8, 4.6))
    # class 1 limits (IEC 62053-21, Ib = 10 A)
    lim_pf1_x, lim_pf1_y = [0.5, 1.0, 1.0, 63], [1.5, 1.5, 1.0, 1.0]
    lim_lo_x, lim_lo_y = [1.0, 2.0, 2.0, 63], [1.5, 1.5, 1.0, 1.0]
    for sgn in (1, -1):
        ax.plot(lim_pf1_x, [sgn * y for y in lim_pf1_y], color="#555555", lw=1.6, zorder=1)
        ax.plot(lim_lo_x, [sgn * y for y in lim_lo_y], color="#999999", lw=1.6, ls=(0, (5, 2)),
                zorder=1)
    ax.text(0.52, 1.62, "class 1, PF 1", fontsize=7.4, color="#555555", va="bottom")
    ax.text(2.1, 1.1, "class 1, PF 0.5L / 0.8C (dashed, from 0.1 $I_b$)", fontsize=7.4,
            color="#888888", va="bottom")
    ax.annotate("4-point: −0.51 % near 4.4 A, PF 0.5L", (4.4, -0.51), xytext=(9, -0.62), fontsize=7.2,
                color=ORANGE, va="center", arrowprops=dict(arrowstyle="-", color=ORANGE, lw=0.7))
    ax.annotate("+0.32 % at 5 A, PF 0.8C", (5, 0.32), xytext=(9, 0.55), fontsize=7.2,
                color=GREEN, va="center", arrowprops=dict(arrowstyle="-", color=GREEN, lw=0.7))
    worst4, worst5 = 0, 0
    for name, (phi, c) in pts.items():
        ref = 230 * I * np.cos(phi)
        raw = 100 * (meter_s(I, phi).real / ref - 1)
        e4 = 100 * (c4(I, phi) / ref - 1)
        e5 = 100 * (c5(I, phi) / ref - 1)
        m = (I >= 0.5) & (I <= 63)
        worst4 = max(worst4, abs(e4[m]).max())
        worst5 = max(worst5, abs(e5[m]).max())
        ax.plot(I, raw, color=c, ls="--", lw=1.3)
        ax.plot(I[m], e4[m], color=c, lw=0.9)
        ax.plot(I[m], e5[m], color=c, lw=2.4, alpha=0.85)
        ly = {"PF 1": -1.45, "PF 0.5L": 5.25, "PF 0.8C": -4.95}[name]
        ax.text(0.31, ly, f"{name} raw", color=c, fontsize=7.8, va="top")
        k5 = np.argmin(abs(I - 5))
        print(f"  {name}: raw {raw[np.argmin(abs(I - 0.5))]:+.2f}..{raw[np.argmin(abs(I - 63))]:+.2f}"
              f" 4pt@5A {e4[k5]:+.2f}  5pt max {abs(e5[m]).max():.3f}")
    print(f"  worst 4-pt {worst4:.2f}, worst 5-pt {worst5:.3f}")
    for ci in (0.5, 2, 5, 10, 40):
        ax.plot(ci, -5.75, marker="^", color=INK if ci != 5 else RED, ms=6, clip_on=False)
    ax.text(40, -5.35, "calibration currents\n(red: 5th point)", fontsize=7.2, ha="center",
            va="bottom")
    from matplotlib.lines import Line2D
    hs = [Line2D([], [], color=INK, ls="--", lw=1.3), Line2D([], [], color=INK, lw=0.9),
          Line2D([], [], color=INK, lw=2.4)]
    ax.legend(hs, ["before calibration", "4-point calibration", "5-point calibration"],
              loc="upper right", fontsize=7.8)
    ax.set_xscale("log")
    ax.set_xlim(0.3, 70)
    ax.set_ylim(-6, 6)
    ax.set_xticks([0.3, 0.5, 1, 2, 5, 10, 20, 40, 63])
    ax.set_xticklabels(["0.3", "0.5", "1", "2", "5", "10", "20", "40", "63"])
    ax.set_xlabel("Current (A), log scale; $I_b$ = 10 A, $I_{max}$ = 63 A")
    ax.set_ylabel("Active-energy error (%)")
    ax.axhline(0, color=INK, lw=0.6)
    save(fig, "35", "fig-35-4-calibration-error-vs-current")


# ----------------------------------------------------------------------------
# Figure 35.5 — isolation layout
# ----------------------------------------------------------------------------
def fig_35_5():
    fig, ax = schematic(6.8, 5.3, xlim=(-5, 85), ylim=(-9, 66))
    PCB, CU = "#E3EFE3", "#B87333"
    ax.add_patch(Rectangle((0, 0), 80, 60, fc=PCB, ec=INK, lw=1.4))
    # mains / SELV tint
    ax.add_patch(Rectangle((0, 0), 31, 60, fc=tint(ORANGE, "18"), ec="none"))
    # copper keep-out band, 8 mm centred on the barrier
    ax.add_patch(Rectangle((28, 0), 8, 60, fc="none", ec=RED, lw=0.0, hatch="///", alpha=0.45))
    ax.plot([28, 28], [0, 60], color=RED, lw=0.6, ls=(0, (3, 2)))
    ax.plot([36, 36], [0, 60], color=RED, lw=0.6, ls=(0, (3, 2)))
    # routed slot at x = 31..33, interrupted only under the isolators
    for y0, y1 in ((0, 23.4), (30.4, 35.4), (46.9, 60)):
        ax.add_patch(Rectangle((31, y0), 2, y1 - y0, fc="white", ec=INK, lw=0.8, zorder=3))

    def part(x, y, w, h, label, fc="#2B2B2B", tc="white", fs=6.4, z=4, **kw):
        ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec=INK, lw=0.8, zorder=z))
        if label:
            ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=fs, color=tc,
                    zorder=z + 1, **kw)

    def soic(xc, y0, body_h, npin, name):
        """Wide-body SOIC straddling the slot: body 7.5 mm, leads to 10.3 mm span."""
        part(xc - 3.75, y0, 7.5, body_h, name, fs=5.6, z=6, rotation=90)
        pitch = 1.27
        for k in range(npin // 2):
            yy = y0 + body_h / 2 + (k - (npin // 2 - 1) / 2) * pitch - 0.3
            for xl in (xc - 5.15, xc + 3.75):
                ax.add_patch(Rectangle((xl, yy), 1.4, 0.6, fc="#BBBBBB", ec="#666666", lw=0.4,
                                       zorder=6))
    # isolators
    soic(32, 35.9, 10.5, 16, "ISOW7741")
    soic(32, 23.9, 6.0, 8, "ISO7710")
    # AC/DC module straddling the barrier (slot continues beneath)
    part(23, 4, 18, 12, "", fc="#3C3C3C", fs=6.2, z=5)
    ax.text(32, 10, "AC/DC 230 V → 5 V\n3 W, reinforced", ha="center", va="center", fontsize=6.2,
            color="white", zorder=8, bbox=dict(fc="#3C3C3C", ec="none", pad=0.5))
    ax.add_patch(Rectangle((31, 4), 2, 12, fc="none", ec="white", lw=0.8, ls=(0, (2, 2)), zorder=6))
    # mains side
    part(1, 51, 12, 8, "L      N", fc="#2E7D32", fs=7.5)
    ax.text(7, 50.3, "terminal block", ha="center", va="top", fontsize=6.0)
    part(14.2, 54, 5, 3, "F1", fc="#DDDDDD", tc=INK, fs=6.0)
    ax.add_patch(Circle((22.4, 54.5), 2.3, fc="#1565C0", ec=INK, lw=0.8, zorder=4))
    ax.text(22.4, 54.5, "MOV", ha="center", va="center", fontsize=5.6, color="white", zorder=5)
    for k, x in enumerate((2.0, 8.6, 15.2)):
        part(x, 43, 3.6, 1.6, "", fc="#7FA7C9")
        ax.text(x + 1.8, 45.2, "330 k", ha="center", va="bottom", fontsize=5.6)
    ax.annotate("", xy=(8.6, 42.3), xytext=(5.6, 42.3),
                arrowprops=dict(arrowstyle="<|-|>", lw=0.7, color=INK, mutation_scale=6,
                                shrinkA=0, shrinkB=0))
    ax.text(7.1, 41.8, "3 mm", ha="center", va="top", fontsize=5.6)
    part(20.5, 43.2, 1.6, 1.2, "", fc="#7FA7C9")
    ax.text(22.6, 43.8, "2.10 k", ha="left", va="center", fontsize=5.4)
    part(11, 26, 10, 4.4, "ADS131M04", fs=5.6)
    part(4, 27, 3.2, 2.5, "", fc="#9E9E9E")
    ax.text(5.6, 26.4, "8.192 MHz", ha="center", va="top", fontsize=5.4)
    part(3, 14, 18, 6, "CT burdens +\nanti-alias RC (C0G)", fc="#F5F5F5", tc=INK, fs=5.6)
    for k, x in enumerate((1.0, 8.0, 15.0)):
        part(x, -2.0, 6, 8, f"CT{k + 1}", fc="#424242", fs=5.8)
    ax.text(11, -3.0, "CT jacks (3.5 mm)", ha="center", va="top", fontsize=6.2)
    # SELV side
    part(54.5, 32, 25.5, 18, "ESP32-S3 module", fc="#546E7A", fs=6.6)
    ax.add_patch(Rectangle((74, 32), 6, 18, fc="none", ec="white", lw=0.8, hatch="xx", zorder=5))
    ax.text(77, 51, "antenna", ha="center", va="bottom", fontsize=5.8)
    part(43, 40, 5, 4, "FRAM", fs=5.4)
    part(44, 21, 6, 5, "buck\n3.3 V", fs=5.4)
    part(58, -1.5, 9, 7, "USB", fc="#9E9E9E", tc=INK, fs=6.0)
    for k in range(3):
        ax.add_patch(Circle((70 + 3 * k, 6), 1.0, fc=[GREEN, YELLOW, RED][k], ec=INK, lw=0.5,
                            zorder=4))
    ax.text(73, 8.2, "status LEDs", ha="center", va="bottom", fontsize=5.6)
    # dimensions
    def dim(x0, x1, y, text, above=True):
        ax.annotate("", xy=(x1, y), xytext=(x0, y),
                    arrowprops=dict(arrowstyle="<|-|>", lw=0.9, color=INK, mutation_scale=7,
                                    shrinkA=0, shrinkB=0), zorder=8)
        ax.text((x0 + x1) / 2, y + (0.6 if above else -0.6), text, ha="center",
                va="bottom" if above else "top", fontsize=6.4, zorder=8,
                bbox=dict(fc="white", ec="none", pad=0.4, alpha=0.9))
    dim(28, 36, 19.5, "clearance 8.0 mm")
    dim(28, 36, 49.2, "creepage 8.0 mm")
    dim(0, 80, -6.5, "80 mm", above=False)
    ax.annotate("", xy=(-2.5, 60), xytext=(-2.5, 0),
                arrowprops=dict(arrowstyle="<|-|>", lw=0.9, color=INK, mutation_scale=7,
                                shrinkA=0, shrinkB=0))
    ax.text(-3.2, 30, "60 mm", rotation=90, ha="right", va="center", fontsize=6.4)
    # labels
    ax.text(15, 62.2, "MAINS SIDE", ha="center", va="bottom", fontsize=7.2, weight="bold",
            color="#8A3B12")
    ax.text(58, 62.2, "SELV SIDE", ha="center", va="bottom", fontsize=7.2, weight="bold",
            color="#1D4F7A")
    ax.text(32, 62.2, "CAT III 300 V\nreinforced", ha="center", va="bottom", fontsize=6.6,
            color=RED, weight="bold")
    ax.annotate("routed slot 2 mm\nat x = 32 mm", xy=(33, 33), xytext=(40, 29.5), fontsize=6.0,
                ha="left", va="center", arrowprops=dict(arrowstyle="-", lw=0.6, color=INK), zorder=8)
    ax.annotate("copper keep-out,\nall layers", xy=(35.3, 17.6), xytext=(44, 16.6), fontsize=6.0,
                ha="left", va="center", color=RED,
                arrowprops=dict(arrowstyle="-", lw=0.6, color=RED), zorder=8)
    save(fig, "35", "fig-35-5-isolation-layout")


# ----------------------------------------------------------------------------
# Figure 35.6 — field comparison
# ----------------------------------------------------------------------------
def fig_35_6():
    rng = np.random.default_rng(35)
    day = np.arange(1, 61)
    e_imp = np.clip(19 + 6 * np.sin(2 * np.pi * day / 9.0) + rng.normal(0, 3.5, 60), 8, 32)
    e_exp = np.clip(9 + 4 * np.cos(2 * np.pi * day / 7.0) + rng.normal(0, 3.5, 60), 0.4, 18)
    d_imp = rng.normal(0, 0.38, 60)
    d_imp = np.clip(d_imp - d_imp.mean(), -0.95, 0.85)
    d_imp += 0.18 - d_imp.mean()
    low = e_exp < 2.0
    d_exp = rng.normal(0, 0.38, 60) * np.where(low, 1.8, 1.0)
    d_exp = np.clip(d_exp, -0.8, 0.9)
    d_exp += -0.21 - d_exp.mean()
    print(f"  imp {d_imp.min():.2f}..{d_imp.max():.2f} mean {d_imp.mean():.2f}; exp {d_exp.min():.2f}"
          f"..{d_exp.max():.2f} mean {d_exp.mean():.2f}; low-export days {low.sum()}")
    fig, ax = plt.subplots(figsize=(6.8, 4.0))
    a2 = ax.twinx()
    a2.spines["right"].set_visible(True)
    a2.bar(day, e_imp, color="#E6ECF2", width=0.8, zorder=0)
    a2.set_ylim(0, 80)
    a2.set_yticks([0, 8, 16, 24, 32])
    a2.set_ylabel("Daily import energy (kWh), bars", color=GREY)
    a2.tick_params(axis="y", colors=GREY)
    ax.set_zorder(a2.get_zorder() + 1)
    ax.patch.set_visible(False)
    ax.axhspan(-1, 1, color="#E8E8E8", alpha=0.6, lw=0, zorder=0)
    ax.axhline(0, color=INK, lw=0.6)
    ax.plot(day, d_imp, "o", color=BLUE, ms=4.5, label=f"import, mean {d_imp.mean():+.2f} %")
    ax.plot(day[~low], d_exp[~low], "o", color=ORANGE, ms=4.5,
            label=f"export, mean {d_exp.mean():+.2f} %")
    ax.plot(day[low], d_exp[low], "o", mfc="white", mec=ORANGE, mew=1.3, ms=4.5,
            label="export day < 2 kWh")
    ax.axhline(d_imp.mean(), color=BLUE, lw=1, ls="--")
    ax.axhline(d_exp.mean(), color=ORANGE, lw=1, ls="--")
    ax.plot(-1.5, 1.85, "D", color=RED, ms=6, clip_on=False)
    ax.annotate("prototype before redesign:\n+4 % monthly (off scale)", (-1.5, 1.85), xytext=(3, 1.6),
                fontsize=7.6, color=RED, va="center",
                arrowprops=dict(arrowstyle="-", color=RED, lw=0.8))
    ax.text(60.5, 1.0, "±1 %", fontsize=7.6, color=GREY, va="bottom", ha="right")
    ax.set_xlim(-3, 61)
    ax.set_ylim(-2, 2)
    ax.set_xlabel("Day")
    ax.set_ylabel("Monitor − billing meter (%)")
    ax.legend(loc="lower left", fontsize=7.6, ncol=3, bbox_to_anchor=(0.0, -0.01))
    save(fig, "35", "fig-35-6-field-comparison")


if __name__ == "__main__":
    _only = sys.argv[1:]
    for _f in (fig_35_1, fig_35_2, fig_35_3, fig_35_4, fig_35_5, fig_35_6):
        if not _only or _f.__name__[-1] in _only:
            _f()
