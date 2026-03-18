import { NextResponse } from 'next/server'

export async function GET() {
  try {
    const path = process.env.DATA_PATH || '../data/paper_trades/equity_curve.json'
    const file = await import('fs').then(mod => mod.promises.readFile(path, 'utf8')).catch(() => null)
    if (!file) {
      // return placeholder
      return NextResponse.json({ equity_curve: [10000, 10200, 10150, 10300, 10400] })
    }
    const data = JSON.parse(file)
    return NextResponse.json(data)
  } catch (e) {
    return NextResponse.json({ error: 'Failed to load equity curve' }, { status: 500 })
  }
}
