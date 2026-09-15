"""
Konfiguration: vilka aktier som ska bevakas.

Svenska aktier använder Yahoo Finance-suffix:
  .ST  = Nasdaq Stockholm

Lägg till/ta bort tickers efter behov.
"""

SWEDISH_TICKERS = [
    "INVE-B.ST",    # Investor B
    "ATCO-A.ST",    # Atlas Copco A
    "ATCO-B.ST",    # Atlas Copco B
    "AZN.ST",       # AstraZeneca
    "VOLV-B.ST",    # Volvo B
    "ERIC-B.ST",    # Ericsson B
    "ASSA-B.ST",    # Assa Abloy B
    "HEXA-B.ST",    # Hexagon B
    "SAND.ST",      # Sandvik
    "EPI-A.ST",     # Epiroc A
    "EPI-B.ST",     # Epiroc B
    "SEB-A.ST",     # SEB A
    "SWED-A.ST",    # Swedbank A
    "NDA-SE.ST",    # Nordea
    "SHB-A.ST",     # Handelsbanken A
    "SKA-B.ST",     # Skanska B
    "SKF-B.ST",     # SKF B
    "ALFA.ST",      # Alfa Laval
    "TELIA.ST",     # Telia
    "ESSITY-B.ST",  # Essity B
    "HM-B.ST",      # H&M B
    "GETI-B.ST",    # Getinge B
    "BOL.ST",       # Boliden
    "EVO.ST",       # Evolution AB
    "NIBE-B.ST",    # Nibe Industrier B
    "KINV-B.ST",    # Kinnevik B
    "INDU-C.ST",    # Industrivärden C
    "LATO-B.ST",    # Latour B
    "EQT.ST",       # EQT AB
    "SAGA-B.ST",    # Sagax B
    "FABG.ST",      # Fabege
    "CAST.ST",      # Castellum
    "WALL-B.ST",    # Wallenstam B
    "SCA-B.ST",     # SCA B
    "HUSQ-B.ST",    # Husqvarna B
    "ELUX-B.ST",    # Electrolux B
    "ALIV-SDB.ST",  # Autoliv SDB
    "BEIJ-B.ST",    # Beijer Ref B
    "INDT.ST",      # Indutrade
    "LIFCO-B.ST",   # Lifco B
    "ADDT-B.ST",    # Addtech B
    "SWEC-B.ST",    # Sweco B
    "AXFO.ST",      # Axfood
    "LOOM-B.ST",    # Loomis B
    "TEL2-B.ST",    # Tele2 B
    "BILI-A.ST",    # Bilia A
    "EKTA-B.ST",    # Elekta B
    "TREL-B.ST",    # Trelleborg B
    "SSAB-B.ST",    # SSAB B
    "HOLM-B.ST",    # Holmen B
]

US_TICKERS = [
    "NVDA",   # Nvidia
    "AAPL",   # Apple
    "GOOGL",  # Alphabet
    "MSFT",   # Microsoft
    "AMZN",   # Amazon
    "META",   # Meta
    "AVGO",   # Broadcom
    "BRK-B",  # Berkshire Hathaway
    "TSLA",   # Tesla
    "LLY",    # Eli Lilly
    "JPM",    # JPMorgan Chase
    "V",      # Visa
    "WMT",    # Walmart
    "MA",     # Mastercard
    "UNH",    # UnitedHealth
    "XOM",    # ExxonMobil
    "ORCL",   # Oracle
    "COST",   # Costco
    "NFLX",   # Netflix
    "HD",     # Home Depot
    "PG",     # Procter & Gamble
    "JNJ",    # Johnson & Johnson
    "BAC",    # Bank of America
    "ABBV",   # AbbVie
    "KO",     # Coca-Cola
    "CVX",    # Chevron
    "CRM",    # Salesforce
    "AMD",    # Advanced Micro Devices
    "CSCO",   # Cisco
    "PEP",    # PepsiCo
    "MRK",    # Merck
    "MCD",    # McDonald's
    "ADBE",   # Adobe
    "WFC",    # Wells Fargo
    "DIS",    # Disney
    "NKE",    # Nike
    "IBM",    # IBM
    "QCOM",   # Qualcomm
    "INTC",   # Intel
    "TXN",    # Texas Instruments
    "VZ",     # Verizon
    "T",      # AT&T
    "CMCSA",  # Comcast
    "HON",    # Honeywell
    "BA",     # Boeing
    "CAT",    # Caterpillar
    "GS",     # Goldman Sachs
    "MS",     # Morgan Stanley
    "AXP",    # American Express
    "UNP",    # Union Pacific
]

ALL_TICKERS = SWEDISH_TICKERS + US_TICKERS

TICKER_NAMES = {
    "INVE-B.ST": "Investor B",
    "ATCO-A.ST": "Atlas Copco A",
    "ATCO-B.ST": "Atlas Copco B",
    "AZN.ST": "AstraZeneca",
    "VOLV-B.ST": "Volvo B",
    "ERIC-B.ST": "Ericsson B",
    "ASSA-B.ST": "Assa Abloy B",
    "HEXA-B.ST": "Hexagon B",
    "SAND.ST": "Sandvik",
    "EPI-A.ST": "Epiroc A",
    "EPI-B.ST": "Epiroc B",
    "SEB-A.ST": "SEB A",
    "SWED-A.ST": "Swedbank A",
    "NDA-SE.ST": "Nordea",
    "SHB-A.ST": "Handelsbanken A",
    "SKA-B.ST": "Skanska B",
    "SKF-B.ST": "SKF B",
    "ALFA.ST": "Alfa Laval",
    "TELIA.ST": "Telia",
    "ESSITY-B.ST": "Essity B",
    "HM-B.ST": "H&M B",
    "GETI-B.ST": "Getinge B",
    "BOL.ST": "Boliden",
    "EVO.ST": "Evolution AB",
    "NIBE-B.ST": "Nibe Industrier B",
    "KINV-B.ST": "Kinnevik B",
    "INDU-C.ST": "Industrivärden C",
    "LATO-B.ST": "Latour B",
    "EQT.ST": "EQT AB",
    "SAGA-B.ST": "Sagax B",
    "FABG.ST": "Fabege",
    "CAST.ST": "Castellum",
    "WALL-B.ST": "Wallenstam B",
    "SCA-B.ST": "SCA B",
    "HUSQ-B.ST": "Husqvarna B",
    "ELUX-B.ST": "Electrolux B",
    "ALIV-SDB.ST": "Autoliv SDB",
    "BEIJ-B.ST": "Beijer Ref B",
    "INDT.ST": "Indutrade",
    "LIFCO-B.ST": "Lifco B",
    "ADDT-B.ST": "Addtech B",
    "SWEC-B.ST": "Sweco B",
    "AXFO.ST": "Axfood",
    "LOOM-B.ST": "Loomis B",
    "TEL2-B.ST": "Tele2 B",
    "BILI-A.ST": "Bilia A",
    "EKTA-B.ST": "Elekta B",
    "TREL-B.ST": "Trelleborg B",
    "SSAB-B.ST": "SSAB B",
    "HOLM-B.ST": "Holmen B",
    "NVDA": "Nvidia",
    "AAPL": "Apple",
    "GOOGL": "Alphabet",
    "MSFT": "Microsoft",
    "AMZN": "Amazon",
    "META": "Meta",
    "AVGO": "Broadcom",
    "BRK-B": "Berkshire Hathaway",
    "TSLA": "Tesla",
    "LLY": "Eli Lilly",
    "JPM": "JPMorgan Chase",
    "V": "Visa",
    "WMT": "Walmart",
    "MA": "Mastercard",
    "UNH": "UnitedHealth",
    "XOM": "ExxonMobil",
    "ORCL": "Oracle",
    "COST": "Costco",
    "NFLX": "Netflix",
    "HD": "Home Depot",
    "PG": "Procter & Gamble",
    "JNJ": "Johnson & Johnson",
    "BAC": "Bank of America",
    "ABBV": "AbbVie",
    "KO": "Coca-Cola",
    "CVX": "Chevron",
    "CRM": "Salesforce",
    "AMD": "Advanced Micro Devices",
    "CSCO": "Cisco",
    "PEP": "PepsiCo",
    "MRK": "Merck",
    "MCD": "McDonald's",
    "ADBE": "Adobe",
    "WFC": "Wells Fargo",
    "DIS": "Disney",
    "NKE": "Nike",
    "IBM": "IBM",
    "QCOM": "Qualcomm",
    "INTC": "Intel",
    "TXN": "Texas Instruments",
    "VZ": "Verizon",
    "T": "AT&T",
    "CMCSA": "Comcast",
    "HON": "Honeywell",
    "BA": "Boeing",
    "CAT": "Caterpillar",
    "GS": "Goldman Sachs",
    "MS": "Morgan Stanley",
    "AXP": "American Express",
    "UNP": "Union Pacific",
}


def display_name(ticker: str) -> str:
    """T.ex. "Amazon (AMZN)" - faller tillbaka på bara tickern om namnet saknas."""
    name = TICKER_NAMES.get(ticker)
    return f"{name} ({ticker})" if name else ticker

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

# --- Geopolitiska/makronyheter som kan påverka hela marknaden ---
# Kräver samma AI-nyckel som AI-omdömet (GEMINI_API_KEY eller
# ANTHROPIC_API_KEY) - utan nyckel skippas den här delen helt,
# eftersom nyckelordsbaserad "geopolitik-detektering" är för opålitlig.
CHECK_GEOPOLITICAL_NEWS = True
MARKET_INDEX_TICKERS = ["^GSPC", "^OMX"]  # S&P 500 resp. OMX Stockholm 30
GEOPOLITICAL_NEWS_MAX_ITEMS = 8
GEOPOLITICAL_SEEN_CAP = 150  # max antal ihågkomna rubriker (undviker dubbletter)

# Liten paus (sekunder) mellan AI-anrop för olika aktier i samma körning.
# Gemini gratisnivå har en gräns för antal anrop PER MINUT - om många
# aktier ändrar signal samtidigt kan senare anrop annars nekas
# (rate limit) medan tidigare går igenom.
AI_CALL_DELAY_SECONDS = 4

STATE_FILE = "state.json"
