"""
Valfri funktion: låt en AI dels förklara den tekniska rekommendationen
i text, dels ge en egen, oberoende bedömning (håller med/skeptisk +
konfidens) baserat på samma data plus färska nyheter.

Viktigt: AI-bedömningen ERSÄTTER ALDRIG den tekniska poängmodellen
(scoring.py) - den visas som ett separat, extra perspektiv bredvid.
Anledningen är att siffrorna (RSI, MACD osv.) alltid ska vara
konsekventa och spårbara, medan en AI kan hitta på saker (hallucinera)
eller resonera olika från gång till gång. AI:n är bäst på att fånga
sånt siffrorna missar - t.ex. en nyhet om en stämning eller ett
vinstvarnings-rykte - och att vara uttalat oense om det är motiverat.

Stöder två alternativ, i prioritetsordning:
  1. Anthropic (Claude) - kräver ANTHROPIC_API_KEY, kostar en liten
     summa per anrop.
  2. Google Gemini - kräver GEMINI_API_KEY, HELT GRATIS via Google AI
     Studio (inget kreditkort krävs).

Om ingen nyckel finns, eller om anropet/parsningen misslyckas,
faller systemet automatiskt tillbaka på enbart den mall-baserade
förklaringen från scoring.py - ingen notis går förlorad för att
det här steget failar.
"""

import logging
import os
import re

import requests

import config as cfg

logger = logging.getLogger(__name__)

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_URL_TEMPLATE = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


def _build_prompt(ticker: str, data: dict, bullets: list[str], news_text: str) -> str:
    bullet_text = "\n".join(f"- {b}" for b in bullets)
    news_section = news_text if news_text else "Inga färska nyheter hittades."

    return f"""Du får strukturerad data om aktien {ticker} från ett automatiserat
teknisk analys-system som precis ändrat sin rekommendation.

Data:
- Pris: {data.get('price')}
- RSI: {data.get('rsi')}
- MACD-korsning: {data.get('macd_cross')}
- Trend (SMA50/SMA200): pris={data.get('price')}, sma50={data.get('sma50')}, sma200={data.get('sma200')}
- Position i 52-veckorsintervall: {data.get('position_52w')}%
- Analytikerkonsensus: {data.get('analyst_signal')}
- Sammanlagd teknisk poäng: {data.get('total_score')}
- Systemets nya rekommendation: {data.get('label')}

Punkter det tekniska systemet redan räknat fram:
{bullet_text}

{news_section}

Du har två uppgifter:

1. Gör en EGEN, OBEROENDE bedömning av om den tekniska rekommendationen
   verkar rimlig just nu - väg in nyheterna ovan (t.ex. kommande
   rapport, vinstvarning, rättstvist, makronyheter) som det tekniska
   systemet inte kan se. Du får gärna vara oense med systemet om
   nyheterna talar för det - var inte bara ett eko.
2. Skriv en kort, konkret förklaring (max 4-5 meningar) av argumenten
   FÖR och EVENTUELLA MOTARGUMENT/RISKER. Undvik klyschor och undvik
   att bara rada upp punkterna ordagrant igen - väv ihop dem till
   läsbar text. Avsluta INTE med någon investeringsrådgivning-brasklapp.

Svara i EXAKT detta format, inget annat, ingen inledning:

BEDÖMNING: <ett av: HÅLLER MED / DELVIS / SKEPTISK>
KONFIDENS: <en siffra 1-5, där 5 = mycket säker>
FÖRKLARING: <din text här>
"""


def _call_anthropic(prompt: str) -> str | None:
    if not ANTHROPIC_API_KEY:
        return None
    response = requests.post(
        ANTHROPIC_URL,
        headers={
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": cfg.ANTHROPIC_MODEL,
            "max_tokens": 500,
            "messages": [{"role": "user", "content": prompt}],
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
    return "\n".join(p for p in text_parts if p).strip() or None


def _call_gemini(prompt: str) -> str | None:
    if not GEMINI_API_KEY:
        return None

    last_error = None
    for model in cfg.GEMINI_MODEL_CANDIDATES:
        url = GEMINI_URL_TEMPLATE.format(model=model)
        try:
            response = requests.post(
                url,
                params={"key": GEMINI_API_KEY},
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=30,
            )
            if response.status_code == 404:
                # Modellnamnet finns inte (längre) för det här kontot/API-versionen -
                # prova nästa kandidat istället för att ge upp direkt.
                logger.info("Gemini-modellen '%s' gav 404, provar nästa kandidat.", model)
                last_error = f"404 för modell {model}"
                continue

            response.raise_for_status()
            payload = response.json()
            candidates = payload.get("candidates", [])
            if not candidates:
                continue
            parts = candidates[0].get("content", {}).get("parts", [])
            text = "".join(p.get("text", "") for p in parts).strip()
            if text:
                return text
        except Exception as exc:  # noqa: BLE001
            last_error = str(exc)
            # Andra fel än 404 (nätverk, 429, 403 osv.) - inte meningsfullt
            # att prova fler modellnamn, ge upp Gemini för den här gången.
            raise

    if last_error:
        logger.warning("Alla Gemini-modellkandidater misslyckades: %s", last_error)
    return None


def _parse_response(raw_text: str) -> dict | None:
    """Plockar ut BEDÖMNING / KONFIDENS / FÖRKLARING ur AI-svaret."""
    verdict_match = re.search(r"BED[ÖO]MNING:\s*(.+)", raw_text, re.IGNORECASE)
    confidence_match = re.search(r"KONFIDENS:\s*(\d)", raw_text, re.IGNORECASE)
    explanation_match = re.search(r"F[ÖO]RKLARING:\s*(.+)", raw_text, re.IGNORECASE | re.DOTALL)

    if not explanation_match:
        # Kunde inte tolka formatet - använd hela svaret som förklaring,
        # utan separat bedömning, hellre än att kasta bort det.
        return {"verdict": None, "confidence": None, "explanation": raw_text.strip()}

    return {
        "verdict": verdict_match.group(1).strip() if verdict_match else None,
        "confidence": int(confidence_match.group(1)) if confidence_match else None,
        "explanation": explanation_match.group(1).strip(),
    }


def get_ai_analysis(ticker: str, data: dict, bullets: list[str], news_text: str) -> dict | None:
    """
    Returnerar {"verdict":..., "confidence":..., "explanation":...} eller
    None om AI-funktionen är avstängd, ingen nyckel finns, eller allt misslyckas.
    """
    if not cfg.USE_LLM_EXPLANATION:
        return None

    prompt = _build_prompt(ticker, data, bullets, news_text)

    for name, call_fn in (("Anthropic", _call_anthropic), ("Gemini", _call_gemini)):
        try:
            raw_text = call_fn(prompt)
            if raw_text:
                return _parse_response(raw_text)
        except Exception as exc:  # noqa: BLE001
            logger.warning("%s-anrop misslyckades för %s, provar nästa alternativ: %s", name, ticker, exc)

    logger.info("Ingen AI-nyckel satt eller alla anrop misslyckades - använder bara mallen för %s.", ticker)
    return None
