
from datetime import datetime, timedelta, timezone
from django.test import SimpleTestCase
from apps.technical.services.indicators import calculate_indicators


def make_quotes(values):
    """Gera cotações fictícias para os testes."""
    base_date = datetime(2026, 1, 1, tzinfo=timezone.utc)

    return [
        {
            "timestamp": base_date + timedelta(days=i),
            "close": value,
        }
        for i, value in enumerate(values)
    ]


class TechnicalIndicatorsTests(SimpleTestCase):

    def test_empty_quotes(self):
        """Deve retornar uma lista vazia sem cotações."""
        self.assertEqual(calculate_indicators([]), [])

    def test_sma_20(self):
        """SMA 20 deve calcular a média dos últimos 20 preços."""
        quotes = make_quotes(list(range(1, 21)))
        result = calculate_indicators(quotes)

        self.assertAlmostEqual(result[-1]["sma_20"], 10.5)

    def test_bollinger_bands(self):
        """Bandas de Bollinger devem usar média e desvio padrão."""
        quotes = make_quotes(list(range(1, 21)))
        result = calculate_indicators(quotes)

        last = result[-1]

        self.assertAlmostEqual(last["bollinger_middle"], 10.5)
        self.assertAlmostEqual(last["bollinger_upper"], 22.032563, places=5)
        self.assertAlmostEqual(last["bollinger_lower"], -1.032563, places=5)

    def test_sma_200_requires_200_quotes(self):
        """SMA 200 não deve existir antes de 200 observações."""
        quotes = make_quotes(list(range(1, 200)))
        result = calculate_indicators(quotes)

        self.assertIsNone(result[-1]["sma_200"])

        quotes = make_quotes(list(range(1, 201)))
        result = calculate_indicators(quotes)

        self.assertIsNotNone(result[-1]["sma_200"])

    def test_ema_9_requires_nine_quotes(self):
        """EMA 9 precisa de pelo menos nove observações."""
        quotes = make_quotes(list(range(1, 9)))
        result = calculate_indicators(quotes)

        self.assertIsNone(result[-1]["ema_9"])

        quotes = make_quotes(list(range(1, 10)))
        result = calculate_indicators(quotes)

        self.assertIsNotNone(result[-1]["ema_9"])

    def test_rsi_in_uptrend(self):
        """Uma sequência de altas deve produzir RSI 100."""
        quotes = make_quotes(list(range(1, 21)))
        result = calculate_indicators(quotes)

        self.assertAlmostEqual(result[-1]["rsi_14"], 100)

    def test_rsi_in_flat_market(self):
        """Uma sequência sem variação deve produzir RSI 50."""
        quotes = make_quotes([10] * 20)
        result = calculate_indicators(quotes)

        self.assertAlmostEqual(result[-1]["rsi_14"], 50)

    def test_macd_histogram(self):
        """Histograma deve ser MACD menos linha de sinal."""
        values = [
            float(i) + (i % 5) * 0.5
            for i in range(1, 61)
        ]

        result = calculate_indicators(make_quotes(values))
        last = result[-1]

        self.assertAlmostEqual(
            last["macd_histogram"],
            last["macd"] - last["macd_signal"],
        )

    def test_quotes_are_sorted_by_timestamp(self):
        """As observações devem sair em ordem cronológica."""
        quotes = make_quotes([10, 20, 30])
        quotes.reverse()

        result = calculate_indicators(quotes)

        dates = [item["timestamp"] for item in result]

        self.assertEqual(dates, sorted(dates))
