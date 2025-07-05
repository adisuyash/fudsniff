"use client";

import Link from "next/link";

export default function Navigation() {
  return (
    <>
      <div
        style={{
          position: "fixed",
          top: "32px",
          left: 0,
          width: "100vw",
          display: "flex",
          justifyContent: "center",
          gap: "24px",
          zIndex: 100,
        }}
      >
        <Link
          href="/dashboard"
          style={{
            color: "#fff",
            textDecoration: "none",
            fontSize: "18px",
            border: "none",
            background: "none",
            padding: "8px 16px",
            cursor: "pointer",
          }}
        >
          Dashboard
        </Link>
        <Link
          href="/telegram-signals"
          style={{
            color: "#fff",
            textDecoration: "none",
            fontSize: "18px",
            border: "none",
            background: "none",
            padding: "8px 16px",
            cursor: "pointer",
          }}
        >
          Telegram Signals
        </Link>
      </div>
    </>
  );
}
