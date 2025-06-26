"use client";

import React, { useEffect, useState } from "react";
import { BarChart3, RefreshCw, Newspaper } from "lucide-react";
import { analyzeNews } from "@/app/lib/api";
import { SignalCard } from "@/app/components/SignalCard";
import Image from "next/image";
import Link from "next/link";

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
    <div className="relative w-full h-full font-[family-name:var(--font-geist-sans)] text-gray-100">
      {/* <div className="fixed top-10 left-10 flex items-center gap-4 z-10">
        <div className="relative group">
          <Image
            src="/fudsniff.png"
            alt="FudSniff logo"
            width={48}
            height={48}
            className="h-12 w-12 transition-transform duration-200 group-hover:scale-110"
            priority
          />
          <div className="absolute inset-0 bg-white opacity-0 group-hover:opacity-20 rounded-full blur-md transition-opacity duration-200 -z-10"></div>
        </div>
        <h1 className="text-3xl font-bold tracking-tight text-white">
          Fud Sniff
        </h1>
      </div> */}
      <Link
        href="/"
        className="fixed top-10 left-10 flex items-center gap-4 z-10 group"
      >
        <div className="relative">
          <Image
            src="/fudsniff.png"
            alt="FudSniff logo"
            width={48}
            height={48}
            className="h-12 w-12 transition-transform duration-200 group-hover:scale-110"
            priority
          />
          <div className="absolute inset-0 bg-white opacity-0 group-hover:opacity-20 rounded-full blur-md transition-opacity duration-200 -z-10"></div>
        </div>
        <h1 className="text-3xl font-bold tracking-tight text-white">
          Fud Sniff
        </h1>
      </Link>

      <div className="mt-32 px-4 sm:px-8 md:px-16 w-full max-w-6xl mx-auto overflow-y-auto">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-8">
            {/* Input */}
            <div className="bg-black/20 border border-white/10 backdrop-blur rounded-xl p-6">
              <div className="flex items-center gap-2 mb-4">
                <Newspaper className="w-5 h-5 text-white/70" />
                <h2 className="text-2xl font-bold">Analyze News</h2>
              </div>
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleAnalyze(newsText);
                }}
              >
                <textarea
                  rows={4}
                  className="w-full p-3 rounded-lg text-sm text-white bg-black/30 border border-white/10 focus:outline-none focus:ring-2 focus:ring-white/20"
                  placeholder="Paste crypto news article here..."
                  value={newsText}
                  onChange={(e) => setNewsText(e.target.value)}
                  disabled={isLoading}
                />
                <div className="mt-4 flex justify-between items-center">
                  <button
                    type="button"
                    onClick={() =>
                      setNewsText(
                        "Bitcoin surges as MicroStrategy buys more BTC..."
                      )
                    }
                    className="text-sm text-blue-400 hover:underline"
                    disabled={isLoading}
                  >
                    Use Sample
                  </button>
                  <button
                    type="submit"
                    disabled={!newsText || isLoading}
                    className="group relative overflow-hidden rounded-md border border-gray-600 text-sm sm:text-base text-gray-900 bg-white transition-all duration-300 font-medium disabled:bg-gray-500 px-4 py-2 flex items-center gap-2"
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

            {/* Signal Results */}
            <div className="space-y-4">
              <h3 className="text-2xl font-semibold text-white">
                Recent Signals
              </h3>
              {signals.length === 0 ? (
                <div className="bg-black/20 p-6 text-center rounded-xl border border-white/10">
                  <p className="text-sm text-white/60">
                    No signals yet. Paste a news article to begin.
                  </p>
                </div>
              ) : (
                <div className="space-y-3 max-h-[60vh] overflow-y-auto pr-1">
                  {signals.map((signal) => (
                    <SignalCard
                      key={signal.id}
                      signal={signal.signal as "BUY" | "SHORT" | "HOLD"}
                      confidence={signal.confidence}
                      reasoning={signal.reasoning}
                      coin={signal.coin}
                      timestamp={signal.timestamp}
                    />
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-black/20 p-4 rounded-xl text-center border border-white/10">
                <div className="text-white text-2xl font-bold">
                  {stats.totalAnalyses}
                </div>
                <div className="text-sm text-white/60">Total Analyses</div>
              </div>
              <div className="bg-black/20 p-4 rounded-xl text-center border border-white/10">
                <div className="text-purple-300 text-2xl font-bold">
                  {stats.avgConfidence}%
                </div>
                <div className="text-sm text-white/60">Avg Confidence</div>
              </div>
              <div className="bg-black/20 p-4 rounded-xl text-center border border-white/10">
                <div className="text-green-400 text-2xl font-bold">
                  {stats.buySignals}
                </div>
                <div className="text-sm text-white/60">Buy Signals</div>
              </div>
              <div className="bg-black/20 p-4 rounded-xl text-center border border-white/10">
                <div className="text-red-400 text-2xl font-bold">
                  {stats.shortSignals}
                </div>
                <div className="text-sm text-white/60">Short Signals</div>
              </div>
            </div>

            <div className="bg-black/20 p-4 rounded-xl border border-white/10">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-white">
                  Latest News
                </h3>
                <button
                  onClick={() => window.location.reload()}
                  className="p-1 text-white/70 hover:text-white"
                >
                  <RefreshCw className="w-4 h-4" />
                </button>
              </div>
              <ul className="space-y-3 text-sm text-white/90">
                {latestNews.map((news, i) => (
                  <li key={i} className="border-b border-white/10 pb-2">
                    <strong className="text-base text-white font-semibold">
                      {news.title}
                    </strong>
                    <p className="text-sm text-white/60 mb-2">
                      {news.description}
                    </p>
                    <button
                      onClick={() =>
                        handleAnalyze(`${news.title}. ${news.description}`)
                      }
                      disabled={isLoading}
                      className="text-blue-400 text-sm hover:underline"
                    >
                      Quick Analyze
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
