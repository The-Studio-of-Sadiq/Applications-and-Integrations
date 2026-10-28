"""Figures for Chapter 26 — Communication-System Integration.

Run from the repository root:  python figures/scripts/ch26.py
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import schemdraw  # noqa: E402
import schemdraw.elements as elm  # noqa: E402

from figstyle import COLORS, INK, box, save, schematic, new_fig  # noqa: E402

schemdraw.use("matplotlib")
BLUE, ORANGE, GREEN, PINK, YELLOW, SKY = COLORS[:6]
RED = "#C62828"
GREY = "#777777"

# ----------------------------------------------------------------------------
# Models of Sections 26.4 and 26.5 (same equations as the chapter listings)
# ----------------------------------------------------------------------------
SNR_REQ = {7: -7.5, 8: -10.0, 9: -12.5, 10: -15.0, 11: -17.5, 12: -20.0}
NOISE = -174 + 10*np.log10(125e3) + 6.0


def path_loss(d_km, pl1=110.0, n=3.4):
    return pl1 + 10*n*np.log10(d_km)


def hata(d_km, f=868.0, hb=30.0, hm=1.5):
    """Okumura-Hata urban loss and its suburban and open-area corrections (dB)."""
    a = (1.1*np.log10(f) - 0.7)*hm - (1.56*np.log10(f) - 0.8)
    L = 69.55 + 26.16*np.log10(f) - 13.82*np.log10(hb) - a + (44.9 - 6.55*np.log10(hb))*np.log10(d_km)
    sub = L - 2*np.log10(f/28)**2 - 5.4
    op = L - 4.78*np.log10(f)**2 + 18.33*np.log10(f) - 40.94
    return sub, op


def time_on_air(sf, payload=26, bw=125e3, cr=1, preamble=8, crc=True, header=True):
    de = 1 if sf >= 11 and bw <= 125e3 else 0
    ts = 2**sf / bw
    n = 8 + max(math.ceil((8*payload - 4*sf + 28 + 16*crc - 20*(not header))
                          / (4*(sf - 2*de))) * (cr + 4), 0)
    return (preamble + 4.25)*ts + n*ts


def battery_years(sf, tries, cap_mah=6800, period_s=900):
    toa = time_on_air(sf)
    q_tx = 45.0*toa
    q_rx = 2*5.0*time_on_air(sf, payload=12)
    q_msg = tries*(q_tx + q_rx) + 3.0
    n = 365*86400/period_s
    mah_year = n*q_msg/3600 + 0.002*8760 + 0.01*cap_mah
    return cap_mah/mah_year


# ----------------------------------------------------------------------------
# Figure 26.1 — network architecture
# ----------------------------------------------------------------------------
def fig_26_1():
    fig, ax = schematic(6.8, 5.0, xlim=(0, 17.4), ylim=(0, 12.6))
    nodes = [
        (8.8, 2.2, "12 pump-station nodes", "mains · whip on 4 m mast\nalarms (confirmed uplinks)", "≤ 8 km"),
        (5.6, 1.7, "8 reservoir kiosk nodes", "dipole at 1.5 m", "≤ 6 km"),
        (1.6, 2.9, "16 valve-chamber nodes", "Li-SOCl₂ C cell\npressure transducer\nantenna in lid (Rev A),\n"
                                            "on marker bollard (Rev B)", "≤ 5 km"),
    ]
    tx = 8.4
    tip = (tx, 11.2)
    for y, h, title, sub, dist in nodes:
        box(ax, 0.1, y, 4.9, h, "", fc="#EEF3F8")
        ax.text(2.55, y + h - 0.25, title, ha="center", va="top", fontsize=7.6, weight="bold")
        ax.text(2.55, y + h - 0.8, sub, ha="center", va="top", fontsize=7, linespacing=1.2)
        x0, y0 = 5.0, y + h/2
        ax.plot([x0, tip[0] - 0.1], [y0, tip[1] - 0.15], color=BLUE, ls="--", lw=1.0)
        fr = 0.3
        ax.text(x0 + fr*(tip[0] - x0), y0 + fr*(tip[1] - y0), dist, fontsize=7.5, color=BLUE,
                ha="center", va="center", bbox=dict(fc="white", ec="none", pad=0.6))
    ax.text(4.4, 12.25, "LoRa uplinks 868.1 / 868.3 / 868.5 MHz, SF7–SF12, 0.5–8 km\n"
            "≤ 1 % duty cycle per device in 868.0–868.6 MHz (36 s per hour)", fontsize=7.3, color=BLUE,
            ha="center", va="center")
    # water tower
    ax.plot([tx - 0.6, tx - 0.15], [0.3, 8.6], color=GREY, lw=1.6)
    ax.plot([tx + 0.6, tx + 0.15], [0.3, 8.6], color=GREY, lw=1.6)
    ax.add_patch(plt.Rectangle((tx - 0.75, 8.6), 1.5, 1.4, fc="#E0E0E0", ec=GREY, lw=1.0))
    ax.text(tx, 9.3, "30 m\ntower", ha="center", va="center", fontsize=6.8)
    ax.plot([tx, tx], [10.0, 11.2], color=INK, lw=1.6)
    ax.plot([tx - 0.12, tx + 0.12], [11.2, 11.2], color=INK, lw=1.6)
    ax.text(tx + 0.2, 10.9, "6 dBi\ncollinear", fontsize=6.8, ha="left", va="center")
    # LTE sector antenna 5 m below the gateway antenna
    ax.add_patch(plt.Rectangle((tx + 0.6, 7.3), 0.3, 0.9, fc="#F8D7D7", ec=RED, lw=1.0))
    ax.text(tx + 1.05, 7.75, "LTE 800 sector antenna, 5 m below\nthe gateway antenna (interferer,\n"
            "791–821 MHz downlink)", fontsize=6.8, color=RED, ha="left", va="center")
    # Rev B gateway at the top
    box(ax, tx + 1.2, 9.4, 4.7, 1.0, "Rev B: mast-top gateway\n+ cavity filter (1.5 dB)",
        fc="#E6F4EA", fontsize=6.8)
    ax.plot([tx + 0.75, tx + 1.2], [9.9, 9.9], color=INK, lw=0.9)
    # Rev A gateway at the base
    box(ax, tx + 1.0, 0.3, 4.2, 1.3, "Rev A: gateway at base\n30 m LMR-400 feeder\n+ connectors (4.3 dB)",
        fc="#FDECEC", fontsize=6.8)
    ax.plot([tx + 0.5, tx + 1.0], [0.95, 0.95], color=INK, lw=0.9)
    ax.text(tx, 4.6, "feeder (A)\nPoE (B)", fontsize=6.6, ha="center", va="center",
            color=INK, bbox=dict(fc="white", ec="none", pad=0.5))
    # back end
    xs = 14.0
    box(ax, xs, 5.2, 3.3, 1.2, "Network server\n(on-premises)", fc="#EFE6F5", fontsize=7.8)
    box(ax, xs, 2.9, 3.3, 1.0, "SCADA historian", fc="#FDF1DC", fontsize=7.8)
    box(ax, xs, 0.6, 3.3, 1.0, "Operator HMI", fc="#FDF1DC", fontsize=7.8)
    ax.annotate("", xy=(xs + 0.5, 5.2), xytext=(tx + 3.4, 1.6),
                arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=1.0, mutation_scale=10))
    ax.text(tx + 3.3, 3.6, "private fibre\nUDP / Basic Station\n(up- and downlinks)", fontsize=6.8,
            ha="center", va="center", bbox=dict(fc="white", ec="none", pad=0.5))
    ax.annotate("", xy=(xs + 1.65, 3.9), xytext=(xs + 1.65, 5.2),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.0, mutation_scale=10))
    ax.text(xs + 1.8, 4.55, "MQTT", fontsize=7.3, ha="left", va="center")
    ax.annotate("", xy=(xs + 1.65, 1.6), xytext=(xs + 1.65, 2.9),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.0, mutation_scale=10))
    save(fig, "26", "fig-26-1-telemetry-network")


def fig_26_2():
    fig, ax = plt.subplots(figsize=(6.8, 4.9))
    ax.axis("off")
    d = schemdraw.Drawing(canvas=ax, show=False)
    d.config(fontsize=7.5, unit=2, lw=1.1)
    fs = 7
    # transceiver body
    rects = [((0, 0), 5, 9.5, "#EEF3F8"), ((14.2, 4.6), 2.2, 3.6, "#FDF1DC"), ((8.3, 1.6), 3.6, 2.0, "#E6F4EA"),
             ((6.4, 11.1), 3.4, 1.4, "#EFE6F5")]
    d.add(elm.Label().at((3.3, 5.3)).label("SX1262\nLoRa\ntransceiver", fontsize=8.5))
    left = [("NSS", 8.2), ("SCK", 7.5), ("MOSI", 6.8), ("MISO", 6.1), ("BUSY", 4.2), ("DIO1", 3.5),
            ("NRESET", 2.8)]
    for name, y in left:
        d.add(elm.Line().at((0, y)).to((-1.3, y)))
        d.add(elm.Label().at((0.12, y)).label(name, halign="left", fontsize=fs))
    d.add(elm.Label().at((-1.45, 7.15)).label("to MCU\nSPI", halign="right", fontsize=fs))
    d.add(elm.Label().at((-1.45, 3.5)).label("to MCU\nGPIO / EXTI", halign="right", fontsize=fs))
    for name, y in [("VR_PA", 8.6), ("RFO", 7.6), ("RFI_P", 3.0), ("RFI_N", 2.2)]:
        d.add(elm.Label().at((4.88, y)).label(name, halign="right", fontsize=fs))
    for name, x in [("DIO2", 1.3), ("DIO3", 2.8), ("XTA", 4.3)]:
        d.add(elm.Label().at((x, 9.35)).label(name, valign="top", fontsize=fs))
    for name, x in [("VBAT", 0.9), ("DCC_SW", 2.6), ("VREG", 4.3)]:
        d.add(elm.Label().at((x, 0.15)).label(name, valign="bottom", fontsize=6.5))
    # PA supply choke and TX match
    yt = 7.6
    d.add(elm.Line().at((5, 8.6)).to((5.7, 8.6)))
    d.add(elm.Inductor2(loops=2).at((5.7, 8.6)).to((5.7, yt)))
    d.add(elm.Line().at((5, yt)).to((5.7, yt)))
    d.add(elm.Dot().at((5.7, yt)))
    d.add(elm.Inductor2(loops=2).at((5.7, yt)).to((7.5, yt)).label("L", loc="top", fontsize=fs))
    d.add(elm.Dot().at((7.5, yt)))
    d.add(elm.Capacitor().at((7.5, yt)).to((7.5, 6.1)))
    d.add(elm.Label().at((7.8, 6.85)).label("C", halign="left", fontsize=fs))
    d.add(elm.Ground().at((7.5, 6.1)))
    d.add(elm.Label().at((6.3, 4.8)).label("PA match\n(vendor\nreference)", fontsize=fs))
    # 5th-order low-pass C-L-C-L-C
    d.add(elm.Line().at((7.5, yt)).to((8.6, yt)))
    for i, x in enumerate([8.6, 10.5, 12.4]):
        d.add(elm.Dot().at((x, yt)))
        d.add(elm.Capacitor().at((x, yt)).to((x, 6.1)))
        d.add(elm.Ground().at((x, 6.1)))
        if i < 2:
            d.add(elm.Inductor2(loops=2).at((x, yt)).to((x + 1.9, yt)))
    d.add(elm.Label().at((10.6, 4.8)).label("5th-order LC low-pass\nC-L-C-L-C, fc ≈ 1 GHz\n−35 dB at 1.7 GHz",
                                            fontsize=fs))
    d.add(elm.Line().at((12.4, yt)).to((14.2, yt)))
    # RF switch
    d.add(elm.Label().at((15.3, 6.4)).label("SPDT\nswitch\n0.4 dB", fontsize=fs))
    d.add(elm.Label().at((14.3, yt)).label("TX", halign="left", fontsize=6.5))
    d.add(elm.Label().at((14.3, 5.2)).label("RX", halign="left", fontsize=6.5))
    # RX path through balun and match to the LNA
    d.add(elm.Line().at((14.2, 5.2)).to((13.6, 5.2)))
    d.add(elm.Line().at((13.6, 5.2)).to((13.6, 2.6)))
    d.add(elm.Line().at((13.6, 2.6)).to((11.9, 2.6)))
    d.add(elm.Label().at((10.1, 2.6)).label("balun\n+ LNA match", fontsize=fs))
    d.add(elm.Line().at((8.3, 3.0)).to((5.0, 3.0)))
    d.add(elm.Line().at((8.3, 2.2)).to((5.0, 2.2)))
    # antenna side: ESD, U.FL, antenna
    ya = 6.4
    d.add(elm.Line().at((16.4, ya)).to((17.3, ya)))
    d.add(elm.Dot().at((17.3, ya)))
    d.add(elm.DiodeTVS().at((17.3, ya)).to((17.3, 4.6)))
    d.add(elm.Label().at((17.65, 5.5)).label("ESD", halign="left", fontsize=fs))
    d.add(elm.Ground().at((17.3, 4.6)))
    d.add(elm.Line().at((17.3, ya)).to((18.3, ya)))
    d.add(elm.CoaxConnect().at((18.7, ya)))
    d.add(elm.Label().at((18.7, 7.0)).label("U.FL", fontsize=fs))
    d.add(elm.Line().at((19.1, ya)).to((19.8, ya)))
    d.add(elm.Line().at((19.8, ya)).to((19.8, 7.6)))
    d.add(elm.Antenna().at((19.8, 7.6)))
    d.add(elm.Label().at((19.8, 9.4)).label("antenna\n2 dBi", fontsize=fs))
    # DIO2 -> RF switch control
    d.add(elm.Line().at((1.3, 9.5)).to((1.3, 13.3)))
    d.add(elm.Line().at((1.3, 13.3)).to((15.3, 13.3)))
    d.add(elm.Line().at((15.3, 13.3)).to((15.3, 8.2)))
    d.add(elm.Label().at((11.5, 13.65)).label("DIO2 → RF switch control (SetDIO2AsRfSwitchCtrl)", fontsize=fs))
    # DIO3 -> TCXO supply, TCXO -> XTA
    d.add(elm.Line().at((2.8, 9.5)).to((2.8, 12.1)))
    d.add(elm.Line().at((2.8, 12.1)).to((6.4, 12.1)))
    d.add(elm.Label().at((8.1, 11.85)).label("TCXO 32 MHz\n±2 ppm", fontsize=fs))
    d.add(elm.Line().at((6.4, 11.6)).to((4.3, 11.6)))
    d.add(elm.Line().at((4.3, 11.6)).to((4.3, 9.5)))
    d.add(elm.Label().at((8.1, 12.95)).label("VDD 1.8 V from DIO3", halign="center", fontsize=6.5))
    # power: Li-SOCl2 cell and hybrid-layer capacitor; DC-DC inductor
    d.add(elm.Line().at((0.9, 0)).to((0.9, -1.0)))
    d.add(elm.Line().at((0.9, -1.0)).to((-3.2, -1.0)))
    d.add(elm.Dot().at((-1.2, -1.0)))
    d.add(elm.Battery().at((-3.2, -1.0)).to((-3.2, -3.0)))
    d.add(elm.Label().at((-3.7, -2.0)).label("3.6 V\nLi-SOCl₂\nC cell", halign="right", fontsize=fs))
    d.add(elm.Ground().at((-3.2, -3.0)))
    d.add(elm.Capacitor(polar=True).at((-1.2, -1.0)).to((-1.2, -3.0)))
    d.add(elm.Label().at((-0.8, -2.0)).label("100 µF\nhybrid-layer", halign="left", fontsize=fs))
    d.add(elm.Ground().at((-1.2, -3.0)))
    d.add(elm.Label().at((-2.2, -0.65)).label("buffers 45 mA TX pulse", fontsize=6.5))
    d.add(elm.Line().at((2.6, 0)).to((2.6, -1.3)))
    d.add(elm.Inductor2(loops=2).at((2.6, -1.3)).to((4.3, -1.3)))
    d.add(elm.Line().at((4.3, -1.3)).to((4.3, 0)))
    d.add(elm.Label().at((3.45, -2.3)).label("DC-DC mode\nenabled", fontsize=6.5))
    # level annotations
    d.add(elm.Label().at((7.3, 10.55)).label("+14 dBm conducted\n2nd harmonic −11 dBm", fontsize=fs, color=RED))
    d.add(elm.Label().at((12.0, 9.25)).label("2nd harmonic −46 dBm\n(limit −30 dBm)", fontsize=fs, color=RED))
    d.draw()
    for (x0, y0), w, h, fc in rects:
        ax.add_patch(plt.Rectangle((x0, y0), w, h, fc=fc, ec=INK, lw=1.1, zorder=0.5))
    ax.set_aspect("equal")
    ax.set_xlim(-6.0, 21.0); ax.set_ylim(-3.8, 14.2)
    save(fig, "26", "fig-26-2-node-rf-front-end")


# ----------------------------------------------------------------------------
# Figure 26.3 — path loss: survey, fit, Hata, free space
# ----------------------------------------------------------------------------
def fig_26_3():
    rng = np.random.default_rng(26)
    dpts = 10**rng.uniform(np.log10(0.3), np.log10(9.0), 4200)
    pl = path_loss(dpts) + 7.0*rng.standard_normal(4200)
    d = np.logspace(np.log10(0.3), 1, 200)
    sub, op = hata(d)
    fs = 20*np.log10(d) + 20*np.log10(868) + 32.44
    fig, ax = new_fig(6.4, 4.0)
    ax.scatter(dpts, pl, s=2, color="#B0B0B0", alpha=0.5, lw=0, label="Drive survey, 4,200 points")
    ax.semilogx(d, path_loss(d), color=INK, lw=2, label="Fit 110 + 34 log₁₀(d), σ = 7 dB")
    ax.semilogx(d, path_loss(d) + 11.5, color=INK, lw=1, ls=":", label="Fit ± 1.645σ (± 11.5 dB)")
    ax.semilogx(d, path_loss(d) - 11.5, color=INK, lw=1, ls=":")
    ax.semilogx(d, sub, color=ORANGE, ls="--", label="Hata, suburban")
    ax.semilogx(d, op, color=BLUE, ls="-.", label="Hata, open area")
    ax.semilogx(d, fs, color=GREEN, lw=1.0, label="Free space")
    for x, lab in [(5, "5 km\nchambers"), (6, "6 km\nreservoirs"), (8, "8 km\npump stns")]:
        ax.axvline(x, color=GREY, lw=0.8, ls=(0, (2, 2)))
        ax.text(x*0.985, 81.5, lab.replace(chr(10), " "), fontsize=7, va="bottom", ha="right", rotation=90)
    ax.set_xlim(0.3, 10); ax.set_ylim(80, 160)
    ax.set_xticks([0.3, 0.5, 1, 2, 3, 5, 10]); ax.set_xticklabels(["0.3", "0.5", "1", "2", "3", "5", "10"])
    ax.set_xlabel("Distance from gateway (km)")
    ax.set_ylabel("Path loss at 868 MHz (dB)")
    ax.legend(loc="upper left", fontsize=7.5)
    save(fig, "26", "fig-26-3-path-loss-survey")


# ----------------------------------------------------------------------------
# Figure 26.4 — margin by class, Revision A and B
# ----------------------------------------------------------------------------
def fig_26_4():
    classes = [("Pump station\n8 km", 8.0, -6.0, 7.0), ("Reservoir\n6 km", 6.0, 0.0, 7.0),
               ("Chamber, in lid\n5 km", 5.0, 22.0, np.hypot(7, 4)), ("Chamber, bollard\n5 km", 5.0, 1.5, 7.0)]
    fig, ax = new_fig(6.4, 3.9)
    x = np.arange(4)
    w = 0.36
    for j, (rev, gl, c) in enumerate([("Rev A: indoor gateway, 4.3 dB feeder", 4.3, "#9E9E9E"),
                                      ("Rev B: mast-top gateway + filter, 1.5 dB", 1.5, BLUE)]):
        ms, sfs = [], []
        for name, dk, extra, sig in classes:
            pr = 16.0 - path_loss(dk) - extra + 6.0 - gl
            need = 1.645*sig + 3
            ms.append(pr - (NOISE + SNR_REQ[12]))
            sf = next((s for s, snr in SNR_REQ.items() if pr - (NOISE + snr) >= need), None)
            sfs.append(f"SF{sf}" if sf else "none")
        xb = x + (j - 0.5)*w
        ax.bar(xb, ms, w, color=c, label=rev)
        for xi, m, s in zip(xb, ms, sfs):
            ax.text(xi, max(m, 0) + 0.5, f"{s}\n{m:.1f}", ha="center", va="bottom", fontsize=7.3,
                    color=RED if s == "none" else INK)
    ax.axhline(14.5, color=GREEN, ls="--", lw=1.1)
    ax.axhline(16.3, color=ORANGE, ls="--", lw=1.1)
    ax.text(2.0, 14.0, "14.5 dB required, outdoor", fontsize=7.3, color=GREEN, ha="center", va="top")
    ax.text(2.0, 16.8, "16.3 dB required, chamber", fontsize=7.3, color=ORANGE, ha="center", va="bottom")
    ax.axhline(0, color=INK, lw=0.7)
    ax.set_xticks(x); ax.set_xticklabels([c[0] for c in classes], fontsize=8.5)
    ax.set_ylabel("Margin above SF12 sensitivity (dB)")
    ax.set_ylim(-3, 30)
    ax.legend(loc="upper right", fontsize=7.5, bbox_to_anchor=(1.0, 1.08))
    ax.text(0.0, -0.17, "Bar labels: lowest SF meeting the required margin, and the SF12 margin in dB",
            transform=ax.transAxes, fontsize=7.3, color=GREY)
    save(fig, "26", "fig-26-4-margin-by-class")


# ----------------------------------------------------------------------------
# Figure 26.5 — time on air and battery life versus SF
# ----------------------------------------------------------------------------
def fig_26_5():
    sfs = np.arange(7, 13)
    toa = np.array([time_on_air(s) for s in sfs])*1e3
    life1 = np.array([battery_years(s, 1) for s in sfs])
    life3 = np.array([battery_years(s, 3) for s in sfs])
    fig, (ax, a2) = plt.subplots(2, 1, figsize=(6.4, 4.8), sharex=True,
                                 gridspec_kw=dict(height_ratios=[1, 1.25]))
    ax.semilogy(sfs, toa, "o-", color=INK)
    for s, t in zip(sfs, toa):
        ax.text(s + (0.1 if s == 7 else -0.08), t*(0.8 if s == 7 else 1.18), f"{t:,.0f} ms",
                ha="left" if s == 7 else "right", va="top" if s == 7 else "bottom", fontsize=7.5)
    ax.set_ylim(30, 3000)
    ax.set_ylabel("Time on air,\n26-byte packet (ms)")
    a2.axhspan(15, 35, color=GREY, alpha=0.12, lw=0)
    a2.text(12.35, 34.3, "above 15 years: limited by cell shelf life", fontsize=7.5, color=GREY,
            va="top", ha="right")
    a2.axhline(10, color=RED, ls="--", lw=1.1)
    a2.text(6.9, 10.4, "R4: 10 years", color=RED, fontsize=7.5, ha="left", va="bottom")
    a2.plot(sfs, np.minimum(life1, 60), "s-", color=BLUE, label="one attempt per report")
    a2.plot(sfs, np.minimum(life3, 60), "^--", color=ORANGE, label="three attempts (confirmed, retried)")
    for s in (9, 10, 12):
        v = life1[s - 7]
        a2.text(s + 0.1, v + 0.5, f"{v:.1f} y", color=BLUE, fontsize=7.5, va="bottom")
    a2.text(12.1, life3[-1], f"{life3[-1]:.1f} y", color=ORANGE, fontsize=7.5, va="center")
    a2.set_ylim(0, 35)
    a2.set_xlim(6.7, 12.5)
    a2.set_ylabel("Chamber-node\nbattery life (years)")
    a2.set_xticks(sfs); a2.set_xticklabels([f"SF{s}" for s in sfs])
    a2.set_xlabel("Spreading factor")
    a2.legend(loc="upper right", fontsize=7.5, bbox_to_anchor=(1.0, 0.86))
    fig.align_ylabels()
    save(fig, "26", "fig-26-5-airtime-battery")


# ----------------------------------------------------------------------------
# Figure 26.6 — gateway blocking spectrum and noise floor
# ----------------------------------------------------------------------------
def fig_26_6():
    f = np.linspace(780, 880, 4001)
    floor = -125.0
    # LTE 10 MHz carrier 801-811 MHz: -18.4 dBm total = -38.4 dBm per 100 kHz, ~45 dBc ACLR skirts
    lte = np.where((f >= 801) & (f <= 811), -38.4, -38.4 - 45 - 2*np.minimum(np.abs(f - 806) - 5, 40))
    lte = np.where((f >= 801) & (f <= 811), -38.4, lte)
    lora = np.full_like(f, -200.0)
    for fc in (868.1, 868.3, 868.5):
        lora = np.maximum(lora, -119 - 40*((f - fc)/0.0625)**2)

    def pw(*db):
        return 10*np.log10(sum(10**(x/10) for x in db))
    # cavity band-pass 863-870 MHz: 1 dB passband loss, >= 45 dB rejection below 821 MHz
    off = np.maximum(0, np.maximum(863 - f, f - 870))
    rej = np.minimum(1.0 + 1.0*off**1.6, 46.0)
    before = pw(lte, lora, np.full_like(f, floor))
    after = pw(lte - rej, lora - rej, np.full_like(f, floor))
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.8, 3.7), gridspec_kw=dict(width_ratios=[1.35, 1]))
    a1.axvspan(863, 870, color=GREEN, alpha=0.12, lw=0)
    a1.text(866.5, -15, "filter\npassband\n863–870", fontsize=7, color=GREEN, ha="center", va="top")
    a1.plot(f, before, color=RED, lw=1.2, label="without filter")
    a1.plot(f, after, color=BLUE, lw=1.2, label="with cavity filter")
    a1.text(812, -36, "LTE 800, 801–811 MHz\n−38 dBm/100 kHz\n(−18.4 dBm total)", fontsize=7, color=RED,
            va="center")
    a1.text(812, -80, "−83 dBm/100 kHz", fontsize=7, color=BLUE, va="center")
    a1.annotate("LoRa 868.1/.3/.5", xy=(868.3, -118), xytext=(828, -108), fontsize=7,
                arrowprops=dict(arrowstyle="-", lw=0.6))
    a1.set_xlim(780, 880); a1.set_ylim(-130, -10)
    a1.set_xlabel("Frequency (MHz)")
    a1.set_ylabel("Power at gateway input (dBm / 100 kHz)")
    a1.legend(loc="center right", fontsize=7)
    # noise floor over 24 h
    t = np.linspace(0, 24, 24*12 + 1)
    rng = np.random.default_rng(6)
    load = np.clip((t - 16.0)/1.0, 0, 1)*np.clip((23.5 - t)/0.5, 0, 1)
    nf_no = -117 + 9*load + 0.3*rng.standard_normal(t.size)
    nf_f = -117 + 0.35*load + 0.2*rng.standard_normal(t.size)
    a2.axvspan(17, 23, color=RED, alpha=0.08, lw=0)
    a2.plot(t, nf_no, color=RED, lw=1.1, label="without filter")
    a2.plot(t, nf_f, color=BLUE, lw=1.1, label="with filter")
    a2.text(20, -107.3, "+9 dB\nLTE loaded", fontsize=7, color=RED, ha="center", va="bottom")
    a2.text(1, -116.3, "within 0.5 dB (R6)", fontsize=7, color=BLUE, va="bottom")
    a2.set_xlim(0, 24); a2.set_ylim(-120, -104)
    a2.set_xticks(range(0, 25, 6))
    a2.set_xlabel("Time of day (h)")
    a2.set_ylabel("Noise floor in 125 kHz (dBm)")
    a2.legend(loc="upper left", fontsize=7)
    fig.tight_layout(w_pad=1.5)
    save(fig, "26", "fig-26-6-gateway-blocking")


if __name__ == "__main__":
    fig_26_1()
    fig_26_2()
    fig_26_3()
    fig_26_4()
    fig_26_5()
    fig_26_6()
