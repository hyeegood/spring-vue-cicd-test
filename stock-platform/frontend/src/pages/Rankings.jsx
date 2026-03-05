import { useState, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { getRankings, refreshFull, getRefreshStatus } from '../api'

const TABS = [
  { key: 'score', label: '투자 점수 Top' },
  { key: 'value', label: '밸류 Top' },
  { key: 'growth', label: '성장 Top' },
]

function formatLastUpdated(iso) {
  if (!iso) return null
  try {
    return new Date(iso).toLocaleString('ko-KR', { dateStyle: 'short', timeStyle: 'short' })
  } catch {
    return iso
  }
}

export default function Rankings() {
  const [tab, setTab] = useState('score')
  const [data, setData] = useState([])
  const [lastRefreshAt, setLastRefreshAt] = useState(null)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  const load = useCallback(() => {
    setLoading(true)
    getRankings(tab, 50)
      .then(setData)
      .catch(() => setData([]))
      .finally(() => setLoading(false))
  }, [tab])

  useEffect(() => { load() }, [load])

  const handleRefresh = () => {
    setRefreshing(true)
    refreshFull()
      .then(() => {
        const poll = () => {
          getRefreshStatus()
            .then((st) => {
              if (st && st.running) {
                setTimeout(poll, 2000)
              } else {
                setLastRefreshAt(st?.last_completed_at ?? null)
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
      .catch(() => {
        setRefreshing(false)
      })
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="flex flex-wrap items-center gap-4 mb-4">
        <h1 className="text-2xl font-bold">종목 발견</h1>
        <button
          type="button"
          onClick={handleRefresh}
          disabled={refreshing || loading}
          className="px-4 py-2 rounded bg-blue-600 text-white disabled:opacity-50 disabled:cursor-not-allowed hover:bg-blue-700"
        >
          {refreshing ? '업데이트 중...' : '새로고침'}
        </button>
        {lastRefreshAt && (
          <span className="text-sm text-gray-500">마지막 업데이트: {formatLastUpdated(lastRefreshAt)}</span>
        )}
      </div>
      <div className="flex gap-2 mb-4">
        {TABS.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`px-4 py-2 rounded ${tab === t.key ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
          >
            {t.label}
          </button>
        ))}
      </div>
      {loading ? (
        <p>로딩 중...</p>
      ) : (
        <ul className="space-y-2">
          {data.map((row, i) => (
            <li key={row.ticker} className="flex items-center gap-4 border-b py-2">
              <span className="text-gray-500 w-8">{i + 1}</span>
              <Link to={`/stock/${row.ticker}`} className="text-blue-600 font-medium hover:underline">
                {row.ticker}
              </Link>
              <span className="text-gray-700">
                {row.company_name}
                {row.company_name_ko ? <span className="text-gray-500 ml-1">({row.company_name_ko})</span> : null}
              </span>
              <span className="font-semibold">{row.score != null ? row.score.toFixed(1) : '-'}점</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
