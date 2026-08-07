import csv
import re
from functools import lru_cache
from pathlib import Path

DATA_PATH = Path(__file__).parent / "data" / "ticker_allowlist.csv"

# Common English words and finance-forum acronyms that collide with real ticker
# symbols (e.g. "ARE" = Alexandria Real Estate, "IT" = Gartner, "ON" = ON Semiconductor).
# Bare (non-$-prefixed) mentions of these are dropped since context alone can't
# disambiguate; a "$TICKER" mention always bypasses this blocklist.
STOPWORDS = {
    "A", "I", "ALL", "ARE", "AT", "BE", "BY", "CEO", "CFO", "DD", "FOR", "GO",
    "IF", "IN", "IS", "IT", "ME", "MY", "NEW", "NO", "NOW", "OF", "OK",
    "ON", "ONE", "OR", "SO", "TO", "TWO", "UP", "US", "WE", "YOLO",
    "FOMO", "ATH", "ATL", "IPO", "ETF", "EPS", "IMO", "TLDR", "USA",
    "OP", "PSA", "FAQ", "ELI5", "LOL", "WSB", "HODL", "FYI", "ASAP",
}

DOLLAR_TICKER_RE = re.compile(r"\$([A-Za-z]{1,5})\b")
BARE_TICKER_RE = re.compile(r"\b[A-Z]{2,5}\b")


@lru_cache
def _load_allowlist() -> dict[str, str]:
    with DATA_PATH.open(newline="") as f:
        reader = csv.DictReader(f)
        return {row["symbol"]: row["name"] for row in reader}


def is_known_ticker(symbol: str) -> bool:
    return symbol.upper() in _load_allowlist()


def extract_tickers(text: str) -> set[str]:
    """Extract likely stock ticker mentions from free text.

    `$TICKER` mentions are trusted as long as they're in the exchange allowlist.
    Bare all-caps mentions (no `$`) additionally must not be a common word/acronym
    in STOPWORDS, since those produce the bulk of false positives in forum text.
    """
    allowlist = _load_allowlist()
    found: set[str] = set()

    for match in DOLLAR_TICKER_RE.finditer(text):
        symbol = match.group(1).upper()
        if symbol in allowlist:
            found.add(symbol)

    for match in BARE_TICKER_RE.finditer(text):
        symbol = match.group(0)
        if symbol in STOPWORDS:
            continue
        if symbol in allowlist:
            found.add(symbol)

    return found
