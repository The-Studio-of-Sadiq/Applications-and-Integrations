"""Figures for Chapter 17 — Robotic System Integration.

Run from the repository root:  python figures/scripts/ch17.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle  # noqa: E402
from scipy.optimize import least_squares  # noqa: E402

from figstyle import COLORS, INK, box, save, schematic  # noqa: E402

BLUE, ORANGE, GREEN, PINK, YELLOW, SKY = COLORS[:6]
RED = "#C62828"
GREY = "#777777"
POWER = "#C62828"
DATA = "#0072B2"
SAFE = "#D4A000"


def tint(c, a="30"):
    return c + a


def line(ax, pts, color=INK, lw=1.1, ls="-", arrow_end=False, both=False, ms=10):
    """Poly-line through pts with optional arrow head(s) on the last segment."""
    xs, ys = zip(*pts)
    if not arrow_end and not both:
        ax.plot(xs, ys, color=color, lw=lw, ls=ls, solid_capstyle="butt")
        return
    if len(pts) > 2:
        ax.plot(xs[:-1], ys[:-1], color=color, lw=lw, ls=ls)
    ax.annotate("", xy=pts[-1], xytext=pts[-2],
                arrowprops=dict(arrowstyle="<|-|>" if both else "-|>", color=color, lw=lw,
                                ls=ls, shrinkA=0, shrinkB=0, mutation_scale=ms))


def rbox(ax, x, y, w, h, fc="#EEF3F8", ec=INK, lw=1.0, ls="-"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc=fc, ec=ec, lw=lw, ls=ls))


def tbox(ax, x, y, w, h, title, body="", fc="#EEF3F8", ec=INK, fs=8.0, bfs=7.2, lw=1.0):
    """Box with a bold title and an optional smaller body text below it."""
    rbox(ax, x, y, w, h, fc=fc, ec=ec, lw=lw)
    if body:
        ax.text(x + w / 2, y + h - 0.12, title, ha="center", va="top", fontsize=fs, weight="bold")
        ax.text(x + w / 2, y + (h - 0.45) / 2, body, ha="center", va="center", fontsize=bfs,
                linespacing=1.25)
    else:
        ax.text(x + w / 2, y + h / 2, title, ha="center", va="center", fontsize=fs, weight="bold")


# ----------------------------------------------------------------------------
# Figure 17.1 — architecture of the arm
# ----------------------------------------------------------------------------
def fig_17_1():
    fig, ax = schematic(6.8, 5.7, xlim=(0, 17), ylim=(-0.7, 13.5))
    pfc = tint(POWER, "18")
    # --- power chain -------------------------------------------------------
    y0, h = 11.2, 1.7
    blocks = [(1.7, "230 V AC", "mains"), (2.0, "EMI filter", "line filter"),
              (2.6, "48 V PSU", "750 W cont.\n1125 W for 3 s"),
              (2.3, "Precharge", "10 Ω resistor,\nbypassed\nafter 0.2 s"),
              (3.3, "48 V bus (base)", "1 mF + 6 × 470 µF\n= 3.82 mF\nbus monitor"),
              (3.0, "Brake chopper", "6.8 Ω resistor\non at 56 V,\noff at 54 V")]
    x = 0.1
    xr = []
    for w, t, b in blocks:
        fc = "#F2F2F2" if t == "230 V AC" else pfc
        tbox(ax, x, y0, w, h, t, b, fc=fc, fs=7.6, bfs=6.6)
        xr.append((x, x + w))
        x += w + 0.35
    for k in range(5):
        line(ax, [(xr[k][1], y0 + h / 2), (xr[k + 1][0], y0 + h / 2)], color=POWER, lw=1.6,
             arrow_end=True)
    xbus = xr[4][0] + 0.6

    # --- controllers -------------------------------------------------------
    yc, hc = 7.5, 2.5
    tbox(ax, 0.65, yc + 0.5, 2.15, 1.5, "DC-DC", "48 V → 24 V\n90 %", fc=pfc, fs=7.8, bfs=6.8)
    tbox(ax, 3.35, yc, 4.8, hc, "Main controller",
         "Linux PREEMPT_RT, 1 kHz\ntrajectory · inverse kinematics\ngravity + inertia feed-forward",
         fc=tint(DATA, "18"), bfs=7.0)
    tbox(ax, 8.65, yc + 0.5, 2.2, 1.5, "Pendant", "jog, program,\nenabling dev.", fc=tint(DATA, "18"),
         fs=7.8, bfs=6.6)
    tbox(ax, 11.35, yc, 5.55, hc, "Safety controller",
         "dual channel\nE-stop · enabling device\nforces STO if not stopped in 0.5 s",
         fc=tint(SAFE, "30"), bfs=7.0)
    # 48 V bus to DC-DC and down the left edge to the joints
    line(ax, [(xbus, y0), (xbus, 10.55), (0.3, 10.55)], color=POWER, lw=1.6)
    line(ax, [(1.7, 10.55), (1.7, yc + 2.0)], color=POWER, lw=1.6, arrow_end=True)
    ax.text(6.0, 10.62, "48 V", fontsize=7.4, color=POWER, ha="center", va="bottom")
    # 24 V to main controller and pendant
    line(ax, [(2.8, yc + 1.25), (3.35, yc + 1.25)], color=POWER, lw=1.3, arrow_end=True)

    line(ax, [(1.7, yc + 0.5), (1.7, yc - 0.3), (9.75, yc - 0.3), (9.75, yc + 0.5)], color=POWER,
         lw=1.1, arrow_end=True)
    ax.text(9.0, yc - 0.23, "24 V", fontsize=6.6, color=POWER, ha="center", va="bottom")
    line(ax, [(8.65, yc + 1.25), (8.15, yc + 1.25)], color=DATA, lw=1.2, both=True)
    line(ax, [(10.85, yc + 1.25), (11.35, yc + 1.25)], color=SAFE, lw=1.4, arrow_end=True)
    # E-stop symbol at safety controller
    ax.add_patch(plt.Circle((16.3, 10.45), 0.3, fc=RED, ec=INK, lw=0.8))
    ax.add_patch(plt.Circle((16.3, 10.45), 0.12, fc="#F6D000", ec=INK, lw=0.6))
    ax.text(15.85, 10.45, "E-stop", fontsize=7, ha="right", va="center")
    line(ax, [(16.3, 10.15), (16.3, yc + hc)], color=SAFE, lw=1.4, arrow_end=True)

    # --- harness through the arm -------------------------------------------
    yj, hj, wj = 3.55, 1.75, 2.15
    xs = [0.75 + i * 2.75 for i in range(6)]
    gears = ["100:1"] * 3 + ["50:1"] * 3
    for i, (x, g) in enumerate(zip(xs, gears)):
        tbox(ax, x, yj, wj, hj, f"J{i + 1}", f"joint module\ngear {g}", fc="#F5F5F5", fs=8.5,
             bfs=6.8)
    lanes = [(yj + 1.42, POWER), (yj + 1.02, DATA), (yj + 0.62, SAFE), (yj + 0.25, GREY)]
    for yy, c in lanes:
        for i in range(5):
            line(ax, [(xs[i] + wj, yy), (xs[i + 1], yy)], color=c, lw=1.6 if c != GREY else 1.0)
    # 48 V into J1
    line(ax, [(0.3, 10.55), (0.3, yj + 1.42), (xs[0], yj + 1.42)], color=POWER, lw=1.6,
         arrow_end=True)
    # CAN FD from main controller
    line(ax, [(4.4, yc), (4.4, 6.05), (0.45, 6.05), (0.45, yj + 1.02), (xs[0], yj + 1.02)],
         color=DATA, lw=1.6, arrow_end=True)
    ax.text(4.55, 6.75, "CAN FD 1 Mbit/s nominal, 8 Mbit/s data\nsetpoints ↓ 1 kHz, status ↑ 1 kHz",
            fontsize=6.8, color=DATA, ha="left", va="center")
    ax.text(4.25, yc - 0.38, "120 Ω\n(base)", fontsize=6.0, color=DATA, ha="right", va="top")
    # STO from safety controller
    line(ax, [(13.2, yc), (13.2, 5.8), (0.6, 5.8), (0.6, yj + 0.62), (xs[0], yj + 0.62)],
         color=SAFE, lw=1.6, arrow_end=True)
    ax.text(13.35, 6.6, "STO ch1 + ch2\n(hardwired)", fontsize=6.8, color="#8A6A00",
            ha="left", va="center")
    # wrist termination
    xt = xs[5] + wj
    ax.add_patch(Rectangle((xt, yj + 0.87), 0.3, 0.3, fc="white", ec=DATA, lw=1.0))
    ax.text(xt + 0.15, yj + 1.3, "120 Ω\n(wrist)", fontsize=6.0, color=DATA, ha="center",
            va="bottom")
    # lane key below the chain
    ky = yj - 0.45
    kx = 0.75
    items = [(POWER, "48 V / 0 V, 1.0 mm²"), (DATA, "CAN FD pair"), (SAFE, "STO ×2"),
             (GREY, "CAN ground")]
    for kx, (c, lab) in zip((0.75, 4.55, 7.3, 9.55), items):
        line(ax, [(kx, ky), (kx + 0.55, ky)], color=c, lw=1.8)
        ax.text(kx + 0.65, ky, lab, fontsize=6.8, va="center")
    ax.text(16.9, ky, "(1.6 m daisy chain through\nthe hollow shafts)", fontsize=6.6, ha="right",
            va="center", style="italic", linespacing=1.0)

    # --- inside one joint ----------------------------------------------------
    yd = -0.6
    rbox(ax, 0.1, yd, 16.8, 3.0, fc="white", ec=GREY, ls=(0, (4, 2)))
    ax.text(0.3, yd + 2.82, "Inside each joint module", fontsize=7.8, weight="bold", va="top")
    bx = [(0.3, "STM32G474", "M4, 170 MHz\nFOC at 20 kHz"),
          (3.0, "Gate driver +\nMOSFET bridge", "470 µF bus cap.\n3 × 2 mΩ shunts"),
          (5.7, "Frameless\nBLDC", "spring brake\nNTC in winding"),
          (8.4, "Strain-wave\ngear", "100:1 J1–J3\n50:1 J4–J6"),
          (11.1, "Output\nflange", "to next link")]
    wb, hb, yb = 2.35, 2.0, yd + 0.42
    for x, t, b in bx:
        rbox(ax, x, yb, wb, hb, fc="#F5F5F5")
        ax.text(x + wb / 2, yb + hb - 0.1, t, ha="center", va="top", fontsize=7.0, weight="bold",
                linespacing=1.05)
        ax.text(x + wb / 2, yb + 0.42, b, ha="center", va="center", fontsize=6.2, linespacing=1.15)
    for i in range(4):
        line(ax, [(bx[i][0] + wb, yb + hb / 2), (bx[i + 1][0], yb + hb / 2)], color=INK, lw=1.1,
             arrow_end=True)
    xe = 13.6
    rbox(ax, xe, yb, 3.15, hb, fc=tint(DATA, "18"))
    ax.text(xe + 1.575, yb + hb / 2, "14-bit motor encoder\n(commutation, speed)\n"
            "19-bit output encoder\n(BiSS-C, link angle)\nΔ angle → gear torque",
            fontsize=5.8, ha="center", va="center", linespacing=1.15, color=INK)
    line(ax, [(xe + 1.5, yb), (xe + 1.5, yd + 0.17), (1.4, yd + 0.17), (1.4, yb)], color=DATA,
         lw=0.9, ls=(0, (3, 2)), arrow_end=True, ms=8)


    # legend
    lx, ly = 3.9, 13.25
    for i, (c, lab) in enumerate(((POWER, "power"), (DATA, "data"), (SAFE, "safety"))):
        line(ax, [(lx + i * 2.6, ly), (lx + i * 2.6 + 0.7, ly)], color=c, lw=2.0)
        ax.text(lx + i * 2.6 + 0.85, ly, lab, fontsize=7.6, va="center")
    save(fig, "17", "fig-17-1-arm-architecture")


# ----------------------------------------------------------------------------
# Figure 17.2 — joint state machine
# ----------------------------------------------------------------------------
def fig_17_2():
    fig, ax = schematic(6.8, 4.9, xlim=(0, 17), ylim=(0, 12.2))
    W, H = 2.6, 1.75
    yt, yb = 8.6, 3.5
    st = {
        "INIT": (0.2, yt, "self-test,\nparameter CRC", "#F2F2F2"),
        "STANDBY": (4.6, yt, "brake on,\nbridge off", tint(SKY, "40")),
        "PRECHECK": (9.0, yt, "bridge on,\nholding torque\nbuilt", tint(GREEN, "30")),
        "OPERATIONAL": (14.2, yt, "1 kHz setpoints", tint(GREEN, "55")),
        "STOPPING": (14.2, yb, "velocity ramp on\nlocal sensors,\n≤ 400 ms", tint(YELLOW, "45")),
        "FAULT": (4.6, yb, "brake on,\nbridge off,\nlatched", "#F4C7C7"),
    }
    for n, (x, y, body, fc) in st.items():
        rbox(ax, x, y, W, H, fc=fc, lw=1.3)
        ax.text(x + W / 2, y + H - 0.3, n, ha="center", va="center", fontsize=7.3, weight="bold")
        ax.text(x + W / 2, y + (H - 0.55) / 2, body, ha="center", va="center", fontsize=6.6,
                linespacing=1.1)

    def mid(n, side, f=0.5):
        x, y, *_ = st[n]
        return {"l": (x, y + H * f), "r": (x + W, y + H * f), "t": (x + W * f, y + H),
                "b": (x + W * f, y)}[side]

    fs = 6.8
    # initial pseudo-state
    xi = 0.2 + W / 2
    ax.plot([xi], [11.7], "o", color=INK, ms=6)
    line(ax, [(xi, 11.65), mid("INIT", "t")], arrow_end=True, lw=1.2)
    ax.text(xi + 0.2, 10.95, "power-up", fontsize=fs, va="center")
    # top-row transitions, labels above the arrows
    for a, b, lab in (("INIT", "STANDBY", "self-test\npass"), ("STANDBY", "PRECHECK", "enable,\nno faults"),
                      ("PRECHECK", "OPERATIONAL", "torque ready /\nrelease brake")):
        p0, p1 = mid(a, "r"), mid(b, "l")
        line(ax, [p0, p1], arrow_end=True, lw=1.2)
        ax.text((p0[0] + p1[0]) / 2, p0[1] + 0.15, lab, fontsize=fs, ha="center", va="bottom",
                linespacing=1.05)
    # OPERATIONAL -> STOPPING
    p0, p1 = mid("OPERATIONAL", "b", 0.85), mid("STOPPING", "t", 0.85)
    line(ax, [p0, p1], arrow_end=True, lw=1.2)
    ax.text(p0[0] - 0.15, 7.35, "fault: comm loss\n(3 missed = 3 ms),\novertemperature,\n"
            "overvoltage;\nor enable withdrawn", fontsize=fs, ha="right", va="center", linespacing=1.1)
    # STOPPING -> STANDBY (diagonal)
    p0, p1 = (14.2, yb + H - 0.15), mid("STANDBY", "b", 0.75)
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=10, lw=1.2, color=INK,
                                 shrinkA=0, shrinkB=0))
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    ang = np.degrees(np.arctan2(dy, dx)) + 180
    nrm = np.array([dy, -dx]) / np.hypot(dx, dy)          # normal pointing below the line
    if nrm[1] > 0:
        nrm = -nrm
    ax.text(9.65, 6.0, "zero velocity, no fault /\nbrake on, bridge off", fontsize=fs,
            ha="center", va="center", linespacing=1.05)
    # STOPPING -> FAULT (fault latched) and immediate (red dashed)
    ya = yb + 1.15
    line(ax, [(14.2, ya), (4.6 + W, ya)], arrow_end=True, lw=1.2)
    ax.text(10.7, ya + 0.1, "fault latched: at zero\nvelocity or after 400 ms", fontsize=fs,
            ha="center", va="bottom", linespacing=1.05)
    yr = yb + 0.45
    line(ax, [(14.2, yr), (4.6 + W, yr)], arrow_end=True, lw=1.4, color=RED, ls=(0, (4, 2)))
    ax.text(10.7, yr - 0.12, "at once: overcurrent or\nencoder mismatch (torque off, brake on)",
            fontsize=fs, ha="center", va="top", color=RED, linespacing=1.1)
    # PRECHECK -> FAULT
    p0, p1 = mid("PRECHECK", "b", 0.2), mid("FAULT", "t", 0.8)
    line(ax, [p0, p1], arrow_end=True, lw=1.1, color=RED)
    ax.text(p0[0] - 0.45, p0[1] - 0.35, "fault", fontsize=fs, color=RED, ha="right", va="center")
    # INIT -> FAULT
    line(ax, [mid("INIT", "b", 0.4), (0.2 + W * 0.4, yb + H * 0.5), mid("FAULT", "l")],
         arrow_end=True, lw=1.1, color=RED)
    ax.text(0.2 + W * 0.4 - 0.12, 6.3, "self-test or\nCRC fail", fontsize=fs, color=RED, ha="right",
            va="center")
    # FAULT -> INIT (reset)
    line(ax, [mid("FAULT", "t", 0.25), (4.6 + W * 0.25, 7.3), (0.2 + W * 0.8, 7.3),
              mid("INIT", "b", 0.8)], arrow_end=True, lw=1.1, color=GREY, ls=(0, (3, 2)))
    ax.text(4.6 + W * 0.25 + 0.12, 6.35, "reset\nonly", fontsize=fs, color=GREY, ha="left",
            va="center")
    # STO path
    rbox(ax, 0.2, 0.15, 16.55, 1.95, fc=tint(SAFE, "22"), ec=SAFE, lw=1.2)
    ax.text(0.45, 1.05, "Safety\ncontroller", fontsize=8, weight="bold", va="center")
    line(ax, [(2.6, 0.8), (11.1, 0.8)], color=SAFE, lw=1.8, arrow_end=True)
    ax.text(6.8, 0.92, "STO ch1, ch2 (hardwired, dual channel)", fontsize=7.0, ha="center",
            va="bottom", color="#6A5200")
    rbox(ax, 11.2, 0.4, 5.3, 0.95, fc="white", ec=SAFE)
    ax.text(13.85, 0.88, "gate-driver enable:\nbridge cannot switch", fontsize=6.8, ha="center",
            va="center")
    ax.text(8.5, 1.85, "bypasses the firmware: no state or fault of this state machine can defeat it",
            fontsize=6.6, ha="center", va="center", style="italic", color="#6A5200")
    save(fig, "17", "fig-17-2-joint-state-machine")


# ----------------------------------------------------------------------------
# Figure 17.3 — bus voltage during a controlled stop
# ----------------------------------------------------------------------------
def bus_sim():
    E0, td, eta = 52.0, 0.25, 0.68
    C, V0, P_load = 3.82e-3, 48.0, 50.0
    V_ov, V_on, V_off, Rb = 60.0, 56.0, 54.0, 6.8
    dt = 1e-5
    t = np.arange(0, 0.35, dt)
    P_mech = np.where(t < td, 2 * E0 / td * (1 - t / td), 0.0)

    def run(chopper):
        V, on = V0, False
        Vt = np.empty(t.size)
        Pr = np.zeros(t.size)
        Eb, trip = 0.0, None
        for k, tk in enumerate(t):
            P_in = eta * P_mech[k] - P_load
            if chopper:
                on = V > V_on or (on and V > V_off)
            P_r = V * V / Rb if on else 0.0
            V = np.sqrt(max(V * V + 2 * (P_in - P_r) * dt / C, 0.0))
            V = max(V, V0)
            Eb += P_r * dt
            Vt[k] = V
            Pr[k] = P_r
            if trip is None and V >= V_ov:
                trip = tk
        return Vt, Pr, Eb, trip

    Vn, _, _, trip = run(False)
    Vc, Pr, Eb, _ = run(True)
    return t, P_mech, Vn, trip, Vc, Pr, Eb


def fig_17_3():
    t, P_mech, Vn, trip, Vc, Pr, Eb = bus_sim()
    ms = t * 1e3
    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    ax2 = ax.twinx()
    ax2.spines["right"].set_visible(True)
    # power on right axis (behind)
    # resistor power averaged over each chopper cycle (on-edge to on-edge)
    on = Pr > 0
    starts = np.where(on[1:] & ~on[:-1])[0] + 1
    ends = np.append(starts[1:], 2 * starts[-1] - starts[-2])  # last cycle as long as the one before
    Pr_avg = np.zeros_like(Pr)
    for a, b in zip(starts, ends):
        Pr_avg[a:b] = Pr[a:b].mean()
    ax2.fill_between(ms, 0, Pr_avg, color=GREEN, alpha=0.30, lw=0, step="post",
                     label=f"resistor power (mean per chopper cycle), {Eb:.1f} J per stop")
    ax2.plot(ms, P_mech, color=GREY, lw=1.4, label="mechanical power returned")
    ax2.set_ylim(0, 450)
    ax2.set_ylabel("power (W)", color=GREY)
    ax2.tick_params(axis="y", colors=GREY)
    ax2.spines["right"].set_color(GREY)
    # voltages
    ax.set_zorder(ax2.get_zorder() + 1)
    ax.patch.set_visible(False)
    k = int(np.searchsorted(t, trip))
    ax.plot(ms[:k + 1], Vn[:k + 1], color=RED, lw=1.8, label="no chopper")
    kk = np.searchsorted(Vn, 70.0)
    ax.plot(ms[k:kk], Vn[k:kk], color=RED, lw=1.2, ls=(0, (4, 2)))
    ax.plot(ms, Vc, color=BLUE, lw=1.1, label="with chopper (on 56 V, off 54 V)")
    ax.plot([trip * 1e3], [60], "o", color=RED, ms=6, zorder=5)
    ax.annotate(f"overvoltage trip at {trip*1e3:.1f} ms,\ntorque off", xy=(trip * 1e3, 60),
                xytext=(24, 62.7), fontsize=8, color=RED, va="center",
                arrowprops=dict(arrowstyle="-", color=RED, lw=0.8))
    for v, lab, c in ((60, "60 V overvoltage trip", RED), (58, "58 V limit (R6)", INK),
                      (56, "56 V chopper on", BLUE)):
        ax.axhline(v, color=c, lw=0.8, ls=(0, (5, 3)), alpha=0.8)
        ax.text(348, v + 0.25, lab, fontsize=7.4, color=c, ha="right", va="bottom")
    ax.text(95, 52.6, "chopper cycles 54–56 V", fontsize=7.6, color=BLUE, ha="center")
    ax.text(262, 49.2, "returned power below\nchopper threshold;\nbus load brings it\nback to 48 V",
            fontsize=7.0, color=BLUE, ha="left", va="bottom")
    ax.set_xlim(0, 350)
    ax.set_ylim(44, 70)
    ax.set_xlabel("time after stop command (ms)")
    ax.set_ylabel("DC-bus voltage (V)")
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper right", fontsize=7.4, bbox_to_anchor=(1.0, 1.02))
    save(fig, "17", "fig-17-3-bus-voltage-stop")


# ----------------------------------------------------------------------------
# Figure 17.4 — calibration errors
# ----------------------------------------------------------------------------
def calibration():
    rng = np.random.default_rng(17)
    nom = np.array([0.350, 0.300, 0.100, 0, 0, 0, 0, 0])
    true = nom + np.array([0.8e-3, -0.6e-3, 0.4e-3, np.radians(0.60), np.radians(-0.90),
                           np.radians(0.50), 1.5e-3, -2.0e-3])

    def fk(p, q):
        a, dq, base = p[:3], p[3:6], p[6:8]
        th = np.cumsum(q + dq, axis=1)
        x = base[0] + (a * np.cos(th)).sum(axis=1)
        z = base[1] + (a * np.sin(th)).sum(axis=1)
        return np.column_stack([x, z])

    def poses(n):
        return np.column_stack([rng.uniform(-0.3, 1.3, n), rng.uniform(-2.2, -0.3, n),
                                rng.uniform(-1.5, 1.5, n)])
    q_id, q_val = poses(40), poses(40)

    def meas(q):
        return fk(true, q) + 30e-6 * rng.standard_normal((len(q), 2))
    m_id, m_val = meas(q_id), meas(q_val)
    res = least_squares(lambda p: (fk(p, q_id) - m_id).ravel(), nom)
    e_nom = 1e3 * (fk(nom, q_val) - m_val)
    e_cal = 1e3 * (fk(res.x, q_val) - m_val)
    return e_nom, e_cal


def fig_17_4():
    e_nom, e_cal = calibration()
    n_nom = np.linalg.norm(e_nom, axis=1)
    n_cal = np.linalg.norm(e_cal, axis=1)
    rms_n, rms_c = np.sqrt(np.mean(n_nom ** 2)), np.sqrt(np.mean(n_cal ** 2))
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.8, 3.7), gridspec_kw=dict(width_ratios=[1, 1.2]))
    for e in e_nom:
        a1.annotate("", xy=(e[0], e[1]), xytext=(0, 0),
                    arrowprops=dict(arrowstyle="-|>", color=RED, lw=0.7, alpha=0.75,
                                    mutation_scale=6, shrinkA=0, shrinkB=0))
    a1.plot(e_cal[:, 0], e_cal[:, 1], "o", color=BLUE, ms=2.0, zorder=5)
    a1.plot([], [], color=RED, lw=1.0, label=f"nominal model (max {n_nom.max():.2f} mm)")
    a1.plot([], [], "o", color=BLUE, ms=3, label=f"calibrated (max {n_cal.max():.2f} mm)")
    a1.add_patch(plt.Circle((0, 0), 1.0, fill=False, ls=(0, (4, 2)), color=INK, lw=0.8))
    a1.text(0.75, -0.8, "1.0 mm\n(R3)", fontsize=7, ha="left", va="top")
    a1.set_xlim(-3, 3)
    a1.set_ylim(-3, 3)
    a1.set_aspect("equal")
    a1.axhline(0, color="#CCCCCC", lw=0.6, zorder=0)
    a1.axvline(0, color="#CCCCCC", lw=0.6, zorder=0)
    a1.set_xlabel("x error (mm)")
    a1.set_ylabel("z error (mm)")
    a1.legend(fontsize=6.8, loc="upper left", handletextpad=0.4, borderaxespad=0.1)
    a1.set_title("Error vectors, 40 validation poses", fontsize=9)
    # inset: calibrated errors magnified
    ai = a1.inset_axes([0.62, 0.03, 0.36, 0.36])
    ai.plot(e_cal[:, 0], e_cal[:, 1], "o", color=BLUE, ms=2.2)
    ai.add_patch(plt.Circle((0, 0), 0.042, fill=False, ls=":", color=GREEN, lw=1.0))
    ai.set_xlim(-0.15, 0.15)
    ai.set_ylim(-0.15, 0.15)
    ai.set_aspect("equal")
    ai.set_xticks([-0.1, 0.1])
    ai.set_yticks([-0.1, 0.1])
    ai.tick_params(labelsize=6, length=2, pad=1)
    ai.set_facecolor('white')
    for sp in ("top", "right"):
        ai.spines[sp].set_visible(True)
    ai.set_title("calibrated (mm), ×20", fontsize=6.4, pad=2, color=BLUE)

    bins = np.arange(0, 3.0001, 0.1)
    a2.hist(n_nom, bins=bins, color=RED, alpha=0.75,
            label=f"nominal: RMS {rms_n:.2f} mm, max {n_nom.max():.2f} mm")
    cnt, _, _ = a2.hist(n_cal, bins=bins, color=BLUE, alpha=0.9,
                        label=f"calibrated: RMS {rms_c:.3f} mm, max {n_cal.max():.2f} mm")
    ytop = 12
    for i, c in enumerate(cnt):
        if c > ytop:
            a2.text(bins[i] + 0.12, ytop - 0.4, f"{int(c)} poses ↑", fontsize=7, color=BLUE,
                    va="top", ha="left")
    a2.axvline(1.0, color=INK, ls=(0, (5, 3)), lw=1.0)
    a2.text(1.03, 9.0, "R3 limit\n1.0 mm", fontsize=7.4, va="top")
    a2.axvline(0.042, color=GREEN, ls=":", lw=1.4)
    a2.annotate("tracker noise floor\n0.03 × √2 = 0.042 mm", xy=(0.042, 6.5), xytext=(0.3, 6.5),
                fontsize=7.2, color=GREEN, va="center",
                arrowprops=dict(arrowstyle="-", color=GREEN, lw=0.7))
    a2.set_xlim(0, 3)
    a2.set_ylim(0, ytop)
    a2.set_xlabel("error magnitude (mm)")
    a2.set_ylabel("number of poses (0.1 mm bins)")
    a2.legend(fontsize=6.6, loc="upper right", bbox_to_anchor=(1.0, 1.0))
    a2.set_title("Distribution of error magnitude", fontsize=9)
    fig.tight_layout(w_pad=1.0)
    save(fig, "17", "fig-17-4-calibration-errors")


# ----------------------------------------------------------------------------
# Figure 17.5 — shoulder frequency response
# ----------------------------------------------------------------------------
def two_mass(f, JL, JM, K, zeta):
    """Torque command -> motor velocity, two-mass model; zeta is the damping ratio of the resonance."""
    s = 2j * np.pi * f
    wr = np.sqrt(K * (JL + JM) / (JL * JM))
    c = 2 * zeta * wr * JL * JM / (JL + JM)       # shaft damping (N m s/rad)
    num = JL * s ** 2 + c * s + K
    den = s * (JM * JL * s ** 2 + c * (JM + JL) * s + K * (JM + JL))
    return num / den


def fig_17_5():
    f = np.logspace(0, 2, 1200)
    JL, JM, K, z = 2.84, 1.2, 2.5e4, 0.05
    G = two_mass(f, JL, JM, K, z)
    Gf = two_mass(f, 0.6, JM, K, z)
    # "measured": a slightly different real joint, chirp-estimated with noise
    rng = np.random.default_rng(175)
    fm = np.logspace(0, 2, 90)
    Gm = two_mass(fm, 2.70, 1.22, 2.42e4, 0.06)
    mag_m = 20 * np.log10(np.abs(Gm)) + rng.normal(0, 0.8, fm.size)
    ph_m = np.degrees(np.angle(Gm)) + rng.normal(0, 4, fm.size)
    mass = 1 / (2 * np.pi * f * (JL + JM))
    fa, fr = np.sqrt(K / JL) / (2 * np.pi), np.sqrt(K * (1 / JL + 1 / JM)) / (2 * np.pi)
    faf, frf = np.sqrt(K / 0.6) / (2 * np.pi), np.sqrt(K * (1 / 0.6 + 1 / JM)) / (2 * np.pi)

    fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.4, 4.8), sharex=True,
                                 gridspec_kw=dict(height_ratios=[1.6, 1]))
    for a in (a1, a2):
        a.axvspan(4.6, 5.4, color=GREEN, alpha=0.18, lw=0)
        a.set_xscale("log")
    a1.plot(fm, mag_m, "o", color="#999999", ms=3, label="measured (chirp 1–100 Hz)")
    a1.plot(f, 20 * np.log10(mass), color=GREY, lw=0.9, ls=":", label="rigid mass line, −20 dB/dec")
    a1.plot(f, 20 * np.log10(np.abs(G)), color=BLUE, lw=1.8,
            label="fitted two-mass model, full reach")
    a1.plot(f, 20 * np.log10(np.abs(Gf)), color=ORANGE, lw=1.4, ls=(0, (5, 2)),
            label="folded, no payload ($J_L$ = 0.6 kg·m²)")
    dB = lambda g: 20 * np.log10(np.abs(g))  # noqa: E731
    ya = dB(G[np.argmin(np.abs(G))])
    yr = dB(G).max()
    a1.annotate(f"anti-resonance {fa:.1f} Hz", xy=(fa, ya), xytext=(18, -84), fontsize=7.6,
                color=BLUE, arrowprops=dict(arrowstyle="-", color=BLUE, lw=0.7), va="center")
    a1.annotate(f"resonance {fr:.1f} Hz", xy=(fr, yr), xytext=(9.0, -22), fontsize=7.6,
                color=BLUE, va="center", ha="right",
                arrowprops=dict(arrowstyle="-", color=BLUE, lw=0.7))
    yaf = dB(Gf[np.argmin(np.abs(Gf))])
    a1.annotate(f"folded: {faf:.0f} Hz / {frf:.0f} Hz", xy=(faf, yaf), xytext=(45, -78),
                fontsize=7.4, color=ORANGE, va="center", ha="left",
                arrowprops=dict(arrowstyle="-", color=ORANGE, lw=0.7))
    a1.set_ylim(-95, -15)
    a1.set_ylabel("magnitude (dB re 1 rad/s per N·m)")
    a1.legend(fontsize=6.9, loc="lower left", ncol=1)
    a1.text(1.05, -64, "fit: $J_L$ 2.84, $J_M$ 1.2 kg·m²,\n$K$ 2.5×10⁴ N·m/rad, ζ 0.05",
            fontsize=7.0, color=BLUE)
    a2.plot(fm, ph_m, "o", color="#999999", ms=3)
    a2.plot(f, np.degrees(np.angle(G)), color=BLUE, lw=1.8)
    a2.plot(f, np.degrees(np.angle(Gf)), color=ORANGE, lw=1.4, ls=(0, (5, 2)))
    a2.set_ylim(-180, 90)
    a2.set_yticks([-180, -90, 0, 90])
    a2.set_ylabel("phase (°)")
    a2.set_xlabel("frequency (Hz)")
    a2.set_xlim(1, 100)
    a2.text(5.6, -150, "position-loop bandwidth 5 Hz", fontsize=7.2, color="#2F6B3A", va="center")
    from matplotlib.ticker import FixedLocator, NullFormatter
    a2.xaxis.set_major_locator(FixedLocator([1, 2, 5, 10, 20, 50, 100]))
    a2.set_xticklabels(["1", "2", "5", "10", "20", "50", "100"])
    a2.xaxis.set_minor_formatter(NullFormatter())
    fig.align_ylabels([a1, a2])
    fig.tight_layout(h_pad=0.4)
    save(fig, "17", "fig-17-5-shoulder-frf")


# ----------------------------------------------------------------------------
# Figure 17.6 — the two HIL benches
# ----------------------------------------------------------------------------
def tb2(ax, x, y, w, h, title, body, fc, fs=7.6, bfs=6.4):
    """Box with the title at the top and the body text at the bottom."""
    rbox(ax, x, y, w, h, fc=fc)
    ax.text(x + w / 2, y + h - 0.15, title, ha="center", va="top", fontsize=fs, weight="bold",
            linespacing=1.05)
    if body:
        ax.text(x + w / 2, y + 0.18, body, ha="center", va="bottom", fontsize=bfs, linespacing=1.1)


def fig_17_6():
    fig, ax = schematic(6.8, 4.95, xlim=(0, 17), ylim=(0, 12.3))
    real = tint(GREEN, "35")
    emu = tint(SKY, "40")
    inj = tint(RED, "20")
    # top: test PC and its links
    tbox(ax, 5.0, 10.3, 7.0, 1.8, "Test PC: pytest suite",
         "≈ 300 cases in 6 h, every firmware build", fc=tint(PINK, "28"), fs=8, bfs=7.0)
    tbox(ax, 0.1, 10.45, 4.3, 1.5, "Requirements DB", "traced to R1–R12", fc="#F2F2F2",
         fs=7.8, bfs=7.0)
    tbox(ax, 12.6, 10.45, 4.3, 1.5, "Nightly regression", "report", fc="#F2F2F2", fs=7.8, bfs=7.0)
    line(ax, [(4.4, 11.2), (5.0, 11.2)], both=True)
    line(ax, [(12.0, 11.2), (12.6, 11.2)], arrow_end=True)
    # bench frames
    rbox(ax, 0.1, 0.1, 8.2, 9.5, fc="white", ec=GREY, ls=(0, (4, 2)))
    rbox(ax, 8.7, 0.1, 8.2, 9.5, fc="white", ec=GREY, ls=(0, (4, 2)))
    ax.text(4.2, 9.15, "Joint dynamometer bench", fontsize=8.8, weight="bold", ha="center")
    ax.text(12.8, 9.15, "System HIL bench", fontsize=8.8, weight="bold", ha="center")
    line(ax, [(6.5, 10.3), (6.5, 9.6)], arrow_end=True)
    line(ax, [(10.5, 10.3), (10.5, 9.6)], arrow_end=True)

    # --- joint dynamometer -------------------------------------------------
    tb2(ax, 0.4, 6.3, 2.6, 2.2, "Real joint\nmodule", "DUT: firmware,\nFOC, brake", real)
    rbox(ax, 3.15, 6.95, 1.9, 0.9, fc="#F5F5F5")
    ax.text(4.1, 7.4, "100 N·m\ntorque sensor", fontsize=6.2, ha="center", va="center")
    line(ax, [(3.0, 7.4), (3.15, 7.4)], lw=2.4)
    line(ax, [(5.05, 7.4), (5.2, 7.4)], lw=2.4)
    tb2(ax, 5.2, 6.3, 2.8, 2.2, "Load motor", "controller runs\nlink model\nat 10 kHz", emu)
    ax.text(8.0, 5.55, "virtual inertia 0.6–4 kg·m²,\ngravity torque to 50 N·m,\ncompliant coupling",
            fontsize=6.4, ha="right", va="center", color="#1B5E7A")
    tb2(ax, 0.4, 2.5, 3.3, 1.9, "Programmable\n48 V source/sink", "set source-only,\n3.82 mF", emu)
    line(ax, [(1.3, 4.4), (1.3, 6.3)], color=POWER, lw=1.6, both=True)
    ax.text(1.15, 5.35, "48 V\nbus", fontsize=6.4, color=POWER, ha="right", va="center")
    tb2(ax, 4.6, 2.5, 3.4, 1.9, "Fault relays", "on encoder lines,\nCAN and bus", inj)
    line(ax, [(5.0, 4.4), (2.8, 6.3)], color=RED, lw=1.0, arrow_end=True, ls=(0, (3, 2)))
    ax.text(4.2, 1.15, "covers 20 kHz current loop … 30 Hz resonances:\n"
            "fast loops, heating, regeneration, fault reactions", fontsize=6.6, ha="center",
            va="center", style="italic")

    # --- system HIL --------------------------------------------------------
    tbox(ax, 9.0, 6.6, 2.9, 1.9, "Real main\ncontroller", "", fc=real, fs=7.8)
    tbox(ax, 12.4, 6.6, 2.7, 1.9, "Real safety\ncontroller", "", fc=real, fs=7.8)
    tbox(ax, 15.35, 6.6, 1.35, 1.9, "relay\nE-stop\ninputs", "", fc=inj, fs=6.4)
    line(ax, [(15.35, 7.55), (15.1, 7.55)], color=SAFE, lw=1.3, arrow_end=True, ms=8)
    ybus = 5.75
    line(ax, [(9.2, ybus), (16.6, ybus)], color=DATA, lw=2.4)
    ax.text(16.6, ybus - 0.12, "real CAN FD bus", fontsize=6.6, color=DATA, ha="right", va="top")
    line(ax, [(10.45, 6.6), (10.45, ybus)], color=DATA, lw=1.4)
    line(ax, [(13.2, 6.6), (13.2, ybus)], color=DATA, lw=1.4)
    tbox(ax, 9.0, 4.0, 4.6, 1.1, "", "", fc=inj)
    ax.text(11.3, 4.72, "bus fault injector", fontsize=6.8, weight="bold", ha="center", va="center")
    ax.text(11.3, 4.3, "drop · delay · corrupt · bus-off", fontsize=6.2, ha="center", va="center",
            color=RED)
    line(ax, [(11.3, ybus), (11.3, 5.1)], color=DATA, lw=1.4)
    line(ax, [(11.3, 4.0), (11.3, 3.6)], color=DATA, lw=1.4)
    tb2(ax, 9.0, 2.0, 7.6, 1.6, "Real-time target", "", emu)
    ax.text(12.8, 2.5, "emulates six joints on the bus;\nintegrates rigid-body dynamics at 1 ms",
            fontsize=6.3, ha="center", va="center")
    line(ax, [(14.6, 6.6), (14.6, 3.6)], color=SAFE, lw=1.4, arrow_end=True)
    ax.text(14.75, 4.6, "STO ×2", fontsize=6.4, color="#8A6A00", ha="left", va="center")
    ax.text(12.8, 1.15, "covers 30 Hz … minutes: trajectories, feed-forward,\n"
            "bus timing, system-level fault reactions", fontsize=6.6, ha="center",
            va="center", style="italic")
    save(fig, "17", "fig-17-6-hil-benches")


if __name__ == "__main__":
    fig_17_1()
    fig_17_2()
    fig_17_3()
    fig_17_4()
    fig_17_5()
    fig_17_6()
