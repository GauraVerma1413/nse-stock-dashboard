<script>
  import { filters } from '../lib/stores.js'

  let { sectors = [] } = $props()

  const riskOptions = [
    { value: 'conservative', label: 'Conservative' },
    { value: 'moderate',     label: 'Moderate' },
    { value: 'aggressive',   label: 'Aggressive' }
  ]
  const marketCapOptions = [
    { value: 'all',   label: 'All Caps' },
    { value: 'large', label: 'Large Cap (>20K Cr)' },
    { value: 'mid',   label: 'Mid Cap (5K–20K Cr)' },
    { value: 'small', label: 'Small Cap (<5K Cr)' }
  ]
</script>

<div class="filter-bar">
  <div class="filter-group">
    <label>Risk Tolerance</label>
    <div class="btn-group">
      {#each riskOptions as opt}
        <button
          class:active={$filters.risk === opt.value}
          onclick={() => filters.update(f => ({ ...f, risk: opt.value }))}
        >{opt.label}</button>
      {/each}
    </div>
  </div>

  <div class="filter-group">
    <label>Time Horizon: <strong>{$filters.horizon} yr{$filters.horizon > 1 ? 's' : ''}</strong></label>
    <input
      type="range" min="1" max="10" step="1"
      value={$filters.horizon}
      oninput={(e) => filters.update(f => ({ ...f, horizon: Number(e.target.value) }))}
    />
    <div class="range-labels"><span>1yr</span><span>10yr</span></div>
  </div>

  <div class="filter-group">
    <label>Sector</label>
    <select
      value={$filters.sector}
      onchange={(e) => filters.update(f => ({ ...f, sector: e.target.value }))}
    >
      <option value="all">All Sectors</option>
      {#each sectors as s}
        <option value={s}>{s}</option>
      {/each}
    </select>
  </div>

  <div class="filter-group">
    <label>Market Cap</label>
    <select
      value={$filters.marketCap}
      onchange={(e) => filters.update(f => ({ ...f, marketCap: e.target.value }))}
    >
      {#each marketCapOptions as opt}
        <option value={opt.value}>{opt.label}</option>
      {/each}
    </select>
  </div>

  <button onclick={() => filters.reset()} style="align-self:flex-end">Reset</button>
</div>

<style>
  .filter-bar {
    display: flex; flex-wrap: wrap; gap: 20px;
    padding: 16px; background: var(--bg-secondary);
    border-bottom: 1px solid var(--border);
    align-items: flex-start;
  }
  .filter-group { display: flex; flex-direction: column; gap: 6px; }
  label { font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); }
  .btn-group { display: flex; gap: 4px; }
  .range-labels { display: flex; justify-content: space-between; font-size: 10px; color: var(--text-muted); }
  input[type="range"] { width: 140px; }
</style>
