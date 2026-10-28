"""Figures for Chapter 38 — Project: Wireless Sensor Network.

Run from the repository root:  python figures/scripts/ch38.py
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle, FancyBboxPatch, Circle  # noqa: E402

from figstyle import COLORS, INK, GRID, box, save, new_fig  # noqa: E402

BLUE, ORANGE, GREEN, PINK, YELLOW, SKY = COLORS[:6]
RED = "#C62828"
GREY = "#777777"
SF_COL = {7: BLUE, 8: GREEN, 9: ORANGE}
SENS = {7: -124.0, 8: -127.0, 9: -129.0, 10: -132.0}


def toa(n_bytes, sf, bw=125e3, cr=1, n_pre=8):
    """LoRa time on air (s), explicit header, CRC on (Semtech formula, as in 38.4)."""
    de = 1 if sf >= 11 else 0
    ts = 2 ** sf / bw
    n = 8 + max(math.ceil((8 * n_bytes - 4 * sf + 44) / (4 * (sf - 2 * de))) * (cr + 4), 0)
    return (n_pre + 4.25 + n) * ts


def p_model(d):
    """Fitted received power (dBm): 14 + 0 + 5 - 2 - PL(d), PL = 85 + 33 log10(d/100)."""
    return 14 + 0 + 5 - 2 - (85 + 33 * np.log10(np.asarray(d) / 100.0))


def survey():
    """Synthetic site survey consistent with the chapter: 32 medians whose least-squares
    fit is exactly the stated model, node 17 behind the shed; SF = lowest with >= 12 dB margin."""
    rng = np.random.default_rng(38)
    d = np.sort(rng.uniform(150, 850, 32))
    d[0], d[-1] = 150.0, 850.0
    i29 = int(np.argmin(np.abs(d - 610)))
    d[i29] = 610.0
    x = np.log10(d / 100)
    r = rng.normal(0, 3.2, 32)
    r[i29] = -(p_model(610) - (-129 + 7.5))          # 7.5 dB margin at SF9 before the fix
    # make the least-squares line through all 32 points exactly the model (residuals orthogonal to [1, x])
    A = np.c_[np.ones(32), x]
    free = np.ones(32, bool)
    free[i29] = False
    Af = A[free]
    c = np.linalg.solve(Af.T @ Af, Af.T @ r[free] + A[i29] * r[i29])
    r[free] = r[free] - Af @ c
    p = p_model(d) + r
    p_after = p.copy()
    p_after[i29] = -129 + 13.5                       # moved 15 m and antenna raised
    # spreading factor as assigned: the lowest SF giving >= 12 dB measured margin (R5)
    sf = np.full(32, 9)
    for s_ in (8, 7):
        sf[p_after - SENS[s_] >= 12.0] = s_
    # renumber so the shed position is node 17
    perm = rng.permutation(32)
    perm[perm == 17], perm[i29] = perm[i29], 17
    return d, p, p_after, sf, perm, i29


# ----------------------------------------------------------------------------
def fig_38_1():
    """Network architecture: field star, node detail, gateway."""
    d, p, pa, sf, nid, i29 = survey()
    fig = plt.figure(figsize=(6.8, 5.0))
    am = fig.add_axes([0.0, 0.12, 0.40, 0.80])
    ab = fig.add_axes([0.40, 0.0, 0.60, 1.0])
    # --- field map
    rng = np.random.default_rng(5)
    ang = np.radians(rng.uniform(5, 175, 32))
    xs, ys = d * np.cos(ang), d * np.sin(ang)
    for r in (250, 500, 750):
        am.add_patch(Circle((0, 0), r, fill=False, ec=GRID, lw=0.8, ls="--"))
        am.text(-r, -70, f"{r} m", fontsize=6.6, color=GREY,
                ha="center")
    for k in range(32):
        am.plot([0, xs[k]], [0, ys[k]], color=GRID, lw=0.6, zorder=1)
    leaf = np.argsort(rng.uniform(size=32))[:8]
    for k in range(32):
        am.plot(xs[k], ys[k], "o", ms=5.2, color=SF_COL[sf[k]], mec="white", mew=0.5, zorder=3)
        if k in leaf:
            am.plot(xs[k], ys[k], "o", ms=9.5, mfc="none", mec=INK, mew=0.9, zorder=3)
    am.plot(0, 0, "s", ms=8, color=INK, zorder=4)
    am.text(40, -40, "gateway (winery roof)", ha="left", va="top", fontsize=7)
    k29 = i29
    am.annotate("node 17\n(behind shed)", xy=(xs[k29], ys[k29]), xytext=(xs[k29] + (260 if xs[k29] < 300 else -260), ys[k29] + 120),
                fontsize=6.8, arrowprops=dict(arrowstyle="-", lw=0.7, color=GREY), ha="center")
    am.set_xlim(-900, 900)
    am.set_ylim(-130, 960)
    am.set_aspect("equal")
    am.axis("off")
    am.text(-880, 950, "32 nodes, 40 ha, 150–850 m", fontsize=7.6, weight="bold", va="top")
    hs = [plt.Line2D([], [], marker="o", ls="", color=SF_COL[s], ms=5, label=f"SF{s} ({np.sum(sf == s)} node{'s' if np.sum(sf == s) > 1 else ''})")
          for s in (7, 8, 9) if np.any(sf == s)]
    hs.append(plt.Line2D([], [], marker="o", ls="", mfc="none", mec=INK, ms=8, label="with leaf-wetness sensor (8)"))
    am.legend(handles=hs, loc="lower center", fontsize=6.8, ncol=2, bbox_to_anchor=(0.5, -0.32),
              handletextpad=0.3, columnspacing=0.8)

    # --- detail boxes
    ab.set_xlim(0, 10)
    ab.set_ylim(0, 10)
    ab.axis("off")
    fs = 6.9
    # node
    ab.add_patch(FancyBboxPatch((0.15, 5.55), 9.7, 4.3, boxstyle="round,pad=0.02,rounding_size=0.15",
                                fc="#FAFAFA", ec=INK, lw=1.0))
    ab.text(0.35, 9.62, "Sensor node (post in the row, IP65)", fontsize=7.4, weight="bold", va="center")
    box(ab, 0.35, 7.55, 2.55, 1.75, "SHT45-class\nT/RH in multi-\nplate shield,\n1.5 m", fc="#E9F5EF", fontsize=fs)
    box(ab, 3.35, 7.55, 3.1, 1.75, "STM32WLE5-class SoC\nCortex-M4, LoRa radio,\nTCXO 32 MHz,\n32.768 kHz, AES",
        fc="#EEF3F8", fontsize=fs)
    box(ab, 6.85, 8.3, 1.2, 1.0, "RF\nswitch", fc="#EEF3F8", fontsize=fs)
    box(ab, 8.35, 7.55, 1.35, 1.75, "868 MHz\nλ/4 whip\nat 2.2 m", fc="#EEF3F8", fontsize=fs)
    for (x0, x1, y, t) in ((2.9, 3.35, 8.42, "I²C"), (6.45, 6.85, 8.8, ""), (8.05, 8.35, 8.8, "")):
        ab.annotate("", xy=(x1, y), xytext=(x0, y), arrowprops=dict(arrowstyle="-|>", lw=1.0, color=INK,
                                                                    mutation_scale=8))
        if t:
            ab.text((x0 + x1) / 2, y + 0.08, t, fontsize=6.4, ha="center", va="bottom")
    box(ab, 0.35, 5.75, 2.55, 1.4, "2 × AA Li-FeS₂\n3.0 V, 3.0 Ah", fc="#FBEFE6", fontsize=fs)
    box(ab, 3.35, 5.75, 3.1, 1.4, "SoC internal SMPS\n(1.8–3.6 V input)", fc="#FBEFE6", fontsize=fs)
    box(ab, 6.85, 5.75, 2.85, 1.4, "battery divider and\nleaf sensor, switched\nby a MOSFET", fc="#FBEFE6",
        fontsize=fs)
    ab.annotate("", xy=(3.35, 6.45), xytext=(2.9, 6.45), arrowprops=dict(arrowstyle="-|>", lw=1.0, color=ORANGE,
                                                                        mutation_scale=8))
    ab.annotate("", xy=(4.9, 7.55), xytext=(4.9, 7.15), arrowprops=dict(arrowstyle="-|>", lw=1.0, color=ORANGE,
                                                                       mutation_scale=8))
    ab.annotate("", xy=(6.85, 6.45), xytext=(6.45, 6.45), arrowprops=dict(arrowstyle="-|>", lw=1.0, color=ORANGE,
                                                                         mutation_scale=8))
    # radio links
    ab.annotate("", xy=(1.6, 4.75), xytext=(1.6, 5.55), arrowprops=dict(arrowstyle="-|>", lw=1.4, color=BLUE,
                                                                       mutation_scale=10))
    ab.text(1.85, 5.15, "uplinks 868.1 MHz, own 1 s slot,\nSF7–SF9, 21-byte AES-CCM frame", fontsize=6.7,
            color=BLUE, va="center")
    ab.annotate("", xy=(8.9, 5.55), xytext=(8.9, 4.75), arrowprops=dict(arrowstyle="-|>", lw=1.4, color=PINK,
                                                                       mutation_scale=10))
    ab.text(8.65, 5.15, "group-ACK beacon\n869.525 MHz,\nonce per 60 s frame", fontsize=6.7, color=PINK,
            va="center", ha="right")
    # gateway
    ab.add_patch(FancyBboxPatch((0.15, 0.1), 9.7, 4.6, boxstyle="round,pad=0.02,rounding_size=0.15",
                                fc="#FAFAFA", ec=INK, lw=1.0))
    ab.text(0.35, 4.45, "Gateway (winery roof, mains + UPS 12 h)", fontsize=7.4, weight="bold", va="center")
    box(ab, 0.35, 2.45, 2.0, 1.6, "5 dBi collinear\nat 8 m,\nlightning\narrester", fc="#EEF3F8", fontsize=fs)
    box(ab, 2.75, 2.45, 1.7, 1.6, "SX1262-\nclass\nradio", fc="#EEF3F8", fontsize=fs)
    box(ab, 4.85, 2.45, 2.75, 1.6, "Linux SBC: slot\nscheduler, decryption,\nSQLite store, wet-bulb\nand frost logic",
        fc="#EEF3F8", fontsize=fs)
    box(ab, 8.0, 2.45, 1.7, 1.6, "LTE\nmodem", fc="#EEF3F8", fontsize=fs)
    for x0, x1 in ((2.35, 2.75), (4.45, 4.85), (7.6, 8.0)):
        ab.annotate("", xy=(x1, 3.25), xytext=(x0, 3.25), arrowprops=dict(arrowstyle="-|>", lw=1.0, color=INK,
                                                                         mutation_scale=8))
    box(ab, 0.35, 0.35, 2.75, 1.5, "UPS: 12 V LiFePO₄,\n12 h; hardware\nwatchdog", fc="#FBEFE6", fontsize=fs)
    box(ab, 3.45, 0.35, 3.1, 1.5, "relay → lamp at wind-\nmachine start panel\n(manual confirm)", fc="#FDECEC",
        fontsize=fs)
    box(ab, 6.9, 0.35, 2.8, 1.5, "MQTT broker,\ndashboard; SMS to\nvineyard manager", fc="#FDECEC", fontsize=fs)
    ab.annotate("", xy=(5.0, 1.85), xytext=(5.6, 2.45), arrowprops=dict(arrowstyle="-|>", lw=1.0, color=RED,
                                                                       mutation_scale=8))
    ab.annotate("", xy=(8.85, 1.85), xytext=(8.85, 2.45), arrowprops=dict(arrowstyle="-|>", lw=1.0, color=RED,
                                                                         mutation_scale=8))
    save(fig, "38", "fig-38-1-network-architecture")


# ----------------------------------------------------------------------------
I_SLEEP, I_SENS, I_START, I_TX, I_RX = 1.6e-6, 1.5e-3, 3e-3, 45e-3, 6e-3
T_UP = toa(21, 9)
T_BCN = toa(16, 9)


def node_current(t):
    """Current (A) of SF9 node 17 through one frame, t in s (frame starts at 0)."""
    i = np.full_like(t, I_SLEEP)
    i[(t >= 0) & (t < 0.010)] = I_SENS                     # wake and sensor read
    i[(t >= 16.993) & (t < 17.0)] = I_START                # radio start 5 ms + AES 2 ms
    i[(t >= 17.0) & (t < 17.0 + T_UP)] = I_TX              # uplink
    i[(t >= 48.0) & (t < 48.0 + T_BCN + 0.040)] = I_RX     # beacon window incl. 2 x 20 ms guard
    return i


def fig_38_2():
    """TDMA frame structure and the timing of one node's report."""
    fig = plt.figure(figsize=(6.8, 5.2))
    a0 = fig.add_axes([0.08, 0.80, 0.90, 0.12])
    for k in range(32):
        a0.add_patch(Rectangle((k, 0), 1, 1, fc="#DCE8F3" if k != 17 else ORANGE, ec="white", lw=0.6))
    for k in range(16):
        a0.add_patch(Rectangle((32 + k, 0), 1, 1, fc="#E3F2EA", ec="white", lw=0.6))
    a0.add_patch(Rectangle((48, 0), 2, 1, fc=PINK, ec="white", lw=0.6))
    a0.add_patch(Rectangle((50, 0), 10, 1, fc="#EEEEEE", ec="white", lw=0.6))
    for k in (0, 10, 20, 31):
        a0.text(k + 0.5, 0.5, str(k), ha="center", va="center", fontsize=6.2)
    a0.text(17.5, 0.5, "17", ha="center", va="center", fontsize=6.2, color="white", weight="bold")
    a0.text(16, 1.15, "32 dedicated uplink slots × 1.0 s (868.1 MHz)", ha="center", va="bottom", fontsize=7.2)
    a0.text(39.5, 1.15, "16 shared retry slots", ha="center", va="bottom", fontsize=7.2)
    a0.text(49.3, 1.15, "beacon 2 s", ha="center", va="bottom", fontsize=7.2, color=PINK)
    a0.text(55, 0.5, "spare 10 s", ha="center", va="center", fontsize=7.2)
    a0.set_xlim(0, 60)
    a0.set_ylim(-0.2, 1.9)
    a0.set_yticks([])
    a0.spines["left"].set_visible(False)
    a0.set_xticks(np.arange(0, 61, 10))
    a0.set_xlabel("Time in the 60 s frame (s)", fontsize=8.5, labelpad=1)
    a0.set_title("Frost-watch frame: every node reports in every frame", fontsize=8.6, loc="left")
    # zooms: frame start, slot 17, beacon window
    zooms = [(-0.005, 0.030, "frame start: wake, read sensor", 1e3, "ms"),
             (16.975, 17.225, "slot 17 (SF9 node): uplink", 1e3, "ms after 17 s"),
             (47.975, 48.225, "beacon window", 1e3, "ms after 48 s")]
    for j, (t0, t1, title, scale, unit) in enumerate(zooms):
        az = fig.add_axes([0.08 + 0.325 * j, 0.33, 0.255, 0.30])
        t = np.linspace(t0, t1, 4000)
        i = node_current(t)
        off = 0 if j == 0 else (17.0 if j == 1 else 48.0)
        az.step((t - off) * scale, i * 1e3, where="post", color=INK, lw=1.2)
        az.fill_between((t - off) * scale, 1e-4, i * 1e3, step="post", color=SKY, alpha=0.35, lw=0)
        az.set_yscale("log")
        az.set_ylim(1e-3, 200)
        az.set_xlim((t0 - off) * scale, (t1 - off) * scale)
        az.set_title(title, fontsize=7.8)
        az.set_xlabel(f"Time ({unit})", fontsize=7.6)
        az.tick_params(labelsize=7)
        if j == 0:
            az.set_ylabel("Node current (mA)", fontsize=7.8)
            az.text(5, 2.4, "1.5 mA, 10 ms", fontsize=6.8, ha="center")
            az.text(22, 3e-3 * 1.5, "sleep 1.6 µA", fontsize=6.8, ha="center")
        if j == 1:
            az.text(92, 70, "TX 45 mA, 185 ms", fontsize=6.8, ha="center")
            az.text(92, 12, "868.1 MHz", fontsize=6.6, ha="center")
            az.annotate("wake 15 ms early;\nradio start + AES", xy=(-4, 3), xytext=(60, 0.08), fontsize=6.6,
                        arrowprops=dict(arrowstyle="-", lw=0.7, color=GREY))
        if j == 2:
            az.text(102, 12, "RX 6 mA, 205 ms incl.\n20 ms guard each side", fontsize=6.6, ha="center", va="bottom")
            az.axvspan(0, 20, color=PINK, alpha=0.15, lw=0)
            az.axvspan(20 + T_BCN * 1e3, 40 + T_BCN * 1e3, color=PINK, alpha=0.15, lw=0)
            az.text(102, 0.12, "beacon 165 ms,\nSF9, 869.525 MHz;\nnode checks bit 17\nof the ACK bitmap", fontsize=6.4,
                    ha="center", va="center")
    # connectors from the frame bar to the zooms (figure coordinates)
    from matplotlib.lines import Line2D
    for x_bar, j in ((0.0, 0), (17.5, 1), (49.0, 2)):
        xb = 0.08 + 0.90 * x_bar / 60
        xz = 0.08 + 0.325 * j + 0.1275
        fig.add_artist(Line2D([xb, xz], [0.735, 0.665], color=GREY, lw=0.8, ls="--"))
    # normal mode
    an = fig.add_axes([0.08, 0.07, 0.90, 0.10])
    for f in range(5):
        an.add_patch(Rectangle((f * 60, 0), 60, 1, fc="#F4F4F4", ec=INK, lw=0.6))
    an.add_patch(Rectangle((17, 0), 1, 1, fc=ORANGE, ec=ORANGE))
    an.add_patch(Rectangle((48, 0), 2, 1, fc=PINK, ec=PINK))
    an.add_patch(Rectangle((0, 0), 0.6, 1, fc=GREEN, ec=GREEN))
    for f in range(1, 5):
        an.add_patch(Rectangle((f * 60, 0), 0.6, 1, fc=GREEN, ec=GREEN))
        an.text(f * 60 + 30, 0.5, "sample only, no TX", ha="center", va="center", fontsize=6.8, color=GREY)
    an.text(30, 0.5, "sample, TX, beacon", ha="center", va="center", fontsize=6.8)
    an.set_xlim(0, 300)
    an.set_ylim(0, 1)
    an.set_yticks([])
    an.spines["left"].set_visible(False)
    an.set_xticks(np.arange(0, 301, 60))
    an.set_xlabel("Time (s)", fontsize=8.5, labelpad=1)
    an.set_title("Normal mode: node samples every minute, reports in every fifth frame (5 min)", fontsize=8.6,
                 loc="left")
    save(fig, "38", "fig-38-2-tdma-frame")


# ----------------------------------------------------------------------------
def fig_38_3():
    """Link survey: received power against distance, fit and sensitivities."""
    d, p, pa, sf, nid, i29 = survey()
    fig, ax = new_fig(6.4, 4.2)
    dd = np.logspace(2, 3, 100)
    for s, c in ((7, BLUE), (8, GREEN), (9, ORANGE), (10, PINK)):
        ax.axhline(SENS[s], color=c, ls="--", lw=1.0)
        if s < 10:
            ax.axhline(SENS[s] + 12, color=c, ls=":", lw=1.0)
        ax.text(1020, SENS[s], f"SF{s} {SENS[s]:.0f} dBm", color=c, fontsize=7.4, va="center", ha="left")
    ax.axhspan(-135, -112, color=GREY, alpha=0.06, lw=0)
    ax.text(103, -110.8, "dotted: sensitivity + 12 dB, the required measured margin (R5)", fontsize=7,
            color=GREY, va="bottom")
    ax.text(1020, -114.5, "SF7/8/9\n+12 dB", fontsize=7, color=GREY, va="center")
    ax.plot(dd, p_model(dd), color=INK, lw=1.6, label="fit: $P$ = 14 + 5 − 2 − 85 − 33 log$_{10}$($d$/100 m)")
    for s in (7, 8, 9):
        if not np.any(sf == s):
            continue
        m = (sf == s)
        m[i29] = False
        ax.plot(d[m], pa[m], "o", ms=5, color=SF_COL[s], mec="white", mew=0.5,
                label=f"measured median, assigned SF{s} ({np.sum(sf == s)})")
    ax.plot(d[i29], pa[i29], "o", ms=6, color=SF_COL[sf[i29]], mec=INK, mew=0.8)
    ax.plot(d[i29], p[i29], "o", ms=6, mfc="white", mec=SF_COL[sf[i29]], mew=1.0)
    ax.annotate("", xy=(d[i29], pa[i29] - 0.6), xytext=(d[i29], p[i29] + 0.6),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.8, mutation_scale=7))
    ax.annotate("node 17 behind the machinery shed, 610 m:\n7.5 dB at SF9 → 13.5 dB after moving 15 m\n"
                "and raising its antenna to 3.0 m (weakest link)", xy=(d[i29], pa[i29]), xytext=(103, -101),
                fontsize=7.2, arrowprops=dict(arrowstyle="-", color=GREY, lw=0.7), va="center")
    ax.plot([850], [p_model(850)], "D", color=INK, ms=4.5)
    ax.annotate("−98.7 dBm at 850 m", xy=(850, p_model(850)), xytext=(560, -86), fontsize=7.4,
                arrowprops=dict(arrowstyle="-", color=GREY, lw=0.7))
    ax.set_xscale("log")
    ax.set_xlim(100, 1000)
    ax.set_ylim(-135, -60)
    ax.set_xticks([100, 200, 300, 500, 700, 1000])
    ax.set_xticklabels(["100", "200", "300", "500", "700", "1000"])
    ax.xaxis.set_minor_formatter(plt.NullFormatter())
    ax.set_xlabel("Distance from gateway (m)")
    ax.set_ylabel("Received power, median RSSI (dBm)")
    ax.legend(loc="upper right", fontsize=7.2)
    ax.grid(True, which="both", color=GRID, lw=0.5)
    save(fig, "38", "fig-38-3-link-survey")
    return d, p, pa, sf


# ----------------------------------------------------------------------------
def fig_38_4():
    """Measured current of an SF9 node through one report (broken time axis)."""
    segs = [(-0.003, 0.030, 0.0, "frame start"), (16.975, 17.25, 17.0, "slot 17"), (47.98, 48.25, 48.0,
                                                                                    "beacon window")]
    fig, axs = plt.subplots(1, 3, figsize=(6.6, 3.9), sharey=True, gridspec_kw=dict(wspace=0.08,
                                                                                    width_ratios=[1, 1.4, 1.4]))
    rng = np.random.default_rng(4)
    q_sens = 0.010 * I_SENS * 1e3
    q_tx = T_UP * I_TX * 1e3
    q_rx = (T_BCN + 0.040) * I_RX * 1e3
    for k, (ax, (t0, t1, off, nm)) in enumerate(zip(axs, segs)):
        t = np.linspace(t0, t1, 3000)
        i = node_current(t)
        meas = i * (1 + 0.03 * rng.standard_normal(t.size))
        ax.plot((t - off) * 1e3, meas * 1e3, color=BLUE, lw=0.9)
        ax.set_yscale("log")
        ax.set_ylim(1e-3, 100)
        ax.set_xlim((t0 - off) * 1e3, (t1 - off) * 1e3)
        ax.set_xlabel(f"ms after {off:g} s" if off else "ms after frame start", fontsize=8)
        ax.set_title(nm, fontsize=8.5)
        ax.grid(True, which="major", color=GRID, lw=0.5)
        if k > 0:
            ax.spines["left"].set_visible(False)
            ax.tick_params(which="both", left=False)
        # break marks
        kw = dict(transform=ax.transAxes, color=INK, clip_on=False, lw=0.9)
        if k < 2:
            ax.plot([0.98, 1.02], [-0.03, 0.03], **kw)
        if k > 0:
            ax.plot([-0.02, 0.02], [-0.03, 0.03], **kw)
    axs[0].set_ylabel("Current (mA, log scale)")
    axs[0].text(11.5, 1.5, f"sensor read\n1.5 mA × 10 ms\n= {q_sens:.3f} mC", fontsize=6.9, ha="left", va="center")
    axs[0].text(20, 2.2e-3, "sleep\n1.6 µA", fontsize=6.9, ha="center", va="bottom")
    axs[1].text(92, 25, f"TX 45 mA × {T_UP * 1e3:.0f} ms\n= {q_tx:.2f} mC", fontsize=6.9, ha="center", va="top")
    axs[1].annotate("radio start + AES\n3 mA", xy=(-3.5, 3), xytext=(60, 0.05), fontsize=6.9,
                    arrowprops=dict(arrowstyle="-", color=GREY, lw=0.7))
    axs[2].text(102, 7.5, f"RX 6 mA × {(T_BCN + 0.04) * 1e3:.0f} ms\n= {q_rx:.2f} mC", fontsize=6.9, ha="center",
                va="bottom")
    axs[2].text(102, 0.02, "includes 20 ms\nguard each side", fontsize=6.9, ha="center", color=GREY)
    q_tot = q_sens + 0.005 * I_START * 1e3 + 0.002 * I_START * 1e3 + q_tx + q_rx
    fig.text(0.5, -0.09, f"Time axis broken between the three windows (frame of 60 s).  Charge per report: predicted "
             f"{q_tot:.2f} mC\n(sensor {q_sens:.3f}, radio start and AES 0.021, TX {q_tx:.2f}, beacon RX {q_rx:.2f} mC)"
             f" against 9.92 mC measured at 20 °C", ha="center", fontsize=7.8)
    save(fig, "38", "fig-38-4-node-current-profile")
    return q_tot


# ----------------------------------------------------------------------------
def _hm(h, m):
    """Hours after 20:00 for a clock time h:m (night spanning midnight)."""
    return (h + m / 60 - 20) % 24


def fig_38_5():
    """A frost night as recorded by the network."""
    t = np.arange(0, 12 + 1e-9, 1 / 60)            # hours after 20:00, one reading per minute

    def interp(knots):
        x, y = zip(*[(_hm(*k[0]), k[1]) for k in knots])
        from scipy.interpolate import PchipInterpolator
        return PchipInterpolator(x, y)(t)
    cold = interp([((20, 0), 6.0), ((21, 30), 4.6), ((23, 10), 3.0), ((1, 0), 1.6), ((2, 38), 0.48),
                   ((2, 55), 0.25), ((3, 15), 1.75), ((3, 45), 1.0), ((4, 40), -0.6), ((5, 30), -1.4),
                   ((6, 15), -0.7), ((6, 50), 0.9), ((7, 5), 1.55), ((8, 0), 4.2)])
    warm = interp([((20, 0), 7.8), ((22, 0), 6.4), ((0, 0), 5.2), ((3, 0), 4.0), ((5, 30), 3.4), ((6, 30), 3.6),
                   ((8, 0), 6.5)])
    med = interp([((20, 0), 7.0), ((22, 0), 5.5), ((0, 0), 4.0), ((2, 55), 2.6), ((3, 15), 3.1), ((5, 30), 1.6),
                  ((6, 30), 2.0), ((8, 0), 5.4)])
    rng = np.random.default_rng(385)
    noise = lambda n: 0.04 * rng.standard_normal(n)
    cold_r, warm_r, med_r = cold + noise(t.size), warm + noise(t.size), med + noise(t.size)
    wet = cold_r - (1.0 + 0.15 * np.sin(t * 0.7))   # wet-bulb about 1 K below dry-bulb at RH near 85 %
    fig, (ax, ad) = plt.subplots(2, 1, figsize=(6.6, 4.6), sharex=True,
                                 gridspec_kw=dict(height_ratios=[4, 0.6], hspace=0.08))
    ax.plot(t, warm_r, color=ORANGE, lw=1.3, label="warmest node")
    ax.plot(t, med_r, color=GREY, lw=1.3, label="median of 32 nodes")
    ax.plot(t, cold_r, color=BLUE, lw=1.5, label="coldest node (low corner)")
    ax.plot(t, wet, color=SKY, lw=1.2, ls="--", label="wet-bulb, coldest node")
    ax.axhline(0.5, color=RED, ls="--", lw=1.0)
    ax.text(12.1, 0.5, "0.5 °C\nalarm", color=RED, fontsize=7.2, ha="left", va="center")
    ax.axhline(3.0, color=INK, ls=":", lw=1.0)
    ax.text(12.1, 3.0, "3 °C\nfrost\nwatch", fontsize=7.2, ha="left", va="center")
    events = [((23, 10), "frost watch\n23:10", INK, 7.2),
              ((2, 41), "alarm 02:41\nSMS 02:42", RED, 7.2),
              ((2, 55), "wind machines\nstarted 02:55", GREEN, 6.3),
              ((7, 20), "alarm cleared\n07:20", RED, 7.2)]
    for (hm, lab, c, y) in events:
        x = _hm(*hm)
        ax.axvline(x, color=c, lw=0.9, ls="-.")
        ax.text(x + 0.08, y, lab, fontsize=7, color=c, va="top")
    k3 = np.argmin(np.abs(t - _hm(3, 15)))
    ax.annotate("+1.5 °C in 20 min\nin the low corner", xy=(t[k3], cold[k3]), xytext=(_hm(0, 30), -1.3),
                fontsize=7, color=BLUE, arrowprops=dict(arrowstyle="-", color=BLUE, lw=0.7))
    k5 = np.argmin(np.abs(t - _hm(5, 30)))
    ax.annotate("−1.4 °C at 05:30", xy=(t[k5], cold[k5]), xytext=(_hm(2, 10), -2.6), fontsize=7, color=BLUE,
                arrowprops=dict(arrowstyle="-", color=BLUE, lw=0.7))
    ax.set_ylim(-3, 8)
    ax.set_ylabel("Temperature (°C)")
    ax.legend(loc="lower left", fontsize=7.2)
    ax.grid(True, color=GRID, lw=0.5)
    # delivery strip: one tick per frame received (every 5 min before frost watch, every minute after)
    fw = _hm(23, 10)
    frames = np.r_[np.arange(0, fw, 5 / 60), np.arange(fw, 12, 1 / 60)]
    ad.vlines(frames, 0, 1, color=GREEN, lw=0.4)
    late = np.array([_hm(4, 8), _hm(4, 10), _hm(4, 12)])
    ad.vlines(late, -0.2, 1.2, color=RED, lw=1.6)
    ad.text(_hm(4, 0), 0.5, "3 late readings (one tractor-shadowed node)", color=RED, fontsize=6.8, va="center", ha="right",
            bbox=dict(fc="white", ec="none", pad=0.5))
    ad.set_ylim(-0.3, 1.3)
    ad.set_yticks([])
    ad.set_ylabel("frames", rotation=0, ha="right", va="center", fontsize=7.6)
    ad.spines["left"].set_visible(False)
    ticks = np.arange(0, 12.01, 2)
    ad.set_xticks(ticks)
    ad.set_xticklabels([f"{int((20 + h) % 24):02d}:00" for h in ticks])
    ad.set_xlim(0, 12)
    ad.set_xlabel("Local time")
    save(fig, "38", "fig-38-5-frost-night")


if __name__ == "__main__":
    fig_38_1()
    fig_38_2()
    fig_38_3()
    print("charge", fig_38_4())
    fig_38_5()
