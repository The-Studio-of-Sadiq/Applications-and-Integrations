"""Figures for Chapter 32 — AI and Machine Learning for EEE.

Run from the repository root:  python figures/scripts/ch32.py

The plots are computed from the chapter's own listings (synthetic fleet of
Listing 32.1, regressions of 32.3, DGA classifier of 32.4, forecaster of 32.5,
CUSUM of 32.6 and surrogate of 32.7), reproduced here so the script is
self-contained.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Polygon, Rectangle  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

from figstyle import COLORS, INK, save, schematic  # noqa: E402

BLUE, ORANGE, GREEN, PINK, YELLOW, SKY = COLORS[:6]
RED = "#C62828"
PURPLE = "#6A3D9A"
GREY = "#777777"


def tint(c, a="30"):
    return c + a


# ----------------------------------------------------------------------------
# Listing 32.1 — synthetic fleet (reproduced)
# ----------------------------------------------------------------------------
H = 24 * 365
t = np.arange(H)
hour, day = t % 24, t // 24


def top_oil_rise(K, d_or, R, tau_h, n=0.8):
    ult = d_or * ((1 + R * K**2) / (1 + R)) ** n
    a, x, out = np.exp(-1.0 / tau_h), ult[0], np.empty_like(K)
    for i, u in enumerate(ult):
        x = a * x + (1 - a) * u
        out[i] = x
    return out


def make_fleet(n_units=40, seed=2026):
    rng = np.random.default_rng(seed)
    amb = 12 - 9 * np.cos(2 * np.pi * (day - 20) / 365) + 4 * np.sin(2 * np.pi * (hour - 9) / 24)
    amb += np.convolve(rng.normal(0, 0.6, H), np.ones(72), "same") / np.sqrt(72) * 4
    amb[200 * 24:212 * 24] += 11 * np.hanning(288)
    units = []
    for u in range(n_units):
        p = dict(d_or=rng.uniform(45, 60), R=rng.uniform(5, 8), tau_h=rng.uniform(2.5, 3.5))
        shape = 0.55 + 0.25 * np.exp(-((hour - 19) / 3) ** 2) + 0.12 * np.exp(-((hour - 8) / 2) ** 2)
        K = rng.uniform(0.65, 1.0) * shape * np.where(day % 7 >= 5, 0.9, 1.0)
        K *= 1 + 0.12 * np.cos(2 * np.pi * day / 365) + 0.012 * np.clip(amb - 24, 0, None)
        K *= 1 + 0.04 * np.convolve(rng.normal(0, 1, H), np.ones(6) / 6 ** 0.5, "same")
        d_or = np.where((u == 31) & (day >= 250), 1.18 * p["d_or"], p["d_or"])
        theta = amb + top_oil_rise(K, d_or, p["R"], p["tau_h"]) + rng.normal(0, 0.3, H)
        I_meas = K * np.where((20 <= u <= 25) & (t >= 6000), 0.8, 1.0)
        I_meas = I_meas * (1 + rng.normal(0, 0.01, H))
        theta[rng.random(H) < 0.01] = np.nan
        units.append(dict(id=u, params=p, K_true=K, I=I_meas, theta=theta))
    units[12]["theta"][3000:3120] = units[12]["theta"][2999]
    units[3]["theta"][rng.choice(H, 20, replace=False)] += 40
    return amb, units


_FLEET = None


def fleet():
    global _FLEET
    if _FLEET is None:
        _FLEET = make_fleet()
    return _FLEET


def line(ax, pts, color=INK, lw=1.1, ls="-", arrow_end=True):
    xs, ys = zip(*pts)
    if len(pts) > 2:
        ax.plot(xs[:-1], ys[:-1], color=color, lw=lw, ls=ls, solid_capstyle="butt")
    ax.annotate("", xy=pts[-1], xytext=pts[-2],
                arrowprops=dict(arrowstyle="-|>" if arrow_end else "-", color=color, lw=lw, ls=ls,
                                shrinkA=0, shrinkB=0, mutation_scale=10))


def rbox(ax, x, y, w, h, fc, title, body="", fs=7.6, bfs=7.0, ec=INK, lw=1.0, ls="-"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc=fc, ec=ec, lw=lw, ls=ls))
    if body:
        ax.text(x + w / 2, y + h - 0.12, title, ha="center", va="top", fontsize=fs, weight="bold", color=INK)
        ax.text(x + w / 2, y + h - 0.47, body, ha="center", va="top", fontsize=bfs, color=INK,
                linespacing=1.25)
    else:
        ax.text(x + w / 2, y + h / 2, title, ha="center", va="center", fontsize=fs, weight="bold", color=INK)


# ----------------------------------------------------------------------------
# Figure 32.1 — analytics architecture
# ----------------------------------------------------------------------------
def fig_32_1():
    fig, ax = schematic(6.8, 5.0, xlim=(0, 17.2), ylim=(-0.3, 12.4))
    # --- left column: sources
    src_fc = tint(GREEN, "26")
    rbox(ax, 0.1, 9.5, 3.4, 2.4, src_fc, "Transformer\nmonitor", "", fs=7.6)
    ax.texts[-1].set_position((1.8, 11.45))
    ax.text(1.8, 10.85, "CT currents\nPT100 top-oil\nstatus · hourly", ha="center", va="top",
            fontsize=6.8, linespacing=1.25)
    rbox(ax, 0.1, 8.0, 3.4, 1.25, src_fc, "Weather service", "ambient grid")
    rbox(ax, 0.1, 6.4, 3.4, 1.25, src_fc, "DGA lab", "annual samples")
    rbox(ax, 0.1, 4.2, 3.4, 1.3, "#E8E8E8", "Head-end system")
    rbox(ax, 0.1, 1.9, 3.4, 1.75, "#E8E8E8", "Time-series store", "210 MB per year\nfor 1200 units")
    for yy in (10.7, 8.62, 7.02):
        ax.plot([3.5, 3.8], [yy, yy], color=INK, lw=1.1)
    ax.plot([3.8, 3.8], [10.7, 4.85], color=INK, lw=1.1)
    line(ax, [(3.8, 4.85), (3.52, 4.85)])
    line(ax, [(1.8, 4.2), (1.8, 3.67)])
    # --- data-quality gate
    rbox(ax, 4.4, 8.3, 3.7, 3.1, tint(YELLOW, "45"), "Data-quality gate",
         "gaps · stuck sensor\nspikes (Hampel)\nfleet-relative\ncalibration step")
    rbox(ax, 4.4, 6.75, 2.1, 0.9, tint(RED, "22"), "Quarantine", ec=RED, fs=7.6)
    line(ax, [(5.45, 8.3), (5.45, 7.67)], color=RED)
    ax.text(5.55, 7.98, "fail", fontsize=7, color=RED, va="center")
    line(ax, [(7.3, 8.3), (7.3, 6.12)])
    ax.text(7.4, 7.2, "pass", fontsize=7, va="center")
    # store -> gate
    line(ax, [(3.52, 2.75), (4.1, 2.75), (4.1, 9.6), (4.38, 9.6)])
    # --- feature pipeline
    rbox(ax, 4.4, 1.9, 3.7, 4.2, tint(SKY, "30"), "Feature pipeline",
         "$I^2$ loss term\nthermal filter, $\\tau$ = 3 h\ncalendar · lags\nIEC 60599\ngas ratios")
    # --- model registry (training, central)
    ax.add_patch(FancyBboxPatch((8.85, 1.9), 3.95, 9.5, boxstyle="round,pad=0.02,rounding_size=0.15",
                                fc="#F4F4F4", ec=INK, lw=1.0, ls=(0, (4, 2))))
    ax.text(10.83, 11.25, "Model registry", ha="center", va="top", fontsize=8.5, weight="bold")
    ax.text(10.83, 10.8, "(training, central)", ha="center", va="top", fontsize=7, color=GREY)
    mfc = tint(BLUE, "26")
    models = [("Grey-box top-oil", "3 parameters per unit"),
              ("Load forecaster", "ridge, 28 weights"),
              ("DGA classifier", "logistic, 25 weights"),
              ("Hot-spot surrogate", "RBF, 60 centres\ncentral only")]
    ys = [8.75, 6.85, 4.95, 2.15]
    hs = [1.45, 1.45, 1.45, 1.75]
    for (n, b), y, h in zip(models, ys, hs):
        rbox(ax, 9.05, y, 3.55, h, mfc if "surrogate" not in n else "#E8E8E8", n, b, fs=7.6, bfs=6.9)
    line(ax, [(8.12, 4.0), (8.83, 4.0)])
    ax.text(8.47, 4.2, "features", fontsize=6.6, ha="center", va="bottom", rotation=90)
    # --- gateway
    gx, gw = 14.35, 2.75
    ax.add_patch(FancyBboxPatch((gx, 4.9), gw, 6.5, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc=tint(ORANGE, "28"), ec=INK, lw=1.0))
    ax.text(gx + gw / 2, 11.25, "Substation\ngateway", ha="center", va="top", fontsize=8,
            weight="bold", linespacing=1.15)
    ax.text(gx + gw / 2, 10.25, "Cortex-A53, 1 GB", ha="center", va="top", fontsize=6.9, color=GREY)
    steps = ["predict", "residual", "CUSUM", "alarm"]
    for k, s_ in enumerate(steps):
        yy = 9.3 - 1.05 * k
        rbox(ax, gx + 0.35, yy - 0.35, gw - 0.7, 0.7, "#FFFFFF", s_, fs=7.4)
        if k:
            line(ax, [(gx + gw / 2, yy + 0.7), (gx + gw / 2, yy + 0.37)])
    rbox(ax, gx, 2.9, gw, 1.5, "#FFFFFF", "Fallback", "fixed top-oil\nthresholds", fs=7.8, bfs=7,
         ec=GREY, ls=(0, (3, 2)))
    line(ax, [(gx + gw / 2, 4.9), (gx + gw / 2, 4.42)], color=GREY, ls=(0, (3, 2)))
    # deployment arrows with version tags
    for yy in (9.47, 7.57, 5.67):
        line(ax, [(12.62, yy), (14.33, yy)], lw=1.3)
    ax.text(13.55, 11.35, "deploy", ha="center", va="top", fontsize=7.2, weight="bold")
    ax.text(13.55, 10.9, "model id\ndata hash\ncode hash", ha="center", va="top", fontsize=6.4,
            linespacing=1.2, bbox=dict(fc="white", ec=GREY, lw=0.6, boxstyle="round,pad=0.2"))
    # --- maintenance feedback
    rbox(ax, 4.6, -0.2, 6.9, 1.25, tint(PINK, "30"), "Maintenance records",
         "labels: about 15 confirmed faults per year")
    line(ax, [(gx + gw / 2, 2.9), (gx + gw / 2, 0.42), (11.52, 0.42)], color=PINK)
    ax.text(gx + gw / 2 - 0.15, 1.5, "alarms →"+chr(10)+"inspections", fontsize=6.6, color=PINK, ha="right",
            va="center")
    line(ax, [(10.8, 1.05), (10.8, 1.88)], color=PINK)
    ax.text(10.92, 1.45, "labels to training", fontsize=6.6, color=PINK, va="center")
    save(fig, "32", "fig-32-1-analytics-architecture")


# ----------------------------------------------------------------------------
# Figure 32.2 — heat-wave predictions (Listing 32.3)
# ----------------------------------------------------------------------------
def regression_unit0():
    from scipy.spatial import cKDTree
    amb, units = fleet()
    u = units[0]
    ok = ~np.isnan(u["theta"])
    phys = top_oil_rise(u["I"], 1.0, 6.0, 3.0)
    raw = np.column_stack([np.ones(H), u["I"], u["I"] ** 2, amb,
                           np.sin(2 * np.pi * hour / 24), np.cos(2 * np.pi * hour / 24)])
    X = {"knn": np.column_stack([day, hour, u["I"], amb]), "raw": raw,
         "phys": np.column_stack([np.ones(H), amb, phys])}

    def fit_predict(name, Xtr, ytr, Xte):
        if name == "knn":
            mu, sd = Xtr.mean(0), Xtr.std(0)
            _, idx = cKDTree((Xtr - mu) / sd).query((Xte - mu) / sd, k=5)
            return ytr[idx].mean(1)
        w = np.linalg.solve(Xtr.T @ Xtr + 1e-3 * np.eye(Xtr.shape[1]), Xtr.T @ ytr)
        return Xte @ w

    rng = np.random.default_rng(0)
    random_test = ok & (rng.random(H) < 0.2)
    mae = {}
    e = fit_predict("knn", X["knn"][ok & ~random_test], u["theta"][ok & ~random_test],
                    X["knn"][random_test]) - u["theta"][random_test]
    mae["kNN\nrandom"] = np.abs(e).mean()
    tr = ok & (day < 181)
    te = ok & (day >= 181) & (day < 273)
    heat = (day >= 200) & (day < 212)
    win = (day >= 195) & (day < 215)
    pred, hwmax = {}, {}
    for name in ("knn", "raw", "phys"):
        p_all = fit_predict(name, X[name][tr], u["theta"][tr], X[name])
        err = p_all[te] - u["theta"][te]
        mae[{"knn": "kNN\nblocked", "raw": "ridge\nraw", "phys": "ridge\nphysics"}[name]] = np.abs(err).mean()
        hwmax[name] = np.abs(err[heat[te]]).max()
        pred[name] = p_all
    amb_train_max = amb[day < 181].max()
    return dict(amb=amb, theta=u["theta"], pred=pred, mae=mae, hwmax=hwmax, win=win,
                heat=heat, te=te, amb_train_max=amb_train_max, train_theta_max=np.nanmax(u["theta"][tr]))


def fig_32_2():
    r = regression_unit0()
    w = r["win"]
    x = t[w] / 24.0
    fig, ax = plt.subplots(figsize=(6.8, 4.2))
    amb = r["amb"]
    atm = r["amb_train_max"]
    ax.axhline(atm, color=RED, lw=0.8, ls=":")
    ax.fill_between(x, atm, amb[w], where=amb[w] > atm, color=tint(RED, "40"), lw=0)
    ax.text(197.8, atm + 0.4, f"training max {atm:.1f} °C", fontsize=7.5, color=RED, va="bottom")
    ax.annotate("ambient outside\ntraining range", xy=(204.9, 31.0), xytext=(200.6, 33.2),
                fontsize=7.5, color=RED, ha="center", va="center",
                arrowprops=dict(arrowstyle="-", color=RED, lw=0.6))
    ax.plot(x, amb[w], color=GREY, ls="--", lw=1.0, label="ambient")
    ax.plot(x, r["theta"][w], color="k", lw=1.1, label="measured top-oil")
    ax.plot(x, r["pred"]["knn"][w], color=ORANGE, lw=1.2, label="kNN (day, hour, I, amb)")
    ax.plot(x, r["pred"]["phys"][w], color=BLUE, lw=1.0, ls=(0, (4, 1.5)), label="ridge on physics feature")
    # worst kNN error in the heat wave
    m = w & r["heat"] & r["te"]
    err = np.where(m, np.abs(r["pred"]["knn"] - r["theta"]), -1)
    i = int(np.nanargmax(err))
    ax.annotate("", xy=(t[i] / 24, r["theta"][i]), xytext=(t[i] / 24, r["pred"]["knn"][i]),
                arrowprops=dict(arrowstyle="<|-|>", color=ORANGE, lw=1.0, mutation_scale=8, shrinkA=0, shrinkB=0))
    ax.annotate(f"kNN error {r['hwmax']['knn']:.1f} K",
                xy=(t[i] / 24, (r["theta"][i] + r["pred"]["knn"][i]) / 2),
                xytext=(198.0, 60.0), fontsize=7.5, color=ORANGE, va="center",
                arrowprops=dict(arrowstyle="-", color=ORANGE, lw=0.6))
    j = int(np.nanargmax(np.where(w, r["theta"], -1)))
    ax.annotate(f"peak {r['theta'][j]:.1f} °C", xy=(t[j] / 24, r["theta"][j]),
                xytext=(200.0, 71.0), fontsize=7.5,
                arrowprops=dict(arrowstyle="-", color=INK, lw=0.6))
    k = int(np.argmax(np.where(w, amb, -99)))
    ax.annotate(f"ambient peak {amb[k]:.1f} °C", xy=(t[k] / 24, amb[k]),
                xytext=(210.4, 32.5), fontsize=7.5, color=GREY,
                arrowprops=dict(arrowstyle="-", color=GREY, lw=0.6))
    ax.text(214.8, 11.0, f"physics ridge: heat-wave max error {r['hwmax']['phys']:.1f} K",
            fontsize=7.5, color=BLUE, ha="right")
    ax.set_xlim(195, 215)
    ax.set_ylim(10, 80)
    ax.set_xticks(range(195, 216, 5))
    ax.set_xlabel("Day of year")
    ax.set_ylabel("Temperature (°C)")
    ax.legend(loc="upper left", fontsize=7.5, ncol=2, bbox_to_anchor=(0.0, 1.13))
    # inset bar chart
    ins = ax.inset_axes([0.735, 0.67, 0.255, 0.31])
    labels = list(r["mae"].keys())
    vals = list(r["mae"].values())
    cols = [ORANGE, ORANGE, GREY, BLUE]
    ins.bar(range(4), vals, color=cols, width=0.65)
    for kk, v in enumerate(vals):
        ins.text(kk, v + 0.05, f"{v:.2f}", ha="center", va="bottom", fontsize=6.3)
    ins.set_xticks(range(4))
    ins.set_xticklabels([lb.replace("random", "rand.").replace("blocked", "block.") for lb in labels], fontsize=5.8)
    ins.set_ylim(0, 2.7)
    ins.tick_params(axis="y", labelsize=6)
    ins.set_ylabel("MAE (K)", fontsize=6.5)
    ins.patch.set_alpha(0.9)
    save(fig, "32", "fig-32-2-heatwave-predictions")
    return r


# ----------------------------------------------------------------------------
# Figure 32.3 — DGA confusion matrices (Listing 32.4)
# ----------------------------------------------------------------------------
def dga():
    from scipy.optimize import minimize
    from scipy.special import logsumexp
    MEAN = np.array([[30, 10, 15, 5, 0.5], [300, 30, 10, 2, 0.5], [40, 120, 150, 30, 0.5],
                     [80, 200, 60, 400, 5], [400, 80, 10, 150, 200]])
    COUNT = [1700, 80, 120, 60, 40]

    def samples(seed):
        rng = np.random.default_rng(seed)
        y = np.repeat(np.arange(5), COUNT)
        gas = MEAN[y] * rng.lognormal(0, 0.6, (y.size, 5)) * rng.lognormal(0, 0.8, (y.size, 1))
        H2, CH4, C2H6, C2H4, C2H2 = gas.T
        X = np.column_stack([np.log(CH4 / H2), np.log(C2H2 / C2H4), np.log(C2H4 / C2H6),
                             np.log(gas.sum(1)), np.ones(y.size)])
        return X, y

    def train(X, y, balanced):
        w_s = (y.size / (5 * np.bincount(y)))[y] if balanced else np.ones(y.size)

        def loss(W):
            Z = X @ W.reshape(5, 5).T
            return -np.sum(w_s * (Z[np.arange(y.size), y] - logsumexp(Z, axis=1))) + 0.1 * np.sum(W ** 2)
        return minimize(loss, np.zeros(25), method="L-BFGS-B").x.reshape(5, 5)

    (Xtr, ytr), (Xte, yte) = samples(1), samples(2)
    out = {}
    for balanced in (False, True):
        pred = np.argmax(Xte @ train(Xtr, ytr, balanced).T, axis=1)
        C = np.zeros((5, 5))
        for a, b in zip(yte, pred):
            C[a, b] += 1
        out[balanced] = dict(C=C, acc=np.mean(pred == yte), bal=np.mean(np.diag(C) / C.sum(1)))
    return out, COUNT


def fig_32_3():
    res, COUNT = dga()
    names = ["normal", "PD", "T1", "T3", "D2"]
    fig, axs = plt.subplots(1, 2, figsize=(6.8, 3.6))
    for ax, bal in zip(axs, (False, True)):
        C = res[bal]["C"]
        F = C / C.sum(1, keepdims=True)
        im = ax.imshow(F, cmap="Blues", vmin=0, vmax=1)
        for i in range(5):
            for j in range(5):
                v = F[i, j]
                vr = float(np.round(v, 2))  # same rounding as Listing 32.4's printout
                txt = "0" if C[i, j] == 0 else ("<0.01" if vr == 0 else f"{vr:.2f}")
                ax.text(j, i, txt, ha="center", va="center", fontsize=7.5,
                        color="white" if v > 0.55 else INK, weight="bold" if i == j else None)
        ax.set_xticks(range(5))
        ax.set_xticklabels(names, fontsize=8)
        ax.set_yticks(range(5))
        ax.set_yticklabels([f"{n} ({c})" for n, c in zip(names, COUNT)], fontsize=8)
        ax.set_xlabel("Predicted class")
        ttl = "class-weighted" if bal else "unweighted"
        ax.set_title(f"{ttl}\naccuracy {res[bal]['acc']:.3f}, balanced {res[bal]['bal']:.3f}", fontsize=9)
        for s in ax.spines.values():
            s.set_visible(False)
        ax.tick_params(length=0)
    axs[0].set_ylabel("True class (test count)")
    axs[1].set_yticklabels([])
    cb = fig.colorbar(im, ax=axs, fraction=0.035, pad=0.03)
    cb.set_label("Row fraction", fontsize=8)
    cb.ax.tick_params(labelsize=7)
    save(fig, "32", "fig-32-3-dga-confusion")
    return res


# ----------------------------------------------------------------------------
# Figure 32.4 — day-ahead load forecast (Listing 32.5)
# ----------------------------------------------------------------------------
def forecast():
    amb, units = fleet()
    I = units[5]["I"].reshape(365, 24)
    A = amb.reshape(365, 24)
    rng = np.random.default_rng(1)
    A_fc = A + rng.normal(0, 1.5, A.shape)

    def features(d):
        weekend = np.full((24, 1), float(d % 7 >= 5))
        return np.column_stack([np.eye(24), I[d - 1], I[d - 7], A_fc[d], weekend])

    days = np.arange(7, 365)
    train, test = days[days < 273], days[days >= 273]
    X = np.vstack([features(d) for d in train])
    y = I[train].ravel()
    w = np.linalg.solve(X.T @ X + 0.1 * np.eye(X.shape[1]), X.T @ y)
    naive = lambda d: I[d - 7]  # noqa: E731
    ridge = lambda d: features(d) @ w  # noqa: E731
    mae_n = 100 * np.mean([np.abs(naive(d) - I[d]).mean() for d in test])
    mae_r = 100 * np.mean([np.abs(ridge(d) - I[d]).mean() for d in test])
    return I, naive, ridge, mae_n, mae_r, w.size


def fig_32_4():
    I, naive, ridge, mae_n, mae_r, nw = forecast()
    d0 = 308  # day % 7 == 0 -> Monday in Listing 32.1's calendar; day 0 = 1 Jan, so 5-11 November
    wk = range(d0, d0 + 7)
    meas = np.concatenate([I[d] for d in wk])
    fn = np.concatenate([naive(d) for d in wk])
    fr = np.concatenate([ridge(d) for d in wk])
    h = np.arange(168) + 0.5
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.8, 4.6), sharex=True,
                                 gridspec_kw=dict(height_ratios=[2.2, 1], hspace=0.1))
    a1.axvspan(120, 168, color="#F0F0F0", lw=0)
    a1.plot(h, meas, color="k", lw=1.3, label="measured")
    a1.plot(h, fn, color=GREY, ls="--", lw=1.1, label="seasonal naive (last week)")
    a1.plot(h, fr, color=BLUE, lw=1.2, label="ridge (lags, weather, calendar)")
    a1.set_ylim(0.3, 1.0)
    a1.set_ylabel("Load (p.u.)")
    a1.legend(loc="lower left", fontsize=7.5, ncol=3, bbox_to_anchor=(0, 0.0))
    for k, dn in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
        a1.text(24 * k + 12, 0.975, dn, ha="center", va="top", fontsize=7.5, color=INK)
        for a in (a1, a2):
            if k:
                a.axvline(24 * k, color="#DDDDDD", lw=0.7, zorder=0)
    a1.text(144, 0.935, "weekend", ha="center", va="top", fontsize=7.5, color=GREY)
    a2.axvspan(120, 168, color="#F0F0F0", lw=0)
    a2.plot(h, 100 * np.abs(fn - meas), color=GREY, ls="--", lw=1.0)
    a2.plot(h, 100 * np.abs(fr - meas), color=BLUE, lw=1.0)
    a2.set_ylabel("|error|\n(% of rating)")
    a2.set_xlabel("Hour of the week (5–11 November, Monday to Sunday)")
    a2.set_xlim(0, 168)
    a2.set_xticks(range(0, 169, 24))
    top = a2.get_ylim()[1]
    a2.set_ylim(0, top * 1.35)
    a2.text(167, top * 1.3, f"MAE, hold-out quarter Oct–Dec:  seasonal naive {mae_n:.2f} %   "
            f"ridge {mae_r:.2f} %\nthis week:  seasonal naive {100*np.abs(fn-meas).mean():.2f} %   "
            f"ridge {100*np.abs(fr-meas).mean():.2f} %", ha="right", va="top", fontsize=7,
            bbox=dict(fc="white", ec="none", alpha=0.85, pad=1))
    save(fig, "32", "fig-32-4-load-forecast")
    return mae_n, mae_r, nw


# ----------------------------------------------------------------------------
# Figure 32.5 — CUSUM (Listing 32.6)
# ----------------------------------------------------------------------------
def cusum(unit_ids=(0, 23, 31)):
    from scipy.optimize import least_squares
    amb, units = fleet()
    fit_days = day < 151
    out = {}
    for uid in unit_ids:
        u = units[uid]
        ok = ~np.isnan(u["theta"])
        model = lambda p: amb + top_oil_rise(u["I"], *p)  # noqa: E731
        p = least_squares(lambda p: (model(p) - u["theta"])[ok & fit_days], x0=[50, 6, 3],
                          bounds=([20, 1, 0.5], [90, 15, 10]), loss="soft_l1").x
        r = np.where(ok, u["theta"] - model(p), np.nan).reshape(365, 24)
        daily = np.nanmedian(r, axis=1)
        sigma = max(np.std(daily[151:181]), 0.5)
        S, Ss, alarm = 0.0, [], None
        for d in range(181, 365):
            S = max(0.0, S + daily[d] / sigma - 0.5)
            Ss.append(S)
            if S > 5.0 and alarm is None:
                alarm = d
        out[uid] = dict(daily=daily, S=np.array(Ss), alarm=alarm, sigma=sigma)
    return out


def fig_32_5():
    res = cusum()
    d = np.arange(181, 365)
    spec = [(31, RED, "unit 31: cooling fault"), (23, PURPLE, "unit 23: CT-ratio error"),
            (0, GREY, "unit 0: healthy")]
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.8, 4.6), sharex=True,
                                 gridspec_kw=dict(height_ratios=[1, 1.15], hspace=0.12))
    for uid, c, lab in spec:
        a1.plot(d, res[uid]["daily"][181:], color=c, lw=1.1, label=lab, marker=None)
    a1.axhline(0, color=INK, lw=0.6)
    a1.set_ylabel("Daily median\nresidual (K)")
    a1.legend(loc="upper left", fontsize=7.5, ncol=3, bbox_to_anchor=(0, 1.16))
    for uid, c, _ in spec[:2]:
        v0 = res[uid]["daily"][250]
        a1.annotate(f"{v0:.1f} K on day 250", xy=(250.5, v0), xytext=(256 if uid == 31 else 214, 2.4 if uid == 31 else 3.3),
                    fontsize=7.5, color=c, va="center",
                    arrowprops=dict(arrowstyle="-", color=c, lw=0.6))
    a1.text(364, 1.1, "faulty residuals grow as the winter load rises", fontsize=7, color=GREY, ha="right", va="center")
    a1.set_ylim(-1, 7.4)
    ytop = 12
    for uid, c, _ in spec:
        S = res[uid]["S"]
        a2.plot(d, np.minimum(S, ytop * 1.2), color=c, lw=1.3, clip_on=uid != 0, zorder=3)
    a2.axhline(5, color=INK, ls="--", lw=0.9)
    a2.text(183, 5.3, "alarm threshold S = 5", fontsize=7.5, va="bottom")
    for a in (a1, a2):
        a.axvline(250, color="#BBBBBB", lw=0.8, ls=":", zorder=0)
    a1.text(251, -0.85, "day 250", fontsize=7, color=GREY)
    al = sorted({res[u]["alarm"] for u in (23, 31)})
    a2.text(254, 8.2, (f"both faulty units cross on day {al[0]}" if len(al) == 1 else
            f"alarms on days {', '.join(map(str, al))}") + "\n(S keeps rising, off scale)",
            fontsize=7.5, va="center")
    smax = res[0]["S"].max()
    a2.text(184, 0.4, f"healthy unit 0: S ≤ {smax:.2f}, below 1", fontsize=7.5, color=GREY,
            va="bottom", ha="left")
    a2.set_ylim(0, ytop)
    a2.set_ylabel("CUSUM S")
    a2.set_xlabel("Day of year")
    a2.set_xlim(181, 365)
    a2.text(364, 3.0, "same signature, different cause:\nthe data-quality gate separates them",
            ha="right", va="center", fontsize=7.5, style="italic",
            bbox=dict(fc="white", ec=GREY, lw=0.6, boxstyle="round,pad=0.3"))
    save(fig, "32", "fig-32-5-cusum")
    return res


# ----------------------------------------------------------------------------
# Figure 32.6 — surrogate error (Listing 32.7)
# ----------------------------------------------------------------------------
def hot_spot_day(K_peak, amb_mean, d_or, R=6.0, n=0.8, Hgr=23.0, y=1.6, tau_o=3.0, tau_w=0.12):
    from scipy.integrate import solve_ivp
    K = lambda h: K_peak * (0.5 + 0.5 * np.exp(-(((h % 24) - 19) / 2.5) ** 2))  # noqa: E731
    amb = lambda h: amb_mean + 5 * np.sin(2 * np.pi * ((h % 24) - 9) / 24)  # noqa: E731

    def f(h, x):
        k = K(h)
        return [(d_or * ((1 + R * k ** 2) / (1 + R)) ** n - x[0]) / tau_o, (Hgr * k ** y - x[1]) / tau_w]
    sol = solve_ivp(f, (0, 72), [0.0, 0.0], method="LSODA", max_step=0.05, dense_output=True)
    h = np.linspace(48, 72, 1441)
    theta_h = amb(h) + sol.sol(h).sum(axis=0)
    ageing = np.trapezoid(2 ** ((theta_h - 98) / 6), h) / 24
    return theta_h.max(), np.log10(ageing)


def surrogate():
    from scipy.interpolate import RBFInterpolator
    from scipy.stats import qmc
    lo, hi = [0.6, 0.0, 45.0], [1.6, 40.0, 60.0]
    X_test = qmc.scale(np.random.default_rng(5).random((300, 3)), lo, hi)
    Y_test = np.array([hot_spot_day(*x) for x in X_test])
    scale = np.array(hi) - np.array(lo)
    out = {}
    for n in (30, 60, 120):
        X_train = qmc.scale(qmc.LatinHypercube(d=3, seed=4).random(n), lo, hi)
        Y_train = np.array([hot_spot_day(*x) for x in X_train])
        sur = RBFInterpolator(X_train / scale, Y_train, kernel="thin_plate_spline", degree=1)
        err = sur(X_test / scale) - Y_test
        out[n] = dict(err=err, mean=np.abs(err[:, 0]).mean(), max=np.abs(err[:, 0]).max())
    return X_test, Y_test, out


def fig_32_6():
    X_test, Y_test, out = surrogate()
    ns = [30, 60, 120]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.8, 3.6), gridspec_kw=dict(wspace=0.35))
    mean = [out[n]["mean"] for n in ns]
    mx = [out[n]["max"] for n in ns]
    a1.loglog(ns, mx, "o-", color=ORANGE, label="maximum |error|")
    a1.loglog(ns, mean, "s-", color=BLUE, label="mean |error|")
    for n, v in zip(ns, mx):
        a1.text(n * 1.07, v * (1.12 if n != 60 else 0.8), f"{v:.2f}", fontsize=7, color=ORANGE,
                va="bottom" if n != 60 else "top")
    for n, v in zip(ns, mean):
        a1.text(n * 1.07, v * 1.12, f"{v:.2f}", fontsize=7, color=BLUE, va="bottom")
    a1.axhline(3, color=ORANGE, ls="--", lw=0.9)
    a1.axhline(1, color=BLUE, ls="--", lw=0.9)
    a1.text(145, 3.2, "R6 max 3 K", fontsize=7, color=ORANGE, va="bottom", ha="right")
    a1.text(28, 0.93, "R6 mean 1 K", fontsize=7, color=BLUE, va="top", ha="left")
    a1.set_xlim(26, 150)
    a1.set_title("Peak hot-spot error vs. training runs", fontsize=9)
    a1.set_ylim(0.05, 8)
    a1.set_xticks(ns)
    a1.set_xticklabels([str(n) for n in ns])
    a1.minorticks_off()
    a1.set_yticks([0.05, 0.1, 0.3, 1, 3])
    a1.set_yticklabels(["0.05", "0.1", "0.3", "1", "3"])
    a1.set_xlabel("Training runs (Latin hypercube)")
    a1.set_ylabel("Peak hot-spot error (K)")
    a1.legend(loc="lower left", fontsize=7.5)
    # parity, 60-run surrogate
    err = out[60]["err"][:, 0]
    ref = Y_test[:, 0]
    sur = ref + err
    lo_, hi_ = 30, 170
    a2.plot([lo_, hi_], [lo_, hi_], color=INK, lw=0.8)
    a2.scatter(ref, sur, s=9, color=BLUE, alpha=0.7, lw=0)
    k = int(np.argmax(np.abs(err)))
    a2.scatter([ref[k]], [sur[k]], s=110, facecolor="none", edgecolor=RED, lw=1.3)
    x = X_test[k]
    a2.annotate(f"worst: {ref[k]:.1f} °C ref., error {err[k]:+.2f} K\ncorner of the box:\n"
                f"K {x[0]:.2f}, ambient {x[1]:.0f} °C, rise {x[2]:.0f} K",
                xy=(ref[k], sur[k]), xytext=(78, 42), fontsize=6.8, color=RED,
                arrowprops=dict(arrowstyle="-", color=RED, lw=0.7))
    a2.text(36, 160, f"60 runs, 300 test points\nmean |e| {out[60]['mean']:.2f} K, "
            f"max {out[60]['max']:.2f} K", fontsize=7, va="top")
    a2.set_xlim(lo_, hi_)
    a2.set_ylim(lo_, hi_)
    a2.set_aspect("equal")
    a2.set_xlabel("Reference peak hot spot (°C)")
    a2.set_ylabel("Surrogate peak hot spot (°C)")
    save(fig, "32", "fig-32-6-surrogate-error")
    return X_test, Y_test, out


if __name__ == "__main__":
    if len(sys.argv) > 1:
        for name in sys.argv[1:]:
            globals()[name]()
        sys.exit()
    fig_32_1()
    r = fig_32_2()
    print("32.2 MAE", {k.replace("\n", " "): round(v, 2) for k, v in r["mae"].items()},
          "hw max", {k: round(v, 1) for k, v in r["hwmax"].items()},
          "amb train max", round(r["amb_train_max"], 1), "theta train max", round(r["train_theta_max"], 1))
    d = fig_32_3()
    for b in (False, True):
        C = d[b]["C"]
        print("32.3", b, np.round(C / C.sum(1, keepdims=True), 2).tolist(), round(d[b]["acc"], 3), round(d[b]["bal"], 3))
    print("32.4", fig_32_4())
    c = fig_32_5()
    print("32.5", {u: (c[u]["alarm"], round(float(c[u]["S"].max()), 2), round(c[u]["sigma"], 2)) for u in c})
    X, Y, o = fig_32_6()
    print("32.6", {n: (round(o[n]["mean"], 2), round(o[n]["max"], 2)) for n in o},
          "range", Y[:, 0].min().round(1), Y[:, 0].max().round(1))
