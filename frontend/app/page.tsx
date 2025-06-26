"use client";
import { useEffect, useState } from "react";
import Image from "next/image";
import Paws from "./components/paws";

export default function Home() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <div className="flex flex-col items-center text-center gap-8 font-[family-name:var(--font-geist-mono)] w-full max-w-3xl text-gray-100">
      {mounted && <Paws />}{" "}
      <div className="flex items-center space-x-4 sm:space-x-6">
        <div className="relative group"> 
          <Image
            src="/fudsniff.png"
            alt="FudSniff logo"
            width={64}
            height={64}
            className="h-12 w-12 sm:h-16 sm:w-16 transition-transform duration-200 group-hover:scale-110"
            priority
          />
          <div className="absolute inset-0 bg-white opacity-0 group-hover:opacity-20 rounded-full blur-md transition-opacity duration-200 -z-10"></div>
        </div>
        <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold tracking-tight text-white">
          Fud Sniff
        </h1>
      </div>

      <p className="text-base sm:text-lg md:text-xl tracking-wide leading-relaxed text-gray-400 font-[family-name:var(--font-geist-sans)] max-w-2xl">
        sniffs real-time crypto sentiment and news to generate
        <br />
        high-confidence signals for market action.
      </p>

      <div className="flex flex-col items-center gap-3 mt-2">
        <button className="group relative overflow-hidden rounded-md border border-gray-600 px-6 py-3 text-sm sm:text-base text-gray-900 bg-white transition-all duration-300 font-medium">
          <code>sniffing on localhost @3000</code>
        </button>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
          <span className="text-xs sm:text-sm text-gray-500 font-[family-name:var(--font-geist-sans)] tracking-widest">
            Launching Soon!
          </span>
        </div>
      </div>
    </div>
  );
}
