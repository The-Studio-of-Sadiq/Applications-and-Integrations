"""Figures for Chapter 29 — Engineering Software Workflows.

Run from the repository root:  python figures/scripts/ch29.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle  # noqa: E402
from scipy import signal  # noqa: E402
from scipy.optimize import brentq  # noqa: E402

from figstyle import COLORS, INK, box, save, schematic  # noqa: E402

BLUE, ORANGE, GREEN, PINK, YELLOW, SKY = COLORS[:6]
RED = "#C62828"
GREY = "#777777"


def tint(c, a="30"):
    return c + a


def line(ax, pts, color=INK, lw=1.1, ls="-", arrow_end=True):
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
# Models from the chapter (Listings: losses.py and loop.py)
# ----------------------------------------------------------------------------
P = dict(vin=48.0, vo=12.0, fsw=200e3, L=6.8e-6, dcr=3e-3, esr=5e-3, c_out=470e-6,
         rds25=7e-3, k_t=1.6, t_sw=8e-9, qoss=50e-9, qrr=40e-9, qg=35e-9,
         v_drv=10.0, t_dead=20e-9, vf=0.8, p_core=0.25, p_bias=0.10)


def losses(io, p=P):
    d = p["vo"] / p["vin"]
    di = (p["vin"] - p["vo"]) * d / (p["fsw"] * p["L"])
    r2 = (di / io) ** 2 / 12
    rds = p["rds25"] * p["k_t"]
    return {
        "cond_hs": io**2 * d * (1 + r2) * rds,
        "cond_ls": io**2 * (1 - d) * (1 + r2) * rds,
        "switching": 0.5 * p["vin"] * p["fsw"] * p["t_sw"] * (2 * io),
        "coss": 0.5 * p["qoss"] * p["vin"] * p["fsw"],
        "qrr": p["qrr"] * p["vin"] * p["fsw"],
        "dead_time": p["vf"] * io * 2 * p["t_dead"] * p["fsw"],
        "gate": 2 * p["qg"] * p["v_drv"] * p["fsw"],
        "inductor": (io**2 + di**2 / 12) * p["dcr"] + p["p_core"],
        "cap_esr": di**2 / 12 * p["esr"],
        "bias": p["p_bias"],
    }


def efficiency(io, p=P):
    po = p["vo"] * io
    return po / (po + sum(losses(io, p).values()))


Lf, Cf, ESR, DCR = 6.8e-6, 470e-6, 5e-3, 3e-3
VIN, VRAMP, HDIV = 48.0, 4.8, 0.1
W0 = 1 / np.sqrt(Lf * Cf)


def plant(io):
    R = 12.0 / io
    den = [Lf * Cf * (1 + ESR / R), Lf / R + Cf * (ESR + DCR) + Cf * ESR * DCR / R, 1 + DCR / R]
    return np.array([VIN * Cf * ESR, VIN]), np.array(den)


ZOL = (np.polymul([Lf, DCR], [Cf * ESR, 1]), np.array([Lf * Cf, Cf * (ESR + DCR), 1]))


def loop_gain(k, io):
    gn, gd = plant(io)
    wz1, wz2, wp1, wp2 = 0.8 * W0, W0, 1 / (ESR * Cf), 2 * np.pi * 100e3
    nc = k * np.polymul([1 / wz1, 1], [1 / wz2, 1])
    dc = np.polymul([1, 0], np.polymul([1 / wp1, 1], [1 / wp2, 1]))
    return np.polymul(nc, gn) * HDIV / VRAMP, np.polymul(dc, gd)


def T_at(f, k, io=10.0):
    n, d = loop_gain(k, io)
    s = 2j * np.pi * np.asarray(f)
    return np.polyval(n, s) / np.polyval(d, s)


K = 1 / abs(T_at(20e3, 1.0))


# ----------------------------------------------------------------------------
# Figure 29.1 — workflow pipeline
# ----------------------------------------------------------------------------
def fig_29_1():
    fig, ax = schematic(6.8, 5.0, xlim=(0, 19.5), ylim=(-0.7, 13.65))
    top, bot = 11.9, 2.2

    # Git repository column
    ax.add_patch(FancyBboxPatch((0.15, bot), 4.5, top - bot,
                                boxstyle="round,pad=0.02,rounding_size=0.2",
                                fc="#F4F4F4", ec=INK, lw=1.1))
    ax.text(2.4, top - 0.45, "Git repository", ha="center", va="center", fontsize=9,
            weight="bold")
    repo = [("requirements.toml", "R1–R5, W1–W5 as data"),
            ("model/", "losses.py, loop.py"),
            ("spice/ + models/", "netlists; vendor\nmodels + SHA-256"),
            ("tests/", "unit, property,\nregression and\nrequirement"),
            ("data/manifest", "SHA-256 of raw\ncaptures (files in\nobject storage)"),
            ("docs/", "report sources")]
    y = top - 0.95
    for name, sub in repo:
        h = 0.62 + 0.36 * (sub.count("\n") + 1)
        box(ax, 0.35, y - h, 4.15, h, fc="white")
        ax.text(0.5, y - 0.28, name, ha="left", va="center", fontsize=7.0, family="monospace",
                weight="bold")
        ax.text(0.5, y - 0.5 - (h - 0.5) / 2, sub, ha="left", va="center", fontsize=6.6,
                color="#444444", linespacing=1.15)
        y -= h + 0.12

    # build box
    bx0, bx1 = 5.3, 13.8
    ax.add_patch(FancyBboxPatch((bx0, bot + 1.3), bx1 - bx0, top - bot - 1.3,
                                boxstyle="round,pad=0.02,rounding_size=0.2",
                                fc=tint(BLUE, "12"), ec=BLUE, lw=1.2))
    ax.text(bx0 + 0.3, top - 0.45, "make all", ha="left", va="center", fontsize=9,
            weight="bold", family="monospace")
    ax.text(bx0 + 0.3, top - 1.05, "locally, or as the CI job on every push", ha="left",
            va="center", fontsize=7.0)
    box(ax, bx0 + 0.3, top - 3.05, bx1 - bx0 - 0.6, 1.55,
        "container image pinned by digest\nPython 3.12, numpy, scipy,\nngspice 44",
        fc="white", ec=BLUE, fontsize=7.0)

    stages1 = [("loss\nmodel", GREEN), ("averaged\nloop\nmodel", GREEN),
               ("SPICE\ncorners,\nparallel,\ncached", ORANGE),
               ("bench\ndata\nimport", PINK)]
    stages2 = [("comparison\n+ tests\n(pytest)", YELLOW), ("plots", SKY), ("report", SKY)]
    sw, sh = 1.75, 2.05
    gap1 = ((bx1 - bx0 - 0.5) - 4 * sw) / 3
    xs1 = [bx0 + 0.25 + i * (sw + gap1) for i in range(4)]
    y1 = 6.3
    for (t, c), x in zip(stages1, xs1):
        box(ax, x, y1, sw, sh, t, fc=tint(c, "40"), fontsize=6.8)
    for a, b in zip(xs1[:-1], xs1[1:]):
        line(ax, [(a + sw, y1 + sh / 2), (b, y1 + sh / 2)])
    xs2 = [xs1[0] + 0.5 + i * (sw + 0.75) for i in range(3)]
    y2 = 3.7
    for (t, c), x in zip(stages2, xs2):
        box(ax, x, y2, sw, sh, t, fc=tint(c, "40"), fontsize=6.8)
    for a, b in zip(xs2[:-1], xs2[1:]):
        line(ax, [(a + sw, y2 + sh / 2), (b, y2 + sh / 2)])
    xr = xs1[-1] + sw / 2
    line(ax, [(xr, y1), (xr, 5.95), (xs2[0] + sw / 2, 5.95), (xs2[0] + sw / 2, y2 + sh)])

    # repository -> build
    line(ax, [(4.65, y1 + sh / 2), (bx0, y1 + sh / 2)], lw=1.4)
    ax.text(4.97, y1 + sh / 2 + 0.2, "checkout", ha="center", va="bottom", fontsize=6.8,
            rotation=90)

    # results column
    rx, rw = 14.3, 5.05
    ax.add_patch(FancyBboxPatch((rx, bot + 1.3), rw, top - bot - 1.3,
                                boxstyle="round,pad=0.02,rounding_size=0.2",
                                fc="#F4F4F4", ec=INK, lw=1.1))
    ax.text(rx + 0.3, top - 0.45, "results/", ha="left", va="center", fontsize=9,
            weight="bold", family="monospace")
    ax.text(rx + 0.3, top - 1.05, "generated, not committed", ha="left", va="center",
            fontsize=7.0, color="#444444")
    res = [("*.json + *.prov.json", "provenance record\nper result"),
           ("figures/", "generated from JSON"),
           ("report.pdf", "every number inserted\nfrom a result file"),
           ("traceability matrix", "requirement → tests\n→ status")]
    y = top - 1.5
    for name, sub in res:
        h = 1.45
        box(ax, rx + 0.15, y - h, rw - 0.3, h, fc="white")
        ax.text(rx + 0.3, y - 0.3, name, ha="left", va="center", fontsize=7.0,
                family="monospace", weight="bold")
        ax.text(rx + 0.3, y - 0.9, sub, ha="left", va="center", fontsize=6.6,
                color="#444444", linespacing=1.15)
        y -= h + 0.18
    ax.plot([xs2[-1] + sw, bx1], [y2 + sh / 2] * 2, color=INK, lw=1.4)
    line(ax, [(bx1, y2 + sh / 2), (rx, y2 + sh / 2)], lw=1.4)

    # tag -> release artifacts (top)
    box(ax, 0.4, 12.55, 3.2, 0.85, "git tag v1.2.0", fc=tint(GREEN, "40"), fontsize=8)
    box(ax, 14.95, 12.55, 3.6, 0.85, "release artifacts", fc=tint(GREEN, "40"), fontsize=8)
    line(ax, [(3.6, 12.97), (14.95, 12.97)], color=GREEN, lw=1.4)
    ax.text(9.3, 13.08, "W1: one command from tag to report", ha="center", va="bottom",
            fontsize=8.5, weight="bold", color="#1B6B4F")
    line(ax, [(16.75, top), (16.75, 12.55)], color=GREEN, lw=1.2)

    # developer and failure feedback
    box(ax, 0.4, -0.55, 4.0, 1.35, "developer", fc=tint(ORANGE, "30"), fontsize=8.5)
    line(ax, [(2.4, 0.8), (2.4, bot)], lw=1.2)
    ax.text(2.6, 1.5, "commit, push", ha="left", va="center", fontsize=7.0)
    fx = xs2[0] + sw / 2
    line(ax, [(fx, y2), (fx, 0.12), (4.4, 0.12)], color=RED, ls=(0, (4, 2.5)), lw=1.3)
    ax.text(fx + 0.2, 1.75, "test failures,\nregression diff", ha="left", va="center",
            fontsize=7.0, color=RED)
    ax.text(16.7, 1.4, "per-push pipeline 200 s (W2 ≤ 600 s)\n"
            "full corner campaign: nightly\nand on release tags",
            ha="center", va="center", fontsize=7.0, color="#444444", linespacing=1.25)
    save(fig, "29", "fig-29-1-workflow-pipeline")


# ----------------------------------------------------------------------------
# Figure 29.2 — SPICE switching waveforms
# ----------------------------------------------------------------------------
def _edge(t, t0, tr):
    return np.clip((t - t0) / tr, 0, 1)


def _waves(t):
    """Piecewise waveforms (t in us) built from the netlist timing and the 10 A operating point."""
    ton, toff, tls, T = 0.020, 1.240, 1.260, 5.0
    tr = 0.005
    gl = 10 * (1 - _edge(t, 0.0, tr)) + 10 * _edge(t, tls, tr) - 10 * _edge(t, T, tr)
    gh = 10 * _edge(t, ton, tr) - 10 * _edge(t, toff, tr)
    il_min, il_max = 6.69, 13.31
    il = np.where(t < ton, il_min,
                  np.where(t < toff, il_min + (il_max - il_min) * (t - ton) / (toff - ton),
                           il_max - (il_max - il_min) * (t - toff) / (T - toff)))
    rds = 7e-3 * 1.6
    sw = np.empty_like(t)
    on_hs = (t >= ton) & (t < toff)
    dead = ((t >= 0) & (t < ton)) | ((t >= toff) & (t < tls)) | (t >= T)
    sw[:] = -il * rds
    sw[dead] = -0.8
    # rise with ringing: 48 V plus damped oscillation, first overshoot to ~56 V
    tt = t[on_hs] - ton
    rise = np.clip(tt / 0.006, 0, 1)
    ring = 10.6 * np.exp(-tt / 0.022) * np.sin(2 * np.pi * 85.0 * np.clip(tt - 0.006, 0, None)
                                              + np.pi / 2) * (tt > 0.006)
    sw[on_hs] = -0.8 + (48.0 - il[on_hs] * rds + 0.8) * rise + ring
    # high-side drain current with reverse-recovery spike
    idh = np.zeros_like(t)
    tt = t[on_hs] - ton
    irr = 6.0 * np.where(tt < 0.008, tt / 0.008, np.exp(-(tt - 0.008) / 0.006))
    idh[on_hs] = il[on_hs] * np.clip(tt / 0.005, 0, 1) + irr
    return gl, gh, sw, il, idh


def fig_29_2():
    t = np.linspace(-0.05, 5.0, 60001)
    tz = np.linspace(-0.02, 0.14, 4001)
    W, Z = _waves(t), _waves(tz)
    fig, axs = plt.subplots(4, 2, figsize=(6.8, 5.6), sharex="col",
                            gridspec_kw=dict(width_ratios=[3.2, 1.25], hspace=0.18, wspace=0.28))
    labels = ["gate (V)", "$v_{sw}$ (V)", "$i_L$ (A)", "$i_{D,HS}$ (A)"]
    ylims = [(-1.5, 12.5), (-6, 62), (0, 16), (-1, 22)]
    for r in range(4):
        for c, (tv, wv) in enumerate([(t, W), (tz * 1e3, Z)]):
            a = axs[r, c]
            if r == 0:
                a.plot(tv, wv[0], color=BLUE, lw=1.3, label="gl (low side)")
                a.plot(tv, wv[1], color=ORANGE, lw=1.3, label="gh (high side, re sw)")
            else:
                a.plot(tv, wv[r + 1], color=[INK, GREEN, PINK][r - 1], lw=1.2)
            a.set_ylim(*ylims[r])
            # dead-time shading
            for t0, t1 in [(0, 0.02), (1.24, 1.26), (5.0, 5.02)]:
                if c == 0:
                    a.axvspan(t0, t1 + 0.012, color="#BBBBBB", alpha=0.6, lw=0)
                else:
                    a.axvspan(t0 * 1e3, t1 * 1e3, color="#BBBBBB", alpha=0.6, lw=0)
        axs[r, 0].set_ylabel(labels[r])
    axs[0, 0].legend(loc="upper right", fontsize=7.2, ncol=2, bbox_to_anchor=(1.0, 1.32))
    axs[0, 0].set_xlim(-0.05, 5.0)
    axs[0, 1].set_xlim(-20, 140)
    axs[3, 0].set_xlabel("time (µs)")
    axs[3, 1].set_xlabel("time (ns), turn-on")
    axs[0, 1].set_title("zoom: 0–140 ns", fontsize=8.5)
    # annotations
    a = axs[1, 0]
    a.annotate("−0.8 V body diode\n(dead time)", xy=(1.25, -0.8), xytext=(1.6, 22),
               fontsize=7, arrowprops=dict(arrowstyle="-", color=GREY, lw=0.8))
    a = axs[1, 1]
    a.annotate("≈ 56 V overshoot", xy=(31, 56.2), xytext=(55, 30), fontsize=7,
               arrowprops=dict(arrowstyle="-", color=GREY, lw=0.8))
    a.annotate("−0.8 V", xy=(12, -0.8), xytext=(-19, 30), fontsize=7,
               arrowprops=dict(arrowstyle="-", color=GREY, lw=0.8))
    a = axs[2, 0]
    a.axhline(10, color=GREY, ls=":", lw=0.9)
    a.text(3.2, 10.6, "average 10 A", fontsize=7, color=GREY)
    a.text(1.27, 14.0, "13.31 A", fontsize=7)
    a.text(0.05, 4.3, "6.69 A", fontsize=7)
    a = axs[3, 1]
    a.annotate("reverse recovery\n≈ 6 A spike", xy=(28, 12.6), xytext=(50, 15), fontsize=7,
               arrowprops=dict(arrowstyle="-", color=GREY, lw=0.8))
    axs[0, 0].text(1.30, 4.5, "dead time 20 ns (shaded)", fontsize=7, color="#555555")
    axs[2, 0].text(1.45, 1.2, ".meas: eff = 96.9 %, vout ripple 41 mV p-p",
                   fontsize=7.6, bbox=dict(fc="white", ec=GREY, lw=0.6, boxstyle="round,pad=0.25"))
    for a in axs.flat:
        a.tick_params(labelsize=8)
    fig.align_ylabels(axs[:, 0])
    save(fig, "29", "fig-29-2-spice-switching-waveforms")


# ----------------------------------------------------------------------------
# Figure 29.3 — loop gain Bode plot
# ----------------------------------------------------------------------------
def fig_29_3():
    f = np.logspace(2, np.log10(3e5), 4000)
    fig, (am, ap) = plt.subplots(2, 1, figsize=(6.4, 5.0), sharex=True,
                                 gridspec_kw=dict(hspace=0.12))
    styles = {2: (SKY, (0, (5, 2))), 10: (BLUE, "-"), 20: (ORANGE, (0, (1.5, 1.5)))}
    pm_txt = []
    for io in (2, 10, 20):
        Tf = T_at(f, K, io)
        mag = 20 * np.log10(abs(Tf))
        ph = np.degrees(np.unwrap(np.angle(Tf)))
        c, ls = styles[io]
        am.semilogx(f, mag, color=c, ls=ls, lw=1.5, label=f"model, {io} A")
        ap.semilogx(f, ph, color=c, ls=ls, lw=1.5)
        fc = brentq(lambda x: abs(T_at(x, K, io)) - 1, 5e3, 1e5)
        pm = 180 + np.degrees(np.angle(T_at(fc, K, io)))
        pm_txt.append(f"{io:>2} A: $f_c$ = {fc/1e3:.1f} kHz, PM = {pm:.1f}°")
        ap.plot(fc, pm - 180, "o", color=c, ms=4)
    # bench points: model at 10 A with gain and delay fitted to the FRA result
    fcb, pmb = 18.7e3, 61.0
    g = 1 / abs(T_at(fcb, K))
    tau = np.radians((180 + np.degrees(np.angle(T_at(fcb, K)))) - pmb) / (2 * np.pi * fcb)
    fb = np.logspace(np.log10(500), 5, 15)
    rng = np.random.default_rng(29)
    Tb = T_at(fb, K) * g * np.exp(-2j * np.pi * fb * tau)
    am.semilogx(fb, 20 * np.log10(abs(Tb)) + rng.normal(0, 0.25, fb.size), "D", ms=4.5,
                mfc="white", mec=INK, mew=1.1, ls="none", label="bench FRA, 10 A")
    ap.semilogx(fb, np.degrees(np.unwrap(np.angle(Tb))) + rng.normal(0, 1.0, fb.size), "D",
                ms=4.5, mfc="white", mec=INK, mew=1.1, ls="none")
    am.axhline(0, color=GREY, lw=0.8)
    f0 = W0 / 2 / np.pi
    for a in (am, ap):
        a.axvline(f0, color=GREY, ls=":", lw=0.9)
        a.grid(True, which="major", color="#E6E6E6", lw=0.6)
    am.text(f0 * 1.07, 62, f"LC resonance\n{f0/1e3:.2f} kHz", fontsize=7.6, va="center")
    am.annotate("crossover ≈ 20 kHz\n(bench 18.7 kHz)", xy=(20e3, 0), xytext=(45e3, 32),
                fontsize=7.6, arrowprops=dict(arrowstyle="-", color=GREY, lw=0.8))
    am.set_ylim(-60, 80)
    am.set_ylabel("|T| (dB)")
    am.legend(loc="lower left", fontsize=7.6, ncol=2)
    ap.axhline(-135, color=RED, ls="--", lw=1.1)
    ap.text(120, -130, "R4 limit: 45° phase margin (−135°)", color=RED, fontsize=7.6, va="bottom")
    ap.axhline(-180, color=GREY, lw=0.8)
    ap.text(0.985, 0.04, "\n".join(pm_txt) + "\nbench 10 A: $f_c$ = 18.7 kHz, PM = 61°",
            transform=ap.transAxes, ha="right", va="bottom", fontsize=7.4,
            bbox=dict(fc="white", ec=GREY, lw=0.6, boxstyle="round,pad=0.3"))
    ap.set_ylim(-270, 0)
    ap.set_yticks(np.arange(-270, 1, 45))
    ap.set_ylabel("phase (°)")
    ap.set_xlabel("frequency (Hz)")
    ap.set_xlim(100, 3e5)
    save(fig, "29", "fig-29-3-loop-gain-bode")


# ----------------------------------------------------------------------------
# Figure 29.4 — efficiency: model, SPICE, bench; loss breakdown at 10 A
# ----------------------------------------------------------------------------
def fig_29_4():
    fig, (a, b) = plt.subplots(1, 2, figsize=(6.8, 3.9),
                               gridspec_kw=dict(width_ratios=[1.35, 1], wspace=0.55))
    io = np.linspace(1.0, 20, 400)
    a.plot(io, [100 * efficiency(x) for x in io], color=BLUE, lw=1.8, label="loss model")
    a.plot([5, 10, 20], [96.6, 96.9, 96.2], "s", ms=6, mfc="white", mec=ORANGE, mew=1.4,
           ls="none", label="SPICE")
    a.errorbar([5, 10, 20], [96.4, 96.8, 96.1], yerr=0.14, fmt="o", ms=5, color=INK,
               capsize=3, lw=1.0, label="bench (±0.14 points)")
    for x, lim, name in [(10, 96.5, "R1 ≥ 96.5 %"), (20, 95.5, "R2 ≥ 95.5 %")]:
        a.add_patch(Rectangle((x - 0.9, lim - 0.18), 1.8, 0.18, fc="none", ec=RED, lw=0,
                              hatch="////"))
        a.plot([x - 0.9, x + 0.9], [lim, lim], color=RED, lw=2)
        a.text(x + 1.2 if x == 10 else x - 1.0, lim - 0.1, name, color=RED, fontsize=7.6,
               ha="left" if x == 10 else "right", va="center")
    a.set_xlim(0, 21)
    a.set_ylim(93, 98)
    a.set_xlabel("output current (A)")
    a.set_ylabel("efficiency (%)  at $V_{in}$ = 48 V")
    a.legend(loc="lower right", fontsize=7.6, bbox_to_anchor=(1.02, 0.0))
    a.grid(True, color="#ECECEC", lw=0.6)
    a.text(2.3, 94.35, "94.46 % at 2 A", fontsize=7, color=BLUE)

    l10 = losses(10.0)
    items = sorted(l10.items(), key=lambda kv: kv[1])
    names = [k for k, _ in items]
    vals = [v for _, v in items]
    yy = np.arange(len(names))
    colors = [BLUE if k.startswith("cond") else ORANGE if k in ("switching", "coss", "qrr",
              "dead_time", "gate") else GREEN if k in ("inductor", "cap_esr") else GREY
              for k in names]
    b.barh(yy, vals, color=colors, height=0.65)
    # inductor split
    i_ind = names.index("inductor")
    b.barh(i_ind, l10["inductor"] - P["p_core"], color=GREEN, height=0.65)
    b.barh(i_ind, P["p_core"], left=l10["inductor"] - P["p_core"], color=tint(GREEN, "70"),
           height=0.65, hatch="///", ec="white", lw=0)
    for y_, v, k in zip(yy, vals, names):
        txt = f"{v:.2f}"
        if k == "inductor":
            txt += " (0.31 Cu + 0.25 core)"
        b.text(v + 0.02, y_, txt, va="center", fontsize=7.2)
    b.set_yticks(yy)
    b.set_yticklabels(names, family="monospace", fontsize=7.8)
    b.set_xlim(0, 1.25)
    b.set_xlabel("loss at 10 A (W)")
    b.set_title(f"model losses at 10 A, total {sum(vals):.2f} W", fontsize=9)
    save(fig, "29", "fig-29-4-efficiency-model-spice-bench")


# ----------------------------------------------------------------------------
# Figure 29.5 — load-step comparison
# ----------------------------------------------------------------------------
def fig_29_5():
    nt, dt = loop_gain(K, 10.0)
    zcl = signal.lti(np.polymul(ZOL[0], dt), np.polymul(ZOL[1], np.polyadd(dt, nt)))
    t = np.linspace(0, 220e-6, 44001)
    _, v = signal.step(zcl, T=t)
    dv_ideal = -10.0 * v
    # 1 A/us slew: 10 A ramp over 10 us
    ramp = np.clip(t / 10e-6, 0, 1) * 10.0
    _, vr, _ = signal.lsim(zcl, ramp, t)
    dv_ramp = -vr
    ripple = lambda a, ph: a * signal.sawtooth(2 * np.pi * 200e3 * t + ph, 0.25)  # noqa: E731
    dv_spice = dv_ramp * (0.150 / abs(dv_ramp.min())) + ripple(0.0205, 0.3)
    # bench: deeper and slightly slower (52 us), plus ripple and measurement noise
    rng = np.random.default_rng(5)
    tb = t * 46 / 52
    vb = np.interp(tb, t, dv_ramp)
    dv_bench = vb * (0.158 / abs(vb.min())) + ripple(0.022, 1.1) + rng.normal(0, 0.003, t.size)

    fig, ax = plt.subplots(figsize=(6.4, 3.9))
    tp = np.concatenate([[-20e-6, 0], t]) * 1e6

    def pad(x, pre):
        return np.concatenate([[pre, pre], x])

    pre_r = ripple(0.0205, 0.3)[:1]
    ax.plot(tp, 1e3 * pad(dv_bench, 0), color=GREY, lw=0.5, alpha=0.8, label="bench (1 A/µs, 20 MHz BW): 158 mV")
    ax.plot(tp, 1e3 * pad(dv_spice, 0), color=ORANGE, lw=0.7,
            label="SPICE (1 A/µs, switching): ≈150 mV")
    ax.plot(tp, 1e3 * pad(dv_ideal, 0), color=BLUE, lw=2.0,
            label="averaged model (ideal step): 138 mV")
    del pre_r
    # pre-step ripple for SPICE/bench
    tpre = np.linspace(-20e-6, 0, 400)
    ax.plot(tpre * 1e6, 1e3 * 0.022 * signal.sawtooth(2 * np.pi * 200e3 * tpre + 1.1, 0.25),
            color=GREY, lw=0.6)
    ax.plot(tpre * 1e6, 1e3 * 0.0205 * signal.sawtooth(2 * np.pi * 200e3 * tpre + 0.3, 0.25),
            color=ORANGE, lw=0.8)
    ax.axhline(-360, color=RED, ls="--", lw=1.1)
    ax.text(198, -352, "R5: 3 % (−360 mV)", color=RED, fontsize=7.8, ha="right", va="bottom")
    for yl in (30, -30):
        ax.axhline(yl, color=GREEN, ls="--", lw=1.0)
    ax.text(198, -36, "R5: ±0.25 % (±30 mV) band", color="#1B6B4F", fontsize=7.8, ha="right",
            va="top")
    ax.axvline(100, color=RED, ls="--", lw=1.0)
    ax.text(103, -140, "R5 recovery\nlimit 100 µs", color=RED, fontsize=7.8, va="center")
    i = np.argmin(dv_ideal)
    ax.annotate(f"−138 mV at {t[i]*1e6:.0f} µs", xy=(t[i] * 1e6, -138), xytext=(30, -200),
                fontsize=7.6, arrowprops=dict(arrowstyle="-", color=BLUE, lw=0.8), color=BLUE)
    ax.annotate("model inside ±30 mV\nafter 46 µs; bench 52 µs", xy=(46, -30), xytext=(55, -110),
                fontsize=7.6, arrowprops=dict(arrowstyle="-", color=INK, lw=0.8))
    ax.set_xlim(-20, 200)
    ax.set_ylim(-400, 100)
    ax.set_xlabel("time after load step (µs)")
    ax.set_ylabel("output-voltage deviation (mV)")
    ax.legend(loc="lower right", fontsize=7.4, bbox_to_anchor=(1.0, 0.13), ncol=1)
    ax.text(-18, 85, "10 A step at 48 V, 12 V output", fontsize=7.6, va="top")
    save(fig, "29", "fig-29-5-load-step-comparison")


if __name__ == "__main__":
    fig_29_1()
    fig_29_2()
    fig_29_3()
    fig_29_4()
    fig_29_5()
