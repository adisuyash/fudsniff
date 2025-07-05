"use client";

import { useEffect } from "react";

interface ToastProps {
  message: string;
  type?: "success" | "error" | "info" | "stop";
  onClose: () => void;
}

export default function Toast({ message, type = "info", onClose }: ToastProps) {
  useEffect(() => {
    const timeout = setTimeout(onClose, 3000);
    return () => clearTimeout(timeout);
  }, [onClose]);

  const bg =
    type === "success"
      ? "bg-green-700"
      : type === "error"
      ? "bg-red-700"
      : type === "stop"
      ? "bg-red-900"
      : "bg-blue-700";

  return (
    <div
      className={`fixed bottom-4 right-4 px-4 py-3 rounded-xl shadow-lg text-white z-50 ${bg}`}
    >
      {message}
    </div>
  );
}
