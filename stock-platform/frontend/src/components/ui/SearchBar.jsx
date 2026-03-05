import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

export default function SearchBar({ placeholder = '종목 검색 (티커 또는 이름)', className = '' }) {
  const [q, setQ] = useState('')
  const navigate = useNavigate()

  const handleSubmit = (e) => {
    e.preventDefault()
    const ticker = (q || '').trim().toUpperCase()
    if (ticker) navigate(`/stock/${ticker}`)
  }

  return (
    <form onSubmit={handleSubmit} className={'flex ' + className}>
      <div className="relative flex-1 max-w-md">
        <span className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-muted">
          <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </span>
        <input
          type="text"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder={placeholder}
          className="w-full rounded-button border border-surface-border bg-white py-2 pl-9 pr-4 text-sm text-slate-900 placeholder-muted focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
        />
      </div>
      <button type="submit" className="ml-2 rounded-button bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700 transition-colors">
        검색
      </button>
    </form>
  )
}
