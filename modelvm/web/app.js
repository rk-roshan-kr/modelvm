// ModelVM Interactive Web Visualizer Application

let socket = null;
let currentCSP = null;
let currentModels = [];
let currentMemoryStatus = {
  active_memory_gb: 0.0,
  memory_budget_gb: 8.0,
  free_memory_gb: 8.0,
  peak_memory_gb: 0.0,
  total_library_size_gb: 52.7,
  resident_models: [],
  disk_models: [],
  cache_hit_rate: 0.0,
};

// Preset task queries
const PRESET_QUERIES = {
  pdr_example: "Analyze this scientific paper, reproduce its numerical result, write the implementation, and explain the physical meaning.",
  financial_quant: "Develop algorithmic trading strategy backtest, verify stochastic calculus proofs, implement vectorized Python engine, and stress-test market shocks.",
  clinical_trial: "Evaluate clinical trial dataset, verify statistical significance, write reproducibility pipeline, and summarize biological mechanism.",
};

// DOM Elements
const wsDot = document.getElementById("ws-dot");
const wsStatus = document.getElementById("ws-status");
const activeRamVal = document.getElementById("active-ram-val");
const budgetRamVal = document.getElementById("budget-ram-val");
const activeRamPct = document.getElementById("active-ram-pct");
const ramMeterFill = document.getElementById("ram-meter-fill");
const compActiveSlice = document.getElementById("comp-active-slice");
const headerBudget = document.getElementById("header-budget-size");
const headerLib = document.getElementById("header-lib-size");
const statSavings = document.getElementById("stat-savings");
const statPeak = document.getElementById("stat-peak");
const statDensity = document.getElementById("stat-density");
const statHitrate = document.getElementById("stat-hitrate");
const residentTilesList = document.getElementById("resident-tiles-list");
const diskTilesList = document.getElementById("disk-tiles-list");
const residentCountBadge = document.getElementById("resident-count-badge");
const diskCountBadge = document.getElementById("disk-count-badge");
const timelineStream = document.getElementById("timeline-stream");
const taskGoalInput = document.getElementById("task-goal-input");
const taskPresets = document.getElementById("task-presets");
const modeSelect = document.getElementById("mode-select");
const budgetSlider = document.getElementById("budget-slider");
const budgetSliderVal = document.getElementById("budget-slider-val");
const btnRunTask = document.getElementById("btn-run-task");
const btnRunAblation = document.getElementById("btn-run-ablation");
const ablationGrid = document.getElementById("ablation-grid");
const ablationBanner = document.getElementById("ablation-banner");
const ablationWinnerText = document.getElementById("ablation-winner-text");
const catalogFullGrid = document.getElementById("catalog-full-grid");

// Initialize
document.addEventListener("DOMContentLoaded", () => {
  setupNavigation();
  setupEventListeners();
  connectWebSocket();
  fetchInitialData();
});

// Navigation Tabs
function setupNavigation() {
  const tabs = document.querySelectorAll(".nav-tab");
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      const targetId = tab.getAttribute("data-tab");
      document.querySelectorAll(".view-panel").forEach(p => p.classList.remove("active"));
      document.getElementById(targetId).classList.add("active");
    });
  });

  // CSP Tabs
  const cspTabs = document.querySelectorAll(".csp-tab");
  cspTabs.forEach(t => {
    t.addEventListener("click", () => {
      cspTabs.forEach(x => x.classList.remove("active"));
      t.classList.add("active");
      renderCSPTab(t.getAttribute("data-tab"));
    });
  });
}

// Event Listeners
function setupEventListeners() {
  // Preset change
  taskPresets.addEventListener("change", (e) => {
    const val = e.target.value;
    if (PRESET_QUERIES[val]) {
      taskGoalInput.value = PRESET_QUERIES[val];
    }
  });

  // Budget slider
  budgetSlider.addEventListener("input", (e) => {
    const budget = parseFloat(e.target.value);
    budgetSliderVal.textContent = budget.toFixed(1);
    updateBudget(budget);
  });

  // Run Task
  btnRunTask.addEventListener("click", runTask);

  // Clear Timeline
  document.getElementById("btn-clear-timeline").addEventListener("click", () => {
    timelineStream.innerHTML = '<div class="timeline-empty">Timeline cleared.</div>';
  });

  // Run Ablation
  btnRunAblation.addEventListener("click", runAblationStudy);
}

// WebSocket Connection
function connectWebSocket() {
  const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
  const wsUrl = `${proto}//${window.location.host}/ws`;

  socket = new WebSocket(wsUrl);

  socket.onopen = () => {
    wsDot.style.background = "var(--neon-green)";
    wsStatus.textContent = "KERNEL ONLINE";
  };

  socket.onmessage = (event) => {
    try {
      const msg = jsonParse(event.data);
      handleSocketMessage(msg);
    } catch (e) {
      console.error("Socket message error:", e);
    }
  };

  socket.onclose = () => {
    wsDot.style.background = "var(--neon-red)";
    wsStatus.textContent = "DISCONNECTED";
    setTimeout(connectWebSocket, 2000);
  };
}

function jsonParse(str) {
  return JSON.parse(str);
}

function handleSocketMessage(msg) {
  if (msg.type === "INITIAL_STATE") {
    currentMemoryStatus = msg.memory_status;
    currentModels = msg.models;
    renderMemory();
    renderCatalog();
  } else if (msg.type === "PAGING_EVENT") {
    if (msg.memory_status) {
      currentMemoryStatus = msg.memory_status;
      renderMemory();
    }
    appendTimelineItem(msg.data);
  } else if (msg.type === "STAGE_COMPLETED") {
    if (msg.memory_status) {
      currentMemoryStatus = msg.memory_status;
      renderMemory();
    }
    if (msg.data.csp_snapshot) {
      currentCSP = msg.data.csp_snapshot;
      renderCSP();
    }
    appendStageItem(msg.data);
  } else if (msg.type === "TASK_FINISHED") {
    btnRunTask.disabled = false;
    btnRunTask.innerHTML = '<span class="btn-icon">▶</span><span class="btn-text">Execute Task</span>';
    if (msg.summary && msg.summary.final_csp) {
      currentCSP = msg.summary.final_csp;
      renderCSP();
    }
  }
}

// REST Fetch
async function fetchInitialData() {
  try {
    const [statusRes, modelsRes] = await Promise.all([
      fetch("/api/status"),
      fetch("/api/models"),
    ]);
    currentMemoryStatus = await statusRes.json();
    currentModels = await modelsRes.json();
    renderMemory();
    renderCatalog();
  } catch (err) {
    console.error("Fetch initial data error:", err);
  }
}

// Update Budget
async function updateBudget(budget) {
  try {
    const res = await fetch("/api/budget", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ budget_gb: budget }),
    });
    currentMemoryStatus = await res.json();
    renderMemory();
  } catch (err) {
    console.error("Update budget error:", err);
  }
}

// Execute Task
async function runTask() {
  const goal = taskGoalInput.value.trim();
  if (!goal) return;

  const budget = parseFloat(budgetSlider.value);
  const mode = modeSelect.value;

  btnRunTask.disabled = true;
  btnRunTask.innerHTML = '<span class="btn-icon">⏳</span><span class="btn-text">Paging Models...</span>';

  try {
    const res = await fetch("/api/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        goal: goal,
        budget_gb: budget,
        ablation_mode: mode,
      }),
    });
    const summary = await res.json();
    currentCSP = summary.final_csp;
    renderCSP();

    statSavings.textContent = `${(summary.memory_savings_ratio * 100).toFixed(1)}%`;
    statPeak.textContent = `${summary.peak_resident_memory_gb.toFixed(1)} GB`;
    statDensity.textContent = summary.capability_density.toFixed(2);
    statHitrate.textContent = `${(summary.cache_hit_rate * 100).toFixed(1)}%`;

    btnRunTask.disabled = false;
    btnRunTask.innerHTML = '<span class="btn-icon">▶</span><span class="btn-text">Execute Task</span>';
  } catch (err) {
    console.error("Run task error:", err);
    btnRunTask.disabled = false;
    btnRunTask.innerHTML = '<span class="btn-icon">▶</span><span class="btn-text">Execute Task</span>';
  }
}

// Render Memory Status & Slots
function renderMemory() {
  const active = currentMemoryStatus.active_memory_gb || 0.0;
  const budget = currentMemoryStatus.memory_budget_gb || 8.0;
  const totalLib = currentMemoryStatus.total_library_size_gb || 52.7;
  const pct = Math.min(100, Math.round((active / budget) * 100));

  activeRamVal.textContent = active.toFixed(1);
  budgetRamVal.textContent = budget.toFixed(1);
  activeRamPct.textContent = `${pct}% Used`;
  ramMeterFill.style.width = `${pct}%`;

  headerBudget.textContent = `${budget.toFixed(1)} GB`;
  headerLib.textContent = `${totalLib.toFixed(1)} GB`;

  // Virtualization slice comparison
  const compPct = Math.max(5, Math.min(95, Math.round((active / totalLib) * 100)));
  compActiveSlice.style.width = `${compPct}%`;
  compActiveSlice.innerHTML = `<span>Active: ${active.toFixed(1)} GB</span>`;

  // Resident Slots
  const residents = currentMemoryStatus.resident_models || [];
  residentCountBadge.textContent = `${residents.length} Active (${active.toFixed(1)} / ${budget.toFixed(1)} GB)`;

  if (residents.length === 0) {
    residentTilesList.innerHTML = '<div class="empty-state">No models currently paged in. Execute a task to trigger dynamic paging.</div>';
  } else {
    residentTilesList.innerHTML = residents.map(m => `
      <div class="model-tile resident">
        <div class="tile-top">
          <div class="tile-name">${m.name}</div>
          <div class="tile-ram">${m.ram_required.toFixed(1)} GB</div>
        </div>
        <div class="tile-caps">
          ${m.capabilities.map(c => `<span class="cap-badge">${c}</span>`).join("")}
        </div>
        <button class="tile-btn" onclick="manualPageOut('${m.id}')">Unload / Page Out</button>
      </div>
    `).join("");
  }

  // Disk Slots
  const disks = currentMemoryStatus.disk_models || [];
  diskCountBadge.textContent = `${disks.length} Models Paged to Storage`;

  diskTilesList.innerHTML = disks.map(m => `
    <div class="model-tile">
      <div class="tile-top">
        <div class="tile-name">${m.name}</div>
        <div class="tile-ram">${m.ram_required.toFixed(1)} GB</div>
      </div>
      <div class="tile-caps">
        ${m.capabilities.map(c => `<span class="cap-badge">${c}</span>`).join("")}
      </div>
      <button class="tile-btn" onclick="manualPageIn('${m.id}')">Page In to RAM</button>
    </div>
  `).join("");
}

// Manual Paging Controls
window.manualPageIn = async function(modelId) {
  try {
    const res = await fetch("/api/page_in", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model_id: modelId }),
    });
    const data = await res.json();
    currentMemoryStatus = data.status;
    renderMemory();
  } catch (err) {
    console.error("Manual page in error:", err);
  }
};

window.manualPageOut = async function(modelId) {
  try {
    const res = await fetch("/api/page_out", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model_id: modelId }),
    });
    const data = await res.json();
    currentMemoryStatus = data.status;
    renderMemory();
  } catch (err) {
    console.error("Manual page out error:", err);
  }
};

// Timeline item rendering
function appendTimelineItem(event) {
  const item = document.createElement("div");
  item.className = `timeline-item ${event.action}`;
  item.innerHTML = `
    <div class="item-action-badge ${event.action}">${event.action}</div>
    <div class="item-content">
      <div class="item-title">${event.model_id} (${event.ram_gb.toFixed(1)} GB)</div>
      <div class="item-desc">${event.reason}</div>
      <div class="item-meta">Active RAM: ${event.active_memory_gb.toFixed(1)} / ${event.memory_budget_gb.toFixed(1)} GB | Latency: ${event.duration_sec.toFixed(2)}s</div>
    </div>
  `;
  timelineStream.prepend(item);
}

function appendStageItem(stage) {
  const item = document.createElement("div");
  item.className = "timeline-item STAGE";
  item.innerHTML = `
    <div class="item-action-badge STAGE">STAGE ${stage.stage_index + 1}</div>
    <div class="item-content">
      <div class="item-title">${stage.stage_title} [${stage.capability.toUpperCase()}]</div>
      <div class="item-desc">Model: <strong>${stage.model_name}</strong> | Confidence: ${(stage.confidence_score * 100).toFixed(0)}%</div>
      <div class="item-meta">Exec Time: ${stage.execution_duration_sec.toFixed(2)}s | Paging Latency: ${stage.paging_duration_sec.toFixed(2)}s</div>
    </div>
  `;
  timelineStream.prepend(item);
}

// CSP Inspector Rendering
function renderCSP() {
  if (!currentCSP) return;

  document.getElementById("csp-stage-indicator").textContent = `Stage ${currentCSP.stage_index || 0}: ${currentCSP.current_capability ? currentCSP.current_capability.toUpperCase() : "Active"}`;

  document.getElementById("count-facts").textContent = (currentCSP.facts || []).length;
  document.getElementById("count-calcs").textContent = (currentCSP.calculations || []).length;
  document.getElementById("count-evidence").textContent = (currentCSP.evidence || []).length;
  const decCount = (currentCSP.decisions || []).length + (currentCSP.assumptions || []).length;
  document.getElementById("count-decisions").textContent = decCount;
  document.getElementById("count-artifacts").textContent = Object.keys(currentCSP.artifacts || {}).length;

  const activeTab = document.querySelector(".csp-tab.active");
  if (activeTab) {
    renderCSPTab(activeTab.getAttribute("data-tab"));
  }
}

function renderCSPTab(tabName) {
  const container = document.getElementById("csp-tab-content");
  if (!currentCSP) {
    container.innerHTML = '<div class="csp-empty">No Cognitive State Packet loaded yet.</div>';
    return;
  }

  if (tabName === "facts") {
    const facts = currentCSP.facts || [];
    if (facts.length === 0) {
      container.innerHTML = '<div class="csp-empty">No verified facts recorded yet.</div>';
    } else {
      container.innerHTML = facts.map(f => `<div class="csp-list-item">💡 ${f}</div>`).join("");
    }
  } else if (tabName === "calculations") {
    const calcs = currentCSP.calculations || [];
    if (calcs.length === 0) {
      container.innerHTML = '<div class="csp-empty">No calculations performed yet.</div>';
    } else {
      container.innerHTML = calcs.map(c => `
        <div class="csp-list-item">
          <div class="calc-row">
            <span class="calc-expr">${c.expression}</span>
            <span class="calc-res">= ${c.result} ${c.units || ""}</span>
          </div>
        </div>
      `).join("");
    }
  } else if (tabName === "evidence") {
    const evs = currentCSP.evidence || [];
    if (evs.length === 0) {
      container.innerHTML = '<div class="csp-empty">No evidence claims captured yet.</div>';
    } else {
      container.innerHTML = evs.map(e => `
        <div class="csp-list-item">
          <div class="evidence-claim">📌 ${e.claim}</div>
          <div class="evidence-meta">
            <span>Source: ${e.source}</span>
            <span>Confidence: ${(e.confidence * 100).toFixed(0)}%</span>
          </div>
        </div>
      `).join("");
    }
  } else if (tabName === "decisions") {
    const decisions = currentCSP.decisions || [];
    const assumptions = currentCSP.assumptions || [];
    const uncertainties = currentCSP.uncertainties || [];

    let html = "";
    if (decisions.length > 0) {
      html += `<strong>Architectural Decisions:</strong>` + decisions.map(d => `<div class="csp-list-item">⚖️ ${d}</div>`).join("");
    }
    if (assumptions.length > 0) {
      html += `<strong style="margin-top: 10px; display: block;">Working Assumptions:</strong>` + assumptions.map(a => `<div class="csp-list-item">🔬 ${a}</div>`).join("");
    }
    if (uncertainties.length > 0) {
      html += `<strong style="margin-top: 10px; display: block; color: var(--neon-yellow);">Open Uncertainties:</strong>` + uncertainties.map(u => `<div class="csp-list-item">⚠️ ${u}</div>`).join("");
    }
    container.innerHTML = html || '<div class="csp-empty">No decisions or assumptions logged yet.</div>';
  } else if (tabName === "artifacts") {
    const artifacts = currentCSP.artifacts || {};
    const keys = Object.keys(artifacts);
    if (keys.length === 0) {
      container.innerHTML = '<div class="csp-empty">No code or report artifacts generated yet.</div>';
    } else {
      container.innerHTML = keys.map(k => `
        <div style="margin-bottom: 12px;">
          <strong style="color: var(--neon-cyan); font-family: var(--font-mono); font-size: 0.85rem;">${k}</strong>
          <pre class="code-block-artifact">${artifacts[k]}</pre>
        </div>
      `).join("");
    }
  } else if (tabName === "raw-json") {
    container.innerHTML = `<pre class="code-block-artifact">${JSON.stringify(currentCSP, null, 2)}</pre>`;
  }
}

// Run Critical Ablation Study (Section 13)
async function runAblationStudy() {
  btnRunAblation.disabled = true;
  btnRunAblation.innerHTML = '<span class="btn-icon">⏳</span> Benchmarking 4 Configurations...';

  try {
    const goal = taskGoalInput.value.trim() || PRESET_QUERIES.pdr_example;
    const budget = parseFloat(budgetSlider.value);

    const res = await fetch("/api/ablation", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ goal: goal, budget_gb: budget }),
    });

    const report = await res.json();
    renderAblationReport(report);

    btnRunAblation.disabled = false;
    btnRunAblation.innerHTML = '<span class="btn-icon">⚡</span> Run 4-Configuration Benchmark';
  } catch (err) {
    console.error("Ablation error:", err);
    btnRunAblation.disabled = false;
    btnRunAblation.innerHTML = '<span class="btn-icon">⚡</span> Run 4-Configuration Benchmark';
  }
}

function renderAblationReport(report) {
  ablationBanner.style.display = "flex";
  ablationWinnerText.textContent = report.winner_analysis;

  const runs = report.runs || {};
  const cardsHtml = Object.keys(runs).map(key => {
    const m = runs[key];
    const isWinner = key === "D_FULL_MODELVM";
    const nameMap = {
      "A_STATIC_ROUTER": "Mode A: Static Router",
      "B_DYNAMIC_NO_CSP": "Mode B: Dynamic (No CSP)",
      "C_DYNAMIC_WITH_CSP": "Mode C: Dynamic + CSP",
      "D_FULL_MODELVM": "Mode D: Full ModelVM",
    };
    return `
      <div class="ablation-card ${isWinner ? 'winner-card' : ''}">
        <div class="ablation-header">
          <div class="ablation-name">${nameMap[key] || key}</div>
          <div class="ablation-badge">${isWinner ? '🏆 Optimal Architecture' : 'Baseline Reference'}</div>
        </div>
        <div class="ablation-stat-row">
          <span>Peak Resident Memory</span>
          <span class="text-neon-blue">${m.peak_memory_gb.toFixed(1)} GB</span>
        </div>
        <div class="ablation-stat-row">
          <span>Memory Savings Ratio</span>
          <span class="text-neon-green">${m.memory_savings_percent.toFixed(1)}%</span>
        </div>
        <div class="ablation-stat-row">
          <span>Capability Quality</span>
          <span class="text-neon-purple">${(m.capability_coverage_score * 100).toFixed(0)}%</span>
        </div>
        <div class="ablation-stat-row">
          <span>Capability Density</span>
          <span class="text-neon-yellow">${m.capability_density.toFixed(2)}</span>
        </div>
        <div class="ablation-stat-row">
          <span>Paging Latency</span>
          <span>${m.paging_overhead_sec.toFixed(2)}s</span>
        </div>
        <div class="ablation-stat-row">
          <span>Verified Calculations</span>
          <span>${m.calculations_verified}</span>
        </div>
      </div>
    `;
  }).join("");

  ablationGrid.innerHTML = cardsHtml;
}

// Render Model Catalog View
function renderCatalog() {
  if (!catalogFullGrid || currentModels.length === 0) return;

  catalogFullGrid.innerHTML = currentModels.map(m => `
    <div class="catalog-card">
      <div class="catalog-title">${m.name}</div>
      <div class="catalog-desc">${m.description || "Specialist open-weight reasoning model"}</div>
      <div class="catalog-meta">
        <div>Footprint: <strong style="color: var(--neon-cyan);">${m.ram_required.toFixed(1)} GB</strong></div>
        <div>Load Time: <strong>${m.load_time.toFixed(1)}s</strong></div>
        <div>Params: <strong>${m.parameters_billion}B</strong></div>
        <div>Format: <strong>${m.quantization}</strong></div>
      </div>
    </div>
  `).join("");
}
