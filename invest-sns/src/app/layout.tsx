import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "투자SNS - 스마트한 투자 소통 플랫폼",
  description: "인플루언서 투자 시그널, 실시간 토론, AI 분석까지 - 투자 결정을 도와주는 SNS",
  keywords: "투자, SNS, 주식, 인플루언서, 시그널, 분석, 커뮤니티",
  viewport: "width=device-width, initial-scale=1",
  themeColor: "#1f2937",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <body
        className={`${inter.variable} antialiased bg-gray-50 min-h-screen`}
      >
        <div className="flex flex-col min-h-screen">
          {children}
        </div>
      </body>
    </html>
  );
}