export default function MetricWidget({ label, value, sub, trend, className = '' }) {
  const trendUp = trend === 'up'
  const trendDown = trend === 'down'
  const subClass = trendUp ? 'text-emerald-600' : trendDown ? 'text-rose-600' : 'text-muted'
  return (
    <div className={'rounded-card border border-surface-border bg-white p-4 shadow-card card-hover ' + className}>
      <p className="text-xs font-medium text-muted uppercase tracking-wider">{label}</p>
      <p className="mt-1 text-2xl font-semibold tabular-nums text-slate-900">{value ?? '–'}</p>
      {(sub != null || trend != null) && (
        <p className={'mt-0.5 text-sm tabular-nums ' + subClass}>{sub}</p>
      )}
    </div>
  )
}
