import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { Navbar } from "@/components/navbar";
import { ConditionalFooter } from "@/components/conditional-footer";
import "./globals.css";
import QueryProvider from "@/components/query-provider";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Lotara - AI Travel Planner",
  description:
    "Personalized Vietnam travel planning powered by AI and your travel personality",
};

export const viewport = {
  themeColor: "#ae7d8c",
  userScalable: true,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <QueryProvider>
          <Navbar />
          {children}
          <ConditionalFooter />
        </QueryProvider>
      </body>
    </html>
  );
}
