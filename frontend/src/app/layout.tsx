import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Jyotish Agent",
  description: "Gaudiya Vaishnava jyotish calculations with cited sources.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

