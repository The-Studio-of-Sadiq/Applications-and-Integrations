"""Figures for Chapter 11 — IoT Systems.

Run from the repository root:  python figures/scripts/ch11.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle, FancyBboxPatch  # noqa: E402

from figstyle import COLORS, INK, box, save, schematic, new_fig  # noqa: E402

BLUE, ORANGE, GREEN, PINK, YELLOW, SKY = COLORS[:6]
RED = "#C62828"
GREY = "#777777"
LBLUE = "#EEF3F8"
LGREEN = "#EAF5EF"
LORANGE = "#FBEFE6"
LGREY = "#F3F3F3"


def line(ax, pts, color=INK, lw=1.1, ls="-", arrow_end=True, both=False, ms=10):
    """Poly-line through pts with an arrow head on the last segment."""
    xs, ys = zip(*pts)
    if not arrow_end and not both:
        ax.plot(xs, ys, color=color, lw=lw, ls=ls)
        return
    if len(pts) > 2:
        ax.plot(xs[:-1], ys[:-1], color=color, lw=lw, ls=ls)
    ax.annotate("", xy=pts[-1], xytext=pts[-2],
                arrowprops=dict(arrowstyle="<|-|>" if both else "-|>", color=color, lw=lw,
                                ls=ls, shrinkA=0, shrinkB=0, mutation_scale=ms))


def container(ax, x, y, w, h, title, ec=GREY, fc="none"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.2",
                                fc=fc, ec=ec, lw=1.0, ls="--"))
    ax.text(x + 0.15, y + h - 0.12, title, ha="left", va="top", fontsize=8.5,
            fontweight="bold", color=INK)


# ----------------------------------------------------------------------------
# Figure 11.1 — architecture
# ----------------------------------------------------------------------------
def fig_11_1():
    fig, ax = schematic(6.8, 5.0, xlim=(0, 13.6), ylim=(-1.0, 9.0))
    fs = 6.8

    # pharmacy
    container(ax, 0.05, 0.75, 4.6, 8.2, "Pharmacy (one site)")
    ax.add_patch(Rectangle((0.2, 5.3), 1.35, 2.85, fc=LGREY, ec=INK, lw=1.0))
    ax.text(0.87, 7.98, "fridge", ha="center", va="top", fontsize=6.8)
    box(ax, 0.3, 5.5, 1.15, 1.55, "glycol-\nbuffered\ndigital\nsensor", fc="white", fontsize=fs)
    box(ax, 2.6, 5.3, 1.9, 2.85,
        "BLE radio\nmodule,\noutside fridge\nCR2032\nadvert every\n20 s with last\n3 readings",
        fc=LBLUE, fontsize=fs)
    ax.plot([1.45, 2.6], [6.25, 6.25], color=INK, lw=2.4)
    ax.text(2.02, 6.38, "flat cable\nthrough\ndoor seal", ha="center", va="bottom", fontsize=6.2,
            linespacing=1.1)
    ax.text(0.25, 4.95, "probe × 2 to 16 per site", ha="left", va="center", fontsize=fs,
            style="italic")

    # gateway
    box(ax, 0.25, 0.95, 4.25, 3.5, "", fc=LORANGE)
    ax.text(2.37, 4.27, "Gateway", ha="center", va="top", fontsize=8.5, fontweight="bold")
    ax.text(0.45, 3.82,
            "Linux SoM · BLE scanner\nEthernet · LTE-M modem + SMS\nsecure element\n"
            "8 GB eMMC, SQLite queue\nbattery-backed RTC\n2 h UPS · buzzer + LED",
            ha="left", va="top", fontsize=fs, linespacing=1.35)
    line(ax, [(3.62, 5.3), (3.62, 4.45)])
    ax.text(3.72, 4.88, "BLE\nadverts", ha="left", va="center", fontsize=6.3, linespacing=1.0)

    # WAN
    box(ax, 4.85, 3.25, 1.75, 1.05, "pharmacy\nrouter (NAT)\nEthernet", fc=LGREY, fontsize=fs)
    box(ax, 4.85, 1.15, 1.75, 1.05, "LTE-M\nnetwork\n(failover)", fc=LGREY, fontsize=fs)
    line(ax, [(4.5, 3.77), (4.85, 3.77)])
    line(ax, [(4.5, 1.67), (4.85, 1.67)])
    line(ax, [(6.6, 3.77), (7.3, 3.77)])
    line(ax, [(6.6, 1.67), (6.95, 1.67), (6.95, 3.4), (7.3, 3.4)])
    ax.text(5.68, 2.72, "MQTT over\nTLS 1.3, port 8883", ha="center", va="center", fontsize=6.3,
            linespacing=1.1)
    line(ax, [(5.4, 4.3), (5.4, 7.6), (7.3, 7.6)], color=GREY)
    ax.text(5.5, 6.4, "HTTPS\nclaim, enrol,\nfirmware", ha="left", va="center", fontsize=6.3,
            color=GREY)

    # cloud
    container(ax, 7.05, 0.75, 6.5, 8.2, "Cloud", fc="#F7FAFD")
    L, LW, R, RW = 7.3, 2.5, 10.45, 2.85
    box(ax, L, 3.0, LW, 1.2, "MQTT broker\ncluster", fc=LBLUE, fontsize=fs)
    box(ax, L, 4.9, LW, 1.3, "ingest service\ndedupe by\n(gateway, seq)", fc=LBLUE, fontsize=fs)
    box(ax, R, 4.9, RW, 1.3, "time-series DB\n5-year retention", fc=LBLUE, fontsize=fs)
    box(ax, R, 3.0, RW, 1.2, "rules engine\n(alarms, stale data)", fc=LBLUE, fontsize=fs)
    box(ax, R, 1.05, RW, 1.25, "notification service\npush · SMS · voice",
        fc=LBLUE, fontsize=fs)
    box(ax, L, 6.95, LW, 1.3, "HTTPS API\nprovisioning,\nfirmware,\ndashboards", fc=LGREEN,
        fontsize=fs)
    box(ax, R, 6.95, RW, 1.3, "device registry\nand certificate\nauthority", fc=LGREEN,
        fontsize=fs)
    line(ax, [(L + LW / 2, 4.2), (L + LW / 2, 4.9)])
    line(ax, [(L + LW, 5.55), (R, 5.55)])
    line(ax, [(L + LW, 5.05), (R, 4.05)])
    line(ax, [(R + RW / 2, 3.0), (R + RW / 2, 2.3)])
    line(ax, [(L + LW, 7.6), (R, 7.6)], both=True)
    line(ax, [(R + RW, 7.3), (13.42, 7.3), (13.42, 2.65), (8.9, 2.65), (8.9, 3.0)],
         color=GREY, ls="--", lw=0.9)
    ax.text(7.3, 2.5, "certificate check and\ntopic ACL from registry", ha="left", va="top",
            fontsize=6.3, color=GREY)

    box(ax, R, -0.85, RW, 0.9, "on-call staff (phone)", fc="white", fontsize=fs)
    line(ax, [(R + RW / 2, 1.05), (R + RW / 2, 0.05)])
    line(ax, [(1.0, 0.95), (1.0, -0.4), (R, -0.4)], color=RED, ls="--")
    ax.text(5.6, -0.32, "direct SMS from gateway modem when cloud unreachable",
            ha="center", va="bottom", fontsize=7, color=RED)
    save(fig, "11", "fig-11-1-cold-chain-architecture")


# ----------------------------------------------------------------------------
# Figure 11.2 — LTE data per format
# ----------------------------------------------------------------------------
TLS, TCPIP = 22, 52
MIN_PER_MONTH = 60 * 24 * 30


def mqtt_qos1(topic_len, payload_len):
    publish = 2 + 2 + topic_len + 2 + payload_len + TLS + TCPIP
    puback = 4 + TLS + TCPIP
    return publish + puback + TCPIP


def fig_11_2():
    mb = MIN_PER_MONTH / 1e6
    rows = [  # name, total B/min, payload B/min
        ("JSON, one publish\nper reading", 8 * mqtt_qos1(36, 75), 8 * 75),
        ("HTTPS POST,\nbatched", 250 + 8 * 40 + 30 + 150 + 2 * TLS + 3 * TCPIP, 8 * 40 + 30),
        ("JSON, batched\n(chosen)", mqtt_qos1(28, 8 * 40 + 30), 8 * 40 + 30),
        ("CBOR, batched,\ndelta-coded", mqtt_qos1(28, 8 * 10 + 15), 8 * 10 + 15),
    ]
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(6.8, 3.6),
                                  gridspec_kw=dict(width_ratios=[2.15, 1], wspace=0.42))
    y = np.arange(len(rows))[::-1]
    for yi, (name, tot, pay) in zip(y, rows):
        chosen = "chosen" in name
        ec = INK if chosen else "none"
        ax.barh(yi, pay * mb, color=BLUE, height=0.6, ec=ec, lw=1.4 if chosen else 0)
        ax.barh(yi, (tot - pay) * mb, left=pay * mb, color=SKY, alpha=0.55, height=0.6, ec=ec,
                lw=1.4 if chosen else 0)
        ax.text(tot * mb + 1.5, yi, f"{tot * mb:.1f} MB\n({(tot - pay) / tot:.0%} overhead)",
                va="center", ha="left", fontsize=7.5,
                bbox=dict(boxstyle="square,pad=0.1", fc="white", ec="none"))
    ax.set_yticks(y)
    ax.set_yticklabels([r[0] for r in rows], fontsize=8)
    ax.get_yticklabels()[2].set_fontweight("bold")
    ax.set_xlim(0, 140)
    ax.set_xticks(range(0, 121, 20))
    ax.set_ylim(-0.7, 4.0)
    ax.set_xlabel("LTE data per gateway (MB/month)")
    ax.axvline(50, color=RED, ls="--", lw=1.2)
    ax.axvline(40, color=ORANGE, ls=":", lw=1.4)
    ax.text(51, 3.55, "R6 budget\n50 MB", color=RED, fontsize=7.5, va="center")
    ax.text(39, 3.55, "revisit\n40 MB", color=ORANGE, fontsize=7.5, va="center", ha="right")
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=BLUE, label="payload (readings)"),
                       Patch(color=SKY, alpha=0.55,
                             label="overhead (MQTT/HTTP, TLS,\nTCP/IP, acknowledgements)")],
              loc="lower right", fontsize=7, bbox_to_anchor=(1.0, 0.0))
    ax.set_title("8 probes, 1 reading/min each", fontsize=9)

    n = np.linspace(2, 24, 200)
    vol = (268 + 40 * n) * mb
    ax2.plot(n, vol, color=BLUE)
    ax2.axhline(50, color=RED, ls="--", lw=1.2)
    ax2.axhline(40, color=ORANGE, ls=":", lw=1.4)
    n40 = (40 / mb - 268) / 40
    n50 = (50 / mb - 268) / 40
    for nn, vv, c in ((n40, 40, ORANGE), (n50, 50, RED)):
        ax2.plot(nn, vv, "o", color=c, ms=5)
        ax2.annotate(f"{nn:.1f}", (nn, vv), xytext=(-20, 6), textcoords="offset points",
                     fontsize=7.5, color=c)
    ax2.plot(8, (268 + 320) * mb, "s", color=INK, ms=4)
    ax2.annotate("8 probes\n25.4 MB", (8, (268 + 320) * mb), xytext=(6, -16),
                 textcoords="offset points", fontsize=7)
    ax2.text(3.0, 15.0 - 1.0, "15.0", va="top", fontsize=7, color=BLUE)
    ax2.text(23.8, 53.0 + 1.5, "53.0", fontsize=7, color=BLUE, ha="right")
    ax2.set_xlim(0, 25)
    ax2.set_ylim(0, 60)
    ax2.set_xlabel("probes per gateway")
    ax2.set_ylabel("JSON batched (MB/month)")
    ax2.set_title("Batched JSON vs probe count", fontsize=9)
    save(fig, "11", "fig-11-2-lte-data-per-format")


# ----------------------------------------------------------------------------
# Figure 11.3 — MQTT session through a NAT router
# ----------------------------------------------------------------------------
def _lifelines(ax, x0, x1, ys, names):
    for y, nm in zip(ys, names):
        ax.plot([x0, x1], [y, y], color=GREY, lw=1.0)
        ax.text(x0 - 0.15, y, nm, ha="right", va="center", fontsize=7.5)


def _msg(ax, xa, ya, xb, yb, text="", color=INK, ls="-", tdx=0.0, tdy=0.0, ha="left",
         fs=6.8, lost=False):
    ax.annotate("", xy=(xb, yb), xytext=(xa, ya),
                arrowprops=dict(arrowstyle="-" if lost else "-|>", color=color, lw=1.0, ls=ls,
                                shrinkA=0, shrinkB=0, mutation_scale=8))
    if lost:
        ax.plot(xb, yb, "x", color=RED, ms=8, mew=2)
    if text:
        ax.text((xa + xb) / 2 + tdx, (ya + yb) / 2 + tdy, text, fontsize=fs, color=color,
                ha=ha, va="center")


def fig_11_3():
    fig, (axA, axB) = plt.subplots(2, 1, figsize=(6.8, 5.0))
    for a in (axA, axB):
        a.set_xlim(-2.1, 10.5)
        a.set_ylim(-1.15, 2.75)
        a.axis("off")
    YG, YR, YB = 2.0, 1.0, 0.0
    names = ["Gateway", "Pharmacy NAT\n(idle 5 min)", "Broker"]
    fs = 6.6
    UP, LO = 1.5, 0.5          # label bands between lifelines

    def lifelines(ax, breaks):
        _lifelines(ax, 0, 10.0, (YG, YR, YB), names)
        ax.plot([0.2, 10.0], [-0.95, -0.95], color=INK, lw=0.8)
        ax.text(10.05, -0.95, "t", fontsize=7, va="center", ha="left", style="italic")
        for xbk in breaks:
            for y in (YG, YR, YB, -0.95):
                ax.plot([xbk - 0.13, xbk + 0.13], [y, y], color="white", lw=4, zorder=3)
                ax.text(xbk, y, "//", fontsize=8, ha="center", va="center", color=GREY,
                        zorder=4)

    def ticks(ax, items):
        for x, lab in items:
            ax.plot([x, x], [-0.99, -0.91], color=INK, lw=0.8)
            ax.text(x, -1.02, lab, fontsize=6.3, ha="center", va="top")

    def bracket(ax, x0, x1, y, text, color=INK, above=True):
        ax.annotate("", xy=(x1, y), xytext=(x0, y),
                    arrowprops=dict(arrowstyle="<->", color=color, lw=0.8, shrinkA=0, shrinkB=0))
        ax.text((x0 + x1) / 2, y + (0.04 if above else -0.05), text, fontsize=fs, ha="center",
                va="bottom" if above else "top", color=color)

    def down(ax, x, color=INK, ls="-", to=YB, lost=False):
        _msg(ax, x, YG, x + 0.06 * (YG - to), to, color=color, ls=ls, lost=lost)

    def up(ax, x, color=INK, ls="-"):
        _msg(ax, x, YB, x + 0.12, YG, color=color, ls=ls)

    # ---------------- Revision A ----------------
    def xa(t):                     # t in minutes; break between -13 and -1
        return 0.3 + (t + 20) / 7 * 1.0 if t <= -13 else 1.6 + (t + 1) / 33 * 8.3
    ax = axA
    lifelines(ax, [1.45])
    ax.text(-2.1, 2.62, "Revision A", fontsize=9.5, fontweight="bold", va="center")
    ax.text(-0.35, 2.62, "keepalive 1200 s · telemetry in 15-min batches · alarms at QoS 0",
            fontsize=7.3, va="center")
    down(ax, xa(-19.5))
    up(ax, xa(-18.4))
    ax.text(0.3, -0.15, "CONNECT,\nCONNACK", fontsize=fs, ha="left", va="top")
    for t in (-15, 0):
        down(ax, xa(t), color=BLUE)
    ax.text(xa(-15) + 0.1, UP, "batch", fontsize=fs, color=BLUE, va="center")
    ax.text(xa(0) + 0.1, UP, "last batch\nt = 0", fontsize=fs, color=BLUE, va="center")
    bracket(ax, xa(0), xa(5), 2.25, "idle 5 min", color=GREY)
    ax.plot(xa(5), YR, "X", color=RED, ms=7, zorder=5)
    ax.text(xa(5), YR - 0.18, "t = 5 min: mapping\nsilently removed", fontsize=fs,
            ha="center", va="top", color=RED)
    down(ax, xa(6), color=RED, to=YR, lost=True)
    ax.text(xa(6) + 0.15, UP + 0.05,
            "t = 6 min: ALARM at QoS 0 dropped at router (no RST);\n"
            "gateway marks the alarm “sent”",
            fontsize=fs, color=RED, va="center")
    bracket(ax, xa(6), xa(21), 2.25, "TCP retransmissions unanswered (~15 min)", color=GREY)
    ax.plot(xa(30), YB, "X", color=INK, ms=8, zorder=5)
    bracket(ax, xa(0), xa(30), -0.42, "broker drops client at 1.5 × 1200 s = 30 min "
            "after the last packet", above=False)
    ticks(ax, [(xa(-20), "−20"), (xa(-15), "−15")] +
          [(xa(t), f"{t}") for t in (0, 5, 10, 15, 20, 25, 30)])
    ax.text(10.05, -1.08, "(min)", fontsize=6.3, va="top", ha="left")

    # ---------------- Revision B ----------------
    def xb(ts):                    # ts in seconds; breaks at 2.3 and 3.5
        if ts <= 120:
            return 0.3 + ts / 120 * 1.8
        if ts <= 123:
            return 2.5 + (ts - 119) / 4 * 0.8
        return 3.9 + (ts - 129.5) / 9 * 6.0
    ax = axB
    lifelines(ax, [2.3, 3.5])
    ax.text(-2.1, 2.62, "Revision B", fontsize=9.5, fontweight="bold", va="center")
    ax.text(-0.35, 2.62, "keepalive 60 s · telemetry every 60 s at QoS 1 · "
            "alarm pending until cloud acknowledges", fontsize=7.3, va="center")
    down(ax, xb(2))
    up(ax, xb(10))
    for t in (25, 85):
        down(ax, xb(t), color=BLUE)
        up(ax, xb(t + 8), color=BLUE, ls="--")
    ax.text(0.3, -0.15, "CONNECT/CONNACK, then telemetry + PUBACK\nevery 60 s keep the NAT "
            "mapping alive", fontsize=fs, ha="left", va="top", color=BLUE)
    ax.plot(xb(108), YR, "X", color=RED, ms=7, zorder=5)
    ax.text(xb(108) + 0.1, LO + 0.1, "mapping lost\nanyway", fontsize=fs, ha="left",
            va="center", color=RED)
    down(ax, xb(120.5), color=RED, to=YR, lost=True)
    ax.text(xb(120.5) + 0.12, UP, "ALARM\nQoS 1", fontsize=fs, color=RED, va="center")
    bracket(ax, xb(120.5), xb(130.5), 2.25, "10 s: no PUBACK")
    ax.text(xb(130.5) + 0.1, 2.29, "close socket, reconnect over LTE-M", fontsize=fs,
            color=ORANGE, ha="left", va="bottom")
    down(ax, xb(130.5), color=ORANGE)
    ax.text(xb(130.5) + 0.2, LO, "CONNECT\n(LTE-M)", fontsize=fs, color=ORANGE, va="center")
    up(ax, xb(133.5), color=ORANGE)
    ax.text(xb(133.5) - 0.02, UP, "CONNACK", fontsize=fs, color=ORANGE, ha="right",
            va="center")
    bracket(ax, xb(130.5), xb(133.5), -0.3, "TLS 3 s", color=ORANGE, above=False)
    down(ax, xb(134.0), color=RED)
    ax.text(xb(134.0) + 0.17, LO, "ALARM,\nsame id", fontsize=fs, color=RED, va="center")
    up(ax, xb(135.5), ls="--")
    ax.text(xb(135.5) + 0.15, UP, "PUBACK", fontsize=fs, va="center")
    up(ax, xb(137.0), color=GREEN)
    ax.text(xb(137.0) + 0.1, LO, "alarm-ack\n(cmd topic,\nfrom cloud)", fontsize=fs,
            color=GREEN, va="center")
    ax.plot(xb(137.0) + 0.12, YG, "o", color=GREEN, ms=5, zorder=5)
    ax.text(xb(137.0) + 0.2, UP + 0.12, "pending\nalarm\ncleared", fontsize=fs, color=GREEN,
            va="center")
    ticks(ax, [(xb(0), "0"), (xb(60), "1:00"), (xb(120), "2:00"), (xb(121), "2:01"),
               (xb(130), "2:10"), (xb(132), "2:12"), (xb(134), "2:14"), (xb(136), "2:16"),
               (xb(138), "2:18")])
    ax.text(10.05, -1.08, "(min:s)", fontsize=6.3, va="top", ha="left")
    fig.subplots_adjust(hspace=0.1, left=0.02, right=0.98, top=0.98, bottom=0.03)
    save(fig, "11", "fig-11-3-mqtt-session-nat-timing")


# ----------------------------------------------------------------------------
# Figure 11.4 — store and forward
# ----------------------------------------------------------------------------
def fig_11_4():
    rate_h = 16 * 60                     # readings per hour
    n_max = rate_h * 72                  # 69,120
    row_b = 64
    jitter_s = 25.0                      # one draw from the 0-60 s window
    batch, period = 500, 2.0
    n_msgs = int(np.ceil(n_max / batch))
    drain_s = n_msgs * period

    t = np.concatenate([[-6, 0], np.linspace(0, 72, 50)])
    q = np.concatenate([[0, 0], rate_h * np.linspace(0, 72, 50)])
    # drain as steps (s after 72 h)
    ts = [0.0, jitter_s]
    qs = [n_max, n_max]
    rem = n_max
    for k in range(n_msgs):
        tk = jitter_s + (k + 1) * period
        rem = max(0, rem - batch)
        ts += [tk, tk]
        qs += [qs[-1], rem]
    ts = np.array(ts)
    qs = np.array(qs)
    t_all = np.concatenate([t, 72 + ts / 3600, [80]])
    q_all = np.concatenate([q, qs, [0]])

    fig, ax = new_fig(6.4, 3.9)
    ax.plot(t_all, q_all, color=BLUE)
    ax.axvspan(0, 72, color=GREY, alpha=0.08)
    ax.text(36, 72500, "WAN outage 72 h (Ethernet and LTE)", ha="center", fontsize=8, color=GREY)
    ax.axhline(n_max, color=RED, ls="--", lw=1.1)
    ax.text(79.5, n_max + 1200, "R4 design point\n69,120 readings = 4.4 MB", ha="right",
            va="bottom", fontsize=7.5, color=RED)
    ax.annotate("960 readings/h\n(16 probes × 60/h)", (30, 30 * rate_h), xytext=(33, 5000),
                fontsize=7.5, arrowprops=dict(arrowstyle="-", color=INK, lw=0.7))
    ax.annotate("WAN restored, 72 h", (72, 0), xytext=(56, 6000), fontsize=7.5,
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.7, mutation_scale=8))
    ax.set_xlim(-6, 80)
    ax.set_ylim(0, 75000)
    ax.set_xticks([0, 12, 24, 36, 48, 60, 72, 80])
    ax.set_xlabel("time from start of WAN outage (h)")
    ax.set_ylabel("queued readings")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:,.0f}"))
    sec = ax.secondary_yaxis("right", functions=(lambda v: v * row_b / 1e6,
                                                 lambda m: m * 1e6 / row_b))
    sec.set_ylabel("queue size (MB, 64 B/row)")
    sec.set_yticks([0, 1, 2, 3, 4, 4.8])
    ax.text(70, 17000,
            "Not shown, also covered by R4:\n• power cuts ≤ 2 h: gateway UPS\n"
            "• longer gateway outage: probe\n   24 h ring buffer, BLE backfill",
            fontsize=7, ha="right", va="bottom",
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=GREY, lw=0.7))

    ins = ax.inset_axes([0.085, 0.50, 0.33, 0.36])
    ins.step(72 + ts / 3600, qs, where="post", color=BLUE, lw=1.2)
    ins.axvspan(72, 72 + 60 / 3600, color=ORANGE, alpha=0.15)
    ins.text(72 + 70 / 3600, 22000, "← jitter\n    0–60 s", ha="left", fontsize=6.5,
             color=ORANGE)
    for k in range(13):
        tl = 72 + (10 + 60 * k) / 3600
        ins.plot([tl, tl], [0, 4500], color=GREEN, lw=1.0)
    ins.text(72.105, 9000, "live telemetry\nevery 60 s", fontsize=6.5, color=GREEN, ha="left")
    t_end = 72 + (jitter_s + drain_s) / 3600
    ins.annotate(f"drain {drain_s / 60:.1f} min\n500 readings / 2 s\n= 250 readings/s",
                 (72 + (jitter_s + 100) / 3600, 45000), xytext=(72.085, 48000), fontsize=6.5,
                 arrowprops=dict(arrowstyle="-", lw=0.6, color=INK))
    ins.axvline(t_end, color=GREY, ls=":", lw=0.8)
    ins.set_xlim(72.0, 72.2)
    ins.set_ylim(0, 75000)
    ins.set_xticks([72.0, 72.05, 72.1, 72.15, 72.2])
    ins.set_xticklabels(["72.0", "72.05", "72.1", "72.15", "72.2 h"], fontsize=6.5)
    ins.set_yticks([0, 35000, 70000])
    ins.set_yticklabels(["0", "35k", "70k"], fontsize=6.5)
    ins.set_title("zoom: drain after WAN restore", fontsize=7.5)
    ins.spines["top"].set_visible(True)
    ins.spines["right"].set_visible(True)
    save(fig, "11", "fig-11-4-store-and-forward")


# ----------------------------------------------------------------------------
# Figure 11.5 — provisioning swimlanes
# ----------------------------------------------------------------------------
def fig_11_5():
    fig, ax = schematic(6.8, 5.0, xlim=(0, 13.6), ylim=(0, 10))
    lanes = [("Factory", 2.5), ("Device registry\nand CA", 3.0), ("Installer app", 2.6),
             ("Gateway", 3.0), ("Probe", 2.5)]
    xs = [0.0]
    for _, w in lanes:
        xs.append(xs[-1] + w)
    for i, (nm, w) in enumerate(lanes):
        ax.add_patch(Rectangle((xs[i], 0), w, 10, fc=["#FAFAFA", "#F2F6FA"][i % 2], ec=GREY,
                               lw=0.6))
        ax.add_patch(Rectangle((xs[i], 9.3), w, 0.7, fc="#DDE6EF", ec=GREY, lw=0.6))
        ax.text(xs[i] + w / 2, 9.65, nm, ha="center", va="center", fontsize=7.8,
                fontweight="bold")
    cx = [(xs[i] + xs[i + 1]) / 2 for i in range(5)]
    fs = 6.3
    H, PITCH, GAP = 0.8, 0.99, 0.2
    rowy = {}
    y = 9.3 - 0.08 - H / 2 - 0.02
    for r in range(1, 10):
        rowy[r] = y
        y -= PITCH + (GAP if r == 3 else 0.0)

    def B(lane, r, text, fc="white", ls="-"):
        ww = lanes[lane][1] - 0.14
        ax.add_patch(FancyBboxPatch((cx[lane] - ww / 2, rowy[r] - H / 2), ww, H,
                                    boxstyle="round,pad=0.02,rounding_size=0.1",
                                    fc=fc, ec=INK, lw=0.9, ls=ls))
        ax.text(cx[lane], rowy[r], text, ha="center", va="center", fontsize=fs,
                linespacing=1.1)
        return (cx[lane], rowy[r], ww)

    def L(b):
        return b[0] - b[2] / 2

    def Rt(b):
        return b[0] + b[2] / 2

    top = lambda b: b[1] + H / 2   # noqa: E731
    bot = lambda b: b[1] - H / 2   # noqa: E731

    F, R, I, G, P = range(5)
    b1 = B(F, 1, "secure element\ngenerates key pair\n(key never leaves)", fc=LORANGE)
    b2 = B(F, 2, "CSR with\nserial number", fc=LORANGE)
    b3 = B(R, 2, "intermediate CA signs\ndevice certificate\n(CN = serial, 10 yr)", fc=LGREEN)
    b4 = B(R, 3, "serial + certificate\nfingerprint registered\nas unclaimed", fc=LGREEN)
    b5 = B(F, 3, "QR label: serial\n+ one-time\nclaim code", fc=LORANGE)
    B(P, 1, "random 128-bit\npairing key\nin flash; QR label", fc=LORANGE)
    line(ax, [(b1[0], bot(b1)), (b2[0], top(b2))], ms=8)
    line(ax, [(Rt(b2), b2[1]), (L(b3), b3[1])], ms=8)
    line(ax, [(b3[0], bot(b3)), (b4[0], top(b4))], ms=8)
    line(ax, [(L(b4), b4[1]), (Rt(b5), b5[1])], ms=8)

    yd = (rowy[3] + rowy[4]) / 2
    ax.plot([0, 13.6], [yd, yd], color=INK, lw=0.9, ls=(0, (6, 3)))
    ax.text(13.5, yd + 0.06, "at the factory ↑", fontsize=6.6, va="bottom", ha="right",
            style="italic")
    ax.text(13.5, yd - 0.06, "at the pharmacy ↓", fontsize=6.6, va="top", ha="right",
            style="italic")

    b6 = B(I, 4, "scan gateway QR →\nHTTPS claim API:\ncode, tenant, site", fc=LBLUE)
    b7 = B(R, 5, "bind serial to\ntenant + site; create\nbroker policy", fc=LGREEN)
    b8 = B(G, 6, "power on; mutual TLS\nwith factory cert;\nsite config on cmd", fc=LBLUE)
    b9s = B(R, 7, "2-yr operational cert\nvia HTTPS enrolment;\nrenew at 80 % of life",
            ls="--")
    b9 = B(I, 7, "scan each probe QR\n(probe ID +\n128-bit key)", fc=LBLUE)
    b10 = B(G, 8, "store pairing key;\nverify AES-CCM MIC,\ncounter must advance", fc=LBLUE)
    b10p = B(P, 8, "BLE adverts carry\nAES-CCM MIC\n+ counter", fc=LBLUE)
    b11 = B(G, 9, "first telemetry\n(MQTT, QoS 1)", fc="#DCEFE3")

    line(ax, [(b5[0], bot(b5)), (b5[0], b6[1]), (L(b6), b6[1])], ms=8)
    ym = (rowy[4] + rowy[5]) / 2
    line(ax, [(b6[0], bot(b6)), (b6[0], ym), (b7[0], ym), (b7[0], top(b7))], ms=8)
    line(ax, [(Rt(b7), b7[1]), (b8[0], b7[1]), (b8[0], top(b8))], ms=8)
    line(ax, [(L(b8), b8[1]), (b9s[0], b8[1]), (b9s[0], top(b9s))], color=GREY, ls="--", ms=8)
    ax.text(b9s[0] - 0.1, b8[1] + 0.05, "side branch", fontsize=6.2, color=GREY, va="bottom",
            ha="right")
    ym = (rowy[6] + rowy[7]) / 2
    line(ax, [(b8[0], bot(b8)), (b8[0], ym), (b9[0], ym), (b9[0], top(b9))], ms=8)
    line(ax, [(Rt(b9), b9[1]), (b10[0], b9[1]), (b10[0], top(b10))], ms=8)
    line(ax, [(L(b10p), b10p[1]), (Rt(b10), b10[1])], ms=8)
    line(ax, [(b10[0], bot(b10)), (b11[0], top(b11))], ms=8)
    save(fig, "11", "fig-11-5-provisioning-flow")


# ----------------------------------------------------------------------------
# Figure 11.6 — reconnection storm (simulation from the chapter listing)
# ----------------------------------------------------------------------------
N, CAP, COST_FAIL, DT = 12_000, 200.0, 0.25, 0.1


def simulate(delay, t_end=600.0, seed=7):
    rng = np.random.default_rng(seed)
    fails = np.zeros(N, int)
    next_try = rng.uniform(0, 2.0, N) + delay(fails, rng)
    done = np.zeros(N, bool)
    per_step, t_done = [], None
    for k in range(int(t_end / DT)):
        t = k * DT
        idx = rng.permutation(np.flatnonzero(~done & (next_try <= t)))
        per_step.append(idx.size)
        s = int(max(0.0, CAP * DT - COST_FAIL * idx.size) / (1 - COST_FAIL))
        done[idx[:s]] = True
        bad = idx[s:]
        fails[bad] += 1
        next_try[bad] = t + delay(fails[bad], rng)
        if done.all() and t_done is None:
            t_done = t
    per_step = np.array(per_step, float)
    rate = np.convolve(per_step, np.ones(10), "same")      # attempts in a 1 s window
    tt = np.arange(per_step.size) * DT
    return tt, rate, done.mean(), t_done


def fig_11_6():
    policies = [
        ("fixed 5 s retry", lambda f, r: np.full(f.size, 5.0), RED),
        ("exponential back-off, no jitter", lambda f, r: np.minimum(300.0, 2.0 * 2.0 ** f), ORANGE),
        ("exponential back-off, full jitter (first window 60 s)",
         lambda f, r: r.uniform(0, np.minimum(300.0, 60.0 * 2.0 ** f)), BLUE),
    ]
    fig, axs = plt.subplots(3, 1, figsize=(6.4, 5.0), sharex=True)
    for ax, (name, pol, c) in zip(axs, policies):
        tt, rate, frac, t_done = simulate(pol)
        r = np.where(rate > 0, rate, 1.0)
        ax.plot(tt, r, color=c, lw=0.9)
        ax.set_yscale("log")
        ax.set_ylim(10, 10000)
        ax.set_xlim(0, 600)
        ax.axhline(200, color=INK, ls="--", lw=0.9)
        ax.axhline(800, color=GREY, ls=":", lw=1.2)
        peak = rate.max()
        if t_done is None:
            res = f"0 % connected at 600 s; peak {peak:,.0f}/s"
        else:
            res = f"all connected at {t_done:.0f} s; peak {peak:.0f}/s"
        ax.set_title(f"{name}:  {res}", fontsize=8.5, loc="left", color=c)
        ax.set_ylabel("attempts/s")
        if t_done is not None:
            ax.axvline(t_done, color=c, lw=0.8, ls="-.")
            ax.text(t_done + 5, 1500, f"{t_done:.0f} s", color=c, fontsize=7.5)
        print(f"  {name}: {frac:.1%} connected, done {t_done}, peak {peak:.0f}")
    axs[1].text(300, 230, "200/s handshake capacity", fontsize=7, ha="left", va="bottom")
    axs[1].text(300, 900, "800/s collapse: no handshake completes", fontsize=7, ha="left",
                va="bottom", color=GREY)
    axs[2].text(590, 3000, "R10 limit: all reconnected\nwithin 600 s", fontsize=7.5,
                ha="right", va="center",
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=INK, lw=0.7))
    axs[2].text(165, 14, "last retries < 10/s (below axis)", fontsize=7, color=BLUE,
                va="center")
    axs[2].set_xlabel("time after broker restart (s)")
    fig.tight_layout(h_pad=0.6)
    save(fig, "11", "fig-11-6-reconnection-storm")


if __name__ == "__main__":
    fig_11_1()
    fig_11_2()
    fig_11_3()
    fig_11_4()
    fig_11_5()
    fig_11_6()
