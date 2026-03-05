import { createContext, useContext, useState, useCallback, useEffect } from 'react'
import { getDashboard, refreshFull, getRefreshStatus } from '../api'

function sortDashboardRows(rows) {
  if (!Array.isArray(rows) || !rows.length) return rows
  return [...rows].sort((a, b) => {
    const scoreA = a.investment_score ?? a.score ?? -1
    const scoreB = b.investment_score ?? b.score ?? -1
    if (scoreB !== scoreA) return scoreB - scoreA
    const curA = a.current_price != null ? Number(a.current_price) : null
    const entA = a.entry_price != null ? Number(a.entry_price) : null
    const curB = b.current_price != null ? Number(b.current_price) : null
    const entB = b.entry_price != null ? Number(b.entry_price) : null
    const diffA = (curA != null && entA != null) ? Math.abs(curA - entA) : Infinity
    const diffB = (curB != null && entB != null) ? Math.abs(curB - entB) : Infinity
    if (diffA !== diffB) return diffA - diffB
    const gdA = a.glassdoor_rating != null ? a.glassdoor_rating : 0
    const gdB = b.glassdoor_rating != null ? b.glassdoor_rating : 0
    return gdB - gdA
  })
}

const DashboardContext = createContext(null)

const REFRESH_INTERVAL_MS = 5 * 60 * 1000 // 5분마다 자동 새로고침

export function DashboardProvider({ children }) {
  const [items, setItems] = useState([])
  const [lastRefreshAt, setLastRefreshAt] = useState(null)
  const [loading, setLoading] = useState(false)
  const [refreshing, setRefreshing] = useState(false)
  const [error, setError] = useState(null)

  const load = useCallback((showLoading = false) => {
    if (showLoading) setLoading(true)
    setError(null)
    // 항상 full API만 사용 (신뢰도·한글명 등 전체 필드 포함). minimal은 필드 누락 가능성 있음.
    getDashboard()
      .then((res) => {
        setItems(sortDashboardRows(res.items || []))
        setLastRefreshAt(res.last_refresh_at ?? null)
      })
      .catch((e) => setError(e?.message || '오류 발생'))
      .finally(() => setLoading(false))
  }, [])

  const refresh = useCallback(() => {
    setRefreshing(true)
    setError(null)
    refreshFull()
      .then(() => {
        const poll = () => {
          getRefreshStatus()
            .then((st) => {
              if (st && st.running) setTimeout(poll, 2000)
              else {
                setRefreshing(false)
                load()
              }
            })
            .catch(() => {
              setRefreshing(false)
              load()
            })
        }
        poll()
      })
      .catch((e) => {
        setError(e?.message || '새로고침 실패')
        setRefreshing(false)
      })
  }, [load])

  useEffect(() => {
    load(true)
  }, [load])

  useEffect(() => {
    const id = setInterval(() => load(), REFRESH_INTERVAL_MS)
    return () => clearInterval(id)
  }, [load])

  const value = {
    items,
    lastRefreshAt,
    loading,
    refreshing,
    error,
    setError,
    load,
    refresh,
  }

  return (
    <DashboardContext.Provider value={value}>
      {children}
    </DashboardContext.Provider>
  )
}

export function useDashboard() {
  const ctx = useContext(DashboardContext)
  if (!ctx) throw new Error('useDashboard must be used within DashboardProvider')
  return ctx
}
