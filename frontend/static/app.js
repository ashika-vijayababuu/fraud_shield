const form = document.getElementById("prediction-form");
const button = document.getElementById("predict-button");
const badge = document.getElementById("result-badge");
const scoreValue = document.getElementById("score-value");
const labelValue = document.getElementById("label-value");
const modelVersion = document.getElementById("model-version");
const modelVersionPanel = document.getElementById("model-version-panel");
const explanation = document.getElementById("explanation");
const scoreRing = document.querySelector(".score-ring");
const statTotal = document.getElementById("stat-total");
const statFraud = document.getElementById("stat-fraud");
const statLegit = document.getElementById("stat-legit");
const statRisk = document.getElementById("stat-risk");
const historyBody = document.getElementById("history-body");
const transactionsBody = document.getElementById("transactions-body");
const alertList = document.getElementById("alert-list");
const riskChart = document.getElementById("risk-chart");
const chartContext = riskChart.getContext("2d");
const tabButtons = document.querySelectorAll(".tab-button");
const tabPanels = document.querySelectorAll(".tab-panel");

function updateResult(data) {
  const percent = Math.round(data.fraud_probability * 100);
  const isFraud = data.fraud_label === "fraud";
  const angle = Math.max(0, Math.min(360, (percent / 100) * 360));
  const color = isFraud ? "var(--bad)" : "var(--good)";
  const fadedColor = isFraud ? "rgba(166, 62, 36, 0.12)" : "rgba(38, 106, 74, 0.12)";

  scoreValue.textContent = `${percent}%`;
  labelValue.textContent = data.fraud_label.toUpperCase();
  modelVersion.textContent = data.model_version;
  modelVersionPanel.textContent = data.model_version;
  badge.textContent = isFraud ? "High-risk transaction detected" : "Transaction looks legitimate";
  badge.className = `result-badge ${isFraud ? "result-risk" : "result-safe"}`;
  explanation.textContent = isFraud
    ? "The model sees this transaction as suspicious. High amount, risky merchant behavior, or unusual activity may be contributing to the score."
    : "The model sees this transaction as low risk based on the submitted behavior and merchant context.";
  scoreRing.style.background = `conic-gradient(${color} ${angle}deg, ${fadedColor} ${angle}deg)`;
}

function formatFlags(item) {
  const flags = [];
  if (item.international) flags.push("INTL");
  if (!item.card_present) flags.push("CNP");
  if (item.transaction_velocity_1h > 10) flags.push("FAST");
  return flags.length ? flags.join(", ") : "None";
}

function renderHistory(items) {
  if (!items.length) {
    const emptyRow = `<tr><td colspan="6" class="history-empty">No predictions yet. Score a transaction to populate the dashboard.</td></tr>`;
    historyBody.innerHTML = emptyRow;
    transactionsBody.innerHTML = `<tr><td colspan="6" class="history-empty">No transaction history yet.</td></tr>`;
    return;
  }

  const rows = items
    .map((item) => {
      const time = new Date(item.created_at).toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      });
      const percent = Math.round(item.fraud_probability * 100);
      const labelClass = item.fraud_label === "fraud" ? "result-risk" : "result-safe";

      return `
        <tr>
          <td>${time}</td>
          <td>$${Number(item.transaction_amount).toFixed(2)}</td>
          <td>${percent}%</td>
          <td><span class="history-label ${labelClass}">${item.fraud_label.toUpperCase()}</span></td>
          <td>${item.source.toUpperCase()}</td>
          <td>${formatFlags(item)}</td>
        </tr>
      `;
    })
    .join("");

  historyBody.innerHTML = rows;
  transactionsBody.innerHTML = rows;
}

function renderAlerts(items) {
  const alerts = items.filter((item) => item.fraud_label === "fraud");

  if (!alerts.length) {
    alertList.innerHTML = `<article class="alert-empty">No fraud alerts yet.</article>`;
    return;
  }

  alertList.innerHTML = alerts
    .map((item) => {
      const percent = Math.round(item.fraud_probability * 100);
      return `
        <article class="alert-item">
          <span class="eyebrow">Alert</span>
          <strong>${percent}% risk on $${Number(item.transaction_amount).toFixed(2)}</strong>
          <p>${item.source.toUpperCase()} event with flags: ${formatFlags(item)}.</p>
        </article>
      `;
    })
    .join("");
}

function renderChart(items) {
  const width = riskChart.width;
  const height = riskChart.height;
  chartContext.clearRect(0, 0, width, height);

  chartContext.strokeStyle = "rgba(53, 41, 29, 0.16)";
  chartContext.lineWidth = 1;

  for (let i = 1; i <= 4; i += 1) {
    const y = (height / 5) * i;
    chartContext.beginPath();
    chartContext.moveTo(0, y);
    chartContext.lineTo(width, y);
    chartContext.stroke();
  }

  if (!items.length) {
    chartContext.fillStyle = "#6e6256";
    chartContext.font = "16px Source Sans 3";
    chartContext.fillText("Risk trend will appear after predictions are made.", 20, height / 2);
    return;
  }

  const values = items.map((item) => item.fraud_probability);
  const stepX = items.length > 1 ? width / (items.length - 1) : width / 2;

  chartContext.beginPath();
  values.forEach((value, index) => {
    const x = items.length > 1 ? index * stepX : width / 2;
    const y = height - value * (height - 24) - 12;
    if (index === 0) {
      chartContext.moveTo(x, y);
    } else {
      chartContext.lineTo(x, y);
    }
  });
  chartContext.strokeStyle = "#bf5a2b";
  chartContext.lineWidth = 4;
  chartContext.stroke();

  values.forEach((value, index) => {
    const x = items.length > 1 ? index * stepX : width / 2;
    const y = height - value * (height - 24) - 12;
    chartContext.beginPath();
    chartContext.arc(x, y, 5, 0, Math.PI * 2);
    chartContext.fillStyle = value >= 0.5 ? "#a63e24" : "#266a4a";
    chartContext.fill();
  });
}

async function refreshDashboard() {
  try {
    const [statsResponse, historyResponse] = await Promise.all([
      fetch("/api/stats"),
      fetch("/api/recent-predictions"),
    ]);

    if (!statsResponse.ok || !historyResponse.ok) {
      throw new Error("Dashboard request failed");
    }

    const stats = await statsResponse.json();
    const history = await historyResponse.json();

    statTotal.textContent = stats.total_predictions;
    statFraud.textContent = stats.fraud_count;
    statLegit.textContent = stats.legit_count;
    statRisk.textContent = `${Math.round(stats.average_risk * 100)}%`;

    renderHistory(history);
    renderAlerts(history);
    renderChart(history.slice().reverse());
  } catch (error) {
    explanation.textContent = "Dashboard metrics are temporarily unavailable. The prediction form can still be used.";
  }
}

async function submitPrediction(event) {
  event.preventDefault();
  button.disabled = true;
  button.textContent = "Scoring...";

  const formData = new FormData(form);
  const payload = {
    transaction_amount: Number(formData.get("transaction_amount")),
    customer_age: Number(formData.get("customer_age")),
    merchant_risk_score: Number(formData.get("merchant_risk_score")),
    transaction_velocity_1h: Number(formData.get("transaction_velocity_1h")),
    card_present: formData.get("card_present") === "on",
    international: formData.get("international") === "on",
  };

  try {
    const response = await fetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error("Prediction request failed");
    }

    const data = await response.json();
    updateResult(data);
    await refreshDashboard();
  } catch (error) {
    badge.textContent = "Unable to score transaction";
    badge.className = "result-badge result-risk";
    explanation.textContent = "The frontend could not reach the prediction API. Make sure the app is running locally.";
  } finally {
    button.disabled = false;
    button.textContent = "Predict Risk";
  }
}

form.addEventListener("submit", submitPrediction);
refreshDashboard();
setInterval(refreshDashboard, 5000);
modelVersionPanel.textContent = modelVersion.textContent;

tabButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const nextTab = button.dataset.tab;

    tabButtons.forEach((item) => {
      item.classList.toggle("active", item === button);
    });

    tabPanels.forEach((panel) => {
      panel.classList.toggle("active", panel.dataset.panel === nextTab);
    });
  });
});
