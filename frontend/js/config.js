
window.ATLAS_CONFIG = {
  API_BASE_URL: "http://127.0.0.1:8000/api/v1",
  REQUEST_TIMEOUT_MS: 8000,

  ENDPOINTS: {
    health: "/health/",
    markets: "/markets/",
    assets: "/assets/",
    quotes: "/quotes/",
    latest: "/quotes/latest/",
    indicators: "/economy/indicators/"
  }
};
