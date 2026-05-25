import "./style.css";
import { api } from "./api.js";
import { initEngine, isEngineReady, chat as llmChat, checkWebGPU } from "./llm.js";

let currentPage = "overview";
let pageData = {};

const NAV_ITEMS = [
  { id: "overview", label: "Overview", icon: "📊" },
  { id: "live", label: "Live Feed", icon: "📡" },
  { id: "patrons", label: "Patron Context", icon: "👤" },
  { id: "kpi", label: "KPI", icon: "📈" },
  { id: "operations", label: "Member Ops", icon: "🏨" },
  { id: "actions", label: "AI Actions", icon: "🎯" },
  { id: "simulation", label: "Simulation Lab", icon: "🧪" },
  { id: "tasks", label: "Task Center", icon: "✅" },
  { id: "campaigns", label: "Campaigns", icon: "📢" },
  { id: "copilot", label: "AI Copilot", icon: "🤖" },
];

const app = document.getElementById("app");
app.innerHTML = `
  <div class="layout">
    <aside class="sidebar">
      <div class="sidebar-brand">Decision Intelligence<br/>Platform</div>
      <nav class="sidebar-nav" id="nav"></nav>
      <div class="sidebar-footer">v0.2 Demo | 30K DAU</div>
    </aside>
    <main class="main" id="main-content"><div class="loading">Loading...</div></main>
  </div>
`;

const navEl = document.getElementById("nav");
const mainEl = document.getElementById("main-content");

navEl.innerHTML = NAV_ITEMS.map(
  (n) => `<button class="nav-item ${n.id === currentPage ? "active" : ""}" data-page="${n.id}">
    <span class="nav-icon">${n.icon}</span><span class="nav-label">${n.label}</span>
  </button>`
).join("");

navEl.addEventListener("click", (e) => {
  const btn = e.target.closest(".nav-item");
  if (!btn) return;
  // Cleanup SSE on page switch
  if (currentPage === "live" && pageData._eventSource) {
    pageData._eventSource.close();
    pageData._eventSource = null;
  }
  currentPage = btn.dataset.page;
  document.querySelectorAll(".nav-item").forEach((b) => b.classList.toggle("active", b.dataset.page === currentPage));
  renderPage();
});

function fmt(n, prefix = "$") {
  if (n == null) return "N/A";
  return prefix + Number(n).toLocaleString("en-US", { maximumFractionDigits: 0 });
}
function pct(n) {
  if (n == null) return "N/A";
  return (n * 100).toFixed(1) + "%";
}
function esc(s) {
  const d = document.createElement("div");
  d.textContent = s || "";
  return d.innerHTML;
}

// Server-side LLM streaming fallback (POST /api/llm) with SSE parsing and retries
async function serverChat(messages, options = {}) {
  const maxTokens = options.maxTokens || options.max_tokens || 400;
  const temperature = options.temperature || 0.2;
  const payload = { messages, max_tokens: maxTokens, temperature };
  const MAX_RETRIES = 2;
  const BACKOFF_BASE = 500;
  for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
    try {
      const res = await fetch("/api/llm", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (!res.ok) {
        const txt = await res.text().catch(() => "");
        throw new Error(`LLM server error: ${res.status} ${txt}`);
      }
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      return (async function* () {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });
          let idx;
          while ((idx = buffer.indexOf("\n\n")) !== -1) {
            const frame = buffer.slice(0, idx);
            buffer = buffer.slice(idx + 2);
            const lines = frame.split(/\r?\n/);
            for (const line of lines) {
              if (line.startsWith("data:")) {
                const data = line.slice(5).trim();
                try {
                  const obj = JSON.parse(data);
                  const content = (obj.choices && obj.choices[0] && (obj.choices[0].delta?.content || obj.choices[0].text)) || data;
                  yield { choices: [{ delta: { content } }] };
                } catch (e) {
                  yield { choices: [{ delta: { content: data } }] };
                }
              }
            }
          }
        }
        if (buffer.length) {
          const lines = buffer.split(/\r?\n/);
          for (const line of lines) {
            if (line.startsWith("data:")) {
              const data = line.slice(5).trim();
              try {
                const obj = JSON.parse(data);
                const content = (obj.choices && obj.choices[0] && (obj.choices[0].delta?.content || obj.choices[0].text)) || data;
                yield { choices: [{ delta: { content } }] };
              } catch (e) {
                yield { choices: [{ delta: { content: data } }] };
              }
            }
          }
        }
      })();
    } catch (err) {
      if (attempt < MAX_RETRIES) {
        await new Promise(r => setTimeout(r, BACKOFF_BASE * Math.pow(2, attempt)));
        continue;
      }
      throw err;
    }
  }
}

async function renderPage() {
  mainEl.innerHTML = '<div class="loading">Loading...</div>';
  try {
    const renderer = pages[currentPage];
    if (renderer) await renderer();
    else mainEl.innerHTML = '<div class="empty-state">Page not found</div>';
  } catch (err) {
    mainEl.innerHTML = `<div class="error-state">Error: ${esc(err.message)}</div>`;
    console.error(err);
  }
}

const pages = {};

// ===== Overview =====
pages.overview = async () => {
  const data = await api.getOverview();
  const t = data.today || {};
  const tiers = data.tier_breakdown || [];
  const trend = data.trend_7day || [];

  mainEl.innerHTML = `
    <div class="page-header"><h1>Overview</h1><span class="page-subtitle">AI Simulation Lab - Decision Intelligence Platform</span></div>
    <div class="kpi-cards">
      <div class="kpi-card"><div class="kpi-label">Active Patrons</div><div class="kpi-value">${fmt(t.active_patrons, "")}</div></div>
      <div class="kpi-card"><div class="kpi-label">Total Wagered</div><div class="kpi-value">${fmt(t.total_wagered)}</div></div>
      <div class="kpi-card"><div class="kpi-label">Net Revenue</div><div class="kpi-value">${fmt(t.net_revenue)}</div></div>
      <div class="kpi-card"><div class="kpi-label">Avg ADT</div><div class="kpi-value">${fmt(t.avg_adt)}</div></div>
      <div class="kpi-card"><div class="kpi-label">Campaign Response</div><div class="kpi-value">${pct(t.campaign_response_rate)}</div></div>
      <div class="kpi-card"><div class="kpi-label">Churn Risk</div><div class="kpi-value highlight-danger">${fmt(t.churn_risk_count, "")}</div></div>
    </div>
    <div class="grid-2">
      <div class="card">
        <h3>Tier Breakdown</h3>
        <table class="data-table"><thead><tr><th>Tier</th><th>Count</th><th>Avg ADT</th><th>Avg LTV</th><th>Churn Risk</th></tr></thead>
        <tbody>${tiers.map(r => `<tr><td><span class="tier-badge tier-${r.tier.toLowerCase()}">${r.tier}</span></td>
          <td>${fmt(r.count,"")}}</td><td>${fmt(r.avg_adt)}</td><td>${fmt(r.avg_ltv)}</td>
          <td class="${r.avg_churn>0.3?"text-danger":""}">${pct(r.avg_churn)}</td></tr>`).join("")}</tbody></table>
      </div>
      <div class="card">
        <h3>7-Day Trend</h3>
        <div class="sparkline-data">${trend.map(r => `<div class="spark-row">
          <span class="spark-date">${r.kpi_date}</span><span class="spark-val">${fmt(r.total_wagered)}</span>
          <span class="spark-val">${fmt(r.net_revenue)}</span><span class="spark-val">${fmt(r.active_patrons,"")} DAU</span></div>`).join("")}</div>
      </div>
    </div>
    <div class="card"><h3>Quick Actions</h3><div class="action-row">
      <button class="btn" onclick="document.querySelector('[data-page=live]').click()">Live Feed</button>
      <button class="btn" onclick="document.querySelector('[data-page=actions]').click()">AI Actions</button>
      <button class="btn" onclick="document.querySelector('[data-page=simulation]').click()">Run Simulation</button>
      <button class="btn" onclick="document.querySelector('[data-page=tasks]').click()">View Tasks (${data.summary.active_tasks})</button>
    </div></div>`;
};

// ===== Live Feed =====
... (file continues)
