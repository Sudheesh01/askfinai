"use client";

import { useEffect, useState } from "react";

import ChatInput from "@/components/ChatInput";
import ChatMessage from "@/components/ChatMessage";
import Sidebar from "@/components/Sidebar";
import PriceChart from "@/charts/PriceChart";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { streamQuery, type Citation } from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface HistoryPoint {
  date: string;
  Close?: number;
  close?: number;
}

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export default function HomePage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [citations, setCitations] = useState<Citation[]>([]);
  const [history, setHistory] = useState<HistoryPoint[]>([]);
  const [watchlist, setWatchlist] = useState<string[]>([]);

  const fetchWatchlist = async () => {
    const response = await fetch(`${BACKEND_URL}/watchlist`);
    const data = await response.json();
    setWatchlist(data.watchlist || []);
  };

  useEffect(() => {
    fetchWatchlist();
  }, []);

  const handleSend = async () => {
    const query = input.trim();
    if (!query) return;

    setMessages((prev) => [...prev, { role: "user", content: query }, { role: "assistant", content: "" }]);
    setInput("");
    setLoading(true);
    setCitations([]);
    setHistory([]);

    try {
      const result = await streamQuery(query, (token) => {
        setMessages((prev) => {
          const updated = [...prev];
          const last = updated[updated.length - 1];
          if (last && last.role === "assistant") {
            updated[updated.length - 1] = { ...last, content: `${last.content}${token}` };
          }
          return updated;
        });
      });

      setCitations(result.citations);
      const historyData = (result.context?.history as HistoryPoint[]) ||
        (result.context?.rsi as { history?: HistoryPoint[] })?.history || [];
      setHistory(historyData);
    } catch (error) {
      setMessages((prev) => [...prev, { role: "assistant", content: "Sorry, something went wrong." }]);
    } finally {
      setLoading(false);
    }
  };

  const handleAddToWatchlist = async () => {
    if (!input.trim()) return;
    await fetch(`${BACKEND_URL}/watchlist`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ticker: input.trim() }),
    });
    setInput("");
    fetchWatchlist();
  };

  const handleRemoveWatchlist = async (ticker: string) => {
    await fetch(`${BACKEND_URL}/watchlist`, {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ticker }),
    });
    fetchWatchlist();
  };

  return (
    <main className="flex min-h-screen gap-6 bg-fin-bg px-6 py-8">
      <div className="hidden w-64 lg:block">
        <Sidebar watchlist={watchlist} onRemove={handleRemoveWatchlist} />
      </div>
      <div className="flex flex-1 flex-col gap-6">
        <header className="flex flex-col gap-2">
          <h1 className="text-2xl font-semibold text-fin-text">Finance Research Copilot</h1>
          <p className="text-sm text-fin-muted">
            Ask about live prices, indicators, fundamentals, and market news. Powered by free data sources.
          </p>
        </header>

        <Card className="space-y-4">
          <div className="flex flex-col gap-4">
            <div className="space-y-3">
              {messages.length === 0 && (
                <p className="text-sm text-fin-muted">
                  Try: “current price of TCS”, “show RSI for Reliance”, or “summarize today’s market news”.
                </p>
              )}
              {messages.map((message, index) => (
                <ChatMessage key={index} role={message.role} content={message.content} />
              ))}
            </div>
            <ChatInput value={input} onChange={setInput} onSend={handleSend} disabled={loading} />
            <div className="flex flex-wrap gap-2">
              <Button variant="outline" size="sm" onClick={handleAddToWatchlist}>
                Add to watchlist
              </Button>
              <Button variant="outline" size="sm" onClick={() => setInput("show last 6 months chart for TCS")}
              >
                Show 6M chart
              </Button>
              <Button variant="outline" size="sm" onClick={() => setInput("top 5 low volatility stocks")}
              >
                Low volatility picks
              </Button>
            </div>
          </div>
        </Card>

        <div className="grid gap-4 lg:grid-cols-[2fr_1fr]">
          <div className="space-y-4">
            {history.length > 0 && (
              <PriceChart
                title="Price history"
                data={history.map((point) => ({
                  date: point.date as string,
                  close: (point.close ?? point.Close) as number,
                }))}
              />
            )}
            {citations.length > 0 && (
              <Card>
                <h3 className="text-sm font-semibold text-fin-text">Sources</h3>
                <ul className="mt-2 space-y-2 text-sm text-fin-muted">
                  {citations.map((citation, index) => (
                    <li key={citation.url}>
                      <a
                        className="text-fin-accent hover:underline"
                        href={citation.url}
                        target="_blank"
                        rel="noreferrer"
                      >
                        [{index + 1}] {citation.title}
                      </a>
                    </li>
                  ))}
                </ul>
              </Card>
            )}
          </div>

          <Card>
            <h3 className="text-sm font-semibold text-fin-text">Quick prompts</h3>
            <div className="mt-3 space-y-2 text-sm text-fin-muted">
              <button className="block text-left hover:text-fin-text" onClick={() => setInput("compare TCS vs Infosys fundamentals")}>
                Compare TCS vs Infosys fundamentals
              </button>
              <button className="block text-left hover:text-fin-text" onClick={() => setInput("show RSI for Reliance")}
              >
                Show RSI for Reliance
              </button>
              <button className="block text-left hover:text-fin-text" onClick={() => setInput("summarize today’s market news")}
              >
                Summarize today’s market news
              </button>
              <button className="block text-left hover:text-fin-text" onClick={() => setInput("current price of TCS")}
              >
                Current price of TCS
              </button>
            </div>
          </Card>
        </div>
      </div>
    </main>
  );
}
