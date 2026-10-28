"""Shared matplotlib style for all book figures.

Every chapter script imports this module, so figures look like one system:

    from figstyle import new_fig, save, COLORS

Run a chapter script from the repository root:  python figures/scripts/ch05.py
Output goes to figures/chNN/<name>.png (200 dpi, white background).
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
FIG_DIR = ROOT / "figures"

# Categorical palette (colour-blind safe, Okabe–Ito ordering)
COLORS = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9", "#F0E442", "#000000"]
INK = "#222222"
GRID = "#DDDDDD"

plt.rcParams.update({
    "figure.dpi": 100,
    "savefig.dpi": 200,
    "savefig.bbox": "tight",
    "savefig.facecolor": "white",
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "axes.edgecolor": INK,
    "axes.labelcolor": INK,
    "axes.prop_cycle": matplotlib.cycler(color=COLORS),
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": False,
    "grid.color": GRID,
    "xtick.color": INK,
    "ytick.color": INK,
    "legend.frameon": False,
    "lines.linewidth": 1.8,
    "mathtext.fontset": "cm",
})


def new_fig(w=6.4, h=3.8, **kw):
    """Return (fig, ax) at a book-standard size (inches)."""
    return plt.subplots(figsize=(w, h), **kw)


def schematic(w=6.4, h=3.8, xlim=(0, 10), ylim=(0, 6)):
    """Return (fig, ax) for a diagram: equal aspect, no axes, data units = drawing units."""
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def box(ax, x, y, w, h, text="", fc="#EEF3F8", ec=INK, fontsize=9, **kw):
    """Rounded box with lower-left corner (x, y) and centred text."""
    from matplotlib.patches import FancyBboxPatch
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc=fc, ec=ec, lw=1.0, **kw))
    if text:
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fontsize, color=INK)


def arrow(ax, x0, y0, x1, y1, text="", color=INK, fontsize=8.5, both=False, **kw):
    """Arrow from (x0, y0) to (x1, y1) with an optional label at its midpoint."""
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="<|-|>" if both else "-|>", color=color, lw=1.1,
                                shrinkA=0, shrinkB=0, mutation_scale=10, **kw))
    if text:
        ax.text((x0 + x1) / 2, (y0 + y1) / 2, text, ha="center", va="bottom", fontsize=fontsize, color=color)


def save(fig, chapter, name):
    """Save fig to figures/chNN/name.png (or figures/appX/, figures/specNN/) and close it."""
    out = FIG_DIR / (f"ch{chapter}" if str(chapter).isdigit() else str(chapter))
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{name}.png"
    fig.savefig(path)
    plt.close(fig)
    print(f"wrote {path.relative_to(ROOT)}")
    return path
