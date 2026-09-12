"""
Valfri funktion: låt Claude skriva en sammanhängande, naturligt
formulerad förklaring av rekommendationen, baserat på samma
strukturerade data som den mall-baserade förklaringen använder
(scoring.py) plus eventuella nyhetsrubriker.

Kräver en egen Anthropic API-nyckel i miljövariabeln ANTHROPIC_API_KEY
(läggs in som en GitHub Actions-secret). Om nyckeln saknas, eller om
anropet misslyckas av något skäl, faller systemet automatiskt
tillbaka på den mall-baserade förklaringen från scoring.py – ingen
notis går förlorad för att det här steget failar.

OBS: Detta gör ett riktigt API-anrop till Anthropic och kostar därför
en (mycket liten) summa per körning - inte att förväxla med den
gratis inbyggda Claude-funktionen i claude.ai.
"""

import logging
import os

import requests

import config as cfg

logger = logging.getLogger(__name__)

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"


def _build_prompt(ticker: str, data: dict, bullets: list[str], news_text: str) -> str:
    bullet_text = "\n".join(f"- {b}" for b in bullets)
    news_section = f"\n\nSenaste nyheter:\n{news_text}" if news_text else "\n\nInga färska nyheter hittades."

    return f"""Du får strukturerad data om aktien {ticker} från ett automatiserat
teknisk analys-system. Skriv en kort, konkret sammanfattning (max 4-5
meningar, på svenska) som förklarar VARFÖR rekommendationen ändrats
och vad som är argumenten för respektive eventuella motargument/risker.
Var balanserad - nämn även vad som talar emot om något gör det.
Undvik klyschor, undvik att bara rada upp punkterna igen ordagrant -
väv ihop dem till en läsbar text. Avsluta INTE med någon
investeringsrådgivning-brasklapp, det hanteras separat.

Data:
- Pris: {data.get('price')}
- RSI: {data.get('rsi')}
- MACD-korsning: {data.get('macd_cross')}
- Trend (SMA50/SMA200): pris={data.get('price')}, sma50={data.get('sma50')}, sma200={data.get('sma200')}
- Position i 52-veckorsintervall: {data.get('position_52w')}%
- Analytikerkonsensus: {data.get('analyst_signal')}
- Sammanlagd poäng: {data.get('total_score')}
- Ny rekommendation: {data.get('label')}

Punkter det tekniska systemet redan räknat fram:
{bullet_text}{news_section}
"""


def get_llm_summary(ticker: str, data: dict, bullets: list[str], news_text: str) -> str | None:
    """Returnerar en AI-skriven sammanfattning, eller None om det inte går/är avstängt."""
    if not cfg.USE_LLM_EXPLANATION:
        return None
    if not ANTHROPIC_API_KEY:
        logger.info("ANTHROPIC_API_KEY saknas - hoppar över AI-sammanfattning för %s.", ticker)
        return None

    try:
        response = requests.post(
            ANTHROPIC_URL,
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": cfg.ANTHROPIC_MODEL,
                "max_tokens": 400,
                "messages": [
                    {"role": "user", "content": _build_prompt(ticker, data, bullets, news_text)}
                ],
            },
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()

        text_parts = [
            block.get("text", "")
            for block in payload.get("content", [])
            if block.get("type") == "text"
        ]
        summary = "\n".join(p for p in text_parts if p).strip()
        return summary or None

    except Exception as exc:  # noqa: BLE001
        logger.warning("AI-sammanfattning misslyckades för %s, faller tillbaka på mallen: %s", ticker, exc)
        return None
