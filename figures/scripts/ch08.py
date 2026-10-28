"""Figures for Chapter 8 — Data Acquisition Systems.

Run from the repository root:  python figures/scripts/ch08.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle  # noqa: E402

from figstyle import COLORS, INK, box, new_fig, save, schematic  # noqa: E402

BLUE, ORANGE, GREEN, PINK, YELLOW, SKY = COLORS[:6]
RED = "#C62828"
GREY = "#777777"


def line(ax, pts, color=INK, lw=1.1, ls="-", arrow_end=False, both=False, zorder=2):
    """Poly-line through pts with optional arrow head(s) on the last segment."""
    xs, ys = zip(*pts)
    if not arrow_end and not both:
        ax.plot(xs, ys, color=color, lw=lw, ls=ls, solid_capstyle="butt", zorder=zorder)
        return
    if len(pts) > 2:
        ax.plot(xs[:-1], ys[:-1], color=color, lw=lw, ls=ls, zorder=zorder)
    ax.annotate("", xy=pts[-1], xytext=pts[-2], zorder=zorder,
                arrowprops=dict(arrowstyle="<|-|>" if both else "-|>", color=color, lw=lw,
                                ls=ls, shrinkA=0, shrinkB=0, mutation_scale=10))


def titled_box(ax, x, y, w, h, title, body, fc, fs_title=8.8, fs_body=7.6, ec=INK, lw=1.0):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.15",
                                fc=fc, ec=ec, lw=lw))
    ax.text(x + w / 2, y + h - 0.22, title, ha="center", va="top", fontsize=fs_title,
            weight="bold", color=INK)
    if body:
        ax.text(x + w / 2, y + h - 0.72, body, ha="center", va="top", fontsize=fs_body,
                color=INK, linespacing=1.3)


# ----------------------------------------------------------------------------
# Figure 8.1 — distributed DAQ architecture of the dynamometer cell
# ----------------------------------------------------------------------------
def fig_8_1():
    fig, ax = schematic(6.8, 5.0, xlim=(0, 17.4), ylim=(-0.2, 12.6))
    # --- test cell (left)
    ax.add_patch(Rectangle((0.08, 2.9), 2.97, 9.6, fc="#F5F5F5", ec=GREY, lw=1.0, ls=(0, (4, 2))))
    ax.text(1.65, 12.22, "Test cell", ha="center", va="center", fontsize=8.8, weight="bold")
    cell = [("Battery\nemulator", 10.85), ("800 V SiC\ninverter", 9.05), ("PMSM\n150 kW", 7.25),
            ("Torque\nflange", 5.45), ("Absorbing\ndyno", 3.65)]
    for txt, y in cell:
        box(ax, 0.45, y - 0.6, 2.4, 1.2, txt, fc="#FFFFFF", fontsize=7.8)
    for (_, y0), (_, y1) in zip(cell[:-1], cell[1:]):
        line(ax, [(1.65, y0 - 0.6), (1.65, y1 + 0.6)], lw=2.6, color=GREY)

    # --- nodes
    xn, wn = 4.6, 5.8
    fst, fsb = 7.9, 6.9
    titled_box(ax, xn, 8.6, wn, 3.3, "Node P — power",
               "SoC FPGA\n8 isolated 16-bit SAR, 1 MSa/s\nIa Ib Ic · Va Vb Vc · Vdc · Idc\n"
               "one CONVST fanned out\nthrough digital isolators", "#DCE9F5", fst, fsb)
    titled_box(ax, xn, 4.4, wn, 3.5, "Node M — mechanical",
               "Cortex-M7 MCU\n8-ch 24-bit ΔΣ, 51.2 kSa/s:\n6 IEPE accel. + 2 microphones\n"
               "torque frequency · encoder\nCAN FD from inverter", "#DFF0E8", fst, fsb)
    titled_box(ax, xn, 1.3, wn, 2.6, "Node T — thermal",
               "MCU\n5 × 8-ch 24-bit ΔΣ, 10 Sa/s\n32 type-K + 8 Pt100", "#FBEBD9", fst, fsb)

    fw = 6.4
    def wire(pts, lab=None, color=INK, lx=None, ly=None):
        line(ax, pts, arrow_end=True, color=color)
        if lab:
            ax.text(lx, ly, lab, ha="center", va="bottom", fontsize=fw, color=color)
    wire([(2.85, 10.85), (xn, 10.85)], "Vdc, Idc", lx=3.75, ly=10.9)
    wire([(2.85, 9.05), (xn, 9.05)], "Ia–c, Va–c", lx=3.75, ly=9.1)
    wire([(2.85, 8.7), (3.35, 8.7), (3.35, 7.45), (xn, 7.45)], "CAN FD", GREEN, 3.95, 7.95)
    wire([(2.85, 7.0), (3.65, 7.0), (3.65, 6.4), (xn, 6.4)], "IEPE", lx=4.1, ly=6.55)
    wire([(2.85, 5.45), (xn, 5.45)], "f, A B Z", lx=3.75, ly=5.5)
    wire([(2.85, 3.65), (3.65, 3.65), (3.65, 4.75), (xn, 4.75)], "IEPE", lx=4.1, ly=4.05)
    line(ax, [(2.85, 7.6), (3.2, 7.6), (3.2, 2.3), (xn, 2.3)], arrow_end=True, color=ORANGE)
    ax.text(3.9, 2.35, "TC, Pt100", ha="center", va="bottom", fontsize=fw, color=ORANGE)

    # --- switch, grandmaster, host
    sx, sw = 12.4, 1.6
    ax.add_patch(FancyBboxPatch((sx, 1.7), sw, 9.6, boxstyle="round,pad=0.02,rounding_size=0.15",
                                fc="#EEEEEE", ec=INK, lw=1.0))
    ax.text(sx + sw / 2, 6.5, "Gigabit\nswitch\n\nPTP\ntrans-\nparent\nclock", ha="center",
            va="center", fontsize=7.8, linespacing=1.25)
    box(ax, 14.8, 9.4, 2.5, 1.9, "PTP grand-\nmaster\n(GNSS optional)", fc="#F3E6EF", fontsize=6.9)
    line(ax, [(sx + sw, 10.35), (14.8, 10.35)], both=True)
    titled_box(ax, 14.8, 2.6, 2.5, 5.6, "Host server",
               "2 TB NVMe\n\nlive display\n\ntest\nautomation", "#E8E8F4", fst, fsb)
    line(ax, [(sx + sw, 5.4), (14.8, 5.4)], both=True, lw=1.8)
    for y, lab in [(10.25, "135 Mbit/s"), (6.15, "14 Mbit/s"), (2.6, "< 0.1 Mbit/s")]:
        line(ax, [(xn + wn, y), (sx, y)], both=True, lw=1.8)
        ax.text((xn + wn + sx) / 2, y + 0.1, lab, ha="center", va="bottom", fontsize=7.0, color=BLUE)
    ax.text((xn + wn + sx) / 2, 10.1, "fibre", ha="center", va="top", fontsize=6.8,
            color=GREY, style="italic")

    # --- safety PLC (red path)
    box(ax, 0.08, -0.1, 3.4, 1.75, "Safety PLC\nhardwired interlocks\n(over-speed, over-temp.)",
        fc="#FDECEA", ec=RED, fontsize=7.0)
    for y in (9.05, 7.25, 3.65):
        line(ax, [(0.45, y), (0.25, y)], color=RED, lw=1.6)
    line(ax, [(0.25, 9.05), (0.25, 1.65)], color=RED, lw=1.6, arrow_end=True)
    line(ax, [(3.48, 0.75), (15.95, 0.75), (15.95, 2.6)], color=RED, ls=(0, (4, 2)), arrow_end=True)
    ax.text(9.7, 0.65, "interlock status only: DAQ observes, not part of the safety function",
            ha="center", va="top", fontsize=6.6, color=RED)
    save(fig, "08", "fig-8-1-dyno-daq-architecture")


# ----------------------------------------------------------------------------
# Figure 8.2 — coherent FFT test of one Node P channel (listing of Section 8.3)
# ----------------------------------------------------------------------------
def fig_8_2():
    FS, N, NBITS, VFS = 1_000_000, 65_536, 16, 10.0
    CYC = 67
    f0 = CYC * FS / N
    rng = np.random.default_rng(1)
    t = np.arange(N) / FS
    a = VFS * 10 ** (-0.5 / 20)
    v = a * np.sin(2 * np.pi * f0 * t)
    v += a * 10 ** (-98 / 20) * np.sin(2 * np.pi * 2 * f0 * t)
    v += a * 10 ** (-94 / 20) * np.sin(2 * np.pi * 3 * f0 * t)
    v += rng.normal(0, 180e-6, N)
    lsb = 2 * VFS / 2 ** NBITS
    code = np.clip(np.round(v / lsb), -2 ** 15, 2 ** 15 - 1)
    X = np.fft.rfft(code * lsb)
    P = np.abs(X) ** 2
    P[0] = 0
    ref = (VFS * N / 2) ** 2                     # full-scale sine in one bin
    dbfs = 10 * np.log10(np.maximum(P, 1e-30) / ref)
    f = np.fft.rfftfreq(N, 1 / FS)
    sig = P[CYC]
    harm = sum(P[h * CYC] for h in range(2, 7))
    noise = P.sum() - sig - harm
    snr = 10 * np.log10(sig / noise)
    thd = 10 * np.log10(harm / sig)
    sinad = 10 * np.log10(sig / (noise + harm))
    enob = (sinad - 1.76) / 6.02
    sfdr = 10 * np.log10(sig / np.delete(P, [0, CYC]).max())
    noise_bin = 10 * np.log10(np.mean(np.delete(P, [0] + [h * CYC for h in range(1, 7)])) / ref)
    ideal = -(6.02 * NBITS + 1.76) - 10 * np.log10(N / 2)

    fig, ax = new_fig(6.4, 3.9)
    m = f >= 100
    ax.semilogx(f[m], dbfs[m], color=BLUE, lw=0.5, label="Measured channel (65 536-point FFT, no window)")
    ax.axhline(ideal, color=INK, ls="--", lw=1.0,
               label="Ideal 16-bit quantization floor per bin (−" + f"{-ideal:.0f} dBFS)")
    ax.set_xlim(100, 5e5)
    ax.set_ylim(-160, 5)
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Power per bin (dBFS)")
    marks = [(CYC, "fundamental\n1022.34 Hz, −0.5 dBFS", (2.2, -12)),
             (2 * CYC, "HD2  {:.1f} dBFS", (2.4, -78)),
             (3 * CYC, "HD3  {:.1f} dBFS", (3.6, -62))]
    for k, lab, (fx, ty) in marks:
        ax.plot(f[k], dbfs[k], "o", color=ORANGE, ms=4.5, zorder=4)
        ax.annotate((lab.format(dbfs[k]) if "{" in lab else lab).replace("-", "−"), xy=(f[k], dbfs[k]),
                    xytext=(f[k] * fx, ty), fontsize=8, color=INK,
                    arrowprops=dict(arrowstyle="-", color=GREY, lw=0.7))
    ax.annotate(f"noise floor ≈ {noise_bin:.0f} dBFS per bin".replace("-", "−"), xy=(2e5, noise_bin),
                xytext=(8.0e3, -112), fontsize=8,
                arrowprops=dict(arrowstyle="-", color=GREY, lw=0.7))
    rows = [("SNR", f"{snr:.1f} dB"), ("THD", f"{thd:.1f} dBc"), ("SINAD", f"{sinad:.1f} dB"),
            ("ENOB", f"{enob:.2f} bits"), ("SFDR", f"{sfdr:.1f} dBc")]
    txt = "\n".join(f"{k:<6}{v:>11}" for k, v in rows).replace("-", "−")
    ax.text(0.985, 0.97, txt, transform=ax.transAxes, ha="right", va="top", fontsize=8,
            family="monospace", bbox=dict(fc="white", ec=GREY, lw=0.8, boxstyle="round,pad=0.4"))
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=1, fontsize=7.8)
    save(fig, "08", "fig-8-2-adc-fft-test")


# ----------------------------------------------------------------------------
# Figure 8.3 — windowed-logger state machine on Node P
# ----------------------------------------------------------------------------
def fig_8_3():
    fig, ax = schematic(6.8, 4.7, xlim=(0, 17.4), ylim=(0.2, 12.0))
    # ring buffer band
    ax.add_patch(FancyBboxPatch((0.3, 10.4), 16.8, 1.25, boxstyle="round,pad=0.02,rounding_size=0.2",
                                fc="#F1F1F1", ec=GREY, lw=1.0, ls=(0, (4, 2))))
    ax.text(8.7, 11.02, "Ring buffer — always running (0.5 s pre-trigger, 8 MB at 16 MB/s)",
            ha="center", va="center", fontsize=8.4, color=INK, style="italic")
    W, H = 3.2, 1.3
    st = {"IDLE": (0.3, 7.3), "ARMED": (7.1, 7.3), "RECORDING": (13.9, 7.3),
          "FLUSH": (13.9, 1.3), "CLOSED": (0.3, 1.3), "ERROR": (7.1, 4.5)}
    for name, (x, y) in st.items():
        err = name == "ERROR"
        ax.add_patch(FancyBboxPatch((x, y), W, H, boxstyle="round,pad=0.02,rounding_size=0.45",
                                    fc="#FDECEA" if err else "#DCE9F5", ec=RED if err else INK,
                                    lw=1.3))
        ax.text(x + W / 2, y + H / 2, name, ha="center", va="center",
                fontsize=8.2 if name == "RECORDING" else 9.0, weight="bold")

    def c(name, side, dx=0.0):
        x, y = st[name]
        return {"l": (x, y + H / 2), "r": (x + W, y + H / 2), "t": (x + W / 2 + dx, y + H),
                "b": (x + W / 2 + dx, y)}[side]

    ym = 7.3 + H / 2
    line(ax, [c("IDLE", "r"), c("ARMED", "l")], arrow_end=True, lw=1.3)
    ax.text(5.3, ym + 0.15, "arm(test point id,\nmetadata)", ha="center", va="bottom",
            fontsize=7.2, family="monospace")
    line(ax, [c("ARMED", "r"), c("RECORDING", "l")], arrow_end=True, lw=1.3)
    ax.text(12.0, ym + 0.15, "trigger: software\ncommand or hw edge", ha="center", va="bottom",
            fontsize=7.0)
    ax.text(12.1, ym - 0.15, "/ copy 0.5 s\npre-trigger", ha="center", va="top", fontsize=7.4,
            color=BLUE)
    line(ax, [(16.2, 10.4), (16.2, 7.3 + H)], arrow_end=True, ls=(0, (3, 2)), color=BLUE)
    line(ax, [c("RECORDING", "b", 0.4), c("FLUSH", "t", 0.4)], arrow_end=True, lw=1.3)
    ax.text(16.1, 5.15, "2.0 s\ncaptured", ha="left", va="center", fontsize=7.4)
    line(ax, [c("FLUSH", "l"), c("CLOSED", "r")], arrow_end=True, lw=1.3)
    ax.text(8.7, 1.3 + H / 2 - 0.15, "write · SHA-256 · fsync · atomic rename", ha="center",
            va="top", fontsize=7.4)
    line(ax, [c("CLOSED", "t", -0.6), c("IDLE", "b", -0.6)], arrow_end=True, lw=1.3)
    ax.text(0.85, 5.15, "file\nready", ha="right", va="center", fontsize=7.4)
    # error transitions (dashed red)
    ex, ey = st["ERROR"]
    pairs = [(c("ARMED", "b"), (ex + W / 2, ey + H)),
             ((14.3, 7.3), (ex + W, ey + H - 0.2)),
             ((14.3, 1.3 + H), (ex + W, ey + H / 2)),
             ((3.5, 1.3 + H), (ex, ey + H / 2))]
    for s_, t_ in pairs:
        line(ax, [s_, t_], arrow_end=True, color=RED, ls=(0, (4, 2)))
    # acknowledge back to IDLE
    ax.annotate("", xy=(2.5, 7.3), xytext=(ex, ey + H - 0.25),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.3, mutation_scale=10,
                                connectionstyle="arc3,rad=-0.25", shrinkA=0, shrinkB=0))
    ax.text(4.6, 6.75, "acknowledge", ha="left", va="center", fontsize=7.4)
    ax.text(ex + W / 2, ey - 0.15, "from any state: sequence gap,\noverrun or PTP unlock\n"
            "/ flag written into file header", ha="center", va="top", fontsize=7.2, color=RED)
    save(fig, "08", "fig-8-3-logger-state-machine")


# ----------------------------------------------------------------------------
# Figure 8.4 — time error between Node P and Node M over one hour
# ----------------------------------------------------------------------------
def fig_8_4():
    rng = np.random.default_rng(4)
    t = np.linspace(0, 3600, 36001)              # s, 0.1 s steps
    free = 100e-6 * t
    # NTP: residual drift between corrections, steps at poll intervals 64..1024 s
    rate = 4.5e-3 / 1024
    ntp = np.empty_like(t)
    tc, edges = 0.0, []
    while tc < 3600:
        edges.append(tc)
        tc += rng.choice([64, 128, 256, 512, 1024], p=[0.15, 0.25, 0.25, 0.2, 0.15])
    edges.append(1e9)
    for a, b in zip(edges[:-1], edges[1:]):
        mk = (t >= a) & (t < b)
        ntp[mk] = 0.5e-3 + rate * (t[mk] - a)
    ntp = np.minimum(ntp, 5e-3)
    ptp = np.clip(150e-9 + 45e-9 * rng.standard_normal(t.size), 50e-9, 250e-9)
    tm = t / 60

    fig, ax = new_fig(6.4, 3.9)
    ax.axhspan(1e-6, 2, color="#FDECEA", zorder=0)
    ax.text(59, 1.6e-6, "above 1 µs: violates R3 (P–M ≤ 1 µs)", ha="right", va="bottom",
            fontsize=7.8, color=RED)
    ax.axhspan(600e-6, 735e-6, color="#E6E6E6", zorder=1)
    ax.text(1.0, 560e-6, "uncompensated filter delay, 664 µs", ha="left", va="top",
            fontsize=7.8, color=INK, zorder=3)
    ax.semilogy(tm[1:], free[1:], color=ORANGE, lw=1.8, zorder=2)
    ax.semilogy(tm, ntp, color=BLUE, lw=1.1, zorder=2)
    ax.fill_between(tm, 50e-9, 250e-9, color=GREEN, alpha=0.25, lw=0, zorder=1)
    ax.semilogy(tm[::40], ptp[::40], color=GREEN, lw=0.5, zorder=2)
    ax.text(2.5, 0.27, "free-running crystals, 100 ppm worst case: 0.36 s after 60 min",
            fontsize=8, color=ORANGE, ha="left", va="bottom")
    ax.text(30, 1.0e-2, "NTP-corrected software timestamps (0.5–5 ms, steps every 64–1024 s)",
            fontsize=8, color=BLUE, ha="center", va="bottom")
    ax.text(30, 330e-9, "PTP, hardware timestamps, disciplined sample clocks: 50–250 ns",
            fontsize=8, color=GREEN, ha="center", va="bottom")
    ax.set_xlim(0, 60)
    ax.set_ylim(1e-8, 1)
    ax.set_xlabel("Time (min)")
    ax.set_ylabel("|Time error| Node P – Node M (s)")
    ax.set_yticks([1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1])
    ax.set_yticklabels(["10 ns", "100 ns", "1 µs", "10 µs", "100 µs", "1 ms", "10 ms", "100 ms", "1 s"])
    save(fig, "08", "fig-8-4-node-time-error")


# ----------------------------------------------------------------------------
# Figure 8.5 — ping-pong DMA timing on Node M
# ----------------------------------------------------------------------------
def fig_8_5():
    fig, ax = plt.subplots(figsize=(6.8, 4.6))
    rows = ["DRDY\n51.2 kHz", "DMA write\npointer", "DMA\ninterrupts", "Acquisition\ntask",
            "Network\ntask", "Example:\n12 ms host stall\n(no SDRAM ring)"]
    ys = [5.0, 4.0, 3.0, 2.0, 1.0, -0.1]
    hgt = 0.55
    fs = 7.4
    for y in ys:
        ax.axhline(y - hgt / 2, color="#E4E4E4", lw=0.6, zorder=0)
    # row 1: DRDY, one tick per frame (2048 in 40 ms)
    tk = np.arange(0, 40, 1e3 / 51200)
    ax.vlines(tk, ys[0] - hgt / 2, ys[0] + hgt / 2, color="#666666", lw=0.12)
    ax.text(20, ys[0] + hgt / 2 + 0.05, "one DRDY per frame, 19.53 µs apart (2048 in 40 ms)",
            ha="center", va="bottom", fontsize=fs, color=GREY)
    # row 2: halves + pointer ramp
    for i, lab in enumerate("ABAB"):
        x0 = 10 * i
        ax.add_patch(Rectangle((x0, ys[1] - hgt / 2), 10, hgt, fc=BLUE if lab == "A" else SKY,
                               alpha=0.28, ec=INK, lw=0.8))
        ax.plot([x0, x0 + 10], [ys[1] - hgt / 2, ys[1] + hgt / 2], color=INK, lw=0.9)
        ax.text(x0 + 2.4, ys[1] + 0.07, f"half {lab}", ha="center", va="center", fontsize=8,
                weight="bold")
        ax.text(x0 + 7.6, ys[1] - 0.12, "512 frames", ha="center", va="center", fontsize=6.8,
                color=GREY)
    # row 3: interrupts
    for x, lab in [(10, "HT"), (20, "TC"), (30, "HT"), (40, "TC")]:
        ax.annotate("", xy=(x, ys[2] + hgt / 2), xytext=(x, ys[2] - hgt / 2),
                    arrowprops=dict(arrowstyle="-|>", color=ORANGE, lw=1.4, mutation_scale=9))
        ax.text(x - 0.35, ys[2], lab, ha="right", va="center", fontsize=fs, color=ORANGE)
    ax.text(10.8, ys[2], "HT = half-complete\nTC = complete", fontsize=6.8, va="center",
            color=GREY)
    # row 4: acquisition task, 0.55 ms per block
    for x0 in (10, 20, 30):
        ax.add_patch(Rectangle((x0, ys[3] - hgt / 2), 0.55, hgt, fc=GREEN, ec=INK, lw=0.6))
    ax.text(10.9, ys[3], "A: 10.00–10.55 ms", fontsize=fs, va="center")
    ax.text(20.9, ys[3], "B: 20.00–20.55 ms", fontsize=fs, va="center")
    ax.text(30.9, ys[3], "scale, statistics,\npacketize", fontsize=fs, va="center")
    # row 5: network task
    for x0 in (10.55, 20.55, 30.55):
        ax.add_patch(Rectangle((x0, ys[4] - hgt / 2), 0.65, hgt, fc=PINK, ec=INK, lw=0.6))
    ax.text(11.6, ys[4], "A sent, done\nby 11.2 ms", fontsize=fs, va="center")
    ax.text(31.6, ys[4], "12 UDP packets per\nblock, then half released", fontsize=fs,
            va="center")
    # deadline arrow between rows 4 and 5
    yd = 1.45
    ax.annotate("", xy=(20, yd), xytext=(10, yd),
                arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=1.0, mutation_scale=9))
    ax.text(15, yd + 0.04, "deadline for half A: 10 ms", ha="center", va="bottom", fontsize=fs)
    # row 6: stall example
    y6 = ys[5]
    ax.add_patch(Rectangle((10.55, y6 - hgt / 2), 12.0, hgt, fc="#FDECEA", ec=RED, lw=1.0,
                           ls=(0, (4, 2))))
    ax.text(15.0, y6, "host stall: A held", ha="center", va="center", fontsize=fs, color=RED)
    ax.plot([20, 20], [y6 - 0.45, y6 + 0.45], color=RED, lw=1.2, ls=(0, (3, 2)))
    ax.text(20.15, y6 + 0.42, "DMA re-enters A", ha="left", va="bottom", fontsize=6.8, color=RED)
    ax.text(22.9, y6, "release at 22.6 ms > 20 ms:\noverrun++ · gap flag written",
            fontsize=fs, va="center", color=RED)
    ax.set_yticks(ys)
    ax.set_yticklabels(rows, fontsize=8)
    ax.tick_params(axis="y", length=0)
    ax.set_xlim(0, 40.5)
    ax.set_ylim(-0.7, 5.6)
    ax.set_xticks(np.arange(0, 41, 5))
    ax.set_xlabel("Time (ms)")
    ax.spines["left"].set_visible(False)
    save(fig, "08", "fig-8-5-pingpong-timing")


# ----------------------------------------------------------------------------
# Figure 8.6 — shared 97 Hz reference sine, before and after delay compensation
# ----------------------------------------------------------------------------
def fig_8_6():
    F = 97.0
    rng = np.random.default_rng(7)

    def capture(fs, n, d, noise):
        t = np.arange(n) / fs
        return t, np.sin(2 * np.pi * F * (t - d)) + rng.normal(0, noise, n)

    def phase(t, x):
        A = np.column_stack([np.sin(2 * np.pi * F * t), np.cos(2 * np.pi * F * t), np.ones_like(t)])
        s, c, _ = np.linalg.lstsq(A, x, rcond=None)[0]
        return np.arctan2(c, s)

    # same simulation as the listing of Section 8.10
    GD = 34 / 51_200
    tP, xP = capture(1_000_000, 200_000, 0.0, 1e-3)
    tM, xM = capture(51_200, 10_240, GD + 0.35e-6, 1e-3)

    def skew(tm):
        d = (phase(tP, xP) - phase(tm, xM)) / (2 * np.pi * F)
        return (d + 0.5 / F) % (1 / F) - 0.5 / F

    raw, res = skew(tM), skew(tM - GD)
    fig = plt.figure(figsize=(6.8, 5.2))
    gs = fig.add_gridspec(2, 2, width_ratios=[2.6, 1], hspace=0.42, wspace=0.32)
    a1 = fig.add_subplot(gs[0, :])
    a2 = fig.add_subplot(gs[1, 0])
    a3 = fig.add_subplot(gs[1, 1])
    mP = tP <= 0.0205
    mM = tM <= 0.0205
    step = 8
    for ax, tm_, title in [(a1, tM, "Before: Node M timestamped at converter output"),
                           (a2, tM - GD, "After: Node M timestamps − 34/51 200 s")]:
        ax.plot(tP[mP] * 1e3, xP[mP], color=BLUE, lw=1.3, label="Node P, 1 MSa/s (line)")
        ax.plot(tm_[mM][::step] * 1e3, xM[mM][::step], "o", ms=3.0, color=ORANGE,
                label="Node M, 51.2 kSa/s (dots, every 8th sample shown)")
        ax.set_xlim(0, 20)
        ax.set_ylim(-1.1, 1.1)
        ax.set_ylabel("Normalized amplitude")
        ax.set_xlabel("Time (ms)")
        ax.set_title(title, fontsize=9.5, loc="left")
        ax.axhline(0, color=GREY, lw=0.5)
    a1.legend(loc="lower center", bbox_to_anchor=(0.5, 1.12), ncol=2, fontsize=7.8)
    zc = 1 / F
    a1.annotate("", xy=((zc + GD) * 1e3, 0.0), xytext=(zc * 1e3, 0.0),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.2, mutation_scale=9))
    a1.annotate(f"Node M lags by {raw * 1e3:.3f} ms\n= {360 * F * raw:.1f}° at 97 Hz",
                xy=((zc + GD / 2) * 1e3, 0.03), xytext=(5.6, 0.62), fontsize=8,
                arrowprops=dict(arrowstyle="-", color=GREY, lw=0.7))
    a2.add_patch(Rectangle((zc * 1e3 - 0.35, -0.25), 0.7, 0.5, fill=False, ec=INK, lw=0.8))
    a2.text(zc * 1e3 + 0.5, -0.3, "zoom →", fontsize=7.6, ha="left", va="top")
    # zoom panel: fitted sines near the zero crossing at 1/F
    tt = np.linspace(-1e-6, 1e-6, 401)
    a3.plot(tt * 1e6, np.sin(2 * np.pi * F * tt) * 1e3, color=BLUE, lw=1.3, label="P fit")
    a3.plot(tt * 1e6, np.sin(2 * np.pi * F * (tt - res)) * 1e3, color=ORANGE, lw=1.3, ls="--",
            label="M fit")
    a3.axhline(0, color=GREY, lw=0.5)
    a3.annotate("", xy=(res * 1e6, 0), xytext=(0, 0),
                arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.8, mutation_scale=7))
    a3.text(0.1, -0.15, f"residual\n{res * 1e6:.2f} µs", ha="left", va="top", fontsize=7.8)
    a3.set_xlim(-1, 1)
    a3.set_ylim(-0.65, 0.65)
    a3.set_xlabel("t − zero crossing (µs)")
    a3.set_ylabel("Amplitude (×10⁻³)")
    a3.set_title("Zoom: sine fits", fontsize=9.5, loc="left")
    a3.legend(loc="upper left", fontsize=7.4)
    save(fig, "08", "fig-8-6-reference-sine-alignment")


if __name__ == "__main__":
    fig_8_1()
    fig_8_2()
    fig_8_3()
    fig_8_4()
    fig_8_5()
    fig_8_6()
