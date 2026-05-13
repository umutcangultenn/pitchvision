import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "PitchVision Lite",
  description: "Video tabanlı maç analizi ve oyuncu gelişim platformu",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="tr">
      <body className="antialiased min-h-screen bg-bg text-text">{children}</body>
    </html>
  );
}
