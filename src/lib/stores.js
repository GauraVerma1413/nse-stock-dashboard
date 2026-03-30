import { writable } from 'svelte/store'

export const stockData = writable([])
export const lastUpdated = writable(null)
export const dataLoading = writable(true)
export const dataError = writable(null)

const DEFAULT_FILTERS = {
  risk: 'moderate',
  horizon: 3,
  sector: 'all',
  marketCap: 'all'
}

function loadFilters() {
  try {
    const saved = localStorage.getItem('nse_filters')
    return saved ? { ...DEFAULT_FILTERS, ...JSON.parse(saved) } : DEFAULT_FILTERS
  } catch { return DEFAULT_FILTERS }
}

function createFiltersStore() {
  const { subscribe, set, update } = writable(loadFilters())
  return {
    subscribe,
    set(value) {
      localStorage.setItem('nse_filters', JSON.stringify(value))
      set(value)
    },
    update(fn) {
      update(current => {
        const next = fn(current)
        localStorage.setItem('nse_filters', JSON.stringify(next))
        return next
      })
    },
    reset() { this.set(DEFAULT_FILTERS) }
  }
}

export const filters = createFiltersStore()

function createWatchlistStore() {
  const initial = (() => {
    try { return JSON.parse(localStorage.getItem('nse_watchlist') || '[]') }
    catch { return [] }
  })()
  const { subscribe, update } = writable(initial)
  return {
    subscribe,
    add(ticker) {
      update(list => {
        if (list.includes(ticker)) return list
        const next = [...list, ticker]
        localStorage.setItem('nse_watchlist', JSON.stringify(next))
        return next
      })
    },
    remove(ticker) {
      update(list => {
        const next = list.filter(t => t !== ticker)
        localStorage.setItem('nse_watchlist', JSON.stringify(next))
        return next
      })
    },
    has(ticker, list) { return list.includes(ticker) }
  }
}

export const watchlist = createWatchlistStore()
export const activeTab = writable('top-picks')
export const livePrices = writable({})
export const compareSelection = writable([])
