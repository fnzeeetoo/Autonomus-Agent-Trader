'use client'

import { useEffect, useState } from 'react'

interface StrategyState {
  contrarian: { enabled: boolean; rsi_period: number; rsi_overbought: number; rsi_oversold: number; panic_volume_multiplier: number }
  tbo_trend: { enabled: boolean; fast_period: number; slow_period: number }
  tbt_divergence: { enabled: boolean; indicator_period: number; divergence_threshold: number }
  late_entry: { enabled: boolean; entry_minutes_before_close: number; stability_window: number }
}

interface RiskState {
  position_sizing_fixed: number
  position_sizing_pct: number
  circuit_breaker_losses: number
  daily_loss_limit: number
  adx_threshold: number
  bollinger_volatility_cap: number
}

export default function StrategyConfig() {
  const [strat, setStrat] = useState<StrategyState>({
    contrarian: { enabled: true, rsi_period: 14, rsi_overbought: 70, rsi_oversold: 30, panic_volume_multiplier: 2.0 },
    tbo_trend: { enabled: true, fast_period: 10, slow_period: 30 },
    tbt_divergence: { enabled: true, indicator_period: 14, divergence_threshold: 0.05 },
    late_entry: { enabled: true, entry_minutes_before_close: 15, stability_window: 5 }
  })
  const [risk, setRisk] = useState<RiskState>({
    position_sizing_fixed: 20.0,
    position_sizing_pct: 0.02,
    circuit_breaker_losses: 3,
    daily_loss_limit: -100.0,
    adx_threshold: 25.0,
    bollinger_volatility_cap: 2.0
  })
  const [saving, setSaving] = useState(false)

  const saveConfig = async () => {
    setSaving(true)
    try {
      await fetch('/api/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ strategies: strat, risk })
      })
      alert('Configuration saved.')
    } catch (err) {
      alert('Error saving config')
    } finally {
      setSaving(false)
    }
  }

  const updateStrategy = (key: keyof StrategyState, field: string, value: any) => {
    setStrat(prev => ({ ...prev, [key]: { ...prev[key], [field]: value } }))
  }

  const updateRisk = (field: keyof RiskState, value: any) => {
    setRisk(prev => ({ ...prev, [field]: value }))
  }

  return (
    <div className="space-y-8">
      <section>
        <h2 className="text-xl font-semibold mb-2">Strategies</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="border p-4 rounded">
            <h3 className="font-bold">Contrarian</h3>
            <label className="block mt-2">
              <input type="checkbox" checked={strat.contrarian.enabled} onChange={e => updateStrategy('contrarian', 'enabled', e.target.checked)} /> Enabled
            </label>
            <div className="grid grid-cols-2 gap-2 mt-2">
              <div>
                <label>RSI Period</label>
                <input type="number" className="w-full border p-1" value={strat.contrarian.rsi_period} onChange={e => updateStrategy('contrarian', 'rsi_period', parseInt(e.target.value))} />
              </div>
              <div>
                <label>Overbought</label>
                <input type="number" className="w-full border p-1" value={strat.contrarian.rsi_overbought} onChange={e => updateStrategy('contrarian', 'rsi_overbought', parseInt(e.target.value))} />
              </div>
              <div>
                <label>Oversold</label>
                <input type="number" className="w-full border p-1" value={strat.contrarian.rsi_oversold} onChange={e => updateStrategy('contrarian', 'rsi_oversold', parseInt(e.target.value))} />
              </div>
              <div>
                <label>Volume Multiplier</label>
                <input type="number" step="0.1" className="w-full border p-1" value={strat.contrarian.panic_volume_multiplier} onChange={e => updateStrategy('contrarian', 'panic_volume_multiplier', parseFloat(e.target.value))} />
              </div>
            </div>
          </div>

          <div className="border p-4 rounded">
            <h3 className="font-bold">TBO Trend</h3>
            <label className="block mt-2">
              <input type="checkbox" checked={strat.tbo_trend.enabled} onChange={e => updateStrategy('tbo_trend', 'enabled', e.target.checked)} /> Enabled
            </label>
            <div className="grid grid-cols-2 gap-2 mt-2">
              <div>
                <label>Fast Period</label>
                <input type="number" className="w-full border p-1" value={strat.tbo_trend.fast_period} onChange={e => updateStrategy('tbo_trend', 'fast_period', parseInt(e.target.value))} />
              </div>
              <div>
                <label>Slow Period</label>
                <input type="number" className="w-full border p-1" value={strat.tbo_trend.slow_period} onChange={e => updateStrategy('tbo_trend', 'slow_period', parseInt(e.target.value))} />
              </div>
            </div>
          </div>

          <div className="border p-4 rounded">
            <h3 className="font-bold">TBT Divergence</h3>
            <label className="block mt-2">
              <input type="checkbox" checked={strat.tbt_divergence.enabled} onChange={e => updateStrategy('tbt_divergence', 'enabled', e.target.checked)} /> Enabled
            </label>
            <div className="grid grid-cols-2 gap-2 mt-2">
              <div>
                <label>Indicator Period</label>
                <input type="number" className="w-full border p-1" value={strat.tbt_divergence.indicator_period} onChange={e => updateStrategy('tbt_divergence', 'indicator_period', parseInt(e.target.value))} />
              </div>
              <div>
                <label>Divergence Threshold</label>
                <input type="number" step="0.01" className="w-full border p-1" value={strat.tbt_divergence.divergence_threshold} onChange={e => updateStrategy('tbt_divergence', 'divergence_threshold', parseFloat(e.target.value))} />
              </div>
            </div>
          </div>

          <div className="border p-4 rounded">
            <h3 className="font-bold">Late Entry</h3>
            <label className="block mt-2">
              <input type="checkbox" checked={strat.late_entry.enabled} onChange={e => updateStrategy('late_entry', 'enabled', e.target.checked)} /> Enabled
            </label>
            <div className="grid grid-cols-2 gap-2 mt-2">
              <div>
                <label>Entry Min Before Close</label>
                <input type="number" className="w-full border p-1" value={strat.late_entry.entry_minutes_before_close} onChange={e => updateStrategy('late_entry', 'entry_minutes_before_close', parseInt(e.target.value))} />
              </div>
              <div>
                <label>Stability Window (ticks)</label>
                <input type="number" className="w-full border p-1" value={strat.late_entry.stability_window} onChange={e => updateStrategy('late_entry', 'stability_window', parseInt(e.target.value))} />
              </div>
            </div>
          </div>
        </div>
      </section>

      <section>
        <h2 className="text-xl font-semibold mb-2">Risk Parameters</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <div>
            <label>Fixed Position Size ($)</label>
            <input type="number" step="1" className="w-full border p-1" value={risk.position_sizing_fixed} onChange={e => updateRisk('position_sizing_fixed', parseFloat(e.target.value))} />
          </div>
          <div>
            <label>Percentage Position Size</label>
            <input type="number" step="0.001" className="w-full border p-1" value={risk.position_sizing_pct} onChange={e => updateRisk('position_sizing_pct', parseFloat(e.target.value))} />
          </div>
          <div>
            <label>Circuit Breaker Losses</label>
            <input type="number" step="1" className="w-full border p-1" value={risk.circuit_breaker_losses} onChange={e => updateRisk('circuit_breaker_losses', parseInt(e.target.value))} />
          </div>
          <div>
            <label>Daily Loss Limit ($)</label>
            <input type="number" step="1" className="w-full border p-1" value={risk.daily_loss_limit} onChange={e => updateRisk('daily_loss_limit', parseFloat(e.target.value))} />
          </div>
          <div>
            <label>ADX Threshold</label>
            <input type="number" step="0.1" className="w-full border p-1" value={risk.adx_threshold} onChange={e => updateRisk('adx_threshold', parseFloat(e.target.value))} />
          </div>
          <div>
            <label>Bollinger Volatility Cap</label>
            <input type="number" step="0.1" className="w-full border p-1" value={risk.bollinger_volatility_cap} onChange={e => updateRisk('bollinger_volatility_cap', parseFloat(e.target.value))} />
          </div>
        </div>
      </section>

      <button className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50" onClick={saveConfig} disabled={saving}>
        {saving ? 'Saving...' : 'Save Configuration'}
      </button>
    </div>
  )
}
