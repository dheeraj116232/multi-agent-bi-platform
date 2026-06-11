import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "BI Platform — Multi-Agent Intelligence",
  description: "Enterprise-grade AI analytics. Upload your data, get executive insights in minutes.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
