from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from llm_agent import LLMClient
from news import get_news
from tools import (
    compare_stocks,
    compute_indicators,
    get_fundamentals,
    get_history,
    get_price,
    top_low_volatility,
)

app = FastAPI(title="Finance AI App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TICKER_ALIASES = {
    "TCS": "TCS.NS",
    "INFOSYS": "INFY.NS",
    "INFY": "INFY.NS",
    "RELIANCE": "RELIANCE.NS",
    "RELIANCE INDUSTRIES": "RELIANCE.NS",
}

DEFAULT_VOLATILITY_UNIVERSE = [
    "TCS.NS",
    "INFY.NS",
    "RELIANCE.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "HINDUNILVR.NS",
    "ITC.NS",
    "LT.NS",
    "SBIN.NS",
    "BHARTIARTL.NS",
]

WATCHLIST_PATH = Path(__file__).with_name("watchlist.json")


def normalize_tickers(tickers: List[str]) -> List[str]:
    normalized = []
    for ticker in tickers:
        if not ticker:
            continue
        key = ticker.strip().upper()
        normalized.append(TICKER_ALIASES.get(key, key))
    return normalized


def make_citation_for_ticker(ticker: str) -> Dict[str, str]:
    return {
        "title": f"Yahoo Finance {ticker}",
        "url": f"https://finance.yahoo.com/quote/{ticker}",
    }


def serialize_history(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    serialized = []
    for record in records:
        item = dict(record)
        if "Date" in item:
            item["Date"] = str(item["Date"])
        if "date" in item:
            item["date"] = str(item["date"])
        serialized.append(item)
    return serialized


def read_watchlist() -> List[str]:
    if not WATCHLIST_PATH.exists():
        return []
    return json.loads(WATCHLIST_PATH.read_text())


def write_watchlist(tickers: List[str]) -> None:
    WATCHLIST_PATH.write_text(json.dumps(sorted(set(tickers))))


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/watchlist")
async def get_watchlist() -> Dict[str, Any]:
    return {"watchlist": read_watchlist()}


@app.post("/watchlist")
async def add_watchlist(payload: Dict[str, Any]) -> Dict[str, Any]:
    ticker = payload.get("ticker")
    if not ticker:
        raise HTTPException(status_code=400, detail="ticker is required")
    tickers = read_watchlist()
    tickers.append(normalize_tickers([ticker])[0])
    write_watchlist(tickers)
    return {"watchlist": read_watchlist()}


@app.delete("/watchlist")
async def remove_watchlist(payload: Dict[str, Any]) -> Dict[str, Any]:
    ticker = payload.get("ticker")
    if not ticker:
        raise HTTPException(status_code=400, detail="ticker is required")
    tickers = [t for t in read_watchlist() if t != normalize_tickers([ticker])[0]]
    write_watchlist(tickers)
    return {"watchlist": tickers}


@app.post("/plan")
async def plan(payload: Dict[str, Any]) -> Dict[str, Any]:
    query = payload.get("query")
    if not query:
        raise HTTPException(status_code=400, detail="query is required")
    llm = LLMClient()
    return llm.plan(query)


@app.post("/query")
async def query(payload: Dict[str, Any]) -> Dict[str, Any]:
    query_text = payload.get("query")
    stream = payload.get("stream", True)
    if not query_text:
        raise HTTPException(status_code=400, detail="query is required")

    llm = LLMClient()
    plan = llm.plan(query_text)
    tickers = normalize_tickers(plan.get("tickers", []))
    intent = plan.get("intent", "").lower()
    tools = plan.get("tools", [])
    period = plan.get("period", "6mo") or "6mo"

    context: Dict[str, Any] = {"plan": plan}
    citations: List[Dict[str, str]] = []

    def ensure_tickers(defaults: List[str]) -> List[str]:
        return tickers if tickers else defaults

    try:
        if "get_price" in tools or "price" in intent:
            target = ensure_tickers(["TCS.NS"])[:1]
            context["prices"] = [get_price(t) for t in target]
            citations.extend([make_citation_for_ticker(t) for t in target])

        if "get_history" in tools or "chart" in intent or "history" in intent:
            target = ensure_tickers(["TCS.NS"])[:1]
            history = get_history(target[0], period=period)
            context["history"] = serialize_history(history.to_dict(orient="records"))
            citations.append(make_citation_for_ticker(target[0]))

        if "compute_rsi" in tools or "rsi" in intent:
            target = ensure_tickers(["RELIANCE.NS"])[:1]
            indicators = compute_indicators(target[0], period=period)
            context["rsi"] = {
                "ticker": target[0],
                "values": indicators["rsi"],
                "history": serialize_history(indicators["history"].to_dict(orient="records")),
            }
            citations.append(make_citation_for_ticker(target[0]))

        if "compute_macd" in tools:
            target = ensure_tickers(["TCS.NS"])[:1]
            indicators = compute_indicators(target[0], period=period)
            macd_df: pd.DataFrame = indicators["macd"]
            context["macd"] = {
                "ticker": target[0],
                "values": macd_df.to_dict(orient="records"),
                "history": serialize_history(indicators["history"].to_dict(orient="records")),
            }
            citations.append(make_citation_for_ticker(target[0]))

        if "compute_sma" in tools:
            target = ensure_tickers(["TCS.NS"])[:1]
            indicators = compute_indicators(target[0], period=period)
            context["sma"] = {
                "ticker": target[0],
                "values": indicators["sma"],
                "history": serialize_history(indicators["history"].to_dict(orient="records")),
            }
            citations.append(make_citation_for_ticker(target[0]))

        if "compute_bollinger" in tools:
            target = ensure_tickers(["TCS.NS"])[:1]
            indicators = compute_indicators(target[0], period=period)
            bollinger_df: pd.DataFrame = indicators["bollinger"]
            context["bollinger"] = {
                "ticker": target[0],
                "values": bollinger_df.to_dict(orient="records"),
                "history": serialize_history(indicators["history"].to_dict(orient="records")),
            }
            citations.append(make_citation_for_ticker(target[0]))

        if "get_fundamentals" in tools or "fundamentals" in intent:
            target = ensure_tickers(["TCS.NS", "INFY.NS"])
            context["fundamentals"] = [get_fundamentals(t) for t in target]
            citations.extend([make_citation_for_ticker(t) for t in target])

        if "compare_stocks" in tools or "compare" in intent:
            target = ensure_tickers(["TCS.NS", "INFY.NS"])
            context["comparison"] = compare_stocks(target)
            citations.extend([make_citation_for_ticker(t) for t in target])

        if "top_low_volatility" in tools or "low volatility" in intent:
            target = ensure_tickers(DEFAULT_VOLATILITY_UNIVERSE)
            context["low_volatility"] = top_low_volatility(target)
            citations.extend([make_citation_for_ticker(item["ticker"]) for item in context["low_volatility"]])

        if "get_news" in tools or "news" in intent:
            news_items = get_news("stock market")
            context["news"] = news_items
            citations.extend([
                {"title": item["title"], "url": item["url"]}
                for item in news_items if item.get("url")
            ])

    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    if not citations:
        citations.append({"title": "Yahoo Finance", "url": "https://finance.yahoo.com"})

    if stream:
        def event_stream():
            for chunk in llm.summarize_stream(query_text, context, citations):
                yield f"data: {json.dumps({'text': chunk})}\n\n"
            yield f"data: {json.dumps({'done': True, 'citations': citations, 'context': context})}\n\n"

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    answer = llm.summarize(query_text, context, citations)
    return {"answer": answer, "citations": citations, "context": context}
