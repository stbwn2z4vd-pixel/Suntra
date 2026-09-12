"""
Engångstest: skickar en dummy-notis via ntfy för att verifiera att
kopplingen GitHub Actions -> ntfy -> din mobil fungerar.

Kan tas bort när du väl sett att det funkar.
"""

from notify import send_notification

send_notification(
    title="Testnotis från aktie-bevakaren",
    message="Om du ser detta i mobilen funkar hela kedjan: GitHub Actions -> ntfy -> din telefon. 🎉",
    priority=3,
    tags=["white_check_mark"],
)
