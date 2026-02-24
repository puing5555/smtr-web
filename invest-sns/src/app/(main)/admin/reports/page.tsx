'use client';

import { useState, useEffect } from 'react';
import { AlertTriangle, CheckCircle, XCircle } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { useScrapsStore } from '@/stores/scraps';

const SIGNAL_TYPES: Record<string, { label: string; color: string; textColor: string }> = {
  STRONG_BUY: { label: '적극매수', color: 'bg-green-700', textColor: 'text-white' },
  BUY: { label: '매수', color: 'bg-green-500', textColor: 'text-white' },
  POSITIVE: { label: '긍정', color: 'bg-green-300', textColor: 'text-green-900' },
  HOLD: { label: '보유', color: 'bg-yellow-500', textColor: 'text-yellow-900' },
  NEUTRAL: { label: '중립', color: 'bg-gray-500', textColor: 'text-white' },
  CONCERN: { label: '우려', color: 'bg-orange-500', textColor: 'text-white' },
  SELL: { label: '매도', color: 'bg-red-500', textColor: 'text-white' },
  STRONG_SELL: { label: '적극매도', color: 'bg-red-700', textColor: 'text-white' },
};

const REASON_LABELS: Record<string, string> = {
  signal_error: '시그널 표시 오류',
  content_error: '발언 내용 오류',
  other: '기타',
};

export default function AdminReportsPage() {
  const { reports, loadFromStorage, updateReportStatus } = useScrapsStore();
  const [statusFilter, setStatusFilter] = useState<'all' | 'pending' | 'reviewed' | 'rejected'>('all');

  useEffect(() => {
    loadFromStorage();
  }, [loadFromStorage]);

  const filtered = reports.filter(r => statusFilter === 'all' || r.status === statusFilter);
  const pendingCount = reports.filter(r => r.status === 'pending').length;

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <AlertTriangle className="w-6 h-6 text-orange-500" /> 신고 관리
          </h1>
          <p className="text-gray-600 mt-1">유저들의 수정요청을 검토하세요</p>
        </div>
        {pendingCount > 0 && (
          <div className="px-3 py-1.5 bg-orange-100 text-orange-700 rounded-full text-sm font-semibold">
            대기중 {pendingCount}건
          </div>
        )}
      </div>

      {/* 필터 */}
      <div className="flex gap-2">
        {(['all', 'pending', 'reviewed', 'rejected'] as const).map(status => (
          <button
            key={status}
            onClick={() => setStatusFilter(status)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              statusFilter === status ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {status === 'all' ? `전체 (${reports.length})` : 
             status === 'pending' ? `대기중 (${reports.filter(r => r.status === 'pending').length})` :
             status === 'reviewed' ? `검토완료 (${reports.filter(r => r.status === 'reviewed').length})` :
             `반려 (${reports.filter(r => r.status === 'rejected').length})`}
          </button>
        ))}
      </div>

      {/* 리스트 */}
      <div className="space-y-3">
        {filtered.length === 0 ? (
          <div className="text-center py-16 text-gray-400">
            <AlertTriangle className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p className="text-lg font-medium">신고 내역이 없습니다</p>
          </div>
        ) : filtered.map(report => (
          <div key={report.id} className="bg-white rounded-lg border border-gray-200 p-5">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-gray-900">{report.stockName}</span>
                <Badge className={`${SIGNAL_TYPES[report.signalType]?.color} ${SIGNAL_TYPES[report.signalType]?.textColor} text-xs`}>
                  {SIGNAL_TYPES[report.signalType]?.label}
                </Badge>
                <span className="text-xs text-gray-500">by {report.influencer}</span>
                <Badge variant="secondary" className="text-xs">
                  {REASON_LABELS[report.reason] || report.reason}
                </Badge>
              </div>
              <div className="flex items-center gap-1">
                {report.status === 'pending' ? (
                  <span className="px-2 py-1 bg-yellow-100 text-yellow-700 text-xs rounded-full font-medium">대기중</span>
                ) : report.status === 'reviewed' ? (
                  <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full font-medium">검토완료</span>
                ) : (
                  <span className="px-2 py-1 bg-red-100 text-red-700 text-xs rounded-full font-medium">반려</span>
                )}
              </div>
            </div>

            <p className="text-sm text-gray-700 mb-3">{report.detail}</p>

            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-400">{new Date(report.createdAt).toLocaleString('ko-KR')}</span>
              {report.status === 'pending' && (
                <div className="flex gap-2">
                  <button
                    onClick={() => updateReportStatus(report.id, 'reviewed')}
                    className="flex items-center gap-1 px-3 py-1.5 bg-green-500 text-white text-xs rounded-lg hover:bg-green-600 transition-colors"
                  >
                    <CheckCircle className="w-3.5 h-3.5" /> 검토완료
                  </button>
                  <button
                    onClick={() => updateReportStatus(report.id, 'rejected')}
                    className="flex items-center gap-1 px-3 py-1.5 bg-red-500 text-white text-xs rounded-lg hover:bg-red-600 transition-colors"
                  >
                    <XCircle className="w-3.5 h-3.5" /> 반려
                  </button>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
