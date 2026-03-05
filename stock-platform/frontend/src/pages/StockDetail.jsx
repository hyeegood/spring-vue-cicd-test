import { useState, useEffect, useCallback } from 'react'
import { useParams } from 'react-router-dom'
import { getStockDetail, refreshStock } from '../api'
import PriceChart from '../components/PriceChart'
import IndicatorRadar from '../components/IndicatorRadar'
import OptionsChart from '../components/OptionsChart'
import SentimentPanel from '../components/SentimentPanel'

function formatLastUpdated(iso) {
  if (!iso) return null
  try {
    return new Date(iso).toLocaleString('ko-KR', { dateStyle: 'short', timeStyle: 'short' })
  } catch {
    return iso
  }
}

export default function StockDetail() {
  const { ticker } = useParams()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [error, setError] = useState(null)
  const [lastRefreshedAt, setLastRefreshedAt] = useState(null)

  const load = useCallback(() => {
    if (!ticker) return
    setLoading(true)
    setError(null)
    getStockDetail(ticker)
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [ticker])

  useEffect(() => { load() }, [load])

  const handleRefresh = () => {
    if (!ticker) return
    setRefreshing(true)
    setError(null)
    refreshStock(ticker)
      .then((res) => {
        setLastRefreshedAt(res.refreshed_at ?? null)
        return getStockDetail(ticker)
      })
      .then(setData)
      .catch((e) => setError(e?.message || '새로고침 실패'))
      .finally(() => setRefreshing(false))
  }

  if (loading && !data) return <div className="p-8 text-center">로딩 중...</div>
  if (error && !data) return <div className="p-8 text-red-600">오류: {error}</div>
  if (data?.error) return <div className="p-8 text-red-600">오류: {data.error}</div>

  const rec = data?.recommendation || {}
  const fin = data?.financials || {}
  const market = data?.market_indicators || {}
  const options = data?.options || {}

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-8">
      <div className="flex flex-wrap items-center gap-4">
        <h1 className="text-2xl font-bold">
          {data.stock?.company_name}
          {data.stock?.company_name_ko ? <span className="text-gray-600 font-normal ml-1">({data.stock.company_name_ko})</span> : null}
          {' '}({data.stock?.ticker})
        </h1>
        <button
          type="button"
          onClick={handleRefresh}
          disabled={refreshing || loading}
          className="px-4 py-2 rounded bg-blue-600 text-white disabled:opacity-50 disabled:cursor-not-allowed hover:bg-blue-700"
        >
          {refreshing ? '업데이트 중...' : '새로고침'}
        </button>
        {lastRefreshedAt && (
          <span className="text-sm text-gray-500">마지막 업데이트: {formatLastUpdated(lastRefreshedAt)}</span>
        )}
      </div>

      {data.stock?.company_summary && (
        <section className="bg-slate-50 dark:bg-slate-800/50 rounded-lg p-4">
          <h2 className="text-lg font-semibold mb-2">기업 요약</h2>
          <p className="text-slate-700 dark:text-slate-300 text-sm leading-relaxed whitespace-pre-line">
            {data.stock.company_summary}
          </p>
        </section>
      )}

      {/* FEATURE 5: Reliability Analysis */}
      {data.reliability_analysis && (
        <section className="rounded-card border border-surface-border bg-white p-5 shadow-card">
          <h2 className="text-lg font-semibold text-slate-800 mb-4">Reliability Analysis</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
            <div className="rounded-lg border border-slate-200 bg-slate-50/50 p-4">
              <p className="text-xs font-medium text-muted uppercase tracking-wider">Sector Reliability Score</p>
              <p className="mt-1 text-2xl font-semibold tabular-nums text-slate-900">
                {data.reliability_analysis.sector_reliability ?? '–'}
              </p>
              <p className="mt-0.5 text-sm text-muted">0–100 (높을수록 밸류에이션 지표 신뢰도 높음)</p>
            </div>
            <div className="rounded-lg border border-slate-200 bg-slate-50/50 p-4">
              <p className="text-xs font-medium text-muted uppercase tracking-wider">Stock Reliability Score</p>
              <p className="mt-1 text-2xl font-semibold tabular-nums text-slate-900">
                {data.reliability_analysis.stock_reliability ?? '–'}
              </p>
              <p className="mt-0.5 text-sm text-muted">0–100 (섹터·수익안정성·커버리지·변동성 반영)</p>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-2 mb-3">
            <span className="text-sm font-medium text-slate-700">위험 수준:</span>
            <span
              className={`rounded-md border px-2 py-1 text-sm font-medium ${
                data.reliability_analysis.reliability_level === 'high'
                  ? 'bg-emerald-100 text-emerald-800 border-emerald-200'
                  : data.reliability_analysis.reliability_level === 'high_risk'
                    ? 'bg-rose-100 text-rose-800 border-rose-200'
                    : 'bg-amber-100 text-amber-800 border-amber-200'
              }`}
            >
              {data.reliability_analysis.reliability_level === 'high'
                ? 'High Reliability'
                : data.reliability_analysis.reliability_level === 'high_risk'
                  ? 'High Risk'
                  : 'Medium Reliability'}
            </span>
          </div>
          <p className="text-sm text-slate-600 leading-relaxed">
            {data.reliability_analysis.interpretation ?? '–'}
          </p>
        </section>
      )}

      <section>
        <h2 className="text-lg font-semibold mb-2">주식 가격 차트</h2>
        <PriceChart data={data.price_history} />
      </section>

      <section className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h2 className="text-lg font-semibold mb-2">투자 확률 점수</h2>
          <p className="text-3xl font-bold text-blue-600">{data.score_breakdown?.total?.toFixed(1) ?? '-'} / 100</p>
        </div>
        <div>
          <h2 className="text-lg font-semibold mb-2">추천 매매 전략</h2>
          <ul className="space-y-1">
            <li>추천 진입가: {rec.entry_price != null ? rec.entry_price.toLocaleString() : '-'}</li>
            <li>추천 손절가: {rec.stop_loss != null ? rec.stop_loss.toLocaleString() : '-'}</li>
            <li>목표가: {rec.target_price != null ? rec.target_price.toLocaleString() : '-'}</li>
          </ul>
        </div>
      </section>

      <section>
        <h2 className="text-lg font-semibold mb-2">재무 지표</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>ROE: {fin.roe != null ? `${fin.roe.toFixed(1)}%` : '-'}</div>
          <div>PER: {fin.per ?? '-'}</div>
          <div>PBR: {fin.pbr ?? '-'}</div>
          <div>PEG: {fin.peg ?? '-'}</div>
          <div>EV/EBITDA: {fin.ev_ebitda ?? '-'}</div>
          <div>FCF: {fin.fcf_growth ?? '-'}</div>
          <div>영업이익률: {fin.operating_margin != null ? `${fin.operating_margin.toFixed(1)}%` : '-'}</div>
          <div>부채비율: {fin.debt_ratio != null ? `${fin.debt_ratio.toFixed(0)}%` : '-'}</div>
        </div>
      </section>

      <section>
        <h2 className="text-lg font-semibold mb-2">시장 지표</h2>
        <div className="flex gap-4 text-sm">
          <span>기관 보유율: {market.institutional_ownership != null ? `${market.institutional_ownership.toFixed(1)}%` : '-'}</span>
          <span>공매도 비율: {market.short_interest != null ? `${market.short_interest.toFixed(1)}%` : '-'}</span>
          <span>내부자: {market.insider_activity ?? '-'}</span>
        </div>
      </section>

      <section>
        <h2 className="text-lg font-semibold mb-2">기업 문화</h2>
        <div className="flex gap-4 text-sm">
          <span>기업 평점: {data.stock?.glassdoor_rating ?? '-'}</span>
          <span>CEO 승인율: {data.stock?.ceo_approval != null ? `${data.stock.ceo_approval}%` : '-'}</span>
          <span>직원 추천율: {data.stock?.employee_recommendation != null ? `${data.stock.employee_recommendation}%` : '-'}</span>
          <span>직원 증가율: {data.stock?.linkedin_employee_growth != null ? `${data.stock.linkedin_employee_growth}%` : '-'}</span>
        </div>
      </section>

      <section className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h2 className="text-lg font-semibold mb-2">옵션 시장</h2>
          <OptionsChart
            callVolume={options.call_volume}
            putVolume={options.put_volume}
            putCallRatio={options.put_call_ratio}
          />
        </div>
        <div>
          <h2 className="text-lg font-semibold mb-2">지표 레이더</h2>
          <IndicatorRadar breakdown={data.score_breakdown} />
        </div>
      </section>

      <section>
        <h2 className="text-lg font-semibold mb-2">뉴스 감성 분석</h2>
        <SentimentPanel news={data.news} />
      </section>
    </div>
  )
}
