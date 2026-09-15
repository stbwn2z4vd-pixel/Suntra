"""
Hämtar de senaste nyhetsrubrikerna för en ticker via yfinance.

yfinance har bytt struktur på nyhets-JSON:en några gånger mellan
versioner, så koden här är medvetet defensiv och plockar ut fälten
den hittar istället för att anta en exakt struktur.
"""

import logging
from datetime import datetime, timezone

import yfinance as yf

import config as cfg

logger = logging.getLogger(__name__)


def _extract_field(item: dict, *candidates):
    """Leta efter första matchande nyckeln, även nästlat under 'content'."""
    sources = [item, item.get("content", {}) if isinstance(item.get("content"), dict) else {}]
    for source in sources:
        for key in candidates:
            if key in source and source[key]:
                return source[key]
    return None


def get_recent_headlines(ticker: str, max_items: int = None) -> list[dict]:
    """
    Returnerar en lista med dicts: {"title":..., "publisher":..., "link":...}
    Vid fel returneras en tom lista (nyheter är "nice to have", inte kritiskt).
    """
    max_items = max_items or cfg.NEWS_MAX_ITEMS
    try:
        raw_news = yf.Ticker(ticker).news or []
    except Exception as exc:  # noqa: BLE001
        logger.warning("Kunde inte hämta nyheter för %s: %s", ticker, exc)
        return []

    headlines = []
    for item in raw_news[: max_items * 2]:  # hämta lite extra, filtrera sen
        title = _extract_field(item, "title")
        publisher = _extract_field(item, "publisher", "provider")
        link = _extract_field(item, "link", "canonicalUrl", "clickThroughUrl")

        if isinstance(publisher, dict):
            publisher = publisher.get("displayName")
        if isinstance(link, dict):
            link = link.get("url")

        if not title:
            continue

        headlines.append({
            "title": title,
            "publisher": publisher or "okänd källa",
            "link": link,
        })

        if len(headlines) >= max_items:
            break

    return headlines


def format_headlines_for_message(headlines: list[dict]) -> str:
    if not headlines:
        return ""
    lines = ["Senaste nyheter:"]
    for h in headlines:
        line = f"• {h['title']} ({h['publisher']})"
        lines.append(line)
    return "\n".join(lines)


def get_market_headlines(max_items: int = None) -> list[dict]:
    """
    Hämtar färska rubriker kopplade till breda marknadsindex
    (t.ex. S&P 500, OMX Stockholm 30) istället för en enskild aktie -
    används för att fånga upp geopolitiska/makrohändelser som kan
    påverka hela marknaden, inte bara ett enskilt bolag.
    """
    max_items = max_items or cfg.GEOPOLITICAL_NEWS_MAX_ITEMS
    combined: list[dict] = []
    seen_titles = set()

    for index_ticker in cfg.MARKET_INDEX_TICKERS:
        for headline in get_recent_headlines(index_ticker, max_items=max_items):
            if headline["title"] not in seen_titles:
                seen_titles.add(headline["title"])
                combined.append(headline)

    return combined[: max_items * len(cfg.MARKET_INDEX_TICKERS)]
