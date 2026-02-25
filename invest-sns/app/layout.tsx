import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import Header from '@/components/Header'
import BottomNav from '@/components/BottomNav'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: '투자SNS',
  description: 'Investment Social Network Service',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ko">
      <body className={`${inter.className} bg-[#0a0a0a] text-white min-h-screen`}>
        <div className="max-w-[480px] mx-auto min-h-screen bg-[#0a0a0a] relative">
          <Header />
          <main className="pt-16 pb-20 min-h-screen">
            {children}
          </main>
          <BottomNav />
        </div>
      </body>
    </html>
  )
}