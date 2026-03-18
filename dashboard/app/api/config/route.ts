import { NextResponse } from 'next/server'
import fs from 'fs/promises'
import path from 'path'
import yaml from 'yaml'

const configDir = path.join(process.cwd(), '..', 'config')

export async function GET() {
  try {
    const [stratYaml, riskYaml] = await Promise.all([
      fs.readFile(path.join(configDir, 'strategies.yaml'), 'utf8'),
      fs.readFile(path.join(configDir, 'risk.yaml'), 'utf8')
    ])
    const strategies = yaml.parse(stratYaml)
    const risk = yaml.parse(riskYaml)
    return NextResponse.json({ strategies, risk })
  } catch (e) {
    return NextResponse.json({ error: 'Failed to read config files' }, { status: 500 })
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json()
    const { strategies, risk } = body
    await fs.writeFile(path.join(configDir, 'strategies.yaml'), yaml.stringify(strategies, { lineWidth: 0 }), 'utf8')
    await fs.writeFile(path.join(configDir, 'risk.yaml'), yaml.stringify(risk, { lineWidth: 0 }), 'utf8')
    return NextResponse.json({ success: true })
  } catch (e) {
    return NextResponse.json({ error: 'Failed to write config files' }, { status: 500 })
  }
}
