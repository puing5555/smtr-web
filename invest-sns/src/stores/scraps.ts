import { create } from 'zustand';

export interface Scrap {
  id: string;
  signalId: number;
  stock: string;
  stockName: string;
  influencer: string;
  signalType: string;
  content: string;
  memo: string;
  videoDate: string;
  createdAt: string;
}

export interface Report {
  id: string;
  signalId: number;
  stock: string;
  stockName: string;
  influencer: string;
  signalType: string;
  reason: string; // 'signal_error' | 'content_error' | 'other'
  detail: string;
  status: 'pending' | 'reviewed' | 'rejected';
  createdAt: string;
}

interface ScrapsState {
  scraps: Scrap[];
  reports: Report[];
  watchlistStocks: { ticker: string; name: string; addedAt: string }[];
  watchlistInfluencers: { id: string; name: string; addedAt: string }[];

  loadFromStorage: () => void;
  addScrap: (scrap: Omit<Scrap, 'id' | 'createdAt'>) => void;
  updateScrapMemo: (id: string, memo: string) => void;
  removeScrap: (id: string) => void;
  isScraped: (signalId: number) => boolean;
  getScrapBySignalId: (signalId: number) => Scrap | undefined;

  addReport: (report: Omit<Report, 'id' | 'createdAt' | 'status'>) => void;
  updateReportStatus: (id: string, status: Report['status']) => void;

  addWatchlistStock: (ticker: string, name: string) => void;
  removeWatchlistStock: (ticker: string) => void;
  addWatchlistInfluencer: (id: string, name: string) => void;
  removeWatchlistInfluencer: (id: string) => void;
}

const STORAGE_KEYS = {
  scraps: 'smtr_scraps',
  reports: 'smtr_reports',
  watchlistStocks: 'smtr_watchlist_stocks',
  watchlistInfluencers: 'smtr_watchlist_influencers',
};

function saveToStorage(key: string, data: unknown) {
  if (typeof window !== 'undefined') {
    localStorage.setItem(key, JSON.stringify(data));
  }
}

function loadFromStorageRaw<T>(key: string, fallback: T): T {
  if (typeof window === 'undefined') return fallback;
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch {
    return fallback;
  }
}

export const useScrapsStore = create<ScrapsState>((set, get) => ({
  scraps: [],
  reports: [],
  watchlistStocks: [],
  watchlistInfluencers: [],

  loadFromStorage: () => {
    set({
      scraps: loadFromStorageRaw(STORAGE_KEYS.scraps, []),
      reports: loadFromStorageRaw(STORAGE_KEYS.reports, []),
      watchlistStocks: loadFromStorageRaw(STORAGE_KEYS.watchlistStocks, []),
      watchlistInfluencers: loadFromStorageRaw(STORAGE_KEYS.watchlistInfluencers, []),
    });
  },

  addScrap: (scrap) => {
    const newScrap: Scrap = {
      ...scrap,
      id: `scrap_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`,
      createdAt: new Date().toISOString(),
    };
    const updated = [newScrap, ...get().scraps];
    set({ scraps: updated });
    saveToStorage(STORAGE_KEYS.scraps, updated);

    // 관심종목 자동 추가
    const { watchlistStocks, addWatchlistStock } = get();
    if (!watchlistStocks.find(s => s.ticker === scrap.stock)) {
      addWatchlistStock(scrap.stock, scrap.stockName);
    }
    // 관심인플루언서 자동 추가
    const { watchlistInfluencers, addWatchlistInfluencer } = get();
    if (!watchlistInfluencers.find(i => i.name === scrap.influencer)) {
      addWatchlistInfluencer(scrap.influencer, scrap.influencer);
    }
  },

  updateScrapMemo: (id, memo) => {
    const updated = get().scraps.map(s => s.id === id ? { ...s, memo } : s);
    set({ scraps: updated });
    saveToStorage(STORAGE_KEYS.scraps, updated);
  },

  removeScrap: (id) => {
    const updated = get().scraps.filter(s => s.id !== id);
    set({ scraps: updated });
    saveToStorage(STORAGE_KEYS.scraps, updated);
  },

  isScraped: (signalId) => get().scraps.some(s => s.signalId === signalId),

  getScrapBySignalId: (signalId) => get().scraps.find(s => s.signalId === signalId),

  addReport: (report) => {
    const newReport: Report = {
      ...report,
      id: `report_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`,
      status: 'pending',
      createdAt: new Date().toISOString(),
    };
    const updated = [newReport, ...get().reports];
    set({ reports: updated });
    saveToStorage(STORAGE_KEYS.reports, updated);
  },

  updateReportStatus: (id, status) => {
    const updated = get().reports.map(r => r.id === id ? { ...r, status } : r);
    set({ reports: updated });
    saveToStorage(STORAGE_KEYS.reports, updated);
  },

  addWatchlistStock: (ticker, name) => {
    const updated = [...get().watchlistStocks, { ticker, name, addedAt: new Date().toISOString() }];
    set({ watchlistStocks: updated });
    saveToStorage(STORAGE_KEYS.watchlistStocks, updated);
  },

  removeWatchlistStock: (ticker) => {
    const updated = get().watchlistStocks.filter(s => s.ticker !== ticker);
    set({ watchlistStocks: updated });
    saveToStorage(STORAGE_KEYS.watchlistStocks, updated);
  },

  addWatchlistInfluencer: (id, name) => {
    const updated = [...get().watchlistInfluencers, { id, name, addedAt: new Date().toISOString() }];
    set({ watchlistInfluencers: updated });
    saveToStorage(STORAGE_KEYS.watchlistInfluencers, updated);
  },

  removeWatchlistInfluencer: (id) => {
    const updated = get().watchlistInfluencers.filter(i => i.id !== id);
    set({ watchlistInfluencers: updated });
    saveToStorage(STORAGE_KEYS.watchlistInfluencers, updated);
  },
}));
