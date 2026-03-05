import { NavLink } from 'react-router-dom'

const navItems = [
  { to: '/', label: '대시보드' },
  { to: '/rankings', label: '종목 발견' },
  { to: '/portfolio', label: '포트폴리오' },
  { to: '/backtest', label: '백테스트' },
]

export default function Sidebar() {
  return (
    <aside className="fixed left-0 top-0 z-30 h-full w-56 border-r border-surface-border bg-white shadow-sm">
      <div className="flex h-14 items-center border-b border-surface-border px-5">
        <span className="text-lg font-semibold text-slate-900">Stock Analytics</span>
      </div>
      <nav className="space-y-0.5 p-3">
        {navItems.map(({ to, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `flex items-center rounded-button px-3 py-2.5 text-sm font-medium transition-colors
              ${isActive ? 'bg-primary-50 text-primary-700' : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'}`
            }
          >
            {label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
