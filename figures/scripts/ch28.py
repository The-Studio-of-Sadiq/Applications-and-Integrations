"""Figures for Chapter 28 — Biomedical Instrumentation.

Run from the repository root:  python figures/scripts/ch28.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle, Polygon, FancyBboxPatch, Ellipse  # noqa: E402
from scipy import signal  # noqa: E402
import schemdraw  # noqa: E402
import schemdraw.elements as elm  # noqa: E402

from figstyle import COLORS, INK, box, save, schematic, new_fig  # noqa: E402

schemdraw.use("matplotlib")
BLUE, ORANGE, GREEN, PINK, YELLOW, SKY = COLORS[:6]
RED = "#C62828"
GREY = "#777777"


def _arrow(ax, p0, p1, color=INK, lw=1.0, both=False):
    ax.annotate("", xy=p1, xytext=p0,
                arrowprops=dict(arrowstyle="<|-|>" if both else "-|>", color=color, lw=lw,
                                shrinkA=0, shrinkB=0, mutation_scale=9))


# ----------------------------------------------------------------------------
# Figure 28.1 — amplitude-frequency map
# ----------------------------------------------------------------------------
def fig_28_1():
    fig, ax = new_fig(6.4, 4.4)
    ax.set_xscale("log"); ax.set_yscale("log")
    sigs = [("EOG", 0.01, 30, 50e-6, 3.5e-3, PINK), ("ECG", 0.05, 150, 0.5e-3, 4e-3, RED),
            ("EMG", 20, 450, 0.05e-3, 5e-3, GREEN), ("EEG", 0.5, 70, 5e-6, 100e-6, BLUE)]
    for name, f0, f1, a0, a1, c in sigs:
        ax.add_patch(Rectangle((f0, a0), f1 - f0, a1 - a0, fc=c, alpha=0.18, ec=c, lw=1.2))
    ax.text(0.012, 6e-5, "EOG", color=PINK, fontsize=8.5, weight="bold")
    ax.text(0.055, 0.56e-3, "ECG", color=RED, fontsize=8.5, weight="bold", ha="left", va="bottom")
    ax.text(300, 1.2e-4, "EMG", color=GREEN, fontsize=8.5, weight="bold", ha="center")
    ax.text(6, 1.2e-5, "EEG", color=BLUE, fontsize=8.5, weight="bold", ha="center")
    # interferers (hatched)
    ax.add_patch(Rectangle((0.01, 1e-3), 0.05 - 0.01, 0.3 - 1e-3, fc="none", ec=GREY, hatch="///", lw=0.8))
    ax.text(0.0105, 1.3e-2, "electrode\noffset\n≤ 300 mV", fontsize=7.3, color=INK, va="bottom", bbox=dict(fc="white", ec="none", pad=0.4))
    ax.add_patch(Rectangle((0.1, 0.1e-3), 10 - 0.1, 10e-3 - 0.1e-3, fc="none", ec=ORANGE, hatch="\\\\",
                           lw=0.8))
    ax.text(0.9, 6e-3, "motion artefact", fontsize=7.3, color=ORANGE, ha="center")
    for k, fh in enumerate([50, 100, 150, 200, 250]):
        top = 10.0 if k == 0 else 10.0/(3*k)
        ax.add_patch(Rectangle((fh*0.96, 1e-3), fh*0.08, top - 1e-3, fc=GREY, alpha=0.55 if k == 0 else 0.3,
                               ec="none"))
    ax.text(44, 0.08, "mains common mode\n1 mV–10 V at 50 Hz\n+ harmonics", fontsize=7.3, ha="right",
            va="center", color=INK)
    ax.axhline(0.403, color=INK, ls="--", lw=1.0)
    ax.text(0.011, 0.45, "ADC full scale ±0.403 V at gain 6", fontsize=7.3, va="bottom")
    ax.axhline(48e-9 if False else 1.0e-6, color="none")
    ax.axhline(48e-9, color=INK, ls="--", lw=1.0)
    # recorder passbands as brackets
    yb1, yb2 = 3.4e-6, 1.6e-6
    for (f0, f1, y, lab, c) in [(0.05, 150, yb1, "ECG mode 0.05–150 Hz", RED),
                                (20, 450, yb2, "EMG mode 20–450 Hz", GREEN)]:
        ax.plot([f0, f1], [y, y], color=c, lw=1.6)
        ax.plot([f0, f0], [y/1.15, y*1.15], color=c, lw=1.6)
        ax.plot([f1, f1], [y/1.15, y*1.15], color=c, lw=1.6)
        ax.text(f0*1.15 if c == RED else 17.0, y*1.12 if c == RED else y, lab, color=c, fontsize=7.3, va="bottom" if c == RED else "center",
                ha="left" if c == RED else "right")
    ax.set_xlim(0.01, 1000); ax.set_ylim(1e-6, 1.0)
    ax.text(0.011, 1.05e-6, "LSB 48 nV (below axis)", fontsize=7.0, color=GREY, va="bottom")
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Amplitude (V)")
    ax.set_yticks([1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1])
    ax.set_yticklabels(["1 µV", "10 µV", "100 µV", "1 mV", "10 mV", "100 mV", "1 V"])
    ax.set_xticks([0.01, 0.1, 1, 10, 100, 1000])
    ax.set_xticklabels(["0.01", "0.1", "1", "10", "100", "1k"])
    save(fig, "28", "fig-28-1-biopotential-map")


# ----------------------------------------------------------------------------
# Figure 28.2 — recorder architecture
# ----------------------------------------------------------------------------
def fig_28_2():
    fig, ax = schematic(6.8, 5.0, xlim=(0, 18.4), ylim=(0, 13.2))
    # electrodes
    for i, e in enumerate(["RA", "LA", "LL", "V5", "RL"]):
        y = 10.8 - i*0.75
        ax.add_patch(plt.Circle((0.55, y), 0.27, fc="#FFF3D6", ec=INK, lw=0.9))
        ax.text(0.55, y, e, fontsize=6.3, ha="center", va="center")
        ax.plot([0.82, 1.9], [y, y], color=INK, lw=0.9)
    ax.text(1.2, 11.55, "snap electrodes,\nshielded cable", fontsize=6.8, ha="center", va="bottom")
    box(ax, 1.9, 7.5, 1.7, 3.8, "J1\nshared\nsocket:\npatient\ncable\nor USB\ncradle", fc="#FDECEC", fontsize=6.6)
    ax.text(1.0, 7.25, "mechanically\nexclusive", fontsize=6.4, color=RED, ha="center", va="top")
    box(ax, 4.0, 7.5, 3.3, 3.8, "Input protection\n+ RFI filter\n\n10 kΩ pulse-rated\nseries R\n47 pF CM, 4.7 nF DM\n"
        "low-leakage clamps", fc="#F2F2F2", fontsize=6.2)
    _arrow(ax, (3.6, 9.4), (4.0, 9.4))
    box(ax, 7.9, 7.0, 3.6, 4.8, "", fc="#E3F0FA")
    ax.text(9.7, 11.55, "ADS1292 AFE", fontsize=8, weight="bold", ha="center", va="top")
    ax.text(9.7, 10.9, "2 × PGA, gain 6\n2 × 24-bit ΔΣ ADC\n1 kS/s\n\nRLD amplifier\n→ 499 kΩ → RL\n\n"
            "lead-off sources 6 nA", fontsize=6.6, ha="center", va="top")
    _arrow(ax, (7.3, 9.4), (7.9, 9.4))
    ax.plot([9.7, 9.7, 3.0, 3.0], [7.0, 6.5, 6.5, 7.5], color=INK, lw=0.9, ls="--")
    ax.text(6.3, 6.35, "RLD → RL electrode", fontsize=6.4, ha="center", va="top")
    # MCU
    box(ax, 12.4, 6.6, 5.4, 5.2, "", fc="#EFE6F5")
    ax.text(15.1, 11.55, "nRF52840", fontsize=8, weight="bold", ha="center", va="top")
    ax.text(15.1, 11.0, "Cortex-M4F 64 MHz, BLE", fontsize=6.8, ha="center", va="top")
    for k, t in enumerate(["31-tap FIR: 1 kS/s → 500 S/s", "QRS detection (status)",
                           "1 s blocks + CRC-32", "file system, 64 KB writes"]):
        box(ax, 12.7, 9.65 - k*0.82, 4.8, 0.65, t, fc="white", fontsize=6.4)
    _arrow(ax, (11.5, 9.4), (12.4, 9.4), both=True)
    ax.text(11.95, 9.2, "SPI\n+ DRDY", fontsize=6.4, ha="center", va="top")
    # side blocks below the MCU
    sides = [(12.4, 4.6, "LIS2DW12\naccel. (I²C)"), (15.0, 4.6, "event button"),
             (12.4, 2.9, "RTC crystal\n32.768 kHz"), (15.0, 2.9, "microSD 4 GB\nload-switched")]
    for x, y, t in sides:
        box(ax, x, y, 2.5, 1.3, t, fc="#FDF1DC", fontsize=6.5)
    for x in (13.65, 16.25):
        ax.plot([x, x], [6.6, 5.9], color=INK, lw=0.9)
    # power
    box(ax, 0.2, 2.5, 3.6, 2.0, "Li-po 3.7 V\n200 mAh\ncharger active\nonly in cradle", fc="#E6F4EA", fontsize=6.6)
    box(ax, 4.4, 3.6, 3.4, 0.95, "buck 3.0 V (digital)", fc="#E6F4EA", fontsize=6.6)
    box(ax, 4.4, 2.4, 3.4, 0.95, "LDO 3.0 V (analog)", fc="#E6F4EA", fontsize=6.6)
    _arrow(ax, (3.8, 4.05), (4.4, 4.05))
    _arrow(ax, (3.8, 2.9), (4.4, 2.9))
    ax.plot([7.8, 9.7, 9.7], [2.9, 2.9, 7.0], color=GREEN, lw=1.0)
    ax.plot([7.8, 11.9, 11.9, 12.4], [4.05, 4.05, 7.2, 7.2], color=GREEN, lw=1.0)
    ax.text(10.0, 3.0, "AVDD", fontsize=6.3, color=GREEN, va="bottom")
    ax.text(10.4, 4.15, "DVDD", fontsize=6.3, color=GREEN, va="bottom")
    # BLE link
    box(ax, 12.4, 0.3, 5.4, 1.5, "clinician tablet\nBLE: hookup check, status only", fc="#F2F2F2",
        fontsize=6.6)
    ax.annotate("", xy=(17.65, 1.8), xytext=(17.65, 6.6),
                arrowprops=dict(arrowstyle="<|-|>", color=BLUE, lw=1.0, ls="--", mutation_scale=9))
    ax.text(17.78, 3.6, "BLE", fontsize=6.6, color=BLUE, rotation=90, va="bottom", ha="left")
    ax.text(0.3, 0.8, "Recording stays on the card; read out after return\n"
            "(USB only in the cradle, patient disconnected)", fontsize=6.6, color=GREY, style="italic")
    save(fig, "28", "fig-28-2-ecg-recorder-architecture")


# ----------------------------------------------------------------------------
# Figure 28.3 — USB leakage path
# ----------------------------------------------------------------------------
def fig_28_3():
    fig, ax = plt.subplots(figsize=(6.8, 5.0))
    ax.axis("off")
    d = schemdraw.Drawing(canvas=ax, show=False)
    d.config(fontsize=7.5, unit=2, lw=1.1)
    # mains source
    d.add(elm.SourceSin().at((0.6, 6.0)).to((0.6, 8.6)))
    d.add(elm.Label().at((0.05, 7.3)).label("230 V\n50 Hz", halign="right", fontsize=7.5))
    d.add(elm.Line().at((0.6, 8.6)).to((3.3, 8.6)))
    d.add(elm.Line().at((0.6, 6.0)).to((0.6, 1.0)))
    d.add(elm.Ground().at((0.6, 1.0)))
    d.add(elm.Label().at((1.15, 1.6)).label("N–E bond at\nsupply transformer", halign="left", fontsize=6.6))
    # Y-capacitor inside the adapter
    d.add(elm.Line().at((3.3, 8.6)).to((3.3, 7.9)))
    d.add(elm.Capacitor().at((3.3, 7.9)).to((3.3, 6.5)))
    d.add(elm.Line().at((3.3, 6.5)).to((3.3, 5.6)))
    d.add(elm.Line().at((3.3, 5.6)).to((5.2, 5.6)))
    d.add(elm.Label().at((3.6, 7.2)).label("Y-cap\n2.2 nF", halign="left", fontsize=7))
    # DC output to laptop, USB to recorder
    d.add(elm.Line().at((5.2, 5.6)).to((6.4, 5.6)))
    d.add(elm.Line().at((8.9, 5.6)).to((10.4, 5.6)))
    d.add(elm.Label().at((9.65, 5.75)).label("USB", valign="bottom", fontsize=7))
    d.add(elm.Line().at((12.8, 5.6)).to((13.6, 5.6)))
    # electrodes to the patient
    for k in range(5):
        d.add(elm.Line().at((13.6, 5.6)).to((14.6, 6.6 - 0.5*k)))
    # bed frame to earth
    d.add(elm.Line().at((16.3, 3.6)).to((16.3, 2.1)))
    d.add(elm.Ground().at((16.3, 2.1)))
    d.draw()
    # boxes drawn as patches (data units = drawing units)
    ax.add_patch(FancyBboxPatch((2.2, 4.9), 3.0, 4.3, boxstyle="round,pad=0.02,rounding_size=0.15",
                                fc="#F6F6F6", ec=INK, lw=1.0, zorder=0))
    ax.text(3.7, 9.45, "class II adapter", fontsize=7.5, ha="center")
    ax.text(2.35, 8.75, "primary", fontsize=6.5, ha="left", va="bottom", color=GREY)
    ax.text(5.1, 5.45, "DC out", fontsize=6.5, ha="right", va="top", color=GREY)
    box(ax, 6.4, 4.8, 2.5, 1.6, "laptop", fc="#E3F0FA", fontsize=7.5)
    box(ax, 10.4, 4.8, 2.4, 1.6, "ECG\nrecorder", fc="#EFE6F5", fontsize=7.5)
    # patient
    ax.add_patch(Ellipse((15.4, 5.7), 1.6, 2.9, fc="#FFE8D6", ec=INK, lw=1.0))
    ax.add_patch(plt.Circle((15.4, 7.6), 0.45, fc="#FFE8D6", ec=INK, lw=1.0))
    ax.text(15.4, 5.6, "patient", fontsize=7, ha="center", rotation=90)
    ax.add_patch(Rectangle((14.0, 3.35), 3.2, 0.25, fc=GREY, ec=INK, lw=0.8))
    ax.text(17.3, 3.47, "earthed\nbed frame", fontsize=6.8, va="center", ha="left")
    ax.plot([15.6, 15.9], [4.3, 3.6], color=INK, lw=1.0)
    # current loop arrows
    red = dict(color=RED, lw=1.8)
    ax.annotate("", xy=(3.0, 6.6), xytext=(3.0, 8.3), arrowprops=dict(arrowstyle="-|>", **red, mutation_scale=10))
    ax.annotate("", xy=(13.4, 6.75), xytext=(5.4, 6.75), arrowprops=dict(arrowstyle="-|>", **red, mutation_scale=10))
    ax.annotate("", xy=(16.0, 2.6), xytext=(16.0, 3.3), arrowprops=dict(arrowstyle="-|>", **red, mutation_scale=10))
    ax.plot([16.0, 16.0, 0.9, 0.9], [2.6, 0.55, 0.55, 5.8], color=RED, lw=1.2, ls="--")
    ax.text(9.8, 7.45, "leakage I = 2π·50 Hz·2.2 nF·230 V = 159 µA", color=RED, fontsize=7.0, ha="center",
            va="bottom", weight="bold")
    ax.text(8.6, 0.65, "return through earth", color=RED, fontsize=7, ha="center", va="bottom")
    ax.text(19.0, 10.1, "limits (patient leakage, NC):\ntype CF 10 µA  ×16 exceeded\n"
            "type BF 100 µA  exceeded", fontsize=7.2, ha="right", va="top",
            bbox=dict(fc="#FFF8E1", ec=GREY, lw=0.6))
    # three fixes
    fixes = [("1  Exclusive connector J1:\npatient cable OR USB,\nnever both (chosen)", GREEN),
             ("2  Firmware VBUS interlock:\nacquisition off, but the\ncurrent path is still present", ORANGE),
             ("3  Isolated USB, barrier 10 pF:\n2π·50·10 pF·230 V = 0.72 µA\n(within CF)", BLUE)]
    for k, (t, c) in enumerate(fixes):
        x0 = 0.2 + k*6.3
        ax.add_patch(FancyBboxPatch((x0, -2.9), 6.0, 2.1, boxstyle="round,pad=0.02,rounding_size=0.15",
                                    fc="white", ec=c, lw=1.4))
        ax.text(x0 + 0.2, -1.85, t, fontsize=7, va="center", ha="left")
    ax.set_aspect("equal")
    ax.set_xlim(-1.4, 19.2); ax.set_ylim(-3.1, 10.3)
    save(fig, "28", "fig-28-3-usb-leakage-path")


# ----------------------------------------------------------------------------
# Figure 28.4 — one lead pair of the front end
# ----------------------------------------------------------------------------
def fig_28_4():
    fig, ax = plt.subplots(figsize=(6.8, 5.0))
    ax.axis("off")
    d = schemdraw.Drawing(canvas=ax, show=False)
    d.config(fontsize=7.5, unit=2, lw=1.1)
    fs = 7
    yA, yB, yR = 6.0, 2.0, -2.2
    for y, lab in [(yA, "E+"), (yB, "E−"), (yR, "RL")]:
        d.add(elm.Dot(open=True).at((0, y)))
        d.add(elm.Label().at((-0.25, y)).label(lab, halign="right", fontsize=8))
    # series resistors
    for y in (yA, yB):
        d.add(elm.Resistor().at((0, y)).to((2.6, y)))
        d.add(elm.Label().at((1.3, y + 0.45)).label("10 kΩ", fontsize=fs))
        d.add(elm.Line().at((2.6, y)).to((9.0, y)))
        d.add(elm.Dot().at((3.6, y)))
        d.add(elm.Dot().at((5.2, y)))
        d.add(elm.Dot().at((7.0, y)))
    d.add(elm.Label().at((1.3, yA + 1.0)).label("pulse-rated MELF", fontsize=6.5))
    # 47 pF to AGND
    for y in (yA, yB):
        d.add(elm.Capacitor().at((3.6, y)).to((3.6, y - 1.4)))
        d.add(elm.Ground().at((3.6, y - 1.4)))
        d.add(elm.Label().at((3.25, y - 0.7)).label("47 pF", halign="right", fontsize=fs))
    # 4.7 nF across the pair
    d.add(elm.Capacitor().at((5.2, yA)).to((5.2, yB)))
    d.add(elm.Label().at((5.55, 4.0)).label("4.7 nF", halign="left", fontsize=fs))
    # clamp diodes
    for y in (yA, yB):
        d.add(elm.Diode().at((7.0, y)).to((7.0, y + 1.3)))
        d.add(elm.Line().at((6.6, y + 1.3)).to((7.4, y + 1.3)))
        d.add(elm.Label().at((7.5, y + 1.3)).label("AVDD", halign="left", fontsize=6.3))
        d.add(elm.Diode().at((7.0, y - 1.4)).to((7.0, y)))
        d.add(elm.Ground().at((7.0, y - 1.4)))
    # IC body
    x0, x1, y0, y1 = 9.0, 17.6, -4.4, 8.6
    for name, y in [("IN1P", yA), ("IN1N", yB), ("RLDOUT", yR), ("RLDINV", -3.5)]:
        d.add(elm.Label().at((x0 + 0.1, y + 0.1)).label(name, halign="left", valign="bottom", fontsize=6.3))
    # lead-off current sources
    d.add(elm.Line().at((10.0, 7.2 - 0.35)).to((10.0, yA)))
    d.add(elm.Line().at((10.0, yB)).to((10.0, 1.35)))
    d.add(elm.Line().at((10.0, 0.65)).to((10.0, 0.25)))
    d.add(elm.Dot().at((10.0, yA)))
    d.add(elm.Dot().at((10.0, yB)))
    d.add(elm.Line().at((10.0, 7.2 + 0.35)).to((10.0, 7.95)))
    d.add(elm.Line().at((9.7, 7.95)).to((10.3, 7.95)))
    d.add(elm.Label().at((10.0, 8.25)).label("AVDD", fontsize=6.0))
    d.add(elm.Ground().at((10.0, 0.25)))
    d.add(elm.Label().at((10.5, 7.2)).label("6 nA", halign="left", fontsize=6.5))
    d.add(elm.Label().at((10.5, 1.0)).label("6 nA", halign="left", fontsize=6.5))
    # inputs to the PGA
    d.add(elm.Line().at((9.0, yA)).to((11.2, yA)))
    d.add(elm.Line().at((11.2, yA)).to((11.2, 4.5)))
    d.add(elm.Line().at((11.2, 4.5)).to((11.8, 4.5)))
    d.add(elm.Line().at((9.0, yB)).to((11.2, yB)))
    d.add(elm.Line().at((11.2, yB)).to((11.2, 3.5)))
    d.add(elm.Line().at((11.2, 3.5)).to((11.8, 3.5)))
    d.add(elm.Line().at((13.3, 4.0)).to((13.8, 4.0)))
    d.add(elm.Line().at((16.2, 4.0)).to((18.4, 4.0)))
    d.add(elm.Label().at((18.5, 4.0)).label("SPI to\nnRF52840", halign="left", fontsize=6.5))
    # common-mode sense to RLD
    d.add(elm.Dot().at((11.2, yA)))
    d.add(elm.Dot().at((11.2, yB)))
    d.add(elm.Line().at((11.2, yB)).to((11.2, 0.0)))
    d.add(elm.Line().at((11.2, 0.0)).to((11.8, 0.0)))
    d.add(elm.Line().at((14.4, -0.6)).to((14.8, -0.6)))
    d.add(elm.Line().at((14.8, -0.6)).to((14.8, yR)))
    d.add(elm.Line().at((14.8, yR)).to((13.6, yR)))
    d.add(elm.Line().at((12.2, yR)).to((9.0, yR)))
    d.add(elm.Line().at((12.9, -3.5)).to((12.9, -2.75)))
    d.add(elm.Line().at((9.0, -3.5)).to((12.9, -3.5)))
    # external integrating feedback and the 499 k output resistor
    d.add(elm.Line().at((9.0, yR)).to((8.4, yR)))
    d.add(elm.Line().at((9.0, -3.5)).to((8.4, -3.5)))
    d.add(elm.Capacitor().at((8.4, yR)).to((8.4, -3.5)))
    d.add(elm.Line().at((8.4, yR)).to((7.0, yR)))
    d.add(elm.Line().at((8.4, -3.5)).to((7.0, -3.5)))
    d.add(elm.Resistor().at((7.0, yR)).to((7.0, -3.5)))
    d.add(elm.Label().at((6.6, -2.85)).label("R_F", halign="right", fontsize=6.5))
    d.add(elm.Label().at((8.0, -4.1)).label("C_F  (integrating feedback)", fontsize=6.5))
    d.add(elm.Dot().at((7.0, yR)))
    d.add(elm.Line().at((7.0, yR)).to((5.4, yR)))
    d.add(elm.Resistor().at((5.4, yR)).to((0.0, yR)))
    d.add(elm.Label().at((2.7, yR + 0.5)).label("499 kΩ", fontsize=fs))
    d.add(elm.Label().at((2.4, yR - 1.25)).label("DC current ≤ 3.0 V / 499 kΩ = 6.0 µA", fontsize=6.5,
                                                 color=RED))
    d.draw()
    # IC outline, PGA, ADC, CM block, RLD amplifier
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc="#E3F0FA", ec=INK, lw=1.2, zorder=0))
    ax.text(x1 - 0.2, y1 - 0.25, "ADS1292", fontsize=9, weight="bold", ha="right", va="top")
    for yc in (7.2, 1.0):
        ax.add_patch(plt.Circle((10.0, yc), 0.35, fc="white", ec=INK, lw=1.1, zorder=3))
        ax.annotate("", xy=(10.0, yc - 0.22), xytext=(10.0, yc + 0.22), zorder=4,
                    arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.9, mutation_scale=7))
    ax.add_patch(Polygon([(11.8, 2.9), (11.8, 5.1), (13.3, 4.0)], closed=True, fc="white", ec=INK, lw=1.1))
    ax.text(12.3, 4.0, "PGA\n×6", fontsize=6.5, ha="center", va="center")
    ax.add_patch(Rectangle((13.8, 3.1), 2.4, 1.8, fc="white", ec=INK, lw=1.1))
    ax.text(15.0, 4.0, "24-bit ΔΣ\n1 kS/s", fontsize=6.5, ha="center", va="center")
    ax.add_patch(Rectangle((13.8, 5.6), 2.4, 0.9, fc="white", ec=INK, lw=1.1))
    ax.text(15.0, 6.05, "VREF 2.42 V", fontsize=6.5, ha="center", va="center")
    ax.plot([15.0, 15.0], [5.6, 4.9], color=INK, lw=1.0)
    ax.text(15.0, 2.3, "full scale\n±2.42 V / 6 = ±403 mV", fontsize=6.5, ha="center", va="center",
            color=RED)
    ax.add_patch(Rectangle((11.8, -1.2), 2.6, 1.6, fc="white", ec=INK, lw=1.1))
    ax.text(13.1, -0.4, "CM sense\n(IN1P+IN1N)/2", fontsize=5.8, ha="center", va="center")
    ax.plot([11.6, 11.6, 12.0], [yA, 0.0, 0.0], color=INK, lw=0.0)
    ax.add_patch(Polygon([(13.6, -1.55), (13.6, -2.85), (12.2, -2.2)], closed=True, fc="white", ec=INK, lw=1.1))
    ax.text(13.15, -2.2, "RLD", fontsize=6.0, ha="center", va="center")
    ax.text(5.2, 7.8, "differential corner\n1/(2π·20 kΩ·4.7 nF) = 1.7 kHz", fontsize=6.5, ha="center",
            color=RED)
    ax.text(7.0, -0.25, "BAV199-class\nlow-leakage clamps", fontsize=6.3, ha="center", va="top")
    ax.set_aspect("equal")
    ax.set_xlim(-1.4, 20.6); ax.set_ylim(-4.8, 9.2)
    save(fig, "28", "fig-28-4-ecg-front-end-circuit")


# ----------------------------------------------------------------------------
# Figure 28.5 — mains interference versus imbalance
# ----------------------------------------------------------------------------
def fig_28_5():
    dz = np.logspace(3, 6, 200)
    vcm = 0.5e-6*51e3                      # 25.5 mV
    fig, ax = new_fig(6.4, 4.0)
    z0 = abs(1/(1/51e3 + 1j*2*np.pi*50*47e-9))
    for C, c in [(47e-12, BLUE), (1e-9, ORANGE)]:
        zcm = 1/(2*np.pi*50*C)
        for A, ls, tag in [(0, "-", "no DRL"), (100, "--", "DRL 40 dB")]:
            vpp = vcm/(1 + A)*dz/zcm*2*np.sqrt(2)*1e6
            lab = f"{'47 pF' if C < 1e-10 else '1 nF'} CM capacitors, {tag}"
            ax.loglog(dz, vpp, color=c, ls=ls, label=lab)
            v0 = vcm/(1 + A)*z0/zcm*2*np.sqrt(2)*1e6
            ax.plot([z0], [v0], "o", color=c, ms=5)
            ax.text(z0*1.15, v0, f"{v0:.2g} µV" if v0 < 10 else f"{v0:.0f} µV", fontsize=7.3,
                    color=c, ha="left", va="center")
    ax.axvline(z0, color=GREY, ls=":", lw=1.0)
    ax.text(z0*0.92, 0.012, "51 kΩ ∥ 47 nF\n|Z| = 40.7 kΩ", fontsize=7.3, color=GREY, va="bottom", ha="right")
    ax.axhline(20, color=RED, ls="--", lw=1.0)
    ax.text(9.5e5, 23, "R5: 20 µV p-p", color=RED, fontsize=7.5, va="bottom", ha="right")
    ax.set_xlim(1e3, 1e6); ax.set_ylim(0.01, 1000)
    ax.set_xlabel("Electrode impedance imbalance |ΔZ| at 50 Hz (Ω)")
    ax.set_ylabel("Differential interference (µV p-p)")
    ax.legend(loc="lower right", fontsize=7.3)
    ax.text(1.15e3, 600, "body displacement current 0.5 µA\nRL electrode 51 kΩ → V_cm = 25.5 mV",
            fontsize=7.2, va="center", ha="left", bbox=dict(fc="white", ec=GREY, lw=0.6))
    save(fig, "28", "fig-28-5-mains-vs-imbalance")


# ----------------------------------------------------------------------------
# Figure 28.6 — Pan-Tompkins stages (the Section 28.9 listing)
# ----------------------------------------------------------------------------
def _qrs_sim():
    fs, T = 500, 120.0
    rng = np.random.default_rng(11)
    t = np.arange(int(fs * T)) / fs
    rr = 60 / 72 + 0.04 * rng.standard_normal(int(T * 72 / 60))
    beats = np.cumsum(rr)
    beats = beats[beats < T - 1]
    ecg = np.zeros_like(t)
    for b in beats:
        for dt, a, w in [(-0.20, 0.15, 0.025), (-0.03, -0.10, 0.008), (0.0, 1.2, 0.010),
                         (0.03, -0.25, 0.008), (0.25, 0.30, 0.040)]:
            ecg += a * np.exp(-0.5 * ((t - b - dt) / w) ** 2)
    x = ecg + 0.5 * np.sin(2 * np.pi * 0.25 * t) + 0.03 * np.sin(2 * np.pi * 50 * t)
    x += 0.015 * rng.standard_normal(t.size)
    emg = signal.sosfilt(signal.butter(4, [10, 200], 'bandpass', fs=fs, output='sos'),
                         rng.standard_normal(t.size))
    x += 0.60 * emg / emg.std() * ((t > 40) & (t < 60))
    bp = signal.sosfiltfilt(signal.butter(2, [5, 15], 'bandpass', fs=fs, output='sos'), x)
    sq = np.gradient(bp) ** 2
    mwi = np.convolve(sq, np.ones(int(0.15 * fs)) / (0.15 * fs), 'same')
    thr = 0.3 * np.percentile(mwi, 99)
    pk, _ = signal.find_peaks(mwi, height=thr, distance=int(0.25 * fs))
    r = np.array([p - 40 + np.argmax(bp[max(p - 40, 0):p + 40]) for p in pk]) / fs
    return t, x, bp, sq, mwi, thr, r, beats


def fig_28_6():
    t, x, bp, sq, mwi, thr, r, beats = _qrs_sim()
    fig, axs = plt.subplots(5, 2, figsize=(6.8, 5.0), sharex="col",
                            gridspec_kw=dict(hspace=0.12, wspace=0.08))
    wins = [(10, 14, "clean, 10–14 s"), (56, 60, "inside the EMG burst, 56–60 s")]
    names = ["raw (mV)", "5–15 Hz\n(mV)", "(d/dt)²\n(×10⁻³)", "MWI\n(×10⁻³)", "beats"]
    for j, (t0, t1, title) in enumerate(wins):
        m = (t >= t0) & (t <= t1)
        axs[0, j].plot(t[m], x[m], color=INK, lw=0.7)
        axs[0, j].set_ylim(-1, 2)
        axs[0, j].set_title(title, fontsize=8.5)
        axs[1, j].plot(t[m], bp[m], color=BLUE, lw=0.8)
        axs[2, j].plot(t[m], sq[m]*1e3, color=ORANGE, lw=0.8)
        axs[3, j].plot(t[m], mwi[m]*1e3, color=GREEN, lw=0.9)
        axs[3, j].axhline(thr*1e3, color=RED, ls="--", lw=0.9)
        rr_ = r[(r >= t0) & (r <= t1)]
        bb = beats[(beats >= t0) & (beats <= t1)]
        a = axs[4, j]
        a.vlines(rr_, 0.1, 0.8, color=INK, lw=1.2)
        a.plot(bb, np.full_like(bb, 0.5), "o", mfc="none", mec=BLUE, ms=7)
        false = [v for v in rr_ if np.min(np.abs(beats - v)) > 0.075]
        a.plot(false, np.full(len(false), 0.5), "x", color=RED, ms=8, mew=2)
        a.set_ylim(0, 1); a.set_yticks([])
        a.set_xlim(t0, t1)
        a.set_xticks(np.arange(t0, t1 + 0.1, 1.0))
        a.set_xlabel("Time (s)")
        for i in range(5):
            axs[i, j].tick_params(labelsize=7)
            if j == 1:
                axs[i, j].set_yticklabels([])
            else:
                axs[i, j].set_ylabel(names[i], fontsize=7.5)
        if j == 1:
            axs[1, 1].set_ylim(axs[1, 0].get_ylim())
            for i in (2, 3):
                axs[i, 1].set_ylim(axs[i, 0].get_ylim())
    for i in range(1, 4):
        lo = min(axs[i, 0].get_ylim()[0], axs[i, 1].get_ylim()[0])
        hi = max(axs[i, 0].get_ylim()[1], axs[i, 1].get_ylim()[1])
        axs[i, 0].set_ylim(lo, hi); axs[i, 1].set_ylim(lo, hi)
    axs[3, 0].text(13.95, thr*1e3, "threshold 0.3 × P99", fontsize=6.5, color=RED, ha="right", va="bottom")
    axs[4, 1].text(59.95, 0.99, "| detection   ○ true beat   × false", fontsize=6.5, ha="right", va="top")
    fig.align_ylabels(axs[:, 0])
    save(fig, "28", "fig-28-6-pan-tompkins-stages")


if __name__ == "__main__":
    fig_28_1()
    fig_28_2()
    fig_28_3()
    fig_28_4()
    fig_28_5()
    fig_28_6()
