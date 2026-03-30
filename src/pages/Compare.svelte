<script>
  import { stockData, compareSelection, filters } from '../lib/stores.js'
  import { getICS } from '../lib/ics.js'
  import ICSGauge from '../components/ICSGauge.svelte'

  let selectedStocks = $derived(
    $compareSelection
      .map(ticker => $stockData.find(s => s.ticker === ticker))
      .filter(Boolean)
      .map(s => ({ ...s, _ics: getICS(s, $filters.risk, $filters.horizon) }))
  )

  const metrics = [
    { key: '_ics',            label: 'ICS Score',       isICS: true },
    { key: 'cmp',             label: 'CMP ₹',           fmt: v => `₹${v?.toLocaleString()}` },
    { key: 'pe',              label: 'P/E',              fmt: v => `${v?.toFixed(1)}x` },
    { key: 'de_ratio',        label: 'D/E',              fmt: v => v?.toFixed(2) },
    { key: 'revenue_cagr_5y', label: 'Rev CAGR 5Y',     fmt: v => `${v?.toFixed(1)}%` },
    { key: 'div_yield',       label: 'Div Yield',        fmt: v => `${v?.toFixed(2)}%` },
    { key: 'moat',            label: 'Moat' },
    { key: 'risk_rating',     label: 'Risk',             fmt: v => `${v}/10` },
    { key: 'bull_target',     label: 'Bull Target',      fmt: v => `₹${v?.toLocaleString()}` },
    { key: 'bear_target',     label: 'Bear Target',      fmt: v => `₹${v?.toLocaleString()}` },
  ]

  function display(metric, stock) {
    const v = stock[metric.key]
    if (metric.isICS) return null  // rendered as ICSGauge
    if (metric.fmt) return metric.fmt(v)
    return v ?? '—'
  }
</script>

<div class="compare">
  {#if selectedStocks.length === 0}
    <div class="empty">
      <p>No stocks selected for comparison.</p>
      <p>Go to <strong>Top Picks</strong> and click <strong>+ Compare</strong> on up to 4 stocks.</p>
    </div>
  {:else}
    <div class="compare-grid" style={`grid-template-columns: 160px repeat(${selectedStocks.length}, 1fr)`}>
      <!-- Header row -->
      <div class="header-cell label-col">Stock</div>
      {#each selectedStocks as s}
        <div class="header-cell stock-col">
          <div class="name">{s.name}</div>
          <div class="ticker">{s.ticker.replace('.NS','')}</div>
          <button onclick={() => compareSelection.update(sel => sel.filter(t => t !== s.ticker))}>✕ Remove</button>
        </div>
      {/each}

      <!-- Metric rows -->
      {#each metrics as m}
        <div class="metric-label">{m.label}</div>
        {#each selectedStocks as s}
          <div class="metric-val">
            {#if m.isICS}
              <ICSGauge value={s._ics} />
            {:else}
              {display(m, s)}
            {/if}
          </div>
        {/each}
      {/each}
    </div>
  {/if}
</div>

<style>
  .compare { padding: 16px; overflow-x: auto; }
  .empty { text-align: center; padding: 80px 20px; color: var(--text-secondary); line-height: 2.5; }
  .compare-grid {
    display: grid;
    gap: 1px;
    background: var(--border);
    border: 1px solid var(--border);
    border-radius: 8px;
    overflow: hidden;
    min-width: 400px;
  }
  .header-cell { background: var(--bg-secondary); padding: 12px; }
  .label-col { background: var(--bg-secondary); }
  .stock-col { text-align: center; }
  .stock-col .name { font-weight: 700; font-size: 13px; margin-bottom: 2px; }
  .stock-col .ticker { font-size: 11px; color: var(--text-muted); margin-bottom: 6px; }
  .metric-label { background: var(--bg-secondary); padding: 10px 12px; font-size: 12px; color: var(--text-secondary); display: flex; align-items: center; }
  .metric-val { background: var(--bg-card); padding: 10px 12px; font-size: 13px; display: flex; align-items: center; }
</style>
