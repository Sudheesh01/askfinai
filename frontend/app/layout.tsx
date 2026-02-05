import "./globals.css";

import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Finance AI Research",
  description: "AI finance research app with live data.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
