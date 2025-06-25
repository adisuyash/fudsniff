"use client";

import Image from "next/image";
import { useEffect, useState } from "react";

interface PawprintProps {
  id: number;
  x: number;
  y: number;
  rotation: number;
  scale: number;
  opacity: number;
  delay: number;
}

export default function Paws() {
  const [pawprints, setPawprints] = useState<PawprintProps[]>([]);

  useEffect(() => {
    // Generate pawprint positions for background pattern
    const generatePawprints = (): PawprintProps[] => {
      return Array.from({ length: 30 }, (_, i) => ({
        id: i,
        x: Math.random() * 100,
        y: Math.random() * 100,
        rotation: Math.random() * 360,
        scale: 0.2 + Math.random() * 0.3,
        opacity: 0.03 + Math.random() * 0.07,
        delay: Math.random() * 4,
      }));
    };

    setPawprints(generatePawprints());
  }, []);

  return (
    <>
      {/* Fixed Background Container */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
        {/* Random Scattered Pawprints */}
        {pawprints.map((paw) => (
          <div
            key={paw.id}
            className="absolute animate-pulse"
            style={{
              left: `${paw.x}%`,
              top: `${paw.y}%`,
              transform: `rotate(${paw.rotation}deg) scale(${paw.scale})`,
              opacity: paw.opacity,
              animationDelay: `${paw.delay}s`,
              animationDuration: "6s",
            }}
          >
            <Image
              src="/pawprint.png"
              alt=""
              width={80}
              height={80}
              className="w-16 h-16 filter grayscale"
              draggable={false}
            />
          </div>
        ))}

        {/* Curved Pathway of Pawprints */}
        <div className="absolute inset-0">
          {Array.from({ length: 15 }, (_, i) => {
            const progress = i / 14;
            const pathX = 5 + progress * 90;
            const pathY = 30 + Math.sin(progress * Math.PI * 2) * 20;

            return (
              <div
                key={`path-${i}`}
                className="absolute animate-bounce"
                style={{
                  left: `${pathX}%`,
                  top: `${pathY}%`,
                  animationDelay: `${i * 0.3}s`,
                  animationDuration: "4s",
                  transform: `rotate(${progress * 180 - 90}deg)`,
                }}
              >
                <Image
                  src="/pawprint.png"
                  alt=""
                  width={50}
                  height={50}
                  className="w-10 h-10 opacity-8 filter grayscale"
                  draggable={false}
                />
              </div>
            );
          })}
        </div>

        {/* Corner Accent Pawprints */}
        <div className="absolute top-10 left-10 animate-float opacity-5">
          <Image
            src="/pawprint.png"
            alt=""
            width={120}
            height={120}
            className="w-20 h-20 -rotate-12 filter grayscale"
            draggable={false}
          />
        </div>

        <div
          className="absolute top-20 right-16 animate-float opacity-5"
          style={{ animationDelay: "2s" }}
        >
          <Image
            src="/pawprint.png"
            alt=""
            width={100}
            height={100}
            className="w-16 h-16 rotate-45 filter grayscale"
            draggable={false}
          />
        </div>

        <div
          className="absolute bottom-20 left-20 animate-float opacity-5"
          style={{ animationDelay: "1s" }}
        >
          <Image
            src="/pawprint.png"
            alt=""
            width={140}
            height={140}
            className="w-24 h-24 rotate-12 filter grayscale"
            draggable={false}
          />
        </div>

        <div
          className="absolute bottom-16 right-12 animate-float opacity-5"
          style={{ animationDelay: "3s" }}
        >
          <Image
            src="/pawprint.png"
            alt=""
            width={110}
            height={110}
            className="w-18 h-18 -rotate-30 filter grayscale"
            draggable={false}
          />
        </div>

        {/* Subtle Moving Trail */}
        <div className="absolute inset-0">
          {Array.from({ length: 8 }, (_, i) => (
            <div
              key={`trail-${i}`}
              className="absolute animate-ping"
              style={{
                left: `${15 + i * 10}%`,
                top: `${60 + Math.cos(i * 0.5) * 10}%`,
                animationDelay: `${i * 0.5}s`,
                animationDuration: "8s",
              }}
            >
              <Image
                src="/pawprint.png"
                alt=""
                width={40}
                height={40}
                className="w-8 h-8 opacity-3 filter grayscale"
                draggable={false}
              />
            </div>
          ))}
        </div>
      </div>

      {/* Custom CSS for float animation */}
      <style jsx global>{`
        @keyframes float {
          0%,
          100% {
            transform: translateY(0px) rotate(var(--rotation, 0deg));
          }
          50% {
            transform: translateY(-10px) rotate(var(--rotation, 0deg));
          }
        }

        .animate-float {
          animation: float 6s ease-in-out infinite;
        }
      `}</style>
    </>
  );
}
