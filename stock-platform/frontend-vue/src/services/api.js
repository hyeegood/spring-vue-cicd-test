// =======================================
// API 호출: 대시보드 집계, 종목 상세, 랭킹
// 비동기 호출로 1초 이내 응답 목표
// =======================================
const API_BASE = import.meta.env.VITE_API_BASE || ''

export async function getDashboardAnalytics() {
  const r = await fetch(`${API_BASE}/api/dashboard/analytics`)
  if (!r.ok) throw new Error('대시보드 조회 실패')
  return r.json()
}

export async function getDashboard() {
  const r = await fetch(`${API_BASE}/api/dashboard`)
  if (!r.ok) throw new Error('대시보드 조회 실패')
  return r.json()
}

export async function getStockDetail(ticker) {
  const r = await fetch(`${API_BASE}/api/stocks/${encodeURIComponent(ticker)}`)
  if (!r.ok) throw new Error('종목 조회 실패')
  return r.json()
}

export async function getRankings(listType, limit = 50) {
  const r = await fetch(`${API_BASE}/api/rankings/${listType}?limit=${limit}`)
  if (!r.ok) throw new Error('랭킹 조회 실패')
  return r.json()
}

export async function getRecommendations(limit = 50) {
  const r = await fetch(`${API_BASE}/api/recommendations?limit=${limit}`)
  if (!r.ok) throw new Error('추천 조회 실패')
  return r.json()
}

export async function getScreener(params = {}) {
  const q = new URLSearchParams(params).toString()
  const r = await fetch(`${API_BASE}/api/screener${q ? '?' + q : ''}`)
  if (!r.ok) throw new Error('스크리너 조회 실패')
  return r.json()
}

export async function getStockChart(symbol) {
  const r = await fetch(`${API_BASE}/api/stocks/${encodeURIComponent(symbol)}/chart`)
  if (!r.ok) throw new Error('차트 조회 실패')
  return r.json()
}
