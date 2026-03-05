import { useState } from 'react'
import { refreshKoreanNames } from '../api'
import { useDashboard } from '../context/DashboardContext'
import StockTable from '../components/StockTable'
import StockCard from '../components/StockCard'
import Card from '../components/ui/Card'
import MetricWidget from '../components/ui/MetricWidget'
import Button from '../components/ui/Button'

function formatLastUpdated(iso) {
  if (!iso) return null
  try {
    return new Date(iso).toLocaleString('ko-KR', { dateStyle: 'short', timeStyle: 'short' })
  } catch {
    return iso
  }
}

function groupByReliability(items) {
  const high = items.filter((r) => (r.reliability_level || 'medium') === 'high')
  const medium = items.filter((r) => (r.reliability_level || 'medium') === 'medium')
  const highRisk = items.filter((r) => (r.reliability_level || 'medium') === 'high_risk')
  return { high, medium, highRisk }
}

export default function Dashboard() {
  const { items: data, lastRefreshAt, loading, refreshing, error, setError, load, refresh } = useDashboard()
  const [fetchingKorean, setFetchingKorean] = useState(false)

  const handleFetchKoreanNames = () => {
    setFetchingKorean(true)
    setError(null)
    refreshKoreanNames()
      .then((res) => { load(); if (res.updated != null) setError(null) })
      .catch((e) => setError(e?.message || '한글명 가져오기 실패'))
      .finally(() => setFetchingKorean(false))
  }

  const first = data[0]
  const invScores = data.map((r) => r.investment_score ?? r.score).filter((x) => x != null)
  const avgScore = invScores.length ? invScores.reduce((s, x) => s + x, 0) / invScores.length : null
  const withPrice = data.filter((r) => r.current_price != null).length
  const { high, medium, highRisk } = groupByReliability(data)

  if (loading && !data.length) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center">
        <div className="text-center">
          <div className="mx-auto h-8 w-8 animate-spin rounded-full border-2 border-primary-500 border-t-transparent" />
          <p className="mt-3 text-sm text-muted">로딩 중...</p>
        </div>
      </div>
    )
  }

  if (error && !data.length) {
    return (
      <div className="rounded-card border border-rose-200 bg-rose-50 p-6 text-rose-700">
        오류: {error}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-semibold text-slate-900">대시보드</h1>
          <p className="mt-0.5 text-sm text-muted">기업평점 4.0 이상 종목 · 투자점수·진입가 기준 정렬</p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          {lastRefreshAt && (
            <span className="text-xs text-muted">마지막 업데이트: {formatLastUpdated(lastRefreshAt)}</span>
          )}
          <Button variant="secondary" onClick={handleFetchKoreanNames} disabled={fetchingKorean || loading}>
            {fetchingKorean ? '한글명 조회 중...' : '한글 회사명'}
          </Button>
          <Button onClick={refresh} disabled={refreshing || loading}>
            {refreshing ? '업데이트 중...' : '데이터 새로고침'}
          </Button>
        </div>
      </div>

      {error && (
        <div className="rounded-card border border-amber-200 bg-amber-50 px-4 py-2 text-sm text-amber-800">
          {error}
        </div>
      )}

      <section className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
        <MetricWidget label="종목 수" value={data.length} />
        <MetricWidget label="평균 투자점수" value={avgScore != null ? avgScore.toFixed(1) : null} sub={avgScore != null ? '/ 100' : null} />
        <MetricWidget label="고신뢰도" value={high.length} sub="종목" />
        <MetricWidget label="중신뢰도" value={medium.length} sub="종목" />
        <MetricWidget label="고위험" value={highRisk.length} sub="종목" />
      </section>

      {/* FEATURE 4: 신뢰도 구간별 카드 섹션 */}
      <section className="space-y-6">
        {high.length > 0 && (
          <div>
            <h2 className="mb-3 flex items-center gap-2 text-base font-semibold text-slate-800">
              <span className="inline-block h-2 w-2 rounded-full bg-emerald-500" />
              High Reliability Stocks
            </h2>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {high.map((row) => (
                <StockCard key={row.ticker} item={row} />
              ))}
            </div>
          </div>
        )}
        {medium.length > 0 && (
          <div>
            <h2 className="mb-3 flex items-center gap-2 text-base font-semibold text-slate-800">
              <span className="inline-block h-2 w-2 rounded-full bg-amber-500" />
              Medium Reliability Stocks
            </h2>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {medium.map((row) => (
                <StockCard key={row.ticker} item={row} />
              ))}
            </div>
          </div>
        )}
        {highRisk.length > 0 && (
          <div>
            <h2 className="mb-3 flex items-center gap-2 text-base font-semibold text-slate-800">
              <span className="inline-block h-2 w-2 rounded-full bg-rose-500" />
              High Risk Stocks
            </h2>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {highRisk.map((row) => (
                <StockCard key={row.ticker} item={row} />
              ))}
            </div>
          </div>
        )}
      </section>

      <Card title="전체 종목 목록" hover={false}>
        <StockTable rows={data} />
      </Card>
    </div>
  )
}
