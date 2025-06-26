// app/components/SignalCard.tsx
"use client";

import React from "react";
import { TrendingUp, TrendingDown, AlertCircle } from "lucide-react";
import { FC } from "react";

type SignalType = "BUY" | "SHORT" | "HOLD";

interface SignalCardProps {
  signal: SignalType;
  confidence: number;
  reasoning: string;
  coin: string;
  timestamp: string | number | Date;
}

export const SignalCard: FC<SignalCardProps> = ({
  signal,
  confidence,
  reasoning,
  coin,
  timestamp,
}) => {
  const colorMap: Record<SignalType, string> = {
    BUY: "green",
    SHORT: "red",
    HOLD: "yellow",
  };

  const iconMap: Record<SignalType, React.ReactElement> = {
    BUY: <TrendingUp className="w-5 h-5 text-green-400" />,
    SHORT: <TrendingDown className="w-5 h-5 text-red-400" />,
    HOLD: <AlertCircle className="w-5 h-5 text-yellow-400" />,
  };

  const color = colorMap[signal];
  const icon = iconMap[signal];

  return (
    <div
      className={`bg-zinc-900 border border-${color}-400/30 p-4 rounded-2xl shadow-sm text-left text-gray-100 transition hover:shadow-lg`}
    >
      <div className="flex justify-between items-center mb-2">
        <div className="flex gap-3 items-center">
          <div className="p-1 rounded-full bg-zinc-800">{icon}</div>
          <div>
            <span className="text-lg font-bold">{signal}</span>
            <span className="ml-2 text-sm text-gray-400">({coin})</span>
          </div>
        </div>
        <div className="text-right">
          <div className="text-sm font-semibold text-white">{confidence}%</div>
          <div className="text-xs text-gray-500">Confidence</div>
        </div>
      </div>

      <p className="text-sm text-gray-300 leading-relaxed mb-2">{reasoning}</p>

      <div className="text-xs text-gray-500 tracking-wide">
        {new Date(timestamp).toLocaleString()}
      </div>
    </div>
  );
};
