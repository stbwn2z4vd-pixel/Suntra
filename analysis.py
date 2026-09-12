"""
Hämtar data för en ticker och räknar ut alla underliggande signaler
(RSI, MACD, trend, 52-veckorsläge, analytikerkonsensus), och väger
ihop dem till en samlad rekommendation via scoring.py.
"""

import logging
import yfinance as yf

from config import (
    RSI_PERIOD,
    MACD_FAST,
    MACD_SLOW,
    MACD_SIGNAL,
    MACD_CROSS_LOOKBACK,
    SMA_SHORT_PERIOD,
    SMA_LONG_PERIOD,
    POSITION_52W_LOOKBACK_DAYS,
    HISTORY_PERIOD,
)
from indicators import rsi, sma, macd, detect_macd_cross, position_in_52w_range

logger = logging.getLogger(__name__)

ANALYST_MAP = {
    "strong_buy": "BUY",
    "buy": "BUY",
    "hold": "HOLD",
    "sell": "SELL",
    "strong_sell": "SELL",
    "none": "UNKNOWN",
}


def get_analyst_signal(ticker_obj: yf.Ticker) -> str:
    try:
        info = ticker_obj.info
        key = (info.get("recommendationKey") or "none").lower()
        return ANALYST_MAP.get(key, "UNKNOWN")
    except Exception as exc:  # noqa: BLE001
        logger.warning("Kunde inte hämta analytikerdata: %s", exc)
        return "UNKNOWN"


def analyze_ticker(ticker: str) -> dict | None:
    """Hämtar data och räknar ut alla signaler för en enskild ticker."""
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period=HISTORY_PERIOD, auto_adjust=True)

        min_len = max(RSI_PERIOD, MACD_SLOW, SMA_SHORT_PERIOD) + 5
        if hist.empty or len(hist) < min_len:
            logger.warning("För lite data för %s, hoppar över.", ticker)
            return None

        close = hist["Close"]
        high = hist["High"]
        low = hist["Low"]

        last_rsi = round(float(rsi(close, RSI_PERIOD).iloc[-1]), 1)

        macd_line, signal_line, _ = macd(close, MACD_FAST, MACD_SLOW, MACD_SIGNAL)
        macd_cross = detect_macd_cross(macd_line, signal_line, MACD_CROSS_LOOKBACK)
        macd_above_signal = bool(macd_line.iloc[-1] > signal_line.iloc[-1])

        sma50 = None
        sma200 = None
        if len(close) >= SMA_SHORT_PERIOD:
            sma50 = round(float(sma(close, SMA_SHORT_PERIOD).iloc[-1]), 2)
        if len(close) >= SMA_LONG_PERIOD:
            sma200 = round(float(sma(close, SMA_LONG_PERIOD).iloc[-1]), 2)

        position_52w = position_in_52w_range(high, low, close, POSITION_52W_LOOKBACK_DAYS)

        analyst_signal = get_analyst_signal(t)
        price = round(float(close.iloc[-1]), 2)

        return {
            "ticker": ticker,
            "price": price,
            "rsi": last_rsi,
            "macd_cross": macd_cross,
            "macd_above_signal": macd_above_signal,
            "sma50": sma50,
            "sma200": sma200,
            "position_52w": position_52w,
            "analyst_signal": analyst_signal,
        }
    except Exception as exc:  # noqa: BLE001
        logger.error("Fel vid analys av %s: %s", ticker, exc)
        return None
