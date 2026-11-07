(() => {
  function calculateRSI(rows, period = 14) {
  const ordered = [...rows].sort(
    (a, b) => new Date(a.timestamp) - new Date(b.timestamp)
  );

  const closes = ordered.map(row => Number(row.close));
  const result = [];

  if (closes.length <= period) return result;

  let gains = 0;
  let losses = 0;

  for (let i = 1; i <= period; i++) {
    const change = closes[i] - closes[i - 1];
    gains += Math.max(change, 0);
    losses += Math.max(-change, 0);
  }

  let averageGain = gains / period;
  let averageLoss = losses / period;

  function getValue() {
    if (averageLoss === 0) {
      return averageGain === 0 ? 50 : 100;
    }

    const rs = averageGain / averageLoss;
    return 100 - (100 / (1 + rs));
  }

  result.push({
    time: ordered[period].timestamp.slice(0, 10),
    value: getValue()
  });

  for (let i = period + 1; i < closes.length; i++) {
    const change = closes[i] - closes[i - 1];

    const gain = Math.max(change, 0);
    const loss = Math.max(-change, 0);

    averageGain = ((averageGain * (period - 1)) + gain) / period;
    averageLoss = ((averageLoss * (period - 1)) + loss) / period;

    result.push({
      time: ordered[i].timestamp.slice(0, 10),
      value: getValue()
    });
  }

  return result;
}
function calculateEMA(values, period) {
  if (!values.length) return [];

  const multiplier = 2 / (period + 1);
  const result = [];

  let ema = values[0];
  result.push(ema);

  for (let i = 1; i < values.length; i++) {
    ema = (values[i] * multiplier) + (ema * (1 - multiplier));
    result.push(ema);
  }

  return result;
}

function calculateMACD(rows, fast = 12, slow = 26, signalPeriod = 9) {
  const ordered = [...rows].sort(
    (a, b) => new Date(a.timestamp) - new Date(b.timestamp)
  );

  const closes = ordered.map(row => Number(row.close));

  if (closes.length < slow + signalPeriod) return [];

  const fastEMA = calculateEMA(closes, fast);
  const slowEMA = calculateEMA(closes, slow);

  const macdValues = closes.map(
    (_, index) => fastEMA[index] - slowEMA[index]
  );

  const signalValues = calculateEMA(macdValues, signalPeriod);

  return ordered.map((row, index) => ({
    time: row.timestamp.slice(0, 10),
    macd: macdValues[index],
    signal: signalValues[index],
    histogram: macdValues[index] - signalValues[index]
  })).slice(slow - 1);
}
function renderRSI(containerId, rows, period = 14) {
  const node = document.getElementById(containerId);
  const valueNode = document.getElementById("rsi-value");
  const statusNode = document.getElementById("rsi-status");

  if (!node || !window.Plotly) return false;

  const data = calculateRSI(rows, period);

  if (!data.length) {
    showEmpty(containerId, "Dados insuficientes", "O RSI precisa de pelo menos 15 fechamentos.");
    if (valueNode) valueNode.textContent = "—";
    if (statusNode) statusNode.textContent = "Aguardando histórico";
    return false;
  }

  const latest = data[data.length - 1].value;

  let status = "Neutro";
  if (latest >= 70) status = "Sobrecomprado";
  else if (latest <= 30) status = "Sobrevendido";

  if (valueNode) {
    valueNode.textContent = latest.toFixed(2).replace(".", ",");
  }

  if (statusNode) {
    statusNode.textContent = status;
    statusNode.style.color = latest >= 70
      ? "#e17878"
      : latest <= 30
        ? "#55c59a"
        : "#91a0b2";
  }

  window.Plotly.newPlot(node, [
    {
      x: data.map(item => item.time),
      y: data.map(item => item.value),
      type: "scatter",
      mode: "lines",
      line: { color: "#55c6d9", width: 2 },
      hovertemplate: "%{x}<br>RSI: %{y:.2f}<extra></extra>"
    }
  ], {
    paper_bgcolor: "transparent",
    plot_bgcolor: "transparent",
    margin: { l: 42, r: 15, t: 8, b: 25 },
    font: { color: "#91a0b2", family: "DM Mono", size: 10 },
    xaxis: { gridcolor: "#1d2a39", zeroline: false },
    yaxis: {
      range: [0, 100],
      gridcolor: "#1d2a39",
      zeroline: false,
      tickvals: [0, 30, 50, 70, 100]
    },
    shapes: [
      {
        type: "line",
        xref: "paper",
        x0: 0, x1: 1,
        y0: 70, y1: 70,
        line: { color: "#e17878", dash: "dash", width: 1 }
      },
      {
        type: "line",
        xref: "paper",
        x0: 0, x1: 1,
        y0: 30, y1: 30,
        line: { color: "#55c59a", dash: "dash", width: 1 }
      },
      {
        type: "line",
        xref: "paper",
        x0: 0, x1: 1,
        y0: 50, y1: 50,
        line: { color: "#718096", dash: "dot", width: 1 }
      }
    ],
    showlegend: false
  }, {
    responsive: true,
    displayModeBar: false
  });

  return true;
}
  const chartInstances = new Map();
  const resizeObservers = new Map();
  function renderMACD(containerId, rows) {
  const node = document.getElementById(containerId);
  const valueNode = document.getElementById("macd-value");
  const statusNode = document.getElementById("macd-status");

  if (!node || !window.Plotly) return false;

  const data = calculateMACD(rows, 12, 26, 9);

  if (!data.length) {
    showEmpty(
      containerId,
      "Dados insuficientes",
      "O MACD precisa de pelo menos 34 fechamentos."
    );

    if (valueNode) valueNode.textContent = "—";
    if (statusNode) statusNode.textContent = "Aguardando histórico";

    return false;
  }

  const latest = data[data.length - 1];

  const bullish = latest.macd >= latest.signal;

  if (valueNode) {
    valueNode.textContent = latest.macd.toFixed(3).replace(".", ",");
  }

  if (statusNode) {
    statusNode.textContent = bullish
      ? "MACD acima do sinal"
      : "MACD abaixo do sinal";

    statusNode.style.color = bullish
      ? "#55c59a"
      : "#e17878";
  }

  const dates = data.map(item => item.time);

  window.Plotly.newPlot(node, [
    {
      x: dates,
      y: data.map(item => item.histogram),
      type: "bar",
      name: "Histograma",
      marker: {
        color: data.map(item =>
          item.histogram >= 0 ? "#55c59a" : "#e17878"
        )
      },
      hovertemplate: "%{x}<br>Histograma: %{y:.4f}<extra></extra>"
    },
    {
      x: dates,
      y: data.map(item => item.macd),
      type: "scatter",
      mode: "lines",
      name: "MACD",
      line: { color: "#55c6d9", width: 2 }
    },
    {
      x: dates,
      y: data.map(item => item.signal),
      type: "scatter",
      mode: "lines",
      name: "Sinal",
      line: { color: "#e6b65c", width: 1.5 }
    }
  ], {
    paper_bgcolor: "transparent",
    plot_bgcolor: "transparent",
    margin: { l: 48, r: 15, t: 12, b: 28 },
    font: {
      color: "#91a0b2",
      family: "DM Mono",
      size: 10
    },
    xaxis: {
      gridcolor: "#1d2a39",
      zeroline: false
    },
    yaxis: {
      gridcolor: "#1d2a39",
      zeroline: true,
      zerolinecolor: "#718096"
    },
    legend: {
      orientation: "h",
      y: 1.15
    },
    showlegend: true
  }, {
    responsive: true,
    displayModeBar: false
  });

  return true;
}
  function showEmpty(containerId, title, detail) {
    const node = document.getElementById(containerId);
    if (!node) return;

    node.innerHTML = `
      <div class="empty-state">
        <span class="empty-symbol">⌁</span>
        <strong>${title}</strong>
        <small>${detail}</small>
      </div>
    `;
  }

  
function renderPerformanceChart(containerId, rows, technicalRows = []) {
  const node = document.getElementById(containerId);
node.classList.remove("chart-empty");
node.innerHTML = "";
  if (!node || !Array.isArray(rows) || !rows.length || !window.Plotly) {
    return false;
  }

  const traces = [
    {
      x: rows.map(row => row.timestamp),
      y: rows.map(row => Number(row.close)),
      type: "scatter",
      mode: "lines",
      name: "Fechamento",
      line: { color: "#55c6d9", width: 2 },
      fill: "tozeroy",
      fillcolor: "rgba(85,198,217,.07)",
      hovertemplate: "%{x}<br>Fechamento: %{y:,.2f}<extra></extra>"
    }
  ];

  const averages = [
    { key: "sma_20", name: "SMA 20", color: "#e6b65c" },
    { key: "sma_50", name: "SMA 50", color: "#b58be8" },
    { key: "sma_200", name: "SMA 200", color: "#55c59a" }
  ];

  const technicalByDate = new Map(
    technicalRows.map(item => [
      item.timestamp.slice(0, 10),
      item
    ])
  );

  averages.forEach(indicator => {
    const values = rows.map(row => {
      const technical = technicalByDate.get(
        row.timestamp.slice(0, 10)
      );

      return technical?.[indicator.key] != null
        ? Number(technical[indicator.key])
        : null;
    });

    if (values.some(value => value !== null)) {
      traces.push({
        x: rows.map(row => row.timestamp),
        y: values,
        type: "scatter",
        mode: "lines",
        name: indicator.name,
        connectgaps: false,
        line: { color: indicator.color, width: 1.5 }
      });
    }
  });

  window.Plotly.newPlot(node, traces, {
    paper_bgcolor: "transparent",
    plot_bgcolor: "transparent",
    margin: { l: 48, r: 12, t: 25, b: 28 },
    font: { color: "#91a0b2", family: "DM Mono", size: 10 },
    xaxis: { gridcolor: "#1d2a39", zeroline: false },
    yaxis: {
      gridcolor: "#1d2a39",
      zeroline: false,
      tickformat: ",.2f"
    },
    legend: { orientation: "h", y: 1.15 },
    showlegend: true,
    autosize: true
  }, {
    responsive: true,
    displayModeBar: false
  });

  return true;
}

  function renderCandles(containerId, candles) {
    const node = document.getElementById(containerId);

    if (
      !node ||
      !Array.isArray(candles) ||
      !candles.length ||
      !window.LightweightCharts
    ) {
      return false;
    }

    // Remove o gráfico anterior antes de criar outro.
    if (chartInstances.has(containerId)) {
      chartInstances.get(containerId).remove();
      chartInstances.delete(containerId);
    }

    if (resizeObservers.has(containerId)) {
      resizeObservers.get(containerId).disconnect();
      resizeObservers.delete(containerId);
    }

    node.innerHTML = "";

    const validCandles = candles
      .filter(candle =>
        candle.time &&
        [candle.open, candle.high, candle.low, candle.close]
          .every(Number.isFinite)
      )
      .sort((a, b) => a.time.localeCompare(b.time));

    if (!validCandles.length) return false;

    const chart = window.LightweightCharts.createChart(node, {
      width: node.clientWidth,
      height: 260,

      layout: {
        background: { color: "#101a27" },
        textColor: "#91a0b2",
        fontFamily: "DM Mono, monospace",
        fontSize: 11
      },

      grid: {
        vertLines: { color: "#1d2a39" },
        horzLines: { color: "#1d2a39" }
      },

      rightPriceScale: {
        borderColor: "#28384a",
        autoScale: true,
        scaleMargins: {
          top: 0.10,
          bottom: 0.10
        }
      },

      timeScale: {
        borderColor: "#28384a",
        timeVisible: true,
        rightOffset: 4,
        barSpacing: 12,
        minBarSpacing: 4
      },

      crosshair: {
        mode: window.LightweightCharts.CrosshairMode.Normal,
        vertLine: {
          color: "#718096",
          width: 1,
          style: 2,
          labelBackgroundColor: "#243449"
        },
        horzLine: {
          color: "#718096",
          width: 1,
          style: 2,
          labelBackgroundColor: "#243449"
        }
      },

      // Navegação horizontal e zoom.
      handleScroll: {
        mouseWheel: true,
        pressedMouseMove: true,
        horzTouchDrag: true,
        vertTouchDrag: true
      },

      handleScale: {
        axisPressedMouseMove: true,
        mouseWheel: true,
        pinch: true
      }
    });

    const series = chart.addSeries(
      window.LightweightCharts.CandlestickSeries,
      {
        upColor: "#55c59a",
        downColor: "#e17878",
        borderUpColor: "#55c59a",
        borderDownColor: "#e17878",
        wickUpColor: "#55c59a",
        wickDownColor: "#e17878",
        lastValueVisible: true,
        priceLineVisible: true
      }
    );

    series.setData(validCandles);
    // Escala independente para o volume, na parte inferior.
chart.priceScale("volume").applyOptions({
  scaleMargins: {
    top: 0.82,
    bottom: 0
  },
  visible: false,
  autoScale: true
});

// Barras de volume.
const volumeSeries = chart.addSeries(
  window.LightweightCharts.HistogramSeries,
  {
    priceFormat: {
      type: "volume"
    },
    priceScaleId: "volume",
    lastValueVisible: false,
    priceLineVisible: false
  }
);

volumeSeries.setData(
  validCandles.map(candle => ({
    time: candle.time,
    value: candle.volume,
    color: candle.close >= candle.open
      ? "rgba(85,197,154,0.65)"
      : "rgba(225,120,120,0.65)"
  }))
);
    // Destaca o último preço negociado.
    const lastCandle = validCandles[validCandles.length - 1];

    series.createPriceLine({
      price: lastCandle.close,
      color: "#55c6d9",
      lineWidth: 1,
      lineStyle: 2,
      axisLabelVisible: true,
      title: "Último preço"
    });

    chart.timeScale().fitContent();

    const observer = new ResizeObserver(() => {
      if (node.clientWidth > 0) {
        chart.applyOptions({
          width: node.clientWidth
        });
      }
    });

    observer.observe(node);

    chartInstances.set(containerId, chart);
    resizeObservers.set(containerId, observer);

    return true;
  }

  window.AtlasCharts = {
  showEmpty,
  renderPerformanceChart,
  renderCandles,
  renderRSI,
  calculateRSI,
  calculateEMA,
  calculateMACD,
  renderMACD
};
})();
