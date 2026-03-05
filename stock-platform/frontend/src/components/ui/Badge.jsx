const variants = {
  success: 'bg-emerald-100 text-emerald-800 border-emerald-200',
  warning: 'bg-amber-100 text-amber-800 border-amber-200',
  danger: 'bg-rose-100 text-rose-800 border-rose-200',
  neutral: 'bg-slate-100 text-slate-700 border-slate-200',
  primary: 'bg-primary-100 text-primary-800 border-primary-200',
}

export default function Badge({ children, variant = 'neutral', className = '' }) {
  return (
    <span
      className={`
        inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-medium
        ${variants[variant] || variants.neutral}
        ${className}
      `}
    >
      {children}
    </span>
  )
}
