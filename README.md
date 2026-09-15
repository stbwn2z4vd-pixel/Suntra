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

## 4. (Valfritt) Slå på AI-skriven förklaring + oberoende bedömning

Systemet skriver alltid en mall-baserad, punktvis förklaring
automatiskt (gratis, ingen extra tjänst behövs) – **det är alltid
denna, tillsammans med poängmodellen, som avgör om en notis skickas.**

Om du dessutom vill ha en AI inkopplad får du **två extra saker** i
notisen, tydligt separerade från den tekniska rekommendationen:

- **AI-omdöme**: en egen, oberoende bedömning – "Håller med",
  "Delvis" eller "Skeptisk" + en konfidenssiffra 1–5. AI:n väger in
  färska nyheter (t.ex. en vinstvarning eller rättstvist) som det
  tekniska systemet inte kan se, och kan alltså vara oense med
  poängmodellen om nyheterna talar för det.
- **Textförklaring**: en sammanhängande text med argument för och
  eventuella motargument/risker.

Viktigt: AI:n **ersätter aldrig** poängmodellen – den lägger bara
till ett extra perspektiv ovanpå den redan beräknade rekommendationen.
Om AI-anropet skulle strula (nätverksfel, tillfällig gräns nådd, osv.)
skickas notisen ändå, bara utan AI-delen.

Två alternativ för vilken AI som används:

### Alternativ A: Gemini (gratis, rekommenderas)

1. Gå till https://aistudio.google.com/apikey och logga in med ett
   Google-konto.
2. Klicka **Create API key** – inget kreditkort krävs.
3. Lägg in den som en secret i repot: **Settings -> Secrets and
   variables -> Actions -> New repository secret**.
   Namn: `GEMINI_API_KEY`, Värde: nyckeln du fick.

Gratisnivån har en daglig gräns, men eftersom vi bara gör ett anrop
per aktie **och bara när dess rekommendation faktiskt ändras**
(inte varje körning), räcker den mer än väl för det här systemet.

### Alternativ B: Claude / Anthropic (betalt, bättre kvalitet)

1. Skaffa en API-nyckel på https://console.anthropic.com (kräver eget
   konto, det är en betaltjänst – kostnaden per körning är dock
   mycket liten eftersom det bara är kort text).
2. Lägg in den som secreten `ANTHROPIC_API_KEY` på samma sätt som
   ovan.

Om du sätter **båda** nycklarna prioriteras Claude. Lämnas båda
secrets tomma/borttagna används bara mall-förklaringen – allt annat
i systemet fungerar precis likadant.

## 5. Testa

Gå till fliken **Actions** i repot, välj workflowen **Stock Monitor**,
klicka **Run workflow** för att köra den direkt istället för att vänta
på schemat. Första körningen bygger bara upp en "baseline" per aktie
(du får ingen notis då) – från och med att en akties rekommendation
ändras nästa gång får du en notis.

## Hur och när det körs

Systemet körs automatiskt två gånger per vardag, med olika aktier vid
varje tillfälle:

- **~12:00 svensk tid**: bara **svenska** aktier (Stockholmsbörsen har
  öppnat, amerikanska börsen inte än).
- **~18:00 svensk tid**: bara **amerikanska** aktier (några timmar in
  i den amerikanska handelsdagen).

(Tiderna stämmer exakt under vintertid/CET; under sommartid/CEST blir
båda en timme senare eftersom GitHub Actions cron inte justerar för
sommartid automatiskt. Ändra klockslagen i `.github/workflows/monitor.yml`
om du vill finjustera.)

En manuell körning via **Run workflow** i Actions-fliken kör alltid
**alla** aktier (både svenska och amerikanska) oavsett tid på dygnet.

## Geopolitisk/makroekonomisk bevakning

Utöver de enskilda aktiernas rekommendationer kollar systemet vid
**varje körning** färska rubriker kopplade till breda marknadsindex
(S&P 500 och OMX Stockholm 30) - inte en specifik akties nyheter, utan
sådant som rör hela marknaden. En AI bedömer om något är en genuint
marknadspåverkande händelse (krig, sanktioner, handelstullar, stora
centralbanksbeslut, osv.) - vardaglig bolagsnyhet ignoreras.

Du får en separat notis ("⚠️ Möjlig marknadspåverkande händelse") bara
när något nytt och relevant dyker upp. Systemet minns vilka rubriker
det redan sett (sparat i `state.json`), så du får inte samma varning
upprepade gånger. Denna funktion kräver samma AI-nyckel som
AI-omdömet (`GEMINI_API_KEY` eller `ANTHROPIC_API_KEY`, se ovan) -
utan nyckel hoppas den bara över.

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
