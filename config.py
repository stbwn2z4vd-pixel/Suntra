"""
Konfiguration: vilka aktier som ska bevakas.

Svenska aktier använder Yahoo Finance-suffix:
  .ST  = Nasdaq Stockholm

Lägg till/ta bort tickers efter behov.
"""

SWEDISH_TICKERS = [
    "ERIC-B.ST",   # Ericsson
    "VOLV-B.ST",   # Volvo
    "ATCO-A.ST",   # Atlas Copco A
    "ATCO-B.ST",   # Atlas Copco B
    "INVE-B.ST",   # Investor B
    "SAND.ST",     # Sandvik
    "SEB-A.ST",    # SEB
    "SWED-A.ST",   # Swedbank
    "HM-B.ST",     # H&M
    "ASSA-B.ST",   # Assa Abloy
    "ALFA.ST",     # Alfa Laval
    "SKF-B.ST",    # SKF
    "TELIA.ST",    # Telia
    "NDA-SE.ST",   # Nordea
    "ESSITY-B.ST", # Essity
]

US_TICKERS = [
    "AAPL",
    "MSFT",
    "GOOGL",
    "AMZN",
    "NVDA",
    "META",
    "TSLA",
    "BRK-B",
    "JPM",
    "V",
]

ALL_TICKERS = SWEDISH_TICKERS + US_TICKERS

# --- Tekniska analys-parametrar ---
RSI_PERIOD = 14
RSI_OVERSOLD = 30    # under detta = köpsignal (tekniskt "översåld")
RSI_OVERBOUGHT = 70  # över detta = säljsignal ("överköpt")

SMA_SHORT_PERIOD = 50
SMA_LONG_PERIOD = 200  # långsiktigt trendfilter

MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
MACD_CROSS_LOOKBACK = 3  # hur många dagar tillbaka vi letar efter en korsning

# Position i 52-veckorsintervall (0% = årslägsta, 100% = årshögsta)
POSITION_52W_LOOKBACK_DAYS = 252
POSITION_52W_LOW_THRESHOLD = 15   # under denna % = "nära årslägsta"
POSITION_52W_HIGH_THRESHOLD = 90  # över denna % = "nära årshögsta"

# Hur mycket historik som hämtas (behövs för SMA200 m.fl.)
HISTORY_PERIOD = "2y"

# --- Poängmodell: väger ihop alla signaler till en rekommendation ---
# Varje faktor bidrar med poäng (positivt = köp, negativt = sälj).
SCORE_RSI_OVERSOLD = 2        # RSI < RSI_OVERSOLD
SCORE_RSI_LOW = 1             # RSI < 45
SCORE_RSI_HIGH = -1           # RSI > 55
SCORE_RSI_OVERBOUGHT = -2     # RSI > RSI_OVERBOUGHT

SCORE_MACD_BULLISH_CROSS = 2  # MACD korsade nyligen upp
SCORE_MACD_ABOVE = 1          # MACD-linjen ligger över signallinjen (utan ny korsning)
SCORE_MACD_BELOW = -1
SCORE_MACD_BEARISH_CROSS = -2

SCORE_TREND_UP = 1            # pris > SMA50 > SMA200
SCORE_TREND_DOWN = -1         # pris < SMA50 < SMA200

SCORE_NEAR_52W_LOW = 1         # möjligt bra ingångsläge
# (nära årshögsta ger ingen poäng automatiskt - redovisas bara som info,
#  eftersom det kan vara antingen momentum eller "överköpt".)

SCORE_ANALYST_BUY = 2
SCORE_ANALYST_SELL = -2

# Gränser för den samlade rekommendationen (summan av alla poäng ovan)
LABEL_STRONG_BUY = 5
LABEL_BUY = 2
LABEL_SELL = -2
LABEL_STRONG_SELL = -5

# --- Nyheter ---
FETCH_NEWS_ON_CHANGE = True   # hämta nyhetsrubriker bara för aktier där signalen ändrats
NEWS_MAX_ITEMS = 3

# --- Valfri AI-genererad förklaringstext (Claude) ---
# Kräver en egen Anthropic API-nyckel i secreten ANTHROPIC_API_KEY.
# Om den saknas används den mall-baserade förklaringen istället.
USE_LLM_EXPLANATION = True
ANTHROPIC_MODEL = "claude-sonnet-5"
# Google byter/döper om Gemini-modeller ganska ofta. Vi provar dessa i
# ordning tills en fungerar, så att systemet inte går sönder bara för
# att ett enskilt modellnamn pensioneras.
GEMINI_MODEL_CANDIDATES = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-flash-latest",
    "gemini-2.0-flash",
]

STATE_FILE = "state.json"
