import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Ci Moment v2",
  description: "A personal moment signal and symbolic checkpoint.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
