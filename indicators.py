"""
Tekniska indikatorer, implementerade rakt av med pandas
(inga externa TA-bibliotek behövs, så det finns inget som kan
krocka med olika Python/pandas-versioner i GitHub Actions).
"""

import pandas as pd


def rsi(close: pd.Series, period: int = 14) -> pd.Series:
    """Klassisk RSI (Wilder-utjämning)."""
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def sma(close: pd.Series, period: int) -> pd.Series:
    return close.rolling(window=period).mean()


def macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def detect_macd_cross(macd_line: pd.Series, signal_line: pd.Series, lookback: int = 3) -> str | None:
    """
    Kollar om MACD-linjen har korsat signallinjen någon gång de senaste
    `lookback` dagarna. Returnerar "bullish", "bearish" eller None.
    """
    diff = macd_line - signal_line
    if len(diff) < lookback + 1:
        return None

    current = diff.iloc[-1]
    past = diff.iloc[-(lookback + 1)]

    if past <= 0 < current:
        return "bullish"
    if past >= 0 > current:
        return "bearish"
    return None


def position_in_52w_range(high: pd.Series, low: pd.Series, close: pd.Series, lookback: int = 252) -> float | None:
    """
    Var i 52-veckorsintervallet ligger senaste priset?
    0%   = på årslägsta
    100% = på årshögsta
    """
    if len(close) < 2:
        return None

    window_high = high.tail(lookback).max()
    window_low = low.tail(lookback).min()
    last_price = close.iloc[-1]

    if window_high == window_low:
        return None

    pct = (last_price - window_low) / (window_high - window_low) * 100
    return round(float(pct), 1)
