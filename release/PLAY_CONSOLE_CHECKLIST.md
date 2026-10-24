# ✅ Checklist Pubblicazione Google Play Console — Caregiver Senior v1.1.1

Guida operativa passo-passo. Segui l'ordine, spunta ogni sezione, e in ~2 ore avrai la scheda pronta per la revisione Google.

---

## 🎯 Sintesi rapida

| Cosa serve | File | Stato |
|---|---|---|
| Account Play Console attivo (25 USD una tantum) | — | ⬜ Da fare |
| File `.aab` firmato | `caregiver-sync-v1.1.1.aab` | ✅ Pronto |
| Icona 512×512 | `store-graphics/icon-512.png` | ✅ Pronto |
| Feature graphic 1024×500 | *da generare* | ⏳ Manca |
| Screenshot 1080×1920 (min 2, consigliati 5) | `screenshots/01-05*.png` | ✅ Pronto |
| Descrizione breve + lunga | `MARKETING.md` | ✅ Pronto |
| Modulo Sicurezza Dati | `DATA_SAFETY.md` | ✅ Pronto |
| Privacy policy pubblicata su URL | `PRIVACY_POLICY.md` → *da pubblicare* | ⏳ Manca |
| Keystore salvata in luoghi sicuri | `caregiver-sync-release.jks` | ✅ Pronto |

---

## 📋 STEP 1 — Account Google Play Console

- ⬜ Vai su https://play.google.com/console
- ⬜ Accedi con l'account Google che vuoi usare (idealmente un account dedicato all'azienda, non personale)
- ⬜ Paga la **quota di iscrizione: 25 USD una tantum**
- ⬜ Compila la sezione **"Dettagli account sviluppatore"**:
  - Tipo: personale o organizzazione (per un'app medicale meglio organizzazione se possibile)
  - Nome sviluppatore visibile: es. "Caregiver Senior" (**non modificabile facilmente**, sceglilo bene)
  - Email di contatto pubblico
  - Indirizzo (verrà mostrato sulla scheda Play)
- ⬜ Verifica identità con documento (richiesto per app medicali dal 2023)

> ⏱️ Tempo: 30-60 min. Approvazione account: **1-3 giorni lavorativi**.

---

## 📋 STEP 2 — Pubblica la Privacy Policy

**Ordine cronologico**: fai questo PRIMA di compilare la scheda, perché serve un URL pubblico.

### Opzione A — Notion (più veloce, 5 minuti)
- ⬜ Apri Notion, crea una nuova pagina "Privacy Policy — Caregiver Senior"
- ⬜ Apri `PRIVACY_POLICY.md`, copia tutto il testo
- ⬜ Incolla nella pagina Notion
- ⬜ Sostituisci i placeholder `[…]` con i tuoi dati reali:
  - Ragione sociale
  - Indirizzo
  - Email (`supporto@caregiversync.example` → il tuo email vero)
  - Foro competente (es. "Milano")
- ⬜ Impostazioni pagina → **"Condividi sul Web"** → **Attiva**
- ⬜ Copia l'URL pubblico (es. `https://tuo-workspace.notion.site/Privacy-Policy-...`)

### Opzione B — GitHub Pages (più professionale, 15 minuti)
- ⬜ Crea repo pubblico `caregiver-sync-legal`
- ⬜ Aggiungi `privacy.md` con il contenuto di `PRIVACY_POLICY.md` (dopo aver sostituito i placeholder)
- ⬜ Impostazioni → Pages → attiva su branch `main`
- ⬜ URL sarà `https://tuo-user.github.io/caregiver-sync-legal/privacy.html`

### Opzione C — Il tuo sito
- ⬜ Se hai già un dominio (es. `caregiversync.it`), pubblica il file come `/privacy.html`

⚠️ **L'URL deve essere accessibile pubblicamente da chiunque, senza login.**

---

## 📋 STEP 3 — Crea l'app su Play Console

- ⬜ Play Console → **Tutte le app** → **Crea app**
- ⬜ Nome dell'app: `Caregiver Senior` (visibile sullo store, modificabile dopo)
- ⬜ Lingua predefinita: **Italiano - it-IT**
- ⬜ Tipo: **App** (non gioco)
- ⬜ Gratuita o a pagamento: **Gratuita**
- ⬜ Dichiarazioni obbligatorie:
  - ✅ Ho letto e accetto le Norme sul programma per gli sviluppatori
  - ✅ Accetto che l'app sia soggetta alle norme USA sull'esportazione
- ⬜ Clicca **Crea app**

---

## 📋 STEP 4 — Configura la scheda del Play Store

**Menu laterale → "Cresci → Presenza in store → Scheda del Play Store principale"**

### 4.1 Dettagli app
- ⬜ **Nome app**: `Caregiver Senior: cura & IA` (24/30 caratteri, da `MARKETING.md`)
- ⬜ **Descrizione breve** (80 char): copia da `MARKETING.md` sezione "Descrizione breve":
  > `Diario condiviso per assistiti anziani e cronici, con consegne generate dall'IA`
- ⬜ **Descrizione completa** (max 4000 char): copia dal `MARKETING.md` sezione "Descrizione completa"

### 4.2 Grafica

Sezione | File | Note
---|---|---
**Icona dell'app** | `store-graphics/icon-512.png` | Trascina il PNG 512×512
**Feature graphic** | *manca* (1024×500) | Vedi Step 5 sotto per rimediare
**Screenshot smartphone** | `screenshots/01-05*.png` in ordine | Almeno 2, consigliati 5 in ordine numerico
**Screenshot tablet 7"** | opzionale | Puoi lasciarli vuoti per la prima release
**Screenshot tablet 10"** | opzionale | Puoi lasciarli vuoti per la prima release
**Video promozionale** | opzionale | URL YouTube 30-120s (raddoppia il conversion rate)

### 4.3 Categorizzazione
- ⬜ **Tipo di app**: App
- ⬜ **Categoria**: **Medicina** (Medical) — categoria consigliata per app che aiutano nella cura
- ⬜ Tag: `salute`, `medico`, `caregiver`, `anziani`, `badante`, `diario clinico`

### 4.4 Dettagli di contatto
- ⬜ Email: la tua email di supporto
- ⬜ Sito web: (opzionale) il tuo dominio se ce l'hai
- ⬜ **Privacy Policy**: incolla l'URL pubblicato nello Step 2 ⚠️ **obbligatorio**

Clicca **Salva** in fondo a ogni sezione.

---

## 📋 STEP 5 — Feature Graphic (l'immagine promo mancante)

L'unico asset che ancora manca. **Non blocca la sottomissione tecnicamente ma la scheda risulterà meno accattivante**.

Se vuoi te la genero: scrivimi *"generami il feature graphic"* e in 2 minuti hai un PNG 1024×500 in stile brand teal.

Alternativa rapida DIY (15 min):
- Apri Canva → template "Google Play Feature Graphic"
- Sfondo teal `#0F766E`
- Al centro: logo cuore bianco + testo "Caregiver Senior — cura condivisa con IA"
- Esporta PNG 1024×500

---

## 📋 STEP 6 — Compila i moduli obbligatori "App Content"

**Menu laterale → Norme → Contenuti dell'app**

### 6.1 Norme sulla privacy ✅
- ⬜ Incolla l'URL pubblicato nello Step 2

### 6.2 Accesso all'app
- ⬜ Rispondi: **"Tutte le funzionalità dell'app sono disponibili senza restrizioni di accesso"** (l'app non ha login)

### 6.3 Annunci
- ⬜ **La mia app non contiene annunci**

### 6.4 Classificazione dei contenuti
- ⬜ Avvia il **questionario di classificazione IARC**
- ⬜ Categoria: **Reference, News, or Education**
- ⬜ Alle domande:
  - Violenza: No
  - Contenuti sessuali: No
  - Linguaggio volgare: No
  - Sostanze controllate: No
  - Simulazione di gioco d'azzardo: No
  - Contenuti generati da utenti/social: **Sì** (i caregiver inseriscono dati liberi)
  - Condivisione della posizione utente: No
  - Info personali/finanziarie: **Sì** (dati sanitari sull'assistito)
- ⬜ Risultato atteso: **PEGI 3** in Europa, **Everyone** in USA

### 6.5 Pubblico di destinazione
- ⬜ Fascia età: **18+** (contenuti sanitari)
- ⬜ App attrattiva per bambini: **No**

### 6.6 Sicurezza dei dati ⭐ (importante!)
- ⬜ Segui **esattamente** il documento `DATA_SAFETY.md` — è compilato apposta con le risposte corrette
- ⬜ Dichiarazioni chiave:
  - Dati sanitari (Health info): **Sì**
  - Crittografia in transito: **Sì**
  - Cancellazione utente disponibile: **Sì, in-app**
  - Condivisione con terze parti: **Sì** — Anthropic per funzione IA
- ⬜ Nel campo "additional details" incolla il testo suggerito nel documento

### 6.7 App per famiglie
- ⬜ **Non è un'app per famiglie**

### 6.8 Attività finanziaria/salute/COVID-19
- ⬜ **App di salute**: **Sì**
- ⬜ Alla domanda "L'app fornisce diagnosi mediche o cure?" → **NO** (fondamentale per non finire in categoria "dispositivo medico")
- ⬜ Descrizione uso: "Strumento di supporto organizzativo per la coordinazione tra caregiver di persone anziane e croniche. Non fornisce diagnosi né cure."

### 6.9 Google Play per governo
- ⬜ **Non applicabile**

---

## 📋 STEP 7 — Prezzo e distribuzione

**Menu laterale → Distribuisci → Prezzo e distribuzione**

- ⬜ App gratuita
- ⬜ Paesi: seleziona quelli di tuo interesse (minimo l'Italia). Puoi selezionare tutta l'UE + Svizzera per pubblico italiano diaspora.
- ⬜ App primaria per bambini: **No**
- ⬜ Contiene annunci: **No**
- ⬜ Norme di contenuti + esportazione: accetta

---

## 📋 STEP 8 — Carica l'AAB in una release di produzione

**Menu laterale → Rilascio → Produzione**

- ⬜ Clicca **Crea nuova release**
- ⬜ Sezione **"Firma dell'app da Google Play"**: alla prima release Google ti proporrà di attivarla
  - ✅ **Accetta la firma Play App Signing** (Google gestirà la chiave finale, la tua keystore diventa "chiave di upload")
- ⬜ Trascina il file `caregiver-sync-v1.1.1.aab`
- ⬜ Attendi il caricamento (30-60s)
- ⬜ Nome release: `1.1.1 (3)`
- ⬜ Note della release (max 500 char in italiano) — copia da `MARKETING.md` sezione "Note release (v1.1.0)"

---

## 📋 STEP 9 — Anteprima e invio per la revisione

- ⬜ Menu → **Pubblicazione → Panoramica pubblicazione**
- ⬜ Verifica il **checklist di errori** che appare in cima. Correggi ogni cosa rossa/arancione.
- ⬜ Se tutto verde: clicca **Invia per la revisione**

⏱️ **Tempo di revisione atteso**: 2-7 giorni lavorativi la prima volta. Aggiornamenti successivi solitamente 4-24h.

Riceverai una email quando l'app è approvata. Compare su Google Play entro poche ore dall'approvazione.

---

## 🚨 Errori comuni da evitare

| Errore Play Console | Soluzione |
|---|---|
| "Missing target SDK 34+" | ✅ Già risolto (targetSdk 35) |
| "APK/AAB non firmato" | ✅ Già firmato (SHA256withRSA) |
| "Privacy policy URL non raggiungibile" | Verifica che l'URL sia PUBBLICO, no login |
| "Categoria Medical richiede documentazione" | Nel questionario dichiara che NON è dispositivo medico, è supporto organizzativo |
| "Data safety incompleta" | Segui il documento fornito, NON saltare la sezione "Health info" |
| "Icona con trasparenza" | ✅ Già opaca (verificato) |
| "Screenshot troppo pochi" | ✅ Hai 5 (minimo 2, consigliati 4-8) |

---

## 📁 Dove sono tutti i file

```
/app/release/
├── caregiver-sync-v1.1.1.aab       ⭐ Da caricare
├── caregiver-sync-v1.1.1.apk           (Solo per test sul telefono)
├── caregiver-sync-release.jks          🔐 FAI BACKUP!
├── DATA_SAFETY.md                      Come compilare "Sicurezza dei dati"
├── MARKETING.md                        Testi scheda Play Store
├── PRIVACY_POLICY.md                   Da pubblicare come URL
├── PLAY_CONSOLE_CHECKLIST.md           ← Questo file
├── README.md                           Indice + credenziali keystore
├── SORGENTE_CODICE.zip                 Codice sorgente
├── screenshots/                        5 screenshot 1080×1920
│   ├── 01-home.png
│   ├── 02-detail.png
│   ├── 03-handover.png
│   ├── 04-trend.png
│   ├── 05-menu.png
│   └── README.md
├── store-graphics/                     Icona + varianti
│   ├── icon-512.png                    ⭐ Icona Play Store
│   ├── icon-1024.png
│   ├── icon-192.png
│   ├── adaptive-icon-fg.png
│   └── README.md
└── google-play-kit.zip                 Pacchetto zip con TUTTO
```

Scarica `google-play-kit.zip` per avere tutto in un colpo solo.

---

## ⏱️ Timeline realistica

| Attività | Tempo attivo | Tempo totale |
|---|---|---|
| Registrazione account Play Console | 30-60 min | 1-3 giorni (verifica) |
| Pubblicazione privacy policy | 10 min | subito |
| Compilazione scheda Play Store | 30-60 min | subito |
| Moduli App Content | 30 min | subito |
| Upload AAB + release | 15 min | subito |
| **Revisione Google** | 0 (attesa) | **2-7 giorni** |
| **TOTALE fino alla pubblicazione** | ~3 ore attive | **3-10 giorni** |

Buona pubblicazione! 🚀
