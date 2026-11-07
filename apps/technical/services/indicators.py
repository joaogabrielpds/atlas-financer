
import pandas as pd


def calculate_indicators(quotes):
    """
    Calcula indicadores técnicos a partir de cotações históricas.

    Indicadores:
    - SMA 20, 50 e 200
    - EMA 9 e 21
    - RSI 14
    - MACD (12, 26, 9)
    - Bandas de Bollinger (20, 2)
    """

    df = pd.DataFrame(quotes)

    if df.empty:
        return []

    df["close"] = pd.to_numeric(df["close"], errors="coerce")

    df = (
        df.dropna(subset=["close"])
        .sort_values("timestamp")
        .reset_index(drop=True)
    )

    if df.empty:
        return []

    close = df["close"]

    # Médias móveis simples
    df["sma_20"] = close.rolling(20).mean()
    df["sma_50"] = close.rolling(50).mean()
    df["sma_200"] = close.rolling(200).mean()

    # Médias móveis exponenciais
    df["ema_9"] = close.ewm(
        span=9,
        adjust=False,
        min_periods=9
    ).mean()

    df["ema_21"] = close.ewm(
        span=21,
        adjust=False,
        min_periods=21
    ).mean()

    # RSI 14 - suavização de Wilder
    delta = close.diff()

    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)

    avg_gain = gains.ewm(
        alpha=1 / 14,
        adjust=False,
        min_periods=14
    ).mean()

    avg_loss = losses.ewm(
        alpha=1 / 14,
        adjust=False,
        min_periods=14
    ).mean()

    rs = avg_gain / avg_loss

    df["rsi_14"] = 100 - (100 / (1 + rs))

    # Tratamento de movimentos sem perdas ou sem ganhos
    df.loc[
        (avg_loss == 0) & (avg_gain > 0),
        "rsi_14"
    ] = 100

    df.loc[
        (avg_gain == 0) & (avg_loss > 0),
        "rsi_14"
    ] = 0

    df.loc[
        (avg_gain == 0) & (avg_loss == 0),
        "rsi_14"
    ] = 50

    # MACD (12, 26, 9)
    ema_12 = close.ewm(
        span=12,
        adjust=False,
        min_periods=12
    ).mean()

    ema_26 = close.ewm(
        span=26,
        adjust=False,
        min_periods=26
    ).mean()

    df["macd"] = ema_12 - ema_26

    df["macd_signal"] = df["macd"].ewm(
        span=9,
        adjust=False,
        min_periods=9
    ).mean()

    df["macd_histogram"] = (
        df["macd"] - df["macd_signal"]
    )

    # Bandas de Bollinger (20, 2)
    middle = close.rolling(20).mean()
    deviation = close.rolling(20).std(ddof=0)

    df["bollinger_middle"] = middle
    df["bollinger_upper"] = middle + (2 * deviation)
    df["bollinger_lower"] = middle - (2 * deviation)

    # Preparação para resposta JSON
    indicator_columns = [
        "sma_20",
        "sma_50",
        "sma_200",
        "ema_9",
        "ema_21",
        "rsi_14",
        "macd",
        "macd_signal",
        "macd_histogram",
        "bollinger_middle",
        "bollinger_upper",
        "bollinger_lower",
    ]

    result = []

    for _, row in df.iterrows():
        item = {
            "timestamp": row["timestamp"].isoformat(),
            "close": round(float(row["close"]), 6),
        }

        for column in indicator_columns:
            value = row[column]

            item[column] = (
                round(float(value), 6)
                if pd.notna(value)
                else None
            )

        result.append(item)

    return result
