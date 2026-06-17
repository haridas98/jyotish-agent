import type { Metadata, Viewport } from "next";
import "./globals.css";
import "./clean-ui.css";
import "./clean-ui-final.css";

export const metadata: Metadata = {
  title: "Веда Джйотиш",
  description: "Карты джйотиш с расчётами и ссылками на источники.",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ru">
      <body>{children}</body>
    </html>
  );
}
