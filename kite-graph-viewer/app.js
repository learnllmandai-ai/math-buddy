const labels = ["128 LOC", "256 LOC", "384 LOC", "512 LOC", "640 LOC", "768 LOC", "896 LOC", "1024 LOC"];
  
const languageConfig = [
  { key: "python", label: "Python", role: "Primary", color: "#3aa8ff", width: 3.6, tension: 0.42, faded: false, hidden: false },
  { key: "javascript", label: "JavaScript", role: "Primary", color: "#ffd84d", width: 3.2, tension: 0.38, faded: false, hidden: false },
  { key: "java", label: "Java", role: "Background", color: "rgba(119, 143, 176, 0.42)", width: 1.5, tension: 0.36, faded: true, hidden: false },
  { key: "go", label: "Go", role: "Background", color: "rgba(92, 160, 195, 0.34)", width: 1.5, tension: 0.34, faded: true, hidden: false },
  { key: "php", label: "PHP", role: "Background", color: "rgba(164, 142, 214, 0.28)", width: 1.4, tension: 0.34, faded: true, hidden: false },
  { key: "cpp", label: "C++", role: "Background", color: "rgba(94, 196, 179, 0.3)", width: 1.5, tension: 0.35, faded: true, hidden: false },
  { key: "ruby", label: "Ruby", role: "Background", color: "rgba(208, 104, 104, 0.28)", width: 1.4, tension: 0.34, faded: true, hidden: false },
  { key: "bash", label: "Bash", role: "Background", color: "rgba(189, 206, 111, 0.28)", width: 1.4, tension: 0.33, faded: true, hidden: false }
];

const baseTelemetry = {
  python: [98, 105, 111, 116, 123, 127, 133, 140],
  javascript: [103, 110, 116, 121, 127, 132, 138, 146],
  java: [112, 118, 123, 129, 136, 142, 149, 156],
  go: [107, 114, 118, 125, 131, 139, 144, 151],
  php: [117, 125, 132, 137, 143, 149, 155, 164],
  cpp: [109, 115, 121, 126, 132, 140, 147, 153],
  ruby: [121, 129, 136, 143, 149, 156, 163, 171],
  bash: [101, 106, 112, 117, 124, 130, 135, 142]
};

const codeSample = [
  "const inferenceWindow = metrics.slice(-8);",
  "const tokenSlope = language.latency / Math.max(language.probability, 0.12);",
  "",
  "// Smooth telemetry for active code paths",
  "function streamInference(language, loc) {",
  "  const baseline = profile[language].latency;",
  "  const complexityBias = Math.log2(loc + 1) * 4.8;",
  "  const probability = Math.max(0.14, 0.91 - loc / 1800);",
  "  return {",
  "    speedMs: Math.round(baseline + complexityBias + jitter()),",
  "    tokensPerSecond: Math.round(1000 / (baseline / 18)),",
  "    probability",
  "  };",
  "}",
  "",
  "async function fetchLLMTelemetry(model) {",
  "  const response = await simulatePull(model);",
  "  return response.languages.filter((entry) => entry.visible);",
  "}",
  "",
  "requestAnimationFrame(renderMiniMap);",
  "setInterval(updateDashboard, 2000);"
];

const state = {
  profiles: structuredClone(baseTelemetry),
  modelIndex: 0,
  feed: [],
  isFetching: false
};

const modelSources = ["Codex Stream", "Gemini Stream"];

const languageList = document.getElementById("languageList");
const peakTps = document.getElementById("peakTps");
const visibleCount = document.getElementById("visibleCount");
const activeModel = document.getElementById("activeModel");
const modelSource = document.getElementById("modelSource");
const nextPull = document.getElementById("nextPull");
const snapshotInfo = document.getElementById("snapshotInfo");
const feedList = document.getElementById("feedList");
const feedTime = document.getElementById("feedTime");
const codeBlock = document.getElementById("codeBlock");
const miniMap = document.getElementById("miniMap");
const streamStatus = document.getElementById("streamStatus");
const chartCanvas = document.getElementById("analyticsChart");

function buildCodeBlock() {
  codeBlock.innerHTML = codeSample
    .map((line, index) => {
      const html = line
        .replace(/\b(const|function|return|async|await)\b/g, '<span class="kw">$1</span>')
        .replace(/\b(streamInference|fetchLLMTelemetry|simulatePull|updateDashboard|renderMiniMap)\b/g, '<span class="fn">$1</span>')
        .replace(/\b(\d+(?:\.\d+)?)\b/g, '<span class="num">$1</span>')
        .replace(/(\/\/.*)/g, '<span class="cm">$1</span>');
      return `<span class="line-no">${String(index + 1).padStart(2, "0")}</span>${html}`;
    })
    .join("\n");
}

function buildMiniMap() {
  const maxLength = Math.max(...codeSample.map((line) => line.length), 1);
  const linesMarkup = codeSample
    .map((line) => {
      const width = Math.max(14, (line.length / maxLength) * 100);
      return `<div class="minimap-line" style="width:${width}%"></div>`;
    })
    .join("");

  miniMap.innerHTML = `${linesMarkup}<div class="minimap-window" id="miniMapWindow"></div>`;
  syncMiniMapWindow();
}

function syncMiniMapWindow() {
  const windowEl = document.getElementById("miniMapWindow");
  if (!windowEl) {
    return;
  }

  const totalLines = codeSample.length;
  const visibleLines = Math.min(9, totalLines);
  const lineHeight = 7;
  const top = ((Date.now() / 120) % (totalLines - visibleLines + 1 || 1)) * lineHeight;
  windowEl.style.top = `${top}px`;
  windowEl.style.height = `${visibleLines * lineHeight}px`;
}

function datasetFromLanguage(language) {
  const isPrimary = !language.faded;
  const color = language.color;
  return {
    label: language.label,
    data: state.profiles[language.key],
    borderColor: color,
    backgroundColor: color,
    borderWidth: language.width,
    pointRadius: isPrimary ? 2.5 : 0,
    pointHoverRadius: isPrimary ? 5 : 2,
    pointBackgroundColor: isPrimary ? color : "rgba(255,255,255,0.35)",
    borderCapStyle: "round",
    borderJoinStyle: "round",
    cubicInterpolationMode: "monotone",
    tension: language.tension,
    fill: false,
    hidden: language.hidden,
    borderDash: language.faded ? [6, 6] : [],
    spanGaps: true
  };
}

function initializeChart() {
  if (!window.Chart) {
    const fallback = document.createElement("div");
    fallback.className = "chart-fallback";
    fallback.textContent = "Chart.js could not be loaded from the CDN. Reconnect or bundle Chart.js locally to render the graph.";
    chartCanvas.replaceWith(fallback);
    streamStatus.textContent = "Chart unavailable";
    return null;
  }

  return new Chart(chartCanvas, {
    type: "line",
    data: {
      labels,
      datasets: languageConfig.map(datasetFromLanguage)
    },
    options: {
      animation: {
        duration: 650,
        easing: "easeOutQuart"
      },
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: "index",
        intersect: false
      },
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          backgroundColor: "rgba(9, 13, 18, 0.95)",
          borderColor: "rgba(255,255,255,0.08)",
          borderWidth: 1,
          titleColor: "#edf3ff",
          bodyColor: "#d3dbe8",
          padding: 14,
          displayColors: true,
          callbacks: {
            label(context) {
              const probability = deriveProbability(context.raw, context.dataIndex);
              const tps = deriveTokensPerSecond(context.raw, probability);
              return `${context.dataset.label}: ${context.raw} ms | ${tps} Tokens / Sec | P=${probability.toFixed(2)}`;
            }
          }
        }
      },
      scales: {
        x: {
          ticks: {
            color: "rgba(237, 243, 255, 0.72)",
            maxRotation: 0
          },
          title: {
            display: true,
            text: "Time / Complexity (Lines of Code)",
            color: "rgba(237, 243, 255, 0.9)"
          },
          grid: {
            color: "rgba(125, 139, 157, 0.08)"
          },
          border: {
            color: "rgba(125, 139, 157, 0.12)"
          }
        },
        y: {
          ticks: {
            color: "rgba(237, 243, 255, 0.72)"
          },
          title: {
            display: true,
            text: "Inference Speed (ms) / Token Probability",
            color: "rgba(237, 243, 255, 0.9)"
          },
          grid: {
            color: "rgba(125, 139, 157, 0.08)"
          },
          border: {
            color: "rgba(125, 139, 157, 0.12)"
          }
        }
      }
    }
  });
}

const chart = initializeChart();

function renderLanguageToggles() {
  languageList.innerHTML = "";

  languageConfig.forEach((language) => {
    const item = document.createElement("label");
    item.className = "language-item";
    item.innerHTML = `
      <div class="language-info">
        <span class="language-chip" style="color:${language.color}; background:${language.color}"></span>
        <div class="language-labels">
          <span class="language-name">${language.label}</span>
          <span class="language-role">${language.role}</span>
        </div>
      </div>
      <span class="toggle">
        <input type="checkbox" ${language.hidden ? "" : "checked"} data-language="${language.key}" />
        <span class="toggle-slider"></span>
      </span>
    `;
    languageList.appendChild(item);
  });

  languageList.querySelectorAll("input[type='checkbox']").forEach((checkbox) => {
    checkbox.addEventListener("change", (event) => {
      const key = event.target.dataset.language;
      const language = languageConfig.find((entry) => entry.key === key);
      language.hidden = !event.target.checked;
      if (chart) {
        const dataset = chart.data.datasets.find((entry) => entry.label === language.label);
        dataset.hidden = language.hidden;
        chart.update();
      }
      updateMetrics();
      streamStatus.textContent = `${language.label} ${language.hidden ? "muted" : "restored"} | Live every 2s`;
    });
  });
}

function deriveProbability(latency, index) {
  const base = 1 - latency / 240;
  const complexityFactor = 1 - index * 0.025;
  return Math.max(0.11, Math.min(0.98, base * complexityFactor + 0.14));
}

function deriveTokensPerSecond(latency, probability) {
  return Math.max(8, Math.round((1000 / latency) * (10 + probability * 16)));
}

function simulateTelemetryPull() {
  return new Promise((resolve) => {
    const networkLag = 240 + Math.round(Math.random() * 260);
    setTimeout(() => {
      const languages = languageConfig.map((language, datasetIndex) => {
        const previous = state.profiles[language.key];
        const nextSeries = previous.map((value, pointIndex) => {
          const wave = Math.sin(Date.now() / 1800 + pointIndex * 0.75 + datasetIndex) * 4.5;
          const jitter = (Math.random() - 0.5) * (language.faded ? 5 : 8);
          const target = baseTelemetry[language.key][pointIndex] + wave + jitter;
          return Math.max(72, Math.round(value * 0.32 + target * 0.68));
        });

        return {
          ...language,
          latencySeries: nextSeries,
          latest: nextSeries[nextSeries.length - 1],
          probability: deriveProbability(nextSeries[nextSeries.length - 1], nextSeries.length - 1),
          visible: !language.hidden
        };
      });

      resolve({
        fetchedAt: new Date(),
        source: modelSources[state.modelIndex],
        modelName: state.modelIndex === 0 ? "Codex" : "Gemini",
        lag: networkLag,
        languages
      });
    }, networkLag);
  });
}

function updateFeed(snapshot) {
  const visibleEntries = snapshot.languages.filter((entry) => entry.visible).slice(0, 4);
  const latestItems = visibleEntries.map((entry) => {
    const tps = deriveTokensPerSecond(entry.latest, entry.probability);
    return {
      title: `${entry.label} steady at ${entry.latest} ms`,
      body: `${tps} Tokens / Sec at ${entry.probability.toFixed(2)} token probability. Complexity ceiling ${labels.at(-1)}.`
    };
  });

  state.feed = [...latestItems, ...state.feed].slice(0, 4);
  feedList.innerHTML = state.feed
    .map((item) => `<article class="feed-item"><strong>${item.title}</strong><span>${item.body}</span></article>`)
    .join("");
  feedTime.textContent = `Last fetch ${snapshot.fetchedAt.toLocaleTimeString()}`;
}

function updateMetrics(snapshot) {
  const datasets = chart
    ? chart.data.datasets.filter((dataset) => !dataset.hidden)
    : languageConfig.filter((language) => !language.hidden).map((language) => ({
        data: state.profiles[language.key]
      }));
  const allValues = datasets.flatMap((dataset) => dataset.data);
  const peak = allValues.reduce((best, value, index) => {
    const probability = deriveProbability(value, index % labels.length);
    return Math.max(best, deriveTokensPerSecond(value, probability));
  }, 0);

  peakTps.textContent = String(peak);
  visibleCount.textContent = String(datasets.length);

  if (snapshot) {
    activeModel.textContent = snapshot.modelName;
    modelSource.textContent = snapshot.source;
    snapshotInfo.textContent = `${snapshot.languages.length} langs | ${snapshot.lag}ms simulated latency`;
  }
}

async function updateDashboard() {
  if (state.isFetching) {
    return;
  }

  state.isFetching = true;
  nextPull.textContent = "pulling…";
  try {
    const snapshot = await simulateTelemetryPull();
    state.modelIndex = (state.modelIndex + 1) % modelSources.length;

    snapshot.languages.forEach((language) => {
      state.profiles[language.key] = language.latencySeries;
      if (chart) {
        const dataset = chart.data.datasets.find((entry) => entry.label === language.label);
        dataset.data = language.latencySeries;
        dataset.hidden = language.hidden;
      }
    });

    if (chart) {
      chart.update();
    }
    updateFeed(snapshot);
    updateMetrics(snapshot);
    syncMiniMapWindow();

    const nextIn = 2;
    nextPull.textContent = `${nextIn.toFixed(1)}s`;
    streamStatus.textContent = `${snapshot.modelName} synced at ${snapshot.fetchedAt.toLocaleTimeString()}`;
  } catch (error) {
    nextPull.textContent = "retrying";
    streamStatus.textContent = "Telemetry fetch failed";
    snapshotInfo.textContent = error instanceof Error ? error.message : "Unknown fetch error";
  } finally {
    state.isFetching = false;
  }
}

function startPullCountdown() {
  let remaining = 2;
  setInterval(() => {
    remaining -= 0.1;
    if (remaining <= 0) {
      remaining = 2;
    }
    nextPull.textContent = `${remaining.toFixed(1)}s`;
  }, 100);
}

function startMiniMapAnimation() {
  setInterval(syncMiniMapWindow, 180);
}

buildCodeBlock();
buildMiniMap();
renderLanguageToggles();
updateMetrics();
updateFeed({
  fetchedAt: new Date(),
  languages: languageConfig.map((language) => ({
    ...language,
    latest: baseTelemetry[language.key][baseTelemetry[language.key].length - 1],
    probability: deriveProbability(baseTelemetry[language.key][baseTelemetry[language.key].length - 1], labels.length - 1),
    visible: !language.hidden
  }))
});
updateDashboard();
setInterval(updateDashboard, 2000);
startPullCountdown();
startMiniMapAnimation();
