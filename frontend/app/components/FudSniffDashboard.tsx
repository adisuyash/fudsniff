"use client";

import React, { useEffect, useState } from "react";
import { BarChart3, RefreshCw, Newspaper } from "lucide-react";
import { analyzeNews } from "@/app/lib/api";
import { SignalCard } from "@/app/components/SignalCard";

interface NewsArticle {
  title: string;
  description: string;
  publishedAt: string;
}

interface Signal {
  signal: string;
  confidence: number;
  reasoning: string;
  coin: string;
  timestamp: string;
  id: number;
}

export function FudSniffDashboard() {
  const [signals, setSignals] = useState<Signal[]>([]);
  const [newsText, setNewsText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [latestNews, setLatestNews] = useState<NewsArticle[]>([]);
  const [stats, setStats] = useState({
    totalAnalyses: 0,
    buySignals: 0,
    shortSignals: 0,
    avgConfidence: 0,
  });

  useEffect(() => {
    const loadNews = async () => {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/news`);
      const data = await res.json();
      setLatestNews(data.news || []);
    };
    loadNews();
  }, []);

  useEffect(() => {
    const totalAnalyses = signals.length;
    const buySignals = signals.filter(
      (s) => s.signal.toUpperCase() === "BUY"
    ).length;
    const shortSignals = signals.filter(
      (s) => s.signal.toUpperCase() === "SHORT"
    ).length;
    const avgConfidence =
      totalAnalyses > 0
        ? Math.round(
            signals.reduce((sum, s) => sum + s.confidence, 0) / totalAnalyses
          )
        : 0;

    setStats({ totalAnalyses, buySignals, shortSignals, avgConfidence });
  }, [signals]);

  const handleAnalyze = async (text: string) => {
    setIsLoading(true);
    try {
      const result = await analyzeNews(text);
      const newSignal: Signal = {
        ...result,
        timestamp: new Date().toISOString(),
        id: Date.now(),
      };
      setSignals((prev) => [newSignal, ...prev]);
    } catch (e) {
      console.error("Error analyzing news:", e);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center gap-3">
          <BarChart3 className="w-6 h-6 text-blue-600" />
          <h1 className="text-xl font-bold text-gray-900">
            FudSniff Dashboard
          </h1>
        </div>
      </header>

      <main className="max-w-7xl mx-auto p-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          {/* Input Card */}
          <div className="bg-white rounded-lg p-6 shadow">
            <div className="flex items-center gap-2 mb-4">
              <Newspaper className="w-5 h-5 text-blue-600" />
              <h2 className="text-lg font-bold text-gray-800">Analyze News</h2>
            </div>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleAnalyze(newsText);
              }}
            >
              <textarea
                rows={4}
                className="w-full p-3 border rounded-lg text-sm focus:outline-none text-gray-700"
                placeholder="Paste crypto news article here..."
                value={newsText}
                onChange={(e) => setNewsText(e.target.value)}
                disabled={isLoading}
              />
              <div className="mt-4 flex justify-between">
                <button
                  type="button"
                  onClick={() =>
                    setNewsText(
                      "Bitcoin surges as MicroStrategy buys more BTC..."
                    )
                  }
                  className="text-sm text-blue-500 hover:underline"
                  disabled={isLoading}
                >
                  Use Sample
                </button>
                <button
                  type="submit"
                  disabled={!newsText || isLoading}
                  className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg flex items-center gap-2"
                >
                  {isLoading ? (
                    <RefreshCw className="w-4 h-4 animate-spin" />
                  ) : (
                    <BarChart3 className="w-4 h-4" />
                  )}
                  {isLoading ? "Analyzing..." : "Analyze"}
                </button>
              </div>
            </form>
          </div>

          {/* Results */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-800">
              Recent Signals
            </h3>
            {signals.length === 0 ? (
              <div className="bg-white text-center p-6 rounded-lg shadow">
                <p className="text-sm text-gray-500">
                  No signals yet. Paste a news article to begin.
                </p>
              </div>
            ) : (
              signals.map((signal) => (
                <SignalCard key={signal.id} {...signal} />
              ))
            )}
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Stats */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-white p-4 rounded shadow text-center">
              <div className="text-blue-600 text-xl font-bold">
                {stats.totalAnalyses}
              </div>
              <div className="text-xs text-gray-600">Total Analyses</div>
            </div>
            <div className="bg-white p-4 rounded shadow text-center">
              <div className="text-green-600 text-xl font-bold">
                {stats.buySignals}
              </div>
              <div className="text-xs text-gray-600">Buy Signals</div>
            </div>
            <div className="bg-white p-4 rounded shadow text-center">
              <div className="text-red-600 text-xl font-bold">
                {stats.shortSignals}
              </div>
              <div className="text-xs text-gray-600">Short Signals</div>
            </div>
            <div className="bg-white p-4 rounded shadow text-center">
              <div className="text-purple-600 text-xl font-bold">
                {stats.avgConfidence}%
              </div>
              <div className="text-xs text-gray-600">Avg Confidence</div>
            </div>
          </div>

          {/* Latest News */}
          <div className="bg-white p-4 rounded shadow">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-sm font-semibold text-gray-800">
                Latest News
              </h3>
              <button
                onClick={() => window.location.reload()}
                className="p-1 text-blue-600"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
            </div>
            <ul className="space-y-3 text-sm">
              {latestNews.map((news, i) => (
                <li key={i} className="border-b pb-2">
                  <strong>{news.title}</strong>
                  <p className="text-xs text-gray-600 mb-2">
                    {news.description}
                  </p>
                  <button
                    onClick={() =>
                      handleAnalyze(`${news.title}. ${news.description}`)
                    }
                    disabled={isLoading}
                    className="text-blue-500 text-xs hover:underline"
                  >
                    Quick Analyze
                  </button>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </main>
    </div>
  );
}
