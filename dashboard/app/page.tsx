'use client'

import EquityChart from '@/app/components/EquityChart'

export default function HomePage() {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Equity Curve</h1>
      <EquityChart />
    </div>
  )
}
