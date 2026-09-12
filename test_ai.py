"""
Engångstest: kör en påhittad (fejkad) aktiesignal genom AI-analysen
och skickar resultatet som en notis, för att verifiera att
GEMINI_API_KEY (eller ANTHROPIC_API_KEY) fungerar end-to-end.

Ingen riktig aktiedata hämtas - det här testar bara AI-kopplingen.
Kan tas bort när du väl sett att det funkar.
"""

from llm_explain import get_ai_analysis
from notify import send_notification

# Påhittad data som om en aktie precis fått en stark köpsignal
fake_data = {
    "price": 123.45,
    "rsi": 27.4,
    "macd_cross": "bullish",
    "sma50": 120.0,
    "sma200": 110.0,
    "position_52w": 12.0,
    "analyst_signal": "BUY",
    "total_score": 7,
    "label": "STRONG BUY",
}
fake_bullets = [
    "RSI är 27.4 (översåld) → köpsignal (+2)",
    "MACD korsade nyligen upp genom signallinjen → köpsignal (+2)",
    "Kursen ligger över både 50- och 200-dagars glidande medelvärde → uppåtgående trend (+1)",
    "Analytikerkonsensus: Buy (+2)",
    "Totalpoäng: +7 → Rekommendation: STRONG BUY",
]
fake_news = "Senaste nyheter:\n• Exempel-bolaget rapporterar rekordvinst (Exempel Nyheter)"

analysis = get_ai_analysis("TESTAKTIE", fake_data, fake_bullets, fake_news)

if analysis is None:
    title = "AI-test: fick inget svar"
    message = (
        "Ingen AI-nyckel hittades eller anropet misslyckades.\n\n"
        "Kolla att GEMINI_API_KEY (eller ANTHROPIC_API_KEY) verkligen "
        "är tillagd som secret i repot, med exakt det namnet."
    )
else:
    verdict = analysis.get("verdict") or "(inget tydligt format i svaret)"
    confidence = analysis.get("confidence")
    conf_text = f" (konfidens {confidence}/5)" if confidence else ""
    explanation = analysis.get("explanation") or "(ingen text)"
    title = "AI-test: lyckades!"
    message = f"AI-omdöme: {verdict}{conf_text}\n\n{explanation}"

send_notification(title=title, message=message, priority=3, tags=["robot"])
