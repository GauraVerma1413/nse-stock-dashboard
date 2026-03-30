"""
score_stocks.py
Reads data/raw_stocks.json, computes ICS for all 30 risk×horizon combos,
writes data/scored_stocks.json.
"""

import json
from pathlib import Path
from collections import defaultdict

DATA_DIR = Path(__file__).parent.parent / "data"

RISK_WEIGHTS = {
    'conservative': {
        'pe': 0.10, 'revenue': 0.15, 'de': 0.25,
        'dividend': 0.20, 'moat': 0.15, 'risk': 0.10, 'volume': 0.05,
    },
    'moderate': {
        'pe': 0.15, 'revenue': 0.20, 'de': 0.15,
        'dividend': 0.10, 'moat': 0.20, 'risk': 0.10, 'volume': 0.10,
    },
    'aggressive': {
        'pe': 0.10, 'revenue': 0.30, 'de': 0.05,
        'dividend': 0.05, 'moat': 0.30, 'risk': 0.05, 'volume': 0.15,
    }
}

# Horizon multipliers: short (1-2y), medium (3-5y), long (6-10y)
def horizon_multipliers(horizon: int) -> dict:
    if horizon <= 2:
        return {'pe': 1.3, 'volume': 1.3, 'revenue': 0.8, 'moat': 0.8, 'dividend': 0.8}
    elif horizon <= 5:
        return {'pe': 1.0, 'volume': 1.0, 'revenue': 1.2, 'moat': 1.2, 'dividend': 1.0}
    else:
        return {'pe': 0.8, 'volume': 0.7, 'revenue': 1.1, 'moat': 1.4, 'dividend': 1.3}


def revenue_cagr(revenue_list: list) -> float:
    if not revenue_list or len(revenue_list) < 2:
        return None
    start, end = revenue_list[0], revenue_list[-1]
    if start <= 0 or end <= 0:
        return None
    n = len(revenue_list) - 1
    return ((end / start) ** (1 / n) - 1) * 100


def compute_sector_pe(stocks: list) -> dict:
    pe_by_sector = defaultdict(list)
    for s in stocks:
        pe = s.get('pe')
        if pe and 0 < pe < 200:
            pe_by_sector[s['sector']].append(pe)
    return {
        sec: sum(vals) / len(vals)
        for sec, vals in pe_by_sector.items()
    }


def moat_rating(stock: dict) -> str:
    de = stock.get('de_ratio') or 1.0
    pe = stock.get('pe') or 20
    div = stock.get('div_yield') or 0
    if de < 0.3 and pe > 0:
        return 'strong'
    if de < 1.0:
        return 'moderate'
    return 'weak'


def risk_rating(stock: dict) -> int:
    score = 5
    beta = stock.get('beta') or 1.0
    de = stock.get('de_ratio') or 0.5
    if beta > 1.5:   score += 2
    elif beta > 1.0: score += 1
    elif beta < 0.7: score -= 1
    if de > 2.0:   score += 2
    elif de > 1.0: score += 1
    elif de < 0.3: score -= 1
    return max(1, min(10, score))


def score_metric(value, low_is_good=False, min_val=0, max_val=100) -> float:
    if value is None:
        return 0.0
    norm = (value - min_val) / (max_val - min_val) if max_val != min_val else 0
    norm = max(0.0, min(1.0, norm))
    return (1 - norm if low_is_good else norm) * 10


def compute_ics(metric_scores: dict, risk: str, horizon: int) -> float:
    weights = dict(RISK_WEIGHTS[risk])
    mults = horizon_multipliers(horizon)
    for metric, mult in mults.items():
        if metric in weights:
            weights[metric] *= mult
    total = sum(weights.values())
    weights = {k: v / total for k, v in weights.items()}
    composite = sum(metric_scores.get(m, 0) * w for m, w in weights.items())
    return round(min(10.0, composite), 1)


def warning_text(stock: dict, risk_r: int) -> str:
    warnings = []
    if risk_r >= 7:
        warnings.append("High risk stock")
    if (stock.get('de_ratio') or 0) > 2:
        warnings.append("High debt levels")
    if (stock.get('beta') or 1) > 1.5:
        warnings.append("High market sensitivity")
    return "; ".join(warnings) if warnings else None


def main():
    raw = json.loads((DATA_DIR / "raw_stocks.json").read_text())
    sector_pe = compute_sector_pe(raw)
    scored = []

    for s in raw:
        cagr = revenue_cagr(s.get('revenue_5y') or [])
        s['revenue_cagr_5y'] = round(cagr, 2) if cagr is not None else None
        s['sector_pe_avg'] = round(sector_pe.get(s['sector'], 20.0), 1)
        s['moat'] = moat_rating(s)
        risk_r = risk_rating(s)
        s['risk_rating'] = risk_r

        pe_ratio = s.get('pe') or 20
        sector_pe_avg = s.get('sector_pe_avg') or 20
        pe_discount = max(0, (sector_pe_avg - pe_ratio) / sector_pe_avg * 100)

        metric_scores = {
            'pe':       score_metric(pe_discount, min_val=0, max_val=50),
            'revenue':  score_metric(s.get('revenue_cagr_5y'), min_val=-5, max_val=40),
            'de':       score_metric(s.get('de_ratio'), low_is_good=True, min_val=0, max_val=5),
            'dividend': score_metric(s.get('div_yield'), min_val=0, max_val=6),
            'moat':     {'strong': 10, 'moderate': 5, 'weak': 2}[s['moat']],
            'risk':     score_metric(risk_r, low_is_good=True, min_val=1, max_val=10),
            'volume':   score_metric(s.get('volume_30d_avg'), min_val=0, max_val=5e7),
        }

        ics_map = {}
        for risk in ('conservative', 'moderate', 'aggressive'):
            for horizon in range(1, 11):
                key = f"{risk}_{horizon}y"
                ics_map[key] = compute_ics(metric_scores, risk, horizon)

        ics_breakdown = {
            f"{k}_score": round(metric_scores[k] * RISK_WEIGHTS['moderate'][k], 2)
            for k in metric_scores
        }

        cmp = s.get('cmp') or 0
        scored.append({
            **s,
            "bull_target":   round(cmp * 1.20) if cmp else None,
            "bear_target":   round(cmp * 0.85) if cmp else None,
            "entry_zone":    [round(cmp * 0.95), round(cmp * 0.97)] if cmp else None,
            "stop_loss":     round(cmp * 0.85 * 0.95) if cmp else None,
            "ics":           ics_map,
            "ics_breakdown": ics_breakdown,
            "warning":       warning_text(s, risk_r),
        })

    out_path = DATA_DIR / "scored_stocks.json"
    out_path.write_text(json.dumps(scored, indent=2))
    print(f"Scored {len(scored)} stocks → {out_path}")


if __name__ == '__main__':
    main()
