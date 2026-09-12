"""
Skickar pushnotiser via ntfy.sh (https://ntfy.sh), med JSON-publicering
(inte HTTP-headers) så att svenska tecken (åäö) alltid blir rätt.

Ingen inloggning krävs: du väljer ett eget, svårgissat "topic"-namn
(t.ex. "sven-aktier-8f2k1"), prenumererar på det i ntfy-appen, och
skriptet postar meddelanden till https://ntfy.sh med det topic-namnet.
"""

import logging
import os

import requests

logger = logging.getLogger(__name__)

NTFY_TOPIC = os.environ.get("NTFY_TOPIC")
NTFY_PUBLISH_URL = "https://ntfy.sh/"


def send_notification(title: str, message: str, priority: int = 3, tags: list[str] | None = None) -> None:
    """
    priority: 1 (min) - 5 (max), ntfy default är 3.
    tags: ntfy-emoji-taggar, t.ex. ["chart_with_upwards_trend"] eller ["chart_with_downwards_trend"]
    """
    if not NTFY_TOPIC:
        logger.error("NTFY_TOPIC saknas - kan inte skicka notis. Meddelande: %s", message)
        return

    payload = {
        "topic": NTFY_TOPIC,
        "title": title,
        "message": message,
        "priority": priority,
        "tags": tags or ["bar_chart"],
    }

    try:
        response = requests.post(NTFY_PUBLISH_URL, json=payload, timeout=15)
        response.raise_for_status()
        logger.info("Notis skickad: %s", title)
    except Exception as exc:  # noqa: BLE001
        logger.error("Kunde inte skicka notis: %s", exc)
