export async function fetchLivePrices(tickers) {
  const results = {}
  const batches = []
  for (let i = 0; i < tickers.length; i += 5) {
    batches.push(tickers.slice(i, i + 5))
  }
  for (const batch of batches) {
    await Promise.all(batch.map(async ticker => {
      try {
        const url = `https://query1.finance.yahoo.com/v8/finance/chart/${ticker}?interval=1d&range=1d`
        const res = await fetch(url)
        if (!res.ok) return
        const json = await res.json()
        const meta = json?.chart?.result?.[0]?.meta
        if (!meta) return
        const price = meta.regularMarketPrice
        const prev  = meta.chartPreviousClose || meta.previousClose
        const change = price - prev
        const changePct = prev ? (change / prev) * 100 : 0
        results[ticker] = { price, change, changePct }
      } catch { /* skip */ }
    }))
    await new Promise(r => setTimeout(r, 200))
  }
  return results
}

export async function loadScreenedData() {
  const base = import.meta.env.BASE_URL
  const res = await fetch(`${base}data/nse_screened.json`)
  if (!res.ok) throw new Error(`Failed to load data: ${res.status}`)
  return res.json()
}
