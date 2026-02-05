import numpy as np
import pandas as pd


def compute_rsi(series: pd.Series, window: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=window, min_periods=window).mean()
    avg_loss = loss.rolling(window=window, min_periods=window).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi


def compute_macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return pd.DataFrame({"macd": macd_line, "signal": signal_line, "histogram": histogram})


def compute_sma(series: pd.Series, window: int = 20) -> pd.Series:
    return series.rolling(window=window).mean()


def compute_bollinger(series: pd.Series, window: int = 20, num_std: int = 2) -> pd.DataFrame:
    sma = compute_sma(series, window=window)
    rolling_std = series.rolling(window=window).std()
    upper = sma + (rolling_std * num_std)
    lower = sma - (rolling_std * num_std)
    return pd.DataFrame({"middle": sma, "upper": upper, "lower": lower})
