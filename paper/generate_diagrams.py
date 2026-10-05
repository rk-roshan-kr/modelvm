"""Generate Publication-Quality Vector PDF Diagrams for ModelVM Architecture and Control Flow."""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# Publication aesthetics
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 9.5,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})

def create_architecture_diagram():
    fig, ax = plt.subplots(figsize=(11.8, 7.2))
    ax.set_xlim(0, 118)
    ax.set_ylim(0, 72)
    ax.axis("off")

    # High-contrast, publication-grade executive palette
    c_k_bg = "#f4f7fa"
    c_k_border = "#1d446c"
    c_k_head = "#143250"
    
    c_s_bg = "#f7f5fa"
    c_s_border = "#523275"
    c_s_head = "#3c2158"
    
    c_p_bg = "#fbf6f0"
    c_p_border = "#995212"
    c_p_head = "#733c09"
    
    c_e_bg = "#f2f8f5"
    c_e_border = "#1c613e"
    c_e_head = "#124229"

    c_box = "#ffffff"
    arrow_color = "#222222"

    # =========================================================================
    # LAYER 1: COGNITIVE KERNEL (Supervisory Plane)  [y: 54.5 -> 69.5]
    # =========================================================================
    r1 = FancyBboxPatch((3, 54.5), 92.5, 15.0, boxstyle="round,pad=0.5,rounding_size=1.0",
                        facecolor=c_k_bg, edgecolor=c_k_border, linewidth=1.4)
    ax.add_patch(r1)
    ax.text(5.5, 67.2, "COGNITIVE KERNEL (Supervisory & Orchestration Plane)", 
            fontsize=10.0, fontweight="bold", color=c_k_head)

    # Box 1.1: Task Decomposer (x: 5.5 -> 32.0, w: 26.5)
    b11 = FancyBboxPatch((5.5, 56.0), 26.5, 9.2, boxstyle="round,pad=0.3,rounding_size=0.5",
                         facecolor=c_box, edgecolor=c_k_border, linewidth=0.9)
    ax.add_patch(b11)
    ax.text(18.75, 62.7, "Task Decomposer", fontsize=9.0, fontweight="bold", ha="center", color=c_k_head)
    ax.text(18.75, 60.3, r"Goal $G \to$ Stage DAG $\mathcal{S}$", fontsize=8.2, ha="center", color="#222222")
    ax.text(18.75, 58.0, r"Demand Sequence $\{C(s_t)\}_{t=1}^N$", fontsize=7.8, ha="center", color="#555555")

    # Arrow 1.1 -> 1.2
    a1 = FancyArrowPatch((32.0, 60.6), (36.5, 60.6), arrowstyle="-|>", mutation_scale=11, color=arrow_color, lw=1.2)
    ax.add_patch(a1)

    # Box 1.2: Stage Execution Supervisor (x: 36.5 -> 67.0, w: 30.5)
    b12 = FancyBboxPatch((36.5, 56.0), 30.5, 9.2, boxstyle="round,pad=0.3,rounding_size=0.5",
                         facecolor=c_box, edgecolor=c_k_border, linewidth=0.9)
    ax.add_patch(b12)
    ax.text(51.75, 62.7, "Stage Execution Supervisor", fontsize=9.0, fontweight="bold", ha="center", color=c_k_head)
    ax.text(51.75, 60.3, r"Stage $s_t$: Instruction $\tau_t$", fontsize=8.2, ha="center", color="#222222")
    ax.text(51.75, 58.0, r"Capability Requirement $C(s_t)$", fontsize=7.8, ha="center", color="#555555")

    # Arrow 1.2 -> 1.3
    a2 = FancyArrowPatch((67.0, 60.6), (71.5, 60.6), arrowstyle="-|>", mutation_scale=11, color=arrow_color, lw=1.2)
    ax.add_patch(a2)

    # Box 1.3: Cognitive State Packet Carrier (x: 71.5 -> 93.5, w: 22.0)
    b13 = FancyBboxPatch((71.5, 56.0), 22.0, 9.2, boxstyle="round,pad=0.3,rounding_size=0.5",
                         facecolor=c_box, edgecolor="#701a5e", linewidth=1.1)
    ax.add_patch(b13)
    ax.text(82.5, 62.7, r"State Carrier $\mathcal{S}_t$ (CSP)", fontsize=9.0, fontweight="bold", ha="center", color="#701a5e")
    ax.text(82.5, 60.3, r"$\langle G, F_t, C_t, \dots, O_t \rangle$", fontsize=8.0, ha="center", color="#222222")
    ax.text(82.5, 58.0, "Typed 9-Tuple Carrier", fontsize=7.8, ha="center", color="#555555")

    # =========================================================================
    # LAYER 2: PREDICTIVE SCHEDULER & WORKING SET  [y: 37.0 -> 51.0]
    # =========================================================================
    r2 = FancyBboxPatch((3, 37.0), 92.5, 14.0, boxstyle="round,pad=0.5,rounding_size=1.0",
                        facecolor=c_s_bg, edgecolor=c_s_border, linewidth=1.4)
    ax.add_patch(r2)
    ax.text(5.5, 48.7, "PREDICTIVE COGNITIVE SCHEDULER & WORKING-SET ENGINE", 
            fontsize=10.0, fontweight="bold", color=c_s_head)

    # Box 2.1: Working Set Predictor (x: 5.5 -> 45.0, w: 39.5)
    b21 = FancyBboxPatch((5.5, 38.5), 39.5, 8.6, boxstyle="round,pad=0.3,rounding_size=0.5",
                         facecolor=c_box, edgecolor=c_s_border, linewidth=0.9)
    ax.add_patch(b21)
    ax.text(25.25, 44.7, r"Working-Set Predictor: $W(t, k)$", fontsize=9.0, fontweight="bold", ha="center", color=c_s_head)
    ax.text(25.25, 42.4, r"Distance Decay: $w_j = \max(0.1, 1 - 0.2(j-1))$", fontsize=8.0, ha="center", color="#222222")
    ax.text(25.25, 40.2, r"Prefetch Utility: $U_{\mathrm{prefetch}}(m)$", fontsize=7.8, ha="center", color="#555555")

    # Arrow 2.1 -> 2.2
    a21 = FancyArrowPatch((45.0, 42.8), (49.5, 42.8), arrowstyle="-|>", mutation_scale=11, color=arrow_color, lw=1.2)
    ax.add_patch(a21)

    # Box 2.2: Multi-Objective Scheduler (x: 49.5 -> 93.5, w: 44.0)
    b22 = FancyBboxPatch((49.5, 38.5), 44.0, 8.6, boxstyle="round,pad=0.3,rounding_size=0.5",
                         facecolor=c_box, edgecolor=c_s_border, linewidth=0.9)
    ax.add_patch(b22)
    ax.text(71.5, 44.7, "Multi-Objective Cognitive Scheduler", fontsize=9.0, fontweight="bold", ha="center", color=c_s_head)
    ax.text(71.5, 42.4, r"Empirical Profiling Matrix $\mathbf{P} \in [0, 1]^{K \times |\mathcal{C}|}$", fontsize=8.0, ha="center", color="#222222")
    ax.text(71.5, 40.2, r"Score$(m) = F_{\mathrm{cap}} - \alpha M_{\mathrm{cost}} - \beta L_{\mathrm{load}} - \delta E_{\mathrm{evict}} + \eta F_{\mathrm{fut}}$", fontsize=7.4, ha="center", color="#555555")

    # =========================================================================
    # LAYER 3: MODEL PAGER (Memory Virtualization)  [y: 19.5 -> 33.5]
    # =========================================================================
    r3 = FancyBboxPatch((3, 19.5), 92.5, 14.0, boxstyle="round,pad=0.5,rounding_size=1.0",
                        facecolor=c_p_bg, edgecolor=c_p_border, linewidth=1.4)
    ax.add_patch(r3)
    ax.text(5.5, 31.2, "MODEL PAGER: HARDWARE MEMORY VIRTUALIZATION", 
            fontsize=10.0, fontweight="bold", color=c_p_head)
    ax.text(93.5, 31.2, r"Configured Budget $\mathcal{B}_{\mathrm{RAM}}$ (Nominal: $8.0\,\mathrm{GB}$)  |  Headroom $\Delta \geq 1.0\,\mathrm{GB}$", 
            fontsize=7.8, fontweight="bold", color=c_p_head, ha="right")

    # Box 3.1: Active Resident Set (x: 5.5 -> 28.5, w: 23)
    b31 = FancyBboxPatch((5.5, 21.0), 23, 8.6, boxstyle="round,pad=0.3,rounding_size=0.5",
                         facecolor=c_box, edgecolor=c_p_border, linewidth=0.9)
    ax.add_patch(b31)
    ax.text(17.0, 27.2, r"Resident Table $\mathcal{R}_t$", fontsize=9.0, fontweight="bold", ha="center", color=c_p_head)
    ax.text(17.0, 24.9, r"$\sum_{m \in \mathcal{R}_t} \mathrm{RAM}_{\mathrm{req}}(m) \leq \mathcal{B}_{\mathrm{RAM}}$", fontsize=7.6, ha="center", color="#222222")
    ax.text(17.0, 22.7, "Timestamps & Pin Flags", fontsize=7.5, ha="center", color="#555555")

    # Box 3.2: Cache Hit Decision (x: 30.5 -> 49.5, w: 19)
    b32 = FancyBboxPatch((30.5, 21.0), 19, 8.6, boxstyle="round,pad=0.3,rounding_size=0.5",
                         facecolor=c_box, edgecolor=c_p_border, linewidth=0.9)
    ax.add_patch(b32)
    ax.text(40.0, 27.2, "Cache Hit Check", fontsize=9.0, fontweight="bold", ha="center", color=c_p_head)
    ax.text(40.0, 24.9, r"If $M_t \in \mathcal{R}_t \to 0.0\,\mathrm{s}$", fontsize=7.8, ha="center", color="#1c613e")
    ax.text(40.0, 22.7, "Zero Load Overhead", fontsize=7.5, ha="center", color="#1c613e")

    # Box 3.3: Shielded Eviction (x: 51.5 -> 73.0, w: 21.5)
    b33 = FancyBboxPatch((51.5, 21.0), 21.5, 8.6, boxstyle="round,pad=0.3,rounding_size=0.5",
                         facecolor=c_box, edgecolor=c_p_border, linewidth=0.9)
    ax.add_patch(b33)
    ax.text(62.25, 27.2, "Shielded Eviction", fontsize=9.0, fontweight="bold", ha="center", color=c_p_head)
    ax.text(62.25, 24.9, "CostAwareEvictionPolicy", fontsize=7.6, ha="center", color="#222222")
    ax.text(62.25, 22.7, r"$W(t, k)$ Shielding: $1.8\times$", fontsize=7.5, ha="center", color=c_p_head)

    # Box 3.4: Headroom Prefetch Buffer (x: 75.0 -> 93.5, w: 18.5)
    b34 = FancyBboxPatch((75.0, 21.0), 18.5, 8.6, boxstyle="round,pad=0.3,rounding_size=0.5",
                         facecolor=c_box, edgecolor=c_p_border, linewidth=0.9)
    ax.add_patch(b34)
    ax.text(84.25, 27.2, "Prefetch Staging", fontsize=9.0, fontweight="bold", ha="center", color=c_p_head)
    ax.text(84.25, 24.9, r"$\mathrm{RAM}_{\mathrm{free}} \geq 1.0\,\mathrm{GB}$", fontsize=7.6, ha="center", color="#222222")
    ax.text(84.25, 22.7, r"$U_{\mathrm{prefetch}} > 0$", fontsize=7.6, ha="center", color="#1c613e")

    # =========================================================================
    # LAYER 4: EXECUTION BACKEND & TELEMETRY  [y: 2.0 -> 16.0]
    # Reordered: 4.1 Specialist -> 4.2 Hardware Telemetry -> 4.3 Independent AST Verifier (Rightmost)
    # =========================================================================
    r4 = FancyBboxPatch((3, 2.0), 92.5, 14.0, boxstyle="round,pad=0.5,rounding_size=1.0",
                        facecolor=c_e_bg, edgecolor=c_e_border, linewidth=1.4)
    ax.add_patch(r4)
    ax.text(5.5, 13.7, "EXECUTION BACKEND, VERIFICATION & HARDWARE TELEMETRY", 
            fontsize=10.0, fontweight="bold", color=c_e_head)

    # Box 4.1: Specialist Model Execution (x: 5.5 -> 34.0, w: 28.5)
    b41 = FancyBboxPatch((5.5, 3.5), 28.5, 8.6, boxstyle="round,pad=0.3,rounding_size=0.5",
                         facecolor=c_box, edgecolor=c_e_border, linewidth=0.9)
    ax.add_patch(b41)
    ax.text(19.75, 9.7, "Specialist Model Execution", fontsize=9.0, fontweight="bold", ha="center", color=c_e_head)
    ax.text(19.75, 7.4, r"Forward Pass $M_t(\mathcal{S}_t) \to y_t$", fontsize=8.2, ha="center", color="#222222")
    ax.text(19.75, 5.2, r"Emits Candidate Delta $\Delta\mathcal{S}_t$", fontsize=7.8, ha="center", color="#555555")

    # Arrow 4.1 -> 4.2
    a41 = FancyArrowPatch((34.0, 7.8), (38.5, 7.8), arrowstyle="-|>", mutation_scale=11, color=arrow_color, lw=1.2)
    ax.add_patch(a41)

    # Box 4.2: Hardware Telemetry (x: 38.5 -> 63.5, w: 25.0)
    b42 = FancyBboxPatch((38.5, 3.5), 25.0, 8.6, boxstyle="round,pad=0.3,rounding_size=0.5",
                         facecolor=c_box, edgecolor=c_e_border, linewidth=0.9)
    ax.add_patch(b42)
    ax.text(51.0, 9.7, "Hardware Telemetry", fontsize=9.0, fontweight="bold", ha="center", color=c_e_head)
    ax.text(51.0, 7.4, "Host: /proc/[pid]/statm", fontsize=7.6, ha="center", color="#333333")
    ax.text(51.0, 5.2, "GPU: NVML RSS Sampling", fontsize=7.6, ha="center", color="#555555")

    # Arrow 4.2 -> 4.3
    a42 = FancyArrowPatch((63.5, 7.8), (67.5, 7.8), arrowstyle="-|>", mutation_scale=11, color=arrow_color, lw=1.2)
    ax.add_patch(a42)

    # Box 4.3: Independent AST Verifier (x: 67.5 -> 93.5, w: 26.0)
    b43 = FancyBboxPatch((67.5, 3.5), 26.0, 8.6, boxstyle="round,pad=0.3,rounding_size=0.5",
                         facecolor=c_box, edgecolor="#1c613e", linewidth=1.1)
    ax.add_patch(b43)
    ax.text(80.5, 9.7, "Independent AST Verifier", fontsize=9.0, fontweight="bold", ha="center", color="#1c613e")
    ax.text(80.5, 7.4, "AST Arithmetic Certification", fontsize=7.8, ha="center", color="#222222")
    ax.text(80.5, 5.2, r"Certified Delta $\Delta\mathcal{S}_t^*$", fontsize=8.0, ha="center", color="#1c613e", fontweight="bold")

    # =========================================================================
    # VERTICAL INTER-LAYER CONTROL SIGNALS (Clean, uncrowded)
    # =========================================================================
    # Downward Signal 1: Stage Supervisor -> Scheduler (at x = 51.75)
    arr_d1 = FancyArrowPatch((51.75, 56.0), (51.75, 51.0), arrowstyle="-|>", mutation_scale=12, color="#143250", lw=1.5)
    ax.add_patch(arr_d1)
    pill1 = FancyBboxPatch((53.5, 52.2), 22, 2.8, boxstyle="round,pad=0.2,rounding_size=0.4",
                           facecolor="#ffffff", edgecolor="#143250", linewidth=0.8)
    ax.add_patch(pill1)
    ax.text(64.5, 53.6, r"Target Capability $C(s_t)$", fontsize=7.6, ha="center", va="center", color="#143250", fontweight="bold")

    # Downward Signal 2: Scheduler -> Pager (at x = 71.5)
    arr_d2 = FancyArrowPatch((71.5, 38.5), (71.5, 33.5), arrowstyle="-|>", mutation_scale=12, color="#523275", lw=1.5)
    ax.add_patch(arr_d2)
    pill2 = FancyBboxPatch((73.0, 34.7), 18, 2.8, boxstyle="round,pad=0.2,rounding_size=0.4",
                           facecolor="#ffffff", edgecolor="#523275", linewidth=0.8)
    ax.add_patch(pill2)
    ax.text(82.0, 36.1, r"Scheduled Model $M_t$", fontsize=7.6, ha="center", va="center", color="#523275", fontweight="bold")

    # Downward Signal 3: Pager -> Backend (at x = 17.0)
    arr_d3 = FancyArrowPatch((17.0, 21.0), (17.0, 16.0), arrowstyle="-|>", mutation_scale=12, color="#995212", lw=1.5)
    ax.add_patch(arr_d3)
    pill3 = FancyBboxPatch((19.0, 17.2), 22, 2.8, boxstyle="round,pad=0.2,rounding_size=0.4",
                           facecolor="#ffffff", edgecolor="#995212", linewidth=0.8)
    ax.add_patch(pill3)
    ax.text(30.0, 18.6, r"Resident Weights Ready", fontsize=7.6, ha="center", va="center", color="#995212", fontweight="bold")

    # =========================================================================
    # STATE VIRTUALIZATION FEEDBACK BUS (RIGHT MARGIN - ZERO COLLISION)
    # =========================================================================
    bus_x = 105.0
    
    # Horizontal out from AST Verifier Box 4.3 (x=93.5, y=7.8) -> bus_x
    arr_fb_out = FancyArrowPatch((93.5, 7.8), (bus_x, 7.8), arrowstyle="-", color="#701a5e", lw=1.6, linestyle="--")
    ax.add_patch(arr_fb_out)
    
    # Vertical trunk 1: from y=7.8 up to bottom of Return Bus Node Card at y=28.0
    arr_fb_up1 = FancyArrowPatch((bus_x, 7.8), (bus_x, 28.0), arrowstyle="-|>", mutation_scale=11, color="#701a5e", lw=1.6, linestyle="--")
    ax.add_patch(arr_fb_up1)
    
    # State Return Bus Processing Node Card: centered at bus_x=105, y=28.0 to 42.0 (w=20, h=14)
    fb_card = FancyBboxPatch((95.5, 28.0), 19.5, 14.0, boxstyle="round,pad=0.4,rounding_size=0.8",
                             facecolor="#ffffff", edgecolor="#701a5e", linewidth=1.3)
    ax.add_patch(fb_card)
    ax.text(105.25, 39.5, "STATE RETURN BUS", fontsize=8.2, fontweight="bold", ha="center", color="#701a5e")
    ax.text(105.25, 36.8, "Monotonic State Merge", fontsize=7.5, ha="center", color="#222222")
    ax.text(105.25, 33.8, r"$\mathcal{S}_{t+1} = \mathcal{S}_t \oplus \Delta\mathcal{S}_t^*$", fontsize=8.5, ha="center", color="#701a5e", fontweight="bold")
    ax.text(105.25, 31.0, r"(AST Certified)", fontsize=7.2, ha="center", color="#1c613e", style="italic")

    # Vertical trunk 2: from top of Card at y=42.0 up to y=60.6
    arr_fb_up2 = FancyArrowPatch((bus_x, 42.0), (bus_x, 60.6), arrowstyle="-", color="#701a5e", lw=1.6, linestyle="--")
    ax.add_patch(arr_fb_up2)

    # Horizontal return into State Carrier (Box 1.3) at (93.5, 60.6)
    arr_fb_in = FancyArrowPatch((bus_x, 60.6), (93.5, 60.6), arrowstyle="-|>", mutation_scale=13, color="#701a5e", lw=1.6, linestyle="--")
    ax.add_patch(arr_fb_in)

    plt.tight_layout()
    plt.savefig("fig_architecture_topology.pdf", dpi=300, bbox_inches="tight")
    plt.close()
    print("Generated publication-grade paper/fig_architecture_topology.pdf")

def create_control_flow_diagram():
    fig, ax = plt.subplots(figsize=(6.8, 8.8))
    ax.set_xlim(-10, 100)
    ax.set_ylim(-2, 146)
    ax.axis("off")

    nodes = [
        (134, r"User Objective / Task Goal $G$", "#1d446c", "#f4f7fa", 12),
        (120, r"Task Decomposition $\to$ Stage Plan $\mathcal{G}=(\mathcal{S},\mathcal{E})$", "#1d446c", "#ffffff", 10),
        (106, r"Working-Set Lookahead $W(t, k)$ & Demand Forecast", "#523275", "#f7f5fa", 10),
        (92,  r"Multi-Objective Scheduling: $\mathrm{Score}(m)$ via Empirical Profiling", "#523275", "#ffffff", 10),
        (78,  r"Model Pager: Cache Check, Admission & Shielded Eviction", "#995212", "#fbf6f0", 10),
        (64,  r"Opportunistic Prefetch Staging ($\Delta_{\mathrm{headroom}} \geq 1.0\,\mathrm{GB}$)", "#995212", "#ffffff", 10),
        (50,  r"Specialist Inference on Backend $M_t(\mathcal{S}_t) \to$ Candidate $\Delta\mathcal{S}_t$", "#1c613e", "#f2f8f5", 10),
        (36,  r"Independent AST Verification $\to$ Certified $\Delta\mathcal{S}_t^*$", "#1c613e", "#ffffff", 10),
        (22,  r"Monotonic State Merge: $\mathcal{S}_{t+1} = \mathcal{S}_t \oplus \Delta\mathcal{S}_t^*$", "#701a5e", "#fbf5fa", 10),
        (8,   r"Confidence Assessment & Loop Escalation / Next Stage", "#94202e", "#fdf4f5", 10),
    ]

    for y, label, border, bg, h in nodes:
        w = 84
        x = 8
        rect = FancyBboxPatch((x, y - h/2), w, h, boxstyle="round,pad=0.4,rounding_size=1.0",
                              facecolor=bg, edgecolor=border, linewidth=1.3)
        ax.add_patch(rect)
        ax.text(x + w/2, y, label, fontsize=8.8, fontweight="bold" if h > 10 else "normal", 
                ha="center", va="center", color=border)

    # Vertical Connecting Arrows
    for i in range(len(nodes) - 1):
        y_top = nodes[i][0] - nodes[i][4]/2
        y_bot = nodes[i+1][0] + nodes[i+1][4]/2
        arr = FancyArrowPatch((50, y_top), (50, y_bot), arrowstyle="-|>", mutation_scale=11, color="#333333", lw=1.2)
        ax.add_patch(arr)

    # Escalation loop arrow from bottom node back to scheduler
    arr_loop = FancyArrowPatch((8, 8), (8, 92),
                               connectionstyle="arc3,rad=-0.35",
                               arrowstyle="-|>", mutation_scale=12, color="#94202e", lw=1.4, linestyle="--")
    ax.add_patch(arr_loop)
    ax.text(-1.5, 50, "Escalation Loop\n(Confidence < Threshold)", fontsize=8, color="#94202e", ha="right", va="center", rotation=90)

    plt.tight_layout()
    plt.savefig("fig_control_flow.pdf", dpi=300, bbox_inches="tight")
    plt.close()
    print("Generated publication-grade paper/fig_control_flow.pdf")

if __name__ == "__main__":
    create_architecture_diagram()
    create_control_flow_diagram()
