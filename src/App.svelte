<script>
  import { onMount } from 'svelte'
  import { stockData, lastUpdated, dataLoading, dataError, activeTab } from './lib/stores.js'
  import { loadScreenedData } from './lib/api.js'
  import { getSectors } from './lib/screener.js'

  // Lazy imports for pages — avoids loading all pages upfront
  import TopPicks from './pages/TopPicks.svelte'
  import Watchlist from './pages/Watchlist.svelte'
  import SectorView from './pages/SectorView.svelte'
  import Compare from './pages/Compare.svelte'
  import MarketPulse from './pages/MarketPulse.svelte'

  let sectors = $state([])

  const tabs = [
    { id: 'top-picks',    label: 'Top Picks' },
    { id: 'watchlist',    label: 'My Watchlist' },
    { id: 'sector-view',  label: 'Sector View' },
    { id: 'compare',      label: 'Compare' },
    { id: 'market-pulse', label: 'Market Pulse' }
  ]

  onMount(async () => {
    try {
      const json = await loadScreenedData()
      stockData.set(json.stocks)
      lastUpdated.set(json.last_updated)
      sectors = getSectors(json.stocks)
    } catch (e) {
      dataError.set(e.message)
    } finally {
      dataLoading.set(false)
    }
  })
</script>

<div class="app">
  <header>
    <div class="header-left">
      <h1>📈 NSE Stock Screener</h1>
      {#if $lastUpdated}
        <span class="last-updated">Updated: {new Date($lastUpdated).toLocaleString('en-IN')}</span>
      {/if}
    </div>
    <div class="header-right">
      {#if $dataLoading}
        <span class="loading-dot">Loading data…</span>
      {:else if $dataError}
        <span class="error-dot">⚠ {$dataError}</span>
      {:else}
        <span class="ok-dot">✓ {$stockData.length} stocks loaded</span>
      {/if}
    </div>
  </header>

  <nav>
    {#each tabs as tab}
      <button class:active={$activeTab === tab.id} onclick={() => activeTab.set(tab.id)}>
        {tab.label}
      </button>
    {/each}
  </nav>

  <main>
    {#if $dataLoading}
      <div class="center-msg">Loading NSE data…</div>
    {:else if $dataError}
      <div class="center-msg error">Failed to load data: {$dataError}</div>
    {:else}
      {#if $activeTab === 'top-picks'}
        <TopPicks {sectors} />
      {:else if $activeTab === 'watchlist'}
        <Watchlist {sectors} />
      {:else if $activeTab === 'sector-view'}
        <SectorView />
      {:else if $activeTab === 'compare'}
        <Compare />
      {:else if $activeTab === 'market-pulse'}
        <MarketPulse />
      {/if}
    {/if}
  </main>
</div>

<style>
  .app { display: flex; flex-direction: column; min-height: 100vh; }
  header {
    display: flex; justify-content: space-between; align-items: center;
    padding: 12px 20px; background: var(--bg-secondary);
    border-bottom: 1px solid var(--border);
    position: sticky; top: 0; z-index: 10;
  }
  h1 { font-size: 18px; font-weight: 700; }
  .last-updated { font-size: 11px; color: var(--text-muted); margin-left: 12px; }
  .header-right { font-size: 12px; }
  .loading-dot { color: var(--accent-yellow); }
  .error-dot   { color: var(--accent-red); }
  .ok-dot      { color: var(--accent-green); }
  nav {
    display: flex; gap: 4px; padding: 8px 16px;
    background: var(--bg-secondary); border-bottom: 1px solid var(--border);
    overflow-x: auto;
  }
  nav button { white-space: nowrap; }
  main { flex: 1; overflow: hidden; }
  .center-msg { display: flex; align-items: center; justify-content: center; height: 300px; color: var(--text-secondary); }
  .center-msg.error { color: var(--accent-red); }
</style>
