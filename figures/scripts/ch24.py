"""Figures for Chapter 24 — Electric Vehicles.

Run from the repository root:  python figures/scripts/ch24.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch  # noqa: E402

from figstyle import COLORS, INK, save, schematic, new_fig  # noqa: E402

BLUE, ORANGE, GREEN, PINK, YELLOW, SKY = COLORS[:6]
RED = "#C62828"
GREY = "#777777"
HV = "#B03A2E"

# Van parameters (Sections 24.2-24.3)
M_TEST, CRR, CDA, RHO, ETA_D, KM = 3000.0, 0.009, 1.296, 1.20, 0.88, 1.05
G_RATIO, R_TYRE, ETA_GB = 11.0, 0.36, 0.97


def line(ax, pts, color=INK, lw=1.2, ls="-", arrow_end=False, z=2):
    xs, ys = zip(*pts)
    if not arrow_end:
        ax.plot(xs, ys, color=color, lw=lw, ls=ls, solid_capstyle="butt", zorder=z)
        return
    if len(pts) > 2:
        ax.plot(xs[:-1], ys[:-1], color=color, lw=lw, ls=ls, zorder=z)
    ax.annotate("", xy=pts[-1], xytext=pts[-2],
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, ls=ls, shrinkA=0,
                                shrinkB=0, mutation_scale=9), zorder=z)


def rbox(ax, x, y, w, h, text="", fc="#EEF3F8", ec=INK, fs=7.0, lw=1.0, z=3, weight="normal"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.1",
                                fc=fc, ec=ec, lw=lw, zorder=z))
    if text:
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=INK,
                zorder=z + 0.5, weight=weight, linespacing=1.15)


# ----------------------------------------------------------------------------
# Drive-cycle model (the listing of Section 24.2)
# ----------------------------------------------------------------------------
def cycle(dt=0.1):
    legs = [(40, 300, 30)] * 8 + [(60, 1000, 20)] * 3 + [(90, 3000, 10)]
    v, out = 0.0, []
    for vk, cruise, dwell in legs:
        vt = vk / 3.6
        while v < vt:
            v = min(vt, v + 1.0 * dt)
            out.append(v)
        for _ in range(int(cruise / vt / dt)):
            out.append(vt)
        while v > 0:
            v = max(0.0, v - 1.2 * dt)
            out.append(v)
        out += [0.0] * int(dwell / dt)
    return np.array(out)


def powers(v, dt=0.1, m=M_TEST, crr=CRR, CdA=CDA, rho=RHO, eta_d=ETA_D, p_chg_max=100e3,
           p_aux=0.8e3):
    a = np.gradient(v, dt)
    f_wheel = KM * m * a + m * 9.81 * crr + 0.5 * rho * CdA * v ** 2
    p_wheel = f_wheel * v
    p_drive = np.where(p_wheel > 0, p_wheel / eta_d, p_wheel * eta_d)
    regen_ok = v > 5 / 3.6
    p_drive = np.where(p_drive < 0, np.where(regen_ok, np.maximum(p_drive, -p_chg_max), 0.0),
                       p_drive)
    return f_wheel, p_wheel, p_drive, p_drive + p_aux


COLD = dict(crr=0.0104, rho=1.34, p_chg_max=8e3, p_aux=5.3e3)


# ----------------------------------------------------------------------------
# Figure 24.1 — architecture
# ----------------------------------------------------------------------------
def fig_24_1():
    fig, ax = schematic(6.8, 5.6, xlim=(0, 17), ylim=(0, 14))
    LV = ORANGE
    # pack
    ax.add_patch(FancyBboxPatch((0.2, 5.0), 4.2, 8.0, boxstyle="round,pad=0,rounding_size=0.25",
                                fc="#F6EEEC", ec=HV, lw=1.4, zorder=1))
    ax.text(2.3, 12.85, "Traction battery\n120s LFP, 200 Ah\n384 V nom., 300-438 V", fontsize=7.0,
            ha="center", va="top", weight="bold", zorder=2)
    rbox(ax, 0.45, 6.4, 1.55, 4.5, "120 cells\nin series\n\n76.8 kWh\n(72 usable)", fc="#E6F4EC",
         fs=6.6)
    rbox(ax, 0.45, 5.25, 1.55, 0.9, "BMS", fc="#DCE8F5", fs=7.0)
    comps = [("Fuse 400 A", 10.25), ("K+ main", 9.25), ("pre-charge\nK + 50 Ω", 8.05),
             ("current\nsensor", 6.9), ("K− main", 5.85)]
    for txt, y in comps:
        rbox(ax, 2.3, y, 1.85, 0.8 if "\n" not in txt else 0.95, txt, fc="white", ec=HV, fs=6.3)
    line(ax, [(2.0, 10.65), (2.3, 10.65)], color=HV, lw=1.4)
    line(ax, [(3.22, 10.25), (3.22, 10.05)], color=HV, lw=1.4)
    line(ax, [(2.0, 6.25), (2.3, 6.25)], color=HV, lw=1.4)
    # HV bus
    yb0, yb1 = 4.6, 11.6
    line(ax, [(4.4, 8.5), (5.3, 8.5)], color=HV, lw=3.2)
    line(ax, [(5.3, yb0), (5.3, yb1)], color=HV, lw=3.2)

    rows = [11.6, 10.2, 8.8, 7.4, 6.0, 4.6]
    h = 1.0
    for y in rows:
        line(ax, [(5.3, y), (6.3, y)], color=HV, lw=2.4)
    # row 1: traction chain
    rbox(ax, 6.3, rows[0] - h / 2, 2.6, h, "Traction inverter\nSiC 750 V, 800 µF", fc="#FBE3D6",
         fs=6.6)
    line(ax, [(8.9, rows[0]), (9.5, rows[0])], color=HV, lw=2.4)
    rbox(ax, 9.5, rows[0] - h / 2, 2.2, h, "PMSM\n150 kW peak", fc="#FBE3D6", fs=6.8)
    line(ax, [(11.7, rows[0]), (12.3, rows[0])], color=GREY, lw=3.0)
    rbox(ax, 12.3, rows[0] - h / 2, 2.0, h, "Gearbox\n11:1", fc="#EFEFEF", fs=6.8)
    line(ax, [(14.3, rows[0]), (14.9, rows[0])], color=GREY, lw=3.0)
    rbox(ax, 14.9, rows[0] - h / 2, 1.9, h, "Rear axle", fc="#EFEFEF", fs=6.8)
    # row 2: DC-DC and 14 V
    rbox(ax, 6.3, rows[1] - h / 2, 2.6, h, "DC-DC (LDC)\n2.5 kW", fc="#FBE3D6", fs=6.8)
    line(ax, [(8.9, rows[1]), (9.5, rows[1])], color=LV, lw=2.2)
    rbox(ax, 9.5, rows[1] - h / 2, 7.3, h,
         "14 V network: 12 V auxiliary battery · lights · EPS\nbrake booster · ECUs", fc="#FFF4D6",
         ec=LV, fs=6.3)
    # rows 3-6
    rbox(ax, 6.3, rows[2] - h / 2, 2.6, h, "E-compressor", fc="#FBE3D6", fs=6.8)
    rbox(ax, 6.3, rows[3] - h / 2, 2.6, h, "PTC heater 5 kW", fc="#FBE3D6", fs=6.8)
    rbox(ax, 6.3, rows[4] - h / 2, 2.6, h, "On-board\ncharger 11 kW", fc="#FBE3D6", fs=6.8)
    line(ax, [(9.5, rows[4]), (8.9, rows[4])], color=HV, lw=2.0, arrow_end=True)
    rbox(ax, 9.5, rows[4] - h / 2, 2.6, h, "Type 2 AC inlet", fc="white", fs=6.8)
    rbox(ax, 6.3, rows[5] - h / 2, 2.6, h, "DC charge\ncontactors", fc="#FBE3D6", fs=6.8)
    line(ax, [(9.5, rows[5]), (8.9, rows[5])], color=HV, lw=2.0, arrow_end=True)
    rbox(ax, 9.5, rows[5] - h / 2, 2.6, h, "CCS2 DC inlet", fc="white", fs=6.8)
    # isolation monitor
    rbox(ax, 9.5, rows[2] - h / 2, 2.6, h, "Isolation monitor\n≥ 100 Ω/V", fc="white", fs=6.6)
    line(ax, [(9.5, rows[2]), (9.2, rows[2]), (9.2, 8.05), (5.3, 8.05)], color=INK, lw=0.9)
    # HVIL loop
    xl, xr = 4.75, 5.85
    ax.add_patch(Rectangle((xl, 4.0), xr - xl, 8.25, fc="none", ec=YELLOW, lw=1.3, ls=(0, (3, 2)),
                           zorder=4))
    for y in rows:
        ax.add_patch(Rectangle((xr - 0.12, y - 0.12), 0.24, 0.24, fc="white", ec=INK, lw=0.8, zorder=5))
    ax.add_patch(Rectangle((xl - 0.12, 8.5 - 0.12), 0.24, 0.24, fc="white", ec=INK, lw=0.8, zorder=5))
    ax.text(xl + (xr - xl) / 2, 12.35, "HVIL loop\n(dashed)", fontsize=6.4, color="#A06F00",
            ha="center", va="bottom")
    # CAN
    names = ["Inverter", "VCU", "BMS", "Brake ECU", "Thermal\ncontroller", "DC-DC", "OBC"]
    bw, pitch, x0, yn = 1.95, 2.35, 0.35, 1.45
    cx = [x0 + k * pitch + bw / 2 for k in range(7)]
    line(ax, [(0.2, 0.75), (16.8, 0.75)], color=BLUE, lw=2.0)
    ax.text(16.8, 0.6, "powertrain CAN 500 kbit/s", fontsize=6.6, color=BLUE, ha="right", va="top")
    for k, nm in enumerate(names):
        rbox(ax, x0 + k * pitch, yn, bw, 0.85, nm, fc="#DCE8F5" if nm == "VCU" else "white", fs=6.5,
             weight="bold" if nm == "VCU" else "normal")
        line(ax, [(cx[k], yn), (cx[k], 0.75)], color=BLUE, lw=1.2)
    ytop = yn + 0.85

    def msg(x_src, x_dst, lane_y, text, tx):
        line(ax, [(x_src, ytop), (x_src, lane_y), (x_dst, lane_y), (x_dst, ytop)], color=BLUE,
             lw=0.9, arrow_end=True, z=4)
        ax.text(tx, lane_y + 0.04, text, fontsize=6.1, color=BLUE, ha="center", va="bottom",
                zorder=6)

    msg(cx[1] - 0.65, cx[0], 2.65, "torque request", (cx[0] + cx[1] - 0.65) / 2)
    msg(cx[2], cx[1] + 0.65, 2.65, "power limits", (cx[2] + cx[1] + 0.65) / 2)
    msg(cx[3], cx[1] + 0.2, 3.1, "regen request", (cx[3] + cx[2]) / 2 + 0.4)
    msg(cx[4], cx[1] - 0.25, 3.55, "coolant temperature", (cx[4] + cx[3]) / 2 + 0.3)
    # legend
    lx, ly = 12.6, 7.4
    for k, (c, lw, lab) in enumerate(((HV, 3.0, "HV energy"), (LV, 2.2, "14 V energy"),
                                      (BLUE, 1.5, "CAN"), (GREY, 3.0, "mechanical"))):
        yy = ly + 0.5 - k * 0.55
        ax.plot([lx, lx + 0.8], [yy, yy], color=c, lw=lw)
        ax.text(lx + 0.95, yy, lab, fontsize=6.6, va="center")
    yy = ly + 0.5 - 4 * 0.55
    ax.plot([lx, lx + 0.8], [yy, yy], color=YELLOW, lw=1.3, ls=(0, (3, 2)))
    ax.text(lx + 0.95, yy, "HVIL", fontsize=6.6, va="center")
    save(fig, "24", "fig-24-1-ev-architecture")


# ----------------------------------------------------------------------------
# Figure 24.2 — urban loop and battery power
# ----------------------------------------------------------------------------
def fig_24_2():
    dt = 0.1
    v = cycle(dt)
    t = np.arange(v.size) * dt
    _, _, _, pw = powers(v, dt)
    _, _, pdc, pc = powers(v, dt, **COLD)
    dist = v.sum() * dt / 1000
    e_w = pw.sum() * dt / 3.6e6
    e_c = pc.sum() * dt / 3.6e6
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.6, 4.8), sharex=True,
                                 gridspec_kw=dict(height_ratios=[1, 1.5], hspace=0.1))
    a1.plot(t, v * 3.6, color=INK, lw=1.3)
    a1.set_ylim(0, 95)
    a1.set_ylabel("Speed (km/h)")
    a1.text(10, 86, f"loop {dist:.2f} km in {t[-1] / 60:.1f} min, mean "
            f"{dist / (t[-1] / 3600):.1f} km/h: 8 × 40, 3 × 60, 1 × 90 km/h", fontsize=7.6,
            va="top")
    a2.axhline(0, color=GREY, lw=0.6)
    a2.plot(t, pw / 1e3, color=BLUE, lw=1.0, label=f"20 °C: {100 * e_w / dist:.1f} kWh/100 km")
    a2.plot(t, pc / 1e3, color=RED, lw=1.0, ls="--",
            label=f"−10 °C: {100 * e_c / dist:.1f} kWh/100 km")
    a2.set_ylim(-70, 120)
    a2.set_ylabel("Battery power (kW)")
    a2.set_xlabel("Time (s)")
    a2.set_xlim(0, t[-1])
    k = np.argmax(pw)
    a2.annotate(f"{pw[k] / 1e3:.0f} kW, accelerating to 90 km/h", xy=(t[k], pw[k] / 1e3),
                xytext=(560, 100), fontsize=7.2,
                arrowprops=dict(arrowstyle="-", color=INK, lw=0.6))
    k = np.argmin(pw)
    a2.annotate(f"regen {pw[k] / 1e3:.0f} kW".replace("-", "−"), xy=(t[k], pw[k] / 1e3), xytext=(760, -60),
                fontsize=7.2, arrowprops=dict(arrowstyle="-", color=INK, lw=0.6))
    a2.annotate("cold: regen capped at 8 kW at the drive;\nbattery net "
                f"{pc.min() / 1e3:.1f} kW with the 5.3 kW auxiliary load".replace("-", "−"),
                xy=(t[np.argmin(pc)], pc.min() / 1e3), xytext=(140, -58), fontsize=7.0,
                color=RED, arrowprops=dict(arrowstyle="-", color=RED, lw=0.6))
    a2.legend(fontsize=7.4, loc="upper left")
    save(fig, "24", "fig-24-2-urban-loop-power")
    return dist, e_w / dist * 100, e_c / dist * 100, pw.max(), pw.min(), pc.min()


# ----------------------------------------------------------------------------
# Figure 24.3 — torque-speed envelope
# ----------------------------------------------------------------------------
def fig_24_3():
    n = np.linspace(1, 12000, 2000)
    w = n * 2 * np.pi / 60
    T_pk = np.minimum(310, 150e3 / w)
    T_ct = np.minimum(155, 75e3 / w)
    n_base = 150e3 / 310 * 60 / (2 * np.pi)
    fig, ax = new_fig(6.6, 4.3)
    ax.axvspan(9726, 12000, color=GREY, alpha=0.12, lw=0)
    ax.text(10863, 240, "speed\nmargin\n19 %", ha="center", va="bottom", fontsize=7.2,
            color=GREY)
    ax.plot(n, T_pk, color=RED, lw=2, label="peak: 310 N·m / 150 kW")
    ax.plot(n, T_ct, color=BLUE, lw=2, label="continuous: 155 N·m / 75 kW")
    ax.plot(n, -T_pk, color=RED, lw=1.0, ls=":", label="peak envelope, generating")
    ax.axhline(0, color=GREY, lw=0.6)
    ax.axvline(n_base, color=GREY, lw=0.6, ls=":")
    ax.text(n_base + 80, 322, f"base speed {n_base:,.0f} rpm", fontsize=7.2, color=GREY)
    # operating cloud from the urban loop
    dt = 0.1
    v = cycle(dt)
    f_w, _, _, _ = powers(v, dt)
    mov = v > 0.05
    nm = (v / R_TYRE * G_RATIO * 60 / (2 * np.pi))[mov]
    fw = f_w[mov]
    Tm = np.where(fw > 0, fw * R_TYRE / (G_RATIO * ETA_GB), fw * R_TYRE * ETA_GB / G_RATIO)
    ax.scatter(nm[::10], Tm[::10], s=3, color=GREEN, alpha=0.35, lw=0,
               label="urban-loop operating points")
    # sizing points
    F_grade = 3500 * 9.81 * (np.sin(np.arctan(0.25)) + CRR * np.cos(np.arctan(0.25)))
    T_grade = F_grade * R_TYRE / (G_RATIO * ETA_GB)
    ax.plot(150, T_grade, "s", color=INK, ms=6, zorder=5)
    ax.annotate(f"R3: 25 % grade start at GVW\n{T_grade:.0f} N·m", xy=(150, T_grade),
                xytext=(900, 205), fontsize=7.4, arrowprops=dict(arrowstyle="-", color=INK, lw=0.6))
    v120 = 120 / 3.6
    n120 = v120 / R_TYRE * G_RATIO * 60 / (2 * np.pi)
    P120 = (M_TEST * 9.81 * CRR + 0.5 * RHO * CDA * v120 ** 2) * v120 / ETA_GB
    T120 = P120 / (n120 * 2 * np.pi / 60)
    ax.plot(n120, T120, "D", color=INK, ms=5, zorder=5)
    ax.annotate(f"R4: 120 km/h cruise\n{n120:,.0f} rpm, {P120 / 1e3:.1f} kW, {T120:.0f} N·m",
                xy=(n120, T120), xytext=(7300, 175), fontsize=7.4,
                arrowprops=dict(arrowstyle="-", color=INK, lw=0.6))
    v60 = 60 / 3.6
    n60 = v60 / R_TYRE * G_RATIO * 60 / (2 * np.pi)
    T60 = -KM * M_TEST * 1.2 * R_TYRE * ETA_GB / G_RATIO
    ax.plot(n60, T60, "v", color=PINK, ms=7, zorder=5)
    ax.annotate(f"1.2 m/s² regen at 60 km/h\n−{-T60:.0f} N·m at {n60:,.0f} rpm", xy=(n60, T60),
                xytext=(1500, -215), fontsize=7.4, color=PINK,
                arrowprops=dict(arrowstyle="-", color=PINK, lw=0.6))
    ax.set_xlim(0, 12000)
    ax.set_ylim(-320, 360)
    ax.set_xlabel("Motor speed (rpm)")
    ax.set_ylabel("Motor torque (N·m)")
    ax.legend(fontsize=7.2, loc="center right", bbox_to_anchor=(1.0, 0.4))
    top = ax.secondary_xaxis("top", functions=(
        lambda x: x * 2 * np.pi / 60 / G_RATIO * R_TYRE * 3.6,
        lambda kmh: kmh / 3.6 / R_TYRE * G_RATIO * 60 / (2 * np.pi)))
    top.set_xlabel("Vehicle speed (km/h), gear ratio 11.0, tyre radius 0.36 m", fontsize=8.5)
    save(fig, "24", "fig-24-3-torque-speed-envelope")
    return T_grade, n120, P120, T120, n60, T60


# ----------------------------------------------------------------------------
# Figure 24.4 — regen demand versus charge-power limit
# ----------------------------------------------------------------------------
def fig_24_4():
    vk = np.linspace(0, 90, 901)
    F = KM * M_TEST * 1.2
    P = np.where(vk > 5, ETA_D * F * vk / 3.6, 0) / 1e3
    fig, ax = new_fig(6.4, 4.0)
    ax.plot(vk, P, color=INK, lw=2, label="regen demand at battery, 0.88 × 3.78 kN × v")
    lims = [(100, "pack 25 °C: 100 kW", GREEN), (30, "pack 5-10 °C: 30 kW", ORANGE),
            (8, "pack −10 °C: 8 kW", BLUE)]
    for lim, lab, c in lims:
        ax.axhline(lim, color=c, lw=1.4, ls="--")
        ax.text(1, lim + 1.2, lab, color=c, fontsize=7.6, va="bottom")
    ax.fill_between(vk, np.minimum(P, 8), np.minimum(P, 30), color=BLUE, alpha=0.13, lw=0)
    ax.fill_between(vk, np.minimum(P, 30), P, color=ORANGE, alpha=0.16, lw=0)
    ax.text(76, 47, "friction brake\nwith 30 kW or 8 kW limit", fontsize=7.4, ha="center",
            color=INK)
    ax.text(76, 17, "friction brake\nwith 8 kW limit only", fontsize=7.4, ha="center", color=INK)
    P60 = ETA_D * F * 60 / 3.6 / 1e3
    ax.axvline(60, color=GREY, lw=0.7, ls=":")
    ax.plot(60, P60, "o", color=INK, ms=4)
    ax.annotate(f"60 km/h: demand {P60:.1f} kW\nrecovered: {8 / P60 * 100:.0f} % at −10 °C,\n"
                f"{30 / P60 * 100:.0f} % at 30 kW limit, 100 % warm", xy=(60, P60),
                xytext=(14, 62), fontsize=7.4, arrowprops=dict(arrowstyle="-", color=INK, lw=0.6))
    ax.text(88.5, ETA_D * F * 90 / 3.6 / 1e3 + 1, f"{ETA_D * F * 90 / 3.6 / 1e3:.0f} kW",
            ha="right", va="bottom", fontsize=7.4)
    ax.set_xlim(0, 90)
    ax.set_ylim(0, 105)
    ax.set_xlabel("Vehicle speed (km/h); regen off below 5 km/h")
    ax.set_ylabel("Power at battery (kW)")
    ax.legend(fontsize=7.4, loc="upper left", bbox_to_anchor=(0.0, 0.86))
    save(fig, "24", "fig-24-4-regen-acceptance")
    return P60


# ----------------------------------------------------------------------------
# Figure 24.5 — DC fast charge
# ----------------------------------------------------------------------------
def fig_24_5():
    E = 76.8
    s = np.linspace(0.10, 0.80, 7001)
    p25 = np.where(s <= 0.55, 115.0, 115.0 + (60.0 - 115.0) * (s - 0.55) / 0.25)
    p0 = np.full_like(s, 0.3 * 200 * 370 / 1e3)
    def cum(p):
        dtm = E * np.diff(s) / (0.5 * (p[1:] + p[:-1])) * 60
        return np.concatenate([[0], np.cumsum(dtm)])
    t25, t0 = cum(p25), cum(p0)
    fig, ax = new_fig(6.4, 4.0)
    ax.plot(s * 100, p25, color=BLUE, lw=2, label="power, pack 25 °C")
    ax.plot(s * 100, p0, color=RED, lw=2, label=f"power, pack 0 °C ({p0[0]:.1f} kW, 0.3C)")
    ax.set_ylim(0, 130)
    ax.set_xlim(10, 80)
    ax.set_xlabel("State of charge (%)")
    ax.set_ylabel("Charge power (kW)")
    ax2 = ax.twinx()
    ax2.spines["right"].set_visible(True)
    ax2.plot(s * 100, t25, color=BLUE, ls="--", lw=1.6, label="cumulative time, 25 °C")
    ax2.plot(s * 100, t0, color=RED, ls="--", lw=1.6, label="cumulative time, 0 °C")
    ax2.axhline(40, color=INK, ls=":", lw=1.2)
    ax2.text(11, 41, "R7: 10-80 % in ≤ 40 min", fontsize=7.6, va="bottom")
    ax2.set_ylim(0, 150)
    ax2.set_ylabel("Cumulative charging time (min)")
    ax2.text(79.5, t25[-1] + 2, f"{t25[-1]:.1f} min", color=BLUE, ha="right", va="bottom",
             fontsize=7.6)
    ax2.text(76.5, 148, f"{t0[-1]:.0f} min", color=RED, ha="right", va="top", fontsize=7.6)
    ax.text(40, 89, "preconditioning 25 min at 7 kW\n(2.9 kWh) moves the 0 °C case\n"
            "onto the 25 °C curve", fontsize=7.6, ha="center",
            bbox=dict(fc="white", ec=GREY, lw=0.6))
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, fontsize=7.2, loc="upper center", bbox_to_anchor=(0.5, -0.15),
              ncol=2)
    save(fig, "24", "fig-24-5-dc-charge-curve")
    return t25[-1], t0[-1]


# ----------------------------------------------------------------------------
# Figure 24.6 — depot load (the listing of Section 24.10)
# ----------------------------------------------------------------------------
def depot():
    N, P_EVSE, P_MIN, CAP = 20, 11.0, 4.16, 280.0
    dt = 1 / 60
    t = np.arange(18.0, 30.5, dt)
    building = 60 + 140 * np.clip((21 - t) / 3, 0, 1)
    arrive = np.linspace(18.0, 19.5, N)
    need = np.full(N, 62.1 / 0.94)

    def run(managed):
        left, site, done = need.copy(), [], np.full(N, np.nan)
        for k, tk in enumerate(t):
            active = (tk >= arrive) & (left > 0)
            p = np.where(active, P_EVSE, 0.0)
            if managed and active.any():
                share = (CAP - building[k]) / active.sum()
                p = np.where(active, np.clip(share, P_MIN, P_EVSE), 0.0)
            p = np.minimum(p, left / dt)
            left -= p * dt
            done[(left <= 1e-9) & np.isnan(done)] = tk
            site.append(building[k] + p.sum())
        return np.array(site), done

    return t, building, run(False), run(True)


def hhmm(h):
    h = h % 24
    return f"{int(h):02d}:{int(round((h % 1) * 60)) % 60:02d}"


def fig_24_6():
    t, building, (s_u, d_u), (s_m, d_m) = depot()
    fig, ax = new_fig(6.6, 4.0)
    ax.axvspan(30.0, 30.5, color=YELLOW, alpha=0.25, lw=0)
    ax.text(29.95, 200, "staggered pack\npreconditioning\n06:00-06:30", fontsize=7.2,
            ha="right", va="center")
    ax.plot(t, building, color=GREY, lw=1.0, label="building load")
    ax.plot(t, s_u, color=RED, lw=1.6, label="uncontrolled, 11 kW per van")
    ax.plot(t, s_m, color=BLUE, lw=1.6, label="load-managed")
    ax.axhline(280, color=INK, ls="--", lw=1.0)
    ax.text(27.0, 283, "site cap 280 kW", fontsize=7.6, va="bottom")
    ax.text(23.7, 286, "21:00-00:00: both at 60 + 20 × 11 = 280 kW", fontsize=7.0, ha="center", va="bottom", color=GREY)
    k = np.argmax(s_u)
    ax.annotate(f"peak {s_u[k]:.0f} kW at {hhmm(t[k])}", xy=(t[k], s_u[k]),
                xytext=(t[k] + 0.6, 360), fontsize=7.6, color=RED,
                arrowprops=dict(arrowstyle="-", color=RED, lw=0.6))
    lu, lm = np.nanmax(d_u), np.nanmax(d_m)
    ax.annotate(f"last van full {hhmm(lu)}", xy=(lu, 60), xytext=(lu + 0.3, 140), fontsize=7.4,
                color=RED, arrowprops=dict(arrowstyle="-", color=RED, lw=0.6))
    ax.annotate(f"last van full {hhmm(lm)}", xy=(lm, 60), xytext=(lm + 0.6, 100), fontsize=7.4,
                color=BLUE, arrowprops=dict(arrowstyle="-", color=BLUE, lw=0.6))
    ticks = np.arange(18, 31, 2)
    ax.set_xticks(ticks)
    ax.set_xticklabels([hhmm(x) for x in ticks])
    ax.set_xlim(18, 30.5)
    ax.set_ylim(0, 380)
    ax.set_xlabel("Clock time")
    ax.set_ylabel("Site import power (kW)")
    ax.legend(fontsize=7.4, loc="center", bbox_to_anchor=(0.37, 0.5))
    save(fig, "24", "fig-24-6-depot-load")
    first_cap = t[np.argmax(s_m >= 279.9)]
    return s_u.max(), hhmm(t[np.argmax(s_u)]), hhmm(lu), s_m.max(), hhmm(lm), hhmm(first_cap)


if __name__ == "__main__":
    fig_24_1()
    print("24.2:", fig_24_2())
    print("24.3:", fig_24_3())
    print("24.4 P60:", fig_24_4())
    print("24.5:", fig_24_5())
    print("24.6:", fig_24_6())
