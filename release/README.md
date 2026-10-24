# 📦 Caregiver Senior v1.1.1 — Kit di Pubblicazione Google Play

Tutto quello che serve per pubblicare l'app su Google Play Console. Segui il file **`PLAY_CONSOLE_CHECKLIST.md`** per la guida step-by-step.

---

## ⚡ Scorciatoia — Download tutto in un colpo

**`google-play-kit.zip`** (9.4 MB) contiene AAB, APK, keystore, screenshot, icona e tutti i documenti. Scaricalo e hai tutto.

---

## 📁 Contenuto della cartella

### 🔴 Da caricare in Play Console
| File | Dove va in Play Console |
|---|---|
| **`caregiver-sync-v1.1.1.aab`** (4.0 MB) | Produzione → Crea release → Trascina l'AAB |
| **`store-graphics/icon-512.png`** (32 KB) | Scheda del Play Store → Grafica → Icona dell'app |
| **`screenshots/01-05*.png`** (5 file, 1080×1920) | Scheda del Play Store → Grafica → Screenshot smartphone |

### 📄 Testi da copiare in Play Console
| File | Cosa contiene |
|---|---|
| **`MARKETING.md`** | Titolo (24/30), descrizione breve (79/80), descrizione lunga (~3200/4000) |
| **`DATA_SAFETY.md`** | Risposte esatte per il modulo Sicurezza Dati |
| **`PRIVACY_POLICY.md`** | Privacy policy GDPR completa **da pubblicare come URL** prima di sottomettere |

### 🔐 Da conservare gelosamente
| File | Perché |
|---|---|
| **`caregiver-sync-release.jks`** (2.7 KB) | Keystore di firma — se la perdi non puoi più aggiornare l'app |

### 📖 Documentazione
| File | Cosa contiene |
|---|---|
| **`PLAY_CONSOLE_CHECKLIST.md`** ⭐ | **Checklist operativa step-by-step** — segui questa dall'inizio alla fine |
| `README.md` (questo file) | Indice generale |
| `SORGENTE_CODICE.zip` (148 KB) | Codice sorgente frontend + backend + icone Android |

### 🎁 Extra
| File | Note |
|---|---|
| `caregiver-sync-v1.1.1.apk` (4.2 MB) | Per installare direttamente sul telefono e testare (non serve per Play Store) |
| `screenshots.zip` (1.6 MB) | Screenshots zippati |
| `icon-source.svg` | Sorgente vettoriale dell'icona (per modifiche future) |
| `adaptive-icon-foreground.svg` | Sorgente adaptive icon Android |

---

## 🔐 Credenziali keystore (⚠️ salva in password manager AL VOLO)

```
Keystore file:    caregiver-sync-release.jks
Alias:            caregiver-sync
Store password:   CGSync2026#SecureKey
Key password:     CGSync2026#SecureKey
Algoritmo:        RSA 2048 bit, SHA256withRSA
Validità:         fino al 19 dicembre 2053
Fingerprint SHA-256:
  55:B2:98:5B:02:4C:9C:21:1E:3E:71:97:B6:48:3E:32:
  25:02:4D:B9:6E:8A:B0:EC:5A:1D:54:EF:1A:EF:CE:F1
Owner:  CN=Caregiver Senior Assistiti, OU=Mobile,
        O=Caregiver Senior, L=Milano, ST=IT, C=IT
```

> ⚠️ **CRITICO**: Se perdi la keystore o le password **NON POTRAI PIÙ AGGIORNARE L'APP** su Google Play. Salva subito in 1Password/Bitwarden + carica il file `.jks` in una cartella cloud sicura (Drive/Dropbox/iCloud).

---

## ✅ Configurazione tecnica AAB

| Parametro | Valore | Note |
|---|---|---|
| **Package name** | `com.caregiversync.assistiti` | Unico, non modificabile dopo pubblicazione |
| **versionCode** | `3` | Google Play richiede sempre crescente |
| **versionName** | `1.1.1` | Visibile all'utente |
| **minSdk** | `23` (Android 6.0+) | Copre >99% dei device attivi |
| **targetSdk** | `35` (Android 15) | ✅ Rispetta requisito Play Store 2026 |
| **Formato** | Android App Bundle (`.aab`) | Obbligatorio dal 2021 |
| **Firma** | RSA 2048 SHA-256 | Valida 27 anni |
| **Backend URL** | `https://app-release-config.emergent.host` | Incorporato nel bundle |
| **Framework** | Capacitor 6 + WebView Chromium | Mantiene 100% del codice React |
| **Icona** | Cuore Lucide bianco su teal `#0F766E` con gradiente | 5 densità Android + adaptive |

---

## 🎯 Ordine consigliato di pubblicazione

Consulta **`PLAY_CONSOLE_CHECKLIST.md`** per la versione dettagliata. In sintesi:

1. **Registra account** Play Console (25 USD, 1-3 giorni per verifica) → *puoi iniziare adesso mentre aspetti*
2. **Pubblica privacy policy** come URL pubblico (Notion in 5 min o GitHub Pages)
3. **Crea l'app** su Play Console
4. **Compila la scheda** con testi da `MARKETING.md`
5. **Carica grafica**: icona `icon-512.png` + 5 screenshot
6. **Compila App Content** (sicurezza dati, classificazione, ecc.) usando `DATA_SAFETY.md`
7. **Carica AAB** in Produzione → crea release 1.1.1
8. **Invia per revisione** → attesa **2-7 giorni**

---

## 🆘 Cosa NON è ancora incluso (impatto minimo, ma nice-to-have)

- **Feature graphic 1024×500** — l'immagine promo in cima alla scheda. La scheda funziona anche senza (rimane la sola icona ingrandita), ma un feature graphic dedicato aumenta il conversion rate. Se lo vuoi, dimmi *"generami il feature graphic"* e te lo produco allo stesso livello di qualità dell'icona.
- **Video promozionale YouTube 30-120s** — ancora più impattante ma richiede editing video

---

## 📝 Cambiamenti versione (changelog)

### v1.1.1 (versionCode 3) — questa release
- 🎨 Nuove icone Play Store 512×512 + tutte le densità Android
- Corretti alcuni glitch grafici minori (recharts warning)

### v1.1.0 (versionCode 2)
- 🏠 Home ridisegnata con saluto contestuale, quick stats, ricerca
- ✏️ Modifica voci diario dal menu ⋮
- 📚 Storico consegne IA salvato automaticamente
- 📈 Grafico Andamento parametri vitali (recharts)
- Nuovi endpoint API: PATCH /entries, /handovers, /trend

### v1.0.0 (versionCode 1) — prima release
- Registrazione assistiti, diario clinico condiviso
- 🤖 Generazione consegne con IA (Claude Sonnet 4.6)
- Cancellazione dati completa GDPR-compliant
- Menu contestuali `⋮` mobile-first
- targetSdk 35 per Play Store 2026

---

**Buona pubblicazione!** 🚀 In caso di problemi durante la sottomissione, scrivimi.
