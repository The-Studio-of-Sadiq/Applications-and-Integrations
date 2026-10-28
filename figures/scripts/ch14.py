"""Figures for Chapter 14 — Mobile Robotics.

Run from the repository root:  python figures/scripts/ch14.py
"""
import heapq
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle, Circle, Polygon, FancyArrowPatch  # noqa: E402
from matplotlib.colors import ListedColormap  # noqa: E402
from scipy.ndimage import distance_transform_edt  # noqa: E402
from scipy.optimize import least_squares  # noqa: E402

from figstyle import COLORS, INK, box, save, schematic, new_fig  # noqa: E402

BLUE, ORANGE, GREEN, PINK, YELLOW, SKY = COLORS[:6]
RED = "#C62828"
GREY = "#777777"


def tint(c, a="30"):
    return c + a


def line(ax, pts, color=INK, lw=1.1, ls="-", arrow_end=False, both=False, ms=10):
    xs, ys = zip(*pts)
    if not arrow_end and not both:
        ax.plot(xs, ys, color=color, lw=lw, ls=ls, solid_capstyle="butt")
        return
    if len(pts) > 2:
        ax.plot(xs[:-1], ys[:-1], color=color, lw=lw, ls=ls)
    ax.annotate("", xy=pts[-1], xytext=pts[-2],
                arrowprops=dict(arrowstyle="<|-|>" if both else "-|>", color=color, lw=lw,
                                ls=ls, shrinkA=0, shrinkB=0, mutation_scale=ms))


# ----------------------------------------------------------------------------
# Figure 14.1 — architecture of the delivery robot
# ----------------------------------------------------------------------------
def fig_14_1():
    fig, ax = schematic(6.8, 5.0, xlim=(0, 17.4), ylim=(0, 12.8))
    # top row: navigation computer and its peripherals
    box(ax, 4.6, 9.4, 6.0, 2.2, "Navigation computer (ROS 2)\nlocalization, planner,\n"
        "mission state machine", fc=tint(BLUE, "26"), fontsize=8.4)
    box(ax, 0.1, 11.0, 3.4, 1.1, "2D lidar", fc="#EFEFEF", fontsize=8)
    box(ax, 0.1, 9.3, 3.4, 1.1, "Depth camera", fc="#EFEFEF", fontsize=8)
    box(ax, 11.4, 11.0, 4.3, 1.4, "Wi-Fi: fleet manager\nand lift API", fc="#EFEFEF", fontsize=7.8)
    line(ax, [(3.5, 11.55), (4.6, 11.0)], both=True, color=GREY)
    ax.text(3.6, 11.75, "Ethernet", fontsize=7, color=GREY)
    line(ax, [(3.5, 9.85), (4.6, 10.0)], both=True, color=GREY)
    ax.text(3.65, 9.45, "USB", fontsize=7, color=GREY)
    line(ax, [(10.6, 11.0), (11.4, 11.6)], both=True, color=GREY)

    # middle: MCU
    box(ax, 4.6, 5.4, 6.0, 2.0, "Motor-control MCU\nSTM32G4 class\n1 kHz wheel loops, odometry",
        fc=tint(GREEN, "30"), fontsize=8.4)
    line(ax, [(6.6, 9.4), (6.6, 7.4)], arrow_end=True, color=BLUE, lw=1.3)
    line(ax, [(8.6, 7.4), (8.6, 9.4)], arrow_end=True, color=GREEN, lw=1.3)
    ax.text(6.45, 8.4, "cmd_vel\n50 Hz", fontsize=7.2, color=BLUE, ha="right", va="center")
    ax.text(8.75, 8.4, "odometry\n100 Hz", fontsize=7.2, color=GREEN, ha="left", va="center")
    ax.text(7.6, 8.4, "UART\n1 Mbit/s", fontsize=7.2, ha="center", va="center")
    # MCU inputs on the left
    ins = ["IMU (SPI)", "Encoders L, R", "Bumper", "4 cliff ToF sensors"]
    for i, t in enumerate(ins):
        y = 7.45 - i * 0.78
        box(ax, 0.1, y - 0.33, 3.4, 0.66, t, fc="#F6F6F6", fontsize=7.6)
        line(ax, [(3.5, y), (4.6, 6.4 + (1.5 - i) * 0.3)], arrow_end=True, lw=0.9)
    # outputs: drivers and motors
    for k, (x, side) in enumerate([(4.4, "L"), (7.7, "R")]):
        box(ax, x, 3.2, 3.0, 1.2, f"Motor driver {side}\nSTO input", fc="#FBE3D6", fontsize=7.6)
        box(ax, x, 0.6, 3.0, 1.3, f"Gearmotor {side}: BLDC\n+ spring brake", fc="#FBE3D6",
            fontsize=7.0)
        line(ax, [(x + 1.2, 5.4), (x + 1.2, 4.4)], arrow_end=True)
        line(ax, [(x + 1.2, 3.2), (x + 1.2, 1.9)], arrow_end=True)
        line(ax, [(x + 2.5, 2.55), (x + 2.5, 3.2)], arrow_end=True, color=ORANGE, lw=1.4)
    ax.text(5.7, 4.9, "PWM", fontsize=7, ha="left", va="center")
    ax.text(9.0, 4.9, "PWM", fontsize=7, ha="left", va="center")

    # safety chain on the right
    box(ax, 12.2, 6.3, 4.2, 1.8, "Safety laser scanner\nfield sets, OSSD", fc=tint(RED, "22"),
        fontsize=7.8)
    box(ax, 12.2, 3.3, 4.2, 1.3, "Safety relay", fc=tint(RED, "22"), fontsize=8.2)
    line(ax, [(10.6, 7.2), (12.2, 7.2)], arrow_end=True, color=INK)
    ax.text(11.4, 7.05, "field-set\ninputs\n(speed)", fontsize=6.8, ha="center", va="top")
    line(ax, [(14.3, 6.3), (14.3, 4.6)], arrow_end=True, color=RED, lw=1.3)
    ax.text(14.45, 5.45, "OSSD", fontsize=7.2, color=RED, va="center")
    line(ax, [(12.2, 3.95), (10.7, 3.95)], arrow_end=True, color=RED, lw=1.3, ls=(0, (4, 2)))
    line(ax, [(12.2, 3.6), (11.5, 3.6), (11.5, 4.8), (7.0, 4.8), (7.0, 4.4)],
         color=RED, lw=1.3, ls=(0, (4, 2)), arrow_end=True)
    ax.text(14.3, 3.2, "cuts STO of both drivers", fontsize=7.2, color=RED, ha="center",
            va="top")

    # bottom: power
    box(ax, 11.6, 0.1, 5.7, 2.1, "", fc="#FFF3D6")
    ax.text(14.45, 1.8, "25.6 V 30 Ah LFP pack + BMS", fontsize=7.4, ha="center", va="center",
            weight="bold")
    ax.text(14.45, 0.85, "fuse → motor bus\nDC-DC 12 V and 5 V rails\ncharge contacts",
            fontsize=7.4, ha="center", va="center")
    line(ax, [(11.6, 1.2), (11.2, 1.2), (11.2, 2.55), (6.9, 2.55)], color=ORANGE, lw=1.6)
    ax.text(7.75, 2.45, "motor bus", fontsize=7, color=ORANGE, ha="left", va="top")
    line(ax, [(16.8, 2.2), (16.8, 9.0), (10.6, 9.0)], color=ORANGE, lw=1.6, arrow_end=True)
    ax.text(16.65, 8.85, "12 V / 5 V", fontsize=7, color=ORANGE, ha="right", va="top")
    save(fig, "14", "fig-14-1-delivery-robot-architecture")


# ----------------------------------------------------------------------------
# Figure 14.2 — differential-drive kinematics
# ----------------------------------------------------------------------------
def fig_14_2():
    # Page coordinates in metres: robot x_R points up the page, y_R to the left.
    fig, ax = schematic(6.6, 3.9, xlim=(-1.5, 0.95), ylim=(-0.62, 0.78))
    ax.add_patch(Circle((0, 0), 0.30, fc="#EEF3F8", ec=INK, lw=1.2))
    for xw in (-0.2, 0.2):     # wheels 150 mm long, 40 mm wide
        ax.add_patch(Rectangle((xw - 0.02, -0.075), 0.04, 0.15, fc="#555555", ec=INK, lw=0.8,
                               zorder=3))
    for yc in (0.22, -0.22):   # casters 100 mm
        ax.add_patch(Rectangle((-0.01, yc - 0.05), 0.02, 0.10, fc="#AAAAAA", ec=INK, lw=0.6,
                               zorder=3))
        ax.add_patch(Circle((0, yc), 0.022, fc="white", ec=INK, lw=0.8, zorder=4))
    ax.annotate("casters Ø 100 mm", xy=(0.02, -0.235), xytext=(0.36, -0.47), fontsize=7.6,
                color=GREY, arrowprops=dict(arrowstyle="-", color=GREY, lw=0.7))
    ax.text(-0.29, -0.2, "L", fontsize=8, ha="center", weight="bold")
    ax.text(0.29, -0.2, "R", fontsize=8, ha="center", weight="bold")
    # axle line, ICR, R
    R = 1.2
    ax.plot([-R - 0.08, 0.3], [0, 0], color=GREY, lw=0.8, ls="-.", zorder=1)
    ax.plot(-R, 0, "o", color=RED, ms=7, zorder=5)
    ax.text(-R, 0.06, "ICR", fontsize=9, color=RED, ha="center", va="bottom")
    ax.annotate("", xy=(0, -0.43), xytext=(-R, -0.43),
                arrowprops=dict(arrowstyle="<|-|>", color=RED, lw=0.9, mutation_scale=8,
                                shrinkA=0, shrinkB=0))
    ax.plot([-R, -R], [-0.02, -0.47], color=RED, lw=0.6, ls=":")
    ax.plot([0, 0], [-0.31, -0.47], color=RED, lw=0.6, ls=":")
    ax.text(-R / 2 - 0.05, -0.46, "R = v/ω = 1.2 m", fontsize=8.2, color=RED, ha="center",
            va="top")
    # velocity arrows, 0.6 m of page per m/s
    sc = 0.6
    for xw, v, lab, col, dx, ha in [(-0.2, 0.5, "$v_L$ = 0.5 m/s", BLUE, -0.03, "right"),
                                    (0.2, 0.7, "$v_R$ = 0.7 m/s", BLUE, 0.03, "left"),
                                    (0.0, 0.6, "$v$ = 0.6 m/s", INK, 0.0, "center")]:
        ax.annotate("", xy=(xw, sc * v), xytext=(xw, 0),
                    arrowprops=dict(arrowstyle="-|>", color=col, lw=1.8, mutation_scale=12,
                                    shrinkA=0, shrinkB=0), zorder=6)
        ax.text(xw + dx, sc * v + 0.02, lab, fontsize=8.2, color=col, ha=ha, va="bottom")
    # linear velocity distribution about the ICR
    ax.plot([-R, 0.2], [0, sc * 0.7], color=BLUE, lw=0.9, ls="--", zorder=2)
    ax.plot([-R, -0.2], [0, 0], color=RED, lw=0.9, ls="--", zorder=2)
    ax.text(-0.75, 0.2, "speed ∝ distance\nfrom the ICR", fontsize=7.4, color=BLUE,
            ha="center", rotation=0)
    # robot frame
    ax.annotate("", xy=(0, 0.16), xytext=(0, 0),
                arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.6, mutation_scale=10), zorder=7)
    ax.annotate("", xy=(-0.16, 0), xytext=(0, 0),
                arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=1.6, mutation_scale=10), zorder=7)
    ax.text(0.03, 0.12, "$x_R$", fontsize=9, color=RED, ha="left")
    ax.text(-0.12, -0.03, "$y_R$", fontsize=9, color=GREEN, ha="center", va="top")
    # track width
    ax.annotate("", xy=(0.2, -0.36), xytext=(-0.2, -0.36),
                arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.9, mutation_scale=8,
                                shrinkA=0, shrinkB=0))
    for xw in (-0.2, 0.2):
        ax.plot([xw, xw], [-0.08, -0.39], color=INK, lw=0.6)
    ax.text(-0.24, -0.36, "b = 0.400 m", fontsize=8, ha="right", va="center")
    # omega arrow (counter-clockwise)
    tt = np.radians(np.linspace(-50, 25, 60))
    ax.plot(0.4 * np.cos(tt[:-3]), 0.4 * np.sin(tt[:-3]), color=ORANGE, lw=1.4)
    ax.annotate("", xy=(0.4 * np.cos(tt[-1]), 0.4 * np.sin(tt[-1])),
                xytext=(0.4 * np.cos(tt[-4]), 0.4 * np.sin(tt[-4])),
                arrowprops=dict(arrowstyle="-|>", color=ORANGE, lw=1.4, mutation_scale=11,
                                shrinkA=0, shrinkB=0))
    ax.text(0.44, -0.12, "ω = 0.5 rad/s", fontsize=8.2, color=ORANGE, ha="left")
    # world frame and heading angle theta (x_W drawn 30 deg above horizontal: theta = 60 deg)
    a = np.radians(30)
    wo = np.array([-1.28, 0.36])
    for ang, lab in [(a, "$x_W$"), (a + np.pi / 2, "$y_W$")]:
        d = np.array([np.cos(ang), np.sin(ang)])
        ax.annotate("", xy=wo + 0.24 * d, xytext=wo,
                    arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.2, mutation_scale=10))
        ax.text(*(wo + 0.31 * d), lab, fontsize=9, ha="center", va="center")
    d = np.array([np.cos(a), np.sin(a)])
    ax.plot([0, 0.42 * d[0]], [0, 0.42 * d[1]], color=GREY, lw=0.9, ls="--", zorder=2)
    ax.text(0.44 * d[0], 0.44 * d[1], "∥ $x_W$", fontsize=7.6, color=GREY, va="bottom")
    tt = np.linspace(a, np.pi / 2, 40)
    ax.plot(0.2 * np.cos(tt), 0.2 * np.sin(tt), color=INK, lw=0.9, zorder=6)
    ax.text(0.22 * np.cos(np.radians(62)), 0.22 * np.sin(np.radians(62)), "θ", fontsize=10,
            ha="left", va="bottom")
    ax.text(0.92, 0.72, "chassis Ø 0.60 m\ndrive wheels Ø 150 mm, 40 mm wide",
            fontsize=7.4, color=GREY, ha="right", va="top")
    save(fig, "14", "fig-14-2-diff-drive-kinematics")


# ----------------------------------------------------------------------------
# Figure 14.3 — stopping distance and protective fields
# ----------------------------------------------------------------------------
def fig_14_3():
    v = np.linspace(0, 1.4, 300)
    tr, a = 0.17, 1.0
    s_r = v * tr
    s = v * tr + v ** 2 / (2 * a)
    fig, ax = new_fig(6.4, 3.9)
    ax.plot(v, s_r, ls="--", color=GREY, lw=1.4, label="reaction distance $v\\,t_r$ ($t_r$ = 0.17 s)")
    ax.plot(v, s, color=BLUE, lw=2, label="stopping distance $v\\,t_r + v^2/2a$ (a = 1.0 m/s²)")
    edges = [0.0, 0.6, 0.9, 1.2]
    fields = [0.48, 0.80, 1.12]
    ax.stairs(fields, edges, color=ORANGE, lw=2, baseline=None, label="protective field length")
    for (x0, x1), f in zip(zip(edges[:-1], edges[1:]), fields):
        vv = np.linspace(x0, x1, 50)
        ax.fill_between(vv, vv * tr + vv ** 2 / (2 * a), f, color=ORANGE, alpha=0.15, lw=0)
        ax.text(x1 - 0.015, f + 0.025, f"{f:.2f} m", fontsize=7.8, color=ORANGE, ha="right",
                va="bottom")
    ax.text(0.33, 0.33, "margin", fontsize=8, color=ORANGE, ha="center")
    vm = np.array([0.3, 0.6, 0.9, 1.2])
    sm = np.array([0.11, 0.30, 0.59, 0.97])
    ax.plot(vm, sm, "o", mfc="white", mec=RED, mew=1.6, ms=6, label="measured stop (R8 test)")
    for vi in vm:
        si = vi * tr + vi ** 2 / 2
        ax.text(vi + 0.02, si - 0.05, f"{si:.3f}", fontsize=7, color=BLUE, ha="left", va="top")
    ax.set_xlim(0, 1.4)
    ax.set_ylim(0, 1.6)
    ax.set_xlabel("speed (m/s)")
    ax.set_ylabel("distance (m)")
    ax.legend(fontsize=7.6, loc="upper left")
    save(fig, "14", "fig-14-3-stopping-distance")


# ----------------------------------------------------------------------------
# Figure 14.4 — UMBmark squares (Listing 14.1)
# ----------------------------------------------------------------------------
def _square(true, model, cw, L=4.0, n=200, path=False):
    (rL, rR, b), (mL, mR, mb) = true, model
    s = -1.0 if cw else 1.0
    seg = [(L / mL, L / mR), (-s * np.pi / 4 * mb / mL, s * np.pi / 4 * mb / mR)]
    x = y = th = 0.0
    pts = [(0.0, 0.0)]
    for _ in range(4):
        for pL, pR in seg:
            for _ in range(n):
                dL, dR = rL * pL / n, rR * pR / n
                ds, dth = 0.5 * (dL + dR), (dR - dL) / b
                x += ds * np.cos(th + dth / 2)
                y += ds * np.sin(th + dth / 2)
                th += dth
                pts.append((x, y))
    return np.array(pts) if path else np.array([x, y])


def _wheels(Ed, b, r=0.075):
    return (2 * r / (1 + Ed), 2 * r * Ed / (1 + Ed), b)


def fig_14_4():
    true, nominal = _wheels(1.005, 0.406), _wheels(1.0, 0.400)

    def ends(model):
        return np.concatenate([_square(true, model, cw) for cw in (True, False)])
    rng = np.random.default_rng(1)
    meas = ends(nominal) + rng.normal(0, 0.005, 4)
    fit = least_squares(lambda p: np.concatenate(
        [_square(_wheels(*p), nominal, cw) for cw in (True, False)]) - meas,
        [1.0, 0.400], diff_step=1e-4)
    Ed, b = fit.x
    cal = _wheels(Ed, b)

    fig = plt.figure(figsize=(6.6, 5.2))
    ax = fig.add_axes([0.09, 0.09, 0.48, 0.88])
    sq_cw = np.array([(0, 0), (4, 0), (4, -4), (0, -4), (0, 0)])
    sq_ccw = np.array([(0, 0), (4, 0), (4, 4), (0, 4), (0, 0)])
    ax.plot(*sq_cw.T, color="#BBBBBB", lw=3.5, label="commanded", zorder=1)
    ax.plot(*sq_ccw.T, color="#BBBBBB", lw=3.5, zorder=1)
    p_cw = _square(true, nominal, True, path=True)
    p_ccw = _square(true, nominal, False, path=True)
    a_cw = _square(true, cal, True, path=True)
    a_ccw = _square(true, cal, False, path=True)
    ax.plot(*p_cw.T, color=RED, lw=1.4, label="before, CW")
    ax.plot(*p_ccw.T, color=ORANGE, lw=1.4, label="before, CCW")
    ax.plot(*a_cw.T, color=BLUE, lw=1.0, label="after calibration")
    ax.plot(*a_ccw.T, color=BLUE, lw=1.0)
    dm = np.hypot(*meas.reshape(2, 2).T)          # floor-mark distances (Listing 14.1 output)
    for p, c, xy, d in [(p_cw, RED, (0.55, -1.3), dm[0]), (p_ccw, ORANGE, (0.75, 1.1), dm[1])]:
        e = p[-1]
        ax.plot(*e, "o", color=c, ms=5, zorder=6)
        ax.annotate(f"ends {d:.2f} m\nfrom start", xy=e, xytext=xy, fontsize=8, color=c,
                    va="center", arrowprops=dict(arrowstyle="-", color=c, lw=0.8))
    ax.plot(0, 0, "k+", ms=10, mew=1.5, zorder=7)
    ax.text(2.0, -3.7, "CW square", fontsize=8.5, ha="center", color=INK)
    ax.text(2.0, 3.55, "CCW square", fontsize=8.5, ha="center", color=INK)
    ax.set_xlim(-1.0, 4.8)
    ax.set_ylim(-4.8, 4.8)
    ax.set_aspect("equal")
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    fig.text(0.79, 0.68, f"simulated after calibration: both\nend within "
            f"{max(np.hypot(*a_cw[-1]), np.hypot(*a_ccw[-1])) * 1e3:.0f} mm of the start",
            fontsize=7.4, color=BLUE, ha="center", va="top")
    h, lab = ax.get_legend_handles_labels()
    fig.legend(h, lab, fontsize=8, loc="upper left", bbox_to_anchor=(0.62, 0.95))
    # inset: measured end points of the real robot after calibration (illustrative scatter)
    ins = fig.add_axes([0.66, 0.1, 0.3, 0.42])
    rng2 = np.random.default_rng(7)
    for c, mk, lab, ph in [(BLUE, "o", "CW", -0.6), (GREEN, "s", "CCW", 1.9)]:
        rr = rng2.uniform(48, 71, 5)
        rr[0] = 48.0 if lab == "CW" else rr[0]
        rr[1] = 71.0 if lab == "CCW" else rr[1]
        ang = ph + rng2.uniform(-0.7, 0.7, 5)
        ins.plot(rr * np.cos(ang), rr * np.sin(ang), mk, color=c, ms=5, label=lab,
                 mfc="white" if lab == "CCW" else c)
    tt = np.linspace(0, 2 * np.pi, 200)
    for r0 in (48, 71):
        ins.plot(r0 * np.cos(tt), r0 * np.sin(tt), color=GREY, lw=0.6, ls=":")
    ins.plot(0, 0, "k+", ms=8)
    ins.set_xlim(-90, 90)
    ins.set_ylim(-90, 90)
    ins.set_aspect("equal")
    ins.tick_params(labelsize=7)
    ins.set_xlabel("x (mm)", fontsize=8)
    ins.set_ylabel("y (mm)", fontsize=8)
    ins.set_title("real robot after calibration:\n5 end points per direction,\n48–71 mm from start",
                  fontsize=7.6)
    ins.legend(fontsize=7, loc="upper right", handletextpad=0.2, borderaxespad=0.1,
               bbox_to_anchor=(1.02, 1.02))
    for sp in ("top", "right"):
        ins.spines[sp].set_visible(True)
    save(fig, "14", "fig-14-4-umbmark-squares")


# ----------------------------------------------------------------------------
# Figure 14.5 — A* on the inflated costmap (Listing 14.2)
# ----------------------------------------------------------------------------
def fig_14_5():
    res = 0.05
    occ = np.zeros((240, 400), bool)
    occ[[0, -1], :] = occ[:, [0, -1]] = True
    occ[100:104, :] = True
    occ[100:104, 60:78] = False
    occ[100:104, 300:318] = False
    occ[150:170, 180:200] = True
    dist = distance_transform_edt(~occ) * res
    r_robot, r_infl = 0.30, 0.55
    cost = np.where(dist <= r_robot, np.inf,
                    1.0 + 10.0 * np.clip((r_infl - dist) / (r_infl - r_robot), 0, 1))
    C = cost.tolist()

    def astar(start, goal):
        moves = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

        def h(c):
            return res * math.hypot(c[0] - goal[0], c[1] - goal[1])
        g, parent, todo = {start: 0.0}, {start: None}, [(h(start), start)]
        while todo:
            _, c = heapq.heappop(todo)
            if c == goal:
                path = []
                while c:
                    path.append(c)
                    c = parent[c]
                return path[::-1]
            for dr, dc in moves:
                nb = (c[0] + dr, c[1] + dc)
                step = res * math.hypot(dr, dc) * C[nb[0]][nb[1]]
                if step < math.inf and g[c] + step < g.get(nb, math.inf):
                    g[nb], parent[nb] = g[c] + step, c
                    heapq.heappush(todo, (g[nb] + h(nb), nb))
        return None

    path = np.array(astar((40, 20), (200, 380)))
    p = path * res
    length = np.sum(np.hypot(*np.diff(p, axis=0).T))
    clr = dist[tuple(path.T)]
    k = int(np.argmin(clr))

    fig, ax = new_fig(6.8, 4.5)
    disp = np.where(np.isinf(cost), np.nan, cost)
    cmap = plt.get_cmap("Greys")
    cm2 = ListedColormap(cmap(np.linspace(0.04, 0.55, 256)))
    im = ax.imshow(disp, origin="lower", extent=(0, 20, 0, 12), cmap=cm2, vmin=1, vmax=11,
                   interpolation="nearest")
    lethal = np.where(np.isinf(cost) & ~occ, 1.0, np.nan)
    ax.imshow(lethal, origin="lower", extent=(0, 20, 0, 12),
              cmap=ListedColormap(["#5A5A5A"]), interpolation="nearest")
    ax.imshow(np.where(occ, 1.0, np.nan), origin="lower", extent=(0, 20, 0, 12),
              cmap=ListedColormap(["#000000"]), interpolation="nearest")
    # path: cells are (row, col) -> (y, x)
    ax.plot(p[:, 1] + res / 2, p[:, 0] + res / 2, color=BLUE, lw=2)
    ax.plot(1.0 + res / 2, 2.0 + res / 2, "o", color=GREEN, ms=8, mec="white", mew=1.2)
    ax.plot(19.0 + res / 2, 10.0 + res / 2, "*", color=RED, ms=13, mec="white", mew=0.8)
    ax.text(1.25, 2.3, "start (1.0, 2.0)", fontsize=8, va="bottom")
    ax.text(18.8, 10.45, "goal: lab door (19.0, 10.0)", fontsize=8, ha="right", va="bottom")
    ax.text(13.3, 6.9, f"A* path {length:.2f} m", fontsize=8.5, color=BLUE, ha="left",
            weight="bold")
    door = p[k]
    ax.annotate(f"min. clearance {clr[k]:.2f} m\n(door centre x ≈ {(3.0 + 3.9) / 2:.2f} m)",
                xy=(door[1] + res / 2, door[0] + res / 2), xytext=(5.0, 3.4), fontsize=8,
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.9, mutation_scale=8))
    ax.text(9.5, 8.75, "parked bed", fontsize=7.5, ha="center", va="bottom")
    ax.text(15.45, 4.4, "second door", fontsize=7.5, ha="center", va="top")
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 12)
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.set_aspect("equal")
    cb = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    cb.set_label("cell cost (per metre)", fontsize=8.5)
    cb.ax.tick_params(labelsize=7.5)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(fc="#000000", label="occupied"),
                       Patch(fc="#5A5A5A", label="lethal (< 0.30 m)"),
                       Patch(fc=cm2(0.6), label="keep-away (to 0.55 m)")],
              fontsize=7.2, loc="upper left", bbox_to_anchor=(0.0, 1.0), framealpha=0.9,
              frameon=True)
    save(fig, "14", "fig-14-5-astar-costmap")


if __name__ == "__main__":
    fig_14_1()
    fig_14_2()
    fig_14_3()
    fig_14_4()
    fig_14_5()
