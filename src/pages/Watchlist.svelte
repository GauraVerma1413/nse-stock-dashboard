<script>
  import { stockData, watchlist, livePrices, filters } from '../lib/stores.js'
  import { fetchLivePrices } from '../lib/api.js'
  import StockDetail from '../components/StockDetail.svelte'
  import ICSGauge from '../components/ICSGauge.svelte'
  import { getICS } from '../lib/ics.js'
  import { onMount } from 'svelte'

  let { sectors = [] } = $props()
  let expandedTicker = $state(null)

  let watchlistStocks = $derived(
    $stockData
      .filter(s => $watchlist.includes(s.ticker))
      .map(s => ({ ...s, _ics: getICS(s, $filters.risk, $filters.horizon) }))
  )

  onMount(async () => {
    if (watchlistStocks.length) {
      const prices = await fetchLivePrices(watchlistStocks.map(s => s.ticker))
      livePrices.update(p => ({ ...p, ...prices }))
    }
  })
</script>

<div class="watchlist-page">
  {#if watchlistStocks.length === 0}
    <div class="empty">
      <p>Your watchlist is empty.</p>
      <p>Go to <strong>Top Picks</strong> and click <strong>+ Watchlist</strong> on any stock.</p>
    </div>
  {:else}
    <table>
      <thead>
        <tr>
          <th>Stock</th>
          <th>CMP ₹</th>
          <th>Day %</th>
          <th>ICS</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        {#each watchlistStocks as stock}
          <tr
            class="stock-row"
            onclick={() => expandedTicker = expandedTicker === stock.ticker ? null : stock.ticker}
          >
            <td>
              <div class="stock-name">{stock.name}</div>
              <div class="stock-ticker">{stock.ticker.replace('.NS','')}</div>
            </td>
            <td class="mono">₹{($livePrices[stock.ticker]?.price ?? stock.cmp)?.toLocaleString()}</td>
            <td>
              {#if $livePrices[stock.ticker]}
                <span class:positive={$livePrices[stock.ticker].changePct >= 0}
                      class:negative={$livePrices[stock.ticker].changePct < 0}>
                  {$livePrices[stock.ticker].changePct >= 0 ? '+' : ''}{$livePrices[stock.ticker].changePct.toFixed(2)}%
                </span>
              {:else}—{/if}
            </td>
            <td><ICSGauge value={stock._ics} /></td>
            <td>
              <button onclick={(e) => { e.stopPropagation(); watchlist.remove(stock.ticker) }}>Remove</button>
            </td>
          </tr>
          {#if expandedTicker === stock.ticker}
            <tr><td colspan="5" style="padding:0">
              <StockDetail {stock} onAddWatchlist={() => {}} onAddCompare={() => {}} />
            </td></tr>
          {/if}
        {/each}
      </tbody>
    </table>
  {/if}
</div>

<style>
  .watchlist-page { padding: 16px; }
  .empty { text-align: center; padding: 80px 20px; color: var(--text-secondary); line-height: 2.5; }
  .stock-row { cursor: pointer; }
  .stock-name { font-weight: 600; font-size: 13px; }
  .stock-ticker { font-size: 11px; color: var(--text-muted); }
  .mono { font-family: var(--font-mono); }
</style>
