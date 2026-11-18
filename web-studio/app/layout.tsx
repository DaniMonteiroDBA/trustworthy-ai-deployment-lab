import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Value & Adoption Studio — Dani Monteiro",
  description: "Private, synthetic reference lab for evidence-first AI adoption decisions.",
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
