"""
Huvudskript. Körs schemalagt (se .github/workflows/monitor.yml) - numera
två gånger per vardag: en gång bara för svenska aktier (kring 12:00
svensk tid) och en gång bara för amerikanska (kring 18:00 svensk tid),
styrt av miljövariabeln MARKET_FILTER ("SE", "US" eller "ALL").

Flöde per ticker:
 1. Hämta pris + räkna ut RSI, MACD, trend, 52-veckorsläge, analytiker
 2. Väg ihop allt till en rekommendation (scoring.py) - detta är den
    "officiella" tekniska rekommendationen och styr ALLTID om en
    notis skickas.
 3. Jämför mot förra körningens rekommendation (state.json)
 4. Om den ändrats:
    - hämta färska nyhetsrubriker
    - försök få en oberoende AI-bedömning + textförklaring
      (llm_explain.py, valfritt - visas separat, ersätter aldrig
      den tekniska rekommendationen)
    - skicka EN pushnotis med siffror, ev. AI-bedömning och ev. nyheter
 5. Kollar dessutom breda marknadsnyheter (S&P 500 / OMX Stockholm 30)
    efter genuint marknadspåverkande geopolitiska/makrohändelser, och
    skickar en separat notis om AI:n bedömer något som relevant.
 6. Sparar allt till state.json (committas av workflowen) - bara de
    tickers som faktiskt kördes den här gången uppdateras, resten
    behåller sitt tidigare värde.
"""

import json
import logging
import os
import time

from config import (
    ALL_TICKERS,
    SWEDISH_TICKERS,
    US_TICKERS,
    STATE_FILE,
    FETCH_NEWS_ON_CHANGE,
    CHECK_GEOPOLITICAL_NEWS,
    GEOPOLITICAL_SEEN_CAP,
    AI_CALL_DELAY_SECONDS,
    display_name,
)
from analysis import analyze_ticker
from scoring import compute_composite_score
from news import get_recent_headlines, format_headlines_for_message, get_market_headlines
from llm_explain import get_ai_analysis, get_geopolitical_analysis
from notify import send_notification

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

TAGS_BY_LABEL = {
    "STRONG BUY": ["rocket"],
    "BUY": ["chart_with_upwards_trend"],
    "HOLD": ["neutral_face"],
    "SELL": ["chart_with_downwards_trend"],
    "STRONG SELL": ["warning"],
}
PRIORITY_BY_LABEL = {
    "STRONG BUY": 5,
    "BUY": 4,
    "HOLD": 2,
    "SELL": 4,
    "STRONG SELL": 5,
}

GEOPOLITICAL_SEEN_KEY = "_geopolitical_seen"


def load_state() -> dict:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_state(state: dict) -> None:
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def get_tickers_for_this_run() -> list[str]:
    market_filter = os.environ.get("MARKET_FILTER", "ALL").upper()
    if market_filter == "SE":
        logger.info("MARKET_FILTER=SE - kör bara svenska aktier.")
        return SWEDISH_TICKERS
    if market_filter == "US":
        logger.info("MARKET_FILTER=US - kör bara amerikanska aktier.")
        return US_TICKERS
    logger.info("MARKET_FILTER=ALL (eller ej satt) - kör alla aktier.")
    return ALL_TICKERS


def build_message(name: str, old_label: str | None, score_result, news_text: str, ai_analysis: dict | None) -> str:
    parts = [f"{name}", f"Teknisk rekommendation: {old_label or '(första körningen)'} -> {score_result.label}", ""]
    parts.extend(score_result.bullets)

    if ai_analysis:
        parts.append("")
        parts.append("— — —")
        verdict = ai_analysis.get("verdict")
        confidence = ai_analysis.get("confidence")
        if verdict:
            conf_text = f" (konfidens {confidence}/5)" if confidence else ""
            parts.append(f"AI-omdöme: {verdict}{conf_text}")
            parts.append("")
        explanation = ai_analysis.get("explanation")
        if explanation:
            parts.append(explanation)

    if news_text:
        parts.append("")
        parts.append(news_text)

    return "\n".join(parts)


def run_ticker_analysis(state: dict) -> int:
    """Analyserar den här körningens tickers och returnerar antal skickade notiser."""
    notified = 0

    for ticker in get_tickers_for_this_run():
        result = analyze_ticker(ticker)
        if result is None:
            continue

        score_result = compute_composite_score(
            rsi=result["rsi"],
            macd_cross=result["macd_cross"],
            macd_above_signal=result["macd_above_signal"],
            price=result["price"],
            sma50=result["sma50"],
            sma200=result["sma200"],
            position_52w=result["position_52w"],
            analyst_signal=result["analyst_signal"],
        )

        old_entry = state.get(ticker, {})
        old_label = old_entry.get("label")
        is_first_run = ticker not in state

        state[ticker] = {
            "label": score_result.label,
            "score": score_result.total_score,
        }

        logger.info(
            "%s: pris=%s rsi=%s macd_cross=%s label=%s (poäng %+d)",
            ticker, result["price"], result["rsi"], result["macd_cross"],
            score_result.label, score_result.total_score,
        )

        if is_first_run or old_label == score_result.label:
            continue

        news_text = ""
        if FETCH_NEWS_ON_CHANGE:
            headlines = get_recent_headlines(ticker)
            news_text = format_headlines_for_message(headlines)

        ai_data = {**result, "total_score": score_result.total_score, "label": score_result.label}
        name = display_name(ticker)
        ai_analysis = get_ai_analysis(name, ai_data, score_result.bullets, news_text)
        time.sleep(AI_CALL_DELAY_SECONDS)  # undvik att bränna igenom rate limit vid flera ändringar i rad

        message = build_message(name, old_label, score_result, news_text, ai_analysis)
        title = f"{name}: {score_result.label} ({result['price']})"

        send_notification(
            title=title,
            message=message,
            priority=PRIORITY_BY_LABEL.get(score_result.label, 3),
            tags=TAGS_BY_LABEL.get(score_result.label, ["bar_chart"]),
        )
        notified += 1

    return notified


def run_geopolitical_check(state: dict) -> None:
    """Kollar breda marknadsnyheter efter genuint marknadspåverkande händelser."""
    if not CHECK_GEOPOLITICAL_NEWS:
        return

    headlines = get_market_headlines()
    if not headlines:
        return

    seen_titles = set(state.get(GEOPOLITICAL_SEEN_KEY, []))
    new_headlines = [h for h in headlines if h["title"] not in seen_titles]

    if new_headlines:
        analysis = get_geopolitical_analysis(new_headlines)
        if analysis and analysis.get("relevant") and analysis.get("summary"):
            send_notification(
                title="⚠️ Möjlig marknadspåverkande händelse",
                message=analysis["summary"],
                priority=4,
                tags=["warning"],
            )
        elif analysis is None:
            logger.info("Ingen AI-nyckel eller anropet misslyckades - hoppar över geopolitisk bedömning.")

    # Uppdatera vad vi sett, oavsett om något bedömdes relevant eller ej,
    # så vi inte frågar AI:n om samma rubriker om och om igen.
    all_titles = seen_titles.union(h["title"] for h in headlines)
    state[GEOPOLITICAL_SEEN_KEY] = list(all_titles)[-GEOPOLITICAL_SEEN_CAP:]


def main() -> None:
    state = load_state()  # vi bygger vidare på detta - inte en tom dict

    notified = run_ticker_analysis(state)
    run_geopolitical_check(state)

    if notified == 0:
        logger.info("Inga signalförändringar denna körning.")

    save_state(state)


if __name__ == "__main__":
    main()
