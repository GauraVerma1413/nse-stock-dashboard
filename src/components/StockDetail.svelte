<script>
  import { onMount } from 'svelte'
  import { Chart, BarController, BarElement, CategoryScale, LinearScale, Tooltip } from 'chart.js'
  import ICSGauge from './ICSGauge.svelte'
  import { filters } from '../lib/stores.js'
  import { getICS } from '../lib/ics.js'

  Chart.register(BarController, BarElement, CategoryScale, LinearScale, Tooltip)

  let { stock, onAddWatchlist, onAddCompare } = $props()

  let chartCanvas = $state()
  let chartInstance = $state()

  let ics = $derived(getICS(stock, $filters.risk, $filters.horizon))

  onMount(() => {
    if (!stock.revenue_5y?.length) return
    const currentYear = new Date().getFullYear()
    chartInstance = new Chart(chartCanvas, {
      type: 'bar',
      data: {
        labels: stock.revenue_5y.map((_, i) => `${currentYear - stock.revenue_5y.length + i + 1}`),
        datasets: [{
          label: 'Revenue (Cr)',
          data: stock.revenue_5y,
          backgroundColor: '#58a6ff55',
          borderColor: '#58a6ff',
          borderWidth: 1,
          borderRadius: 4
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: false },
          tooltip: { callbacks: { label: ctx => `₹${(ctx.raw / 100).toFixed(0)}K Cr` } }
        },
        scales: {
          x: { ticks: { color: '#8b949e' }, grid: { color: '#30363d' } },
          y: { ticks: { color: '#8b949e' }, grid: { color: '#30363d' } }
        }
      }
    })
    return () => chartInstance?.destroy()
  })
</script>

<div class="detail">
  <div class="detail-header">
    <div>
      <h3>{stock.name} <span class="ticker">({stock.ticker})</span></h3>
      <span class="sector">{stock.sector}</span>
    </div>
    <div class="actions">
      <button onclick={() => onAddWatchlist?.(stock.ticker)}>+ Watchlist</button>
      <button onclick={() => onAddCompare?.(stock.ticker)}>+ Compare</button>
    </div>
  </div>

  {#if stock.warning}
    <div class="warning">⚠ {stock.warning}</div>
  {/if}

  <div class="ics-section">
    <ICSGauge value={ics} />
  </div>

  <div class="grid-2">
    <div class="card">
      <h4>Price Targets (12M)</h4>
      <div class="targets">
        <div><span class="label">Bull</span><span class="positive">₹{stock.bull_target?.toLocaleString()}</span></div>
        <div><span class="label">Bear</span><span class="negative">₹{stock.bear_target?.toLocaleString()}</span></div>
        <div><span class="label">Entry Zone</span><span>₹{stock.entry_zone?.[0]?.toLocaleString()} – ₹{stock.entry_zone?.[1]?.toLocaleString()}</span></div>
        <div><span class="label">Stop Loss</span><span class="negative">₹{stock.stop_loss?.toLocaleString()}</span></div>
      </div>
    </div>

    <div class="card">
      <h4>Fundamentals</h4>
      <div class="targets">
        <div><span class="label">P/E</span><span>{stock.pe?.toFixed(1)}x <span class="text-muted">(sector avg {stock.sector_pe_avg?.toFixed(1)}x)</span></span></div>
        <div><span class="label">D/E Ratio</span><span>{stock.de_ratio?.toFixed(2)}</span></div>
        <div><span class="label">Div Yield</span><span>{stock.div_yield?.toFixed(2)}%</span></div>
        <div><span class="label">Payout</span><span>{stock.payout_ratio?.toFixed(0)}%</span></div>
        <div><span class="label">Moat</span><span class="moat-{stock.moat}">{stock.moat?.toUpperCase()}</span></div>
        <div><span class="label">Risk</span><span>{stock.risk_rating}/10</span></div>
      </div>
    </div>
  </div>

  {#if stock.revenue_5y?.length}
    <div class="card chart-card">
      <h4>Revenue Growth (5 Years) — CAGR {stock.revenue_cagr_5y?.toFixed(1)}%</h4>
      <canvas bind:this={chartCanvas} height="120"></canvas>
    </div>
  {/if}

  {#if stock.ics_breakdown}
    <div class="card breakdown">
      <h4>ICS Breakdown</h4>
      {#each Object.entries(stock.ics_breakdown) as [key, val]}
        <div class="breakdown-row">
          <span class="label">{key.replace(/_/g,' ').replace('score','').trim()}</span>
          <div class="bar-track">
            <div class="bar-fill" style={`width:${Math.min((val/3)*100, 100)}%;background:var(--accent-blue)`}></div>
          </div>
          <span class="val">+{val?.toFixed(1)}</span>
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
  .detail { padding: 16px; background: var(--bg-secondary); border-top: 1px solid var(--accent-blue); }
  .detail-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; }
  h3 { font-size: 16px; margin-bottom: 4px; }
  .ticker { color: var(--text-secondary); font-size: 13px; }
  .sector { font-size: 11px; color: var(--text-secondary); text-transform: uppercase; }
  .actions { display: flex; gap: 8px; }
  .warning { background: #3a2f1a; border: 1px solid var(--accent-orange); border-radius: 6px; padding: 8px 12px; color: var(--accent-orange); font-size: 13px; margin-bottom: 12px; }
  .ics-section { margin-bottom: 16px; }
  .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px; }
  h4 { font-size: 12px; text-transform: uppercase; color: var(--text-secondary); margin-bottom: 10px; }
  .targets { display: flex; flex-direction: column; gap: 6px; }
  .targets div { display: flex; justify-content: space-between; font-size: 13px; }
  .label { color: var(--text-secondary); }
  .text-muted { color: var(--text-muted); font-size: 11px; }
  .moat-strong   { color: var(--accent-green); font-weight: 700; }
  .moat-moderate { color: var(--accent-yellow); font-weight: 700; }
  .moat-weak     { color: var(--accent-red); font-weight: 700; }
  .chart-card { margin-bottom: 12px; }
  .breakdown { }
  .breakdown-row { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; font-size: 12px; }
  .breakdown-row .label { width: 120px; color: var(--text-secondary); text-transform: capitalize; }
  .bar-track { flex: 1; background: var(--bg-hover); border-radius: 3px; height: 6px; }
  .bar-fill { height: 100%; border-radius: 3px; transition: width 0.4s; }
  .val { width: 32px; text-align: right; font-family: var(--font-mono); }

  @media (max-width: 600px) { .grid-2 { grid-template-columns: 1fr; } }
</style>
