"use client";

import React, { useEffect, useState } from "react";
import { BarChart3, RefreshCw, Newspaper } from "lucide-react";
import { analyzeNews } from "@/app/lib/api";
import { SignalCard } from "@/app/components/SignalCard";
import Image from "next/image";
import Link from "next/link";
import Paws from "./paws";

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
      <Paws />

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

      <div className="mt-32 w-full max-w-7xl mx-auto flex flex-col flex-1 overflow-hidden">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 flex-1 px-4 sm:px-8 md:px-16 min-h-0">
          {/* Main Analysis + Signals */}
          <div className="lg:col-span-2 flex flex-col gap-8 min-h-0">
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
                    className="group relative overflow-hidden rounded-xl border border-white/20 bg-gradient-to-r from-white to-gray-200 text-black px-5 py-2 font-semibold transition-all duration-300 hover:shadow-lg hover:shadow-white/10 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <div className="flex items-center gap-2">
                      {isLoading ? (
                        <RefreshCw className="w-4 h-4 animate-spin" />
                      ) : (
                        <BarChart3 className="w-4 h-4" />
                      )}
                      {isLoading ? "Sniffing..." : "Analyze"}
                    </div>
                  </button>
                </div>
              </form>
            </div>

            {/* Signals */}
            <div className="flex-1 min-h-0 flex flex-col">
              <h3 className="text-2xl font-semibold text-white mb-2">
                Recent Signals
              </h3>
              <div className="flex-1 overflow-y-auto pr-1 space-y-3">
                {signals.length === 0 ? (
                  <div className="bg-black/20 p-6 text-center rounded-xl border border-white/10">
                    <div className="mb-3 opacity-30">
                      <Image
                        src="/pawprint.png"
                        alt=""
                        width={60}
                        height={60}
                        className="w-12 h-12 mx-auto filter grayscale"
                      />
                    </div>
                    <p className="text-gray-400 text-lg mb-2">
                      No signals detected yet
                    </p>
                    <p className="text-sm text-white/60">
                      Paste a crypto news article above to analyze.
                    </p>
                  </div>
                ) : (
                  signals.map((signal) => (
                    <SignalCard
                      key={signal.id}
                      signal={signal.signal as "BUY" | "SHORT" | "HOLD"}
                      confidence={signal.confidence}
                      reasoning={signal.reasoning}
                      coin={signal.coin}
                      timestamp={signal.timestamp}
                    />
                  ))
                )}
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="flex flex-col space-y-6 min-h-0">
            <div className="grid grid-cols-2 gap-4">
              {[
                {
                  label: "Total Analyses",
                  value: stats.totalAnalyses,
                  color: "text-white",
                },
                {
                  label: "Avg Confidence",
                  value: `${stats.avgConfidence}%`,
                  color: "text-purple-300",
                },
                {
                  label: "Buy Signals",
                  value: stats.buySignals,
                  color: "text-green-400",
                },
                {
                  label: "Short Signals",
                  value: stats.shortSignals,
                  color: "text-red-400",
                },
              ].map((item, idx) => (
                <div
                  key={idx}
                  className="bg-black/20 p-4 rounded-xl text-center border border-white/10"
                >
                  <div className={`${item.color} text-2xl font-bold`}>
                    {item.value}
                  </div>
                  <div className="text-sm text-white/60">{item.label}</div>
                </div>
              ))}
            </div>

            {/* News */}
            <div className="bg-black/20 p-4 rounded-xl border border-white/10 max-h-[40vh] overflow-y-auto">
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
              <ul className="space-y-3 text-sm text-white/90 max-h-[40vh] overflow-y-auto pr-1">
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
