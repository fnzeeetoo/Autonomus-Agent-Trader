// Data fetching utilities

export async function getEquityCurve(): Promise<number[]> {
  const res = await fetch('/api/equity')
  if (!res.ok) throw new Error('Failed to fetch equity curve')
  const json = await res.json()
  return json.equity_curve || json
}

export async function getTrades(): Promise<any[]> {
  const res = await fetch('/api/trades')
  if (!res.ok) throw new Error('Failed to fetch trades')
  const json = await res.json()
  return json.trades || json
}
