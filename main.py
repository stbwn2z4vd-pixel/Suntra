"""
Huvudskript. Körs schemalagt (se .github/workflows/monitor.yml).

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
 5. Spara nya rekommendationer till state.json (committas av workflowen)
"""

import json
import logging
import os

from config import ALL_TICKERS, STATE_FILE, FETCH_NEWS_ON_CHANGE
from analysis import analyze_ticker
from scoring import compute_composite_score
from news import get_recent_headlines, format_headlines_for_message
from llm_explain import get_ai_analysis
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


def load_state() -> dict:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_state(state: dict) -> None:
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def build_message(old_label: str | None, score_result, news_text: str, ai_analysis: dict | None) -> str:
    parts = [f"Teknisk rekommendation: {old_label or '(första körningen)'} -> {score_result.label}", ""]
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


def main() -> None:
    old_state = load_state()
    new_state = {}
    notified = 0

    for ticker in ALL_TICKERS:
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

        old_entry = old_state.get(ticker, {})
        old_label = old_entry.get("label")
        is_first_run = ticker not in old_state

        new_state[ticker] = {
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

        # Signalen har ändrats -> bygg och skicka notis
        news_text = ""
        if FETCH_NEWS_ON_CHANGE:
            headlines = get_recent_headlines(ticker)
            news_text = format_headlines_for_message(headlines)

        ai_data = {**result, "total_score": score_result.total_score, "label": score_result.label}
        ai_analysis = get_ai_analysis(ticker, ai_data, score_result.bullets, news_text)

        message = build_message(old_label, score_result, news_text, ai_analysis)
        title = f"{ticker}: {score_result.label} ({result['price']})"

        send_notification(
            title=title,
            message=message,
            priority=PRIORITY_BY_LABEL.get(score_result.label, 3),
            tags=TAGS_BY_LABEL.get(score_result.label, ["bar_chart"]),
        )
        notified += 1

    if notified == 0:
        logger.info("Inga signalförändringar denna körning.")

    save_state(new_state)


if __name__ == "__main__":
    main()
