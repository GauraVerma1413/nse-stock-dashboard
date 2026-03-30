export function icsKey(risk, horizon) {
  return `${risk}_${horizon}y`
}

export function getICS(stock, risk, horizon) {
  const key = icsKey(risk, horizon)
  return stock.ics?.[key] ?? stock.ics?.['moderate_3y'] ?? 0
}

export function icsLabel(ics) {
  if (ics >= 8) return { cls: 'badge-strong-buy', label: 'STRONG BUY' }
  if (ics >= 6) return { cls: 'badge-consider',   label: 'CONSIDER' }
  if (ics >= 4) return { cls: 'badge-neutral',     label: 'NEUTRAL' }
  if (ics >= 2) return { cls: 'badge-caution',     label: 'CAUTION' }
  return               { cls: 'badge-avoid',       label: 'AVOID' }
}

export function icsColor(ics) {
  if (ics >= 8) return 'var(--ics-strong-buy)'
  if (ics >= 6) return 'var(--ics-consider)'
  if (ics >= 4) return 'var(--ics-neutral)'
  if (ics >= 2) return 'var(--ics-caution)'
  return 'var(--ics-avoid)'
}
