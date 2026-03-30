import { getICS } from './ics.js'

export function applyFilters(stocks, filters) {
  const { risk, horizon, sector, marketCap } = filters
  return stocks
    .filter(s => {
      if (sector !== 'all' && s.sector !== sector) return false
      if (marketCap === 'large' && s.market_cap_cr < 20000) return false
      if (marketCap === 'mid'   && (s.market_cap_cr < 5000 || s.market_cap_cr >= 20000)) return false
      if (marketCap === 'small' && s.market_cap_cr >= 5000) return false
      return true
    })
    .map(s => ({ ...s, _ics: getICS(s, risk, horizon) }))
    .sort((a, b) => b._ics - a._ics)
}

export function getSectors(stocks) {
  return [...new Set(stocks.map(s => s.sector))].sort()
}

export function unusualVolume(stocks, multiplier = 2) {
  return stocks
    .filter(s => s.volume_today && s.volume_30d_avg && s.volume_today > multiplier * s.volume_30d_avg)
    .sort((a, b) => (b.volume_today / b.volume_30d_avg) - (a.volume_today / a.volume_30d_avg))
    .slice(0, 10)
}
