"""Figures for Chapter 3 — Modeling and Simulation Workflow.

Run from the repository root:  python figures/scripts/ch03.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch  # noqa: E402
from scipy.linalg import expm  # noqa: E402
from scipy.integrate import solve_ivp  # noqa: E402
import schemdraw  # noqa: E402
import schemdraw.elements as elm  # noqa: E402

from figstyle import COLORS, INK, save, new_fig  # noqa: E402
from figstyle import schematic as _schematic  # noqa: E402

schemdraw.use("matplotlib")

BLUE, ORANGE, GREEN, PINK, YELLOW, SKY = COLORS[:6]
RED = "#C62828"
GREY = "#888888"
DGREEN = "#1E8A4C"


def schematic(*a, **k):
    """figstyle.schematic with the axes filling the figure (diagrams only)."""
    fig, ax = _schematic(*a, **k)
    fig.subplots_adjust(left=0.01, right=0.99, bottom=0.01, top=0.99)
    return fig, ax


def arr(ax, x0, y0, x1, y1, color=INK, lw=1.1, ls="-", rad=0.0, ms=9, z=2):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", color=color, lw=lw,
                                 ls=ls, mutation_scale=ms, shrinkA=0, shrinkB=0,
                                 connectionstyle=f"arc3,rad={rad}", zorder=z))


def rbox(ax, x, y, w, h, text, fc="white", ec=INK, lw=1.0, fs=8, weight="normal", z=3):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.15",
                                fc=fc, ec=ec, lw=lw, zorder=z))
    if text:
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
                weight=weight, zorder=z + 0.1, linespacing=1.15)


# ----------------------------------------------------------------------------
# Models (Listings 3.1-3.4)
# ----------------------------------------------------------------------------
P1 = dict(Ca=3000.0, Cv=15000.0, Cp=45.0, UA=0.7, Gav=1.5, Gpa=0.04, Gdoor=15.0,
          Tamb=30.0, Qc=60.0)


def thermal_A(Ca, Cv, Cp, g, Gav, Gpa):
    A = np.array([[-(g + Gav + Gpa), Gav, Gpa], [Gav, -Gav, 0], [Gpa, 0, -Gpa]])
    return A / np.array([[Ca], [Cv], [Cp]])


def seven_day(days=7, fault_h=114.0, seed=7, dt=5.0):
    """Listing 3.1 at full 5 s resolution: returns t (h), X = [air, load, probe]."""
    p = P1

    def zoh(g):
        A = thermal_A(p["Ca"], p["Cv"], p["Cp"], g, p["Gav"], p["Gpa"])
        B = np.array([[g / p["Ca"], -1 / p["Ca"]], [0, 0], [0, 0]])
        M = expm(np.block([[A, B], [np.zeros((2, 5))]]) * dt)
        return M[:3, :3], M[:3, 3:]
    closed, opened = zoh(p["UA"]), zoh(p["UA"] + p["Gdoor"])
    rng = np.random.default_rng(seed)
    N = int(days * 86400 // dt)
    door = np.zeros(N, bool)
    for t0 in (rng.uniform(8, 16, (days, 15)) * 3600 + np.arange(days)[:, None] * 86400).ravel():
        door[int(t0 / dt):int((t0 + rng.uniform(20, 60)) / dt)] = True
    x, on = np.array([4.0, 4.0, 4.0]), False
    X = np.empty((N, 3))
    for k in range(N):
        lo, hi = (-4.0, -1.0) if k * dt >= fault_h * 3600 else (2.5, 5.5)
        on = (x[0] > hi) or (on and x[0] > lo)
        Phi, Gam = opened if door[k] else closed
        x = Phi @ x + Gam @ np.array([p["Tamb"], p["Qc"] * on])
        X[k] = x
    return np.arange(1, N + 1) * dt / 3600, X


def lead_time(p, dt=5.0):
    """Listing 3.4: hours from the probe freeze alarm to the load reaching -0.5 degC."""
    A = thermal_A(p["Ca"], p["Cv"], p["Cp"], p["UA"], p["Gav"], p["Gpa"])
    B = np.array([[p["UA"] / p["Ca"], -1 / p["Ca"]], [0, 0], [0, 0]])
    M = expm(np.block([[A, B], [np.zeros((2, 5))]]) * dt)
    x, on, run, t_alarm = np.array([4.0, 4.0, 4.0]), True, 0, None
    for k in range(int(12 * 3600 / dt)):
        on = (x[0] > p["Toff"] + 3) or (on and x[0] > p["Toff"])
        x = M[:3, :3] @ x + M[:3, 3:] @ np.array([p["Tamb"], p["Qc"] * on])
        if k % 12 == 11:
            run = run + 1 if x[2] <= -0.5 else 0
            if run == 60 and t_alarm is None:
                t_alarm = (k + 1) * dt / 3600
        if x[1] <= -0.5:
            return (k + 1) * dt / 3600 - (t_alarm or np.inf)
    return np.nan


# M2 supply model (Listing 3.2)
OCV, R1, C1, CB = 3.65, 3.0, 3.0, 470e-6


def load_segments():
    segs = [(0.0, 0.75, 0.030)]
    for t in 0.75 + 0.005 * np.arange(200):
        segs += [(t, t + 0.001, 0.280), (t + 0.001, t + 0.005, 0.030)]
    segs += [(1.75, 2.5, 0.030), (2.5, 4.0, 5e-6)]
    return segs


def supply_exact(R0, Csc, Resr, dt=1e-4, T=4.0):
    """Exact (ZOH) discretisation of M2 on a 0.1 ms grid aligned with every load edge."""
    if Csc:
        A = np.array([[-(1 / R0 + 1 / Resr) / CB, 1 / (Resr * CB), -1 / (R0 * CB)],
                      [1 / (Resr * Csc), -1 / (Resr * Csc), 0],
                      [-1 / (R0 * C1), 0, -(1 / R0 + 1 / R1) / C1]])
        B = np.array([[1 / (R0 * CB), -1 / CB], [0, 0], [1 / (R0 * C1), 0]])
        x = np.array([OCV, OCV, 0.0])
    else:
        A = np.array([[-1 / (R0 * CB), -1 / (R0 * CB)],
                      [-1 / (R0 * C1), -(1 / R0 + 1 / R1) / C1]])
        B = np.array([[1 / (R0 * CB), -1 / CB], [1 / (R0 * C1), 0]])
        x = np.array([OCV, 0.0])
    n = A.shape[0]
    M = expm(np.block([[A, B], [np.zeros((2, n + 2))]]) * dt)
    Phi, Gam = M[:n, :n], M[:n, n:]
    N = int(round(T / dt))
    k = np.arange(N)
    i_load = np.full(N, 5e-6)
    i_load[k < 25000] = 0.030
    kb = k - 7500
    burst = (kb >= 0) & (kb < 10000) & ((kb % 50) < 10)
    i_load[burst] = 0.280
    v = np.empty(N + 1)
    v[0] = x[0]
    for j in range(N):
        x = Phi @ x + Gam @ np.array([OCV, i_load[j]])
        v[j + 1] = x[0]
    return np.arange(N + 1) * dt, v


def supply_one_call(R0, Csc, Resr):
    """Listing 3.2 with restart=False: one Radau call that steps over the bursts."""
    segs = load_segments()

    def rhs(t, y):
        vb, vc, v1 = y
        i = next((c for a, b, c in segs if a <= t < b), 5e-6)
        ib = (OCV - v1 - vb) / R0
        isc = (vc - vb) / Resr
        return [(ib + isc - i) / CB, -isc / Csc, (ib - v1 / R1) / C1]
    s = solve_ivp(rhs, (0, 4.0), [OCV, OCV, 0.0], method="Radau", rtol=1e-6, atol=1e-8)
    return s.t, s.y[0]


# Validation plant and fitted model (Listing 3.3, Table 3.6)
def lin_sim(A, B, x0, u, n_min=241):
    n, m = A.shape[0], B.shape[1]
    M = expm(np.block([[A, B], [np.zeros((m, n + m))]]) * 60.0)
    X = [np.asarray(x0, float)]
    for _ in range(n_min - 1):
        X.append(M[:n, :n] @ X[-1] + M[:n, n:] @ u)
    return np.array(X)


def plant4(Tamb, Cv=15000.0, n_min=241):
    A4 = np.array([[-4.54, 3.0, 1.5, 0.04], [3.0, -3.75, 0, 0], [1.5, 0, -1.5, 0],
                   [0.04, 0, 0, -0.04]]) / np.array([[1500], [4000], [Cv], [45]])
    liner0 = (3.0 * 4.0 + 0.75 * Tamb) / 3.75          # steady liner with air at 4 degC
    return lin_sim(A4, np.array([[0], [0.75 / 4000], [0], [0]]),
                   [4.0, liner0, 4.0, 4.0], np.array([Tamb]), n_min)


def model3(Tamb, Cv=15000.0, Ca=3793.0, UA=0.5844, Gav=1.52, Gpa=0.04129, n_min=241):
    A = thermal_A(Ca, Cv, 45.0, UA, Gav, Gpa)
    return lin_sim(A, np.array([[UA / Ca], [0], [0]]), [4.0, 4.0, 4.0], np.array([Tamb]), n_min)


def crossing(t, y, thr=8.0):
    i = int(np.argmax(y >= thr))
    return t[i - 1] + (thr - y[i - 1]) / (y[i] - y[i - 1]) * (t[i] - t[i - 1])


# ----------------------------------------------------------------------------
# Figure 3.1 — workflow
# ----------------------------------------------------------------------------
def fig_3_1():
    fig, ax = schematic(6.8, 4.5, xlim=(0, 20), ylim=(0, 13.2))
    w, h = 3.45, 2.3
    xs = [0.2 + i * 3.97 for i in range(5)]
    y1, y2 = 8.2, 3.2
    row1 = ["Question and\naccuracy\n(from requirement)", "Assumptions\nregister",
            "Equivalent circuit\nand equations", "Solver selection\nand verification",
            "Simulation\n(system level,\ncomponent level)"]
    row2 = ["Reproducibility\nrecord (config,\nversions, seed,\nmanifest)",
            "Decision (design\nchange, req.\nchange, test plan)",
            "Validation\nagainst\nindependent data", "Sensitivity\nanalysis",
            "Parameter\nestimation\n(from test data)"]
    for i, t in enumerate(row1):
        rbox(ax, xs[i], y1, w, h, t, fc="#E3EDF7", fs=7.8)
        if i < 4:
            arr(ax, xs[i] + w, y1 + h / 2, xs[i + 1], y1 + h / 2)
    for i, t in enumerate(row2):
        rbox(ax, xs[i], y2, w, h, t, fc="#E4F2EA" if i > 1 else "#FBEBD7", fs=7.8)
        if i > 0:
            arr(ax, xs[i], y2 + h / 2, xs[i - 1] + w, y2 + h / 2)
    arr(ax, xs[4] + w * 0.2, y1, xs[4] + w * 0.2, y2 + h)
    # feedback loops
    fb = dict(color=RED, lw=1.1, ls="--")
    arr(ax, xs[4] + w * 0.75, y1 + h, xs[3] + w * 0.75, y1 + h, rad=0.45, **fb)
    ax.text((xs[3] + xs[4]) / 2 + w * 0.75, y1 + h + 1.35, "solver disagreement", ha="center",
            fontsize=7.2, color=RED)
    arr(ax, xs[2] + w * 0.3, y2 + h, xs[1] + w * 0.7, y1, **fb)
    ax.text(xs[2] - 0.1, (y1 + y2 + h) / 2 + 0.1, "validation\nfails", ha="center", va="center",
            fontsize=7.2, color=RED, bbox=dict(fc="white", ec="none", pad=0.3))
    arr(ax, xs[3] + w * 0.5, y2, xs[4] + w * 0.4, y2, rad=0.45, **fb)
    ax.text((xs[3] + xs[4]) / 2 + w * 0.45, y2 - 1.45, "sensitivity high on a poorly known\n"
            "parameter → test plan, re-estimate", ha="center", va="center", fontsize=7.0,
            color=RED)
    rbox(ax, xs[4] + w * 0.38, 5.95, w * 0.62, 1.45, "non-identi-\nfiable →\nexperiment\ndesign",
         fc="#FDECEC", ec=RED, fs=6.6)
    arr(ax, xs[4] + w * 0.9, y2 + h, xs[4] + w * 0.9, 5.95, color=RED, ls="--")
    arr(ax, xs[4] + w * 0.5, 5.95, xs[4] + w * 0.5, y2 + h, color=RED, ls="--")
    # model tags
    for i, (t, c) in enumerate([("M1 thermal: minutes to days", BLUE),
                                ("M2 supply pulse: 100 µs to 10 s", ORANGE)]):
        ax.text(0.25 + i * 6.6, 12.5, t, fontsize=7.8, color=c, va="center",
                bbox=dict(fc="white", ec=c, lw=0.8, boxstyle="round,pad=0.3"))
    ax.text(0.2, 0.6, "Solid arrows: forward workflow.   Dashed red: loops back to earlier steps.",
            fontsize=7.2, color="#555555", style="italic")
    save(fig, "03", "fig-3-1-modeling-workflow")


# ----------------------------------------------------------------------------
# Figure 3.2 — equivalent circuits
# ----------------------------------------------------------------------------
def fig_3_2():
    fig = plt.figure(figsize=(6.8, 5.3))
    axT = fig.add_axes([0.0, 0.50, 1.0, 0.44])
    axB = fig.add_axes([0.0, 0.0, 1.0, 0.42])
    for a in (axT, axB):
        a.axis("off")
    fig.text(0.01, 0.985, "(a) M1 thermal network (temperature ≙ voltage, heat flow ≙ current)",
             fontsize=8.5, weight="bold", va="top")
    fig.text(0.01, 0.455, "(b) M2 supply network for the transmit pulse", fontsize=8.5,
             weight="bold", va="top")
    U = 2.5

    def T(ax, x, y, s, ha="left", va="center", **k):
        ax.text(x, y, s, ha=ha, va=va, fontsize=7.6, linespacing=1.15, **k)
    # (a) thermal network
    d = schemdraw.Drawing(canvas=axT, show=False)
    d.config(unit=U, lw=1.0, fontsize=7.6)
    d.add(elm.SourceV().up().at((0, 0)))
    d.add(elm.Line().up(1.5))
    d.add(elm.Switch().right())
    d.add(elm.Resistor().right())
    d.add(elm.Line().down(1.5))
    d.add(elm.Resistor().right().at((0, U)))
    d.add(elm.Line().right())
    d.add(elm.Dot())
    d.add(elm.Capacitor().down())
    d.add(elm.Line().right().at((2 * U, U)))
    d.add(elm.Dot())
    d.add(elm.SourceI().down())
    d.add(elm.Resistor().right().at((3 * U, U)))
    d.add(elm.Line().right(1.0))
    d.add(elm.Dot())
    d.add(elm.Capacitor().down())
    d.add(elm.Line().up(3.0).at((3 * U, U)))
    d.add(elm.Resistor().right())
    d.add(elm.Line().right(3.5))
    d.add(elm.Dot())
    d.add(elm.Capacitor().down())
    d.add(elm.Line().down(3.0))
    d.add(elm.Line().left().to((0, 0)))
    d.add(elm.Ground().at((0, 0)))
    d.draw(show=False)
    axT.set_aspect("equal")
    T(axT, -0.75, U / 2, "$T_{amb}$\n30 °C", ha="right")
    T(axT, 0.2, U + 1.5 + 0.45, "door open", ha="left", va="bottom")
    T(axT, 1.5 * U + 0.8, U + 1.5 + 0.45, "$1/G_{door}$, $G_{door}$ = 15 W/K", ha="center",
      va="bottom")
    T(axT, U / 2 + 0.8, U - 0.35, "$1/UA$, UA = 0.7 W/K", ha="center", va="top")
    T(axT, 2 * U - 0.15, U + 0.25, "$T_a$ (air)", ha="right", va="bottom", weight="bold")
    T(axT, 2 * U - 0.45, U / 2 - 0.2, "$C_a$\n3000 J/K", ha="right")
    T(axT, 3 * U + 0.75, U / 2, "$Q_c$ = 60 W\non > 5.5 °C\noff < 2.5 °C")
    T(axT, 3.5 * U + 0.35, U + 0.45, "$1/G_{pa}$ 0.04 W/K", ha="center", va="bottom")
    xp = 4 * U + 1.0
    T(axT, xp + 0.15, U + 0.25, "$T_p$ → sensor", va="bottom", weight="bold")
    T(axT, xp + 0.45, U / 2, "$C_p$\n45 J/K")
    T(axT, 3.5 * U + 0.35, U + 3.0 + 0.45, "$1/G_{av}$ 1.5 W/K", ha="center", va="bottom")
    xv = 4 * U + 3.5
    T(axT, xv + 0.15, U + 3.0 + 0.25, "$T_v$ (vaccine load)", va="bottom", weight="bold")
    T(axT, xv + 0.45, U + 3.0 - U / 2, "$C_v$\n15000 J/K")
    axT.set_xlim(-2.6, 20.0)
    axT.set_ylim(-1.0, 6.9)
    # (b) supply network
    d2 = schemdraw.Drawing(canvas=axB, show=False)
    d2.config(unit=U, lw=1.0, fontsize=7.6)
    d2.add(elm.SourceV().up().at((0, 0)))
    d2.add(elm.Resistor().right())
    d2.add(elm.Line().right(1.0))
    d2.add(elm.Dot())
    d2.add(elm.Line().up(1.0))
    d2.add(elm.Resistor().right())
    d2.add(elm.Line().down(1.0))
    d2.add(elm.Line().down(1.0).at((U + 1.0, U)))
    d2.add(elm.Capacitor().right())
    d2.add(elm.Line().up(1.0))
    d2.add(elm.Dot())
    d2.add(elm.Line().right(1.5))
    d2.add(elm.Dot())
    d2.add(elm.Resistor().down(U / 2))
    d2.add(elm.Capacitor().down(U / 2))
    d2.add(elm.Line().right(3.0).at((2 * U + 2.5, U)))
    d2.add(elm.Capacitor().down())
    d2.add(elm.Line().right(3.0).at((2 * U + 5.5, U)))
    d2.add(elm.SourceI().down())
    d2.add(elm.Line().left().to((0, 0)))
    d2.add(elm.Ground().at((0, 0)))
    d2.draw(show=False)
    axB.set_aspect("equal")
    T(axB, -0.75, U / 2, "OCV\n3.65 V\n(2 × ER14505)", ha="right")
    T(axB, U / 2 + 0.3, U + 0.45, "$R_0$ = 4 Ω fresh,\n12 Ω end of life", ha="center",
      va="bottom")
    T(axB, 1.5 * U + 1.0, U + 1.0 + 0.45, "$R_1$ = 3 Ω", ha="center", va="bottom")
    T(axB, 1.5 * U + 1.0, U - 1.0 - 0.5, "$C_1$ = 3 F  (τ = 9 s)", ha="center", va="top")
    xv = 2 * U + 2.5
    T(axB, xv + 0.6, U + 0.3, "$V$ (module pins)\n$V$ ≥ 3.0 V", ha="center", va="bottom",
      weight="bold")
    T(axB, xv + 0.45, U * 0.75, "ESR 0.25 Ω")
    T(axB, xv + 0.45, U * 0.25, "EDLC 0.47 F")
    T(axB, xv + 3.45, U / 2, "470 µF\npolymer")
    T(axB, xv + 6.75, U / 2, "$i_{load}(t)$: 30 mA for 2.5 s;\n280 mA in 1 ms bursts\n"
      "every 5 ms for 1 s")
    axB.set_xlim(-2.6, 20.0)
    axB.set_ylim(-1.0, 4.9)
    save(fig, "03", "fig-3-2-equivalent-circuits")


# ----------------------------------------------------------------------------
# Figure 3.3 — seven-day system simulation
# ----------------------------------------------------------------------------
def fig_3_3():
    t, X = seven_day()
    air, vac, probe = X.T
    S = X[::12]                                  # logger: one sample per minute
    ts = np.arange(len(S)) / 60.0                # Listing 3.1 time convention (h)
    n4 = 4 * 1440
    cross_idx = np.where((S[1:n4, 0] > 8) & (S[:n4 - 1, 0] <= 8))[0] + 1
    run = np.convolve(S[:, 2] <= -0.5, np.ones(60), "valid")
    i_alarm = int(np.argmax(run == 60) + 59)
    t_alarm = i_alarm / 60
    t_load = np.argmax(S[:, 1] <= -0.5) / 60
    fig = plt.figure(figsize=(6.8, 3.9))
    ax = fig.add_axes([0.08, 0.13, 0.60, 0.80])
    axi = fig.add_axes([0.765, 0.13, 0.225, 0.80])
    ax.plot(t, air, color=GREY, lw=0.45, label="shelf air")
    ax.plot(t, probe, color=BLUE, lw=1.4, label="probe")
    ax.plot(t, vac, color=GREEN, lw=1.7, label="vaccine load")
    for yv in (8, -0.5):
        ax.axhline(yv, color=INK, ls="--", lw=0.8)
    ax.text(1, 8.25, "+8 °C", fontsize=7.5)
    ax.text(1, -1.3, "−0.5 °C", fontsize=7.5)
    for i in cross_idx:
        ax.plot([ts[i]] * 2, [13.2, 13.9], color=RED, lw=0.9)
    ax.text(48, 12.9, f"{len(cross_idx)} air-rule (> 8 °C) alarms, days 1–4", color=RED,
            fontsize=7.5, ha="center", va="top")
    ax.axvline(114, color=RED, ls=":", lw=1.0)
    ax.text(116, 11.5, "thermostat\nfault\n114 h", color=RED, fontsize=7.5, ha="left", va="top")
    ax.axvspan(106, 120, color=YELLOW, alpha=0.12, lw=0)
    ax.set_xlim(0, 168)
    ax.set_ylim(-5, 14)
    ax.set_xticks(np.arange(0, 169, 24))
    ax.set_xlabel("Time (h)")
    ax.set_ylabel("Temperature (°C)")
    ax.legend(loc="lower left", fontsize=7.5, ncol=3, bbox_to_anchor=(0.0, 0.0))
    # inset: hours 106-120
    m = (t >= 106) & (t <= 120)
    axi.set_facecolor("#FFFBEA")
    axi.plot(t[m], air[m], color=GREY, lw=0.5)
    axi.plot(t[m], probe[m], color=BLUE, lw=1.3)
    axi.plot(t[m], vac[m], color=GREEN, lw=1.5)
    axi.axhline(-0.5, color=INK, ls="--", lw=0.7)
    axi.axvline(114, color=RED, ls=":", lw=0.9)
    pa = S[i_alarm, 2]
    axi.plot([t_alarm], [pa], "v", color=RED, ms=6, zorder=5)
    axi.plot([t_load], [-0.5], "s", color=GREEN, ms=5, zorder=5)
    axi.annotate("", (t_load, -4.55), (t_alarm, -4.55),
                 arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.8, mutation_scale=7))
    axi.text((t_alarm + t_load) / 2, -4.75, f"{t_load - t_alarm:.2f} h warning", fontsize=6.6,
             ha="center", va="top")
    axi.plot([t_alarm, t_alarm], [pa, -4.55], color=RED, lw=0.5, ls=":")
    axi.plot([t_load, t_load], [-0.5, -4.55], color=GREEN, lw=0.5, ls=":")
    axi.text(113.8, 1.8, f"probe freeze\nalarm\n{t_alarm:.2f} h", fontsize=6.5, color=RED,
             ha="right", va="top")
    axi.text(t_load + 0.2, 0.0, f"load\n−0.5 °C\n{t_load:.2f} h", fontsize=6.5, color=GREEN,
             ha="left", va="bottom")
    axi.set_xlim(106, 120)
    axi.set_ylim(-5.6, 7)
    axi.set_xticks([106, 110, 114, 118])
    axi.tick_params(labelsize=7)
    axi.set_xlabel("Time (h)", fontsize=8)
    axi.set_title("inset: hours 106–120", fontsize=7.5)
    save(fig, "03", "fig-3-3-seven-day-simulation")


# ----------------------------------------------------------------------------
# Figure 3.4 — supply pulse simulation
# ----------------------------------------------------------------------------
def fig_3_4():
    runs = [(0.0, 1.0, "no EDLC", RED), (0.1, 0.5, "0.1 F (Rev B)", ORANGE),
            (0.47, 0.25, "0.47 F (Rev C)", BLUE)]
    fig = plt.figure(figsize=(6.6, 4.6))
    ax = fig.add_axes([0.11, 0.25, 0.86, 0.68])
    res = {}
    for Csc, Resr, name, c in runs:
        t, v = supply_exact(12.0, Csc, Resr)
        res[name] = (t, v)
        ax.plot(t, v, color=c, lw=0.8, label=f"{name}: min {v.min():.2f} V")
    t1, v1 = supply_one_call(12.0, 0.47, 0.25)
    ax.plot(t1, v1, color=GREY, ls=":", lw=1.6,
            label=f"0.47 F, one Radau call: min {v1.min():.2f} V")
    ax.text(3.0, v1[np.searchsorted(t1, 3.0)] + 0.02, "stepped over the bursts", fontsize=7.5,
            color="#555555", ha="center", va="bottom")
    ax.axhline(3.0, color=RED, ls="--", lw=1.0)
    ax.text(0.03, 2.985, "3.0 V module brownout", color=RED, fontsize=7.5, ha="left", va="top")
    ax.axhline(3.2, color=DGREEN, ls="--", lw=1.0)
    ax.text(3.98, 3.215, "3.2 V design limit", color=DGREEN, fontsize=7.5, ha="right",
            va="bottom")
    ax.axvspan(0.75, 1.75, color=GREY, alpha=0.08, lw=0)
    ax.text(1.25, 2.32, "250 mA bursts\n(1 ms every 5 ms)", fontsize=7, ha="center",
            va="bottom", color="#555555")
    ax.set_xlim(0, 4)
    ax.set_ylim(2.3, 3.7)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Voltage at module pins (V)")
    ax.legend(loc="upper center", fontsize=7.4, ncol=2, bbox_to_anchor=(0.5, -0.13))
    ax.set_title("End-of-life pack, $R_0$ = 12 Ω", fontsize=9)
    axi = fig.add_axes([0.60, 0.36, 0.35, 0.19])
    for Csc, Resr, name, c in runs:
        t, v = res[name]
        m = (t >= 1.0) & (t <= 1.02)
        axi.plot(t[m] * 1000 - 1000, v[m], color=c, lw=1.0)
    axi.set_xlim(0, 20)
    axi.set_xticks([0, 5, 10, 15, 20])
    axi.set_xlabel("t − 1.000 s (ms)", fontsize=7, labelpad=1)
    axi.tick_params(labelsize=6.5)
    axi.set_title("inset: single bursts, 1.000–1.020 s", fontsize=7, pad=2)
    save(fig, "03", "fig-3-4-supply-pulse-simulation")


# ----------------------------------------------------------------------------
# Figure 3.5 — tornado
# ----------------------------------------------------------------------------
def fig_3_5():
    NOM = dict(Ca=3000.0, Cv=15000.0, Cp=45.0, UA=0.7, Gav=1.5, Gpa=0.04, Qc=60.0, Tamb=30.0,
               Toff=-4.0)
    y0 = lead_time(NOM)
    rows = []
    for k in NOM:
        lo = lead_time({**NOM, k: NOM[k] * 0.8})
        hi = lead_time({**NOM, k: NOM[k] * 1.2})
        rows.append((k, lo, hi, (hi - lo) / (0.4 * y0)))
    rows.sort(key=lambda r: abs(r[2] - r[1]) if False else abs(r[1] - r[2]))
    names = {"Toff": "$T_{off}$", "Gav": "$G_{av}$", "Cv": "$C_v$", "Gpa": "$G_{pa}$",
             "Cp": "$C_p$", "UA": "UA", "Tamb": "$T_{amb}$", "Qc": "$Q_c$", "Ca": "$C_a$"}
    fig, ax = new_fig(6.4, 3.9)
    ax.axvspan(0.8, 1.0, color=RED, alpha=0.12, lw=0)
    ax.text(0.9, len(rows) - 0.6, "< 1 h\nwarning", color=RED, fontsize=7.2, ha="center",
            va="top")
    for i, (k, lo, hi, S) in enumerate(rows):
        ax.barh(i, lo - y0, left=y0, height=0.36, color=BLUE, align="edge")
        ax.barh(i - 0.36, hi - y0, left=y0, height=0.36, color=ORANGE, align="edge")
        ax.text(3.12, i, f"S = {S:+.2f}", fontsize=7.5, va="center")
        if abs(lo - y0) > 0.15:
            ax.text(lo + (0.02 if lo > y0 else -0.02), i + 0.18, f"{lo:.2f}", fontsize=6.8,
                    va="center", ha="left" if lo > y0 else "right", color=BLUE)
        if abs(hi - y0) > 0.15:
            ax.text(hi + (0.02 if hi > y0 else -0.02), i - 0.18, f"{hi:.2f}", fontsize=6.8,
                    va="center", ha="left" if hi > y0 else "right", color=ORANGE)
    ax.axvline(y0, color=INK, lw=1.0)
    ax.text(y0 + 0.03, len(rows) - 0.25, f"nominal {y0:.2f} h", ha="left", va="bottom",
            fontsize=8)
    ax.set_yticks(np.arange(len(rows)))
    ax.set_yticklabels([names[r[0]] for r in rows], fontsize=9)
    ax.set_xlim(0.8, 3.5)
    ax.set_xticks([1.0, 1.5, 2.0, 2.5, 3.0])
    ax.set_ylim(-0.7, len(rows) + 0.15)
    ax.set_xlabel("Freeze-alarm lead time (h)")
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=BLUE, label="parameter −20 %"),
                       Patch(color=ORANGE, label="parameter +20 %")], loc="lower left",
              bbox_to_anchor=(0.1, 0.0), fontsize=7.8)
    save(fig, "03", "fig-3-5-lead-time-tornado")


# ----------------------------------------------------------------------------
# Figure 3.6 — validation record V1
# ----------------------------------------------------------------------------
def fig_3_6():
    tr = plant4(43.0, n_min=481)
    t = np.arange(len(tr)) * 1.0                       # minutes
    meas = np.delete(tr, 1, axis=1) + np.random.default_rng(1).normal(0, 0.05, (len(t), 3))
    mod = model3(43.0, n_min=481)
    th = t / 60
    resid = mod[:, 2] - meas[:, 2]
    rms8 = np.sqrt(np.mean(resid ** 2))
    rms = np.sqrt(np.mean(resid[:241] ** 2))
    cp_p, cp_m = crossing(t, tr[:, 3]), crossing(t, mod[:, 2])
    cl_p, cl_m = crossing(t, tr[:, 2]), crossing(t, mod[:, 1])
    fig, (ax, ax2) = plt.subplots(2, 1, figsize=(6.6, 4.8), sharex=True,
                                  gridspec_kw=dict(height_ratios=[2.3, 1], hspace=0.08))
    ax.plot(th, meas[:, 0], color=GREY, lw=0.8, label="air, plant")
    ax.plot(th[::3], meas[::3, 2], "o", ms=2.3, color=BLUE, alpha=0.7, label="probe, plant")
    ax.plot(th, mod[:, 2], color=BLUE, lw=1.4, label="probe, model")
    ax.plot(th[::3], meas[::3, 1], "o", ms=2.3, color=GREEN, alpha=0.7, label="load, plant")
    ax.plot(th, mod[:, 1], color=GREEN, lw=1.4, label="load, model")
    ax.axhline(8, color=INK, ls="--", lw=0.8)
    for tp_, tm_, c, y_t, name in [(cp_p, cp_m, BLUE, 13.0, "probe"),
                                   (cl_p, cl_m, GREEN, 3.0, "load")]:
        ax.plot([tp_ / 60, tm_ / 60], [8, 8], "|", ms=10, mew=1.5, color=c)
        ax.text(tm_ / 60 + 0.05, y_t, f"{name} crosses 8 °C:\nplant {tp_:.1f} min, "
                f"model {tm_:.1f} min", fontsize=7.2, color=c, va="center")
    ax.annotate("", (cp_p / 60, 8.4), (cp_m / 60 + 0.05, 12.2),
                arrowprops=dict(arrowstyle="-", color=BLUE, lw=0.6))
    ax.annotate("", (cl_m / 60, 7.6), (cl_m / 60 + 0.05, 3.9),
                arrowprops=dict(arrowstyle="-", color=GREEN, lw=0.6))
    ax.set_ylim(0, 35)
    ax.set_ylabel("Temperature (°C)")
    ax.legend(loc="upper left", fontsize=7.3, ncol=2)
    ax.set_title("V1: power outage at 43 °C ambient, full load (stand-in plant data)",
                 fontsize=9)
    ax2.axhspan(-0.3, 0.3, color=GREEN, alpha=0.12, lw=0)
    ax2.text(3.95, 0.33, "criterion (c): RMS ≤ 0.3 °C", fontsize=7.2, ha="right",
             va="bottom", color=DGREEN)
    ax2.plot(th, resid, color=BLUE, lw=1.0)
    ax2.axhline(0, color=INK, lw=0.6)
    k = int(np.argmax(np.abs(resid)))
    ax2.annotate(f"peak {resid[k]:+.2f} °C at {t[k]:.0f} min", (th[k], resid[k]),
                 (th[k] + 0.35, -0.8), fontsize=7.2, va="center",
                 arrowprops=dict(arrowstyle="-", lw=0.6))
    ax2.text(3.95, -0.75, f"RMS {rms:.2f} °C over 0–4 h,\n{rms8:.2f} °C over the 8 h record",
             fontsize=7.3, ha="right", va="center")
    ax2.set_ylim(-1, 1)
    ax2.set_xlim(0, 4)
    ax2.set_ylabel("Probe residual\nmodel − plant (°C)", fontsize=8.5)
    ax2.set_xlabel("Time since power cut (h)")
    save(fig, "03", "fig-3-6-validation-43c-outage")


if __name__ == "__main__":
    fig_3_1()
    fig_3_2()
    fig_3_3()
    fig_3_4()
    fig_3_5()
    fig_3_6()
