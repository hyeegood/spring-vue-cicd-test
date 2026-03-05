const variants = {
  primary: 'bg-primary-600 text-white border-transparent hover:bg-primary-700 shadow-sm',
  secondary: 'bg-slate-100 text-slate-700 border-slate-200 hover:bg-slate-200',
  ghost: 'bg-transparent text-slate-600 hover:bg-slate-100 border-transparent',
}

export default function Button({ children, variant, type, disabled, className, ...props }) {
  const v = variant || 'primary'
  return (
    <button
      type={type || 'button'}
      disabled={disabled}
      className={`inline-flex items-center justify-center rounded-button border px-4 py-2 text-sm font-medium transition-all duration-fast disabled:opacity-50 disabled:cursor-not-allowed ${variants[v] || variants.primary} ${className || ''}`}
      {...props}
    >
      {children}
    </button>
  )
}
