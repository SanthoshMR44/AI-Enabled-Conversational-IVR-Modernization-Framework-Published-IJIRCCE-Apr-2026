document.addEventListener("DOMContentLoaded", () => {
  const role = localStorage.getItem("role");
  if (role !== "admin") {
    document.querySelectorAll(".admin-only").forEach(el => el.style.display = "none");
  }

  fetchDashboardData();
});

async function fetchDashboardData() {
  const res = await fetch("/api/analytics/dashboard");
  if (!res.ok) return;
  const data = await res.json();

  document.getElementById("stat-calls").innerText = data.total_calls;
  document.getElementById("stat-duration").innerText = data.avg_duration + "s";
  document.getElementById("stat-accuracy").innerText = data.accuracy + "%";
  document.getElementById("stat-sentiment").innerText = data.avg_sentiment;

  // Build Intent Chart
  const intentCtx = document.getElementById("intentChart").getContext("2d");
  const intentLabels = Object.keys(data.intent_distribution);
  const intentValues = Object.values(data.intent_distribution);

  new Chart(intentCtx, {
    type: 'bar',
    data: {
      labels: intentLabels.length ? intentLabels : ["No Data"],
      datasets: [{
        label: 'Intent Matches',
        data: intentValues.length ? intentValues : [0],
        backgroundColor: '#3b82f6',
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.05)' } },
        x: { grid: { display: false } }
      }
    }
  });

  // Build Sentiment Chart
  const sentimentCtx = document.getElementById("sentimentChart").getContext("2d");
  const sDist = data.sentiment_distribution;
  new Chart(sentimentCtx, {
    type: 'doughnut',
    data: {
      labels: ['Positive', 'Neutral', 'Negative'],
      datasets: [{
        data: [sDist.Positive, sDist.Neutral, sDist.Negative],
        backgroundColor: ['#10b981', '#6b7280', '#ef4444'],
        borderWidth: 0
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false
    }
  });

  // Logs table
  const tbody = document.getElementById("logs-table-body");
  if (data.recent_logs && data.recent_logs.length > 0) {
    tbody.innerHTML = "";
    data.recent_logs.forEach(log => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${log.call_id}</td>
        <td>${log.caller_number}</td>
        <td>${log.duration}s</td>
        <td><span class="badge bg-primary">${log.intent_detected || 'Unknown'}</span></td>
        <td><small class="text-info">${log.entities || 'None'}</small></td>
        <td><span class="badge bg-${log.sentiment === 'Positive' ? 'success' : log.sentiment === 'Negative' ? 'danger' : 'secondary'}">${log.sentiment}</span></td>
      `;
      tbody.appendChild(tr);
    });
  }
}
