<script>
  import { stockData } from '../lib/stores.js'
  import { unusualVolume } from '../lib/screener.js'
  import { fetchLivePrices } from '../lib/api.js'
  import { onMount } from 'svelte'

  let viewMode = $state('today')
  let livePriceMap = $state({})
  let loading = $state(true)

  let volumeLeaders = $derived(
    [...$stockData]
      .filter(s => (s.volume_today ?? 0) > 0)
      .sort((a, b) => (b.volume_today ?? 0) - (a.volume_today ?? 0))
      .slice(0, 10)
  )

  let alerts = $derived(unusualVolume($stockData, 2))

  let sectorGroups = $derived.by(() => {
    const groups = {}
    for (const s of $stockData) {
      if (!groups[s.sector]) groups[s.sector] = { count: 0 }
      groups[s.sector].count++
    }
    return Object.entries(groups)
  })

  onMount(async () => {
    const tickers = volumeLeaders.slice(0, 10).map(s => s.ticker)
    if (tickers.length) {
      livePriceMap = await fetchLivePrices(tickers)
    }
    loading = false
  })

  function sectorBg(changePct) {
    if (changePct > 1.5)  return '#1a3a23'
    if (changePct > 0)    return '#1a2a1a'
    if (changePct > -1.5) return '#2a1a1a'
    return '#3a1a1a'
  }

  function sectorColor(changePct) {
    if (changePct > 0) return 'var(--accent-green)'
    if (changePct < 0) return 'var(--accent-red)'
    return 'var(--text-secondary)'
  }

  function formatVol(v) {
    if (!v) return '—'
    if (v >= 1e7) return `${(v / 1e7).toFixed(1)} Cr`
    if (v >= 1e5) return `${(v / 1e5).toFixed(1)} L`
    return v.toLocaleString()
  }
</script>

<div class="pulse">
  <section class="volume-section">
    <div class="section-header">
      <h2>Top Volume Leaders</h2>
      <div class="btn-group">
        {#each ['today', 'week', 'month'] as m}
          <button class:active={viewMode === m} onclick={() => viewMode = m}>
            {m.charAt(0).toUpperCase() + m.slice(1)}
          </button>
        {/each}
      </div>
    </div>

    {#if loading}
      <p class="muted">Loading live data…</p>
    {:else if volumeLeaders.length === 0}
      <p class="muted">No volume data available yet. Run the GitHub Action to populate data.</p>
    {:else}
      <div class="leader-list">
        {#each volumeLeaders as s, i}
          {@const live = livePriceMap[s.ticker]}
          {@const maxVol = volumeLeaders[0]?.volume_today ?? 1}
          <div class="leader-row">
            <span class="rank">{i + 1}</span>
            <div class="stock-info">
              <span class="name">{s.name}</span>
              <span class="ticker">{s.ticker.replace('.NS','')}</span>
            </div>
            <div class="bar-wrap">
              <div class="bar" style={`width:${((s.volume_today ?? 0) / maxVol) * 100}%`}></div>
            </div>
            <span class="vol">{formatVol(s.volume_today)}</span>
            <span class:positive={live?.changePct >= 0} class:negative={live?.changePct < 0} class="chg">
              {live ? `${live.changePct >= 0 ? '+' : ''}${live.changePct.toFixed(2)}%` : '—'}
            </span>
          </div>
        {/each}
      </div>
    {/if}
  </section>

  <section class="heatmap-section">
    <h2>Sector Heatmap</h2>
    <div class="heatmap">
      {#each sectorGroups as [sector, data]}
        <div class="sector-tile" style={`background:${sectorBg(0)};border:1px solid var(--border)`}>
          <div class="sector-name">{sector}</div>
          <div class="sector-count">{data.count} stocks</div>
        </div>
      {/each}
    </div>
  </section>

  <section class="alerts-section">
    <h2>⚡ Unusual Volume Alerts <span class="sub">Stocks trading &gt;2× their 30-day average</span></h2>
    {#if alerts.length === 0}
      <p class="muted">No unusual volume detected. Data updates every 15 min via GitHub Action.</p>
    {:else}
      {#each alerts as s}
        {@const multiple = ((s.volume_today ?? 0) / s.volume_30d_avg).toFixed(1)}
        <div class="alert-row">
          <span class="alert-icon">⚡</span>
          <div class="alert-info">
            <span class="name">{s.name}</span>
            <span class="ticker">{s.ticker.replace('.NS','')}</span>
          </div>
          <span class="multiple">{multiple}× avg volume</span>
          <span class="muted">possible breakout or institutional activity</span>
        </div>
      {/each}
    {/if}
  </section>
</div>

<style>
  .pulse { padding: 20px; display: flex; flex-direction: column; gap: 32px; max-width: 1000px; }
  h2 { font-size: 15px; font-weight: 700; margin-bottom: 12px; }
  .section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
  .btn-group { display: flex; gap: 4px; }
  .leader-row { display: flex; align-items: center; gap: 10px; padding: 8px 0; border-bottom: 1px solid var(--border); }
  .rank { width: 20px; color: var(--text-muted); font-size: 12px; flex-shrink: 0; }
  .stock-info { width: 180px; flex-shrink: 0; }
  .name { font-size: 13px; font-weight: 600; display: block; }
  .ticker { font-size: 11px; color: var(--text-muted); }
  .bar-wrap { flex: 1; background: var(--bg-hover); border-radius: 3px; height: 8px; min-width: 80px; }
  .bar { height: 100%; background: var(--accent-blue); border-radius: 3px; transition: width 0.3s; }
  .vol { width: 80px; text-align: right; font-family: var(--font-mono); font-size: 13px; flex-shrink: 0; }
  .chg { width: 70px; text-align: right; font-family: var(--font-mono); font-size: 13px; flex-shrink: 0; }
  .heatmap { display: grid; grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); gap: 8px; }
  .sector-tile { padding: 12px; border-radius: 8px; }
  .sector-name { font-size: 12px; font-weight: 600; margin-bottom: 4px; }
  .sector-count { font-size: 10px; color: var(--text-muted); }
  .alert-row { display: flex; align-items: center; gap: 12px; padding: 10px 0; border-bottom: 1px solid var(--border); flex-wrap: wrap; }
  .alert-icon { font-size: 16px; flex-shrink: 0; }
  .alert-info { width: 200px; flex-shrink: 0; }
  .multiple { color: var(--accent-yellow); font-weight: 700; font-family: var(--font-mono); }
  .muted { color: var(--text-muted); font-size: 12px; }
  .sub { font-size: 12px; color: var(--text-muted); font-weight: 400; margin-left: 8px; }
</style>
