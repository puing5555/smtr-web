import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// Date formatting utilities
export function formatTimeAgo(dateString: string): string {
  const now = new Date();
  const date = new Date(dateString);
  const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
  
  if (diffInMinutes < 1) return '방금 전';
  if (diffInMinutes < 60) return `${diffInMinutes}분 전`;
  if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}시간 전`;
  if (diffInMinutes < 10080) return `${Math.floor(diffInMinutes / 1440)}일 전`;
  
  return date.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
}

export function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

// Number formatting utilities
export function formatNumber(num: number): string {
  if (num >= 1e9) return (num / 1e9).toFixed(1) + '조';
  if (num >= 1e8) return (num / 1e8).toFixed(1) + '억';
  if (num >= 1e4) return (num / 1e4).toFixed(1) + '만';
  return num.toLocaleString('ko-KR');
}

export function formatCurrency(amount: number, currency: string = 'KRW'): string {
  const formatted = amount.toLocaleString('ko-KR');
  switch (currency) {
    case 'KRW':
      return `${formatted}원`;
    case 'USD':
      return `$${formatted}`;
    default:
      return formatted;
  }
}

export function formatPercentage(value: number, decimals: number = 2): string {
  return `${value >= 0 ? '+' : ''}${value.toFixed(decimals)}%`;
}

// Stock utilities
export function getStockChangeColor(change: number): string {
  if (change > 0) return 'text-red-600'; // 상승 - 빨간색 (한국 주식 관례)
  if (change < 0) return 'text-blue-600'; // 하락 - 파란색
  return 'text-gray-600'; // 보합 - 회색
}

export function getMarketName(market: string): string {
  switch (market) {
    case 'KOSPI':
      return '코스피';
    case 'KOSDAQ':
      return '코스닥';
    case 'NYSE':
      return '뉴욕증권거래소';
    case 'NASDAQ':
      return '나스닥';
    default:
      return market;
  }
}

// URL utilities
export function createShareUrl(postId: string): string {
  const baseUrl = typeof window !== 'undefined' ? window.location.origin : '';
  return `${baseUrl}/post/${postId}`;
}

export function isValidUrl(string: string): boolean {
  try {
    new URL(string);
    return true;
  } catch (_) {
    return false;
  }
}

// Text utilities
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength - 3) + '...';
}

export function extractHashtags(text: string): string[] {
  const hashtags = text.match(/#[\w가-힣]+/g);
  return hashtags ? hashtags.map(tag => tag.slice(1)) : [];
}

export function extractMentions(text: string): string[] {
  const mentions = text.match(/@[\w]+/g);
  return mentions ? mentions.map(mention => mention.slice(1)) : [];
}

export function extractStockSymbols(text: string): string[] {
  const symbols = text.match(/\$[\w]+/g);
  return symbols ? symbols.map(symbol => symbol.slice(1)) : [];
}

// Validation utilities
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

export function isValidUsername(username: string): boolean {
  const usernameRegex = /^[a-zA-Z0-9_]{3,20}$/;
  return usernameRegex.test(username);
}

export function isValidPassword(password: string): boolean {
  return password.length >= 8;
}

// Array utilities
export function uniqueBy<T>(array: T[], key: keyof T): T[] {
  return array.filter((item, index, self) => 
    index === self.findIndex(t => t[key] === item[key])
  );
}

export function groupBy<T>(array: T[], key: keyof T): Record<string, T[]> {
  return array.reduce((groups, item) => {
    const group = String(item[key]);
    groups[group] = groups[group] || [];
    groups[group].push(item);
    return groups;
  }, {} as Record<string, T[]>);
}

// Local storage utilities
export function setLocalStorage(key: string, value: any): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem(key, JSON.stringify(value));
  }
}

export function getLocalStorage<T>(key: string, defaultValue: T): T {
  if (typeof window !== 'undefined') {
    const item = localStorage.getItem(key);
    if (item) {
      try {
        return JSON.parse(item);
      } catch (e) {
        console.error(`Error parsing localStorage item ${key}:`, e);
      }
    }
  }
  return defaultValue;
}

export function removeLocalStorage(key: string): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(key);
  }
}

// Debounce utility
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout;
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}