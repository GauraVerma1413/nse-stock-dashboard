<script>
  import { icsColor, icsLabel } from '../lib/ics.js'

  let { value = 0 } = $props()

  let color = $derived(icsColor(value))
  let icsBadge = $derived(icsLabel(value))
  let dots = $derived(Array.from({ length: 10 }, (_, i) => i < value))
</script>

<div class="gauge">
  <div class="dots">
    {#each dots as filled}
      <span class="dot" style={filled ? `background:${color}` : ''}></span>
    {/each}
  </div>
  <span class="score" style={`color:${color}`}>{value}/10</span>
  <span class="badge {icsBadge.cls}">{icsBadge.label}</span>
</div>

<style>
  .gauge { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
  .dots { display: flex; gap: 3px; }
  .dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: var(--bg-hover);
    transition: background 0.2s;
  }
  .score { font-family: var(--font-mono); font-size: 13px; font-weight: 700; min-width: 32px; }
</style>
