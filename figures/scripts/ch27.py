"""Figures for Chapter 27 — Practical Signal Processing.

Run from the repository root:  python figures/scripts/ch27.py
"""
import sys
from math import comb
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402
from scipy import signal, ndimage  # noqa: E402
from scipy.stats import norm  # noqa: E402

from figstyle import COLORS, INK, box, save, schematic, new_fig  # noqa: E402

BLUE, ORANGE, GREEN, PINK, YELLOW, SKY = COLORS[:6]
RED = "#C62828"
GREY = "#777777"


def _arrow(ax, p0, p1, color=INK, text="", fs=7, dx=0.0, dy=0.12, ha="center", both=False):
    ax.annotate("", xy=p1, xytext=p0,
                arrowprops=dict(arrowstyle="<|-|>" if both else "-|>", color=color, lw=1.0,
                                shrinkA=0, shrinkB=0, mutation_scale=9))
    if text:
        ax.text((p0[0] + p1[0])/2 + dx, (p0[1] + p1[1])/2 + dy, text, fontsize=fs, ha=ha,
                va="bottom", color=color)


# ----------------------------------------------------------------------------
# Figure 27.1 — node architecture
# ----------------------------------------------------------------------------
def fig_27_1():
    fig, ax = schematic(6.8, 5.0, xlim=(0, 17.6), ylim=(0, 13))
    # sensors
    sens = [(11.5, "ADXL1002, motor DE radial"), (10.5, "ADXL1002, motor DE axial"),
            (9.5, "ADXL1002, pump radial"), (8.5, "MEMS mic, 20 dB preamp")]
    for y, t in sens:
        box(ax, 0.1, y - 0.4, 4.1, 0.8, t, fc="#E3F0FA", fontsize=6.1)
    ax.text(2.1, 12.35, "Sensors (accelerometers 40 mV/g)", ha="center", fontsize=7.5, weight="bold")
    box(ax, 0.1, 5.4, 4.0, 1.2, "MLX90640 thermal array\n32 × 24 px, 2 frames/s", fc="#FDF1DC", fontsize=7)
    box(ax, 0.1, 3.5, 4.0, 1.2, "Optical tachometer\n1 pulse/rev", fc="#FDF1DC", fontsize=7)
    # RC and ADC
    box(ax, 4.9, 7.9, 2.2, 4.2, "Differential\nRC per\nchannel\n\n2 × 499 Ω\n2.2 nF\nfc = 72 kHz",
        fc="#F2F2F2", fontsize=7)
    for y, _ in sens:
        _arrow(ax, (4.2, y), (4.9, y))
    box(ax, 7.7, 7.9, 3.0, 4.2, "AD7768-4\n24-bit ΔΣ\n4-channel\nsimultaneous\nwideband FIR\ndecimator\n32 kS/s",
        fc="#E6F4EA", fontsize=7)
    for y, _ in sens:
        _arrow(ax, (7.1, y), (7.7, y))
    # MCU
    mx, my, mw, mh = 12.2, 3.3, 5.3, 9.0
    box(ax, mx, my, mw, mh, "", fc="#EFE6F5")
    ax.text(mx + mw/2, my + mh - 0.3, "STM32H723\nCortex-M7, 550 MHz", ha="center", va="top",
            fontsize=8, weight="bold")
    box(ax, mx + 0.3, 9.6, mw - 0.6, 1.2, "SAI (TDM slave) + DMA →\nping-pong 2 × 256 frames\n"
        "(non-cacheable)", fc="white", fontsize=6.6)
    tasks = [(8.3, "DSP task (highest priority)"), (7.3, "feature / FFT task"),
             (6.3, "thermal task (I²C)"), (5.3, "comms task")]
    for y, t in tasks:
        box(ax, mx + 0.3, y - 0.4, mw - 0.6, 0.8, t, fc="white", fontsize=6.8)
    box(ax, mx + 0.3, 3.6, mw - 0.6, 0.8, "timer capture (tacho)", fc="white", fontsize=6.8)
    _arrow(ax, (10.7, 10.2), (mx + 0.3, 10.2), text="ADC data\nport", fs=6.5, dy=0.1)
    # thermal on I2C and tacho
    ax.plot([4.1, 11.6, 11.6], [6.0, 6.0, 6.3], color=INK, lw=1.0)
    _arrow(ax, (11.6, 6.3), (mx + 0.3, 6.3))
    ax.text(7.8, 6.1, "I²C", fontsize=7, ha="center", va="bottom")
    _arrow(ax, (4.1, 4.0), (mx + 0.3, 4.0), text="pulse → TIM capture", fs=6.8, dy=0.08)
    # network
    box(ax, 12.2, 0.6, 2.5, 1.5, "Modbus TCP\n→ PLC", fc="#FDF1DC", fontsize=7)
    box(ax, 15.0, 0.6, 2.5, 1.5, "MQTT →\nCM server", fc="#FDF1DC", fontsize=7)
    _arrow(ax, (13.45, my), (13.45, 2.1))
    _arrow(ax, (16.25, my), (16.25, 2.1))
    ax.text(14.85, 2.65, "Ethernet", ha="center", fontsize=7)
    # power
    box(ax, 0.1, 0.6, 9.8, 1.5, "24 V DC in → DC-DC → 5 V and 3.3 V rails (analog / digital)\n"
        "node input power ≈ 1.0 W", fc="#F2F2F2", fontsize=7)
    ax.text(5.0, 2.4, "features only leave the node; raw waveforms on request", fontsize=6.8,
            style="italic", color=GREY, ha="center")
    save(fig, "27", "fig-27-1-pump-node-architecture")


# ----------------------------------------------------------------------------
# Figure 27.2 — anti-alias chain
# ----------------------------------------------------------------------------
def fig_27_2():
    fs = 32e3
    f = np.logspace(2, np.log10(2e5), 3000)
    r = f/21e3
    sens = 20*np.log10(np.abs(1/(1 - r**2 + 1j*r/10)))
    rc = 20*np.log10(np.abs(1/(1 + 1j*f/72e3)))
    sinc3 = 20*np.log10(np.maximum(np.abs(np.sinc(f/fs))**3, 1e-9))
    # wideband FIR decimator: flat to 0.4 ODR, >= 105 dB from 0.5 ODR (datasheet-type mask)
    fir = np.where(f <= 12.8e3, 0.0,
                   np.where(f >= 16e3, -110.0, -110.0*np.clip((f - 12.8e3)/3.2e3, 0, 1)**1.5))
    fig, ax = new_fig(6.4, 4.0)
    ax.axvspan(100, 10e3, color=GREEN, alpha=0.10, lw=0)
    ax.text(900, -128, "analysis band\n0–10 kHz", fontsize=7.5, color=GREEN, ha="center")
    ax.axvspan(22e3, 42e3, color=RED, alpha=0.10, lw=0)
    ax.text(30.3e3, -135, "22–42 kHz\nfolds onto\n0–10 kHz", fontsize=7, color=RED, ha="center",
            va="bottom")
    ax.semilogx(f, sens, color=ORANGE, label="Sensor, 21 kHz resonance, Q = 10")
    ax.semilogx(f, rc, color=GREY, lw=1.2, label="Input RC, fc = 72 kHz")
    ax.semilogx(f, sinc3, color=BLUE, ls="--", lw=1.4, label="sinc³ decimator, 32 kS/s")
    ax.semilogx(f, fir, color=GREEN, lw=1.6, label="Wideband FIR decimator, 32 kS/s")
    ax.axhline(-60, color=INK, ls=":", lw=1.0)
    ax.text(120, -57, "R3: −60 dB alias rejection", fontsize=7.5, va="bottom")
    g22 = np.interp(22e3, f, sens) + np.interp(22e3, f, sinc3)
    ax.plot([22e3], [g22], "o", color=RED, ms=6, zorder=5)
    ax.annotate(f"22 kHz: sensor {np.interp(22e3, f, sens):+.1f} dB,\nsinc³ {np.interp(22e3, f, sinc3):.1f} dB,"
                f" net {g22:.1f} dB", xy=(22e3, g22), xytext=(1.2e3, -30), fontsize=7.5, color=RED,
                arrowprops=dict(arrowstyle="-", color=RED, lw=0.7))
    for n in (32e3, 64e3, 96e3):
        ax.text(n*1.04, -96, f"{n/1e3:.0f}k", fontsize=6.5, color=BLUE, ha="center")
    ax.set_xlim(100, 2e5); ax.set_ylim(-140, 25)
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Gain (dB)")
    ax.legend(loc="lower left", fontsize=7.3, bbox_to_anchor=(0.0, 0.18))
    save(fig, "27", "fig-27-2-anti-alias-chain")


# ----------------------------------------------------------------------------
# Figure 27.3 — raw and envelope spectra (the Section 27.5 simulation)
# ----------------------------------------------------------------------------
def _simulate():
    rng = np.random.default_rng(7)
    fs, T = 32_000, 5.12
    t = np.arange(int(fs * T)) / fs
    fr, bpfo = 1480 / 60, 74.902
    x = 0.050 * np.sin(2*np.pi*fr*t) + 0.020 * np.sin(2*np.pi*3*fr*t)
    x += 2.5e-3 * np.sqrt(fs / 2 / 10e3) * rng.standard_normal(t.size)
    hits = np.cumsum(np.full(int(T * bpfo), 1 / bpfo) * (1 + 0.01 * rng.standard_normal(int(T * bpfo))))
    ring = np.exp(-800 * t[:200]) * np.sin(2 * np.pi * 4_500 * t[:200])
    for k in (hits * fs).astype(int):
        seg = slice(k, min(k + 200, t.size))
        x[seg] += 0.02 * ring[:seg.stop - k]
    sos_bp = signal.butter(4, [2_000, 8_000], btype='bandpass', fs=fs, output='sos')
    y = signal.sosfilt(sos_bp, x)
    env = signal.decimate(np.abs(y), 20, ftype='fir', n=231)
    env -= env.mean()
    E = np.abs(np.fft.rfft(env * np.hanning(env.size)))
    fe = np.fft.rfftfreq(env.size, 20 / fs)
    w = np.hanning(x.size)
    X = 2*np.abs(np.fft.rfft(x * w))/w.sum()                    # line amplitude, g peak
    fx = np.fft.rfftfreq(x.size, 1 / fs)
    return fx, X, fe, E, bpfo


def fig_27_3():
    fx, X, fe, E, bpfo = _simulate()
    floor = np.median(E[(fe > 20) & (fe < 400)])
    Edb = 20*np.log10(E/floor)
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.4, 5.0))
    m = fx <= 500
    a1.semilogy(fx[m], X[m], color=BLUE, lw=0.8)
    a1.axvline(bpfo, color=RED, ls="--", lw=1.0)
    a1.text(bpfo + 6, 1.5e-3, "BPFO 74.90 Hz:\nno line", color=RED, fontsize=7.5, va="center")
    a1.annotate("1× 24.67 Hz, 0.05 g", xy=(24.67, 0.05), xytext=(110, 0.045), fontsize=7.5,
                arrowprops=dict(arrowstyle="-", lw=0.6))
    a1.annotate("3× 74.00 Hz, 0.02 g", xy=(74.0, 0.02), xytext=(160, 0.011), fontsize=7.5,
                arrowprops=dict(arrowstyle="-", lw=0.6))
    a1.set_xlim(0, 500); a1.set_ylim(1e-6, 0.1)
    a1.set_ylabel("Acceleration (g peak)")
    a1.set_xlabel("Frequency (Hz)")
    a1.set_title("Raw spectrum, 32 kS/s, 5.12 s, Hann", fontsize=9, loc="left")
    m2 = fe <= 400
    a2.axvspan(60, 90, color=GREEN, alpha=0.12, lw=0)
    a2.text(75, -9, "search band", fontsize=7, color=GREEN, ha="center", va="bottom", bbox=dict(fc="white", ec="none", pad=0.5))
    a2.plot(fe[m2], Edb[m2], color=ORANGE, lw=0.8)
    for k in (1, 2, 3):
        b = (fe > k*bpfo - 2) & (fe < k*bpfo + 2)
        i = np.argmax(Edb[b])
        fk, vk = fe[b][i], Edb[b][i]
        a2.text(fk + 5, vk, f"{fk:.1f} Hz\n{vk:+.1f} dB", fontsize=7.3, va="center")
    a2.axhline(0, color=GREY, lw=0.6, ls=":")
    a2.set_xlim(0, 400); a2.set_ylim(-10, 45)
    a2.set_xlabel("Frequency (Hz)")
    a2.set_ylabel("Envelope (dB re median floor)")
    a2.set_title("Envelope spectrum, 2–8 kHz band, 1.6 kS/s, 8192 points", fontsize=9, loc="left")
    fig.tight_layout(h_pad=1.0)
    save(fig, "27", "fig-27-3-raw-vs-envelope-spectrum")


# ----------------------------------------------------------------------------
# Figure 27.4 — thermal frame (the Section 27.7 listing)
# ----------------------------------------------------------------------------
def fig_27_4():
    rng = np.random.default_rng(3)
    frame = 28.0 + 0.1 * rng.standard_normal((24, 32))
    frame[8:18, 6:22] = 41.0 + 0.1 * rng.standard_normal((10, 16))
    frame[11:14, 22:25] = 55.0 + 0.1 * rng.standard_normal((3, 3))
    frame[5, 27] = -40.0
    bad = (frame < -20) | (frame > 300)
    med = ndimage.median_filter(frame, size=3)
    clean = np.where(bad, med, frame)
    roi = (slice(9, 16), slice(20, 27))
    ref = (slice(9, 17), slice(8, 18))
    dT = clean[roi].max() - np.median(clean[ref])
    hot = clean > np.median(clean[ref]) + 10.0
    lab, n = ndimage.label(hot)
    sizes = ndimage.sum(hot, lab, range(1, n + 1))
    cy, cx = ndimage.center_of_mass(hot, lab, int(np.argmax(sizes)) + 1)
    fig, ax = plt.subplots(figsize=(6.4, 4.4))
    shown = np.ma.masked_where(bad, frame)
    cmap = plt.get_cmap("inferno").copy()
    cmap.set_bad("#33CCFF")
    im = ax.imshow(shown, cmap=cmap, vmin=25, vmax=60, origin="upper",
                   extent=(-0.5, 31.5, 23.5, -0.5))
    cb = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.02)
    cb.set_label("Temperature (°C)")
    ax.add_patch(Rectangle((19.5, 8.5), 7, 7, fill=False, ec="white", lw=1.8))
    ax.text(26.6, 8.3, "bearing ROI", color="white", fontsize=7.5, ha="right", va="bottom")
    ax.add_patch(Rectangle((7.5, 8.5), 10, 8, fill=False, ec="#9FE7FF", lw=1.6, ls="--"))
    ax.text(7.6, 16.8, "reference ROI (motor frame)", color="#9FE7FF", fontsize=7.5, va="top")
    ax.contour(np.arange(32), np.arange(24), (lab == np.argmax(sizes) + 1).astype(float), [0.5],
               colors=[GREEN], linewidths=1.4)
    ax.plot([cx], [cy], "+", color=GREEN, ms=12, mew=2)
    ax.annotate(f"hotspot centroid (row {cy:.1f}, col {cx:.1f})\nrise over frame {dT:.1f} K",
                xy=(cx + 0.3, cy + 0.3), xytext=(17.5, 21.8), color="white", fontsize=7.5,
                arrowprops=dict(arrowstyle="-", color="white", lw=0.8))
    ax.annotate("dead pixel (row 5, col 27)\nreplaced by 3 × 3 median", xy=(27, 5), xytext=(13.0, 3.0),
                color="white", fontsize=7.5, arrowprops=dict(arrowstyle="-", color="white", lw=0.8))
    ax.text(0.3, 23.0, "pixel footprint 30 mm at 1.0 m", color="white", fontsize=7.5)
    ax.set_xticks(range(0, 32, 4)); ax.set_yticks(range(0, 24, 4))
    ax.set_xlabel("Column (pixel)")
    ax.set_ylabel("Row (pixel)")
    for s in ax.spines.values():
        s.set_visible(True)
    save(fig, "27", "fig-27-4-thermal-frame-roi")


# ----------------------------------------------------------------------------
# Figure 27.5 — DSP block timing
# ----------------------------------------------------------------------------
def fig_27_5():
    fig, ax = plt.subplots(figsize=(6.8, 3.9))
    rows = {"DMA (SAI → buffer)": 5, "DSP task (prio. high)": 4, "FFT task": 3, "Thermal task": 2,
            "Comms task (prio. low)": 1}
    h = 0.55
    for name, y in rows.items():
        ax.axhline(y, color="#EEEEEE", lw=0.8, zorder=0)
    # DMA halves
    for k in range(5):
        half = "A" if k % 2 == 0 else "B"
        ax.add_patch(Rectangle((8*k, rows["DMA (SAI → buffer)"] - h/2), 8, h,
                               fc=SKY if half == "A" else "#BFE3F5", ec=INK, lw=0.8))
        ax.text(8*k + 4, rows["DMA (SAI → buffer)"], f"filling half {half}", ha="center", va="center",
                fontsize=7)
    for t in (8, 16, 24, 32):
        ax.annotate("", xy=(t, 4.3), xytext=(t, 5.6),
                    arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.0, mutation_scale=8))
        ax.text(t, 5.65, "IRQ", color=RED, fontsize=6.5, ha="center", va="bottom")
    # DSP bursts 0.25 ms after each interrupt
    dsp = [(t, 0.25) for t in (8, 16, 24, 32)]
    for t0, d in dsp:
        ax.add_patch(Rectangle((t0, 4 - h/2), d, h, fc=RED, ec=RED))
    ax.text(8.5, 4, "0.25 ms on the half just filled (A)", fontsize=6.8, va="center")
    ax.text(16.5, 4.38, "(B)", fontsize=6.8, va="center")
    # FFT task: 0.9 ms, pre-empted at 16 ms by the DSP burst
    ax.add_patch(Rectangle((15.4, 3 - h/2), 0.6, h, fc=BLUE, ec=BLUE))
    ax.add_patch(Rectangle((16.25, 3 - h/2), 0.3, h, fc=BLUE, ec=BLUE))
    ax.plot([16.0, 16.25], [3, 3], color=BLUE, ls=":", lw=1.2)
    ax.text(16.9, 3, "raw FFT 0.9 ms: pre-empted at 16 ms, resumed", fontsize=6.8, va="center")
    # thermal 0.3 ms at 20 ms
    ax.add_patch(Rectangle((20.0, 2 - h/2), 0.3, h, fc=ORANGE, ec=ORANGE))
    ax.text(20.7, 2, "thermal frame 0.3 ms", fontsize=6.8, va="center")
    # comms bursts
    for t0 in (3.0, 11.5, 27.0, 35.0):
        ax.add_patch(Rectangle((t0, 1 - h/2), 0.15, h, fc=GREEN, ec=GREEN))
    ax.text(3.4, 1, "network", fontsize=6.8, va="center")
    # deadline annotation
    ax.annotate("", xy=(24, 3.75), xytext=(16.25, 3.75),
                arrowprops=dict(arrowstyle="<|-|>", color=GREY, lw=0.8, mutation_scale=8))
    ax.text(20.1, 3.62, "deadline = next IRQ (8 ms)", fontsize=6.8, color=GREY, ha="center", va="top")
    ax.text(40.0, 0.25, "overrun detected when notification count > 1", fontsize=7, color=RED,
            ha="right", va="bottom", style="italic")
    ax.set_yticks(list(rows.values())); ax.set_yticklabels(list(rows.keys()), fontsize=8)
    ax.set_xlim(0, 40); ax.set_ylim(0.2, 6.0)
    ax.set_xticks(range(0, 41, 8))
    ax.set_xlabel("Time (ms)")
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    save(fig, "27", "fig-27-5-dsp-block-timing")


# ----------------------------------------------------------------------------
# Figure 27.6 — detection ROC (binormal model of the rig and soak results)
# ----------------------------------------------------------------------------
def _p3of5(p):
    return sum(comb(5, j) * p**j * (1 - p)**(5 - j) for j in range(3, 6))


def fig_27_6():
    th = np.linspace(0.0, 8.0, 801)
    # feature: (label, evaluations per month, shift of the fault-mean in baseline sigma, colour)
    feats = [("Envelope line at BPFO (5.12 s)", 30*86400/5.12, 4.6, ORANGE),
             ("Kurtosis, band-passed 2–8 kHz (1 s)", 30*86400, 3.85, BLUE),
             ("Overall RMS (1 s)", 30*86400, 2.15, GREY)]
    fig, ax = new_fig(6.4, 4.0)
    for lab, n, d, c in feats:
        pfa = np.array([_p3of5(norm.sf(x)) for x in th])*n
        pd = np.array([_p3of5(norm.sf(x - d)) for x in th])
        ok = pfa > 1e-6
        ax.semilogx(pfa[ok], pd[ok], color=c, label=lab)
        if c == ORANGE:
            fa0 = _p3of5(norm.sf(3.5))*n
            pd0 = _p3of5(norm.sf(3.5 - d))
            ax.plot([fa0], [pd0], "o", color=c, ms=7, mfc="white", mew=2, zorder=5)
            ax.annotate(f"operating point 3.5σ, 3 of 5\n({fa0:.0e} per month, P_D = {pd0:.3f})",
                        xy=(fa0, pd0), xytext=(2.0e-5, 0.70), fontsize=7.5,
                        arrowprops=dict(arrowstyle="-", lw=0.7))
    ax.axvline(1, color=RED, ls="--", lw=1.0)
    ax.text(1.15, 0.05, "R6: 1 per\nnode-month", color=RED, fontsize=7.5)
    ax.axhline(0.95, color=GREEN, ls="--", lw=1.0)
    ax.text(1.2e-5, 0.92, "R5: P_D = 0.95", color=GREEN, fontsize=7.5, va="top")
    ax.set_xlim(1e-5, 100); ax.set_ylim(0, 1.02)
    ax.set_xlabel("False alarms per node-month")
    ax.set_ylabel("Probability of detection")
    ax.legend(loc="center right", fontsize=7.5, bbox_to_anchor=(1.0, 0.42))
    ax.text(1.2e-5, 0.30, "Gaussian (binormal) model fitted to rig and soak data:\n"
            "20 fault runs, 240 node-days; threshold swept, 3-of-5 rule", fontsize=7, color=GREY)
    save(fig, "27", "fig-27-6-detection-roc")


if __name__ == "__main__":
    fig_27_1()
    fig_27_2()
    fig_27_3()
    fig_27_4()
    fig_27_5()
    fig_27_6()
