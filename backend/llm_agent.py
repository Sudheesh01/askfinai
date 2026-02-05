import json
import os
from typing import Any, Dict, List

import requests

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "qwen/qwen-2.5-vl-7b-instruct:free"


class LLMClient:
    def __init__(self) -> None:
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is required")

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def plan(self, query: str) -> Dict[str, Any]:
        system_prompt = (
            "You are a finance query planner. Output STRICT JSON only. "
            "No markdown, no extra text. Schema: {\"intent\":\"\",\"tickers\":[],\"period\":\"\",\"tools\":[]}. "
            "Never include numbers you computed. Infer tickers if possible."
        )
        payload = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query},
            ],
            "temperature": 0.1,
        }
        response = requests.post(OPENROUTER_URL, headers=self._headers(), json=payload, timeout=30)
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        return json.loads(content)

    def summarize(self, query: str, context: Dict[str, Any], citations: List[Dict[str, str]]) -> str:
        system_prompt = (
            "You are a finance assistant. Only use the provided context and citations. "
            "Never calculate new numbers or estimate values. Do not invent tickers. "
            "Include citations as [1], [2], etc."
        )
        user_prompt = {
            "query": query,
            "context": context,
            "citations": citations,
        }
        payload = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_prompt)},
            ],
            "temperature": 0.2,
            "stream": False,
        }
        response = requests.post(OPENROUTER_URL, headers=self._headers(), json=payload, timeout=30)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    def summarize_stream(self, query: str, context: Dict[str, Any], citations: List[Dict[str, str]]):
        system_prompt = (
            "You are a finance assistant. Only use the provided context and citations. "
            "Never calculate new numbers or estimate values. Do not invent tickers. "
            "Include citations as [1], [2], etc."
        )
        user_prompt = {
            "query": query,
            "context": context,
            "citations": citations,
        }
        payload = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_prompt)},
            ],
            "temperature": 0.2,
            "stream": True,
        }
        response = requests.post(OPENROUTER_URL, headers=self._headers(), json=payload, stream=True, timeout=60)
        response.raise_for_status()
        for line in response.iter_lines():
            if not line:
                continue
            if line.startswith(b"data: "):
                data = line[len(b"data: "):]
            else:
                data = line
            if data == b"[DONE]":
                break
            try:
                payload = json.loads(data)
            except json.JSONDecodeError:
                continue
            choices = payload.get("choices", [])
            if not choices:
                continue
            delta = choices[0].get("delta", {}).get("content")
            if delta:
                yield delta
