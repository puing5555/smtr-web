'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  Home, 
  TrendingUp, 
  Bell, 
  Bot, 
  Star, 
  Newspaper, 
  Crown, 
  User,
  Menu,
  X,
  Search,
  Users
} from 'lucide-react';

const navigation = [
  { name: '피드', href: '/feed', icon: Home },
  { name: '시그널', href: '/signals', icon: TrendingUp },
  { name: '인플루언서', href: '/influencers', icon: Users },
  { name: '알림', href: '/alerts', icon: Bell },
  { name: 'AI봇', href: '/bots', icon: Bot },
  { name: '관심종목', href: '/stocks', icon: Star },
  { name: '뉴스', href: '/news', icon: Newspaper },
  { name: '프리미엄', href: '/premium', icon: Crown },
  { name: '프로필', href: '/profile', icon: User },
];

export default function MainLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const pathname = usePathname();

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Desktop Sidebar */}
      <div className="hidden lg:flex lg:flex-col lg:w-64 lg:fixed lg:inset-y-0">
        <div className="flex flex-col flex-grow pt-5 pb-4 overflow-y-auto bg-white border-r border-gray-200">
          {/* Logo */}
          <div className="flex items-center flex-shrink-0 px-4">
            <Link href="/feed" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold text-gray-900">투자SNS</span>
            </Link>
          </div>

          {/* Navigation */}
          <nav className="mt-8 flex-grow flex flex-col">
            <div className="px-2 space-y-1">
              {navigation.map((item) => {
                const isActive = pathname === item.href;
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors ${
                      isActive
                        ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-700'
                        : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                    }`}
                  >
                    <item.icon
                      className={`mr-3 h-5 w-5 transition-colors ${
                        isActive ? 'text-blue-500' : 'text-gray-400 group-hover:text-gray-500'
                      }`}
                    />
                    {item.name}
                  </Link>
                );
              })}
            </div>
          </nav>

          {/* User Profile */}
          <div className="flex-shrink-0 flex border-t border-gray-200 p-4">
            <div className="flex items-center w-full">
              <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                <User className="w-4 h-4 text-gray-600" />
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-700">사용자</p>
                <p className="text-xs text-gray-500">@username</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      <div className="lg:hidden">
        {isMobileMenuOpen && (
          <div className="fixed inset-0 flex z-40">
            <div className="fixed inset-0 bg-gray-600 bg-opacity-75" onClick={() => setIsMobileMenuOpen(false)} />
            
            <div className="relative flex-1 flex flex-col max-w-xs w-full pt-5 pb-4 bg-white">
              <div className="absolute top-0 right-0 -mr-12 pt-2">
                <button
                  type="button"
                  className="ml-1 flex items-center justify-center h-10 w-10 rounded-full focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  <X className="h-6 w-6 text-white" />
                </button>
              </div>

              {/* Mobile Logo */}
              <div className="flex items-center flex-shrink-0 px-4">
                <Link href="/feed" className="flex items-center space-x-2">
                  <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                    <TrendingUp className="w-5 h-5 text-white" />
                  </div>
                  <span className="text-xl font-bold text-gray-900">투자SNS</span>
                </Link>
              </div>

              {/* Mobile Navigation */}
              <nav className="mt-8 flex-grow flex flex-col">
                <div className="px-2 space-y-1">
                  {navigation.map((item) => {
                    const isActive = pathname === item.href;
                    return (
                      <Link
                        key={item.name}
                        href={item.href}
                        onClick={() => setIsMobileMenuOpen(false)}
                        className={`group flex items-center px-2 py-2 text-base font-medium rounded-md transition-colors ${
                          isActive
                            ? 'bg-blue-50 text-blue-700'
                            : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                        }`}
                      >
                        <item.icon
                          className={`mr-4 h-6 w-6 transition-colors ${
                            isActive ? 'text-blue-500' : 'text-gray-400 group-hover:text-gray-500'
                          }`}
                        />
                        {item.name}
                      </Link>
                    );
                  })}
                </div>
              </nav>
            </div>
          </div>
        )}
      </div>

      {/* Main content */}
      <div className="lg:pl-64 flex flex-col w-0 flex-1">
        {/* Top bar - mobile only (hamburger menu) */}
        <div className="relative z-10 flex-shrink-0 flex h-12 bg-white lg:hidden">
          <button
            type="button"
            className="px-4 text-gray-400 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-purple-500"
            onClick={() => setIsMobileMenuOpen(true)}
          >
            <Menu className="h-6 w-6" />
          </button>
        </div>

        {/* Page content */}
        <main className="flex-1 relative overflow-y-auto focus:outline-none">
          <div className="py-6">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 md:px-8">
              {children}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}