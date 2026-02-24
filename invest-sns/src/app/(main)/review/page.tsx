import React from 'react'
import ReviewClient from './ReviewClient'
import fs from 'fs'
import path from 'path'

// 서버 컴포넌트에서 시그널 데이터 로드
async function loadSignalsData() {
  try {
    const filePath = path.join(process.cwd(), 'smtr_data', 'corinpapa1106', '_deduped_signals_8types_dated.json')
    const fileContent = await fs.promises.readFile(filePath, 'utf8')
    return JSON.parse(fileContent)
  } catch (error) {
    console.error('Error loading signals data:', error)
    return []
  }
}

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

export default async function ReviewPage() {
  const signalsData = await loadSignalsData()
  
  return <ReviewClient signalsData={signalsData} />
}