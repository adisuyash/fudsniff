// app/components/SignalCard.tsx
"use client";

import { TrendingUp, TrendingDown, AlertCircle } from "lucide-react";

export function SignalCard({ signal, confidence, reasoning, coin, timestamp }) {
  const color =
    {
      BUY: "green",
      SHORT: "red",
      HOLD: "yellow",
    }[signal] || "gray";

  const icon = {
    BUY: <TrendingUp className="w-5 h-5" />,
    SHORT: <TrendingDown className="w-5 h-5" />,
    HOLD: <AlertCircle className="w-5 h-5" />,
  }[signal];

  return (
    <div
      className={`border-2 p-4 rounded-lg bg-${color}-50 border-${color}-200`}
    >
      <div className="flex justify-between items-center mb-2">
        <div className="flex gap-2 items-center">
          {icon}
          <span className="font-bold text-lg">{signal}</span>
          <span className="text-sm opacity-70">({coin})</span>
        </div>
        <div className="text-right">
          <div className="font-semibold">{confidence}%</div>
          <div className="text-xs opacity-70">Confidence</div>
        </div>
      </div>
      <p className="text-sm mb-1">{reasoning}</p>
      <div className="text-xs opacity-50">
        {new Date(timestamp).toLocaleString()}
      </div>
    </div>
  );
}
