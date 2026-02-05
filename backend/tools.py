from __future__ import annotations

import time
from typing import Any, Dict, List

import pandas as pd
import yfinance as yf

from indicators import compute_bollinger, compute_macd, compute_rsi, compute_sma

CACHE: Dict[str, Dict[str, Any]] = {}
CACHE_TTL_SECONDS = 300


def _cache_get(key: str) -> Any | None:
    entry = CACHE.get(key)
    if not entry:
        return None
    if time.time() - entry["ts"] > CACHE_TTL_SECONDS:
        CACHE.pop(key, None)
        return None
    return entry["value"]


def _cache_set(key: str, value: Any) -> None:
    CACHE[key] = {"value": value, "ts": time.time()}


def _normalize_ticker(ticker: str) -> str:
    return ticker.strip().upper()


def get_price(ticker: str) -> Dict[str, Any]:
    ticker = _normalize_ticker(ticker)
    cache_key = f"price:{ticker}"
    cached = _cache_get(cache_key)
    if cached:
        return cached
    stock = yf.Ticker(ticker)
    data = stock.history(period="1d")
    if data.empty:
        raise ValueError(f"No price data for {ticker}")
    price = float(data["Close"].iloc[-1])
    result = {"ticker": ticker, "price": price, "currency": stock.fast_info.get("currency", "")}
    _cache_set(cache_key, result)
    return result


def get_history(ticker: str, period: str = "6mo") -> pd.DataFrame:
    ticker = _normalize_ticker(ticker)
    cache_key = f"history:{ticker}:{period}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached.copy()
    stock = yf.Ticker(ticker)
    history = stock.history(period=period)
    if history.empty:
        raise ValueError(f"No history for {ticker}")
    history = history.reset_index()
    _cache_set(cache_key, history)
    return history.copy()


def get_fundamentals(ticker: str) -> Dict[str, Any]:
    ticker = _normalize_ticker(ticker)
    cache_key = f"fundamentals:{ticker}"
    cached = _cache_get(cache_key)
    if cached:
        return cached
    stock = yf.Ticker(ticker)
    info = stock.get_info()
    def normalize(value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, (int, float, str)):
            return value
        try:
            return float(value)
        except (TypeError, ValueError):
            return str(value)

    fundamentals = {
        "ticker": ticker,
        "marketCap": normalize(info.get("marketCap")),
        "trailingPE": normalize(info.get("trailingPE")),
        "forwardPE": normalize(info.get("forwardPE")),
        "priceToBook": normalize(info.get("priceToBook")),
        "profitMargins": normalize(info.get("profitMargins")),
        "returnOnEquity": normalize(info.get("returnOnEquity")),
        "beta": normalize(info.get("beta")),
        "sector": normalize(info.get("sector")),
        "industry": normalize(info.get("industry")),
    }
    _cache_set(cache_key, fundamentals)
    return fundamentals


def compare_stocks(tickers: List[str]) -> List[Dict[str, Any]]:
    comparisons = []
    for ticker in tickers:
        comparisons.append(get_fundamentals(ticker))
    return comparisons


def compute_indicators(ticker: str, period: str = "6mo") -> Dict[str, Any]:
    history = get_history(ticker, period=period)
    history = history.rename(columns={"Date": "date", "Close": "close"})
    history = history[["date", "close"]]
    close_series = history["close"]
    rsi = compute_rsi(close_series).where(pd.notna, None).tolist()
    macd = compute_macd(close_series).where(pd.notna, None)
    sma = compute_sma(close_series).where(pd.notna, None).tolist()
    bollinger = compute_bollinger(close_series).where(pd.notna, None)
    return {
        "history": history,
        "rsi": rsi,
        "macd": macd,
        "sma": sma,
        "bollinger": bollinger,
    }


def top_low_volatility(tickers: List[str], period: str = "6mo", top_n: int = 5) -> List[Dict[str, Any]]:
    results = []
    for ticker in tickers:
        history = get_history(ticker, period=period)
        returns = history["Close"].pct_change().dropna()
        volatility = float(returns.std() * (252 ** 0.5))
        results.append({"ticker": _normalize_ticker(ticker), "volatility": volatility})
    results.sort(key=lambda x: x["volatility"])
    return results[:top_n]
