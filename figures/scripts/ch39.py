"""Figures for Chapter 39 — Project: Engineering Simulation Tool.

Run from the repository root:  python figures/scripts/ch39.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle, FancyBboxPatch  # noqa: E402
import scipy.sparse as sp  # noqa: E402
import scipy.sparse.linalg as spla  # noqa: E402

from figstyle import COLORS, INK, GRID, box, save, schematic, new_fig  # noqa: E402

BLUE, ORANGE, GREEN, PINK, YELLOW, SKY = COLORS[:6]
RED = "#C62828"
GREY = "#777777"


def arr(ax, x0, y0, x1, y1, color=INK, lw=1.1, ls="-"):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, ls=ls, shrinkA=0, shrinkB=0,
                                mutation_scale=9))


# ----------------------------------------------------------------------------
# pcbtherm Rev A core, as listed in the chapter (39.3)
K_CU, K_FR4 = 385.0, 0.8
RC_CU, RC_FR4 = 8960 * 385, 1850 * 1100
OZ = 34.8e-6
SOURCES = [dict(name="Q1", x_mm=30, y_mm=40, w_mm=5, h_mm=6, power_W=1.5),
           dict(name="Q2", x_mm=45, y_mm=40, w_mm=5, h_mm=6, power_W=1.5),
           dict(name="shunt", x_mm=70, y_mm=20, w_mm=6, h_mm=3.2, power_W=0.4)]
TCS = {"TC1": (32.5, 40), "TC2": (47.5, 40), "TC3": (70, 22.5), "TC4": (85, 60), "TC5": (5, 5)}


def assemble(G, H, dx, dy):
    ny, nx = G.shape
    idx = np.arange(nx * ny).reshape(ny, nx)
    hm = lambda a, b: 2.0 * a * b / (a + b)
    pairs = [(idx[:, :-1], idx[:, 1:], hm(G[:, :-1], G[:, 1:]) * dy / dx),
             (idx[:-1, :], idx[1:, :], hm(G[:-1, :], G[1:, :]) * dx / dy)]
    r, c, v = [], [], []
    for a, b, g in pairs:
        a, b, g = a.ravel(), b.ravel(), g.ravel()
        r += [a, b, a, b]
        c += [a, b, b, a]
        v += [g, g, -g, -g]
    n = nx * ny
    K = sp.coo_matrix((np.concatenate(v), (np.concatenate(r), np.concatenate(c))), shape=(n, n)).tocsc()
    return (K + sp.diags(H.ravel() * dx * dy)).tocsc()


def build(cell_mm=0.5, h_top=12.0, h_bot=9.0, copper_oz=2.0):
    c = cell_mm * 1e-3
    nx, ny = round(0.100 / c), round(0.080 / c)
    t_cu, t_fr = copper_oz * OZ, 1.6e-3
    G = np.full((ny, nx), 2 * K_CU * t_cu + K_FR4 * t_fr)
    Cs = np.full((ny, nx), 2 * RC_CU * t_cu + RC_FR4 * t_fr)
    H = np.full((ny, nx), h_top + h_bot)
    X, Y = np.meshgrid((np.arange(nx) + 0.5) * c, (np.arange(ny) + 0.5) * c)
    q = np.zeros((ny, nx))
    for s in SOURCES:
        m = ((np.abs(X - s["x_mm"] * 1e-3) < s["w_mm"] * 5e-4 + 1e-9) &
             (np.abs(Y - s["y_mm"] * 1e-3) < s["h_mm"] * 5e-4 + 1e-9))
        q += m * s["power_W"] / (m.sum() * c * c)
    return dict(G=G, Cs=Cs, H=H, q=q, dx=c, dy=c, X=X, Y=Y)


def probe(th, cell_mm, x, y):
    """Value of the cell that contains the point (x, y) in mm."""
    return th[int(np.floor(y / cell_mm)), int(np.floor(x / cell_mm))]


# ----------------------------------------------------------------------------
def fig_39_1():
    """pcbtherm Rev A architecture."""
    fig, ax = schematic(6.8, 3.6, xlim=(0, 18), ylim=(0, 9.6))
    fs = 7.0
    w, h, y = 2.75, 2.7, 5.3
    xs = [0.12 + k * 3.0 for k in range(6)]
    txt = ["Case file\n(TOML)\nfan_ctrl.toml",
           "Validator\nranges, units,\ngeometry,\nedge alignment",
           "Mesher\ncell maps\nG, $C_s$, H, q″",
           "Assembler\nsparse K,\n5-point finite\nvolume",
           "Solver\nsparse LU;\nbackward\nEuler reusing\none LU",
           "Post-\nprocessor\nenergy\nclosure,\nprobes"]
    fcs = ["#FBEFE6", "#EEF3F8", "#EEF3F8", "#EEF3F8", "#EEF3F8", "#E9F5EF"]
    for x, t, fc in zip(xs, txt, fcs):
        box(ax, x, y, w, h, t, fc=fc, fontsize=fs)
    for a, b in zip(xs[:-1], xs[1:]):
        arr(ax, a + w, y + h / 2, b, y + h / 2)
    # dashed core box
    ax.add_patch(Rectangle((xs[1] - 0.1, y - 0.3), xs[4] + w - xs[1] + 0.2, h + 1.35, fill=False, ec=GREY,
                           lw=1.0, ls="--"))
    ax.text(xs[1] + 0.05, y + h + 0.75, "core: about 130 lines of Python (validate.py, mesh.py, core.py)",
            fontsize=fs, color=GREY, va="center")
    # outputs
    ox = xs[5] + 0.45
    box(ax, ox, 2.55, xs[5] + w - ox, 1.9, "Report\nPNG, CSV,\nassumptions", fc="#E9F5EF", fontsize=fs)
    box(ax, ox, 0.2, xs[5] + w - ox, 1.9, "Run manifest\nJSON hashes,\nversions,\nresults", fc="#E9F5EF", fontsize=fs)
    arr(ax, ox + (xs[5] + w - ox) / 2, y, ox + (xs[5] + w - ox) / 2, 4.45)
    ax.plot([xs[5] + 0.2, xs[5] + 0.2], [y, 1.15], color=INK, lw=1.1)
    arr(ax, xs[5] + 0.2, 1.15, ox, 1.15)
    # verification suite
    box(ax, 7.4, 0.5, 6.9, 2.3, "Verification suite (CI, every commit)\nMMS order test, analytic limits,\n"
        "energy closure, golden values", fc="#FDF3DD", fontsize=fs)
    for xc in (xs[3] + w / 2, xs[4] + w / 2):
        arr(ax, xc, 2.8, xc, y - 0.3, color=ORANGE, lw=1.3)
    ax.text((xs[3] + xs[4] + w) / 2, 3.85, "calls the same\nfunctions", fontsize=6.8, color=ORANGE, ha="center",
            va="center")
    ax.text(0.2, 3.2, "Every result leaves\nwith its manifest;\nthe verified code is\nthe code that runs.",
            fontsize=6.8, color=GREY, va="center")
    save(fig, "39", "fig-39-1-pcbtherm-architecture")


# ----------------------------------------------------------------------------
def fig_39_2():
    """Steady temperature-rise map, open bench, 0.5 mm cells."""
    m = build(0.5)
    K = assemble(m["G"], m["H"], m["dx"], m["dy"])
    th = spla.spsolve(K, m["q"].ravel() * m["dx"] * m["dy"]).reshape(m["q"].shape)
    closure = abs(np.sum(m["H"] * th) * m["dx"] * m["dy"] - 3.4) / 3.4
    fig, ax = plt.subplots(figsize=(6.4, 4.6))
    ext = (0, 100, 0, 80)
    im = ax.imshow(th, origin="lower", extent=ext, cmap="viridis", vmin=10, vmax=35, interpolation="nearest")
    cs = ax.contour(m["X"] * 1e3, m["Y"] * 1e3, th, levels=[15, 20, 25, 30], colors="white", linewidths=0.7)
    ax.clabel(cs, fmt="%d K", fontsize=7, manual=[(40, 53), (66, 47), (12, 10), (95.5, 75), (38, 44.5)])
    outlines = {"Q1": (27.5, 32.5, 37, 43), "Q2": (42.5, 47.5, 37, 43), "shunt": (67, 73, 18.5, 21.5)}
    for nm, (x0, x1, y0, y1) in outlines.items():
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, ec="white", lw=1.3))
        below = nm == "shunt"
        ax.text((x0 + x1) / 2, y0 - 1.0 if below else y1 + 1.0, nm, color="white", fontsize=7.5, ha="center",
                va="top" if below else "bottom", weight="bold")
    iy, ix = np.unravel_index(np.argmax(th), th.shape)
    ax.plot(m["X"][iy, ix] * 1e3, m["Y"][iy, ix] * 1e3, "+", color=RED, ms=9, mew=1.6)
    ax.annotate(f"max {th.max():.1f} K", xy=(m["X"][iy, ix] * 1e3, m["Y"][iy, ix] * 1e3), xytext=(12, 60),
                color="white", fontsize=8, arrowprops=dict(arrowstyle="-", color="white", lw=0.8))
    offs = {"TC1": (-1.0, -8.5), "TC2": (1.0, -6.5), "TC3": (1.5, 1.5), "TC4": (1.5, 1.5), "TC5": (2.0, -3.5)}
    vals = {}
    for nm, (x, y) in TCS.items():
        v = probe(th, 0.5, x, y)
        vals[nm] = v
        ax.plot(x, y, "o", ms=5.5, mfc=ORANGE, mec="white", mew=0.9)
        dx, dy = offs[nm]
        ax.text(x + dx, y + dy, f"{nm}\n{v:.1f} K", color="white", fontsize=7.4, va="bottom",
                bbox=dict(boxstyle="round,pad=0.15", fc="black", ec="none", alpha=0.35))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 80)
    ax.set_aspect("equal")
    ax.set_xlabel("x (mm)")
    ax.set_ylabel("y (mm)")
    cb = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.03)
    cb.set_label("Temperature rise above ambient (K)")
    ax.set_title(f"Open bench, $H$ = 21 W/(m² K), 3.4 W; mean rise {th.mean():.2f} K", fontsize=9)
    save(fig, "39", "fig-39-2-steady-map-bench")
    return th.max(), th.mean(), vals, closure


# ----------------------------------------------------------------------------
def fig_39_3():
    """Measured steady-solve time against number of cells."""
    n = np.array([8000, 32000, 128000])
    t_asm = np.array([0.006, 0.016, 0.074])
    t_lu = np.array([0.045, 0.186, 1.336])
    t_cg = np.array([0.093, 1.014, 7.946])
    it = [550, 1089, 2168]
    fig, ax = new_fig(6.4, 4.0)
    ax.loglog(n, t_cg, "s-", color=ORANGE, label="CG + Jacobi (rtol 1e-10)")
    ax.loglog(n, t_lu, "o-", color=BLUE, label="sparse LU (SuperLU, splu)")
    ax.loglog(n, t_asm, "^-", color=GREEN, label="assembly of K")
    for j, (x, t, k) in enumerate(zip(n, t_cg, it)):
        if j in (0, 2):
            ax.text(x * 0.93, t * 1.35, f"{k} iterations", fontsize=7.4, color=ORANGE, ha="right", va="bottom")
        else:
            ax.text(x * 1.08, t * 0.62, f"{k} iterations", fontsize=7.4, color=ORANGE, ha="left", va="top")
    ax.axhline(1.0, color=RED, ls="--", lw=1.1)
    ax.text(5.3e3, 1.1, "R3 budget: 1 s per steady case", color=RED, fontsize=7.8, va="bottom")
    ax.axvline(32000, color=GREY, ls=":", lw=1.1)
    ax.text(33500, 1.6e-3, "0.5 mm grid\n(200 × 160)", fontsize=7.6, color=GREY, va="bottom")
    ref = n / n[0]
    ax.loglog(n, t_lu[0] * ref, color=GREY, lw=0.8, ls="-.")
    ax.text(1.32e5, t_lu[0] * 128000 / 8000, "∝ n", fontsize=7.4, color=GREY, va="center", ha="left")
    ax.set_xlim(5e3, 2e5)
    ax.set_ylim(1e-3, 20)
    ax.set_xlabel("Number of cells")
    ax.set_ylabel("Wall-clock time, best of 3 (s)")
    ax.legend(loc="upper left", fontsize=7.8)
    ax.grid(True, which="major", color=GRID, lw=0.5)
    save(fig, "39", "fig-39-3-runtime-scaling")


# ----------------------------------------------------------------------------
def fig_39_4():
    """MMS convergence: correct code against a mutated face average."""
    h = np.array([4, 2, 1, 0.5, 0.25])
    e_ok = np.array([8.010e-3, 2.001e-3, 5.002e-4, 1.250e-4, 3.126e-5])
    e_mut = np.array([2.210e-2, 9.060e-3, 4.034e-3, 1.894e-3, 9.159e-4])
    p_ok = np.log2(e_ok[:-1] / e_ok[1:])
    p_mut = np.log2(e_mut[:-1] / e_mut[1:])
    fig, ax = new_fig(6.0, 4.2)
    ax.loglog(h, e_ok, "o-", color=BLUE, label=f"correct (harmonic-mean faces): order {p_ok.min():.2f}")
    ax.loglog(h, e_mut, "s--", color=RED,
              label=f"mutant (left-cell face value): order {p_mut.min():.2f}–{p_mut.max():.2f}")
    for i in range(4):
        hm = np.sqrt(h[i] * h[i + 1])
        ax.text(hm, np.sqrt(e_mut[i] * e_mut[i + 1]) * 1.35, f"{p_mut[i]:.2f}", color=RED, fontsize=7.2,
                ha="center", va="bottom")
        ax.text(hm, np.sqrt(e_ok[i] * e_ok[i + 1]) / 1.4, f"{p_ok[i]:.2f}", color=BLUE, fontsize=7.2,
                ha="center", va="top")

    def triangle(x0, y0, slope, dx=2.0, above=True, c=INK):
        x1 = x0 * dx
        y1 = y0 * dx ** slope
        if above:
            ax.plot([x0, x1, x0, x0], [y0, y1, y1, y0], color=c, lw=0.9)
            ax.text(x0 / 1.08, np.sqrt(y0 * y1), str(slope), fontsize=8, ha="right", va="center", color=c)
        else:
            ax.plot([x0, x1, x1, x0], [y0, y0, y1, y0], color=c, lw=0.9)
            ax.text(x1 * 1.06, np.sqrt(y0 * y1), str(slope), fontsize=8, ha="left", va="center", color=c)
        ax.text(np.sqrt(x0 * x1), (y1 if above else y0) * (1.1 if above else 0.9), "1", fontsize=8,
                ha="center", va="bottom" if above else "top", color=c)
    triangle(0.5, 2.6e-5, 2, above=False, c=BLUE)
    triangle(0.3, 6.0e-3, 1, above=False, c=RED)
    ax.set_xlim(0.2, 5)
    ax.set_ylim(1e-5, 1e-1)
    ax.set_xticks([0.25, 0.5, 1, 2, 4])
    ax.set_xticklabels(["0.25", "0.5", "1", "2", "4"])
    ax.xaxis.set_minor_formatter(plt.NullFormatter())
    ax.set_xlabel("Cell size Δ (mm)")
    ax.set_ylabel("L2 error of the rise (K)")
    ax.legend(loc="upper left", fontsize=7.8)
    ax.grid(True, which="major", color=GRID, lw=0.5)
    ax.text(4.6, 1.3e-5, "R5: observed order 1.9–2.1", fontsize=7.6, ha="right", color=GREY)
    save(fig, "39", "fig-39-4-mms-convergence")


# ----------------------------------------------------------------------------
def fig_39_5():
    """Warm-up transient at TC1 and TC5: pcbtherm against the mean of five boards."""
    m = build(0.5)
    K = assemble(m["G"], m["H"], m["dx"], m["dy"])
    dt = 5.0
    M = sp.diags(m["Cs"].ravel() * m["dx"] * m["dy"] / dt)
    lu = spla.splu((M + K).tocsc())
    qv = m["q"].ravel() * m["dx"] * m["dy"]
    x = np.zeros(qv.size)
    i1 = (int(40 / 0.5), int(32.5 / 0.5))
    i5 = (int(5 / 0.5), int(5 / 0.5))
    ts, s1, s5 = [0.0], [0.0], [0.0]
    for k in range(1, 361):
        x = lu.solve(M @ x + qv)
        T = x.reshape(m["q"].shape)
        ts.append(k * dt)
        s1.append(T[i1])
        s5.append(T[i5])
    ts, s1, s5 = map(np.array, (ts, s1, s5))
    t63_1 = np.interp(0.632 * s1[-1], s1, ts)
    t63_5 = np.interp(0.632 * s5[-1], s5, ts)
    # measured mean of five boards: same shape, final 35.1 K / 19.3 K, 63 % at 110 s / 205 s
    tm = np.arange(60, 1801, 60)
    m1 = 35.1 / s1[-1] * np.interp(tm * t63_1 / 110, ts, s1)
    m5 = 19.3 / s5[-1] * np.interp(tm * t63_5 / 205, ts, s5)
    rng = np.random.default_rng(39)
    m1 += rng.normal(0, 0.15, tm.size)
    m5 += rng.normal(0, 0.15, tm.size)
    fig, ax = new_fig(6.4, 4.2)
    ax.fill_between(ts, s1 - 3.2, s1 + 3.2, color=BLUE, alpha=0.10, lw=0)
    ax.text(1500, s1[-1] - 3.0, "R1 band ±3.2 K about TC1", fontsize=7.4, color=BLUE, ha="center", va="bottom")
    ax.plot(ts, s1, color=BLUE, label="TC1, Q1 tab: pcbtherm")
    ax.plot(ts, s5, color=GREEN, label="TC5, corner: pcbtherm")
    ax.errorbar(tm, m1, yerr=0.5, fmt="o", ms=3.8, color=BLUE, mfc="white", capsize=2, lw=0.8,
                label="TC1 measured (mean of 5)")
    ax.errorbar(tm, m5, yerr=0.5, fmt="s", ms=3.6, color=GREEN, mfc="white", capsize=2, lw=0.8,
                label="TC5 measured (mean of 5)")
    for v, c in ((0.632 * s1[-1], BLUE), (0.632 * s5[-1], GREEN)):
        ax.axhline(v, color=c, ls=":", lw=0.9)
    for t63, c, lab, y, va in ((t63_1, BLUE, f"{t63_1:.0f} s", 0.4, "bottom"), (110, BLUE, "110 s", 0.4, "bottom"),
                               (t63_5, GREEN, f"{t63_5:.0f} s", 0.4, "bottom"), (205, GREEN, "205 s", 0.4, "bottom")):
        ax.plot([t63, t63], [0, 1.6], color=c, lw=1.4)
    ax.annotate(f"TC1 63 %: sim. {t63_1:.0f} s, meas. 110 s", xy=(t63_1, 1.6), xytext=(260, 1.2), fontsize=7.2,
                color=BLUE, arrowprops=dict(arrowstyle="-", color=BLUE, lw=0.6))
    ax.annotate(f"TC5 63 %: sim. {t63_5:.0f} s, meas. 205 s", xy=(t63_5, 1.6), xytext=(320, 4.0), fontsize=7.2,
                color=GREEN, arrowprops=dict(arrowstyle="-", color=GREEN, lw=0.6))
    ax.text(1790, s1[-1] - 0.5, f"{s1[-1]:.1f} K", color=BLUE, fontsize=7.4, ha="right", va="top")
    ax.text(1790, 35.1 + 0.6, "35.1 K", color=BLUE, fontsize=7.4, ha="right", va="bottom")
    ax.text(1790, s5[-1] + 0.6, f"{s5[-1]:.1f} K (sim.), 19.3 K (meas.)", color=GREEN, fontsize=7.4, ha="right",
            va="bottom")
    ax.set_xlim(0, 1800)
    ax.set_ylim(0, 40)
    ax.set_xlabel("Time after power-on (s)")
    ax.set_ylabel("Temperature rise (K)")
    ax.legend(loc="lower right", fontsize=7.4)
    ax.grid(True, color=GRID, lw=0.5)
    save(fig, "39", "fig-39-5-transient-validation")
    return t63_1, t63_5, [round(float(np.interp(t, ts, s1)), 1) for t in (60, 120, 300, 600, 900, 1200)]


if __name__ == "__main__":
    fig_39_1()
    print("map", fig_39_2())
    fig_39_3()
    fig_39_4()
    print("transient", fig_39_5())
