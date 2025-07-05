"use client";

import { useState, useEffect, useRef } from "react";
import Image from "next/image";
import Paws from "@/app/components/paws";
import { AlertCircle, PawPrint, RefreshCw, TrendingDown, TrendingUp } from "lucide-react";
import Toast from "@/app/components/Toast";
import Link from "next/link";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000";

interface TelegramSignal {
  id: string;
  source_channel: string;
  message_text: string;
  signal_type: string;
  confidence: number;
  tokens_mentioned: string[];
  timestamp: string;
  user_mention: string;
  reasoning?: string;
}

interface TelegramStatus {
  is_running: boolean;
  total_signals: number;
  last_signal: TelegramSignal | null;
}

interface SignalStats {
  total: number;
  by_type: Record<string, number>;
  by_token: Record<string, number>;
}

export default function TelegramSignalsPage() {
  const [signals, setSignals] = useState<TelegramSignal[] | null>(null);
  const [status, setStatus] = useState<TelegramStatus | null>(null);
  const [stats, setStats] = useState<SignalStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pendingStart, setPendingStart] = useState(false);
  const [toast, setToast] = useState<{ message: string; type?: string } | null>(
    null
  );
  const lastUpdateRef = useRef<number>(0);

  const fetchStatus = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/telegram/status`);
      const data = await res.json();
      setStatus(data);
      if (pendingStart && data.is_running) {
        setPendingStart(false);
        setToast({ message: "Social monitoring is started!", type: "success" });
      }
    } catch (err) {
      console.error("Error fetching status:", err);
    }
  };

  const fetchStats = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/telegram/stats`);
      const data = await res.json();
      setStats(data);
    } catch (err) {
      console.error("Error fetching stats:", err);
    }
  };

  const fetchSignals = async () => {
    const fetchTime = Date.now();
    try {
      const res = await fetch(`${API_BASE}/api/telegram/signals?limit=30`);
      const data = await res.json();

      if (fetchTime < lastUpdateRef.current) return;
      lastUpdateRef.current = fetchTime;

      if (data && Array.isArray(data.signals)) {
        if (data.signals.length || !signals?.length) {
          setSignals(data.signals);
          setError(null);
        }
      } else {
        if (!signals?.length) setSignals([]);
      }
    } catch (err) {
      if (!signals?.length) setError("Failed to load signals.");
    }
  };

  const startMonitoring = async () => {
    setLoading(true);
    setError(null);
    setPendingStart(true);
    try {
      const res = await fetch(`${API_BASE}/api/telegram/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
      const data = await res.json();
      if (data.status === "error") {
        setError(data.message);
        setPendingStart(false);
        setToast({ message: "Failed to start monitoring", type: "error" });
      } else {
        await fetchStatus();
        await fetchSignals();
        await fetchStats();
      }
    } catch (err) {
      setError("Failed to start monitoring");
      setToast({
        message: "404, Failed to start social monitoring!",
        type: "error",
      });
      setPendingStart(false);
    } finally {
      setLoading(false);
    }
  };

  const stopMonitoring = async () => {
    setLoading(true);
    try {
      await fetch(`${API_BASE}/api/telegram/stop`, { method: "POST" });
      setStatus((prev) => (prev ? { ...prev, is_running: false } : null));
      setToast({ message: "Social monitoring is stopped!", type: "stop" });
    } catch (err) {
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
    fetchStats();
    fetchSignals();
  }, []);

  useEffect(() => {
    if (!status?.is_running) return;
    const interval = setInterval(() => {
      fetchStatus();
      fetchSignals();
      fetchStats();
    }, 3000);
    return () => clearInterval(interval);
  }, [status?.is_running]);

  const getSignalColor = (type: string) => {
    switch (type) {
      case "BUY":
        return "text-green-400";
      case "SELL":
        return "text-red-400";
      case "ALERT":
        return "text-yellow-400";
      case "NEWS":
        return "text-blue-400";
      case "SHORT":
        return "text-orange-400";
      default:
        return "text-white/70";
    }
  };

  const getConfidenceColor = (conf: number) =>
    conf > 0.7
      ? "text-green-400"
      : conf > 0.4
      ? "text-yellow-400"
      : "text-red-400";

  return (
    <div className="relative w-full h-full font-[family-name:var(--font-geist-sans)] text-gray-100">
      <Paws />
      <Link
        href="/"
        className="fixed top-10 left-10 flex items-center gap-4 z-100"
      >
        <div className="relative">
          <Image
            src="/fudsniff.png"
            alt="FudSniff logo"
            width={48}
            height={48}
            className="h-12 w-12"
            priority
          />
        </div>
        <h1 className="text-3xl font-bold tracking-tight text-white">
          Fud Sniff
        </h1>
      </Link>
      <div className="mt-30 w-full max-w-7xl mx-auto flex flex-col gap-8 px-4 sm:px-8 md:px-16 z-100">
        {error && (
          <div className="bg-red-900 border border-red-500 text-red-200 p-4 rounded-xl">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 flex flex-col gap-6">
            <div className="flex-1 min-h-0 flex flex-col">
                <h3 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                <PawPrint className="w-5" />
                Recent Social Signals
                </h3>

              <div className="flex-1 overflow-y-auto pr-1 space-y-3">
                {!signals ? (
                  <div className="text-white/60 italic">
                    Unable to load signal feed.
                  </div>
                ) : signals.length === 0 ? (
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
                      Telegram bots haven't sniffed any signal yet.
                    </p>
                  </div>
                ) : (
                  [...signals].reverse().map((sig) => {
                    const icon =
                      sig.signal_type === "BUY" ? (
                        <TrendingUp className="w-5 h-5 text-green-400" />
                      ) : sig.signal_type === "SHORT" ? (
                        <TrendingDown className="w-5 h-5 text-red-400" />
                      ) : (
                        <AlertCircle className="w-5 h-5 text-yellow-400" />
                      );

                    const confidence = Math.round(sig.confidence * 100);

                    return (
                      <div
                        key={sig.id}
                        className="bg-zinc-900 border border-white/40 p-4 rounded-2xl shadow-sm text-left text-gray-100 transition hover:shadow-md"
                      >
                        <div className="flex justify-between items-center mb-2">
                          <div className="flex gap-3 items-center">
                            <div className="p-1 rounded-full bg-zinc-800">
                              {icon}
                            </div>
                            <div>
                              <span className="text-lg font-bold">
                                {sig.signal_type}
                              </span>
                              {sig.tokens_mentioned?.length > 0 && (
                                <span className="ml-2 text-sm text-gray-400">
                                  (${sig.tokens_mentioned[0]})
                                </span>
                              )}
                            </div>
                          </div>
                          <div className="text-right">
                            <div
                              className={`text-sm font-semibold ${getConfidenceColor(
                                sig.confidence
                              )}`}
                            >
                              {confidence}%
                            </div>
                            <div className="text-xs text-gray-500">
                              Confidence
                            </div>
                          </div>
                        </div>
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between flex-wrap gap-2">
                            <p className="text-white/70 truncate w-full sm:w-2/3">
                              <strong>Message:</strong> {sig.message_text}
                            </p>
                            <p className="text-white/70 truncate">
                              <strong>Source:</strong> @{sig.source_channel}
                            </p>
                          </div>

                          {sig.reasoning && (
                            <p className="text-sm text-gray-300 leading-relaxed">
                              {sig.reasoning}
                            </p>
                          )}

                          <div className="text-gray-600 tracking-wide">
                            {new Date(sig.timestamp).toLocaleString()}
                          </div>
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            </div>
          </div>

          <div className="flex flex-col gap-6">
            <div className="bg-black/20 p-4 rounded-xl text-center border border-white/10">
              <h2 className="text-xl font-semibold text-white mb-4 flex items-center">
                Sniffing Status
                <span
                  className={`inline-block w-2.5 h-2.5 rounded-full ml-2 ${
                    status?.is_running
                      ? "bg-green-400 shadow-md"
                      : "bg-red-400 shadow-md"
                  }`}
                  title={status?.is_running ? "Active" : "Inactive"}
                ></span>
              </h2>
              <div className="flex flex-col space-y-6 min-h-0">
                <div className="grid grid-cols-2 gap-4">
                  {[
                    {
                      label: "Monitoring",
                      value: status?.is_running ? "active" : "inactive",
                      color: status?.is_running
                        ? "text-green-400"
                        : "text-red-400",
                    },
                    {
                      label: "Total Signals",
                      value: status?.total_signals ?? 0,
                      color: "text-purple-300",
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
              </div>

              <div className="flex items-center justify-between gap-3 mt-4 mb-2">
                <button
                  onClick={
                    status?.is_running ? stopMonitoring : startMonitoring
                  }
                  disabled={loading}
                  className={`flex-1 font-bold py-1.5 rounded-lg hover:opacity-90 disabled:opacity-50 hover:cursor-pointer ${
                    status?.is_running
                      ? "bg-gradient-to-r from-red-400 to-red-600 text-white"
                      : "bg-gradient-to-r from-green-400 to-green-600 text-black"
                  }`}
                >
                  {loading
                    ? status?.is_running
                      ? "Stopping..."
                      : "Starting..."
                    : status?.is_running
                    ? "Stop Monitoring"
                    : "Start Monitoring"}
                </button>

                <button
                  onClick={() => {
                    fetchSignals();
                    fetchStats();
                    fetchStatus();
                  }}
                  className="ml-2 p-2 rounded-lg bg-zinc-800 text-white/70 hover:text-white hover:bg-zinc-700 transition hover:cursor-pointer"
                  title="Refresh"
                >
                  <RefreshCw className="w-5 h-5" />
                </button>
              </div>
            </div>

            <div className="bg-black/20 p-4 rounded-xl border border-white/10">
              <h2 className="text-xl font-semibold text-white mb-4">
                Signal Breakdown
              </h2>

              {stats?.by_type && Object.keys(stats.by_type).length > 0 ? (
                <div className="grid grid-cols-2 gap-4 mb-2">
                  {[
                    {
                      label: "Buy",
                      count: stats.by_type.BUY ?? 0,
                      color: "text-green-400",
                    },
                    {
                      label: "Short",
                      count: stats.by_type.SHORT ?? 0,
                      color: "text-red-400",
                    },
                  ].map((item, idx) => (
                    <div
                      key={idx}
                      className="bg-black/20 p-4 rounded-xl text-center border border-white/10"
                    >
                      <div className={`${item.color} text-2xl font-bold`}>
                        {item.count}
                      </div>
                      <div className="text-sm text-white/60">{item.label}</div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-white/60">No signals yet.</p>
              )}
            </div>

            {stats?.by_token && Object.keys(stats.by_token).length > 0 && (
              <div className="bg-black/20 border border-white/10 rounded-lg p-5">
                <h2 className="text-xl font-semibold mt-1 mb-5">
                  Most Mentioned Tokens
                </h2>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(stats.by_token)
                    .slice(0, 10)
                    .map(([token, count]) => (
                      <span
                        key={token}
                        className="bg-blue-700 text-sm px-3 py-1 rounded-md font-medium"
                      >
                        ${token} ({count})
                      </span>
                    ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {toast && (
        <Toast
          message={toast.message}
          type={toast.type as "success" | "error" | "info" | "stop"}
          onClose={() => setToast(null)}
        />
      )}
    </div>
  );
}
