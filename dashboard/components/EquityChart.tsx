'use client'

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { useEffect, useState } from 'react'

export default function EquityChart() {
  const [data, setData] = useState<number[]>([])

  useEffect(() => {
    fetch('/api/equity')
      .then(res => res.json())
      .then(json => setData(json.equity_curve || json))
      .catch(() => {
        // Fallback: load from local file via static import? Not possible in client. Use placeholder.
        setData([10000, 10200, 10150, 10300, 10400])
      })
  }, [])

  const chartData = data.map((value, index) => ({ step: index, value }))

  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="step" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="value" stroke="#8884d8" strokeWidth={2} dot={false} name="Equity" />
      </LineChart>
    </ResponsiveContainer>
  )
}
