"""Figures for Chapter 30 — Scientific and Engineering Computing.

Run from the repository root:  python figures/scripts/ch30.py

The heatsink physics core of Listing 30.1 is reproduced below so that every plotted
number is recomputed from the chapter's model (the 420-case sweep takes about 30 s).
"""
import itertools
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import scipy.sparse as sp  # noqa: E402
from scipy.optimize import brentq, minimize_scalar  # noqa: E402
from scipy.sparse.linalg import spsolve  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle, FancyBboxPatch, Polygon  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

from figstyle import COLORS, INK, save, schematic  # noqa: E402

BLUE, ORANGE, GREEN, PINK, YELLOW, SKY = COLORS[:6]
RED = "#C62828"
GREY = "#777777"

# ----------------------------------------------------------------------------
# Physics core (Listing 30.1, hs_model.py)
# ----------------------------------------------------------------------------
RHO, CP, MU, K_AIR = 1.09, 1007.0, 1.96e-5, 0.028
W, L, K_AL, T_AMB = 0.16, 0.30, 200.0, 45.0
CENTRES, FX, FY = [(0.08, 0.06), (0.08, 0.15), (0.08, 0.24)], 0.10, 0.06
REV_A = dict(N=18, H=0.02336, tb=0.004)


def fan_dp(Q):
    return 250.0 * (1.0 - (Q / 0.070) ** 2)


def channel(N, H, t, Q):
    s = (W - N * t) / (N - 1)
    v, Dh = Q / ((N - 1) * s * H), 2 * s * H / (s + H)
    Re = RHO * v * Dh / MU
    f_t = (0.79 * np.log(Re) - 1.64) ** -2
    if Re < 2300:
        Gz = Dh / L * Re * 0.71
        Nu = 7.54 + 0.03 * Gz / (1 + 0.016 * Gz ** (2 / 3))
    else:
        Nu = f_t / 8 * (Re - 1000) * 0.71 / (1 + 12.7 * np.sqrt(f_t / 8) * (0.71 ** (2 / 3) - 1))
    dp = max(96 / Re, f_t) * L / Dh * 0.5 * RHO * v**2 + 0.75 * RHO * v**2
    return dp, Nu * K_AIR / Dh, s, Re


def lap1d(n, dx):
    d = -2.0 * np.ones(n)
    d[[0, -1]] = -1.0
    return sp.diags([np.ones(n - 1), d, np.ones(n - 1)], [-1, 0, 1]) / dx**2


def solve(N=20, H=0.040, t=0.0015, tb=0.010, P=(200.0,) * 3, dx=0.002, bypass=0.0):
    Q = brentq(lambda q: fan_dp(q) - channel(N, H, t, q)[0], 1e-4, 0.0699)
    _, h, s, Re = channel(N, H, t, (1 - bypass) * Q)
    if 2300 <= Re <= 3000:
        raise ValueError(f"Re = {Re:.0f}: transitional flow, no validated correlation")
    m = np.sqrt(2 * h / (K_AL * t))
    eta = np.tanh(m * H) / (m * H)
    h_eff = h * ((N - 1) * s + 2 * N * H * eta) / W
    nx, ny = round(W / dx), round(L / dx)
    X, Y = np.meshgrid((np.arange(nx) + 0.5) * dx, (np.arange(ny) + 0.5) * dx, indexing="ij")
    masks = [(abs(X - cx) <= FX / 2) & (abs(Y - cy) <= FY / 2) for cx, cy in CENTRES]
    q = sum(Pk * mk / (mk.sum() * dx * dx) for Pk, mk in zip(P, masks))
    T_air = T_AMB + sum(P) / (RHO * CP * (1 - bypass) * Q) * Y / L
    A = K_AL * tb * sp.kronsum(lap1d(ny, dx), lap1d(nx, dx)) - h_eff * sp.eye(nx * ny)
    T = spsolve(A.tocsc(), -(q + h_eff * T_air).ravel()).reshape(nx, ny)
    return dict(Q=Q, h=h, eta=eta, h_eff=h_eff, T=T, Tmax=T.max(), X=X, Y=Y, T_air=T_air,
                T_mod=[T[mk].mean() for mk in masks],
                areas=[mk.sum() * dx * dx for mk in masks],
                T_ctr=[T[np.argmin(abs(X[:, 0] - cx)), np.argmin(abs(Y[0] - cy))] for cx, cy in CENTRES],
                mass=2700 * (W * L * tb + N * t * H * L))


def poly(ax, pts, color=INK, lw=1.1, ls="-", head=True):
    xs, ys = zip(*pts)
    if len(pts) > 2:
        ax.plot(xs[:-1], ys[:-1], color=color, lw=lw, ls=ls, solid_capstyle="butt")
    if head:
        ax.annotate("", xy=pts[-1], xytext=pts[-2],
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, ls=ls,
                                    shrinkA=0, shrinkB=0, mutation_scale=10))
    else:
        ax.plot(xs[-2:], ys[-2:], color=color, lw=lw, ls=ls)


def rbox(ax, x, y, w, h, fc, ec=INK, lw=1.0, ls="-"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.15",
                                fc=fc, ec=ec, lw=lw, ls=ls))


# ----------------------------------------------------------------------------
# Figure 30.1 — architecture of the computation
# ----------------------------------------------------------------------------
def fig_30_1():
    fig, ax = schematic(6.8, 5.2, xlim=(0, 18.2), ylim=(-0.5, 13.4))
    fs = 7.4
    # inputs (left)
    inputs = [
        (9.9, 1.8, "Mission profile", "CSV: loss per\nmodule vs time"),
        (5.5, 3.1, "Config (TOML)", "N, H, t$_b$ ranges, dx\nfan curve, limits\nlosses 3 × 200 W"),
        (1.6, 2.1, "Prototype data", "thermocouples\n3 load points"),
    ]
    for y, h, name, sub in inputs:
        rbox(ax, 0.4, y, 3.3, h, "#F2F2F2")
        ax.text(2.05, y + h - 0.38, name, ha="center", va="center", fontsize=8, weight="bold")
        ax.text(2.05, y + (h - 0.65) / 2, sub, ha="center", va="center", fontsize=7.0, linespacing=1.3)
    ax.text(2.05, 9.1, "inputs are data,\nnot code", ha="center", va="center", fontsize=7,
            style="italic", color=GREY)

    # drivers (top), all calling the core
    ax.text(7.25, 13.05, "Drivers (call the core, never reach inside)", ha="center", va="center",
            fontsize=8.5, weight="bold")
    drivers = ["Sweep\n420 cases", "Optimiser\nSLSQP", "Transient\nZOH", "Validation\ncalibrate"]
    cx0, cy0, cw, ch = 4.3, 1.6, 6.1, 7.6
    dw, dg = 2.0, 0.2
    dxs = [3.95 + i * (dw + dg) for i in range(4)]
    for x, t in zip(dxs, drivers):
        rbox(ax, x, 10.3, dw, 1.5, "#E69F0033")
        ax.text(x + dw / 2, 11.05, t, ha="center", va="center", fontsize=7.4, linespacing=1.25)
    for x in dxs[:3]:
        poly(ax, [(x + dw / 2, 10.3), (x + dw / 2, cy0 + ch)])
    xv = dxs[3] + dw / 2
    poly(ax, [(xv, 10.3), (xv, 9.75), (cx0 + cw - 0.3, 9.75), (cx0 + cw - 0.3, cy0 + ch)])
    ax.text(dxs[0] + dw / 2 + 0.12, 9.75, "design dict", fontsize=7, ha="left", va="center")
    ax.text(xv + 0.12, 10.0, "P, bypass", fontsize=7, ha="left", va="center")

    # mission profile -> transient driver (over the top)
    poly(ax, [(2.05, 11.7), (2.05, 12.4), (dxs[2] + dw / 2, 12.4), (dxs[2] + dw / 2, 11.8)], color=GREY)
    # config -> core
    poly(ax, [(3.7, 7.0), (cx0, 7.0)])

    # physics core
    rbox(ax, cx0, cy0, cw, ch, "#0072B214", ec=BLUE, lw=1.4)
    ax.text(cx0 + cw / 2, cy0 + ch - 0.45, "Physics core: solve(design)", ha="center", va="center",
            fontsize=8.0, weight="bold", color=BLUE)
    subs = [("Fan operating point", "brentq: Δp$_{fan}$(Q) = Δp$_{sys}$(Q)"),
            ("Channel and fin model", "Re validity check → $h$, η, $h_{eff}$"),
            ("Base-plate solver", "sparse 2-D FD, spsolve → T field")]
    sy = [6.6, 4.3, 2.0]
    for (name, sub), y in zip(subs, sy):
        rbox(ax, cx0 + 0.4, y, cw - 0.8, 1.55, "white", ec=BLUE)
        ax.text(cx0 + cw / 2, y + 1.05, name, ha="center", va="center", fontsize=8, weight="bold")
        ax.text(cx0 + cw / 2, y + 0.45, sub, ha="center", va="center", fontsize=fs)
    for ya, yb, lab in [(6.6, 5.85, "Q"), (4.3, 3.55, "$h_{eff}$, $T_{air}(y)$")]:
        poly(ax, [(cx0 + cw / 2, ya), (cx0 + cw / 2, yb)], color=BLUE)
        ax.text(cx0 + cw / 2 + 0.15, (ya + yb) / 2, lab, fontsize=7.2, va="center", color=BLUE)

    # gates
    gx, gw, gh = 12.8, 2.4, 2.5

    def diamond(yc, text, fc, ec):
        ax.add_patch(Polygon([(gx - gw / 2, yc), (gx, yc + gh / 2), (gx + gw / 2, yc), (gx, yc - gh / 2)],
                             closed=True, fc=fc, ec=ec, lw=1.3))
        ax.text(gx, yc, text, ha="center", va="center", fontsize=7.2, weight="bold", linespacing=1.15)

    yv, yl = 7.4, 2.9
    diamond(yv, "Verifi-\ncation", "#009E7326", GREEN)
    ax.text(gx, yv - gh / 2 - 0.12, "energy balance\nexact limit\ngrid convergence", ha="center",
            va="top", fontsize=7.0, linespacing=1.2, color="#1E5E3E")
    diamond(yl, "Validation\n±1.6 K", "#CC79A726", PINK)

    poly(ax, [(cx0 + cw, yv), (gx - gw / 2, yv)])
    ax.text((cx0 + cw + gx - gw / 2) / 2, yv + 0.1, "T field", fontsize=6.8, ha="center", va="bottom")
    poly(ax, [(cx0 + cw, yl), (gx - gw / 2, yl)])
    ax.text((cx0 + cw + gx - gw / 2) / 2 + 0.05, yl + 0.1, "T at TCs", fontsize=6.8, ha="center", va="bottom")

    # prototype data -> validation gate (under the core)
    off = 0.45
    ye = yl - gh / 2 * (1 - off / (gw / 2))
    poly(ax, [(2.05, 1.6), (2.05, 0.8), (gx - off, 0.8), (gx - off, ye)], color=PINK)
    ax.text(7.25, 0.88, "measured temperatures, 80 / 140 / 200 W", fontsize=7, ha="center",
            va="bottom", color="#7A2E5C")

    # results store
    sx, sw = 15.05, 3.0
    rbox(ax, sx, 2.2, sw, 6.9, "#56B4E926", ec=BLUE)
    ax.text(sx + sw / 2, 8.25, "Results\nstore", ha="center", va="center", fontsize=8.5, weight="bold")
    ax.text(sx + sw / 2, 4.9, "structured array\n(.npy)\n+\nJSON manifest:\nmodel hash\nresult hash\n"
            "library versions\nstatus per case", ha="center", va="center", fontsize=7.0, linespacing=1.25)
    for y, c in [(yv, GREEN), (yl, PINK)]:
        poly(ax, [(gx + gw / 2, y), (sx, y)], color=c)
    ax.text((gx + gw / 2 + sx) / 2, yv + 0.1, "status\ncode", fontsize=6.8, ha="center", va="bottom",
            color="#1E5E3E", linespacing=1.05)
    ax.text((gx + gw / 2 + sx) / 2, yl + 0.1, "status\ncode", fontsize=6.8, ha="center", va="bottom",
            color="#7A2E5C", linespacing=1.05)

    # dashed feedback: calibrated bypass fraction back to config
    poly(ax, [(gx + off, ye), (gx + off, 0.25), (0.12, 0.25), (0.12, 6.3), (0.4, 6.3)], color=RED,
         ls=(0, (4, 2)))
    ax.text(7.25, 0.15, "calibrated bypass fraction (back into the config)", fontsize=7.2,
            ha="center", va="top", color=RED)
    save(fig, "30", "fig-30-1-computation-architecture")


# ----------------------------------------------------------------------------
# Figure 30.2 — base-plate temperature field
# ----------------------------------------------------------------------------
def fig_30_2():
    r = solve(**REV_A, dx=0.002)
    X, Y, T = r["X"] * 1e3, r["Y"] * 1e3, r["T"]
    fig = plt.figure(figsize=(6.0, 5.2))
    gs = fig.add_gridspec(1, 3, width_ratios=[5, 1.15, 0.28], wspace=0.12)
    ax, axs, cax = fig.add_subplot(gs[0]), fig.add_subplot(gs[1]), fig.add_subplot(gs[2])
    levels = np.arange(72, 106.01, 1.0)
    cf = ax.contourf(X, Y, T, levels=levels, cmap="inferno")
    ax.contour(X, Y, T, levels=np.arange(75, 106, 5), colors="white", linewidths=0.5, alpha=0.5)
    ax.set_xlim(0, 160)
    ax.set_ylim(0, 300)
    ax.set_aspect("equal")
    ax.set_xlabel("x across the fins (mm)")
    ax.set_ylabel("y along the airflow (mm)")
    for k, ((cx, cy), Tm) in enumerate(zip(CENTRES, r["T_mod"])):
        ax.add_patch(Rectangle(((cx - FX / 2) * 1e3, (cy - FY / 2) * 1e3), FX * 1e3, FY * 1e3,
                               fill=False, ec="white", ls="--", lw=1.2))
        ax.text(cx * 1e3, cy * 1e3 - 14, f"M{k + 1}  mean {Tm:.1f} °C", ha="center", va="center",
                fontsize=8, color="white", weight="bold")
    i = np.unravel_index(np.argmax(T), T.shape)
    ax.plot(X[i], Y[i], "+", color="cyan", ms=9, mew=1.6)
    ax.annotate(f"peak {T.max():.1f} °C", xy=(X[i], Y[i]), xytext=(80, 286), ha="center",
                fontsize=8, color="cyan", weight="bold",
                arrowprops=dict(arrowstyle="-", color="cyan", lw=0.8))
    ax.annotate("", xy=(14, 75), xytext=(14, 8),
                arrowprops=dict(arrowstyle="-|>", color="white", lw=1.6, mutation_scale=12))
    ax.text(19, 10, f"airflow\n{r['Q']:.4f} m³/s", color="white", fontsize=7.5, va="bottom")
    ax.text(80, 4, "inlet", color="white", fontsize=7.5, ha="center", va="bottom")
    cb = fig.colorbar(cf, cax=cax, ticks=np.arange(72, 107, 4))
    cb.set_label("base temperature (°C)")
    cax.set_box_aspect(None)

    ya = Y[0]
    ta = r["T_air"][0]
    axs.plot(ta, ya, color=BLUE)
    axs.set_ylim(0, 300)
    axs.set_xlim(42, 63)
    axs.set_xticks([45, 60])
    axs.set_yticklabels([])
    axs.set_xlabel("air (°C)")
    T_out = T_AMB + 600 / (RHO * CP * r["Q"])
    axs.annotate(f"{T_AMB:.1f} °C\ninlet", xy=(ta[0], 1), xytext=(49, 30), fontsize=7.5,
                 arrowprops=dict(arrowstyle="-", lw=0.6))
    axs.annotate(f"{T_out:.1f} °C\noutlet", xy=(ta[-1], 299), xytext=(43, 220), fontsize=7.5,
                 arrowprops=dict(arrowstyle="-", lw=0.6))
    fig.canvas.draw()
    p0 = ax.get_position()
    x = p0.x1 + 0.05
    for a_, w_ in ((axs, 0.16), (cax, 0.03)):
        a_.set_position([x, p0.y0, w_, p0.height])
        x += w_ + 0.03
    save(fig, "30", "fig-30-2-base-temperature-field")


# ----------------------------------------------------------------------------
# Figure 30.3 — sweep map
# ----------------------------------------------------------------------------
def run_sweep():
    rows = []
    for N, H, tb in itertools.product(range(14, 37, 2), [0.020, 0.025, 0.030, 0.035, 0.040, 0.045, 0.050],
                                      [0.004, 0.006, 0.008, 0.010, 0.012]):
        try:
            r = solve(N=N, H=H, tb=tb, dx=0.002)
            rows.append((N, H, tb, r["mass"], max(r["T_mod"]) + 200 * 0.13, 0))
        except ValueError:
            rows.append((N, H, tb, 2700 * (W * L * tb + N * 0.0015 * H * L), np.nan, 1))
    return np.array(rows)


def fig_30_3():
    a = run_sweep()
    N, H, mass, Tj, st = a[:, 0], a[:, 1], a[:, 3], a[:, 4], a[:, 5]
    ok = st == 0
    s = (W - N * 0.0015) / (N - 1)
    asp = H / s <= 10
    feas = ok & asp & (Tj <= 125)
    assert (~ok).sum() == 45 and feas.sum() == 292

    fig, ax = plt.subplots(figsize=(6.6, 5.0))
    ax.axvspan(125, 140, color=RED, alpha=0.07, lw=0)
    ax.axvline(125, color=RED, ls="--", lw=1.1)
    ax.text(125.5, 3.62, "R1: T$_j$ ≤ 125 °C\ninfeasible →", color=RED, fontsize=8, va="center")
    cmap = plt.get_cmap("viridis")
    norm = plt.Normalize(14, 32)
    full = ok & asp
    sc = ax.scatter(Tj[full], mass[full], c=N[full], cmap=cmap, norm=norm, s=16, lw=0, zorder=3)
    hol = ok & ~asp
    ax.scatter(Tj[hol], mass[hol], facecolors="none", edgecolors=cmap(norm(N[hol])), s=18, lw=0.9,
               zorder=3)
    # out-of-domain cases along the top edge
    nf = (~ok).sum()
    xs = np.linspace(96, 106, nf)
    ax.scatter(xs, np.full(nf, 3.68), marker="x", color=GREY, s=12, lw=0.8, zorder=3)
    ax.text(106.8, 3.68, f"{nf} out-of-domain cases\n(N = 34, 36: transitional Re)",
            ha="left", va="center", fontsize=7.3, color=GREY)
    # Pareto front among valid, aspect-feasible cases
    idx = np.where(full)[0]
    idx = idx[np.argsort(Tj[idx])]
    px, py, best = [], [], np.inf
    for i in idx:
        if mass[i] < best:
            best = mass[i]
            px.append(Tj[i])
            py.append(mass[i])
    ax.step(px, py, where="post", color=INK, lw=1.0, zorder=2)
    ax.text(108, 1.3, "Pareto front", fontsize=8, va="top")
    ib = np.where(feas)[0][np.argmin(mass[feas])]
    ax.plot(Tj[ib], mass[ib], "s", mfc="none", mec=RED, ms=8, mew=1.4, zorder=4)
    ax.plot([125.0, 125.53], [1.029, 1.029], "*", color=ORANGE, mec=INK, mew=0.5, ms=11, zorder=5)
    ax.set_xlim(95, 140)
    ax.set_ylim(0.8, 3.8)
    ax.set_xlabel("hottest junction temperature (°C)")
    ax.set_ylabel("heatsink mass (kg)")
    cb = fig.colorbar(sc, ax=ax, pad=0.02, ticks=range(14, 33, 2))
    cb.set_label("fin count N")

    # zoom inset on the optimum
    ins = ax.inset_axes([0.66, 0.44, 0.32, 0.36])
    ins.axvline(125, color=RED, ls="--", lw=1.0)
    ins.axvspan(125, 127, color=RED, alpha=0.07, lw=0)
    sel = full & (Tj > 122.5) & (Tj < 127) & (mass < 1.25)
    ins.scatter(Tj[sel], mass[sel], c=N[sel], cmap=cmap, norm=norm, s=16, lw=0)
    ins.plot(Tj[ib], mass[ib], "s", mfc="none", mec=RED, ms=8, mew=1.4)
    ins.annotate(f"best grid point\n{mass[ib]:.3f} kg, {Tj[ib]:.1f} °C", xy=(Tj[ib], mass[ib]),
                 xytext=(122.7, 1.17), fontsize=6.8, arrowprops=dict(arrowstyle="-", lw=0.6))
    ins.plot([125.0], [1.029], "*", color=ORANGE, mec=INK, mew=0.5, ms=11, zorder=5)
    ins.plot([125.53], [1.029], "*", color=RED, mec=INK, mew=0.5, ms=11, zorder=5)
    ins.annotate("", xy=(125.48, 1.029), xytext=(125.05, 1.029),
                 arrowprops=dict(arrowstyle="-|>", lw=0.9, mutation_scale=8, color=INK))
    ins.text(125.27, 1.058, "0.53 K", ha="center", va="bottom", fontsize=7)
    ins.text(124.9, 1.008, "4 mm", ha="right", va="top", fontsize=6.8, color="#B36B00")
    ins.text(125.65, 1.008, "1 mm", ha="left", va="top", fontsize=6.8, color=RED)
    ins.set_xlim(122.5, 126.5)
    ins.set_ylim(0.97, 1.24)
    ins.tick_params(labelsize=7)
    ins.set_title("optimiser result, 1.029 kg", fontsize=7.2)
    ax.indicate_inset_zoom(ins, edgecolor=GREY)

    handles = [Line2D([], [], marker="o", ls="", color=cmap(0.4), label="valid, H/s ≤ 10"),
               Line2D([], [], marker="o", ls="", mfc="none", mec=cmap(0.4), label="valid, H/s > 10"),
               Line2D([], [], marker="x", ls="", color=GREY, label="out of domain"),
               Line2D([], [], marker="s", ls="", mfc="none", mec=RED, label="best grid point"),
               Line2D([], [], marker="*", ls="", color=ORANGE, mec=INK, ms=10, label="optimiser (4 mm grid)")]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.13), fontsize=7.5, ncol=3)
    save(fig, "30", "fig-30-3-sweep-map")


# ----------------------------------------------------------------------------
# Figure 30.4 — transient and solver cost
# ----------------------------------------------------------------------------
def fig_30_4():
    R = np.array([0.010, 0.030, 0.050, 0.040])
    TAU = np.array([0.001, 0.01, 0.1, 1.0])
    R_HA, C_HS = 0.086, 926.0
    rng = np.random.default_rng(7)
    P = np.repeat(rng.uniform(30, 230, 60), 10)
    A = np.append(-1 / TAU, -1 / (R_HA * C_HS))
    Bv = np.append(R / TAU, 3.0 / C_HS)
    Ad = np.exp(A)
    Bd = (Ad - 1) / A * Bv
    x = np.zeros(5)
    tj, ths = [T_AMB], [T_AMB]
    for Pk in P:
        x = Ad * x + Bd * Pk
        tj.append(T_AMB + x.sum())
        ths.append(T_AMB + x[-1])
    t = np.arange(0, P.size + 1)

    fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.6, 5.0), height_ratios=[1.35, 1],
                                 gridspec_kw=dict(hspace=0.45))
    a1.fill_between(np.arange(P.size + 1), np.append(P, P[-1]), step="post", color="#BBBBBB",
                    alpha=0.5, lw=0)
    a1.step(np.arange(P.size + 1), np.append(P, P[-1]), where="post", color=GREY, lw=0.8)
    a1.set_xlim(0, 600)
    a1.set_ylim(0, 250)
    a1.set_xlabel("time (s)")
    a1.set_ylabel("loss per module (W)", color=GREY)
    b1 = a1.twinx()
    b1.spines["right"].set_visible(True)
    b1.plot(t, tj, color=RED, lw=1.5, label="junction, exact ZOH")
    b1.plot(t, ths, color=BLUE, lw=1.4, ls="--", label="heatsink (R$_{ha}$C$_{hs}$ = 80 s)")
    b1.set_ylim(45, 115)
    b1.set_ylabel("temperature (°C)")
    b1.annotate(f"{tj[-1]:.1f} °C", xy=(600, tj[-1]), xytext=(545, 52), fontsize=8, color=RED,
                arrowprops=dict(arrowstyle="-", lw=0.6, color=RED))
    b1.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), fontsize=7.8, ncol=3,
               handles=b1.get_lines() + [plt.Rectangle((0, 0), 1, 1, fc="#BBBBBB", ec=GREY, lw=0.8, label="loss per module")])
    a1.text(330, 238, "60 loss steps of 10 s, 30–230 W", fontsize=7.5, ha="center", color=GREY)

    names = ["ZOH exact", "LSODA", "BDF", "Radau", "RK45"]
    times = np.array([5.7e-3, 1.2558, 6.5521, 9.0068, 48.1634])
    notes = ["600 steps, exact to rounding", "48 136 evals, max err 1.4e-5 K",
             "27 076 evals, 5.4e-5 K", "60 342 evals, 7.3e-6 K", "1 279 100 evals, 1.0e-3 K"]
    cols = [GREEN, BLUE, BLUE, BLUE, ORANGE]
    y = np.arange(5)[::-1]
    a2.barh(y, times, color=cols, height=0.62, zorder=2)
    a2.set_xscale("log")
    a2.set_xlim(1e-3, 1e2)
    a2.set_yticks(y)
    a2.set_yticklabels(names)
    a2.set_xlabel("wall-clock time (s), one run")
    a2.axvline(1.0, color=RED, ls="--", lw=1.0, zorder=1)
    a2.text(1.08, 4.45, "R5: 1 s", color=RED, fontsize=8, va="center")
    for yi, ti, n in zip(y, times, notes):
        lab = f"{ti * 1e3:.1f} ms" if ti < 1 else f"{ti:.2f} s" if ti < 10 else f"{ti:.1f} s"
        if ti < 0.1:
            a2.text(ti * 1.3, yi, f"{lab}  ·  {n}", va="center", fontsize=7.3, zorder=3)
        else:
            a2.text(1.4e-3, yi, f"{lab}  ·  {n}", va="center", fontsize=7.3, color="white",
                    weight="bold", zorder=3)
    a2.set_ylim(-0.6, 4.75)
    save(fig, "30", "fig-30-4-transient-solvers")


# ----------------------------------------------------------------------------
# Figure 30.5 — grid convergence
# ----------------------------------------------------------------------------
def fig_30_5():
    dxs = np.array([8, 4, 2, 1, 0.5])
    res = [solve(**REV_A, dx=d / 1e3) for d in dxs]
    f = np.array([max(r["T_mod"]) for r in res])
    a4 = res[1]["areas"]
    p = np.log((f[2] - f[3]) / (f[3] - f[4])) / np.log(2)
    fext = f[4] + (f[4] - f[3]) / (2**p - 1)

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.6, 3.6), width_ratios=[1.35, 1],
                                 gridspec_kw=dict(wspace=0.38))
    a1.plot(dxs, f, "-o", color=BLUE, ms=5)
    a1.axhline(fext, color=INK, ls="--", lw=0.9)
    a1.text(9.0, fext + 0.012, f"extrapolated {fext:.3f}", fontsize=7.8, va="bottom", ha="left")
    a1.set_xscale("log")
    a1.set_xticks(dxs)
    a1.set_xticklabels(["8", "4", "2", "1", "0.5"])
    a1.minorticks_off()
    a1.set_xlim(0.42, 10)
    a1.set_ylim(98.9, 99.6)
    a1.invert_xaxis()
    a1.set_xlabel("grid spacing dx (mm)")
    a1.set_ylabel("hottest-module mean (°C)")
    for d, v in zip(dxs, f):
        if d == 2:
            a1.text(d, v + 0.025, f"{v:.3f}", ha="center", va="bottom", fontsize=7.3)
        elif d != 4:
            a1.text(d, v - 0.035, f"{v:.3f}", ha="center", va="top", fontsize=7.3)
    a1.annotate(f"{f[1]:.3f} °C at 4 mm:\nfootprints rasterised to\n{a4[0] * 1e6:.0f} and "
                f"{a4[1] * 1e6:.0f} mm²\n(not 6000 mm²)",
                xy=(4, f[1]), xytext=(2.6, 99.06), fontsize=7.5, va="bottom",
                arrowprops=dict(arrowstyle="-", lw=0.7))
    a1.set_title("all grids", fontsize=9)

    fine = dxs[2:]
    e = np.abs(f[2:] - fext) * 1e3
    a2.loglog(fine, e, "o-", color=BLUE, ms=5, label="|T − T$_{ext}$|")
    ref = e[0] * (fine / fine[0]) ** 2
    a2.loglog(fine, ref, ":", color=INK, lw=1.2, label="slope 2")
    a2.set_xlim(0.4, 2.5)
    a2.set_xlabel("grid spacing dx (mm)")
    a2.set_ylabel("error from extrapolated value (mK)")
    a2.set_xticks([0.5, 1, 2])
    a2.set_xticklabels(["0.5", "1", "2"])
    a2.minorticks_off()
    a2.set_yticks([1, 3, 10, 30])
    a2.set_yticklabels(["1", "3", "10", "30"])
    a2.set_ylim(0.5, 30)
    for d, v in zip(fine, e):
        a2.text(d * (1.08 if d < 1 else 0.92), v, f"{v:.1f}", fontsize=7.3, va="center",
                ha="left" if d < 1 else "right")
    a2.text(0.45, 18, f"observed order p = {p:.2f}", fontsize=8)
    a2.legend(loc="lower right", fontsize=7.8)
    a2.set_title("asymptotic range", fontsize=9)
    save(fig, "30", "fig-30-5-grid-convergence")


# ----------------------------------------------------------------------------
# Figure 30.6 — validation parity plot
# ----------------------------------------------------------------------------
def fig_30_6():
    D = dict(**REV_A, dx=0.002)
    MEAS = {80: [69.1, 72.1, 73.0], 140: [87.8, 93.5, 94.2], 200: [105.8, 113.5, 115.4]}

    def predict(P, b):
        return np.array(solve(P=(P,) * 3, bypass=b, **D)["T_ctr"])

    sse = lambda b: sum(np.sum((predict(P, b) - MEAS[P]) ** 2) for P in (80, 200))  # noqa: E731
    b = minimize_scalar(sse, bounds=(0.0, 0.6), method="bounded").x

    fig, ax = plt.subplots(figsize=(5.4, 5.0))
    lim = np.array([65, 120])
    ax.fill_between(lim, lim - 1.6, lim + 1.6, color=GREEN, alpha=0.15, lw=0, label="±1.6 K (R3)")
    ax.plot(lim, lim, color=INK, lw=0.9)
    first = True
    for P, m in MEAS.items():
        u = predict(P, 0.0)
        ax.plot(m, u, "o", mfc="white", mec=GREY, ms=7, mew=1.3,
                label="uncalibrated (bypass 0)" if first else None)
        c = predict(P, b)
        if P == 140:
            ax.plot(m, c, "^", color=PINK, mec=INK, mew=0.5, ms=8,
                    label="140 W, validation set")
            for mi, ci, xt in zip(m, c, ((78, 93), (97, 86.5), (85.5, 101))):
                ax.annotate(f"{ci - mi:+.2f} K", xy=(mi, ci), xytext=xt, fontsize=7.8,
                            color="#7A2E5C", arrowprops=dict(arrowstyle="-", lw=0.6, color="#7A2E5C"))
        else:
            ax.plot(m, c, "o", color=BLUE, ms=6,
                    label=f"calibrated (bypass {b:.3f}), 80 and 200 W" if first else None)
            first = False
    ax.text(81, 72.5, "3.2 to 10.4 K\nbelow the diagonal", fontsize=7.8, color=GREY, ha="left")
    ax.set_xlim(*lim)
    ax.set_ylim(*lim)
    ax.set_aspect("equal")
    ax.set_xlabel("measured base temperature (°C)")
    ax.set_ylabel("predicted base temperature (°C)")
    ax.legend(loc="upper left", fontsize=7.8)
    ax.text(119, 67, "limit 1.6 K =\n0.6 K measurement (k = 2)\n+ 1.0 K model allowance",
            ha="right", va="bottom", fontsize=7.8,
            bbox=dict(boxstyle="round,pad=0.4", fc="white", ec=GREY, lw=0.8))
    save(fig, "30", "fig-30-6-validation-parity")


if __name__ == "__main__":
    fig_30_1()
    fig_30_2()
    fig_30_3()
    fig_30_4()
    fig_30_5()
    fig_30_6()
