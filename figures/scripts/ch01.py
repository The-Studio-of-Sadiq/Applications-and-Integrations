"""Figures for Chapter 1 — From Requirement to Working System.

Run from the repository root:  python figures/scripts/ch01.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch  # noqa: E402
from scipy.linalg import expm  # noqa: E402
from scipy.stats import chi2  # noqa: E402

from figstyle import COLORS, INK, box, save, schematic, new_fig  # noqa: E402

BLUE, ORANGE, GREEN, PINK, YELLOW, SKY = COLORS[:6]
RED = "#C62828"
GREY = "#888888"
LIGHT = "#F2F2F2"


def harrow(ax, x0, y0, x1, y1, color=INK, lw=1.1, ls="-", both=False, ms=10, rad=0.0, z=2):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1),
                                 arrowstyle="<|-|>" if both else "-|>", color=color, lw=lw,
                                 ls=ls, mutation_scale=ms, shrinkA=0, shrinkB=0,
                                 connectionstyle=f"arc3,rad={rad}", zorder=z))


# ----------------------------------------------------------------------------
# Figure 1.1 — V-shaped chain from problem to acceptance
# ----------------------------------------------------------------------------
def fig_1_1():
    fig, ax = schematic(6.8, 5.2, xlim=(0, 17), ylim=(-0.3, 13.4))
    w, h = 5.6, 1.42
    left = ["Problem statement (1.1)",
            "Stakeholder needs\nSN1–SN8 (1.2)",
            "System requirements R1–R12\n(functional + nonfunctional)\n(1.3–1.4)",
            "Boundary and constraints\nC1–C8 (1.5–1.6)",
            "Design specifications\nSP1–SP10 and budgets (1.7)",
            "Architecture and detailed\ndesign (Ch. 2–3)"]
    right = {0: "Acceptance by\nthe programme",
             1: "Pilot validation against\nSN1–SN8 (field trial,\n60 fridge-months)",
             2: "System verification against\nR1–R12 (AT1–AT9)",
             4: "Specification verification\n(budgets measured)",
             5: "Unit and integration\ntests (Ch. 4)"}
    ytop, dy = 11.2, 1.85
    lx = [0.85 + 0.36 * i for i in range(6)]
    rx = [17 - 0.2 - w - 0.36 * i for i in range(6)]
    ly = [ytop - dy * i for i in range(6)]
    for i, t in enumerate(left):
        box(ax, lx[i], ly[i], w, h, t, fc="#E3EDF7", fontsize=7.8)
        if i < 5:
            harrow(ax, lx[i] + w / 2, ly[i], lx[i + 1] + w / 2, ly[i + 1] + h)
    for i, t in right.items():
        box(ax, rx[i], ly[i], w, h, t, fc="#E4F2EA", fontsize=7.8)
    order = [5, 4, 2, 1, 0]
    for a, b in zip(order[:-1], order[1:]):
        harrow(ax, rx[a] + w / 2, ly[a] + h, rx[b] + w / 2, ly[b])
    # Build at bottom
    bx, by = 8.5 - 1.6, 0.0
    box(ax, bx, by, 3.2, 1.1, "Build (Ch. 4)", fc="#FBEBD7", fontsize=9)
    harrow(ax, lx[5] + w / 2, ly[5], bx, by + 0.55)
    harrow(ax, bx + 3.2, by + 0.55, rx[5] + w / 2, ly[5])
    # traceability links
    for i in (0, 1, 2, 4, 5):
        harrow(ax, lx[i] + w, ly[i] + h / 2, rx[i], ly[i] + h / 2, color=GREY, ls="--",
               both=True, lw=0.9, ms=8)
    harrow(ax, lx[3] + w, ly[3] + h / 2, rx[2] + 0.4, ly[2], color=GREY, ls="--",
           both=True, lw=0.9, ms=8)
    xm = (lx[1] + w + rx[1]) / 2
    ax.text(xm, ly[1] + h / 2 + 0.12, "traceability (1.8)", ha="center", va="bottom",
            fontsize=8, color="#555555", style="italic")
    # acceptance-criteria band along the left leg
    ax.add_patch(Rectangle((0.15, ly[5]), 0.42, ly[0] + h - ly[5], fc="#F6D9D9", ec=RED, lw=0.8))
    ax.text(0.36, (ly[5] + ly[0] + h) / 2, "acceptance criteria written here (1.9)",
            rotation=90, ha="center", va="center", fontsize=8, color=RED)
    ax.add_patch(FancyArrowPatch((0.36, ly[0] + h), (rx[0] + w / 2, ly[0] + h),
                                 arrowstyle="-|>", color=RED, lw=1.0, mutation_scale=10,
                                 connectionstyle="arc,angleA=90,angleB=90,armA=10,armB=10,rad=0.6"))
    ax.text(8.5, ly[0] + h + 0.42, "limits fixed before the build close the right leg",
            ha="center", va="bottom", fontsize=8, color=RED)
    ax.text(3.6, 0.55, "define and allocate", ha="center", fontsize=8.5, color=BLUE, style="italic")
    ax.text(13.4, 0.55, "verify and validate", ha="center", fontsize=8.5, color=GREEN, style="italic")
    save(fig, "01", "fig-1-1-requirements-v-chain")


# ----------------------------------------------------------------------------
# Thermal model of Chapter 3 (Listing 3.1), used for Figure 1.2
# ----------------------------------------------------------------------------
def ccm1_simulation(days=7, fault_h=114.0, seed=7, dt=5.0):
    """Return t (h) at 5 s steps and X (air, vaccine, probe) of Listing 3.1."""
    Ca, Cv, Cp = 3000.0, 15000.0, 45.0
    UA, Gav, Gpa, Gdoor = 0.7, 1.5, 0.04, 15.0
    Tamb, Qc = 30.0, 60.0

    def zoh(g):
        A = np.array([[-(g + Gav + Gpa), Gav, Gpa], [Gav, -Gav, 0], [Gpa, 0, -Gpa]])
        A /= np.array([[Ca], [Cv], [Cp]])
        B = np.array([[g / Ca, -1 / Ca], [0, 0], [0, 0]])
        M = expm(np.block([[A, B], [np.zeros((2, 5))]]) * dt)
        return M[:3, :3], M[:3, 3:]
    closed, opened = zoh(UA), zoh(UA + Gdoor)
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
        x = Phi @ x + Gam @ np.array([Tamb, Qc * on])
        X[k] = x
    return np.arange(1, N + 1) * dt / 3600, X


def fig_1_2():
    t, X = ccm1_simulation()
    air, vac, probe = X.T
    # 1-min logger samples for the alarm rules (as Listing 3.1)
    S = X[::12]
    ts = np.arange(len(S)) / 60.0
    n4 = 4 * 1440
    air_alarms = int(np.sum((S[1:n4, 0] > 8) & (S[:n4 - 1, 0] <= 8)))
    fault = 114.0
    run = np.convolve(S[:, 2] <= -0.5, np.ones(60), "valid")
    t_alarm = ts[np.argmax(run == 60) + 59]
    t_probe = ts[np.argmax((S[:, 2] <= -0.5) & (ts > fault))]
    t_load = ts[np.argmax(S[:, 1] <= -0.5)]
    off = 72.0                                  # show days 4-5 as "day 1-2"
    m = (t > off) & (t <= off + 48)
    tt = t[m] - off
    fig, ax = new_fig(6.6, 4.0)
    ax.axhspan(2, 8, color=GREEN, alpha=0.08, lw=0)
    ax.text(0.6, 7.6, "safe range 2–8 °C", fontsize=8, color=GREEN, va="top")
    ax.plot(tt, air[m], color=GREY, lw=0.6, label="shelf air")
    ax.plot(tt, probe[m], color=BLUE, lw=1.6, label="probe (10 mL buffered vial)")
    ax.plot(tt, vac[m], color=ORANGE, lw=1.8, label="vaccine load")
    ax.axhline(-0.5, color=INK, ls=":", lw=0.9)
    ax.text(0.6, -0.35, "−0.5 °C freeze limit", fontsize=7.5, va="bottom")
    fx = fault - off
    ax.axvline(fx, color=RED, ls="--", lw=1.0)
    ax.text(fx - 0.4, 14.6, "thermostat turned\nto coldest (18:00)", color=RED, fontsize=7.5,
            ha="right", va="top")
    ta, tp, tl = t_alarm - off, t_probe - off, t_load - off
    ax.plot([tp], [-0.5], "o", ms=4, color=BLUE)
    ax.annotate(f"probe ≤ −0.5 °C\n(+{(t_probe - fault) * 60:.0f} min)", (tp, -0.5), (fx - 9.5, -3.6),
                fontsize=7.5, color=BLUE, arrowprops=dict(arrowstyle="-", color=BLUE, lw=0.7))
    ax.plot([ta], [S[np.searchsorted(ts, t_alarm), 2]], "v", ms=7, color=RED)
    ax.annotate(f"probe freeze alarm\n(60 min ≤ −0.5 °C)\nfault + {t_alarm - fault:.1f} h",
                (ta, S[np.searchsorted(ts, t_alarm), 2]), (fx - 13.5, -0.1), fontsize=7.5,
                color=RED, arrowprops=dict(arrowstyle="-", color=RED, lw=0.7))
    ax.plot([tl], [-0.5], "s", ms=4.5, color=ORANGE)
    ax.annotate(f"load reaches −0.5 °C\nfault + {t_load - fault:.1f} h", (tl, -0.5), (fx + 0.5, 5.6),
                fontsize=7.5, color=ORANGE, arrowprops=dict(arrowstyle="-", color=ORANGE, lw=0.7))
    ax.text(12.0, -2.8, f"air > 8 °C: {air_alarms} crossings\nin 4 days (prototype rule)",
            fontsize=7.3, ha="center", va="center", bbox=dict(fc="white", ec=GREY, lw=0.6))
    ax.set_xlim(0, 48)
    ax.set_ylim(-5, 15)
    ax.set_xticks(np.arange(0, 49, 6))
    ax.set_xticklabels(["00:00", "06:00", "12:00", "18:00", "00:00", "06:00", "12:00",
                        "18:00", "24:00"], fontsize=8)
    ax.text(12, -7.3, "day 1", ha="center", fontsize=8.5)
    ax.text(36, -7.3, "day 2", ha="center", fontsize=8.5)
    ax.set_ylabel("Temperature (°C)")
    ax.legend(loc="upper left", fontsize=7.8)
    ax.text(48, -8.6, "Simulated with the model of Chapter 3 to match the site-visit record.",
            ha="right", fontsize=7, color="#555555", style="italic")
    save(fig, "01", "fig-1-2-site-visit-trace")


# ----------------------------------------------------------------------------
# Figure 1.3 — context diagram
# ----------------------------------------------------------------------------
def fig_1_3():
    fig, ax = schematic(6.8, 4.9, xlim=(0, 20), ylim=(0, 14))
    bx, by, bw, bh = 7.2, 3.0, 4.9, 8.0
    ax.add_patch(FancyBboxPatch((bx, by), bw, bh, boxstyle="round,pad=0.05,rounding_size=0.3",
                                fc="#EEF3F8", ec=INK, lw=2.2, ls=(0, (6, 3))))
    cx = bx + bw / 2
    ax.text(cx, 7.9, "CCM-1", ha="center", va="center", fontsize=14, weight="bold")
    ax.text(cx, 6.6, "device + probe\n+ cloud service", ha="center", va="center", fontsize=9)
    ax.text(cx, 4.1, "IF2–IF4 (battery, display,\nflash) are internal", ha="center",
            va="center", fontsize=6.8, color="#555555", style="italic")
    ax.text(cx, 10.5, "system boundary", ha="center", fontsize=7.5, style="italic",
            color="#555555")
    E = [(0.2, 9.0, 3.4, 1.8, "Clinic nurse"),
         (0.2, 5.6, 3.4, 1.8, "Refrigerator"),
         (0.2, 2.9, 3.4, 1.5, "Ambient\nenvironment"),
         (7.85, 0.1, 3.6, 1.5, "Installer /\ntechnician"),
         (16.0, 9.0, 3.9, 1.6, "District officer\nphone"),
         (16.0, 5.8, 3.9, 1.8, "Cellular network\nLTE-M / NB-IoT"),
         (16.0, 2.6, 3.9, 1.8, "National health-\ndata platform")]
    for x, y, w, h, t in E:
        box(ax, x, y, w, h, t, fc="white", fontsize=8.5)
    for x, y, t in [(4.6, 12.4, "refrigerator power supply"), (10.4, 12.4, "SMS gateway (operator)"),
                    (0.2, 0.3, "vaccine stock\nmanagement")]:
        w = 3.4 if "\n" in t else 5.0
        box(ax, x, y, w, 1.1 if "\n" in t else 0.8, t, fc=LIGHT, ec=GREY, fontsize=7.3)
    ax.text(10.0, 13.5, "excluded (outside the boundary, someone else's)", ha="center",
            fontsize=7.5, color=GREY, style="italic")

    def lab(x, y, t, c=INK, ha="center", va="center"):
        ax.text(x, y, t, fontsize=7.2, color=c, ha=ha, va=va, linespacing=1.15)
    L, R = 3.6, 16.0
    xl, xr = (L + bx) / 2, (bx + bw + R) / 2
    # nurse
    harrow(ax, bx, 10.4, L, 10.4)
    lab(xl, 10.55, "IF7 display,\nbuzzer, LED", va="bottom")
    harrow(ax, L, 9.4, bx, 9.4)
    lab(xl, 9.25, "IF7 acknowledge\nbutton", va="top")
    # refrigerator
    harrow(ax, L, 7.0, bx, 7.0)
    lab(xl, 7.15, "IF1 heat via\nprobe vial", va="bottom")
    harrow(ax, L, 6.0, bx, 6.0, color="#555555", both=True)
    lab(xl, 5.85, "mounting surface,\ndoor seal (cable)", c="#555555", va="top")
    # ambient
    harrow(ax, L, 3.65, bx, 3.65)
    lab(xl, 3.5, "0–43 °C,\nhumidity", va="top")
    # technician
    harrow(ax, 8.7, 1.6, 8.7, by)
    lab(8.55, 2.3, "install,\nconfigure (app)", ha="right")
    harrow(ax, 10.6, by, 10.6, 1.6)
    lab(10.75, 2.3, "diagnostic\nlog", ha="left")
    # officer
    harrow(ax, bx + bw, 9.8, R, 9.8)
    lab(xr, 9.95, "IF8 SMS and app\nnotifications", va="bottom")
    # cellular
    harrow(ax, bx + bw, 6.7, R, 6.7, both=True)
    lab(xr, 6.85, "IF5 / IF6 alarm and\nreport messages;\nconfig, firmware,\nnetwork time",
        va="bottom")
    # national platform
    harrow(ax, bx + bw, 3.5, R, 3.5)
    lab(xr, 3.65, "daily summaries\nvia API", va="bottom")
    lab(17.95, 2.4, "outside boundary,\nowned by Ministry IT", c="#555555", va="top")
    save(fig, "01", "fig-1-3-ccm1-context-diagram")


# ----------------------------------------------------------------------------
# Figure 1.4 — error budget
# ----------------------------------------------------------------------------
def fig_1_4():
    items = [("sensor element (SP1)", 0.10), ("calibration reference", 0.10),
             ("drift, 3 years (SP1)", 0.10), ("cable conduction (SP10)", 0.05),
             ("vial gradient (SP2)", 0.05), ("display rounding (SP9)", 0.05),
             ("quantisation (SP1)", 0.008)]
    lims = np.array([v for _, v in items])
    wc = lims.sum()
    rss = np.sqrt(np.sum(lims ** 2))
    U = 2 * rss / np.sqrt(3)
    fig, ax = new_fig(6.4, 4.0)
    y = np.arange(len(items))[::-1] + 3.6
    ax.barh(y, lims, color=BLUE, alpha=0.75, height=0.62)
    for yi, (n, v) in zip(y, items):
        ax.text(v + 0.006, yi, f"{v:.3f}" if v < 0.01 else f"{v:.2f}", va="center", fontsize=8)
    sy = [2.2, 1.2, 0.2]
    vals = [wc, rss, U]
    cols = ["#2E4A6B", "#9EC1E2", "#C9B6E4"]
    for yi, v, c in zip(sy, vals, cols):
        ax.barh(yi, v, color=c, height=0.62, ec=INK, lw=0.5)
    ax.text(wc - 0.006, sy[0], f"{wc:.3f}", va="center", ha="right", fontsize=8, color="white")
    ax.text(rss + 0.006, sy[1], f"{rss:.3f}", va="center", fontsize=8)
    ax.text(U + 0.006, sy[2], f"{U:.2f}", va="center", fontsize=8)
    ax.set_yticks(list(y) + sy)
    ax.set_yticklabels([n for n, _ in items] + ["worst-case sum", "RSS of limits",
                                                "expanded U (k = 2)"], fontsize=8.5)
    ax.axvline(0.5, color=RED, ls="--", lw=1.3)
    ax.text(0.495, y[0] + 0.55, "requirement R1: ±0.5 °C", color=RED, fontsize=8, ha="right",
            va="bottom")
    harrow(ax, wc, sy[0] + 0.48, 0.5, sy[0] + 0.48, both=True, color=INK, lw=0.8, ms=6)
    ax.text(0.505, sy[0] + 0.48, f"margin\n{0.5 - wc:.3f}", ha="left", va="center", fontsize=7.5)
    harrow(ax, rss + 0.045, sy[1], 0.5, sy[1], both=True, color=INK, lw=0.8, ms=6)
    ax.text((rss + 0.545) / 2, sy[1], f"margin {0.5 - rss:.2f}", ha="center", va="center",
            fontsize=7.5, bbox=dict(fc="white", ec="none", pad=0.5))
    ax.set_xlim(0, 0.55)
    ax.set_ylim(-0.5, y[0] + 1.5)
    ax.set_xlabel("Allocated error limit (±°C)")
    save(fig, "01", "fig-1-4-error-budget")


# ----------------------------------------------------------------------------
# Figure 1.5 — traceability graph
# ----------------------------------------------------------------------------
def fig_1_5():
    needs = [f"SN{i}" for i in range(1, 9)]
    reqs = [f"R{i}" for i in range(1, 13)]
    specs = [f"SP{i}" for i in range(1, 11)]
    tests = [f"AT{i}" for i in range(1, 10)]
    req_from = {"R1": ["SN1"], "R2": ["SN1"], "R3": ["SN1", "SN2"], "R4": ["SN2"],
                "R5": ["SN3"], "R6": ["SN4"], "R7": ["SN5"], "R8": ["SN4"],
                "R9": ["SN5"], "R10": ["SN6"], "R11": ["SN7"], "R12": ["SN3"]}
    spec_of = {"SP1": "R1", "SP2": "R1", "SP3": "R2", "SP4": "R3", "SP5": "R4",
               "SP6": "R5", "SP7": "R6", "SP8": "R7", "SP9": "R8", "SP10": "R10"}
    tests_of = {"AT1": ["R1"], "AT2": ["R2", "R3"], "AT3": ["R4"], "AT4": ["R5"],
                "AT5": ["R6"], "AT6": ["R7"], "AT7": ["R8", "R10"], "AT8": ["R11"],
                "AT9": ["R12"]}
    fig, ax = schematic(6.8, 5.2, xlim=(0, 17), ylim=(-1.7, 12.8))
    X = {"N": 1.4, "R": 6.0, "S": 10.6, "T": 15.3}
    nw, nh = 1.5, 0.62

    def col(names, x, top=11.2, bottom=0.6):
        ys = np.linspace(top, bottom, len(names))
        return {n: (x, y) for n, y in zip(names, ys)}
    P = {}
    P.update(col(needs, X["N"]))
    P.update(col(reqs, X["R"]))
    P.update(col(specs, X["S"]))
    P.update(col(tests, X["T"]))
    for title, x, c in [("Needs", X["N"], INK), ("Requirements", X["R"], INK),
                        ("Specifications", X["S"], INK), ("Acceptance tests", X["T"], INK)]:
        ax.text(x, 12.3, title, ha="center", fontsize=9.5, weight="bold", color=c)
    # edges
    for r, ns in req_from.items():
        for n in ns:
            ax.plot([P[n][0] + nw / 2, P[r][0] - nw / 2], [P[n][1], P[r][1]], color=BLUE, lw=0.9,
                    zorder=1)
    for s, r in spec_of.items():
        ax.plot([P[r][0] + nw / 2, P[s][0] - nw / 2], [P[r][1], P[s][1]], color=GREEN, lw=0.9,
                zorder=1)
    for t, rs in tests_of.items():
        for r in rs:
            ax.add_patch(FancyArrowPatch((P[t][0] - nw / 2, P[t][1]), (P[r][0] + nw / 2, P[r][1]),
                                         arrowstyle="-", color=ORANGE, lw=0.8, alpha=0.75,
                                         connectionstyle="arc3,rad=-0.12", zorder=0.5))
    gaps = {"SN8": "no requirement", "R9": "no test, no spec"}
    direct = {"R11", "R12"}
    for n, (x, y) in P.items():
        ec, lw, fc = INK, 0.8, "white"
        if n in gaps:
            ec, lw, fc = RED, 1.8, "#FBE3E3"
        ax.add_patch(FancyBboxPatch((x - nw / 2, y - nh / 2), nw, nh,
                                    boxstyle="round,pad=0.02,rounding_size=0.15",
                                    fc=fc, ec=ec, lw=lw, zorder=3))
        ax.text(x, y, n, ha="center", va="center", fontsize=8, zorder=4)
    ax.text(P["SN8"][0], P["SN8"][1] - 0.55, "no requirement", ha="center", va="top",
            color=RED, fontsize=7.5)
    ax.text(P["R9"][0] + nw / 2 + 0.12, P["R9"][1] + 0.05, "no test", ha="left", va="bottom",
            color=RED, fontsize=7.5, zorder=5, bbox=dict(fc="white", ec="none", pad=0.3))
    for r in direct:
        x, y = P[r]
        ax.add_patch(FancyBboxPatch((x - nw / 2 - 0.12, y - nh / 2 - 0.12), nw + 0.24, nh + 0.24,
                                    boxstyle="round,pad=0.02,rounding_size=0.2", fc="none",
                                    ec=GREY, lw=1.0, ls="--", zorder=3))
    # legend
    for x0, yl, c, t in [(0.2, -0.75, BLUE, "need → requirement"),
                         (7.4, -0.75, GREEN, "requirement → specification"),
                         (0.2, -1.35, ORANGE, "test verifies requirement")]:
        ax.plot([x0, x0 + 0.8], [yl, yl], color=c, lw=1.5)
        ax.text(x0 + 1.0, yl, t, va="center", fontsize=7.8)
    ax.add_patch(FancyBboxPatch((7.4, -1.54), 0.8, 0.38, boxstyle="round,pad=0.02,rounding_size=0.1",
                                fc="none", ec=GREY, lw=1.0, ls="--"))
    ax.text(8.4, -1.35, "R11, R12: verified directly (no spec needed)", va="center",
            fontsize=7.8, color="#555555")
    save(fig, "01", "fig-1-5-traceability-graph")


# ----------------------------------------------------------------------------
# Figure 1.6 — pilot exposure
# ----------------------------------------------------------------------------
def fig_1_6():
    lam = np.logspace(np.log10(0.05), np.log10(0.5), 200)
    fig, ax = new_fig(6.4, 3.9)
    for k, c in zip(range(4), [BLUE, ORANGE, GREEN, PINK]):
        q = chi2.ppf(0.90, 2 * k + 2)
        ax.loglog(lam, q / (2 * lam), color=c, lw=1.8)
        ax.plot([0.1], [q / 0.2], "o", ms=3.5, color=c)
    ax.axhline(60, color=INK, ls="--", lw=1.0)
    ax.text(0.49, 64, "planned pilot: 20 fridges × 3 months = 60 fridge-months", ha="right",
            va="bottom", fontsize=8)
    ax.axvline(0.1, color=RED, ls="--", lw=1.0)
    ax.text(0.098, 1.25, "R6: λ ≤ 0.1", color=RED, rotation=90, ha="right", va="bottom",
            fontsize=8)
    q2 = chi2.ppf(0.90, 6)
    lam_x = q2 / (2 * 60)
    ax.plot([lam_x], [60], "D", ms=7, mfc="none", mec=INK, mew=1.3)
    ax.annotate(f"k = 2 meets the pilot\nat λ = {lam_x:.3f}", (lam_x, 60), (0.125, 105),
                fontsize=8, arrowprops=dict(arrowstyle="-", lw=0.7))
    ax.set_xlim(0.05, 0.5)
    ax.set_ylim(1, 200)
    ax.set_xticks([0.05, 0.1, 0.2, 0.5])
    ax.set_xticklabels(["0.05", "0.1", "0.2", "0.5"])
    ax.set_yticks([1, 2, 5, 10, 20, 50, 100, 200])
    ax.set_yticklabels(["1", "2", "5", "10", "20", "50", "100", "200"])
    ax.minorticks_off()
    ax.grid(True, which="major", lw=0.5)
    ax.set_xlabel("Demonstrated false-alarm rate limit λ (per refrigerator-month)")
    ax.set_ylabel("Required exposure T\n(refrigerator-months)")
    ax.set_title("T = χ²₀.₉₀(2k+2) / (2λ), k = false alarms observed", fontsize=9.5)
    fig.canvas.draw()
    p0, p1 = ax.transData.transform([(0.06, 10.0), (0.3, 2.0)])
    ang = np.degrees(np.arctan2(p1[1] - p0[1], p1[0] - p0[0]))
    for k, c in zip(range(4), [BLUE, ORANGE, GREEN, PINK]):
        q = chi2.ppf(0.90, 2 * k + 2)
        x0 = 0.19
        up = k == 3
        ax.text(x0, q / (2 * x0) * (1.05 if up else 0.95), f"k = {k}:  T = {q / 0.2:.1f} at λ = 0.1",
                color=c, fontsize=7.4, va="bottom" if up else "top", ha="left", rotation=ang,
                rotation_mode="anchor")
    save(fig, "01", "fig-1-6-pilot-exposure")


if __name__ == "__main__":
    fig_1_1()
    fig_1_2()
    fig_1_3()
    fig_1_4()
    fig_1_5()
    fig_1_6()
