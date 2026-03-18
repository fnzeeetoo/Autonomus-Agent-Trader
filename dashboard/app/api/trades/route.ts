import { NextResponse } from 'next/server'

export async function GET() {
  try {
    const path = process.env.DATA_PATH || '../data/paper_trades/trades.json'
    const file = await import('fs').then(mod => mod.promises.readFile(path, 'utf8')).catch(() => null)
    if (!file) {
      return NextResponse.json({ trades: [] })
    }
    const data = JSON.parse(file)
    return NextResponse.json(data)
  } catch (e) {
    return NextResponse.json({ error: 'Failed to load trades' }, { status: 500 })
  }
}
