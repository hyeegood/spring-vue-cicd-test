import { useState, useEffect } from 'react'
import { getPortfolios, getPortfolio, createPortfolio, addPosition } from '../api'

export default function Portfolio() {
  const [portfolios, setPortfolios] = useState([])
  const [selected, setSelected] = useState(null)
  const [detail, setDetail] = useState(null)
  const [newName, setNewName] = useState('')
  const [addStockId, setAddStockId] = useState('')
  const [addShares, setAddShares] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    getPortfolios().then(setPortfolios).catch(() => setPortfolios([]))
  }, [])

  useEffect(() => {
    if (selected) {
      setLoading(true)
      getPortfolio(selected)
        .then(setDetail)
        .catch(() => setDetail(null))
        .finally(() => setLoading(false))
    } else {
      setDetail(null)
    }
  }, [selected])

  const handleCreate = () => {
    if (!newName.trim()) return
    createPortfolio(newName.trim()).then((p) => {
      setPortfolios((prev) => [...prev, p])
      setSelected(p.id)
      setNewName('')
      getPortfolios().then(setPortfolios)
    })
  }

  const handleAddPosition = () => {
    if (!selected || !addStockId || !addShares) return
    addPosition(selected, parseInt(addStockId, 10), parseFloat(addShares)).then(() => {
      getPortfolio(selected).then(setDetail)
      setAddStockId('')
      setAddShares('')
    })
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">포트폴리오</h1>

      <div className="mb-6 flex gap-2">
        <input
          type="text"
          placeholder="포트폴리오 이름"
          value={newName}
          onChange={(e) => setNewName(e.target.value)}
          className="border rounded px-3 py-2"
        />
        <button onClick={handleCreate} className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
          생성
        </button>
      </div>

      {portfolios.length > 0 && (
        <div className="mb-4">
          <label className="block text-sm text-gray-600 mb-1">선택</label>
          <select
            value={selected ?? ''}
            onChange={(e) => setSelected(e.target.value ? parseInt(e.target.value, 10) : null)}
            className="border rounded px-3 py-2"
          >
            <option value="">선택</option>
            {portfolios.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>
        </div>
      )}

      {detail && (
        <>
          <h2 className="text-lg font-semibold mt-4">{detail.name}</h2>
          {loading ? (
            <p>로딩 중...</p>
          ) : (
            <>
              <ul className="list-disc pl-6 mt-2">
                {(detail.positions || []).map((pos) => (
                  <li key={pos.stock_id}>
                    {pos.ticker}: {pos.shares}주 (점수: {pos.score != null ? pos.score.toFixed(1) : '-'})
                  </li>
                ))}
              </ul>
              <div className="mt-4 flex gap-2">
                <input
                  type="number"
                  placeholder="stock_id"
                  value={addStockId}
                  onChange={(e) => setAddStockId(e.target.value)}
                  className="border rounded px-3 py-2 w-24"
                />
                <input
                  type="number"
                  placeholder="수량"
                  value={addShares}
                  onChange={(e) => setAddShares(e.target.value)}
                  className="border rounded px-3 py-2 w-24"
                />
                <button onClick={handleAddPosition} className="bg-green-600 text-white px-4 py-2 rounded">
                  종목 추가
                </button>
              </div>
            </>
          )}
        </>
      )}
    </div>
  )
}
