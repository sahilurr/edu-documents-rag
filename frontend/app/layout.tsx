import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Edu RAG — Research Assistant",
  description: "Grounded answers from your uploaded research documents.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
