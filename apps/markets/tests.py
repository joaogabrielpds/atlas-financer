
from unittest.mock import patch

from django.test import TestCase

from apps.assets.models import Asset
from apps.markets.models import Market, Quote
from apps.markets.services.yahoo_finance import collect_asset_history


class YahooFinanceCollectorTests(TestCase):

    def setUp(self):
        self.market = Market.objects.create(
            name="B3",
            code="B3",
            country="Brasil",
            currency="BRL",
        )

        self.asset = Asset.objects.create(
            market=self.market,
            ticker="PETR4",
            name="Petrobras PN",
            asset_type="STOCK",
            currency="BRL",
            is_active=True,
        )

    @patch("apps.markets.services.yahoo_finance.yf.Ticker")
    def test_collect_history_success(self, mock_ticker):
        import pandas as pd

        history = pd.DataFrame(
            {
                "Open": [35.0],
                "High": [36.0],
                "Low": [34.0],
                "Close": [35.5],
                "Adj Close": [35.2],
                "Volume": [100000],
            },
            index=pd.to_datetime(["2026-10-29"]),
        )

        mock_ticker.return_value.history.return_value = history

        result = collect_asset_history(self.asset, period="1mo")

        self.assertEqual(result, 1)
        self.assertEqual(Quote.objects.count(), 1)

        quote = Quote.objects.get(asset=self.asset)

        self.assertEqual(float(quote.close), 35.5)
        self.assertEqual(quote.source, "yfinance")

    @patch("apps.markets.services.yahoo_finance.yf.Ticker")
    def test_existing_quote_is_updated(self, mock_ticker):
        import pandas as pd

        history = pd.DataFrame(
            {
                "Open": [35.0],
                "High": [36.0],
                "Low": [34.0],
                "Close": [37.0],
                "Adj Close": [36.8],
                "Volume": [150000],
            },
            index=pd.to_datetime(["2026-10-29"]),
        )

        mock_ticker.return_value.history.return_value = history

        collect_asset_history(self.asset, period="1mo")
        collect_asset_history(self.asset, period="1mo")

        self.assertEqual(Quote.objects.count(), 1)

        quote = Quote.objects.get(asset=self.asset)

        self.assertEqual(float(quote.close), 37.0)

    def test_unknown_ticker_raises_error(self):
        self.asset.ticker = "INVALID"
        self.asset.save()

        with self.assertRaises(ValueError):
            collect_asset_history(self.asset, period="1mo")

    @patch("apps.markets.services.yahoo_finance.yf.Ticker")
    def test_empty_history_raises_error(self, mock_ticker):
        import pandas as pd

        mock_ticker.return_value.history.return_value = pd.DataFrame()

        with self.assertRaises(ValueError):
            collect_asset_history(self.asset, period="1mo")
