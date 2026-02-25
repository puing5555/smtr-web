'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'

const navigation = [
  { name: '시그널', href: '/', icon: '📡' },
  { name: '공시', href: '/disclosure', icon: '📋' },
  { name: '피드', href: '/feed', icon: '🏠' },
  { name: '인플루언서', href: '/influencer', icon: '👤' },
  { name: 'MY', href: '/my', icon: '👤' },
]

export default function BottomNav() {
  const pathname = usePathname()

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-[#1a1a2e] border-t border-gray-700 z-50">
      <div className="max-w-[480px] mx-auto px-2 py-2">
        <div className="flex items-center justify-around">
          {navigation.map((item) => {
            const isActive = pathname === item.href
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`flex flex-col items-center gap-1 px-3 py-2 rounded-lg transition-colors ${
                  isActive 
                    ? 'text-[#00d4aa] bg-[#00d4aa]/10' 
                    : 'text-gray-400 hover:text-gray-300'
                }`}
              >
                <span className="text-xl">{item.icon}</span>
                <span className="text-xs font-medium">{item.name}</span>
              </Link>
            )
          })}
        </div>
      </div>
    </nav>
  )
}