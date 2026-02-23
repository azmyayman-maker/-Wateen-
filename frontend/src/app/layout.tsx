import type { Metadata } from "next";
import { Cairo, Inter } from "next/font/google";
import "./globals.css";
import { LanguageProvider } from "@/lib/i18n";
import { AuthProvider } from "@/providers/AuthProvider";

const cairo = Cairo({
  subsets: ["arabic", "latin"],
  display: "swap",
  variable: "--font-cairo",
});

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "wateen",
  description: "منصة وتين للرعاية الصحية — Wateen Healthcare Platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ar" dir="rtl" className={`${cairo.variable} ${inter.variable}`} suppressHydrationWarning>
      <body className="font-sans antialiased bg-background text-text-primary select-none" suppressHydrationWarning>
        <AuthProvider>
          <LanguageProvider>
            <a href="#main-content" className="skip-link">
              Skip to main content
            </a>
            {children}
          </LanguageProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
