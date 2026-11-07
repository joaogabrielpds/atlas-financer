
(() => {
  const $ = selector => document.querySelector(selector);

  const TICKERS = [
    { ticker: "PETR4", name: "Petrobras", market: "B3", metric: "metric-ibov" },
    { ticker: "VALE3", name: "Vale", market: "B3", metric: "metric-spx" },
    { ticker: "ITUB4", name: "Itaú Unibanco", market: "B3", metric: "metric-usd" },
    { ticker: "IVVB11", name: "iShares S&P 500 ETF", market: "B3" },
    { ticker: "AAPL", name: "Apple", market: "NASDAQ" },
    { ticker: "MSFT", name: "Microsoft", market: "NASDAQ" },
    { ticker: "BTC-USD", name: "Bitcoin", market: "CRYPTO", metric: "metric-btc" }
  ];

  let latestQuotes = [];
  let histories = {};
  let technicalHistories = {};
  let selectedTicker = "PETR4";
  const toast = message => {
    const node = $("#toast");
    if (!node) return;

    node.textContent = message;
    node.classList.add("show");
    window.setTimeout(() => node.classList.remove("show"), 2600);
  };

  function formatPrice(value, currency = "BRL") {
    return new Intl.NumberFormat("pt-BR", {
      style: "currency",
      currency,
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(Number(value));
  }

  function formatVolume(value) {
    return new Intl.NumberFormat("pt-BR", {
      notation: "compact",
      maximumFractionDigits: 1
    }).format(Number(value || 0));
  }

  function formatDate(value) {
    return new Intl.DateTimeFormat("pt-BR", {
      timeZone: "America/Sao_Paulo",
      day: "2-digit",
      month: "2-digit",
      year: "numeric"
    }).format(new Date(value));
  }

  function getVariation(current, previous) {
    if (previous === null || previous === undefined || Number(previous) === 0) {
      return null;
    }

    return ((Number(current) - Number(previous)) / Number(previous)) * 100;
  }

  function formatVariation(value) {
    if (value === null) return "—";

    const signal = value > 0 ? "+" : "";
    return `${signal}${value.toFixed(2)}%`;
  }

  function getVariationClass(value) {
    if (value === null || value === 0) return "market-neutral";
    return value > 0 ? "market-positive" : "market-negative";
  }

  function getOrderedHistory(ticker) {
    return [...(histories[ticker] || [])].sort(
      (a, b) => new Date(a.timestamp) - new Date(b.timestamp)
    );
  }

  function getPreviousClose(ticker) {
    const rows = getOrderedHistory(ticker);

    if (rows.length < 2) return null;

    return Number(rows[rows.length - 2].close);
  }

  function updateClock() {
    $("#clock").textContent = new Intl.DateTimeFormat("pt-BR", {
      timeZone: "America/Sao_Paulo",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit"
    }).format(new Date());
  }

  async function checkBackend() {
    const dot = $("#api-dot");
    const label = $("#api-status");
    const badge = $("#backend-badge");
    const detail = $("#backend-detail");

    try {
      await window.AtlasAPI.getHealth();

      dot.style.background = "var(--green)";
      label.textContent = "API CONECTADA";
      label.parentElement.classList.add("connected");

      badge.textContent = "CONECTADO";
      badge.className = "integration-status";
      detail.textContent = "Backend Django respondeu ao health check";

      return true;
    } catch (error) {
      dot.style.background = "var(--amber)";
      label.textContent = "API INDISPONÍVEL";
      label.parentElement.classList.remove("connected");

      badge.textContent = "INDISPONÍVEL";
      badge.className = "integration-status pending";
      detail.textContent = error.message;

      console.error("Falha na conexão com a API:", error);
      return false;
    }
  }

  function updateMetricCards() {
    TICKERS.filter(asset => asset.metric).forEach(asset => {
      const quote = latestQuotes.find(
        item => item.ticker === asset.ticker
      );

      const valueNode = $(`#${asset.metric}`);
      const changeNode = $(`#${asset.metric}-change`);

      if (!valueNode || !changeNode || !quote) return;

      const card = valueNode.closest(".metric-card");
      const title = card?.querySelector(".metric-top span:first-child");

      if (title) title.textContent = `${asset.ticker} · ${asset.name}`;

      valueNode.textContent = formatPrice(quote.close, quote.currency);

      const previous = getPreviousClose(asset.ticker);
      const variation = getVariation(quote.close, previous);

      changeNode.textContent = variation === null
        ? "Variação indisponível"
        : `${formatVariation(variation)} em relação ao pregão anterior`;

      changeNode.className = `metric-foot ${getVariationClass(variation)}`;
    });
  }

  function renderMarketWatch() {
    const body = $("#market-watch-body");
    if (!body) return;

    const rows = TICKERS.map(asset => {
      const quote = latestQuotes.find(
        item => item.ticker === asset.ticker
      );

      if (!quote) return null;

      const previous = getPreviousClose(asset.ticker);
      const variation = getVariation(quote.close, previous);

      return { asset, quote, variation };
    }).filter(Boolean);
    const search = $("#market-search")?.value
    .trim()
    .toLowerCase() || "";

const market = $("#market-filter")?.value || "all";
const sort = $("#market-sort")?.value || "default";

let filteredRows = rows.filter(({ asset }) => {
    const matchesSearch =
        asset.ticker.toLowerCase().includes(search) ||
        asset.name.toLowerCase().includes(search);

    const matchesMarket =
        market === "all" || asset.market === market;

    return matchesSearch && matchesMarket;
});

switch (sort) {
    case "price-desc":
        filteredRows.sort((a, b) =>
            Number(b.quote.close) - Number(a.quote.close)
        );
        break;

    case "price-asc":
        filteredRows.sort((a, b) =>
            Number(a.quote.close) - Number(b.quote.close)
        );
        break;

    case "variation-desc":
        filteredRows.sort((a, b) =>
            (b.variation ?? -Infinity) -
            (a.variation ?? -Infinity)
        );
        break;

    case "variation-asc":
        filteredRows.sort((a, b) =>
            (a.variation ?? Infinity) -
            (b.variation ?? Infinity)
        );
        break;

    case "volume-desc":
        filteredRows.sort((a, b) =>
            Number(b.quote.volume || 0) -
            Number(a.quote.volume || 0)
        );
        break;
}
    if (!filteredRows.length) {
      body.innerHTML = `
    <tr>
        <td colspan="6" class="market-watch-empty">
            Nenhum ativo encontrado com esses filtros.
        </td>
    </tr>
`;

$("#market-watch-count").textContent =
    `${filteredRows.length} / ${rows.length} ATIVOS`;
return;
    }

    body.innerHTML = filteredRows.map(({ asset, quote, variation }) => `
    <tr
      class="${asset.ticker === selectedTicker ? "selected" : ""}"
      data-ticker="${asset.ticker}"
      tabindex="0"
      role="button"
      aria-selected="${asset.ticker === selectedTicker}"
      aria-label="Selecionar ${asset.name}"
    >
        <td>
          <div class="market-asset">
            <strong>${asset.ticker}</strong>
            <small>${asset.name} · ${asset.market}</small>
          </div>
        </td>
        <td>${formatPrice(quote.close, quote.currency)}</td>
        <td class="${getVariationClass(variation)}">
          ${formatVariation(variation)}
        </td>
        <td>${formatPrice(quote.high, quote.currency)}</td>
        <td>${formatPrice(quote.low, quote.currency)}</td>
        <td>${formatVolume(quote.volume)}</td>
      </tr>
    `).join("");

    $("#market-watch-count").textContent = `${rows.length} ATIVOS`;

    const newestDate = rows
      .map(row => new Date(row.quote.timestamp))
      .sort((a, b) => b - a)[0];

    $("#market-watch-updated").textContent =
      `Últimos registros de negociação: ${formatDate(newestDate)} · Fonte: yfinance`;
  }

  function getFilteredHistory() {
    const rows = getOrderedHistory(selectedTicker);
    const period = $("#period-select")?.value || "1M";

    const days = {
        "1D": 1,
        "1M": 30,
        "6M": 180,
        "1Y": 365
    }[period] || 365;

    if (!rows.length) return [];

    if (period === "1D") return rows.slice(-1);

    const end = new Date(rows[rows.length - 1].timestamp);
    const start = new Date(end);
    start.setDate(start.getDate() - days);

    return rows.filter(row => new Date(row.timestamp) >= start);
}

async function loadTechnicalHistory(ticker) {
  if (Object.prototype.hasOwnProperty.call(technicalHistories, ticker)) {
    return;
  }

  try {
    const response = await window.AtlasAPI.getTechnicalIndicators(ticker);

    technicalHistories[ticker] = response.data || [];

    if (ticker !== selectedTicker) return;

    const rows = getFilteredHistory();

    window.AtlasCharts.renderPerformanceChart(
      "performance-chart",
      rows,
      technicalHistories[ticker]
    );

    console.log(`Indicadores técnicos carregados: ${ticker}`);
  } catch (error) {
    technicalHistories[ticker] = [];
    console.error(`Erro ao carregar indicadores de ${ticker}:`, error);
  }
}

  function renderCharts() {
    const rows = getFilteredHistory();
    const fullHistory = getOrderedHistory(selectedTicker);

$("#rsi-title").textContent = `RSI — ${selectedTicker}`;

window.AtlasCharts.renderRSI(
  "rsi-chart",
  fullHistory,
  14
);
$("#macd-title").textContent = `MACD — ${selectedTicker}`;

window.AtlasCharts.renderMACD(
  "macd-chart",
  fullHistory
);
    const asset = TICKERS.find(
    item => item.ticker === selectedTicker
);

const assetName = asset
    ? `${asset.ticker} · ${asset.name}`
    : selectedTicker;

$("#performance-title").textContent =
    `Desempenho histórico — ${assetName}`;

$("#candlestick-title").textContent =
    `Gráfico de candles — ${assetName}`;

    if (!rows.length) {
      window.AtlasCharts.showEmpty(
        "performance-chart",
        "Sem dados históricos",
        "Não foram encontrados registros para PETR4."
      );

      window.AtlasCharts.showEmpty(
        "candlestick-chart",
        "Sem candles disponíveis",
        "Não existem registros para o período selecionado."
      );
      return;
    }

   window.AtlasCharts.renderPerformanceChart(
  "performance-chart",
  rows,
  technicalHistories[selectedTicker] || []
);

loadTechnicalHistory(selectedTicker);

    const candles = rows.map(row => ({
      time: row.timestamp.slice(0, 10),
      open: Number(row.open),
      high: Number(row.high),
      low: Number(row.low),
      close: Number(row.close),
      volume: Number(row.volume || 0)
}));

    window.AtlasCharts.renderCandles(
      "candlestick-chart",
      candles
    );
  }
  function selectAsset(ticker) {
    const asset = TICKERS.find(item => item.ticker === ticker);

    if (!asset || !histories[ticker]) {
        return;
    }

    selectedTicker = ticker;

    renderMarketWatch();
    renderCharts();

    toast(`${asset.ticker} selecionado.`);
}

function setupMarketWatchSelection() {
    const body = $("#market-watch-body");

    if (!body) return;

    body.addEventListener("click", event => {
        const row = event.target.closest("tr[data-ticker]");

        if (!row) return;

        selectAsset(row.dataset.ticker);
    });

    body.addEventListener("keydown", event => {
        if (event.key !== "Enter" && event.key !== " ") {
            return;
        }

        const row = event.target.closest("tr[data-ticker]");

        if (!row) return;

        event.preventDefault();
        selectAsset(row.dataset.ticker);
    });

} function setupMarketWatchFilters() {
    const search = $("#market-search");
    const market = $("#market-filter");
    const sort = $("#market-sort");

    search?.addEventListener("input", renderMarketWatch);
    market?.addEventListener("change", renderMarketWatch);
    sort?.addEventListener("change", renderMarketWatch);
}

  function renderEconomicIndicators(data) {
    const indicators = Array.isArray(data)
        ? data
        : (data.results || []);

    const latestByCode = {};

    indicators.forEach(item => {
        const current = latestByCode[item.code];

        if (
            !current ||
            new Date(item.reference_date) >
            new Date(current.reference_date)
        ) {
            latestByCode[item.code] = item;
        }
    });

    const selic = latestByCode["432"];
    const ipca = latestByCode["433"];

    const selicNode = $("#indicator-selic");
    const ipcaNode = $("#indicator-ipca");

    if (selicNode) {
        selicNode.textContent = selic
            ? `${Number(selic.value).toLocaleString("pt-BR", {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            })}% a.a.`
            : "Indisponível";
    }

    if (ipcaNode) {
        ipcaNode.textContent = ipca
            ? `${Number(ipca.value).toLocaleString("pt-BR", {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            })}% a.m.`
            : "Indisponível";
    }

    const dates = [selic, ipca]
        .filter(Boolean)
        .map(item => item.reference_date)
        .sort((a, b) => new Date(b) - new Date(a));

    const updatedNode = $("#economic-updated");

    if (updatedNode) {
        updatedNode.textContent = dates.length
            ? `Últimas referências: ${dates.join(" · ")} | Fonte: Banco Central`
            : "Nenhum indicador econômico disponível.";
    }
}

  async function loadDashboard() {
    const connected = await checkBackend();
    if (!connected) return;

    try {
      const latest = await window.AtlasAPI.getLatestQuotes();

      latestQuotes = latest;

      const results = await Promise.all(
        TICKERS.map(async asset => {
          const data = await window.AtlasAPI.getQuotes(
            `?ticker=${encodeURIComponent(asset.ticker)}`
          );

          return [asset.ticker, data];
        })
      );

      histories = Object.fromEntries(results);

updateMetricCards();
renderMarketWatch();
renderCharts();

try {
    const indicators = await window.AtlasAPI.getIndicators();
    renderEconomicIndicators(indicators);
} catch (error) {
    console.error("Erro ao carregar indicadores econômicos:", error);

    $("#economic-updated").textContent =
        "Não foi possível carregar os indicadores econômicos.";
}

      const marketStatus = $("#market-status");

if (marketStatus) {
  marketStatus.textContent = "CONECTADO";
  marketStatus.className = "integration-status";
}

      toast("Dados dos sete ativos atualizados.");
    } catch (error) {
      console.error("Erro ao carregar dados:", error);
      toast(`Erro ao carregar dados: ${error.message}`);
    }
  }

  function setupNavigation() {
    document.querySelectorAll(".nav-item").forEach(link => {
      link.addEventListener("click", event => {
        event.preventDefault();

        document.querySelectorAll(".nav-item").forEach(item =>
          item.classList.remove("active")
        );

        link.classList.add("active");

        const label = link.textContent.trim();
        $("#breadcrumb").textContent = label.toUpperCase();

        if (link.dataset.page !== "overview") {
          toast(`${label}: módulo previsto para uma próxima etapa.`);
        }

        $("#sidebar").classList.remove("open");
      });
    });
  }

  function setupControls() {
    $("#refresh-button").addEventListener("click", loadDashboard);

    $("#menu-toggle").addEventListener("click", () =>
      $("#sidebar").classList.toggle("open")
    );

    $("#period-select").addEventListener("change", renderCharts);
  }

  document.addEventListener("DOMContentLoaded", () => {
    updateClock();
    window.setInterval(updateClock, 1000);

    setupNavigation();
    setupControls();
    setupMarketWatchSelection();
    setupMarketWatchFilters();
    loadDashboard();
  });
})();
