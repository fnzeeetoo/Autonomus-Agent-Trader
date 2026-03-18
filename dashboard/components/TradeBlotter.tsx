'use client'

import { useEffect, useState } from 'react'

interface Trade {
  id: string
  timestamp: string
  symbol: string
  side: 'buy' | 'sell'
  quantity: number
  price: number
  pnl?: number
}

export default function TradeBlotter() {
  const [trades, setTrades] = useState<Trade[]>([])

  useEffect(() => {
    fetch('/api/trades')
      .then(res => res.json())
      .then(json => setTrades(json.trades || json))
      .catch(() => setTrades([]))
  }, [])

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full bg-white border">
        <thead>
          <tr className="bg-gray-200">
            <th className="py-2 px-4">Time</th>
            <th className="py-2 px-4">Symbol</th>
            <th className="py-2 px-4">Side</th>
            <th className="py-2 px-4">Qty</th>
            <th className="py-2 px-4">Price</th>
            <th className="py-2 px-4">P&L</th>
          </tr>
        </thead>
        <tbody>
          {trades.length === 0 ? (
            <tr><td colSpan={6} className="text-center py-4">No trades</td></tr>
          ) : (
            trades.map(t => (
              <tr key={t.id}>
                <td className="py-2 px-4 border">{new Date(t.timestamp).toLocaleString()}</td>
                <td className="py-2 px-4 border">{t.symbol}</td>
                <td className="py-2 px-4 border">{t.side}</td>
                <td className="py-2 px-4 border">{t.quantity.toFixed(4)}</td>
                <td className="py-2 px-4 border">{t.price.toFixed(4)}</td>
                <td className="py-2 px-4 border">{t.pnl !== undefined ? t.pnl.toFixed(2) : '-'}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  )
}
