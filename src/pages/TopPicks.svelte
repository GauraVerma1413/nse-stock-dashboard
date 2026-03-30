<script>
  import VirtualList from 'svelte-virtual-list'
  import FilterBar from '../components/FilterBar.svelte'
  import StockDetail from '../components/StockDetail.svelte'
  import ICSGauge from '../components/ICSGauge.svelte'
  import { stockData, filters, watchlist, compareSelection, livePrices } from '../lib/stores.js'
  import { applyFilters } from '../lib/screener.js'
  import { fetchLivePrices } from '../lib/api.js'

  let { sectors = [] } = $props()

  let expandedTicker = $state(null)

  let filtered = $derived(applyFilters($stockData, $filters))

  // Fetch live prices for top 20 whenever filter changes
  $effect(() => {
    const topTickers = filtered.slice(0, 20).map(s => s.ticker)
    if (topTickers.length) {
      fetchLivePrices(topTickers).then(prices => {
        livePrices.update(p => ({ ...p, ...prices }))
      })
    }
  })

  function toggleExpand(ticker) {
    expandedTicker = expandedTicker === ticker ? null : ticker
  }

  function moatStars(moat) {
    if (moat === 'strong')   return '●●●'
    if (moat === 'moderate') return '●●○'
    return '●○○'
  }
</script>

<FilterBar {sectors} />

<div class="table-wrap">
  <div class="results-count">
    Showing {filtered.length.toLocaleString()} of {$stockData.length.toLocaleString()} stocks
  </div>

  <table class="header-table">
    <thead>
      <tr>
        <th style="width:40px">#</th>
        <th>Stock</th>
        <th>CMP ₹</th>
        <th>Day %</th>
        <th>P/E</th>
        <th>D/E</th>
        <th>Rev CAGR</th>
        <th>Moat</th>
        <th>Risk</th>
        <th>ICS</th>
      </tr>
    </thead>
  </table>

  <div class="list-wrap">
    <VirtualList items={filtered} let:item={stock} let:index itemHeight={52}>
      <div class="row-wrap">
        <div
          class="stock-row"
          class:expanded={expandedTicker === stock.ticker}
          onclick={() => toggleExpand(stock.ticker)}
          role="button"
          tabindex="0"
          onkeydown={(e) => e.key === 'Enter' && toggleExpand(stock.ticker)}
        >
          <span class="cell rank">{index + 1}</span>
          <span class="cell name-cell">
            <span class="stock-name">{stock.name}</span>
            <span class="stock-ticker">{stock.ticker.replace('.NS','')}</span>
          </span>
          <span class="cell mono">
            ₹{($livePrices[stock.ticker]?.price ?? stock.cmp)?.toLocaleString()}
          </span>
          <span class="cell">
            {#if $livePrices[stock.ticker]}
              <span class:positive={$livePrices[stock.ticker].changePct >= 0}
                    class:negative={$livePrices[stock.ticker].changePct < 0}>
                {$livePrices[stock.ticker].changePct >= 0 ? '+' : ''}{$livePrices[stock.ticker].changePct.toFixed(2)}%
              </span>
            {:else}—{/if}
          </span>
          <span class="cell">{stock.pe?.toFixed(1)}x</span>
          <span class="cell">{stock.de_ratio?.toFixed(2)}</span>
          <span class="cell"
            class:positive={stock.revenue_cagr_5y >= 15}
            class:negative={stock.revenue_cagr_5y < 5}>
            {stock.revenue_cagr_5y?.toFixed(1)}%
          </span>
          <span class="cell mono moat-{stock.moat}">{moatStars(stock.moat)}</span>
          <span class="cell">{stock.risk_rating}/10</span>
          <span class="cell ics-cell"><ICSGauge value={stock._ics} /></span>
        </div>
        {#if expandedTicker === stock.ticker}
          <div class="detail-wrap">
            <StockDetail {stock}
              onAddWatchlist={(t) => watchlist.add(t)}
              onAddCompare={(t) => compareSelection.update(s => s.includes(t) ? s : [...s, t].slice(-4))}
            />
          </div>
        {/if}
      </div>
    </VirtualList>
  </div>
</div>

<style>
  .table-wrap { display: flex; flex-direction: column; height: calc(100vh - 160px); overflow: hidden; }
  .results-count { padding: 8px 16px; font-size: 12px; color: var(--text-secondary); border-bottom: 1px solid var(--border); background: var(--bg-primary); }
  .header-table { width: 100%; border-collapse: collapse; }
  .list-wrap { flex: 1; overflow: auto; }

  .row-wrap { border-bottom: 1px solid var(--border); }
  .stock-row {
    display: grid;
    grid-template-columns: 40px 1fr 90px 70px 60px 50px 80px 60px 55px 180px;
    align-items: center;
    padding: 6px 12px;
    cursor: pointer;
    transition: background 0.1s;
  }
  .stock-row:hover { background: var(--bg-hover); }
  .stock-row.expanded { background: var(--bg-hover); }

  .cell { font-size: 13px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .rank { color: var(--text-muted); font-size: 12px; }
  .name-cell { display: flex; flex-direction: column; }
  .stock-name { font-size: 13px; font-weight: 600; }
  .stock-ticker { font-size: 11px; color: var(--text-muted); }
  .mono { font-family: var(--font-mono); }
  .ics-cell { min-width: 160px; }
  .moat-strong   { color: var(--accent-green); }
  .moat-moderate { color: var(--accent-yellow); }
  .moat-weak     { color: var(--accent-red); }

  /* Match header column widths */
  :global(.header-table th:nth-child(1)) { width: 40px; }
  :global(.header-table th:nth-child(3)) { width: 90px; }
  :global(.header-table th:nth-child(4)) { width: 70px; }
</style>
