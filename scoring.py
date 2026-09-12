"""
Bygger en samlad rekommendation utifrån flera signaler, och skriver
en mall-baserad förklaring på svenska för varje faktor som bidrog.

Detta är den "deterministiska" förklaringen som alltid finns med.
Den valfria AI-genererade sammanfattningen (llm_explain.py) bygger
vidare på samma strukturerade data.
"""

from dataclasses import dataclass, field

import config as cfg


@dataclass
class ScoreResult:
    total_score: int
    label: str  # STRONG BUY / BUY / HOLD / SELL / STRONG SELL
    bullets: list[str] = field(default_factory=list)


def _score_to_label(score: int) -> str:
    if score >= cfg.LABEL_STRONG_BUY:
        return "STRONG BUY"
    if score >= cfg.LABEL_BUY:
        return "BUY"
    if score <= cfg.LABEL_STRONG_SELL:
        return "STRONG SELL"
    if score <= cfg.LABEL_SELL:
        return "SELL"
    return "HOLD"


def compute_composite_score(
    *,
    rsi: float,
    macd_cross: str | None,
    macd_above_signal: bool,
    price: float,
    sma50: float | None,
    sma200: float | None,
    position_52w: float | None,
    analyst_signal: str,
) -> ScoreResult:
    score = 0
    bullets = []

    # --- RSI ---
    if rsi < cfg.RSI_OVERSOLD:
        score += cfg.SCORE_RSI_OVERSOLD
        bullets.append(f"RSI är {rsi} (översåld) → köpsignal ({cfg.SCORE_RSI_OVERSOLD:+d})")
    elif rsi < 45:
        score += cfg.SCORE_RSI_LOW
        bullets.append(f"RSI är {rsi} (svagt) → lutar mot köp ({cfg.SCORE_RSI_LOW:+d})")
    elif rsi > cfg.RSI_OVERBOUGHT:
        score += cfg.SCORE_RSI_OVERBOUGHT
        bullets.append(f"RSI är {rsi} (överköpt) → säljsignal ({cfg.SCORE_RSI_OVERBOUGHT:+d})")
    elif rsi > 55:
        score += cfg.SCORE_RSI_HIGH
        bullets.append(f"RSI är {rsi} (starkt) → lutar mot sälj ({cfg.SCORE_RSI_HIGH:+d})")
    else:
        bullets.append(f"RSI är {rsi} (neutralt läge, 45–55)")

    # --- MACD ---
    if macd_cross == "bullish":
        score += cfg.SCORE_MACD_BULLISH_CROSS
        bullets.append(f"MACD korsade nyligen upp genom signallinjen → köpsignal ({cfg.SCORE_MACD_BULLISH_CROSS:+d})")
    elif macd_cross == "bearish":
        score += cfg.SCORE_MACD_BEARISH_CROSS
        bullets.append(f"MACD korsade nyligen ner genom signallinjen → säljsignal ({cfg.SCORE_MACD_BEARISH_CROSS:+d})")
    elif macd_above_signal:
        score += cfg.SCORE_MACD_ABOVE
        bullets.append(f"MACD ligger fortsatt över signallinjen → positivt momentum ({cfg.SCORE_MACD_ABOVE:+d})")
    else:
        score += cfg.SCORE_MACD_BELOW
        bullets.append(f"MACD ligger fortsatt under signallinjen → negativt momentum ({cfg.SCORE_MACD_BELOW:+d})")

    # --- Trend (SMA50/SMA200) ---
    if sma50 is not None and sma200 is not None:
        if price > sma50 > sma200:
            score += cfg.SCORE_TREND_UP
            bullets.append(f"Kursen ({price}) ligger över både 50- och 200-dagars glidande medelvärde → uppåtgående trend ({cfg.SCORE_TREND_UP:+d})")
        elif price < sma50 < sma200:
            score += cfg.SCORE_TREND_DOWN
            bullets.append(f"Kursen ({price}) ligger under både 50- och 200-dagars glidande medelvärde → nedåtgående trend ({cfg.SCORE_TREND_DOWN:+d})")
        else:
            bullets.append("Trenden är blandad (pris, SMA50 och SMA200 inte samstämmiga)")
    else:
        bullets.append("För kort historik för att avgöra långsiktig trend (SMA200 saknas)")

    # --- Position i 52-veckorsintervall ---
    if position_52w is not None:
        if position_52w <= cfg.POSITION_52W_LOW_THRESHOLD:
            score += cfg.SCORE_NEAR_52W_LOW
            bullets.append(f"Kursen ligger {position_52w}% upp i 52-veckorsintervallet → nära årslägsta, möjligt bra ingångsläge ({cfg.SCORE_NEAR_52W_LOW:+d})")
        elif position_52w >= cfg.POSITION_52W_HIGH_THRESHOLD:
            bullets.append(f"Kursen ligger {position_52w}% upp i 52-veckorsintervallet → nära årshögsta (momentum, men risk för överköpt läge)")
        else:
            bullets.append(f"Kursen ligger {position_52w}% upp i 52-veckorsintervallet")

    # --- Analytikerkonsensus ---
    if analyst_signal == "BUY":
        score += cfg.SCORE_ANALYST_BUY
        bullets.append(f"Analytikerkonsensus: Buy ({cfg.SCORE_ANALYST_BUY:+d})")
    elif analyst_signal == "SELL":
        score += cfg.SCORE_ANALYST_SELL
        bullets.append(f"Analytikerkonsensus: Sell ({cfg.SCORE_ANALYST_SELL:+d})")
    elif analyst_signal == "HOLD":
        bullets.append("Analytikerkonsensus: Hold (0)")
    else:
        bullets.append("Analytikerkonsensus: okänd/saknas")

    label = _score_to_label(score)
    bullets.append(f"Totalpoäng: {score:+d} → Rekommendation: {label}")

    return ScoreResult(total_score=score, label=label, bullets=bullets)
