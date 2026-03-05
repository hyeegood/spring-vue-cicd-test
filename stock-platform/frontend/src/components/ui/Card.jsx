export default function Card({ title, children, className, hover }) {
  const h = hover !== false
  return (
    <div className={`bg-white rounded-card border border-surface-border shadow-card ${h ? 'card-hover' : ''} ${className || ''}`}>
      {title && (
        <div className="px-5 py-4 border-b border-surface-border">
          <h3 className="text-sm font-semibold text-slate-800 tracking-tight">{title}</h3>
        </div>
      )}
      <div className="p-5">{children}</div>
    </div>
  )
}
