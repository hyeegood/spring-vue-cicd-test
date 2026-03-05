import { useState, useMemo } from 'react'
import { Link } from 'react-router-dom'
import Badge from './ui/Badge'

const NUMERIC_KEYS = ['current_price', 'score', 'entry_price', 'stop_loss', 'target_price', 'institutional_ownership', 'short_interest', 'glassdoor_rating', 'employee_growth', 'news_sentiment']
const DEFAULT_SORT = { key: 'investment_score', dir: 'desc' }

function formatNum(val, type) {
  if (val == null) return '–'
  if (type === 'pct') return `${Number(val).toFixed(1)}%`
  if (type === 'score') return Number(val).toFixed(1)
  if (type === 'float') return Number(val).toFixed(2)
  return Number(val).toLocaleString()
}

function riskVariant(level) {
  if (level === '낮음') return 'success'
  if (level === '높음') return 'danger'
  return 'warning'
}

function reliabilityVariant(level) {
  if (level === 'high') return 'success'
  if (level === 'high_risk') return 'danger'
  return 'warning'
}

function reliabilityLabel(level) {
  if (level === 'high') return '고신뢰'
  if (level === 'high_risk') return '고위험'
  return '중신뢰'
}

export default function StockTable({ rows }) {
  const [sort, setSort] = useState(DEFAULT_SORT)

  const sortedRows = useMemo(() => {
    if (!rows?.length) return []
    const k = sort.key
    const dir = sort.dir === 'asc' ? 1 : -1
    return [...rows].sort((a, b) => {
      const va = a[k]
      const vb = b[k]
      if (va == null && vb == null) return 0
      if (va == null) return 1
      if (vb == null) return -1
      const num = typeof va === 'number' && typeof vb === 'number' ? va - vb : String(va).localeCompare(String(vb))
      return num * dir
    })
  }, [rows, sort])

  const toggleSort = (key) => {
    setSort((s) => ({ key, dir: s.key === key && s.dir === 'desc' ? 'asc' : 'desc' }))
  }

  const Th = ({ colKey, label, className }) => (
    <th
      className={`px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted cursor-pointer select-none hover:text-slate-700 ${className || ''}`}
      onClick={() => colKey && toggleSort(colKey)}
    >
      <span className="inline-flex items-center gap-1">
        {label}
        {sort.key === colKey && (sort.dir === 'asc' ? ' ↑' : ' ↓')}
      </span>
    </th>
  )

  if (!sortedRows.length) {
    return (
      <div className="rounded-card border border-surface-border bg-white py-12 text-center text-muted">
        데이터가 없습니다.
      </div>
    )
  }

  return (
    <div className="overflow-x-auto rounded-card border border-surface-border bg-white shadow-card">
      <table className="min-w-full divide-y divide-surface-border">
        <thead className="bg-slate-50/80">
          <tr>
            <Th colKey="ticker" label="종목" />
            <Th colKey="company_name" label="회사명" />
            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted">한글명</th>
            <Th colKey="current_price" label="현재가" className="text-right" />
            <Th colKey="investment_score" label="투자점수" className="text-right" />
            <Th colKey="stock_reliability" label="신뢰도" className="text-right" />
            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted">신뢰구간</th>
            <Th colKey="entry_price" label="진입가" className="text-right" />
            <Th colKey="stop_loss" label="손절가" className="text-right" />
            <Th colKey="target_price" label="목표가" className="text-right" />
            <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-muted">기관</th>
            <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-muted">공매도</th>
            <Th colKey="glassdoor_rating" label="기업평점" className="text-right" />
            <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-muted">직원증가</th>
            <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-muted">감성</th>
            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted">위험도</th>
            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted">업데이트</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-surface-border bg-white">
          {sortedRows.map((row) => (
            <tr key={row.ticker} className="table-row-hover hover:bg-primary-50/30">
              <td className="whitespace-nowrap px-4 py-3">
                <Link to={`/stock/${row.ticker}`} className="font-semibold text-primary-600 hover:text-primary-700 hover:underline">
                  {row.ticker}
                </Link>
              </td>
              <td className="max-w-[180px] truncate px-4 py-3 text-sm text-slate-700" title={row.company_name}>{row.company_name ?? '–'}</td>
              <td className="whitespace-nowrap px-4 py-3 text-sm text-muted">{row.company_name_ko ?? '–'}</td>
              <td className="whitespace-nowrap px-4 py-3 text-right tabular-nums text-slate-900">{row.current_price != null ? formatNum(row.current_price) : '–'}</td>
              <td className="whitespace-nowrap px-4 py-3 text-right tabular-nums font-semibold text-slate-900">{(row.investment_score ?? row.score) != null ? formatNum(row.investment_score ?? row.score, 'score') : '–'}</td>
              <td className="whitespace-nowrap px-4 py-3 text-right tabular-nums text-slate-600">{row.stock_reliability != null ? formatNum(row.stock_reliability, 'score') : '–'}</td>
              <td className="whitespace-nowrap px-4 py-3">
                {row.reliability_level ? <Badge variant={reliabilityVariant(row.reliability_level)}>{reliabilityLabel(row.reliability_level)}</Badge> : '–'}
              </td>
              <td className="whitespace-nowrap px-4 py-3 text-right tabular-nums text-slate-700">{row.entry_price != null ? formatNum(row.entry_price) : '–'}</td>
              <td className="whitespace-nowrap px-4 py-3 text-right tabular-nums text-slate-700">{row.stop_loss != null ? formatNum(row.stop_loss) : '–'}</td>
              <td className="whitespace-nowrap px-4 py-3 text-right tabular-nums text-slate-700">{row.target_price != null ? formatNum(row.target_price) : '–'}</td>
              <td className="whitespace-nowrap px-4 py-3 text-right tabular-nums text-slate-600">{row.institutional_ownership != null ? formatNum(row.institutional_ownership, 'pct') : '–'}</td>
              <td className="whitespace-nowrap px-4 py-3 text-right tabular-nums text-slate-600">{row.short_interest != null ? formatNum(row.short_interest, 'pct') : '–'}</td>
              <td className="whitespace-nowrap px-4 py-3 text-right tabular-nums text-slate-600">{row.glassdoor_rating != null ? formatNum(row.glassdoor_rating, 'score') : '–'}</td>
              <td className="whitespace-nowrap px-4 py-3 text-right tabular-nums text-slate-600">{row.employee_growth != null ? formatNum(row.employee_growth, 'pct') : '–'}</td>
              <td className="whitespace-nowrap px-4 py-3 text-right tabular-nums text-slate-600">{row.news_sentiment != null ? formatNum(row.news_sentiment, 'float') : '–'}</td>
              <td className="whitespace-nowrap px-4 py-3">
                {row.risk_level ? <Badge variant={riskVariant(row.risk_level)}>{row.risk_level}</Badge> : '–'}
              </td>
              <td className="whitespace-nowrap px-4 py-3 text-xs text-muted">{row.last_updated ? new Date(row.last_updated).toLocaleString('ko-KR', { dateStyle: 'short', timeStyle: 'short' }) : '–'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
