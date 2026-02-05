import os
from typing import Any, Dict, List

import requests

NEWS_API_URL = "https://newsapi.org/v2/everything"


def get_news(query: str, page_size: int = 5) -> List[Dict[str, Any]]:
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        raise ValueError("NEWS_API_KEY is required for news")
    params = {
        "q": query,
        "pageSize": page_size,
        "sortBy": "publishedAt",
        "language": "en",
        "apiKey": api_key,
    }
    response = requests.get(NEWS_API_URL, params=params, timeout=15)
    response.raise_for_status()
    payload = response.json()
    articles = payload.get("articles", [])
    return [
        {
            "title": article.get("title"),
            "url": article.get("url"),
            "source": article.get("source", {}).get("name"),
            "publishedAt": article.get("publishedAt"),
            "description": article.get("description"),
        }
        for article in articles
    ]
