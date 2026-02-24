'use client'

import React, { useState, useMemo, useEffect } from 'react'

interface Signal {
  id?: number
  asset: string
  signal_type: string
  content: string
  confidence: string
  timestamp: string
  video_id: string
  title: string
  upload_date: string
  youtubeLink?: string
}

interface ReviewStatus {
  status: 'approved' | 'rejected' | 'pending'
  reason?: string
  timestamp: string
}

interface ReviewClientProps {
  signalsData: Signal[]
}

const SIGNAL_TYPES = [
  'STRONG_BUY', 'BUY', 'POSITIVE', 'HOLD', 
  'NEUTRAL', 'CONCERN', 'SELL', 'STRONG_SELL'
]

const SIGNAL_COLORS = {
  STRONG_BUY: 'bg-red-600 text-white',
  BUY: 'bg-red-500 text-white',
  POSITIVE: 'bg-orange-500 text-white',
  HOLD: 'bg-yellow-500 text-white',
  NEUTRAL: 'bg-gray-500 text-white',
  CONCERN: 'bg-purple-500 text-white',
  SELL: 'bg-blue-500 text-white',
  STRONG_SELL: 'bg-blue-700 text-white'
}

const SIGNAL_BORDER_COLORS = {
  STRONG_BUY: 'border-l-red-600',
  BUY: 'border-l-red-500',
  POSITIVE: 'border-l-orange-500',
  HOLD: 'border-l-yellow-500',
  NEUTRAL: 'border-l-gray-500',
  CONCERN: 'border-l-purple-500',
  SELL: 'border-l-blue-500',
  STRONG_SELL: 'border-l-blue-700'
}

export default function ReviewClient({ signalsData }: ReviewClientProps) {
  const [filters, setFilters] = useState({
    signalType: '',
    reviewStatus: '',
    asset: '',
    opus: ''
  })

  const [reviews, setReviews] = useState<Record<string, ReviewStatus>>(() => {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('signal_reviews')
      return stored ? JSON.parse(stored) : {}
    }
    return {}
  })

  const [showRejectInput, setShowRejectInput] = useState<string>('')
  const [rejectReason, setRejectReason] = useState('')

  // localStorage에 리뷰 저장
  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('signal_reviews', JSON.stringify(reviews))
    }
  }, [reviews])

  // 시그널 정렬 (최신순)
  const sortedSignals = useMemo(() => {
    return [...signalsData].sort((a, b) => {
      const dateA = new Date(a.upload_date || '1970-01-01')
      const dateB = new Date(b.upload_date || '1970-01-01')
      return dateB.getTime() - dateA.getTime()
    })
  }, [signalsData])

  // 필터링된 시그널
  const filteredSignals = useMemo(() => {
    return sortedSignals.filter(signal => {
      const signalId = `${signal.video_id}_${signal.asset}`
      const review = reviews[signalId]
      const reviewStatus = review?.status || 'pending'

      // 시그널 타입 필터
      if (filters.signalType && signal.signal_type !== filters.signalType) {
        return false
      }

      // 리뷰 상태 필터
      if (filters.reviewStatus && reviewStatus !== filters.reviewStatus) {
        return false
      }

      // 종목 필터
      if (filters.asset && !signal.asset.toLowerCase().includes(filters.asset.toLowerCase())) {
        return false
      }

      return true
    })
  }, [sortedSignals, filters, reviews])

  // 통계 계산
  const stats = useMemo(() => {
    const total = signalsData.length
    const reviewedCount = Object.values(reviews).filter(r => r.status !== 'pending').length
    const approved = Object.values(reviews).filter(r => r.status === 'approved').length
    const rejected = Object.values(reviews).filter(r => r.status === 'rejected').length
    const pending = total - reviewedCount

    return {
      total,
      pending,
      approved,
      rejected,
      displayed: filteredSignals.length
    }
  }, [signalsData.length, reviews, filteredSignals.length])

  const handleReview = (signalId: string, status: 'approved' | 'rejected', reason = '') => {
    setReviews(prev => ({
      ...prev,
      [signalId]: {
        status,
        reason,
        timestamp: new Date().toISOString()
      }
    }))
    setShowRejectInput('')
    setRejectReason('')
  }

  const handleRejectSubmit = (signalId: string) => {
    if (!rejectReason.trim()) {
      alert('거부 사유를 입력해주세요.')
      return
    }
    handleReview(signalId, 'rejected', rejectReason)
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-700 text-white rounded-2xl p-8 mb-8">
          <h1 className="text-3xl font-bold mb-2">시그널 리뷰</h1>
          <p className="text-blue-100 text-lg">코린이 아빠 시그널 검증 시스템</p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
          <div className="bg-white rounded-xl p-6 text-center shadow-lg">
            <div className="text-3xl font-bold text-blue-600">{stats.total}</div>
            <div className="text-sm text-gray-600 mt-1">총 시그널</div>
          </div>
          <div className="bg-white rounded-xl p-6 text-center shadow-lg">
            <div className="text-3xl font-bold text-blue-600">{stats.pending}</div>
            <div className="text-sm text-gray-600 mt-1">검토 대기</div>
          </div>
          <div className="bg-white rounded-xl p-6 text-center shadow-lg">
            <div className="text-3xl font-bold text-green-600">{stats.approved}</div>
            <div className="text-sm text-gray-600 mt-1">승인됨</div>
          </div>
          <div className="bg-white rounded-xl p-6 text-center shadow-lg">
            <div className="text-3xl font-bold text-red-600">{stats.rejected}</div>
            <div className="text-sm text-gray-600 mt-1">거부됨</div>
          </div>
          <div className="bg-white rounded-xl p-6 text-center shadow-lg">
            <div className="text-3xl font-bold text-purple-600">{stats.displayed}</div>
            <div className="text-sm text-gray-600 mt-1">현재 표시</div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-xl p-6 mb-8 shadow-lg">
          <div className="flex flex-wrap gap-4 items-end">
            <div className="flex flex-col">
              <label className="text-sm font-semibold text-gray-600 mb-2">시그널 타입</label>
              <select 
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm min-w-[140px]"
                value={filters.signalType}
                onChange={(e) => setFilters(prev => ({ ...prev, signalType: e.target.value }))}
              >
                <option value="">전체</option>
                {SIGNAL_TYPES.map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>
            
            <div className="flex flex-col">
              <label className="text-sm font-semibold text-gray-600 mb-2">검토 상태</label>
              <select 
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm min-w-[120px]"
                value={filters.reviewStatus}
                onChange={(e) => setFilters(prev => ({ ...prev, reviewStatus: e.target.value }))}
              >
                <option value="">전체</option>
                <option value="pending">검토 대기</option>
                <option value="approved">승인됨</option>
                <option value="rejected">거부됨</option>
              </select>
            </div>
            
            <div className="flex flex-col">
              <label className="text-sm font-semibold text-gray-600 mb-2">종목명</label>
              <input 
                type="text"
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm min-w-[150px]"
                placeholder="종목 검색..."
                value={filters.asset}
                onChange={(e) => setFilters(prev => ({ ...prev, asset: e.target.value }))}
              />
            </div>
          </div>
        </div>

        {/* Signals Grid */}
        <div className="space-y-4">
          {filteredSignals.map((signal, index) => {
            const signalId = `${signal.video_id}_${signal.asset}_${index}`
            const review = reviews[signalId]
            const reviewStatus = review?.status || 'pending'
            
            return (
              <div 
                key={signalId} 
                className={`bg-white rounded-xl p-6 shadow-lg border-l-4 ${SIGNAL_BORDER_COLORS[signal.signal_type as keyof typeof SIGNAL_BORDER_COLORS] || 'border-l-gray-400'}`}
              >
                {/* Header */}
                <div className="flex justify-between items-start mb-4 flex-wrap gap-4">
                  <div className="flex items-center gap-3">
                    <h3 className="text-xl font-bold">{signal.asset}</h3>
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${SIGNAL_COLORS[signal.signal_type as keyof typeof SIGNAL_COLORS] || 'bg-gray-500 text-white'}`}>
                      {signal.signal_type}
                    </span>
                  </div>
                  
                  {reviewStatus !== 'pending' && (
                    <span className={`px-3 py-1 rounded-lg text-sm font-semibold ${
                      reviewStatus === 'approved' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {reviewStatus === 'approved' ? '승인됨' : '거부됨'}
                    </span>
                  )}
                </div>

                {/* Content */}
                <div className="bg-gray-50 p-4 rounded-lg mb-4 border-l-2 border-blue-500">
                  <p className="text-gray-800 italic">{signal.content}</p>
                </div>

                {/* Meta Info */}
                <div className="flex flex-wrap gap-4 text-sm text-gray-600 mb-4">
                  <span>⏱️ {signal.timestamp}</span>
                  <span>📊 {signal.confidence}</span>
                  <a 
                    href={`https://youtube.com/watch?v=${signal.video_id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-red-500 hover:text-red-700 hover:underline"
                  >
                    🎥 영상 보기
                  </a>
                  <span>📅 {signal.title} ({signal.upload_date})</span>
                </div>

                {/* Actions */}
                <div className="flex gap-3 items-center">
                  <button
                    onClick={() => handleReview(signalId, 'approved')}
                    className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors text-sm font-medium"
                  >
                    ✅ 승인
                  </button>
                  
                  {showRejectInput === signalId ? (
                    <div className="flex gap-2 items-center flex-1">
                      <input
                        type="text"
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm"
                        placeholder="거부 사유를 입력하세요..."
                        value={rejectReason}
                        onChange={(e) => setRejectReason(e.target.value)}
                        onKeyPress={(e) => {
                          if (e.key === 'Enter') {
                            handleRejectSubmit(signalId)
                          }
                        }}
                        autoFocus
                      />
                      <button
                        onClick={() => handleRejectSubmit(signalId)}
                        className="px-3 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors text-sm font-medium"
                      >
                        거부 확정
                      </button>
                      <button
                        onClick={() => {
                          setShowRejectInput('')
                          setRejectReason('')
                        }}
                        className="px-3 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition-colors text-sm font-medium"
                      >
                        취소
                      </button>
                    </div>
                  ) : (
                    <button
                      onClick={() => setShowRejectInput(signalId)}
                      className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors text-sm font-medium"
                    >
                      ❌ 거부
                    </button>
                  )}
                </div>

                {/* Rejection Reason Display */}
                {reviewStatus === 'rejected' && review?.reason && (
                  <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
                    <strong className="text-red-800 text-sm">거부 사유:</strong>
                    <span className="ml-2 text-red-700 text-sm">{review.reason}</span>
                  </div>
                )}
              </div>
            )
          })}
        </div>

        {filteredSignals.length === 0 && (
          <div className="text-center py-12">
            <div className="text-gray-500 text-lg">필터 조건에 맞는 시그널이 없습니다.</div>
          </div>
        )}
      </div>
    </div>
  )
}