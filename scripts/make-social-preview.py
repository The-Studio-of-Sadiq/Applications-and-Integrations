"""Render the GitHub social preview (1280x640) to docs/social-preview.png.

    python scripts/make-social-preview.py
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "social-preview.png"

BG = "#0b2230"
INK = "#f2f5f9"
MUTED = "#9fb8c8"
ACCENT = ["#56B4E9", "#E69F00", "#009E73", "#CC79A7", "#F0E442"]

plt.rcParams.update({"font.family": "DejaVu Sans", "mathtext.fontset": "cm"})
fig = plt.figure(figsize=(12.8, 6.4), dpi=100, facecolor=BG)

# Upper right: PV module P-V curves for three irradiances, with maximum power points (Chapter 22).
ax = fig.add_axes([0.62, 0.55, 0.35, 0.36], facecolor=BG)
v = np.linspace(0, 40, 400)
for g, c in zip((1.0, 0.7, 0.4), ACCENT):
    isc, i0, a = 9.5 * g, 1e-9, 1.9
    i = np.clip(isc - i0 * (np.exp(v / a) - 1), 0, None)
    p = v * i
    ax.plot(v, p, color=c, lw=2.4)
    k = int(np.argmax(p))
    ax.plot(v[k], p[k], "o", color=INK, ms=6)
ax.text(41, 300, "MPP", color=MUTED, fontsize=13, va="center")
ax.set_xlim(0, 46)
ax.set_ylim(0, 380)
ax.axis("off")

# Lower right: closed-loop step response under a requirement band (Chapters 1, 15, 37).
ax2 = fig.add_axes([0.64, 0.08, 0.31, 0.38], facecolor=BG)
t = np.linspace(0, 1, 400)
wn, z = 14.0, 0.6
wd = wn * np.sqrt(1 - z**2)
y = 1 - np.exp(-z * wn * t) * (np.cos(wd * t) + z / np.sqrt(1 - z**2) * np.sin(wd * t))
ax2.fill_between(t, 0.98, 1.02, where=t > 0.45, color=ACCENT[2], alpha=0.6, lw=0)
ax2.plot(t, y, color=ACCENT[0], lw=2.4)
ax2.axhline(1.2, color=ACCENT[1], lw=1.2, ls="--")
ax2.text(0.55, 1.33, "R3: overshoot < 20 %", color=MUTED, fontsize=12)
ax2.text(0.42, 0.55, r"$t_s \leq 0.45\ \mathrm{s}$  PASS", color=INK, fontsize=14)
ax2.set_xlim(0, 1.0)
ax2.set_ylim(-0.3, 1.5)
ax2.axis("off")

# Left panel: title block.
fig.text(0.06, 0.83, "BOOK 6  ·  EEE CORE", color=ACCENT[0], fontsize=20, weight="bold")
fig.text(0.06, 0.63, "Applications\nand Integrations", color=INK, fontsize=38, weight="bold",
         va="center", linespacing=1.12)
fig.text(0.06, 0.45, "From requirement to working system: instruments,\nembedded and IoT devices, robots, factories,\n"
         "energy and mobility, medicine, software.",
         color=MUTED, fontsize=16, style="italic", va="top", linespacing=1.35)
fig.text(0.06, 0.24, "requirement → architecture → build → verify → fail safely", color=INK, fontsize=15)
fig.text(0.06, 0.14, "9 parts · 40 chapters · 225 figures · 953-page PDF · MCP server", color=INK, fontsize=14)
fig.text(0.06, 0.07, "github.com/The-Studio-of-Sadiq/Applications-and-Integrations", color=MUTED, fontsize=12)

OUT.parent.mkdir(exist_ok=True)
fig.savefig(OUT, facecolor=BG)
print(f"wrote {OUT.relative_to(ROOT)}")
