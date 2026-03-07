'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import {
  getUserStocks,
  addUserStock,
  updateUserStock,
  deleteUserStock,
} from '@/lib/api/user-stocks';
import {
  getUserWatchlist,
  addToWatchlist,
  updateWatchlistItem,
  removeFromWatchlist,
} from '@/lib/api/user-watchlist';
import type { Database } from '@/types/supabase';

type UserStock = Database['public']['Tables']['user_stocks']['Row'];
type UserWatchlist = Database['public']['Tables']['user_watchlist']['Row'];

type SellRecord = {
  id: string;
  stock_name: string;
  stock_code: string;
  quantity: number;
  sell_price: number;
  buy_price: number;
  sell_date: string;
  memo?: string;
};

type Tab = 'holdings' | 'watchlist' | 'sells';

// ─── 보유종목 모달 ────────────────────────────────────────────────────────────
function StockModal({
  isOpen,
  onClose,
  onSubmit,
  editStock,
}: {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: {
    stock_code: string;
    stock_name: string;
    market: string;
    quantity: number;
    avg_buy_price: number;
    notes?: string;
  }) => void;
  editStock?: UserStock | null;
}) {
  const [code, setCode] = useState('');
  const [name, setName] = useState('');
  const [market, setMarket] = useState('KOSPI');
  const [quantity, setQuantity] = useState('');
  const [price, setPrice] = useState('');
  const [buyDate, setBuyDate] = useState('');
  const [notes, setNotes] = useState('');

  useEffect(() => {
    if (editStock) {
      setCode(editStock.stock_code);
      setName(editStock.stock_name);
      setMarket(editStock.market);
      setQuantity(String(editStock.quantity));
      setPrice(String(editStock.avg_buy_price));
      setNotes(editStock.notes || '');
      setBuyDate('');
    } else {
      setCode('');
      setName('');
      setMarket('KOSPI');
      setQuantity('');
      setPrice('');
      setBuyDate('');
      setNotes('');
    }
  }, [editStock, isOpen]);

  if (!isOpen) return null;

  const handleSubmit = () => {
    if (!code || !name || !quantity || !price) {
      alert('종목코드, 종목명, 수량, 매수가는 필수 입력 항목입니다.');
      return;
    }
    onSubmit({
      stock_code: code,
      stock_name: name,
      market,
      quantity: Number(quantity),
      avg_buy_price: Number(price),
      notes: notes || undefined,
    });
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 px-4">
      <div className="bg-white rounded-2xl p-6 w-full max-w-md max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-5">
          <h2 className="text-lg font-bold text-[#191f28]">{editStock ? '종목 수정' : '종목 추가'}</h2>
          <button onClick={onClose} className="text-[#8b95a1] text-xl">✕</button>
        </div>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-[#8b95a1] mb-1 block">종목코드 (티커)</label>
              <input
                value={code}
                onChange={e => setCode(e.target.value)}
                disabled={!!editStock}
                className="w-full px-3 py-2.5 border border-[#e8e8e8] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#3182f6] disabled:bg-gray-50"
                placeholder="005930"
              />
            </div>
            <div>
              <label className="text-xs text-[#8b95a1] mb-1 block">종목명</label>
              <input
                value={name}
                onChange={e => setName(e.target.value)}
                disabled={!!editStock}
                className="w-full px-3 py-2.5 border border-[#e8e8e8] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#3182f6] disabled:bg-gray-50"
                placeholder="삼성전자"
              />
            </div>
          </div>
          <div>
            <label className="text-xs text-[#8b95a1] mb-1 block">시장</label>
            <select
              value={market}
              onChange={e => setMarket(e.target.value)}
              className="w-full px-3 py-2.5 border border-[#e8e8e8] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#3182f6]"
            >
              <option value="KOSPI">KOSPI</option>
              <option value="KOSDAQ">KOSDAQ</option>
              <option value="NASDAQ">NASDAQ</option>
              <option value="NYSE">NYSE</option>
            </select>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-[#8b95a1] mb-1 block">수량</label>
              <input
                type="number"
                value={quantity}
                onChange={e => setQuantity(e.target.value)}
                className="w-full px-3 py-2.5 border border-[#e8e8e8] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#3182f6]"
                placeholder="100"
              />
            </div>
            <div>
              <label className="text-xs text-[#8b95a1] mb-1 block">매수가</label>
              <input
                type="number"
                value={price}
                onChange={e => setPrice(e.target.value)}
                className="w-full px-3 py-2.5 border border-[#e8e8e8] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#3182f6]"
                placeholder="70000"
              />
            </div>
          </div>
          <div>
            <label className="text-xs text-[#8b95a1] mb-1 block">매수일</label>
            <input
              type="date"
              value={buyDate}
              onChange={e => setBuyDate(e.target.value)}
              className="w-full px-3 py-2.5 border border-[#e8e8e8] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#3182f6]"
            />
          </div>
          <div>
            <label className="text-xs text-[#8b95a1] mb-1 block">메모</label>
            <textarea
              value={notes}
              onChange={e => setNotes(e.target.value)}
              className="w-full px-3 py-2.5 border border-[#e8e8e8] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#3182f6] resize-none"
              placeholder="투자 이유, 목표가 등 메모..."
              rows={3}
            />
          </div>
          <button
            onClick={handleSubmit}
            className="w-full py-3 bg-[#3182f6] text-white rounded-xl font-medium text-sm hover:bg-[#1b64da] transition-colors"
          >
            {editStock ? '수정하기' : '추가하기'}
          </button>
        </div>
      </div>
    </div>
  );
}

// ─── 관심종목 모달 ────────────────────────────────────────────────────────────
function WatchlistModal({
  isOpen,
  onClose,
  onSubmit,
  editItem,
}: {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: {
    stock_code: string;
    stock_name: string;
    market: string;
    alert_on_signals?: boolean;
    alert_price_target?: number;
    alert_price_type?: 'above' | 'below';
    notes?: string;
  }) => void;
  editItem?: UserWatchlist | null;
}) {
  const [code, setCode] = useState('');
  const [name, setName] = useState('');
  const [market, setMarket] = useState('KOSPI');
  const [alertSignals, setAlertSignals] = useState(true);
  const [alertPrice, setAlertPrice] = useState(false);
  const [targetPrice, setTargetPrice] = useState('');
  const [priceType, setPriceType] = useState<'above' | 'below'>('above');
  const [notes, setNotes] = useState('');

  useEffect(() => {
    if (isOpen) {
      if (editItem) {
        setCode(editItem.stock_code);
        setName(editItem.stock_name);
        setMarket(editItem.market);
        setAlertSignals(editItem.alert_on_signals ?? true);
        setTargetPrice(editItem.alert_price_target ? String(editItem.alert_price_target) : '');
        setPriceType((editItem.alert_price_type as 'above' | 'below') || 'above');
        setAlertPrice(!!editItem.alert_price_target);
        setNotes(editItem.notes || '');
      } else {
        setCode('');
        setName('');
        setMarket('KOSPI');
        setAlertSignals(true);
        setAlertPrice(false);
        setTargetPrice('');
        setPriceType('above');
        setNotes('');
      }
    }
  }, [editItem, isOpen]);

  if (!isOpen) return null;

  const handleSubmit = () => {
    if (!code || !name) {
      alert('종목코드와 종목명은 필수입니다.');
      return;
    }
    onSubmit({
      stock_code: code,
      stock_name: name,
      market,
      alert_on_signals: alertSignals,
      alert_price_target: alertPrice && targetPrice ? Number(targetPrice) : undefined,
      alert_price_type: alertPrice ? priceType : undefined,
      notes: notes || undefined,
    });
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 px-4">
      <div className="bg-white rounded-2xl p-6 w-full max-w-md max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-5">
          <h2 className="text-lg font-bold text-[#191f28]">{editItem ? '관심종목 수정' : '관심종목 추가'}</h2>
          <button onClick={onClose} className="text-[#8b95a1] text-xl">✕</button>
        </div>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-[#8b95a1] mb-1 block">종목코드 (티커)</label>
              <input
                value={code}
                onChange={e => setCode(e.target.value)}
                disabled={!!editItem}
                className="w-full px-3 py-2.5 border border-[#e8e8e8] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#3182f6] disabled:bg-gray-50"
                placeholder="005930"
              />
            </div>
            <div>
              <label className="text-xs text-[#8b95a1] mb-1 block">종목명</label>
              <input
                value={name}
                onChange={e => setName(e.target.value)}
                disabled={!!editItem}
                className="w-full px-3 py-2.5 border border-[#e8e8e8] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#3182f6] disabled:bg-gray-50"
                placeholder="삼성전자"
              />
            </div>
          </div>
          <div>
            <label className="text-xs text-[#8b95a1] mb-1 block">시장</label>
            <select
              value={market}
              onChange={e => setMarket(e.target.value)}
              className="w-full px-3 py-2.5 border border-[#e8e8e8] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#3182f6]"
            >
              <option value="KOSPI">KOSPI</option>
              <option value="KOSDAQ">KOSDAQ</option>
              <option value="NASDAQ">NASDAQ</option>
              <option value="NYSE">NYSE</option>
            </select>
          </div>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-[#f8f9fa] rounded-xl">
              <div>
                <div className="text-sm font-medium text-[#191f28]">시그널 알림</div>
                <div className="text-xs text-[#8b95a1]">AI 매매 시그널 발생 시 알림</div>
              </div>
              <button
                onClick={() => setAlertSignals(!alertSignals)}
                className={`w-12 h-6 rounded-full transition-colors ${alertSignals ? 'bg-[#3182f6]' : 'bg-[#e8e8e8]'}`}
              >
                <div className={`w-5 h-5 bg-white rounded-full shadow transition-transform ${alertSignals ? 'translate-x-6' : 'translate-x-0.5'}`} />
              </button>
            </div>
            <div className="flex items-center justify-between p-3 bg-[#f8f9fa] rounded-xl">
              <div>
                <div className="text-sm font-medium text-[#191f28]">가격 알림</div>
                <div className="text-xs text-[#8b95a1]">목표가 도달 시 알림</div>
              </div>
              <button
                onClick={() => setAlertPrice(!alertPrice)}
                className={`w-12 h-6 rounded-full transition-colors ${alertPrice ? 'bg-[#3182f6]' : 'bg-[#e8e8e8]'}`}
              >
                <div className={`w-5 h-5 bg-white rounded-full shadow transition-transform ${alertPrice ? 'translate-x-6' : 'translate-x-0.5'}`} />
              </button>
            </div>
          </div>
          {alertPrice && (
            <div>
              <label className="text-xs text-[#8b95a1] mb-1 block">관심가 (목표가)</label>
              <div className="flex gap-2">
                <select
                  value={priceType}
                  onChange={e => setPriceType(e.target.value as 'above' | 'below')}
                  className="px-3 py-2.5 border border-[#e8e8e8] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#3182f6]"
                >
                  <option value="above">이상</option>
                  <option value="below">이하</option>
                </select>
                <input
                  type="number"
                  value={targetPrice}
                  onChange={e => setTargetPrice(e.target.value)}
                  className="flex-1 px-3 py-2.5 border border-[#e8e8e8] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#3182f6]"
                  placeholder="70000"
                />
              </div>
            </div>
          )}
          <div>
            <label className="text-xs text-[#8b95a1] mb-1 block">메모</label>
            <textarea
              value={notes}
              onChange={e => setNotes(e.target.value)}
              className="w-full px-3 py-2.5 border border-[#e8e8e8] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#3182f6] resize-none"
              placeholder="관심 이유, 분석 메모..."
              rows={3}
            />
          </div>
          <button
            onClick={handleSubmit}
            className="w-full py-3 bg-[#3182f6] text-white rounded-xl font-medium text-sm hover:bg-[#1b64da] transition-colors"
          >
            {editItem ? '수정하기' : '추가하기'}
          </button>
        </div>
      </div>
    </div>
  );
}

// ─── 매도기록 모달 ────────────────────────────────────────────────────────────
function SellModal({
  isOpen,
  onClose,
  onSubmit,
}: {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: Omit<SellRecord, 'id'>) => void;
}) {
  const [stockName, setStockName] = useState('');
  const [stockCode, setStockCode] = useState('');
  const [quantity, setQuantity] = useState('');
  const [sellPrice, setSellPrice] = useState('');
  const [buyPrice, setBuyPrice] = useState('');
  const [sellDate, setSellDate] = useState('');
  const [memo, setMemo] = useState('');

  useEffect(() => {
    if (isOpen) {
      setStockName('');
      setStockCode('');
      setQuantity('');
      setSellPrice('');
      setBuyPrice('');
      setSellDate(new Date().toISOString().split('T')[0]);
      setMemo('');
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSubmit = () => {
    if (!stockName || !quantity || !sellPrice || !buyPrice || !sellDate) {
      alert('종목명, 수량, 매도가, 매수가, 매도일은 필수입니다.');
      return;
    }
    onSubmit({
      stock_name: stockName,
      stock_code: stockCode,
      quantity: Number(quantity),
      sell_price: Number(sellPrice),
      buy_price: Number(buyPrice),
      sell_date: sellDate,
      memo: memo || undefined,
    });
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 px-4">
      <div className="bg-white rounded-2xl p-6 w-full max-w-md max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-5">
          <h2 className="text-lg font-bold text-[#191f28]">매도 기록 추가</h2>
          <button onClick={onClose} className="text-[#8b95a1] text-xl">✕</button>
        </div>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-[#8b95a1] mb-1 block">종목명</label>
              <input
                value={stockName}
                onChange={e => setStockName(e.target.value)}
                className="w-full px-3 py-2.5 border border-[#e8e8e8] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#3182f6]"
                placeholder="삼성전자"
              />
            </div>
            <div>
              <label className="text-xs text-[#8b95a1] mb-1 block">티커 (선택)</label>
              <input
                value={stockCode}
                onChange={e => setStockCode(e.target.value)}
                className="w-full px-3 py-2.5 border border-[#e8e8e8] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#3182f6]"
                placeholder="005930"
              />
            </div>
          </div>
          <div>
            <label className="text-xs text-[#8b95a1] mb-1 block">수량</label>
            <input
              type="number"
              value={quantity}
              onChange={e => setQuantity(e.target.value)}
              className="w-full px-3 py-2.5 border border-[#e8e8e8] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#3182f6]"
              placeholder="100"
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-[#8b95a1] mb-1 block">매수가</label>
              <input
                type="number"
                value={buyPrice}
                onChange={e => setBuyPrice(e.target.value)}
                className="w-full px-3 py-2.5 border border-[#e8e8e8] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#3182f6]"
                placeholder="60000"
              />
            </div>
            <div>
              <label className="text-xs text-[#8b95a1] mb-1 block">매도가</label>
              <input
                type="number"
                value={sellPrice}
                onChange={e => setSellPrice(e.target.value)}
                className="w-full px-3 py-2.5 border border-[#e8e8e8] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#3182f6]"
                placeholder="70000"
              />
            </div>
          </div>
          <div>
            <label className="text-xs text-[#8b95a1] mb-1 block">매도일</label>
            <input
              type="date"
              value={sellDate}
              onChange={e => setSellDate(e.target.value)}
              className="w-full px-3 py-2.5 border border-[#e8e8e8] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#3182f6]"
            />
          </div>
          <div>
            <label className="text-xs text-[#8b95a1] mb-1 block">메모</label>
            <textarea
              value={memo}
              onChange={e => setMemo(e.target.value)}
              className="w-full px-3 py-2.5 border border-[#e8e8e8] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#3182f6] resize-none"
              placeholder="매도 이유..."
              rows={3}
            />
          </div>
          <button
            onClick={handleSubmit}
            className="w-full py-3 bg-[#3182f6] text-white rounded-xl font-medium text-sm hover:bg-[#1b64da] transition-colors"
          >
            기록 추가
          </button>
        </div>
      </div>
    </div>
  );
}

// ─── 메인 페이지 ──────────────────────────────────────────────────────────────
export default function PortfolioPage() {
  const { user } = useAuth();
  const [tab, setTab] = useState<Tab>('holdings');

  // 보유종목 state
  const [stocks, setStocks] = useState<UserStock[]>([]);
  const [stockLoading, setStockLoading] = useState(false);
  const [showStockModal, setShowStockModal] = useState(false);
  const [editStock, setEditStock] = useState<UserStock | null>(null);

  // 관심종목 state
  const [watchlist, setWatchlist] = useState<UserWatchlist[]>([]);
  const [watchlistLoading, setWatchlistLoading] = useState(false);
  const [showWatchlistModal, setShowWatchlistModal] = useState(false);
  const [editWatchlistItem, setEditWatchlistItem] = useState<UserWatchlist | null>(null);

  // 매도기록 state (localStorage)
  const [sellRecords, setSellRecords] = useState<SellRecord[]>([]);
  const [showSellModal, setShowSellModal] = useState(false);

  // 데이터 로드
  useEffect(() => {
    if (!user) return;
    loadStocks();
    loadWatchlist();
    loadSellRecords();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user]);

  const loadStocks = async () => {
    setStockLoading(true);
    try {
      const { data } = await getUserStocks();
      setStocks(data || []);
    } catch (e) {
      console.error(e);
    } finally {
      setStockLoading(false);
    }
  };

  const loadWatchlist = async () => {
    setWatchlistLoading(true);
    try {
      const { data } = await getUserWatchlist();
      setWatchlist(data || []);
    } catch (e) {
      console.error(e);
    } finally {
      setWatchlistLoading(false);
    }
  };

  const loadSellRecords = () => {
    try {
      const raw = localStorage.getItem('sell_records');
      if (raw) setSellRecords(JSON.parse(raw));
    } catch (e) {
      console.error(e);
    }
  };

  const saveSellRecords = (records: SellRecord[]) => {
    localStorage.setItem('sell_records', JSON.stringify(records));
    setSellRecords(records);
  };

  // ── 보유종목 핸들러
  const handleAddStock = async (data: {
    stock_code: string;
    stock_name: string;
    market: string;
    quantity: number;
    avg_buy_price: number;
    notes?: string;
  }) => {
    try {
      await addUserStock(data);
      await loadStocks();
    } catch (e) {
      alert('종목 추가에 실패했습니다.');
      console.error(e);
    }
  };

  const handleUpdateStock = async (data: {
    stock_code: string;
    stock_name: string;
    market: string;
    quantity: number;
    avg_buy_price: number;
    notes?: string;
  }) => {
    if (!editStock) return;
    try {
      await updateUserStock(editStock.id, { quantity: data.quantity, avg_buy_price: data.avg_buy_price, notes: data.notes });
      await loadStocks();
      setEditStock(null);
    } catch (e) {
      alert('종목 수정에 실패했습니다.');
      console.error(e);
    }
  };

  const handleDeleteStock = async (id: string, name: string) => {
    if (!confirm(`"${name}" 종목을 삭제하시겠습니까?`)) return;
    try {
      await deleteUserStock(id);
      await loadStocks();
    } catch (e) {
      alert('삭제에 실패했습니다.');
      console.error(e);
    }
  };

  // ── 관심종목 핸들러
  const handleAddWatchlist = async (data: {
    stock_code: string;
    stock_name: string;
    market: string;
    alert_on_signals?: boolean;
    alert_price_target?: number;
    alert_price_type?: 'above' | 'below';
    notes?: string;
  }) => {
    try {
      await addToWatchlist(data);
      await loadWatchlist();
    } catch (e) {
      alert('관심종목 추가에 실패했습니다.');
      console.error(e);
    }
  };

  const handleUpdateWatchlist = async (data: {
    stock_code: string;
    stock_name: string;
    market: string;
    alert_on_signals?: boolean;
    alert_price_target?: number;
    alert_price_type?: 'above' | 'below';
    notes?: string;
  }) => {
    if (!editWatchlistItem) return;
    try {
      await updateWatchlistItem(editWatchlistItem.id, data);
      await loadWatchlist();
      setEditWatchlistItem(null);
    } catch (e) {
      alert('수정에 실패했습니다.');
      console.error(e);
    }
  };

  const handleDeleteWatchlist = async (id: string, name: string) => {
    if (!confirm(`"${name}" 관심종목을 삭제하시겠습니까?`)) return;
    try {
      await removeFromWatchlist(id);
      await loadWatchlist();
    } catch (e) {
      alert('삭제에 실패했습니다.');
      console.error(e);
    }
  };

  // ── 매도기록 핸들러
  const handleAddSell = (data: Omit<SellRecord, 'id'>) => {
    const newRecord: SellRecord = { ...data, id: Date.now().toString() };
    saveSellRecords([newRecord, ...sellRecords]);
  };

  const handleDeleteSell = (id: string) => {
    if (!confirm('매도 기록을 삭제하시겠습니까?')) return;
    saveSellRecords(sellRecords.filter(r => r.id !== id));
  };

  // 수익률 계산
  const calcReturn = (buy: number, sell: number) => {
    const pct = ((sell - buy) / buy) * 100;
    return pct.toFixed(2);
  };

  // 로그인 안 된 경우
  if (!user) {
    return (
      <div className="min-h-screen bg-[#f4f4f4] flex items-center justify-center px-4">
        <div className="bg-white rounded-2xl p-8 text-center max-w-sm w-full shadow-sm border border-[#e8e8e8]">
          <div className="text-4xl mb-4">📋</div>
          <h2 className="text-lg font-bold text-[#191f28] mb-2">로그인이 필요합니다</h2>
          <p className="text-sm text-[#8b95a1] mb-6">포트폴리오 관리는 로그인 후 이용할 수 있습니다.</p>
          <a
            href="/login"
            className="block w-full py-3 bg-[#3182f6] text-white rounded-xl font-medium text-sm text-center hover:bg-[#1b64da] transition-colors"
          >
            로그인하기
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#f4f4f4]">
      {/* 헤더 */}
      <div className="bg-white border-b border-[#e8e8e8] px-5 py-4 sticky top-0 z-10">
        <h1 className="text-xl font-bold text-[#191f28]">📋 포트폴리오 관리</h1>
      </div>

      <div className="max-w-2xl mx-auto px-4 py-6">
        {/* 탭 */}
        <div className="bg-white rounded-2xl border border-[#e8e8e8] overflow-hidden mb-5 shadow-sm">
          <div className="flex border-b border-[#e8e8e8]">
            {([
              { key: 'holdings', label: '💼 보유종목', count: stocks.length },
              { key: 'watchlist', label: '⭐ 관심종목', count: watchlist.length },
              { key: 'sells', label: '📝 매도기록', count: sellRecords.length },
            ] as const).map(({ key, label, count }) => (
              <button
                key={key}
                onClick={() => setTab(key)}
                className={`flex-1 py-3.5 text-sm font-medium transition-colors ${
                  tab === key
                    ? 'text-[#3182f6] border-b-2 border-[#3182f6] bg-white'
                    : 'text-[#8b95a1] bg-[#f9f9f9]'
                }`}
              >
                {label} <span className="text-xs opacity-70">{count}</span>
              </button>
            ))}
          </div>
        </div>

        {/* ─── 보유종목 탭 ─── */}
        {tab === 'holdings' && (
          <div className="space-y-3">
            <button
              onClick={() => { setEditStock(null); setShowStockModal(true); }}
              className="w-full py-3 bg-[#3182f6] text-white rounded-2xl font-medium text-sm hover:bg-[#1b64da] transition-colors flex items-center justify-center gap-2"
            >
              <span>+</span> 종목 추가
            </button>

            {stockLoading ? (
              <div className="bg-white rounded-2xl border border-[#e8e8e8] p-8 text-center text-sm text-[#8b95a1]">
                불러오는 중...
              </div>
            ) : stocks.length === 0 ? (
              <div className="bg-white rounded-2xl border border-[#e8e8e8] p-8 text-center">
                <div className="text-3xl mb-2">💼</div>
                <p className="text-sm text-[#8b95a1]">보유 종목이 없습니다.<br />종목을 추가해보세요!</p>
              </div>
            ) : (
              stocks.map((stock) => (
                <div key={stock.id} className="bg-white rounded-2xl border border-[#e8e8e8] p-4 shadow-sm">
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-[#191f28]">{stock.stock_name}</span>
                        <span className="text-xs text-[#b0b8c1] bg-[#f4f4f4] px-2 py-0.5 rounded-full">{stock.stock_code}</span>
                        <span className="text-xs text-[#b0b8c1]">{stock.market}</span>
                      </div>
                      <div className="text-sm text-[#8b95a1] mt-1">
                        {stock.quantity.toLocaleString()}주 · 평균 {stock.avg_buy_price.toLocaleString()}원
                      </div>
                      {stock.notes && (
                        <div className="text-xs text-[#8b95a1] mt-1 bg-[#f8f9fa] rounded-lg px-3 py-1.5">
                          📝 {stock.notes}
                        </div>
                      )}
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-bold text-[#191f28]">
                        {(stock.quantity * stock.avg_buy_price).toLocaleString()}원
                      </div>
                      <div className="text-xs text-[#8b95a1]">평가금액</div>
                    </div>
                  </div>
                  <div className="flex gap-2 mt-3">
                    <button
                      onClick={() => { setEditStock(stock); setShowStockModal(true); }}
                      className="flex-1 py-2 border border-[#e8e8e8] text-[#191f28] text-sm rounded-xl hover:bg-[#f8f9fa] transition-colors font-medium"
                    >
                      ✏️ 수정
                    </button>
                    <button
                      onClick={() => handleDeleteStock(stock.id, stock.stock_name)}
                      className="flex-1 py-2 border border-[#ffe0e0] text-[#f04452] text-sm rounded-xl hover:bg-[#fff5f5] transition-colors font-medium"
                    >
                      🗑️ 삭제
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {/* ─── 관심종목 탭 ─── */}
        {tab === 'watchlist' && (
          <div className="space-y-3">
            <button
              onClick={() => { setEditWatchlistItem(null); setShowWatchlistModal(true); }}
              className="w-full py-3 bg-[#3182f6] text-white rounded-2xl font-medium text-sm hover:bg-[#1b64da] transition-colors flex items-center justify-center gap-2"
            >
              <span>+</span> 관심종목 추가
            </button>

            {watchlistLoading ? (
              <div className="bg-white rounded-2xl border border-[#e8e8e8] p-8 text-center text-sm text-[#8b95a1]">
                불러오는 중...
              </div>
            ) : watchlist.length === 0 ? (
              <div className="bg-white rounded-2xl border border-[#e8e8e8] p-8 text-center">
                <div className="text-3xl mb-2">⭐</div>
                <p className="text-sm text-[#8b95a1]">관심 종목이 없습니다.<br />관심 종목을 추가해보세요!</p>
              </div>
            ) : (
              watchlist.map((item) => (
                <div key={item.id} className="bg-white rounded-2xl border border-[#e8e8e8] p-4 shadow-sm">
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-[#191f28]">{item.stock_name}</span>
                        <span className="text-xs text-[#b0b8c1] bg-[#f4f4f4] px-2 py-0.5 rounded-full">{item.stock_code}</span>
                        <span className="text-xs text-[#b0b8c1]">{item.market}</span>
                      </div>
                      <div className="flex gap-2 mt-1 flex-wrap">
                        {item.alert_on_signals && (
                          <span className="text-xs bg-[#e8f0fe] text-[#3182f6] px-2 py-0.5 rounded-full">🔔 시그널알림</span>
                        )}
                        {item.alert_price_target && (
                          <span className="text-xs bg-[#fff3e0] text-[#f57c00] px-2 py-0.5 rounded-full">
                            💰 {item.alert_price_type === 'above' ? '↑' : '↓'} {item.alert_price_target.toLocaleString()}원
                          </span>
                        )}
                      </div>
                      {item.notes && (
                        <div className="text-xs text-[#8b95a1] mt-1 bg-[#f8f9fa] rounded-lg px-3 py-1.5">
                          📝 {item.notes}
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="flex gap-2 mt-3">
                    <button
                      onClick={() => { setEditWatchlistItem(item); setShowWatchlistModal(true); }}
                      className="flex-1 py-2 border border-[#e8e8e8] text-[#191f28] text-sm rounded-xl hover:bg-[#f8f9fa] transition-colors font-medium"
                    >
                      ✏️ 수정
                    </button>
                    <button
                      onClick={() => handleDeleteWatchlist(item.id, item.stock_name)}
                      className="flex-1 py-2 border border-[#ffe0e0] text-[#f04452] text-sm rounded-xl hover:bg-[#fff5f5] transition-colors font-medium"
                    >
                      🗑️ 삭제
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {/* ─── 매도기록 탭 ─── */}
        {tab === 'sells' && (
          <div className="space-y-3">
            <button
              onClick={() => setShowSellModal(true)}
              className="w-full py-3 bg-[#3182f6] text-white rounded-2xl font-medium text-sm hover:bg-[#1b64da] transition-colors flex items-center justify-center gap-2"
            >
              <span>+</span> 매도 기록 추가
            </button>

            {sellRecords.length === 0 ? (
              <div className="bg-white rounded-2xl border border-[#e8e8e8] p-8 text-center">
                <div className="text-3xl mb-2">📝</div>
                <p className="text-sm text-[#8b95a1]">매도 기록이 없습니다.<br />매도 완료 후 기록을 남겨보세요!</p>
              </div>
            ) : (
              sellRecords.map((record) => {
                const pct = Number(calcReturn(record.buy_price, record.sell_price));
                const isPositive = pct >= 0;
                const profit = (record.sell_price - record.buy_price) * record.quantity;
                return (
                  <div key={record.id} className="bg-white rounded-2xl border border-[#e8e8e8] p-4 shadow-sm">
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-[#191f28]">{record.stock_name}</span>
                          {record.stock_code && (
                            <span className="text-xs text-[#b0b8c1] bg-[#f4f4f4] px-2 py-0.5 rounded-full">{record.stock_code}</span>
                          )}
                        </div>
                        <div className="text-sm text-[#8b95a1] mt-1">
                          {record.quantity.toLocaleString()}주 · 매수 {record.buy_price.toLocaleString()}원 → 매도 {record.sell_price.toLocaleString()}원
                        </div>
                        <div className="text-xs text-[#b0b8c1] mt-0.5">{record.sell_date}</div>
                        {record.memo && (
                          <div className="text-xs text-[#8b95a1] mt-1 bg-[#f8f9fa] rounded-lg px-3 py-1.5">
                            📝 {record.memo}
                          </div>
                        )}
                      </div>
                      <div className="text-right">
                        <div className={`text-base font-bold ${isPositive ? 'text-[#f04452]' : 'text-[#3182f6]'}`}>
                          {isPositive ? '+' : ''}{pct}%
                        </div>
                        <div className={`text-xs font-medium ${isPositive ? 'text-[#f04452]' : 'text-[#3182f6]'}`}>
                          {isPositive ? '+' : ''}{profit.toLocaleString()}원
                        </div>
                      </div>
                    </div>
                    <div className="mt-3">
                      <button
                        onClick={() => handleDeleteSell(record.id)}
                        className="w-full py-2 border border-[#ffe0e0] text-[#f04452] text-sm rounded-xl hover:bg-[#fff5f5] transition-colors font-medium"
                      >
                        🗑️ 삭제
                      </button>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        )}
      </div>

      {/* 모달들 */}
      <StockModal
        isOpen={showStockModal}
        onClose={() => { setShowStockModal(false); setEditStock(null); }}
        onSubmit={editStock ? handleUpdateStock : handleAddStock}
        editStock={editStock}
      />
      <WatchlistModal
        isOpen={showWatchlistModal}
        onClose={() => { setShowWatchlistModal(false); setEditWatchlistItem(null); }}
        onSubmit={editWatchlistItem ? handleUpdateWatchlist : handleAddWatchlist}
        editItem={editWatchlistItem}
      />
      <SellModal
        isOpen={showSellModal}
        onClose={() => setShowSellModal(false)}
        onSubmit={handleAddSell}
      />
    </div>
  );
}
