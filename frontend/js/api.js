(() => {
  const config = window.ATLAS_CONFIG;

  async function request(path, options = {}) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), config.REQUEST_TIMEOUT_MS);
    try {
      const response = await fetch(`${config.API_BASE_URL}${path}`, {
        ...options,
        headers: { "Accept": "application/json", ...(options.headers || {}) },
        signal: controller.signal
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } finally {
      clearTimeout(timeout);
    }
  }

   window.AtlasAPI = {
  request,
  getHealth: () => request(config.ENDPOINTS.health),
  getMarkets: () => request(config.ENDPOINTS.markets),
  getAssets: (params = "") => request(`${config.ENDPOINTS.assets}${params}`),
  getQuotes: (params = "") => request(`${config.ENDPOINTS.quotes}${params}`),
  getLatestQuotes: () => request(config.ENDPOINTS.latest),
  getIndicators: () => request(config.ENDPOINTS.indicators),

  getTechnicalIndicators: (ticker, params = "") =>
    request(`/technical/${encodeURIComponent(ticker)}/${params}`)
};
})();
