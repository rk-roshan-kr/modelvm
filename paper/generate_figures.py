"""Generate Publication-Quality Vector PDF Figures for ModelVM Research Paper."""

import matplotlib.pyplot as plt
import numpy as np

# Configure scientific publication aesthetics
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 13,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.titlesize": 14,
    "lines.linewidth": 2.0,
    "lines.markersize": 8,
    "grid.alpha": 0.3,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})

# ==========================================
# 1. Figure: Quality vs. Peak Physical Memory
# ==========================================
fig, ax = plt.subplots(figsize=(6.5, 4.5))

baselines = [
    ("B0: Monolith", 7.10, 0.562, "#7f7f7f", "s"),
    ("B_static: Ensemble", 5.40, 0.624, "#8c564b", "^"),
    ("B1: Unconstrained Router", 19.80, 0.742, "#ff7f0e", "D"),
    ("B2: Router+Raw+LRU", 7.60, 0.562, "#d62728", "x"),
    ("B3: Router+CSP+Uncon.", 19.80, 1.000, "#2ca02c", "o"),
    ("B4: Router+CSP+LRU", 7.60, 0.982, "#9467bd", "v"),
    ("B5: Full ModelVM", 7.60, 1.000, "#1f77b4", "*"),
]

# Plot points
for label, mem, q, color, marker in baselines:
    ms = 12 if marker == "*" else 8
    ax.scatter(mem, q, color=color, marker=marker, s=ms**2, label=label, zorder=5)

# Enforced budget line at 8.0 GB
ax.axvline(x=8.0, color="#d62728", linestyle="--", linewidth=1.5, alpha=0.8, label="8.0 GB Memory Budget")
ax.axvspan(0, 8.0, alpha=0.06, color="green", label="Consumer Hardware (<8GB)")

# Draw Pareto frontier line for valid configurations
frontier_mem = [5.40, 7.60, 19.80]
frontier_q = [0.624, 1.000, 1.000]
ax.plot(frontier_mem, frontier_q, color="#1f77b4", linestyle=":", linewidth=1.8, label="ModelVM Pareto Frontier")

ax.set_xlabel("Peak Physical Memory (GB)")
ax.set_ylabel("Composite Quality ($Q \in [0, 1]$)")
ax.set_title("Quality vs. Peak Physical Memory")
ax.set_xlim(3.0, 22.0)
ax.set_ylim(0.45, 1.08)
ax.grid(True, linestyle="--")
ax.legend(loc="lower right", framealpha=0.9, fontsize=9)

plt.tight_layout()
plt.savefig("fig_pareto_quality_memory.pdf", dpi=300)
plt.close()
print("Generated fig_pareto_quality_memory.pdf")

# ==========================================
# 2. Figure: Quality vs. Execution Latency
# ==========================================
fig, ax = plt.subplots(figsize=(6.5, 4.5))

latency_baselines = [
    ("B0: Monolith", 34.2, 0.562, "#7f7f7f", "s"),
    ("B_static: Ensemble", 29.8, 0.624, "#8c564b", "^"),
    ("B1: Unconstrained Router", 36.4, 0.742, "#ff7f0e", "D"),
    ("B2: Router+Raw+LRU", 62.4, 0.562, "#d62728", "x"),
    ("B3: Router+CSP+Uncon.", 38.1, 1.000, "#2ca02c", "o"),
    ("B4: Router+CSP+LRU", 58.7, 0.982, "#9467bd", "v"),
    ("B5: Full ModelVM", 43.8, 1.000, "#1f77b4", "*"),
]

for label, lat, q, color, marker in latency_baselines:
    ms = 12 if marker == "*" else 8
    ax.scatter(lat, q, color=color, marker=marker, s=ms**2, label=label, zorder=5)

# Pareto frontier in Quality vs Latency
frontier_lat = [29.8, 43.8]
frontier_q_lat = [0.624, 1.000]
ax.plot(frontier_lat, frontier_q_lat, color="#1f77b4", linestyle=":", linewidth=1.8, label="ModelVM Pareto Frontier (Constrained)")

ax.set_xlabel("Total Execution Latency (seconds)")
ax.set_ylabel("Composite Quality ($Q \in [0, 1]$)")
ax.set_title("Quality vs. Execution Latency")
ax.set_xlim(25.0, 70.0)
ax.set_ylim(0.45, 1.08)
ax.grid(True, linestyle="--")
ax.legend(loc="lower right", framealpha=0.9, fontsize=9)

plt.tight_layout()
plt.savefig("fig_pareto_quality_latency.pdf", dpi=300)
plt.close()
print("Generated fig_pareto_quality_latency.pdf")

# ==========================================
# 3. Figure: Memory-Pressure Sweep (EXP-R1)
# ==========================================
fig, ax1 = plt.subplots(figsize=(6.5, 4.5))

budgets = [4.0, 6.0, 8.0, 10.0, 12.0, 16.0]
q_lru = [0.680, 0.920, 0.982, 1.000, 1.000, 1.000]
q_modelvm = [0.885, 1.000, 1.000, 1.000, 1.000, 1.000]
t_paging_lru = [42.6, 28.4, 21.6, 15.4, 8.2, 0.0]
t_paging_modelvm = [14.8, 10.2, 7.2, 3.6, 1.2, 0.0]

ax1.plot(budgets, q_modelvm, "o-", color="#1f77b4", label=r"ModelVM Quality ($Q$)")
ax1.plot(budgets, q_lru, "s--", color="#d62728", label=r"Reactive LRU Quality ($Q$)")
ax1.set_xlabel(r"Memory Budget $\mathcal{B}_{RAM}$ (GB)")
ax1.set_ylabel(r"Quality ($Q \in [0, 1]$)", color="#1f77b4")
ax1.set_ylim(0.55, 1.05)
ax1.tick_params(axis='y', labelcolor="#1f77b4")

ax2 = ax1.twinx()
ax2.plot(budgets, t_paging_modelvm, "^-.", color="#2ca02c", label="ModelVM Paging Time (s)")
ax2.plot(budgets, t_paging_lru, "x:", color="#9467bd", label="Reactive LRU Paging Time (s)")
ax2.set_ylabel("Paging Overhead (seconds)", color="#2ca02c")
ax2.tick_params(axis='y', labelcolor="#2ca02c")
ax2.set_ylim(-2, 50)

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="center right", fontsize=8.5)
ax1.set_title("EXP-R1: Quality and Paging Overhead vs. Memory Pressure")
ax1.grid(True, linestyle="--")

plt.tight_layout()
plt.savefig("fig_exp_r1_memory_sweep.pdf", dpi=300)
plt.close()
print("Generated fig_exp_r1_memory_sweep.pdf")

# ==========================================
# 4. Figure: Model-Transition Decay Curve (EXP-R2)
# ==========================================
fig, ax = plt.subplots(figsize=(6.5, 4.5))

switches = [1, 2, 4, 8, 12]
ret_raw = [0.940, 0.810, 0.460, 0.320, 0.180]
ret_csp = [1.000, 1.000, 1.000, 0.960, 0.940]

ax.plot(switches, ret_csp, "o-", color="#1f77b4", linewidth=2.5, label=r"Typed CSP ($\mathcal{S}_t$)")
ax.plot(switches, ret_raw, "s--", color="#d62728", linewidth=2.0, label="Raw Text Concatenation")

# Theoretical exponential decay fit for raw text
x_fit = np.linspace(1, 12, 100)
y_fit = np.exp(-0.142 * x_fit)
ax.plot(x_fit, y_fit, ":", color="#7f7f7f", label=r"Raw Text Fit ($e^{-0.142 N}$)")

ax.set_xlabel("Number of Model Transitions ($N$)")
ax.set_ylabel(r"Factual Preservation Ratio ($R_{facts}$)")
ax.set_title("EXP-R2: State Retention vs. Model Transition Depth")
ax.set_xlim(0.5, 12.5)
ax.set_ylim(0.0, 1.08)
ax.grid(True, linestyle="--")
ax.legend(loc="lower left", framealpha=0.9)

plt.tight_layout()
plt.savefig("fig_exp_r2_transition_decay.pdf", dpi=300)
plt.close()
print("Generated fig_exp_r2_transition_decay.pdf")
