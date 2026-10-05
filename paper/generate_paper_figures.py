"""
ModelVM — All 10 publication figures.
Pure matplotlib/numpy. Zero AI generation.
All sizes match the frozen physical spec (inches at 300 dpi -> vector PDF).
Run:  python generate_paper_figures.py
Outputs: fig1_architecture.pdf ... fig10_generalization.pdf
"""

import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import matplotlib.ticker as mticker
from matplotlib.patches import FancyBboxPatch
from mpl_toolkits.mplot3d import Axes3D, proj3d  # noqa: F401

HERE = os.path.dirname(os.path.abspath(__file__))

# ── frozen global rcParams ────────────────────────────────────────────────────
matplotlib.rcParams.update({
    "pdf.fonttype":        42,
    "ps.fonttype":         42,
    "font.family":         "sans-serif",
    "font.sans-serif":     ["Arial", "DejaVu Sans", "Liberation Sans"],
    "font.size":           8.0,
    "axes.linewidth":      0.6,
    "axes.edgecolor":      "#444444",
    "xtick.major.width":   0.6,
    "ytick.major.width":   0.6,
    "xtick.minor.width":   0.4,
    "ytick.minor.width":   0.4,
    "xtick.direction":     "out",
    "ytick.direction":     "out",
    "lines.linewidth":     1.0,
    "legend.fontsize":     7.0,
    "legend.framealpha":   0.9,
    "legend.edgecolor":    "#cccccc",
    "legend.borderpad":    0.4,
    "legend.handlelength": 1.2,
    "axes.spines.top":     False,
    "axes.spines.right":   False,
})

# ── frozen semantic palette ───────────────────────────────────────────────────
BLUE  = "#2C5F8A"   # ModelVM / primary
GREY  = "#888888"   # baselines
GREEN = "#1E6B3A"   # selected / positive
RED   = "#8B2020"   # rejected / OOM
MBLUE = "#4A7FA5"   # memory / storage
PURP  = "#5B4A8A"   # CSP / semantic state
LGREY = "#EEEEEE"   # alternating row fill
DARK  = "#222222"   # body text / rules

# ── CANONICAL GROUND-TRUTH DATA DICTIONARIES (TABLES 11, 12, 13, 14, H4) ──────
# Table 11 & Table 12 (EXP-H2 Residency & EXP-R1 Memory Sweep)
TABLE_12_SWEEP = {
    "budgets": [4.0, 6.0, 8.0, 10.0, 12.0, 16.0],
    "B5_ModelVM": {
        "quality": [0.885, 1.000, 1.000, 1.000, 1.000, 1.000],
        "paging_time": [14.80, 10.20, 7.20, 3.60, 1.20, 0.00],
        "reloads": [2.0, 1.0, 1.0, 0.0, 0.0, 0.0],
        "oom_rate": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    },
    "B4_Reactive_LRU": {
        "quality": [0.680, 0.920, 0.982, 1.000, 1.000, 1.000],
        "paging_time": [42.60, 28.40, 21.60, 15.40, 8.20, 0.00],
        "reloads": [7.2, 5.0, 4.0, 2.0, 1.0, 0.0],
        "oom_rate": [60.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    },
}

EXP_H2_TELEMETRY = {
    "B4_paging_stalls": 21.60,  # sec
    "B5_paging_stalls": 7.20,   # sec
    "paging_reduction_pct": 66.7, # (21.6 - 7.2)/21.6 = 66.7%
    "B4_hit_rate": 0.20,
    "B5_hit_rate": 0.60,
    "B4_reloads": 4.0,
    "B5_reloads": 1.0,
}

# Table 13 (EXP-R2 Transition Depth & Fact Retention)
TABLE_13_RETENTION = {
    "transitions": [1, 2, 4, 8, 12],  # W1, W2, W3, W4, W5
    "raw_text_facts": [0.940, 0.810, 0.460, 0.320, 0.180],
    "typed_csp_facts": [1.000, 1.000, 1.000, 0.960, 0.940],
    "typed_csp_calcs_at_12": 0.920,
    "decay_fit_lambda": 0.142,  # R_facts ≈ exp(-0.142 * N)
}

# Table 14 (EXP-R3 Scheduler Generalization Across Workloads)
TABLE_14_GENERALIZATION = {
    "workloads": ["W_A\n(Research)", "W_B\n(Compute)", "W_C\n(Coding)", "W_D\n(Mixed)"],
    "Capability_Greedy": [34.5, 54.2, 41.0, 48.2],  # % Regret vs Oracle
    "Memory_Aware": [12.4, 31.8, 18.2, 28.6],       # % Regret vs Oracle
    "ModelVM": [3.1, 7.8, 4.6, 6.4],                # % Regret vs Oracle
    "Offline_Oracle": [0.0, 0.0, 0.0, 0.0],         # Reference line
}

# Table 2 / Baseline Continuum (EXP-H4 3D Space)
BASELINES_H4 = {
    "B0_Monolith": {"M": 7.10, "L": 34.2, "Q": 0.562, "type": "constrained"},
    "B_static_Ensemble": {"M": 5.40, "L": 29.8, "Q": 0.624, "type": "constrained"},
    "B2_Dynamic_LRU": {"M": 7.60, "L": 62.4, "Q": 0.562, "type": "constrained"},
    "B4_CSP_LRU": {"M": 7.60, "L": 58.7, "Q": 0.982, "type": "constrained"},
    "B5_ModelVM": {"M": 7.60, "L": 43.8, "Q": 1.000, "type": "constrained"},
    # Out of budget insets:
    "B1_Unconstrained_Router": {"M": 19.80, "L": 36.4, "Q": 0.742, "type": "out_of_budget"},
    "B3_Unconstrained_Router_CSP": {"M": 19.80, "L": 38.1, "Q": 1.000, "type": "out_of_budget"},
}


# ── shared drawing helpers ────────────────────────────────────────────────────
def _bbox(ax, x, y, w, h, fc=LGREY, ec=DARK, lw=0.6, radius=0.015, zorder=2):
    style = f"round,pad={radius}"
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle=style, fc=fc, ec=ec, lw=lw, zorder=zorder, clip_on=False
    ))

def _rect(ax, x, y, w, h, fc=LGREY, ec=DARK, lw=0.5, zorder=2):
    ax.add_patch(mpatches.Rectangle(
        (x, y), w, h, fc=fc, ec=ec, lw=lw, zorder=zorder, clip_on=False
    ))

def _arrow(ax, x0, y0, x1, y1, color=DARK, lw=1.1, head=8, shrinkA=0, shrinkB=0, zorder=5):
    """Clean vector arrow with visible solid shaft and sharp arrowhead."""
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
                                mutation_scale=head, shrinkA=shrinkA, shrinkB=shrinkB),
                zorder=zorder)

def _hline(ax, y, x0, x1, lw=0.5, color="#bbbbbb"):
    ax.plot([x0, x1], [y, y], lw=lw, color=color, solid_capstyle="butt")

def _vline(ax, x, y0, y1, lw=0.5, color="#bbbbbb"):
    ax.plot([x, x], [y0, y1], lw=lw, color=color, solid_capstyle="butt")

def _savefig(name):
    path = os.path.join(HERE, name)
    plt.savefig(path, dpi=300, bbox_inches="tight", pad_inches=0.05)
    # also save a preview png
    png_path = os.path.join(HERE, name.replace(".pdf", "_preview.png"))
    plt.savefig(png_path, dpi=180, bbox_inches="tight", pad_inches=0.05)
    plt.close()
    print(f"  saved  {name}")


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 1 — Runtime Architecture    6.9" × 3.2"
# ══════════════════════════════════════════════════════════════════════════════
def fig1_architecture():
    fig = plt.figure(figsize=(6.9, 3.2))
    ax  = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")

    BX, BW, BH = 4, 64, 7.8
    CX = BX + BW / 2  # 36.0

    # 7 tiers evenly spaced from y=5 to y=89 (gap = 6.2 units)
    y_tiers = [89.0, 75.0, 61.0, 47.0, 33.0, 19.0, 5.0]

    # Level 0: User Task
    _bbox(ax, BX, y_tiers[0], BW, BH, fc=LGREY, ec=DARK, lw=0.9)
    ax.text(CX, y_tiers[0] + BH/2, "User Task / Goal", ha="center", va="center",
            fontsize=7.8, color=DARK)

    # Level 1: Cognitive Kernel
    _bbox(ax, BX, y_tiers[1], BW, BH, fc=LGREY, ec=DARK, lw=0.9)
    ax.text(CX, y_tiers[1] + BH/2, "Cognitive Kernel  —  Task Decomposer", ha="center", va="center",
            fontsize=7.8, color=DARK)

    # Level 2: WS Predictor & Scheduler
    HALF_W = (BW - 4) / 2  # 30.0
    _bbox(ax, BX, y_tiers[2], HALF_W, BH, fc=LGREY, ec=BLUE, lw=0.9)
    ax.text(BX + HALF_W/2, y_tiers[2] + BH/2,
            "Working-Set Predictor\n" + r"$W(t,k)$  · prefetch",
            ha="center", va="center", fontsize=7.0, color=DARK, linespacing=1.3)

    _bbox(ax, BX + HALF_W + 4, y_tiers[2], HALF_W, BH, fc=LGREY, ec=BLUE, lw=0.9)
    ax.text(BX + HALF_W + 4 + HALF_W/2, y_tiers[2] + BH/2,
            "Multi-Objective Scheduler\n" + r"$S(m)$",
            ha="center", va="center", fontsize=7.0, color=DARK, linespacing=1.3)

    # horizontal arrow between WS and Sched
    _arrow(ax, BX + HALF_W, y_tiers[2] + BH/2, BX + HALF_W + 4, y_tiers[2] + BH/2,
           color=BLUE, lw=1.1, head=7)

    # Level 3: Model Pager
    _bbox(ax, BX, y_tiers[3], BW, BH, fc="#EBF3FA", ec=MBLUE, lw=0.9)
    ax.text(CX, y_tiers[3] + BH/2, "Model Pager  (Residency + Cost-Aware Eviction + Prefetch)",
            ha="center", va="center", fontsize=7.5, color=DARK)

    # Level 4: Resident Specialist
    _bbox(ax, BX, y_tiers[4], BW, BH, fc=LGREY, ec=DARK, lw=0.9)
    ax.text(CX, y_tiers[4] + BH/2, "Resident Specialist  (Inference)",
            ha="center", va="center", fontsize=7.8, color=DARK)

    # Level 5: AST Verifier
    _bbox(ax, BX, y_tiers[5], BW, BH, fc=LGREY, ec=PURP, lw=0.9)
    ax.text(CX, y_tiers[5] + BH/2, "AST Verifier  +  State Merge",
            ha="center", va="center", fontsize=7.8, color=DARK)

    # Level 6: S_{t+1}
    _bbox(ax, CX - 20, y_tiers[6], 40, BH, fc="#F0ECF8", ec=PURP, lw=1.0)
    ax.text(CX, y_tiers[6] + BH/2, r"$S_{t+1}$  (next CSP state)",
            ha="center", va="center", fontsize=7.8, color=PURP, fontweight="bold")

    # Vertical arrows down the central pipeline
    # Tier 0 -> Tier 1 (User Task to Cognitive Kernel)
    _arrow(ax, CX, y_tiers[0], CX, y_tiers[1] + BH, color=DARK, lw=1.1, head=8)

    # Tier 1 -> Tier 2: Cognitive Kernel forks into Working-Set Predictor (left) and Scheduler (right)
    x_ws = BX + HALF_W / 2
    x_sc = BX + HALF_W + 4 + HALF_W / 2
    _arrow(ax, x_ws, y_tiers[1], x_ws, y_tiers[2] + BH, color=DARK, lw=1.1, head=7)
    _arrow(ax, x_sc, y_tiers[1], x_sc, y_tiers[2] + BH, color=DARK, lw=1.1, head=7)

    # Tier 2 -> Tier 3: Working-Set Predictor (lookahead/shield) & Scheduler (selected model) feed into Model Pager
    _arrow(ax, x_ws, y_tiers[2], x_ws, y_tiers[3] + BH, color=DARK, lw=1.1, head=7)
    _arrow(ax, x_sc, y_tiers[2], x_sc, y_tiers[3] + BH, color=DARK, lw=1.1, head=7)

    # Tier 3 -> Tier 4 (Model Pager to Resident Specialist)
    _arrow(ax, CX, y_tiers[3], CX, y_tiers[4] + BH, color=DARK, lw=1.1, head=8)

    # Tier 4 -> Tier 5 (Resident Specialist to AST Verifier)
    _arrow(ax, CX, y_tiers[4], CX, y_tiers[5] + BH, color=DARK, lw=1.1, head=8)

    # Tier 5 -> Tier 6 (AST Verifier to S_{t+1})
    _arrow(ax, CX, y_tiers[5], CX, y_tiers[6] + BH, color=PURP, lw=1.1, head=8)

    # Right gutter: Memory Hierarchy
    mx, mw, mh = 77, 18, 7.8
    ax.text(mx + mw/2, 89.5, "Memory\nHierarchy",
            ha="center", va="center", fontsize=6.8, color=DARK, style="italic")

    vram_y = y_tiers[2] # 61.0
    ram_y  = y_tiers[3] # 47.0 (matches Model Pager!)
    ssd_y  = y_tiers[4] # 33.0

    _bbox(ax, mx, vram_y, mw, mh, fc="#DDEEFF", ec=BLUE, lw=0.9)
    ax.text(mx + mw/2, vram_y + mh/2, "VRAM", ha="center", va="center",
            fontsize=7.2, color=DARK)

    # Host RAM box
    _bbox(ax, mx, ram_y, mw, mh, fc="#EAF3FA", ec=MBLUE, lw=0.9)
    ax.text(mx + mw/2, ram_y + mh/2, "Host RAM", ha="center", va="center",
            fontsize=7.2, color=DARK)

    # Host RAM budget bracket and label (explicitly attached to Host RAM!)
    ax.add_patch(mpatches.Rectangle((mx - 1.2, ram_y - 1.2), mw + 2.4, mh + 2.4,
                                   fc="none", ec=RED, lw=1.0, ls="--", zorder=3))
    ax.text(mx + mw + 2.2, ram_y + mh/2, r"$\mathcal{B}_{\mathrm{RAM}} = 8.0$ GB" + "\n(active budget)",
            ha="left", va="center", fontsize=5.8, color=RED, fontweight="bold", linespacing=1.2)

    _bbox(ax, mx, ssd_y, mw, mh, fc="#F0F0F0", ec=GREY, lw=0.9)
    ax.text(mx + mw/2, ssd_y + mh/2, "NVMe SSD", ha="center", va="center",
            fontsize=7.2, color=DARK)

    # Vertical arrows in memory hierarchy
    _arrow(ax, mx + mw/2, vram_y, mx + mw/2, ram_y + mh + 1.2, color=GREY, lw=1.0, head=7)
    _arrow(ax, mx + mw/2, ram_y - 1.2,  mx + mw/2, ssd_y + mh, color=GREY, lw=1.0, head=7)

    # Clean horizontal arrow from Model Pager to Host RAM
    _arrow(ax, BX + BW, ram_y + mh/2, mx - 1.2, ram_y + mh/2, color=MBLUE, lw=1.2, head=8)
    ax.text((BX + BW + mx)/2, ram_y + mh/2 + 2.2, "swap / page",
            ha="center", va="bottom", fontsize=5.8, color=MBLUE, style="italic")

    _savefig("fig1_architecture.pdf")


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 2 — CSP & Cross-Model State Boundary    3.35" × 2.4"
# ══════════════════════════════════════════════════════════════════════════════
def fig2_csp():
    fig = plt.figure(figsize=(3.35, 2.4))
    axL = fig.add_axes([0.01, 0.09, 0.50, 0.91])
    axR = fig.add_axes([0.53, 0.09, 0.46, 0.91])
    for ax in (axL, axR):
        ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")

    # LEFT: 9-tuple table
    axL.text(50, 99, "Cognitive State Packet",
             ha="center", va="top", fontsize=6.8, fontweight="bold", color=DARK)
    axL.text(50, 93,
             r"$S_t = \langle G,\,F_t,\,C_t,\,E_t,\,A_t,\,U_t,\,D_t,\,Q_t,\,O_t \rangle$",
             ha="center", va="top", fontsize=5.8, color=BLUE)

    rows = [
        ("G",  "goal",       "Immutable task goal"),
        ("F",  "facts",      "Verified fact set"),
        ("C",  "calcs",      "AST-checked arithmetic"),
        ("E",  "evidence",   "Claims + confidence"),
        ("A",  "assumes",    "Modelling assumptions"),
        ("U",  "risks",      "Risks / ambiguities"),
        ("D",  "decisions",  "Committed choices"),
        ("Q",  "open_q",     "Unresolved questions"),
        ("O",  "artifacts",  "Versioned key-value"),
    ]
    TX, TW = 1, 98
    CW = [10, 27, 61]
    TBL_TOP = 87
    HDR_H   = 6.8
    ROW_H   = 7.5

    _rect(axL, TX, TBL_TOP, TW, HDR_H, fc=BLUE, ec=BLUE, lw=0)
    cx = TX
    for cw, lbl in zip(CW, ["Sym", "Field", "Description"]):
        axL.text(cx + cw/2, TBL_TOP + HDR_H/2, lbl,
                 ha="center", va="center", fontsize=5.8,
                 fontweight="bold", color="white")
        cx += cw

    for r, (sym, field, desc) in enumerate(rows):
        yt = TBL_TOP - ROW_H * (r + 1)
        fc = "white" if r % 2 == 0 else LGREY
        _rect(axL, TX, yt, TW, ROW_H, fc=fc, ec="#cccccc", lw=0.3)
        cx = TX
        sym_str = "$G$" if sym == "G" else f"${sym}_t$"
        axL.text(cx + CW[0]/2, yt + ROW_H/2, sym_str,
                 ha="center", va="center", fontsize=6.0, color=PURP)
        cx += CW[0]
        axL.text(cx + 1.2, yt + ROW_H/2, field,
                 ha="left", va="center", fontsize=5.4, color=DARK, fontfamily="monospace")
        cx += CW[1]
        axL.text(cx + 1.2, yt + ROW_H/2, desc,
                 ha="left", va="center", fontsize=5.3, color=GREY)

    TBOT = TBL_TOP - ROW_H * len(rows)
    _vline(axL, TX,           TBOT, TBL_TOP + HDR_H, lw=0.8, color=DARK)
    _vline(axL, TX + TW,      TBOT, TBL_TOP + HDR_H, lw=0.8, color=DARK)
    _hline(axL, TBL_TOP + HDR_H, TX, TX + TW, lw=0.8, color=BLUE)
    _hline(axL, TBOT, TX, TX + TW, lw=0.8, color=DARK)
    _vline(axL, TX + CW[0],         TBOT, TBL_TOP + HDR_H, lw=0.3, color="#aaaaaa")
    _vline(axL, TX + CW[0] + CW[1], TBOT, TBL_TOP + HDR_H, lw=0.3, color="#aaaaaa")

    axL.text(50, TBOT - 2.5,
             r"$H_t$ (trace log) metadata stored in Host RAM",
             ha="center", va="top", fontsize=5.2, color=GREY, style="italic")

    # RIGHT: serialisation pipeline
    axR.text(50, 99, "Cross-Model Handoff",
             ha="center", va="top", fontsize=6.8, fontweight="bold", color=DARK)

    pipe_yc = [86, 68, 50, 32, 14]
    pipe = [
        ("Upstream  $M_A$\n(vocab $V_A$,  state $h_A$)",
         pipe_yc[0], LGREY,     BLUE),
        ("Candidate  $\\Delta S_t$",
         pipe_yc[1], "#EDF4FB", MBLUE),
        ("AST Verifier\n" + r"$|y_{comp} - y_{decl}| \leq \varepsilon$",
         pipe_yc[2], "#EAF2E8", GREEN),
        ("CSP  to_prompt_context()",
         pipe_yc[3], "#F3F0FA", PURP),
        ("Downstream  $M_B$\n($V_B \\neq V_A$,  $h_B$ independent)",
         pipe_yc[4], LGREY,     BLUE),
    ]
    PW, PH = 92, 10.5
    PX = 4
    for label, yc, fc, ec in pipe:
        _bbox(axR, PX, yc - PH/2, PW, PH, fc=fc, ec=ec, lw=0.8)
        axR.text(PX + PW/2, yc, label,
                 ha="center", va="center", fontsize=5.6, color=DARK,
                 linespacing=1.25)

    arrow_labels = [
        r"$\Delta S_t$ proposed",
        r"$\Delta S_t^{*}$ certified",
        "serialised context",
        "no hidden-state bridge",
    ]
    for i, lbl in enumerate(arrow_labels):
        y0 = pipe_yc[i]   - PH/2
        y1 = pipe_yc[i+1] + PH/2
        _arrow(axR, 32, y0, 32, y1, color=BLUE, lw=1.0, head=7)
        axR.text(38, (y0 + y1)/2, lbl,
                 ha="left", va="center", fontsize=5.2,
                 color=DARK, style="italic")

    fig.text(0.50, 0.03,
             "Architecture-agnostic semantic handoff  |  Bounded state loss  |  Bounded drift",
             ha="center", va="bottom", fontsize=5.8,
             color=GREEN, fontweight="bold")

    fig.add_artist(mlines.Line2D(
        [0.515, 0.515], [0.08, 0.99],
        transform=fig.transFigure,
        color="#bbbbbb", lw=0.7, ls="--"
    ))

    _savefig("fig2_csp.pdf")


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 3 — Scheduler Decision    3.35" × 2.15"
# ══════════════════════════════════════════════════════════════════════════════
def fig3_scheduler():
    fig = plt.figure(figsize=(3.35, 2.15))
    ax  = fig.add_axes([0.01, 0.01, 0.98, 0.98])
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")

    ax.text(50, 96, "Illustrative scheduler decision — catalog manifests",
            ha="center", va="top", fontsize=6.5, fontweight="bold", color=DARK)

    ax.text(50, 89,
            r"$S(m) = F_{cap} - \alpha M_{cost} - \beta L_{load} - \gamma E_{cost}$",
            ha="center", va="top", fontsize=6.0, color=DARK)
    ax.text(50, 83.5,
            r"$- \delta P_{evict} + \eta F_{fut}$"
            r"   $[\alpha{=}0.20,\,\beta{=}0.25,\,\gamma{=}0.10,\,\delta{=}0.30,\,\eta{=}0.35]$",
            ha="center", va="top", fontsize=5.8, color=DARK)

    ax.text(50, 78.0,
            r"Stage: math derivation  |  $B_{RAM}=8.0$ GB  |  Resident: research-expert",
            ha="center", va="top", fontsize=5.3, color=GREY, style="italic")

    TX, TW  = 1, 98
    HDR_H   = 7.0
    ROW_H   = 8.2
    TBL_TOP = 68

    col_labels = ["Candidate", r"$F_{\mathrm{cap}}$", r"$\alpha M$", r"$\beta L$", r"$\gamma E$", r"$\delta P$", r"$\eta F$", "Total", "Status"]
    col_w      = [26,  7.5,  7.5,  7.5,  7.0,  7.0,  7.5,  10.0,  18.0]

    _rect(ax, TX, TBL_TOP, TW, HDR_H, fc=DARK, ec=DARK, lw=0)
    cx = TX
    for cw, lbl in zip(col_w, col_labels):
        ax.text(cx + cw/2, TBL_TOP + HDR_H/2, lbl,
                ha="center", va="center", fontsize=5.8,
                fontweight="bold", color="white")
        cx += cw

    catalog_rows = [
        ("math-expert",     "+0.96", "-0.06", "-0.05", "-0.02", "0.00", "0.00", "+0.83",
         "SELECTED",     "#EAF2E8", GREEN),
        ("coding-expert",   "+0.05", "-0.08", "-0.06", "-0.02", "0.00", "+0.35", "+0.25",
         "AVAILABLE",    LGREY,    GREY),
        ("research-expert", "+0.05", "-0.08", "0.00",  "-0.02", "0.00", "0.00", "-0.05",
         "RESIDENT",     "white",  GREY),
        ("general-reasoner","+0.46", "-0.18", "-0.11", "-0.03", "-0.08", "0.00", "+0.06",
         "OUTSCORED",    "#FDF0F0", RED),
    ]

    for r_idx, (name, cap, ram, load, eng, evict, fut, total, outcome, fc, badge_c) in enumerate(catalog_rows):
        yt = TBL_TOP - ROW_H * (r_idx + 1)
        ec = GREEN if outcome == "SELECTED" else ("#cccccc" if fc != "#FDF0F0" else RED)
        lw = 0.9 if outcome == "SELECTED" else 0.4
        _rect(ax, TX, yt, TW, ROW_H, fc=fc, ec=ec, lw=lw)

        vals = [name, cap, ram, load, eng, evict, fut, total]
        cx   = TX
        for i, (cw, v) in enumerate(zip(col_w, vals)):
            fa = "monospace" if i == 0 else "sans-serif"
            fs = 5.2 if (i == 0 and len(name) > 12) else (5.6 if i == 0 else 6.0)
            try:
                num = float(v)
                vc = GREEN if num > 0 else (RED if num < 0 else DARK)
            except ValueError:
                vc = DARK
            ha = "left" if i == 0 else "center"
            xo = 1.0 if i == 0 else 0
            ax.text(cx + xo + (cw/2 if i else 0), yt + ROW_H/2, v,
                    ha=ha, va="center", fontsize=fs, color=vc, fontfamily=fa)
            cx += cw

        badge_x = TX + sum(col_w[:8])
        badge_w = col_w[8]
        ax.text(badge_x + badge_w/2, yt + ROW_H/2, outcome,
                ha="center", va="center", fontsize=4.8 if len(outcome) > 9 else 5.2,
                fontweight="bold", color=badge_c)

    TBOT = TBL_TOP - ROW_H * len(catalog_rows)
    _vline(ax, TX,      TBOT, TBL_TOP + HDR_H, lw=0.8, color=DARK)
    _vline(ax, TX + TW, TBOT, TBL_TOP + HDR_H, lw=0.8, color=DARK)
    _hline(ax, TBOT, TX, TX + TW, lw=0.7, color=DARK)
    cx = TX
    for cw in col_w[:-1]:
        cx += cw
        _vline(ax, cx, TBOT, TBL_TOP, lw=0.3, color="#aaaaaa")

    ax.text(TX, TBOT - 4.0,
            "general-reasoner admissible under 8.0 GB budget, but outscored by memory cost (7.1 GB) and eviction deficit (2.2 GB deficit vs 4.9 GB free RAM).",
            ha="left", va="top", fontsize=5.0, color=GREY, style="italic")

    _savefig("fig3_scheduler.pdf")


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 4 — Runtime Control Path    6.9" × 2.8"
# ══════════════════════════════════════════════════════════════════════════════
def fig4_control_path():
    fig = plt.figure(figsize=(6.9, 2.8))
    ax  = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 140); ax.set_ylim(0, 100); ax.axis("off")

    TOP_Y = 70
    BOT_Y = 26
    BH    = 11.5

    def rnode(cx, cy, label, fc=LGREY, ec=DARK, fontsize=6.8, lw=0.8, width=17, height=BH):
        _bbox(ax, cx - width/2, cy - height/2, width, height,
              fc=fc, ec=ec, lw=lw, radius=0.012)
        ax.text(cx, cy, label, ha="center", va="center",
                fontsize=fontsize, color=DARK, linespacing=1.3)

    def diamond(cx, cy, label, hw=9, hh=6.5):
        xs = [cx, cx+hw, cx, cx-hw, cx]
        ys = [cy+hh, cy, cy-hh, cy, cy+hh]
        ax.fill(xs, ys, fc="#FFFBE6", ec="#9A7D00", lw=0.8, zorder=3)
        ax.text(cx, cy, label, ha="center", va="center",
                fontsize=6.2, color=DARK, fontweight="bold")

    # Top row mainline
    rnode(12,  TOP_Y, "PLAN\nTask G", width=15)
    rnode(32,  TOP_Y, "FORECAST\n$W(t,k)$", width=16)
    rnode(53,  TOP_Y, "SELECT\nSpecialist", width=16)
    diamond(74, TOP_Y, "RESIDENT\n?", hw=9, hh=6.5)
    rnode(96,  TOP_Y, "EXECUTE\nInference", width=17)
    rnode(118, TOP_Y, "AST\nVERIFY", width=16)

    # Top row mainline arrows
    _arrow(ax, 12 + 15/2, TOP_Y, 32 - 16/2, TOP_Y, color=DARK, lw=1.1, head=7)
    _arrow(ax, 32 + 16/2, TOP_Y, 53 - 16/2, TOP_Y, color=DARK, lw=1.1, head=7)
    _arrow(ax, 53 + 16/2, TOP_Y, 74 - 9,    TOP_Y, color=DARK, lw=1.1, head=7)
    _arrow(ax, 74 + 9,    TOP_Y, 96 - 17/2, TOP_Y, color=GREEN, lw=1.1, head=7)
    ax.text(85, TOP_Y + 2.0, "YES", fontsize=5.8, color=GREEN, fontweight="bold", ha="center")
    _arrow(ax, 96 + 17/2, TOP_Y, 118 - 16/2, TOP_Y, color=DARK, lw=1.1, head=7)

    # From AST Verify down to State Merge
    _arrow(ax, 118, TOP_Y - BH/2, 118, BOT_Y + BH/2, color=PURP, lw=1.1, head=7)

    # Bottom row
    rnode(53,  BOT_Y, "ADMISSION\nCheck", width=16)
    diamond(74, BOT_Y, "EVICT\n?", hw=9, hh=6.5)
    rnode(96,  BOT_Y, "PAGE-IN\nSpecialist", fc="#EAF2EA", ec=GREEN, lw=0.9, width=17)
    rnode(118, BOT_Y, "STATE\nMERGE", fc="#F3F0FA", ec=PURP, lw=0.9, width=16)
    diamond(134, BOT_Y, "CONF\nOK?", hw=6.5, hh=5.5)

    # Resident NO branch: from Resident? down and into Admission Check
    ax.plot([74, 74, 53, 53], [TOP_Y - 6.5, 48, 48, BOT_Y + BH/2 + 2],
            lw=1.0, color=RED, solid_capstyle="round")
    _arrow(ax, 53, BOT_Y + BH/2 + 2, 53, BOT_Y + BH/2, color=RED, lw=1.0, head=7)
    ax.text(75.5, 56, "NO (miss)", fontsize=5.8, color=RED, ha="left", va="center", fontweight="bold")

    # Admission -> Evict?
    _arrow(ax, 53 + 16/2, BOT_Y, 74 - 9, BOT_Y, color=DARK, lw=1.0, head=7)

    # Evict NO -> Page-In (headroom available)
    _arrow(ax, 74 + 9, BOT_Y, 96 - 17/2, BOT_Y, color=DARK, lw=1.0, head=7)
    ax.text(85, BOT_Y + 1.8, "NO", fontsize=5.5, color=DARK, ha="center")

    # Evict YES (loop underneath)
    ax.plot([74, 74, 85, 85], [BOT_Y - 6.5, BOT_Y - 10, BOT_Y - 10, BOT_Y - 2],
            lw=0.8, color="#9A7D00", ls="--", solid_capstyle="round")
    _arrow(ax, 85, BOT_Y - 2, 96 - 17/2, BOT_Y - 2, color="#9A7D00", lw=0.8, head=6)
    ax.text(79.5, BOT_Y - 12.5, "YES: cost-aware eviction", fontsize=5.2, color="#9A7D00", ha="center")

    # Page-In -> vertical up into Execute Inference! (Unobstructed now)
    _arrow(ax, 96, BOT_Y + BH/2, 96, TOP_Y - BH/2, color=GREEN, lw=1.2, head=8)
    ax.text(98.5, (TOP_Y + BOT_Y)/2, "Weights resident", fontsize=5.6, color=GREEN,
            ha="left", va="center", fontweight="bold")

    # State Merge -> Confidence diamond
    _arrow(ax, 118 + 16/2, BOT_Y, 134 - 6.5, BOT_Y, color=PURP, lw=1.0, head=7)

    # Confidence PASS -> Next stage
    ax.plot([134, 134], [BOT_Y - 5.5, 10], lw=1.1, color=GREEN)
    _arrow(ax, 134, 10, 134, 4, color=GREEN, lw=1.1, head=7)
    ax.text(134, 1.0, "NEXT STAGE", ha="center", va="top", fontsize=6.2,
            fontweight="bold", color=GREEN)
    ax.text(135.5, 12, "PASS", fontsize=5.5, color=GREEN, ha="left", fontweight="bold")

    # Confidence FAIL -> Escalate retry loop ROUTED ABOVE TOP ROW (ZERO OVERLAP!)
    ax.plot([134 + 6.5, 138, 138, 53, 53],
            [BOT_Y, BOT_Y, 87, 87, TOP_Y + BH/2 + 2],
            lw=0.9, color=RED, ls="--", solid_capstyle="round")
    _arrow(ax, 53, TOP_Y + BH/2 + 2, 53, TOP_Y + BH/2, color=RED, lw=0.9, head=7)
    ax.text(95, 89.0, r"ESCALATE (retry with $M_{esc}$, $N_{esc} \leq 2$)",
            fontsize=5.6, color=RED, ha="center", va="bottom", fontweight="bold")
    ax.text(139.5, BOT_Y + 10, "FAIL", fontsize=5.5, color=RED, ha="left", fontweight="bold")

    _savefig("fig4_control_path.pdf")


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 5 — Factorial Decomposition    6.9" × 3.4"
# ══════════════════════════════════════════════════════════════════════════════
def fig5_ablation():
    fig, axes = plt.subplots(1, 3, figsize=(6.9, 3.4),
                             gridspec_kw={"wspace": 0.54, "left": 0.07,
                                          "right": 0.97, "top": 0.88,
                                          "bottom": 0.18})

    # (a) Quality factor effects
    ax = axes[0]
    factors = ["A\n(CSP)", "B\n(WS)", "C\n(Sched)", r"B$\times$C"]
    effects = [+0.438, +0.042, +0.031, +0.008]
    ci      = [ 0.021,  0.015,  0.015,  0.009]
    bar_c   = [BLUE, MBLUE, GREY, "#aaaaaa"]
    x       = np.arange(len(factors))

    ax.bar(x, effects, yerr=ci, width=0.55,
           color=bar_c, edgecolor=DARK, lw=0.5,
           capsize=3.0, error_kw={"lw": 0.8, "ecolor": DARK}, zorder=3)
    ax.axhline(0, color=DARK, lw=0.5, zorder=2)
    ax.set_xticks(x); ax.set_xticklabels(factors, fontsize=7.5)
    ax.set_ylabel(r"$\Delta Q$  (main effect)", fontsize=7.5)
    ax.set_title("(a)  Quality effects", fontsize=8.5, fontweight="bold", pad=6)
    ax.set_ylim(-0.05, 0.52)
    ax.yaxis.set_major_locator(mticker.MultipleLocator(0.1))
    ax.grid(axis="y", color="#e8e8e8", lw=0.4, zorder=0)
    ax.set_axisbelow(True)

    # Clean annotation box in open right-center whitespace
    ax.text(0.95, 0.42,
            "Factor A: 96.8 %\nof treatment SS",
            fontsize=6.0, color=BLUE, ha="left", va="center",
            bbox=dict(fc="white", ec=BLUE, lw=0.6, pad=2.5))
    _arrow(ax, 0.95, 0.42, 0.35, 0.438, color=BLUE, lw=0.8, head=6)
    ax.text(0, 0.438 + 0.028, "+0.438", ha="center", va="bottom",
            fontsize=6.2, color=BLUE, fontweight="bold")

    # (b) Paging main effects
    ax = axes[1]
    p_factors = [r"$\Delta_B$ (WS)", r"$\Delta_C$ (Sched)", r"$\Delta_{BC}$ (WS$\times$Sched)"]
    p_effects = [-9.43, -6.44, -0.70]
    p_ci      = [ 0.33,   0.33,   0.33]
    p_bar_c   = ["#8B2020", "#8B2020", "#BC6B6B"]
    y_pos     = np.arange(len(p_factors))

    ax.barh(y_pos, p_effects, xerr=p_ci, height=0.50,
            color=p_bar_c, edgecolor=DARK, lw=0.5,
            capsize=3.0, error_kw={"lw": 0.8, "ecolor": DARK}, zorder=3)
    ax.axvline(0, color=DARK, lw=0.5, zorder=2)
    ax.set_yticks(y_pos); ax.set_yticklabels(p_factors, fontsize=7.5)
    ax.set_xlabel("Seconds  (negative = reduction)", fontsize=7.5)
    ax.set_title("(b)  Paging stall — factorial", fontsize=8.5, fontweight="bold", pad=6)
    ax.set_xlim(-13.5, 1.0)
    ax.xaxis.set_major_locator(mticker.MultipleLocator(4))
    ax.grid(axis="x", color="#e8e8e8", lw=0.4, zorder=0)
    ax.set_axisbelow(True)

    # Value labels safely to the left of the error caps (zero overlap!)
    for yi, (ve, vc) in enumerate(zip(p_effects, p_ci)):
        ax.text(ve - vc - 0.6, yi, f"{ve:.2f} s",
                ha="right", va="center", fontsize=6.2, color=DARK)

    # (c) Interaction matrix (100% pure vector patches, zero raster objects!)
    ax = axes[2]
    matrix = np.array([[24.8, 19.0],
                       [16.2,  7.2]])
    cmap = plt.cm.Blues_r
    norm = matplotlib.colors.Normalize(vmin=5, vmax=28)
    for i in range(2):
        for j in range(2):
            val = matrix[i, j]
            color = cmap(norm(val))
            ax.add_patch(mpatches.Rectangle((j - 0.5, i - 0.5), 1.0, 1.0,
                                           facecolor=color, edgecolor="#cccccc", lw=0.6, zorder=1))
            tc = "white" if val < 13 else DARK
            ax.text(j, i, f"{val:.1f} s", ha="center", va="center",
                    fontsize=8.5, fontweight="bold", color=tc, zorder=2)

    ax.set_xlim(-0.5, 1.5)
    ax.set_ylim(1.5, -0.5)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["Scheduler\nOFF", "Scheduler\nON"], fontsize=7.5)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["WS\nOFF", "WS\nON"], fontsize=7.5)
    ax.set_title(r"(c)  WS $\times$ Sched (stall, s)", fontsize=8.5, fontweight="bold", pad=6)

    pos = ax.get_position()
    cax = fig.add_axes([pos.x1 + 0.02, pos.y0, 0.016, pos.height])
    n_steps = 25
    step_h = (28.0 - 5.0) / n_steps
    for k in range(n_steps):
        v_bot = 5.0 + k * step_h
        v_mid = v_bot + step_h / 2.0
        cax.add_patch(mpatches.Rectangle((0, v_bot), 1.0, step_h,
                                         facecolor=cmap(norm(v_mid)),
                                         edgecolor="none", lw=0))
    cax.set_xlim(0, 1.0)
    cax.set_ylim(5.0, 28.0)
    cax.set_xticks([])
    cax.yaxis.tick_right()
    cax.yaxis.set_label_position("right")
    cax.tick_params(labelsize=6.5, length=2, pad=2)
    cax.set_ylabel("Paging stall (s)", fontsize=7.0, labelpad=4)

    _savefig("fig5_ablation.pdf")


# ══════════════════════════════════════════════════════════════════════════════
# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 6 — Memory Timeline    6.9" × 3.3"
# ══════════════════════════════════════════════════════════════════════════════
def fig6_timeline():
    fig, axes = plt.subplots(2, 1, figsize=(6.9, 3.4), sharex=True,
                             gridspec_kw={"hspace": 0.45, "left": 0.12, "right": 0.98, "top": 0.82, "bottom": 0.12})

    models = ["Synthesis", "Physics", "Coding", "Math", "Research"]
    stage_x = [0, 8.5, 19.5, 29.5, 38.0, 46.0]
    ORANGE = "#C05621"

    fig.text(0.5, 0.96, "Working-Set Paging Execution Timeline Comparison (EXP-H2)",
             fontsize=8.5, fontweight="bold", ha="center", color=DARK)
    fig.text(0.5, 0.90, "Illustrative execution trace derived from canonical 5-stage sequence",
             fontsize=6.2, style="italic", ha="center", color="#555555")

    for ax in axes:
        for sx in stage_x:
            ax.axvline(sx, color="#e0e0e0", lw=0.6, ls=":")
        ax.set_xlim(0, 47)
        ax.set_ylim(-0.7, 5.1)
        ax.set_yticks(range(5))
        ax.set_yticklabels(models, fontsize=7.0)

    # (a) Reactive LRU
    ax = axes[0]
    ax.set_title("(a)  Reactive LRU (Baseline B4)", loc="left", fontsize=7.8, fontweight="bold", pad=4)

    # Stage labels above plot
    for i in range(5):
        cx = (stage_x[i] + stage_x[i+1]) / 2
        stage_names = ["S1: Research", "S2: Math", "S3: Coding", "S4: Physics", "S5: Synthesis"]
        ax.text(cx, 4.65, stage_names[i], ha="center", va="bottom", fontsize=5.8, color=DARK, fontweight="bold")

    # LRU Residency & Active Execution
    # Research: resident 0..19.5, active 0..8.5
    ax.barh(4, 19.5, left=0.0, height=0.45, color="#E4E7EC", edgecolor=GREY, lw=0.4)
    ax.barh(4, 8.5,  left=0.0, height=0.55, color=PURP, edgecolor=DARK, lw=0.6)

    # Math: loaded at 8.5, resident 8.5..29.5, active 8.5..19.5
    ax.barh(3, 21.0, left=8.5, height=0.45, color="#E4E7EC", edgecolor=GREY, lw=0.4)
    ax.barh(3, 11.0, left=8.5, height=0.55, color=BLUE, edgecolor=DARK, lw=0.6)

    # Coding: loaded at 19.5, resident 19.5..38.0, active 19.5..29.5
    ax.barh(2, 18.5, left=19.5, height=0.45, color="#E4E7EC", edgecolor=GREY, lw=0.4)
    ax.barh(2, 10.0, left=19.5, height=0.55, color=GREEN, edgecolor=DARK, lw=0.6)

    # Physics: loaded at 29.5, resident 29.5..46.0, active 29.5..38.0
    ax.barh(1, 16.5, left=29.5, height=0.45, color="#E4E7EC", edgecolor=GREY, lw=0.4)
    ax.barh(1, 8.5,  left=29.5, height=0.55, color=MBLUE, edgecolor=DARK, lw=0.6)

    # Synthesis: loaded cold at 38.0, resident 38.0..46.0, active 38.0..46.0
    ax.barh(0, 8.0,  left=38.0, height=0.45, color="#E4E7EC", edgecolor=GREY, lw=0.4)
    ax.barh(0, 8.0,  left=38.0, height=0.55, color=ORANGE, edgecolor=DARK, lw=0.6)

    # Eviction annotations with clean vertical dashed lines and pointers
    ax.axvline(19.5, color=RED, lw=1.0, ls="--")
    ax.annotate("evict Research", xy=(19.5, 4.1), xytext=(20.5, 4.45),
                arrowprops=dict(arrowstyle="->", color=RED, lw=0.7),
                fontsize=5.4, color=RED, fontweight="bold", ha="left", va="center")

    ax.axvline(29.5, color=RED, lw=1.0, ls="--")
    ax.annotate("evict Math", xy=(29.5, 3.1), xytext=(28.0, 2.45),
                arrowprops=dict(arrowstyle="->", color=RED, lw=0.7),
                fontsize=5.4, color=RED, fontweight="bold", ha="right", va="center")

    ax.axvline(38.0, color=RED, lw=1.0, ls="--")
    ax.annotate("evict Coding", xy=(38.0, 2.1), xytext=(36.5, 1.45),
                arrowprops=dict(arrowstyle="->", color=RED, lw=0.7),
                fontsize=5.4, color=RED, fontweight="bold", ha="right", va="center")

    ax.annotate("cold page-in stall", xy=(38.0, 0.1), xytext=(35.5, -0.45),
                arrowprops=dict(arrowstyle="->", color=RED, lw=0.7),
                fontsize=5.4, color=RED, fontweight="bold", ha="right", va="center")

    # Legend in panel (a)
    leg_patches = [
        mpatches.Patch(facecolor=DARK, edgecolor=DARK, label="Active execution"),
        mpatches.Patch(facecolor="#E4E7EC", edgecolor=GREY, label="RAM resident"),
    ]
    ax.legend(handles=leg_patches, loc="lower right", fontsize=5.6, framealpha=0.9, bbox_to_anchor=(0.99, 0.02))

    # (b) ModelVM
    ax2 = axes[1]
    ax2.set_title("(b)  ModelVM (Predictive Working-Set + Opportunistic Pre-staging B5)", loc="left", fontsize=7.8, fontweight="bold", pad=4)
    ax2.set_xlabel("Wall-clock time (s)", fontsize=7.5)

    # Research: resident across 0..19.5, active at S1 (0..8.5)
    ax2.barh(4, 19.5, left=0.0, height=0.45, color="#E4E7EC", edgecolor=GREY, lw=0.4)
    ax2.barh(4, 8.5,  left=0.0, height=0.55, color=PURP, edgecolor=DARK, lw=0.6)

    # Math: loaded at 8.5, resident 8.5..34.0, active 8.5..19.5
    ax2.barh(3, 25.5, left=8.5, height=0.45, color="#E4E7EC", edgecolor=GREY, lw=0.4)
    ax2.barh(3, 11.0, left=8.5, height=0.55, color=BLUE, edgecolor=DARK, lw=0.6)

    # Coding: loaded at 19.5, resident 19.5..38.0, active 19.5..29.5
    ax2.barh(2, 18.5, left=19.5, height=0.45, color="#E4E7EC", edgecolor=GREY, lw=0.4)
    ax2.barh(2, 10.0, left=19.5, height=0.55, color=GREEN, edgecolor=DARK, lw=0.6)

    # Opportunistic prefetch of Physics into free headroom during Stage 3 (t=24.0)
    ax2.barh(1, 22.0, left=24.0, height=0.45, color="#E4E7EC", edgecolor=GREY, lw=0.4)
    ax2.barh(1, 8.5,  left=29.5, height=0.55, color=MBLUE, edgecolor=DARK, lw=0.6)
    ax2.annotate("opportunistic pre-staging\n(into free headroom)", xy=(24.0, 1.0), xytext=(17.5, 0.45),
                 arrowprops=dict(arrowstyle="->", color=GREEN, lw=0.7),
                 fontsize=5.2, color=GREEN, fontweight="bold", ha="center", va="top")

    # Opportunistic prefetch of Synthesis into free headroom during Stage 4 (t=33.5)
    ax2.barh(0, 12.5, left=33.5, height=0.45, color="#E4E7EC", edgecolor=GREY, lw=0.4)
    ax2.barh(0, 8.0,  left=38.0, height=0.55, color=ORANGE, edgecolor=DARK, lw=0.6)
    ax2.annotate("pre-staged in spare RAM\n(instant cache hit)", xy=(33.5, 0.0), xytext=(28.0, -0.55),
                 arrowprops=dict(arrowstyle="->", color=BLUE, lw=0.7),
                 fontsize=5.2, color=BLUE, fontweight="bold", ha="center", va="top")

    # Summary card in ax2
    ax2.text(46.0, 3.2,
             "Paging stalls: 21.6 s \u2192 7.2 s (66.7% reduction)\n" +
             r"Cache hit rate $H_{\mathrm{cache}}$: 0.20 $\to$ 0.60" + "\n" +
             "Reduces redundant reloads: 4.0 \u2192 1.0",
             ha="right", va="center", fontsize=5.8, color=DARK,
             bbox=dict(boxstyle="round,pad=0.3", fc="#FFFFFF", ec=BLUE, lw=0.7, alpha=0.95))

    _savefig("fig6_timeline.pdf")


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 7 — State Retention vs Depth    3.35" × 2.35"
# ══════════════════════════════════════════════════════════════════════════════
def fig7_retention():
    fig, ax = plt.subplots(figsize=(3.35, 2.35),
                           gridspec_kw={"left": 0.16, "right": 0.95,
                                        "top": 0.88, "bottom": 0.18})

    N_meas = TABLE_13_RETENTION["transitions"]
    R_raw  = TABLE_13_RETENTION["raw_text_facts"]
    R_csp  = TABLE_13_RETENTION["typed_csp_facts"]

    # Continuous exponential fit line for Raw Text
    N_fit = np.linspace(1, 12, 100)
    lam = TABLE_13_RETENTION["decay_fit_lambda"]
    R_fit = np.exp(-lam * N_fit)

    # Plot exponential fit trendline first
    ax.plot(N_fit, R_fit, color="#9E9E9E", lw=1.0, ls="--",
            label=r"Exponential fit: $R_{\mathrm{facts}} \approx e^{-0.142 N}$")

    # Plot empirical measurement points only (N in {1, 2, 4, 8, 12})
    ax.plot(N_meas, R_raw, color=GREY, lw=0,
            marker="s", ms=4.0, markerfacecolor="white",
            markeredgecolor=GREY, markeredgewidth=0.8,
            label="Raw text (empirical)")

    ax.plot(N_meas, R_csp, color=BLUE, lw=1.5,
            marker="o", ms=4.2, markeredgecolor=DARK, markeredgewidth=0.4,
            label="Typed CSP (ModelVM)")

    ax.set_xlabel("Transition depth  $N$", fontsize=7.5)
    ax.set_ylabel(r"Fact retention  $R_{\mathrm{facts}}$", fontsize=7.5)
    ax.set_title("State Retention vs. Model Transition Depth",
                 fontsize=8.0, fontweight="bold", pad=5)
    ax.set_xlim(0.5, 13.5)
    ax.set_ylim(0.05, 1.08)
    ax.set_xticks([1, 2, 4, 6, 8, 10, 12])
    ax.yaxis.set_major_locator(mticker.MultipleLocator(0.2))
    ax.grid(color="#ebebeb", lw=0.4)
    ax.set_axisbelow(True)

    ax.legend(fontsize=5.8, loc="lower left", bbox_to_anchor=(0.02, 0.06), framealpha=0.92)

    # Clean callouts in open whitespace
    ax.text(12.0, 0.99,
            r"$\mathbf{R_{\mathrm{facts}}=0.940}$" + "\n" + r"$(R_{\mathrm{calcs}}=0.920)$",
            ha="right", va="top", fontsize=5.8, color=BLUE)

    ax.text(12.0, 0.18, r"$R_{\mathrm{facts}}=0.180$",
            ha="left", va="center", fontsize=5.8, color=GREY, fontweight="medium")

    _savefig("fig7_retention.pdf")


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 8 — Memory Budget Robustness    6.9" × 3.0"
# ══════════════════════════════════════════════════════════════════════════════
def fig8_robustness():
    fig, axes = plt.subplots(1, 2, figsize=(6.9, 3.0),
                             gridspec_kw={"wspace": 0.32, "left": 0.08,
                                          "right": 0.96, "top": 0.88,
                                          "bottom": 0.18})

    budgets = TABLE_12_SWEEP["budgets"]
    q_b5    = TABLE_12_SWEEP["B5_ModelVM"]["quality"]
    q_b4    = TABLE_12_SWEEP["B4_Reactive_LRU"]["quality"]
    s_b5    = TABLE_12_SWEEP["B5_ModelVM"]["paging_time"]
    s_b4    = TABLE_12_SWEEP["B4_Reactive_LRU"]["paging_time"]

    # (a) Quality vs Budget
    ax = axes[0]
    # Highlight 4 GB stress region
    ax.axvspan(3.5, 4.8, color="#8B2020", alpha=0.07, zorder=0)

    ax.plot(budgets, q_b5, color=BLUE, lw=1.5,
            marker="o", ms=4.5, markeredgecolor=DARK, markeredgewidth=0.4,
            label="ModelVM ($B_5$) [Ours]")
    ax.plot(budgets, q_b4, color=GREY, lw=1.2, ls="--",
            marker="s", ms=4.0, markerfacecolor="white",
            markeredgecolor=GREY, markeredgewidth=0.7,
            label="Reactive LRU ($B_4$)")
    ax.axhline(0.562, color="#9E9E9E", lw=1.0, ls=":", label="Monolith $B_0$ (0.562)")

    # 4 GB callouts
    ax.annotate("60% OOM crash cliff\n(Reactive LRU $B_4$)", xy=(4.0, 0.680), xytext=(4.8, 0.42),
                arrowprops=dict(arrowstyle="->", color=RED, lw=0.7),
                fontsize=5.8, color=RED, fontweight="bold")
    ax.annotate("$Q = 0.885$\n(0% OOM)", xy=(4.0, 0.885), xytext=(4.8, 0.84),
                arrowprops=dict(arrowstyle="->", color=BLUE, lw=0.7),
                fontsize=5.8, color=BLUE, fontweight="bold")

    ax.set_xlabel("Memory budget (GB)", fontsize=8.0)
    ax.set_ylabel("Task quality  $Q$", fontsize=8.0)
    ax.set_title("(a)  Quality vs. memory budget", fontsize=8.5, fontweight="bold", pad=6)
    ax.set_xlim(3.2, 16.8)
    ax.set_ylim(0.35, 1.06)
    ax.set_xticks(budgets)
    ax.grid(color="#ebebeb", lw=0.4, zorder=0)
    ax.set_axisbelow(True)
    ax.legend(fontsize=6.5, loc="lower right")

    # (b) Paging stalls vs Budget
    ax = axes[1]
    ax.axvspan(3.5, 4.8, color="#8B2020", alpha=0.07, zorder=0)

    ax.plot(budgets, s_b5, color=BLUE, lw=1.5,
            marker="o", ms=4.5, markeredgecolor=DARK, markeredgewidth=0.4,
            label="ModelVM ($B_5$) [Ours]")
    ax.plot(budgets, s_b4, color=GREY, lw=1.2, ls="--",
            marker="s", ms=4.0, markerfacecolor="white",
            markeredgecolor=GREY, markeredgewidth=0.7,
            label="Reactive LRU ($B_4$)")

    # Annotate 4 GB paging stall difference and OOM rate
    ax.annotate("42.6 s stall + 60% OOM", xy=(4.0, 42.6), xytext=(5.2, 40.0),
                arrowprops=dict(arrowstyle="->", color=RED, lw=0.7),
                fontsize=5.8, color=RED, fontweight="bold")
    ax.annotate("14.8 s (65.3% reduction)", xy=(4.0, 14.8), xytext=(5.5, 18.0),
                arrowprops=dict(arrowstyle="->", color=BLUE, lw=0.7),
                fontsize=5.8, color=BLUE, fontweight="bold")

    ax.set_xlabel("Memory budget (GB)", fontsize=8.0)
    ax.set_ylabel(r"Paging stall  $t_{\mathrm{paging}}$  (s)", fontsize=8.0)
    ax.set_title("(b)  Paging stalls vs. memory budget", fontsize=8.5, fontweight="bold", pad=6)
    ax.set_xlim(3.2, 16.8)
    ax.set_ylim(-1.5, 48)
    ax.set_xticks(budgets)
    ax.grid(color="#ebebeb", lw=0.4, zorder=0)
    ax.set_axisbelow(True)
    ax.legend(fontsize=6.5, loc="upper right")

    _savefig("fig8_robustness.pdf")


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 9 — Quality-Memory-Latency Pareto    6.9" × 3.5"
# ══════════════════════════════════════════════════════════════════════════════
def fig9_pareto():
    fig = plt.figure(figsize=(6.9, 3.5))

    # Left 3D axes: clear margins, no overlapping titles or cards
    ax3d = fig.add_axes([0.01, 0.04, 0.69, 0.80], projection="3d")
    ax3d.view_init(elev=22, azim=132)

    # Grounded configurations within memory budget (Table 2 / EXP-H4)
    # Note: Ungrounded Offline Oracle is excluded from the 3D volume per P0 audit
    configs = [
        ("B0", r"$B_0$ (Monolith)",             BASELINES_H4["B0_Monolith"]["M"],          BASELINES_H4["B0_Monolith"]["L"],          BASELINES_H4["B0_Monolith"]["Q"],          "#888888", "o", 80,  (14, -14), "left"),
        ("B_static", r"$B_{\mathrm{static}}$ (Ensemble)", BASELINES_H4["B_static_Ensemble"]["M"], BASELINES_H4["B_static_Ensemble"]["L"], BASELINES_H4["B_static_Ensemble"]["Q"], "#9E9E9E", "^", 75,  (0, 16),   "center"),
        ("B2", r"$B_2$ (Dynamic LRU)",          BASELINES_H4["B2_Dynamic_LRU"]["M"],       BASELINES_H4["B2_Dynamic_LRU"]["L"],       BASELINES_H4["B2_Dynamic_LRU"]["Q"],       "#757575", "s", 75,  (-14, -14), "right"),
        ("B4", r"$B_4$ (CSP+LRU)",              BASELINES_H4["B4_CSP_LRU"]["M"],           BASELINES_H4["B4_CSP_LRU"]["L"],           BASELINES_H4["B4_CSP_LRU"]["Q"],           "#546E7A", "D", 80,  (-14, 8),   "right"),
        ("B5", r"$B_5$ (ModelVM)",              BASELINES_H4["B5_ModelVM"]["M"],           BASELINES_H4["B5_ModelVM"]["L"],           BASELINES_H4["B5_ModelVM"]["Q"],           BLUE,      "o", 110, (-14, 14),  "right"),
    ]

    for tag, lbl, m, l, q, c, mk, s, offset, align in configs:
        ax3d.scatter([m], [l], [q], color=c, marker=mk, s=s,
                     edgecolor=DARK, lw=0.8, zorder=10, depthshade=False)

    # Trajectory from B0 to B5
    ax3d.plot([BASELINES_H4["B0_Monolith"]["M"], BASELINES_H4["B5_ModelVM"]["M"]],
              [BASELINES_H4["B0_Monolith"]["L"], BASELINES_H4["B5_ModelVM"]["L"]],
              [BASELINES_H4["B0_Monolith"]["Q"], BASELINES_H4["B5_ModelVM"]["Q"]],
              color=BLUE, lw=1.2, ls="--", alpha=0.85, zorder=4)

    # Budget boundary plane at M = 8.0 GB
    L_grid = np.linspace(25, 68, 5)
    Q_grid = np.linspace(0.48, 1.02, 5)
    LL, QQ = np.meshgrid(L_grid, Q_grid)
    MM = np.full_like(LL, 8.0)
    ax3d.plot_surface(MM, LL, QQ, alpha=0.10, color=RED, edgecolor="#C62828", lw=0.5, linestyle="--", zorder=1)

    ax3d.set_xlabel("Peak RAM  M (GB)", fontsize=7.2, labelpad=5)
    ax3d.set_ylabel("Total latency  L (s)", fontsize=7.2, labelpad=5)
    ax3d.set_zlabel("Task quality  Q", fontsize=7.2, labelpad=9)
    ax3d.set_xlim(5.0, 8.5)
    ax3d.set_ylim(25, 68)
    ax3d.set_zlim(0.45, 1.08)
    ax3d.tick_params(labelsize=6.2, pad=1)

    # Render figure once to compute 3D projections
    fig.canvas.draw()

    # Annotate each point cleanly in 2D projection with zero overlap
    for tag, lbl, m, l, q, c, mk, s, offset, align in configs:
        x2, y2, _ = proj3d.proj_transform(m, l, q, ax3d.get_proj())
        fontweight = "bold" if tag == "B5" else "normal"
        textcolor = BLUE if tag == "B5" else DARK

        ax3d.annotate(
            lbl,
            xy=(x2, y2),
            xytext=offset,
            textcoords="offset points",
            ha=align, va="center",
            fontsize=6.5,
            fontweight=fontweight,
            color=textcolor,
            bbox=dict(boxstyle="round,pad=0.25", fc="#FFFFFF", ec="#CFD8DC", lw=0.6, alpha=0.95),
            arrowprops=dict(arrowstyle="->", color="#90A4AE", lw=0.6, shrinkA=0, shrinkB=3)
        )

    # Figure title
    fig.text(0.50, 0.95, "Quality–Memory–Latency Pareto Optimization Space",
             fontsize=8.8, fontweight="bold", ha="center", color=DARK)

    # Side panel for Legend and Out-of-Budget card
    ax_side = fig.add_axes([0.71, 0.05, 0.27, 0.85])
    ax_side.axis("off")

    # Section 1: Legend Card
    leg_card = mpatches.FancyBboxPatch(
        (0.0, 0.44), 1.0, 0.54,
        boxstyle="round,pad=0.03,rounding_size=0.04",
        fc="#F8F9FA", ec="#CFD8DC", lw=0.7
    )
    ax_side.add_patch(leg_card)

    ax_side.text(0.08, 0.94, "Configurations", fontsize=7.2, fontweight="bold", color=DARK)

    items = [
        (BLUE, "o", r"$B_5$ ModelVM [Ours]"),
        ("#546E7A", "D", r"$B_4$ CSP + LRU"),
        ("#757575", "s", r"$B_2$ Dynamic LRU"),
        ("#888888", "o", r"$B_0$ Monolith"),
        ("#9E9E9E", "^", r"$B_{\mathrm{static}}$ Ensemble"),
    ]

    y_pos = 0.86
    for color, marker, label in items:
        ax_side.plot(0.12, y_pos, marker=marker, color=color, markeredgecolor=DARK, markeredgewidth=0.7, markersize=5.5)
        ax_side.text(0.24, y_pos, label, fontsize=6.3, color=DARK, va="center")
        y_pos -= 0.068

    # Budget plane entry in legend
    ax_side.add_patch(mpatches.Rectangle((0.08, y_pos - 0.015), 0.09, 0.03, facecolor="#FFCDD2", edgecolor="#C62828", linestyle="--", linewidth=0.8, alpha=0.6))
    ax_side.text(0.24, y_pos, r"$M \leq 8.0$ GB Budget", fontsize=6.2, color="#C62828", va="center", fontweight="bold")

    # Section 2: Out-of-Budget Baselines Callout Card (B1 and B3)
    oob_card = mpatches.FancyBboxPatch(
        (0.0, 0.02), 1.0, 0.38,
        boxstyle="round,pad=0.03,rounding_size=0.04",
        fc="#FFF8F8", ec="#E57373", lw=0.7
    )
    ax_side.add_patch(oob_card)

    ax_side.text(0.08, 0.35, "Out-of-Budget Baselines", fontsize=6.6, fontweight="bold", color="#B71C1C")
    ax_side.text(0.08, 0.28, r"$\mathbf{B_1}$ Unconstrained Router:", fontsize=6.0, fontweight="bold", color=DARK)
    ax_side.text(0.12, 0.22, r"$M=19.8$ GB $\mid$ $L=36.4$ s $\mid$ $Q=0.742$", fontsize=5.6, color="#424242")

    ax_side.text(0.08, 0.15, r"$\mathbf{B_3}$ Router + CSP + Uncon.:", fontsize=6.0, fontweight="bold", color=DARK)
    ax_side.text(0.12, 0.09, r"$M=19.8$ GB $\mid$ $L=38.1$ s $\mid$ $Q=1.000$", fontsize=5.6, color="#424242")

    ax_side.text(0.08, 0.03, r"Violates budget: $19.8 > 8.0$ GB", fontsize=5.5, color="#B71C1C", style="italic")

    _savefig("fig9_pareto.pdf")


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 10 — Scheduler Generalization    3.35" × 2.3"
# ══════════════════════════════════════════════════════════════════════════════
def fig10_generalization():
    fig, ax = plt.subplots(figsize=(3.35, 2.3),
                           gridspec_kw={"left": 0.16, "right": 0.94,
                                        "top": 0.88, "bottom": 0.22})

    workloads = TABLE_14_GENERALIZATION["workloads"]
    r_cap     = TABLE_14_GENERALIZATION["Capability_Greedy"]
    r_mem     = TABLE_14_GENERALIZATION["Memory_Aware"]
    r_mvm     = TABLE_14_GENERALIZATION["ModelVM"]
    x = np.arange(len(workloads))

    # Offline Oracle baseline reference line at 0.0% regret
    ax.axhline(0.0, color=GREEN, lw=1.2, ls="--", label="Offline Oracle (0.0% regret)")

    # Plot the 3 evaluators from Table 14
    ax.plot(x, r_cap, color=RED, lw=1.2, ls=":",
            marker="^", ms=4.0, markerfacecolor="white", markeredgecolor=RED, markeredgewidth=0.8,
            label="Capability-Greedy")

    ax.plot(x, r_mem, color="#F57C00", lw=1.2, ls="-.",
            marker="s", ms=3.8, markerfacecolor="white", markeredgecolor="#F57C00", markeredgewidth=0.8,
            label="Memory-Aware Greedy")

    ax.plot(x, r_mvm, color=BLUE, lw=1.5,
            marker="o", ms=4.5, markeredgecolor=DARK, markeredgewidth=0.4,
            label="ModelVM Scheduler [Ours]")

    # Regret percentage callouts above each ModelVM point
    for xi, r in enumerate(r_mvm):
        ax.text(xi, r + 2.0, f"{r:.1f}%",
                ha="center", va="bottom", fontsize=5.8, color=BLUE, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(workloads, fontsize=6.5)
    ax.set_ylabel("Regret vs. Offline Oracle (%)", fontsize=7.2)
    ax.set_title("Scheduler Generalization Across Workloads",
                 fontsize=8.0, fontweight="bold", pad=5)
    ax.set_xlim(-0.4, 3.4)
    ax.set_ylim(-2.0, 62.0)
    ax.yaxis.set_major_locator(mticker.MultipleLocator(10))
    ax.grid(axis="y", color="#ebebeb", lw=0.4)
    ax.set_axisbelow(True)
    ax.legend(fontsize=5.6, loc="upper right", framealpha=0.92)

    # Summary callout in lower left whitespace
    ax.text(0.02, 0.35,
            r"ModelVM regret $\leq 7.8\%$" + "\n" + r"across all workloads",
            transform=ax.transAxes, fontsize=5.6, color=DARK,
            bbox=dict(fc="white", ec="#CFD8DC", lw=0.5, pad=2.0))

    _savefig("fig10_generalization.pdf")


# ── entry point ───────────────────────────────────────────────────────────────
def generate_all():
    funcs = [
        ("Fig 1 — Architecture",     fig1_architecture),
        ("Fig 2 — CSP",              fig2_csp),
        ("Fig 3 — Scheduler",        fig3_scheduler),
        ("Fig 4 — Control Path",     fig4_control_path),
        ("Fig 5 — Ablation",         fig5_ablation),
        ("Fig 6 — Timeline",         fig6_timeline),
        ("Fig 7 — Retention",        fig7_retention),
        ("Fig 8 — Robustness",       fig8_robustness),
        ("Fig 9 — Pareto",           fig9_pareto),
        ("Fig 10 — Generalization",  fig10_generalization),
    ]
    for name, fn in funcs:
        print(f"\n[{name}]")
        fn()

if __name__ == "__main__":
    generate_all()
