<script>
  import { stockData, filters } from '../lib/stores.js'
  import { getICS } from '../lib/ics.js'

  let sectorGroups = $derived(() => {
    const groups = {}
    for (const s of $stockData) {
      if (!groups[s.sector]) groups[s.sector] = []
      const withICS = { ...s, _ics: getICS(s, $filters.risk, $filters.horizon) }
      groups[s.sector].push(withICS)
    }
    return Object.entries(groups)
      .map(([sector, stocks]) => {
        stocks.sort((a, b) => b._ics - a._ics)
        const avgICS = stocks.reduce((sum, s) => sum + s._ics, 0) / stocks.length
        return { sector, stocks, avgICS, best: stocks[0] }
      })
      .sort((a, b) => b.avgICS - a.avgICS)
  })
</script>

<div class="sector-view">
  {#each sectorGroups() as g}
    <div class="card sector-card">
      <div class="sector-header">
        <div>
          <h3>{g.sector}</h3>
          <span class="count">{g.stocks.length} stocks</span>
        </div>
        <div class="avg-ics">Avg ICS <strong>{g.avgICS.toFixed(1)}</strong></div>
      </div>
      <div class="best-pick">
        <span class="label">Best Pick:</span>
        <strong>{g.best.name}</strong>
        <span class="ticker">{g.best.ticker.replace('.NS','')}</span>
        <span class="ics-val">ICS {g.best._ics}/10</span>
      </div>
    </div>
  {/each}
</div>

<style>
  .sector-view { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 12px; padding: 16px; }
  .sector-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px; }
  h3 { font-size: 14px; font-weight: 700; }
  .count { font-size: 11px; color: var(--text-muted); }
  .avg-ics { font-size: 13px; color: var(--text-secondary); }
  .avg-ics strong { color: var(--accent-blue); }
  .best-pick { font-size: 13px; display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
  .label { color: var(--text-muted); font-size: 11px; }
  .ticker { color: var(--text-muted); font-size: 11px; }
  .ics-val { color: var(--accent-green); font-weight: 700; margin-left: auto; }
</style>
