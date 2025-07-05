// layout.tsx
import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Footer from "@/app/components/footer";
import Navigation from "@/app/components/Navigation";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Fud Sniff",
  description:
    "FudSniff is an AI-powered trading signal agent for real-time market sentiment analysis.",
  icons: {
    icon: "/fudsniff.png",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased h-full`}
      >
        <div className="flex flex-col h-full justify-between">
          <Navigation />
          <main className="flex-1 overflow-y-auto flex items-center justify-center px-6 sm:px-12">
            {children}
          </main>
          <Footer />
        </div>
      </body>
    </html>
  );
}
