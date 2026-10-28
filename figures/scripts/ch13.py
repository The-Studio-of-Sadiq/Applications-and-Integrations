"""Figures for Chapter 13 — Robotics Fundamentals.

Run from the repository root:  python figures/scripts/ch13.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import (Rectangle, FancyBboxPatch, Circle, Polygon,  # noqa: E402
                                Wedge)

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
# Kinematic model of the arm (Listing 13.1)
# ----------------------------------------------------------------------------
DH = [(0.000, np.pi / 2, 0.160, 0.0), (0.200, 0.0, 0.000, np.pi / 2),
      (0.000, np.pi / 2, 0.000, 0.0), (0.000, -np.pi / 2, 0.200, 0.0),
      (0.000, np.pi / 2, 0.000, 0.0), (0.000, 0.0, 0.060, 0.0)]


def dh(a, al, d, th):
    ca, sa, ct, st = np.cos(al), np.sin(al), np.cos(th), np.sin(th)
    return np.array([[ct, -st * ca, st * sa, a * ct], [st, ct * ca, -ct * sa, a * st],
                     [0.0, sa, ca, d], [0.0, 0.0, 0.0, 1.0]])


def fk_all(q):
    T = np.eye(4)
    out = [T.copy()]
    for (a, al, d, off), qi in zip(DH, q):
        T = T @ dh(a, al, d, qi + off)
        out.append(T.copy())
    return out


def fk(q):
    return fk_all(q)[-1]


def pose_error(Tg, T):
    dR = Tg[:3, :3] @ T[:3, :3].T
    w = 0.5 * np.array([dR[2, 1] - dR[1, 2], dR[0, 2] - dR[2, 0], dR[1, 0] - dR[0, 1]])
    return np.concatenate([Tg[:3, 3] - T[:3, 3], w])


def jacobian(q, h=1e-6):
    T0 = fk(q)
    return np.column_stack([pose_error(fk(q + h * np.eye(6)[i]), T0) / h for i in range(6)])


def ik(Tg, q, lam=0.01, iters=200):
    for k in range(iters):
        e = pose_error(Tg, fk(q))
        if np.linalg.norm(e) < 1e-9:
            break
        J = jacobian(q)
        q = q + J.T @ np.linalg.solve(J @ J.T + lam ** 2 * np.eye(6), e)
    return q, k, np.linalg.norm(e[:3])


def tool_down(p):
    T = np.eye(4)
    T[:3, :3] = np.diag([1.0, -1.0, -1.0])
    T[:3, 3] = p
    return T


# ----------------------------------------------------------------------------
# Figure 13.1 — architecture of the arm
# ----------------------------------------------------------------------------
def fig_13_1():
    fig, ax = schematic(6.8, 4.6, xlim=(0, 17.4), ylim=(1.3, 12.5))
    # left column
    box(ax, 0.1, 11.1, 2.95, 1.2, "Camera\nfixed above rack", fc="#EFEFEF", fontsize=7.6)
    box(ax, 0.1, 8.0, 2.95, 2.5, "Motion controller\nLinux SBC\n1 kHz trajectory\nand kinematics",
        fc=tint(BLUE, "26"), fontsize=7.6)
    box(ax, 0.1, 5.8, 2.95, 1.4, "Cell PC\nLIMS, job queue", fc="#EFEFEF", fontsize=7.6)
    line(ax, [(1.55, 10.5), (1.55, 11.1)], both=True, color=GREY)
    ax.text(1.7, 10.8, "Ethernet", fontsize=7, va="center", color=GREY)
    line(ax, [(1.55, 7.2), (1.55, 8.0)], both=True, color=GREY)
    ax.text(1.7, 7.6, "Ethernet", fontsize=7, va="center", color=GREY)

    # CAN FD bus and joint modules
    xb = 3.6
    rows = [("J1 base yaw", "42 mm", "1:100", "18 bit", "none"),
            ("J2 shoulder", "57 mm", "1:100", "18 bit", "0.25 N m"),
            ("J3 elbow", "42 mm", "1:100", "18 bit", "0.10 N m"),
            ("J4 forearm roll", "32 mm", "1:50", "17 bit", "none"),
            ("J5 wrist pitch", "32 mm", "1:50", "17 bit", "yes"),
            ("J6 tool roll", "28 mm", "1:30", "none", "none")]
    x0, w, h, pitch = 3.95, 9.0, 1.32, 1.5
    top = 12.3
    ys = []
    for i, (name, mot, gear, enc_o, brk) in enumerate(rows):
        y = top - h - i * pitch
        ys.append(y)
        ax.add_patch(FancyBboxPatch((x0, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                    fc="#F4F6F9", ec=INK, lw=1.0))
        ax.text(x0 + 0.12, y + h - 0.2, name, fontsize=7.8, weight="bold", va="center")
        gname = "planetary" if i == 5 else "SW gear"
        blocks = [("BLDC\n" + mot, "#FBE3D6"), (gname + "\n" + gear, "#E3E3E3"),
                  ("mot. enc\n14 bit", "#DDEEDD"),
                  ("out. enc\n" + enc_o if enc_o != "none" else "no out.\nenc", "#DDEEDD"),
                  ("brake\n" + brk if brk not in ("none", "yes") else
                   ("spring\nbrake" if brk == "yes" else "no\nbrake"), "#EEE0EE"),
                  ("FOC drv\n+ STO in", tint(BLUE, "22"))]
        bw = (w - 0.2) / 6
        for k, (t, fc) in enumerate(blocks):
            bx = x0 + 0.1 + k * bw
            ax.add_patch(Rectangle((bx + 0.03, y + 0.08), bw - 0.06, 0.8, fc=fc, ec=GREY, lw=0.6))
            ax.text(bx + bw / 2, y + 0.48, t, fontsize=6.2, ha="center", va="center",
                    linespacing=1.15)
        line(ax, [(xb, y + h / 2), (x0, y + h / 2)], color=BLUE, lw=1.0)
        ax.plot(xb, y + h / 2, "o", ms=3, color=BLUE)
    ax.text(x0 + w, ys[0] + h + 0.08, "SW = strain-wave", fontsize=6.6, color=GREY, ha="right", va="bottom")
    # gripper
    yg = ys[-1] - 1.15
    hg = 0.8
    box(ax, x0, yg, w, hg, "Gripper: servo gripper, 24 V, CAN", fc="#FFF3D6", fontsize=8)
    line(ax, [(xb, yg + hg / 2), (x0, yg + hg / 2)], color=BLUE, lw=1.0)
    ax.plot(xb, yg + hg / 2, "o", ms=3, color=BLUE)
    # bus line
    ax.plot([xb, xb], [yg + hg / 2, ys[0] + h / 2], color=BLUE, lw=2.4)
    line(ax, [(3.05, 9.25), (xb, 9.25)], color=BLUE, lw=2.4)
    ax.text(0.15, 5.5, "CAN FD bus\n1 Mbit/s arbitration\n5 Mbit/s data", fontsize=7, color=BLUE,
            va="top")
    line(ax, [(3.3, 4.2), (3.3, 3.0)], color=BLUE, arrow_end=True, lw=1.2)
    ax.text(3.15, 3.6, "set points\nq, q̇, τff", fontsize=6.8, color=BLUE, ha="right",
            va="center")
    line(ax, [(3.3, 1.5), (3.3, 2.7)], color=GREEN, arrow_end=True, lw=1.2)
    ax.text(3.15, 2.1, "encoder,\nstatus", fontsize=6.8, color=GREEN, ha="right", va="center")

    # 24 V bus and STO lines on the right of the modules
    xp, xs = 13.25, 13.6
    ytop = ys[0] + h / 2
    ax.plot([xp, xp], [yg + hg / 2, ytop + 0.2], color=ORANGE, lw=2.4)
    ax.plot([xs, xs], [ys[-1] + h / 2 - 0.2, ytop - 0.2], color=RED, lw=1.4, ls=(0, (4, 2)))
    for y in ys:
        line(ax, [(x0 + w, y + h / 2 + 0.2), (xp, y + h / 2 + 0.2)], color=ORANGE, lw=1.0)
        line(ax, [(xs, y + h / 2 - 0.2), (x0 + w, y + h / 2 - 0.2)], color=RED, lw=1.0,
             ls=(0, (3, 2)), arrow_end=True, ms=7)
    line(ax, [(x0 + w, yg + hg / 2), (xp, yg + hg / 2)], color=ORANGE, lw=1.0)
    ax.text(xp + 0.12, yg + 0.35, "24 V bus", fontsize=7, color=ORANGE, ha="left", va="bottom",
            rotation=90)

    # right column: power
    box(ax, 14.15, 11.0, 3.05, 1.3, "PSU\n24 V, 150 W", fc="#FBE3D6", fontsize=8)
    box(ax, 14.15, 9.0, 3.05, 1.3, "Bus clamp\n+ fuse", fc="#FBE3D6", fontsize=8)
    line(ax, [(15.67, 11.0), (15.67, 10.3)], color=ORANGE, arrow_end=True, lw=1.4)
    line(ax, [(14.15, 9.65), (xp, 9.65)], color=ORANGE, lw=2.4)
    # safety
    box(ax, 14.15, 4.6, 3.05, 1.5, "Safety relay\nPL d", fc=tint(RED, "22"), fontsize=8.2)
    box(ax, 14.15, 7.0, 1.45, 1.0, "E-stop", fc="#F6F6F6", fontsize=7.4)
    box(ax, 15.75, 7.0, 1.45, 1.0, "Light\ncurtain", fc="#F6F6F6", fontsize=7.4)
    line(ax, [(14.87, 7.0), (14.87, 6.1)], arrow_end=True)
    line(ax, [(16.47, 7.0), (16.47, 6.1)], arrow_end=True)
    line(ax, [(14.15, 5.35), (xs, 5.35)], color=RED, lw=1.4, ls=(0, (4, 2)))
    ax.text(15.67, 4.3, "STO line (dashed)\nto all joints", fontsize=7, color=RED, ha="center",
            va="top")
    save(fig, "13", "fig-13-1-arm-architecture")


# ----------------------------------------------------------------------------
# Figure 13.2 — DH frames in the zero pose
# ----------------------------------------------------------------------------
def fig_13_2():
    fig, ax = schematic(6.8, 4.5, xlim=(-170, 640), ylim=(-45, 490))
    Ts = fk_all(np.zeros(6))
    P = [T[:3, 3] * 1000 for T in Ts]       # mm
    # bench
    ax.add_patch(Rectangle((-170, -45), 810, 45, fc="#E6E1D8", ec="none"))
    ax.plot([-170, 640], [0, 0], color=INK, lw=1.4)
    ax.text(-160, -25, "bench", fontsize=8, color=GREY)
    # base cylinder
    ax.add_patch(Rectangle((-45, 0), 90, 120, fc="#D9DEE6", ec=INK, lw=1.0))
    # links (thick grey)
    lk = dict(color="#9AA5B1", lw=9, solid_capstyle="round", zorder=1)
    ax.plot([0, 0], [120, 160], **lk)
    ax.plot([0, 0], [160, 360], **lk)
    ax.plot([0, 200], [360, 360], **lk)
    ax.plot([200, 245], [360, 360], **dict(lk, lw=6))

    def joint_inplane(c, d, length=34, wid=22):
        d = np.asarray(d, float) / np.linalg.norm(d)
        n = np.array([-d[1], d[0]])
        c = np.asarray(c, float)
        pts = [c - d * length / 2 - n * wid / 2, c + d * length / 2 - n * wid / 2,
               c + d * length / 2 + n * wid / 2, c - d * length / 2 + n * wid / 2]
        ax.add_patch(Polygon(pts, fc="#F2C9A8", ec=INK, lw=1.0, zorder=3))

    def joint_outplane(c, sign):
        ax.add_patch(Circle(c, 17, fc="#F2C9A8", ec=INK, lw=1.0, zorder=3))
        ax.add_patch(Circle(c, 7, fc="white", ec=INK, lw=0.9, zorder=4))
        if sign > 0:   # out of page (towards viewer): dot
            ax.plot(*c, "o", ms=2.2, color=INK, zorder=5)
        else:          # into page: cross
            ax.plot([c[0] - 4.5, c[0] + 4.5], [c[1] - 4.5, c[1] + 4.5], color=INK, lw=0.9, zorder=5)
            ax.plot([c[0] - 4.5, c[0] + 4.5], [c[1] + 4.5, c[1] - 4.5], color=INK, lw=0.9, zorder=5)

    def axis_arrow(o, v, txt, color, L=70, off=(6, 6), fs=8.5):
        o = np.asarray(o, float)
        v = np.asarray(v, float)
        e = o + v * L
        ax.annotate("", xy=e, xytext=o, arrowprops=dict(arrowstyle="-|>", color=color, lw=1.3,
                                                         shrinkA=0, shrinkB=0, mutation_scale=9),
                    zorder=6)
        ax.text(e[0] + off[0], e[1] + off[1], txt, fontsize=fs, color=color, ha="center",
                va="center", zorder=7)

    # joints: J1 axis z0 at base (vertical), J2..J6 axes z1..z5
    # origins of joint axes in the drawing
    jpos = {1: (0, 90), 2: (0, 160), 3: (0, 360), 4: (110, 360), 5: (200, 360), 6: (232, 360)}
    for i in range(6):
        z = Ts[i][:3, 2]
        c = jpos[i + 1]
        if abs(z[1]) > 0.9:
            joint_outplane(c, -np.sign(z[1]))   # y is into the page
        else:
            joint_inplane(c, (z[0], z[2]))

    # frame axes (projected into x-z view); y-components shown as dot/cross
    zc, xc = BLUE, RED
    # frame 0 at bench on J1 axis
    axis_arrow((0, 0), (0, 1), "", zc, L=0)
    axis_arrow((0, 0), (1, 0), "$x_0$", xc, L=75, off=(10, -12))
    ax.annotate("", xy=(0, 25), xytext=(0, 0), arrowprops=dict(arrowstyle="-", color=zc))
    axis_arrow((-60, 70), (0, 1), "$z_0$", zc, L=70, off=(-14, 0))
    ax.plot([-60, 0], [70, 70], color=zc, lw=0.6, ls=":")
    # frame 1 (origin at shoulder), z1 out of page -> label beside the circle
    ax.text(-30, 160, "$z_1$ ⊙", fontsize=8.5, color=zc, ha="right", va="center")
    T1 = Ts[1]
    axis_arrow((0, 160), (T1[0, 0], T1[2, 0]), "$x_1$", xc, L=60, off=(10, -10))
    # frame 2 at elbow (a2 = 200 along x2), z2 out of page
    T2 = Ts[2]
    axis_arrow((0, 360), (T2[0, 0], T2[2, 0]), "$x_2, x_3$", xc, L=55, off=(26, 2))
    ax.text(-30, 360, "$z_2$ ⊙", fontsize=8.5, color=zc, ha="right", va="center")
    # frame 3 at elbow, z3 along forearm
    T3 = Ts[3]
    ax.text(101, 395, "$z_3$", fontsize=8.5, color=zc, ha="left", va="center")
    axis_arrow((60, 395), (T3[0, 2], T3[2, 2]), "", zc, L=36)
    x3 = (T3[0, 0], T3[2, 0])
    if abs(T3[1, 0]) > 0.9:
        ax.text(-30, 330, "$x_3$ " + ("⊗" if T3[1, 0] > 0 else "⊙"), fontsize=8.5,
                color=xc, ha="right", va="center")
    else:
        pass
    # frame 4 at wrist centre, z4 (J5 axis) into/out of page
    T4 = Ts[4]
    s4 = "⊗" if T4[1, 2] > 0 else "⊙"
    ax.text(214, 328, "$z_4$ " + s4 + " (J5)", fontsize=8.5, color=zc, ha="left", va="center")
    # frame 5 at wrist centre, z5 along tool (J6)
    T5 = Ts[5]
    ax.text(229, 395, "$z_5$", fontsize=8.5, color=zc, ha="left", va="center")
    axis_arrow((188, 395), (T5[0, 2], T5[2, 2]), "", zc, L=36)
    # x-axes of frames 4..6 (all vertical in zero pose)
    for (T, xo, lab) in [(T4, 196, "$x_4$"), (T5, 206, "")]:
        pass
    axis_arrow((200, 360), (T4[0, 0], T4[2, 0]), "$x_4$", xc, L=-45 if T4[2, 0] > 0 else 45,
               off=(-14, 4))
    # tool and TCP
    tcp = P[6]
    ax.plot([245, 272], [372, 372], color=INK, lw=2.4)
    ax.plot([245, 272], [348, 348], color=INK, lw=2.4)
    ax.plot([245, 245], [348, 372], color=INK, lw=2.4)
    ax.add_patch(Rectangle((253.5, 300), 13, 120, fc="#CFE6F5", ec=INK, lw=0.9, zorder=2))
    ax.add_patch(Rectangle((253.5, 412), 13, 14, fc="#E05050", ec=INK, lw=0.9, zorder=2))
    ax.plot(tcp[0], tcp[2], "+", ms=12, color=INK, mew=1.6, zorder=8)
    ax.text(tcp[0] + 18, tcp[2] - 70, "TCP (260, 0, 360) mm", fontsize=8, ha="left")
    line(ax, [(tcp[0] + 18, tcp[2] - 62), (tcp[0] + 3, tcp[2] - 6)], color=GREY, lw=0.8)
    T6 = Ts[6]
    axis_arrow((tcp[0], tcp[2]), (T6[0, 2], T6[2, 2]), "$z_6$", zc, L=55, off=(12, 0))
    ax.text(186, 300, "wrist centre", fontsize=8, ha="right", va="top")
    line(ax, [(188, 302), (198, 352)], color=GREY, lw=0.8)

    # dimension arrows
    def dim(p0, p1, txt, off, horiz=False):
        line(ax, [p0, p1], both=True, color=GREY, lw=0.9, ms=8)
        mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
        ax.text(mx + off[0], my + off[1], txt, fontsize=8, color=INK, ha="center", va="center",
                rotation=0 if horiz else 90)
    dim((-110, 0), (-110, 160), "160 mm", (-14, 0))
    ax.plot([-118, -20], [160, 160], color=GREY, lw=0.6, ls=":")
    dim((-80, 160), (-80, 360), "200 mm", (-14, 0))
    ax.plot([-88, -20], [360, 360], color=GREY, lw=0.6, ls=":")
    dim((0, 455), (200, 455), "200 mm", (0, 13), horiz=True)
    dim((200, 455), (260, 455), "60 mm", (0, 13), horiz=True)
    for xv in (0, 200, 260):
        ax.plot([xv, xv], [430 if xv else 400, 462], color=GREY, lw=0.6, ls=":")
    ax.text(70, 200, "zero pose\n$\\mathbf{q}=\\mathbf{0}$", fontsize=9, style="italic")
    ax.text(-160, 470, "⊙ out of page   ⊗ into page", fontsize=7.4, color=GREY)

    # DH table inset
    tab = [["J", "$a$ (mm)", "$\\alpha$", "$d$ (mm)", "$\\theta$"],
           ["1", "0", "+90°", "160", "$q_1$"],
           ["2", "200", "0", "0", "$q_2$+90°"],
           ["3", "0", "+90°", "0", "$q_3$"],
           ["4", "0", "−90°", "200", "$q_4$"],
           ["5", "0", "+90°", "0", "$q_5$"],
           ["6", "0", "0", "60", "$q_6$"]]
    t = ax.table(cellText=tab, bbox=[0.6, 0.11, 0.4, 0.45], cellLoc="center",
                 colWidths=[0.12, 0.2, 0.18, 0.2, 0.3])
    t.auto_set_font_size(False)
    t.set_fontsize(7.4)
    for (r, c), cell in t.get_celld().items():
        cell.set_linewidth(0.5)
        cell.set_edgecolor(GREY)
        if r == 0:
            cell.set_facecolor("#E8EDF3")
    save(fig, "13", "fig-13-2-dh-frames")


# ----------------------------------------------------------------------------
# Figure 13.3 — joint vs Cartesian transfer (Listing 13.2)
# ----------------------------------------------------------------------------
def fig_13_3():
    A, B, T_move = np.array([0.300, -0.100, 0.150]), np.array([0.150, 0.250, 0.150]), 1.0
    seed = np.radians([0, -45, -45, 0, -90, 0])
    qA, _, _ = ik(tool_down(A), seed)
    qB, _, _ = ik(tool_down(B), qA)
    qB = qA + (qB - qA + np.pi) % (2 * np.pi) - np.pi
    t = np.linspace(0.0, T_move, 201)
    tau = t / T_move
    s = 10 * tau ** 3 - 15 * tau ** 4 + 6 * tau ** 5
    sd = (30 * tau ** 2 - 60 * tau ** 3 + 30 * tau ** 4) / T_move
    pj = np.array([fk(qA + si * (qB - qA))[:3, 3] for si in s])
    u = (B - A) / np.linalg.norm(B - A)
    devv = (pj - A) - np.outer((pj - A) @ u, u)
    dev = np.linalg.norm(devv, axis=1)
    q, Q = qA.copy(), []
    for si in s:
        q, _, _ = ik(tool_down(A + si * (B - A)), q)
        Q.append(q)
    qd = np.degrees(np.abs(np.gradient(np.array(Q), t, axis=0)))
    qdj = np.degrees(np.abs(np.outer(sd, qB - qA)))

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.8, 3.9), gridspec_kw=dict(width_ratios=[1, 1.25]))
    a1.plot([A[0], B[0]], [A[1], B[1]], ls="--", color=INK, lw=1.3)
    a1.plot(pj[:, 0], pj[:, 1], color=BLUE, lw=2)
    k = int(np.argmax(dev))
    pl = pj[k] - devv[k]
    a1.annotate("", xy=pj[k][:2], xytext=pl[:2],
                arrowprops=dict(arrowstyle="<|-|>", color=ORANGE, lw=1.1, mutation_scale=8,
                                shrinkA=0, shrinkB=0))
    a1.text((pj[k][0] + pl[0]) / 2 + 0.012, (pj[k][1] + pl[1]) / 2 - 0.03,
            f"{dev.max() * 1e3:.1f} mm", fontsize=8, color=ORANGE, ha="center")
    # decapper: 40 mm circle, centre 50 mm from the line on the side the joint move bulges to
    nrm = devv[k][:2] / np.linalg.norm(devv[k][:2])
    cdec = A[:2] + 0.30 * (B[:2] - A[:2]) + 0.050 * nrm
    a1.add_patch(Circle(cdec, 0.020, fc=tint(PINK, "40"), ec=PINK, lw=1.2))
    a1.annotate("decapper\n(Ø 40 mm)", xy=cdec - np.array([0.016, 0.012]), xytext=(0.085, -0.055),
                fontsize=7.5, color=PINK, ha="center", va="center",
                arrowprops=dict(arrowstyle="-", color=PINK, lw=0.8))
    a1.plot(0, 0, "s", color=INK, ms=7)
    a1.text(0.012, -0.018, "base (J1)", fontsize=8)
    a1.plot(*A[:2], "o", color=INK, ms=5)
    a1.plot(*B[:2], "o", color=INK, ms=5)
    a1.text(A[0] - 0.015, A[1], "A rack slot\n(0.300, −0.100)", fontsize=7.5,
            ha="right", va="center")
    a1.text(B[0] + 0.01, B[1] + 0.012, "B centrifuge\n(0.150, 0.250)", fontsize=7.5,
            ha="left", va="bottom")
    a1.text(0.17, 0.12, "Cartesian", fontsize=8, rotation=-67, ha="center")
    a1.text(0.318, 0.16, "joint\nmove", fontsize=8, color=BLUE, ha="left")
    a1.set_xlim(0, 0.35)
    a1.set_ylim(-0.15, 0.30)
    a1.set_aspect("equal")
    a1.set_xlabel("x (m)")
    a1.set_ylabel("y (m)")
    a1.set_title("TCP path, top view (z = 150 mm)", fontsize=9.5)

    a2.plot(t, qd[:, 0], color=RED, lw=2, label="Cartesian J1")
    a2.plot(t, qd[:, 5], color=PINK, lw=1.2, ls="--", label="Cartesian J6")
    a2.plot(t, qd[:, 2], color=GREEN, lw=1.6, label="Cartesian J3")
    a2.plot(t, qd[:, 1], color=ORANGE, lw=1.6, label="Cartesian J2")
    a2.plot(t, qdj[:, 0], color=BLUE, lw=2, label="joint move J1")
    a2.axhline(135, color=RED, lw=1.0, ls=":")
    a2.text(0.99, 131, "J1, J6 limit\n135 °/s", fontsize=7.5, color=RED, va="top", ha="right")
    for v, c, i in [(qd[:, 0].max(), RED, 0), (qd[:, 2].max(), GREEN, 2),
                    (qd[:, 1].max(), ORANGE, 1), (qdj[:, 0].max(), BLUE, None)]:
        arr = qd[:, i] if i is not None else qdj[:, 0]
        tk = t[np.argmax(arr)]
        a2.text(tk - (0.035 if i == 2 else 0), v + 2, f"{v:.0f}", fontsize=7.5, color=c,
                va="bottom", ha="center")
    a2.set_xlim(0, 1.0)
    a2.set_ylim(0, 200)
    a2.set_xlabel("time (s)")
    a2.set_ylabel("joint speed (°/s)")
    a2.set_title("Joint speeds, T = 1.0 s", fontsize=9.5)
    a2.legend(fontsize=7.2, loc="upper right", ncol=1, handlelength=1.8, bbox_to_anchor=(1.02, 1.02))
    fig.tight_layout(w_pad=1.2)
    save(fig, "13", "fig-13-3-joint-vs-cartesian")


# ----------------------------------------------------------------------------
# Figure 13.4 — workspace section
# ----------------------------------------------------------------------------
def fig_13_4():
    fig, ax = new_fig(6.4, 4.6)
    sh = np.array([0.0, 0.16])
    xs = np.linspace(0, 0.5, 801)
    ys = np.linspace(-0.10, 0.65, 941)
    X, Y = np.meshgrid(xs, ys)
    r_reach = np.hypot(X - sh[0], Y - sh[1])
    reach = (r_reach <= 0.46) & (r_reach >= 0.077) & (Y >= 0)
    r_w = np.hypot(X, Y - (sh[1] - 0.06))
    dext = (r_w <= 0.399) & (r_w >= 0.137) & (Y >= 0)
    ax.contourf(X, Y, reach.astype(float), levels=[0.5, 1.5], colors=["#DADADA"])
    ax.contourf(X, Y, dext.astype(float), levels=[0.5, 1.5], colors=["#8FA7BF"])
    # bench and keep-out
    ax.axhspan(-0.10, 0.0, color="#EDE7DC", zorder=0)
    ax.axhline(0, color=INK, lw=1.4)
    ax.fill_between([0, 0.5], 0, 0.02, facecolor="none", edgecolor=RED, hatch="////", lw=0)
    ax.text(0.01, -0.012, "bench keep-out (< 20 mm)", fontsize=7.5, color=RED, ha="left",
            va="top")
    ax.text(0.01, -0.06, "bench", fontsize=7.5, color=GREY, va="top")
    # circles and lines
    th = np.linspace(-np.pi / 2, np.pi / 2, 300)
    ax.plot(sh[0] + 0.46 * np.cos(th), sh[1] + 0.46 * np.sin(th), ls="--", color=INK, lw=1.0)
    ax.text(0.405, 0.45, "catalogue\nreach 0.46 m", fontsize=7.6, ha="left")
    ax.axvline(0.397, ls="--", color=BLUE, lw=1.1, ymin=0.0)
    ax.text(0.39, -0.045, "dexterous reach at\n60 mm height: 0.397 m", fontsize=7.4,
            color=BLUE, ha="right", va="top")
    ax.plot(*sh, "o", color=INK, ms=6)
    ax.text(0.012, 0.172, "shoulder (J2)", fontsize=7.8)
    ax.plot([0, 0], [0, 0.16], color=INK, lw=3)
    # fixtures
    pts = [((0.316, 0.06), "rack far slot", (-0.012, -0.018), "right"),
           ((0.29, 0.10), "centrifuge slot", (-0.012, 0.012), "right"),
           ((0.25, 0.15), "decapper", (-0.012, 0.01), "right")]
    for (p, lab, off, ha) in pts:
        ax.plot(*p, "o", ms=6, mfc=ORANGE, mec=INK, zorder=5)
        ax.text(p[0] + off[0], p[1] + off[1], lab, fontsize=7.8, ha=ha, va="center", zorder=5)
    ax.text(0.015, 0.565, "reachable (any orientation)", fontsize=7.6, ha="left", va="center",
            color=INK)
    ax.text(0.20, 0.30, "tool-down (dexterous)", fontsize=8, ha="center", color="white",
            weight="bold")
    ax.set_xlim(0, 0.50)
    ax.set_ylim(-0.10, 0.65)
    ax.set_aspect("equal")
    ax.set_xlabel("horizontal distance from J1 axis (m)")
    ax.set_ylabel("height above bench (m)")
    save(fig, "13", "fig-13-4-workspace-section")


# ----------------------------------------------------------------------------
# Figure 13.5 — shoulder torque over the sizing cycle (Listing 13.3)
# ----------------------------------------------------------------------------
def fig_13_5():
    g = 9.81
    parts = {"upper link": (0.35, 0.10), "elbow module": (0.55, 0.20),
             "forearm": (0.25, 0.30), "wrist modules": (0.60, 0.40),
             "gripper": (0.20, 0.43), "payload": (0.50, 0.46)}
    T_g = sum(m * r * g for m, r in parts.values())
    J_L = sum(m * r * r for m, r in parts.values())
    n, J_m = 100, 4.8e-6
    t_a = 1.0 / 3
    w_max = (np.pi / 2) / (1.0 - t_a)
    T_acc = (J_L + J_m * n ** 2) * w_max / t_a
    T_g, T_acc = round(T_g, 2), round(T_acc, 2)   # values as printed by Listing 13.3
    lv = [T_g + T_acc, T_g, T_g - T_acc]
    edges = [0, t_a, 2 * t_a, 1.0, 2.0]
    hold = lv + [T_g]
    brake = lv + [0.0]
    rms_h = np.sqrt((sum(v * v for v in lv) * t_a + T_g ** 2) / 2.0)
    rms_b = np.sqrt(sum(v * v for v in lv) * t_a / 2.0)

    fig, ax = new_fig(6.4, 3.9)
    ax.stairs(hold, edges, color=BLUE, lw=2, baseline=None, label="motor holding in dwell")
    ax.stairs(brake[3:], edges[3:], color=GREEN, lw=2, ls="--", baseline=None,
              label="brake engaged in dwell")
    ax.plot([1.0, 1.0], [0, T_g], color=GREEN, lw=2, ls="--")
    ax.axhline(rms_h, color=BLUE, lw=1.0, ls="-.")
    ax.axhline(rms_b, color=GREEN, lw=1.0, ls="-.")
    ax.axhline(8.75, color=GREY, lw=1.0)
    ax.axhline(21.0, color=GREY, lw=1.0)
    ax.axhline(6.0, color=RED, lw=1.3, ls="--")
    ax.text(1.98, rms_h + 0.12, f"RMS {rms_h:.2f} N m (holding)", fontsize=7.6, color=BLUE,
            ha="right", va="bottom")
    ax.text(1.98, rms_b - 0.12, f"RMS {rms_b:.2f} N m (brake)", fontsize=7.6, color=GREEN,
            ha="right", va="top")
    ax.text(1.98, 8.75 + 0.12, "42 mm motor cont. 0.125 × 100 × 0.70 = 8.75 N m",
            fontsize=7.6, color=GREY, ha="right", va="bottom")
    ax.text(1.98, 6.0 + 0.1, "first prototype capacity ≈ 6 N m", fontsize=7.6, color=RED,
            ha="right", va="bottom")
    ax.text(1.98, 11.85, "57 mm motor cont. 21.0 N m (off scale) ↑", fontsize=7.6,
            color=GREY, ha="right", va="top")
    for x0, x1, v, lab in [(0, t_a, lv[0], "accelerate"), (t_a, 2 * t_a, lv[1], "cruise"),
                           (2 * t_a, 1.0, lv[2], "decelerate")]:
        below = lab == "decelerate"
        ax.text((x0 + x1) / 2, v - 0.15 if below else v + 0.15, f"{lab}\n{v:.2f}", fontsize=7.6,
                ha="center", va="top" if below else "bottom")
    ax.text(1.5, T_g - 0.15, f"dwell, gravity {T_g:.2f}", fontsize=7.6, ha="center",
            va="top", color=BLUE)
    ax.set_xlim(0, 2.0)
    ax.set_ylim(0, 12)
    ax.set_xlabel("time (s)")
    ax.set_ylabel("J2 output torque (N m)")
    ax.legend(fontsize=7.6, loc="lower left", bbox_to_anchor=(0.0, 0.0))
    save(fig, "13", "fig-13-5-shoulder-torque-cycle")


if __name__ == "__main__":
    fig_13_1()
    fig_13_2()
    fig_13_3()
    fig_13_4()
    fig_13_5()
