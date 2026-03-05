import { Link } from 'react-router-dom'

const LEVEL_STYLES = {
  high: 'bg-emerald-100 text-emerald-800 border-emerald-200',
  medium: 'bg-amber-100 text-amber-800 border-amber-200',
  high_risk: 'bg-rose-100 text-rose-800 border-rose-200',
}

export default function StockCard({ item }) {
  const level = item.reliability_level || 'medium'
  const levelStyle = LEVEL_STYLES[level] || LEVEL_STYLES.medium
  const invScore = item.investment_score ?? item.score
  const relScore = item.stock_reliability

  return (
    <Link
      to={`/stock/${item.ticker}`}
      className="block rounded-card border border-surface-border bg-white p-4 shadow-card transition-all duration-fast hover:shadow-card-hover hover:border-primary-200"
    >
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0 flex-1">
          <p className="truncate font-semibold text-slate-900">{item.company_name || item.ticker}</p>
          <p className="mt-0.5 text-xs text-muted">{item.company_name_ko || item.ticker}</p>
        </div>
        {item.sector && (
          <span className="shrink-0 rounded border border-slate-200 bg-slate-50 px-2 py-0.5 text-xs text-slate-600">
            {item.sector}
          </span>
        )}
      </div>
      <div className="mt-3 flex items-baseline justify-between gap-2">
        <span className="text-lg font-semibold tabular-nums text-slate-900">
          {item.current_price != null ? Number(item.current_price).toLocaleString() : '–'}
        </span>
        <span className={`rounded border px-2 py-0.5 text-xs font-medium ${levelStyle}`}>
          신뢰도 {relScore != null ? relScore.toFixed(0) : '–'}
        </span>
      </div>
      <div className="mt-2 flex gap-3 text-xs text-muted">
        <span>투자점수 {invScore != null ? invScore.toFixed(1) : '–'}</span>
        <span>섹터신뢰도 {item.sector_reliability != null ? item.sector_reliability.toFixed(0) : '–'}</span>
      </div>
    </Link>
  )
}
