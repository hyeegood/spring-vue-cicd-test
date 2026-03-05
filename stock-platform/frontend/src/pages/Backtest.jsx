import { useState } from 'react'
import { runBacktest } from '../api'

export default function Backtest() {
  const [tickers, setTickers] = useState('AAPL,MSFT,GOOGL')
  const [startDate, setStartDate] = useState('2023-01-01')
  const [endDate, setEndDate] = useState('2024-01-01')
  const [entryRule, setEntryRule] = useState('ma20')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleRun = () => {
    setLoading(true)
    setResult(null)
    const list = tickers.split(/[\s,]+/).filter(Boolean)
    runBacktest(list, startDate, endDate, entryRule)
      .then(setResult)
      .catch(() => setResult({ error: '실행 실패' }))
      .finally(() => setLoading(false))
  }

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">백테스트</h1>
      <div className="space-y-4">
        <div>
          <label className="block text-sm text-gray-600">종목 (쉼표 구분)</label>
          <input
            type="text"
            value={tickers}
            onChange={(e) => setTickers(e.target.value)}
            className="border rounded px-3 py-2 w-full"
          />
        </div>
        <div className="flex gap-4">
          <div>
            <label className="block text-sm text-gray-600">시작일</label>
            <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} className="border rounded px-3 py-2" />
          </div>
          <div>
            <label className="block text-sm text-gray-600">종료일</label>
            <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} className="border rounded px-3 py-2" />
          </div>
        </div>
        <div>
          <label className="block text-sm text-gray-600">진입 규칙</label>
          <select value={entryRule} onChange={(e) => setEntryRule(e.target.value)} className="border rounded px-3 py-2">
            <option value="ma20">20일 이평선</option>
            <option value="rsi">RSI &lt; 45</option>
          </select>
        </div>
        <button onClick={handleRun} disabled={loading} className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50">
          {loading ? '실행 중...' : '실행'}
        </button>
      </div>
      {result && !result.error && (
        <div className="mt-6 p-4 bg-gray-50 rounded">
          <h2 className="font-semibold mb-2">결과</h2>
          <p>승률: {(result.win_rate * 100).toFixed(1)}%</p>
          <p>평균 수익률: {(result.avg_return * 100).toFixed(2)}%</p>
          <p>최대 낙폭: {(result.max_drawdown * 100).toFixed(2)}%</p>
        </div>
      )}
      {result?.error && <p className="mt-4 text-red-600">{result.error}</p>}
    </div>
  )
}
