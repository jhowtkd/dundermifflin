import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Dunder Mifflin - Sistema Multi-Agente",
  description: "6 AI Agents operando autonomamente",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR">
      <body className="bg-gray-900 text-white antialiased">
        {children}
      </body>
    </html>
  );
}
