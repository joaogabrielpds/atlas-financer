
import math
from datetime import timedelta

import yfinance as yf

from django.utils import timezone

from apps.assets.models import Asset
from apps.markets.models import Quote



YAHOO_TICKERS = {
    # Ações brasileiras
    "PETR4": "PETR4.SA",
    "VALE3": "VALE3.SA",
    "ITUB4": "ITUB4.SA",
    "BBAS3": "BBAS3.SA",
    "BBDC4": "BBDC4.SA",
    "WEGE3": "WEGE3.SA",

    # FIIs
    "MXRF11": "MXRF11.SA",
    "BTLG11": "BTLG11.SA",
    "HGBS11": "HGBS11.SA",
    "GGRC11": "GGRC11.SA",

    # ETF brasileiro
    "IVVB11": "IVVB11.SA",

    # Ações americanas
    "AAPL": "AAPL",
    "MSFT": "MSFT",
    "NVDA": "NVDA",

    # Criptomoedas
    "BTC-USD": "BTC-USD",
    "ETH-USD": "ETH-USD",
    "SOL-USD": "SOL-USD",

    # Índices
    "IBOV": "^BVSP",
    "SP500": "^GSPC",
}


SOURCE = "yfinance"
OVERLAP_DAYS = 3


def valid_number(value):
    if value is None:
        return None

    try:
        value = float(value)
    except (TypeError, ValueError):
        return None

    return value if math.isfinite(value) else None


def collect_asset_history(asset, period="1y", full=False):
    symbol = YAHOO_TICKERS.get(asset.ticker)

    if not symbol:
        raise ValueError(f"Ticker não configurado: {asset.ticker}")

    history_query = {
        "interval": "1d",
        "auto_adjust": False,
        "actions": False,
    }

    last_quote = None

    if not full:
        last_quote = (
            Quote.objects.filter(
                asset=asset,
                source=SOURCE,
            )
            .order_by("-timestamp")
            .first()
        )

    if last_quote:
        start_date = (
            last_quote.timestamp.date()
            - timedelta(days=OVERLAP_DAYS)
        )

        history_query["start"] = start_date.isoformat()
    else:
        history_query["period"] = period

    history = yf.Ticker(symbol).history(**history_query)

    if history.empty:
        raise ValueError(f"Nenhum histórico recebido para {symbol}")

    saved = 0

    for date, row in history.iterrows():
        close = valid_number(row.get("Close"))

        if close is None or close <= 0:
            continue

        timestamp = date.to_pydatetime()

        if timezone.is_naive(timestamp):
            timestamp = timezone.make_aware(timestamp)

        volume = valid_number(row.get("Volume"))

        Quote.objects.update_or_create(
            asset=asset,
            timestamp=timestamp,
            source=SOURCE,
            defaults={
                "open": valid_number(row.get("Open")),
                "high": valid_number(row.get("High")),
                "low": valid_number(row.get("Low")),
                "close": close,
                "adjusted_close": valid_number(row.get("Adj Close")),
                "volume": int(volume) if volume is not None else None,
                "currency": asset.currency,
            },
        )

        saved += 1

    return saved


def collect_all_assets(period="1y", full=False):
    results = []

    for asset in Asset.objects.filter(is_active=True):
        try:
            count = collect_asset_history(
                asset,
                period=period,
                full=full,
            )

            results.append({
                "ticker": asset.ticker,
                "status": "success",
                "records": count,
            })

        except Exception as error:
            results.append({
                "ticker": asset.ticker,
                "status": "error",
                "message": str(error),
            })

    return results
