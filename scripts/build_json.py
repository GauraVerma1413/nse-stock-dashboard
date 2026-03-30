"""
build_json.py
Reads scored_stocks.json, sorts by moderate_3y ICS,
writes minified data/nse_screened.json consumed by the frontend.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


def main():
    scored = json.loads((DATA_DIR / "scored_stocks.json").read_text())
    scored.sort(key=lambda s: s.get('ics', {}).get('moderate_3y', 0), reverse=True)

    output = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "stocks": scored
    }

    out_path = DATA_DIR / "nse_screened.json"
    out_path.write_text(json.dumps(output, separators=(',', ':')))
    size_kb = out_path.stat().st_size / 1024
    print(f"Built {out_path} — {len(scored)} stocks, {size_kb:.1f} KB")


if __name__ == '__main__':
    main()
