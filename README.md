# Aktie-bevakare med pushnotiser

Bevakar en lista svenska och amerikanska aktier, räknar ut en samlad
teknisk/analytiker-rekommendation (RSI + MACD + trend + 52-veckorsläge
+ analytikerkonsensus) och skickar en pushnotis via **ntfy.sh** varje
gång rekommendationen ändras — med en tydlig förklaring av varför.
Körs helt gratis via **GitHub Actions**.

## 1. Skapa ett ntfy-"topic" (din privata notiskanal)

1. Installera appen **ntfy** ([iOS](https://apps.apple.com/app/ntfy/id1625396347) /
   [Android](https://play.google.com/store/apps/details?id=io.heckel.ntfy)),
   eller använd webbversionen på https://ntfy.sh/app.
2. Hitta på ett unikt, svårgissat topic-namn, t.ex. `ditt-namn-aktier-8f2k1`
   (vem som helst som gissar namnet kan annars läsa dina notiser,
   eftersom ntfy.sh:s gratistjänst är öppen).
3. Prenumerera på det topic-namnet i appen.

## 2. Skapa ett GitHub-repo

1. Skapa ett nytt (gärna privat) repo på GitHub.
2. Ladda upp alla filer i den här mappen till repot
   (behåll mappstrukturen, särskilt `.github/workflows/monitor.yml`).

## 3. Lägg in topic-namnet som en "secret"

1. Gå till repot -> **Settings -> Secrets and variables -> Actions**.
2. Klicka **New repository secret**.
3. Namn: `NTFY_TOPIC`, Värde: topic-namnet du valde i steg 1.

## 4. (Valfritt) Slå på AI-skriven förklaringstext

Systemet skriver alltid en mall-baserad, punktvis förklaring
automatiskt (gratis, ingen extra tjänst behövs). Om du dessutom vill
att **Claude** ska skriva en sammanhängande, resonerande text kring
varje rekommendation (argument + motargument, baserat på siffrorna
och nyheterna):

1. Skaffa en API-nyckel på https://console.anthropic.com (kräver eget
   konto, det är en betaltjänst – kostnaden per körning är dock
   mycket liten eftersom det bara är kort text).
2. Lägg in den som ytterligare en secret i repot:
   Namn: `ANTHROPIC_API_KEY`, Värde: din nyckel.

Lämnas secreten tom/borttagen används bara mall-förklaringen – allt
annat i systemet fungerar precis likadant.

## 5. Testa

Gå till fliken **Actions** i repot, välj workflowen **Stock Monitor**,
klicka **Run workflow** för att köra den direkt istället för att vänta
på schemat. Första körningen bygger bara upp en "baseline" per aktie
(du får ingen notis då) – från och med att en akties rekommendation
ändras nästa gång får du en notis.

## Hur rekommendationen räknas fram

Varje faktor ger plus- eller minuspoäng, som summeras till en
rekommendation:

| Faktor | Vad som mäts | Poäng |
|---|---|---|
| RSI | Översåld/överköpt (14 dagar) | +2 / +1 / -1 / -2 |
| MACD | Nyligen korsning upp/ner, eller fortsatt över/under signallinjen | +2 / +1 / -1 / -2 |
| Trend | Pris vs. 50- och 200-dagars glidande medelvärde | +1 / -1 |
| 52-veckorsläge | Nära årslägsta = möjligt bra ingångsläge | +1 |
| Analytikerkonsensus | Yahoo Finances samlade rekommendation | +2 / 0 / -2 |

Totalpoängen mappas till: **STRONG BUY / BUY / HOLD / SELL / STRONG SELL**.
Du får en notis varje gång en akties rekommendation byter kategori –
notisen innehåller alltid en punktlista med exakt vilka faktorer som
bidrog (plus, om du satt upp steg 4, en skriven sammanfattning och
eventuella färska nyhetsrubriker).

## Anpassa

- **Vilka aktier**: redigera `config.py` (`SWEDISH_TICKERS` /
  `US_TICKERS`). Tickers för svenska aktier hittar du genom att söka
  på Yahoo Finance – de har suffixet `.ST`.
- **Känslighet / vikter**: alla trösklar och poäng ligger samlade
  längst upp i `config.py`.
- **Hur ofta det körs**: ändra `cron`-raden i
  `.github/workflows/monitor.yml` (tiden är i UTC).
- **Antal nyhetsrubriker per notis**: `NEWS_MAX_ITEMS` i `config.py`.

## Begränsningar att känna till

- Yahoo Finance är en inofficiell, gratis datakälla – bra för hobby-
  bruk men inte garanterat 100 % pålitlig eller lämplig för stora
  investeringsbeslut.
- Nyhetsrubrikerna används bara som kontext i notisen (och i
  underlaget till AI-sammanfattningen) – de räknas INTE in i
  poängmodellen, eftersom pålitlig nyhetssentiment kräver mer än en
  enkel regelmotor.
- `recommendationKey` finns inte alltid för mindre bevakade bolag –
  visas då som `UNKNOWN`.
- Den AI-skrivna sammanfattningen (steg 4) är helt valfri och kräver
  en egen, betald Anthropic-nyckel – inget i resten av systemet är
  beroende av den.
- ntfy.sh:s gratisnivå är ett öppet system; håll topic-namnet hemligt,
  eller kör din egen ntfy-server om du vill ha starkare sekretess.
