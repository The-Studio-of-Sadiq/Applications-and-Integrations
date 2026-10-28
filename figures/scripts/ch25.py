"""Figures for Chapter 25 — Microgrids and Hybrid Energy Systems.

Run from the repository root:  python figures/scripts/ch25.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

from figstyle import COLORS, INK, box, save, schematic, new_fig  # noqa: E402

BLUE, ORANGE, GREEN, PINK, YELLOW, SKY = COLORS[:6]
RED = "#C62828"
GREY = "#777777"


# ----------------------------------------------------------------------------
# Site model and dispatch of Section 25.4 (same equations as the chapter listings)
# ----------------------------------------------------------------------------
def profiles(seed=1):
    rng = np.random.default_rng(seed)
    h = np.arange(8760); hod, doy = h % 24, h // 24
    season = 1 + 0.15*np.cos(2*np.pi*(doy - 170)/365)
    load = (85 + 120*np.clip(np.sin(np.pi*(hod - 7)/13), 0, None)**0.8) * season
    load *= 1 + 0.06*rng.standard_normal(8760)
    clear = np.repeat(rng.uniform(0.35, 1.0, 365), 24)
    sun = np.clip(np.sin(np.pi*(hod - 6)/12), 0, None)
    pv = 400*0.82*sun**1.3*clear*(1 + 0.08*np.cos(2*np.pi*(doy - 80)/365))
    x = np.zeros((8760, 2))
    for k in range(1, 8760):
        x[k] = 0.9*x[k-1] + np.sqrt(0.19)*rng.standard_normal(2)
    u = np.hypot(x[:, 0], x[:, 1]) * 6.0/np.sqrt(np.pi/2)
    wind = 2*np.where((u >= 3) & (u < 25), np.minimum(50*(u**3 - 27)/(11**3 - 27), 50), 0)
    outage = np.zeros(8760, bool)
    for s in rng.choice(8760 - 24, 40, replace=False):
        outage[s:s + max(1, int(round(rng.exponential(3.0))))] = True
    return load, pv, wind, outage


def dispatch_log(load, pv, wind, outage, E=600.0, P=300.0, reserve=0.5, exp_lim=100.0, eta=0.95):
    """The chapter's ems.dispatch, logging every hourly flow (kW) and the SOC (fraction)."""
    n = len(load)
    log = {k: np.zeros(n) for k in ("dis", "ch", "imp", "exp", "curt", "gen", "soc")}
    soc, gen_on = 0.8*E, False
    for k in range(n):
        net = pv[k] + wind[k] - load[k]
        floor = (0.10 if outage[k] else reserve) * E
        if net >= 0:
            ch = min(net, P, (0.95*E - soc)/eta); soc += ch*eta; net -= ch
            e = 0.0 if outage[k] else min(net, exp_lim)
            log["ch"][k] = ch; log["exp"][k] = e; log["curt"][k] = net - e
            gen_on = False
        else:
            dis = min(-net, P, max(soc - floor, 0.0)*eta); soc -= dis/eta; net += dis
            log["dis"][k] = dis
            if not outage[k]:
                log["imp"][k] = -net; gen_on = False
            else:
                gen_on = (gen_on or soc < 0.25*E) and soc <= 0.60*E
                if gen_on or net < 0:
                    g = min(320.0, max(-net + min(P, (0.6*E - soc)/eta), 48.0))
                    c = max(g + net, 0.0)
                    soc += c*eta
                    log["gen"][k] = g; log["ch"][k] += c
        log["soc"][k] = soc/E
    return log


# ----------------------------------------------------------------------------
# Figure 25.1 — single-line diagram
# ----------------------------------------------------------------------------
def _cb(ax, x, y, s=0.22, color=INK):
    """Circuit-breaker symbol (small square) centred on (x, y)."""
    ax.add_patch(Rectangle((x - s/2, y - s/2), s, s, fc="white", ec=color, lw=1.2, zorder=3))


def fig_25_1():
    fig, ax = schematic(6.8, 5.0, xlim=(0, 17), ylim=(0, 12.5))
    # grid, feeder and transformer
    ax.text(5.0, 12.25, "11 kV rural feeder, 25 km, 50 mm² ACSR", ha="center", va="center", fontsize=8.5)
    ax.plot([5.0, 5.0], [12.0, 10.95], color=INK, lw=1.4)
    for yc in (10.7, 10.3):
        ax.add_patch(plt.Circle((5.0, yc), 0.28, fc="none", ec=INK, lw=1.2))
    ax.text(5.45, 10.5, "630 kVA, 11/0.4 kV\nDyn11, z = 6 %", ha="left", va="center", fontsize=8)
    ax.plot([5.0, 5.0], [10.02, 8.5], color=INK, lw=1.4)
    _cb(ax, 5.0, 9.2)
    ax.text(5.25, 9.3, "PCC ACB\n+ shunt trip", ha="left", va="bottom", fontsize=7.8)
    box(ax, 7.6, 8.85, 3.4, 0.8, "PCC relay\n27/59/81/ROCOF/25", fc="#FDECEC", fontsize=7.8)
    ax.plot([5.11, 7.6], [9.2, 9.2], color=RED, lw=0.9, ls=":")
    ax.text(6.35, 9.12, "trip", ha="center", va="top", fontsize=7, color=RED)
    ax.text(0.2, 10.55, "Busbar fault level:\n15.2 kA grid-connected\n≈ 0.65 kA island, battery\n"
            "≈ 2.4 kA island + gensets", ha="left", va="center", fontsize=7.3,
            bbox=dict(fc="#FFF8E1", ec=GREY, lw=0.6))
    # main busbar
    yb = 8.5
    ax.plot([0.4, 16.6], [yb, yb], color=INK, lw=4, solid_capstyle="butt")
    ax.text(0.4, yb + 0.25, "400 V main busbar", ha="left", va="bottom", fontsize=8.5, weight="bold")
    # feeders: (x, label, fc)
    feeders = [
        (1.4, "Critical board\n90 kW\ntheatres, ICU,\ncold chain,\nlighting", "#E6F4EA"),
        (4.2, "Non-critical\nboard\ncooling, laundry,\nkitchen; 55 kW\nchiller, soft start", "#F2F2F2"),
        (7.0, "Battery inverter\n300 kVA\ngrid-forming", "#E3F0FA"),
        (9.8, "PV inverters\n8 × 50 kW\n400 kWp\ngrid-following", "#FDF1DC"),
        (12.6, "Wind\n2 × 50 kW\nfull converters", "#E3F0FA"),
        (15.3, "Generators\n2 × 200 kVA\n(160 kW)\nparalleling ctrl", "#FDECEC"),
    ]
    bw, bh, ytop = 2.6, 2.0, 7.0
    for x, lab, fc in feeders:
        ax.plot([x, x], [yb, ytop], color=INK, lw=1.4)
        _cb(ax, x, 7.75)
        box(ax, x - bw/2, ytop - bh, bw, bh, lab, fc=fc, fontsize=7.3)
    ax.text(4.2 + 0.2, 7.75, "shed\ncontactor", ha="left", va="center", fontsize=7, color=RED)
    # battery under the PCS
    box(ax, 7.0 - 1.0, 3.55, 2.0, 0.9, "LFP battery\n600 kWh", fc="#D5EBF8", fontsize=7.8)
    ax.plot([7.0, 7.0], [ytop - bh, 4.45], color=INK, lw=1.4)
    # microgrid controller and comms (dashed)
    box(ax, 6.0, 0.5, 5.0, 1.1, "Microgrid controller (EMS)\nModbus TCP / IEC 61850", fc="#EFE6F5", fontsize=8.2)
    cm = dict(color=PINK, lw=0.9, ls="--")
    yc = 2.4
    ax.plot([4.2, 15.3], [yc, yc], **cm)
    ax.plot([8.5, 8.5], [1.6, yc], **cm)
    for x in (4.2, 9.8, 12.6, 15.3):
        ax.plot([x, x], [yc, ytop - bh], **cm)
    ax.plot([8.05, 8.05], [yc, ytop - bh], **cm)
    ax.plot([11.0, 16.85, 16.85, 11.0], [1.05, 1.05, 9.25, 9.25], **cm)
    ax.text(13.9, 9.32, "to PCC relay", ha="center", va="bottom", fontsize=7.2, color=PINK)
    ax.text(4.1, 3.6, "shed\ncommand", ha="right", va="center", fontsize=7.2, color=PINK)
    ax.text(11.3, 0.45, "dashed: communication\n(not used for fast functions)", ha="left", va="center",
            fontsize=7.2, color=PINK)
    save(fig, "25", "fig-25-1-hospital-microgrid-sld")


# ----------------------------------------------------------------------------
# Figure 25.2 — typical hot-season day
# ----------------------------------------------------------------------------
def fig_25_2():
    h = np.linspace(0, 24, 961)
    season = 1.15                          # day 170, hot season
    load = (85 + 120*np.clip(np.sin(np.pi*(h - 7)/13), 0, None)**0.8) * season
    pv = 400*0.82*np.clip(np.sin(np.pi*(h - 6)/12), 0, None)**1.3*1.0 * \
        (1 + 0.08*np.cos(2*np.pi*(170 - 80)/365))
    wind = 50 + 22*np.cos(2*np.pi*(h - 2)/24) + 8*np.sin(2*np.pi*h/5.3) + 5*np.sin(2*np.pi*h/2.1)
    ren = pv + wind
    fig, ax = new_fig(6.4, 3.9)
    ax.fill_between(h, 0, wind, color=SKY, alpha=0.55, lw=0, label="Wind (2 × 50 kW)")
    ax.fill_between(h, wind, ren, color=YELLOW, alpha=0.55, lw=0, label="PV (400 kWp), stacked on wind")
    ax.plot(h, load, color="black", lw=2.0, label="Hospital load")
    ax.axhline(90, color=GREEN, ls="--", lw=1.3)
    ax.text(0.3, 84, "critical load 90 kW", color=GREEN, fontsize=8.5, va="top")
    sur = ren > load
    ax.fill_between(h, load, ren, where=sur, color=GREEN, alpha=0.25, lw=0, hatch="///",
                    edgecolor=GREEN)
    t0, t1 = h[sur][0], h[sur][-1]
    ax.annotate(f"surplus {t0:.1f}–{t1:.1f} h:\ncharge battery,\nthen export ≤ 100 kW",
                xy=(12.0, 0.5*(np.interp(12, h, load) + np.interp(12, h, ren))),
                xytext=(14.6, 345), fontsize=8, ha="left", va="center",
                arrowprops=dict(arrowstyle="-", color=INK, lw=0.7))
    eve = (h > t1) & (h < 23) & (ren < load)
    ax.fill_between(h, ren, load, where=eve, color=GREY, alpha=0.25, lw=0)
    ax.annotate("deficit: battery,\nthen grid", xy=(19.5, 0.5*(np.interp(19.5, h, load) +
                np.interp(19.5, h, ren))), xytext=(20.0, 245), fontsize=8, ha="left",
                arrowprops=dict(arrowstyle="-", color=INK, lw=0.7))
    ax.set_xlim(0, 24); ax.set_ylim(0, 380)
    ax.set_xticks(range(0, 25, 3))
    ax.set_xlabel("Hour of day")
    ax.set_ylabel("Power (kW)")
    ax.legend(loc="upper left", fontsize=8)
    save(fig, "25", "fig-25-2-daily-profile")


# ----------------------------------------------------------------------------
# Figure 25.3 — one week of dispatch with the 13 h outage
# ----------------------------------------------------------------------------
def fig_25_3():
    load, pv, wind, outage = profiles()
    log = dispatch_log(load, pv, wind, outage)
    s0 = 1716 - 98                          # the 13 h outage of the synthetic year starts at hour 1716
    sl = slice(s0, s0 + 168)
    t = np.arange(168)
    L = load[sl]
    bnet = log["dis"][sl] - log["ch"][sl]          # net battery flow within each hour
    pos = [(pv[sl], ORANGE, "PV"), (wind[sl], BLUE, "Wind"), (bnet.clip(0), GREEN, "Battery discharge"),
           (log["imp"][sl], "#9E9E9E", "Grid import"), (log["gen"][sl], RED, "Generator")]
    neg = [((-bnet).clip(0), GREEN, "Battery charge"), (log["exp"][sl], "#9E9E9E", "Export"),
           (log["curt"][sl], YELLOW, "Curtailed")]
    o = outage[sl]
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.8, 5.0), sharex=True,
                                 gridspec_kw=dict(height_ratios=[1.9, 1]))
    base = np.zeros(168)
    for y, c, lab in pos:
        a1.fill_between(t, base, base + y, step="post", color=c, alpha=0.75, lw=0, label=lab)
        base = base + y
    base = np.zeros(168)
    for y, c, lab in neg:
        a1.fill_between(t, base, base - y, step="post", color=c, alpha=0.4, lw=0, hatch="///",
                        edgecolor=c, label=lab)
        base = base - y
    a1.step(t, L, where="post", color="black", lw=1.4, label="Load")
    d = np.diff(np.r_[0, o.astype(int), 0])
    runs = list(zip(np.where(d == 1)[0], np.where(d == -1)[0]))
    for a in (a1, a2):
        for r0, r1 in runs:
            a.axvspan(r0, r1, color=RED, alpha=0.09, lw=0)
    (r0, r1), (q0, q1) = runs[0], runs[1]
    a1.text(r0 - 1, 440, f"{r1-r0} h grid outage\n{r0}–{r1} h", ha="right", va="top", fontsize=8, color=RED)
    a1.text(q1 + 1, 440, f"{q1-q0} h outage\n{q0}–{q1} h", ha="left", va="top", fontsize=8, color=RED)
    g = (log["gen"][sl] > 0).astype(int)
    dg = np.diff(np.r_[0, g, 0])
    gruns = ", ".join(f"{a}–{b}" for a, b in zip(np.where(dg == 1)[0], np.where(dg == -1)[0]))
    a1.text(126, -330, "generator runs\nhours " + gruns, fontsize=8, color=RED, ha="left")
    a1.axhline(0, color=INK, lw=0.6)
    a1.set_ylabel("Power (kW)")
    a1.set_ylim(-420, 470)
    a1.legend(ncol=5, fontsize=7.2, loc="lower center", bbox_to_anchor=(0.5, 1.0), columnspacing=0.9,
              handlelength=1.4)
    a2.step(t, 100*log["soc"][sl], where="post", color=GREEN, lw=1.6)
    for v, lab in [(95, "95 % max"), (60, "60 % gen stop"), (50, "50 % reserve (grid up)"),
                   (25, "25 % gen start"), (10, "10 % island floor")]:
        a2.axhline(v, color=GREY, ls="--", lw=0.8)
        a2.text(169, v, lab, fontsize=7.2, va="center", ha="left", color=INK)
    a2.set_ylim(0, 100)
    a2.set_ylabel("SOC (%)")
    a2.set_xlabel("Hour of the week")
    a2.set_xlim(0, 168)
    a2.set_xticks(range(0, 169, 24))
    fig.align_ylabels()
    save(fig, "25", "fig-25-3-week-dispatch")


# ----------------------------------------------------------------------------
# Figure 25.4 — frequency-watt curtailment
# ----------------------------------------------------------------------------
def fig_25_4():
    f = np.linspace(49.5, 52.2, 1000)
    pa = np.clip(100 - 40*(f - 50.2).clip(0), 0, 100)
    pb = np.clip(100 - 100*(f - 50.2).clip(0), 0, 100)
    fig, ax = new_fig(6.4, 3.9)
    ax.axvspan(49.0, 51.0, color=GREEN, alpha=0.10, lw=0)
    ax.text(49.55, 6, "R5 island window\n49.0–51.0 Hz", fontsize=8, color=GREEN, va="bottom")
    ax.plot(f, pa, ls="--", color=BLUE, label="A: 5 % droop, 40 %/Hz (grid-code default)")
    ax.plot(f, pb, color=ORANGE, label="B: 2 % droop, 100 %/Hz (island group)")
    ax.axvline(51.5, color=RED, lw=1.4)
    ax.text(51.47, 60, "inverter over-frequency\ntrip 51.5 Hz", color=RED, fontsize=8, ha="right")
    need = 110/390*100
    ax.axhline(need, color=INK, ls=":", lw=1.0)
    ax.text(49.55, need + 1.5, "28 %: 110 of 390 kW needed", fontsize=8, va="bottom")
    fb = 50.2 + (100 - need)/100
    fa = 50.2 + (100 - need)/40
    ax.plot([fb], [need], "o", color=ORANGE, ms=7, zorder=5)
    ax.annotate(f"B: {fb:.2f} Hz\ninside window", xy=(fb, need), xytext=(50.35, 45), fontsize=8,
                arrowprops=dict(arrowstyle="-", lw=0.7))
    ax.plot([fa], [need], "X", color=BLUE, ms=8, zorder=5)
    ax.annotate(f"A: {fa:.2f} Hz\nbeyond trip", xy=(fa, need), xytext=(51.62, 45), fontsize=8,
                arrowprops=dict(arrowstyle="-", lw=0.7))
    ax.text(51.62, 100, "battery f(SOC):\n50.0 Hz below 90 % SOC,\nrising to 51.0 Hz at 98 %",
            fontsize=7.6, va="top", bbox=dict(fc="white", ec=GREY, lw=0.6))
    ax.set_xlim(49.5, 52.2); ax.set_ylim(0, 110)
    ax.set_xlabel("Island frequency (Hz)")
    ax.set_ylabel("PV and wind output (% of available)")
    ax.legend(loc="lower left", bbox_to_anchor=(0.0, 1.0), fontsize=8)
    save(fig, "25", "fig-25-4-frequency-watt")


# ----------------------------------------------------------------------------
# Figure 25.5 — time-current curves in the two modes
# ----------------------------------------------------------------------------
def fig_25_5():
    In = 125.0
    k = 15.0*((650/In)**2 - 1)               # inverse-square long-time: 15 s at 650 A
    I = np.logspace(np.log10(1.07*In), np.log10(20e3), 800)
    lt = k/((I/In)**2 - 1)
    mccb = np.where(I < 1250, lt, 0.02)
    elec = np.where(I < 500, lt, np.where(I < 1250, 0.1, 0.02))
    fig, ax = new_fig(6.4, 4.2)
    ax.loglog(I, mccb, ls="--", color=BLUE, label="125 A MCCB, thermal-magnetic (inst. 10 × In)")
    ax.loglog(I, elec, color=ORANGE, label="Electronic trip, island group (S/T 500 A, 0.1 s)")
    # inverter current-limit bar: 650 A held for 2 s
    ax.plot([650, 650], [0.01, 2.0], color=GREEN, lw=5, alpha=0.6, solid_capstyle="butt")
    ax.plot([560, 760], [2.0, 2.0], color=GREEN, lw=2)
    ax.text(140, 0.9, "battery inverter\nlimit 650 A for 2 s,\nthen inverter trips", color=GREEN,
            fontsize=7.8, va="bottom")
    for x, lab in [(650, "650 A\nisland,\nbattery only"), (2400, "2.4 kA\nisland +\n2 gensets"),
                   (15200, "15.2 kA\ngrid-\nconnected")]:
        ax.axvline(x, color=GREY, lw=0.9, ls=":")
        ax.text(x*1.07, 400, lab, fontsize=7.5, va="top", color=INK)
    ax.plot([650], [15.0], "X", color=RED, ms=9, zorder=5)
    ax.annotate("MCCB at 650 A: ≈ 15 s,\nafter inverter trips (fail)", xy=(650, 15), xytext=(1500, 30),
                fontsize=8, color=RED, arrowprops=dict(arrowstyle="-", color=RED, lw=0.7))
    ax.plot([650], [0.1], "o", color=GREEN, ms=8, zorder=5, mfc="white", mew=2)
    ax.annotate("island group clears\nat 0.1 s (pass)", xy=(650, 0.1), xytext=(140, 0.2),
                fontsize=8, color=GREEN, arrowprops=dict(arrowstyle="-", color=GREEN, lw=0.7))
    ax.set_xlim(100, 20e3); ax.set_ylim(0.01, 1000)
    ax.set_xlabel("Prospective fault current (A)")
    ax.set_ylabel("Clearing time (s)")
    ax.grid(True, which="major", color="#E4E4E4", lw=0.6)
    ax.legend(loc="lower left", fontsize=7.8)
    save(fig, "25", "fig-25-5-island-protection-tcc")


# ----------------------------------------------------------------------------
# Figure 25.6 — cumulative discounted cash flow (the chapter's NPV model)
# ----------------------------------------------------------------------------
def fig_25_6():
    load, pv, wind, outage = profiles()
    TARIFF, EXPORT, DIESEL = 0.18, 0.05, 1.10*0.30
    base = load[~outage].sum()*TARIFF + load[outage].sum()*DIESEL
    PVc, WIND, BOS = 400*700, 100*3500, 80e3

    def bess(E, P):
        return 350*E + 150*P

    opts = [("PV+wind+BESS 600 kWh — meets R2 and R3", PVc + WIND + bess(600, 300) + BOS, 13.8e3, wind, 600, 300, ORANGE),
            ("PV+BESS 600 kWh — meets R2, fails R3", PVc + bess(600, 300) + BOS, 7.8e3, 0*wind, 600, 300, BLUE),
            ("PV+BESS 300 kWh — fails R2 and R3", PVc + bess(300, 150) + BOS, 6.3e3, 0*wind, 300, 150, GREEN)]
    fig, ax = new_fig(6.4, 3.9)
    yrs = np.arange(1, 21)
    for name, capex, opex, w, E, P, c in opts:
        r = dispatch_log(load, pv, w, outage, E=E, P=P)
        imp, exp_, gen = r["imp"].sum(), r["exp"].sum(), r["gen"].sum()
        saving = base - (imp*TARIFF - exp_*EXPORT + gen*DIESEL) - opex
        cash = saving*(1 - 0.005)**(yrs - 1) - np.where(yrs == 12, 0.45*350*E, 0)
        cum = np.concatenate([[-capex], np.cumsum(cash/1.08**yrs) - capex])/1e3
        ax.plot(np.arange(21), cum, color=c, marker="o", ms=3, label=name)
        pay = np.argmax(cum >= 0)
        ax.plot([pay], [cum[pay]], "s", color=c, ms=7, mfc="white", mew=1.8)
        ax.text(20.3, cum[-1], f"{cum[-1]:+.1f} k", color=c, fontsize=8, va="center")
        ax.text(pay, cum[pay] - 55, f"yr {pay}", color=c, fontsize=7.5, ha="center", va="top")
    ax.axhline(0, color=INK, lw=0.8)
    ax.axvline(12, color=GREY, ls=":", lw=0.9)
    ax.text(12.15, -930, "year 12: cell replacement\n(45 % of battery cost)", fontsize=7.5, color=GREY)
    ax.set_xlim(0, 20); ax.set_ylim(-1000, 400)
    ax.set_xticks(range(0, 21, 2))
    ax.set_xlabel("Year")
    ax.set_ylabel("Cumulative discounted cash flow (k$)")
    ax.legend(loc="upper left", fontsize=7.8)
    ax.text(13.0, -620, "8 % discount rate; square = discounted payback", fontsize=7.5, color=INK)
    save(fig, "25", "fig-25-6-discounted-cash-flow")


if __name__ == "__main__":
    fig_25_1()
    fig_25_2()
    fig_25_3()
    fig_25_4()
    fig_25_5()
    fig_25_6()
