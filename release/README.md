# 📱 Caregiver Sync — Release v1.0.0 per Google Play

## 🎯 File pronti per la pubblicazione (v1.1.0)

| File | Dimensione | Uso |
|---|---|---|
| **`caregiver-sync-v1.1.1.aab`** | 4.0 MB | ⭐ **Caricare su Google Play Console** |
| `caregiver-sync-v1.1.1.apk` | 4.2 MB | Test diretto sul telefono (installazione manuale) |
| `caregiver-sync-release.jks` | 2.7 KB | 🔐 **Keystore di firma — CONSERVA CON CURA** |
| `MARKETING.md` | — | Titolo, descrizioni e testi Play Store |
| `DATA_SAFETY.md` | — | Compilazione modulo "Sicurezza dei Dati" di Google |
| `PRIVACY_POLICY.md` | — | Privacy policy pronta da pubblicare (GitHub Pages, Notion, ecc.) |
| `SORGENTE_CODICE.zip` | — | Codice sorgente completo (frontend + backend) |
| **`screenshots/`** | — | 5 screenshot 1080×1920 pronti da caricare in Play Console |
| **`store-graphics/`** | — | 🎨 Icona 512×512 + varianti + adaptive icon Android |
| `screenshots.zip` | 1.6 MB | Stessa cartella zippata per download rapido |

## 🆕 Novità v1.1.0 rispetto a v1.0.0

- ✅ **Home ridisegnata** con saluto contestuale (buongiorno/pomeriggio/sera), data del giorno, quick stats (assistiti, parametri, farmaci, sintomi) e barra di ricerca
- ✅ **Card assistito** con avatar iniziali (es. "MR" per Maria Rossi) e chevron per apertura più veloce
- ✅ **Modifica voce diario** dal menu `⋮` → "Modifica voce" → dialog con tipo/etichetta/valore/unità
- ✅ **Storico consegne IA** salvato automaticamente — ogni handover generato resta consultabile con timestamp e preview
- ✅ **Grafico Andamento parametri vitali** (recharts) — trend visivo di pressione/glicemia/temperatura negli ultimi 30 giorni, con supporto min/max (es. 145/85 mmHg tracciato come 2 linee)
- ✅ Nuovi endpoint API: `PATCH /entries/{id}`, `GET/DELETE /handovers`, `GET /patients/{id}/trend`

## 🔐 Configurazione build

| Parametro | Valore |
|---|---|
| **Package name (unico)** | `com.caregiversync.assistiti` |
| **Version code** | `2` |
| **Version name** | `1.1.0` |
| **minSdk** | `23` (Android 6.0+) |
| **targetSdk** | `35` (Android 15) — soddisfa requisiti Play Store 2026 |
| **Firma** | RSA 2048 SHA-256, valida fino al 19/12/2053 (27 anni) |
| **Framework** | Capacitor 6 (WebView Chromium nativo) |
| **Backend** | https://app-release-config.emergent.host |

## 🔑 Credenziali keystore

> ⚠️ **CRITICO — SALVA IN UN POSTO SICURO (password manager + backup cloud del `.jks`)**
> Se perdi la keystore o le password **non potrai più aggiornare l'app** su Google Play.

```
Keystore file:    caregiver-sync-release.jks
Alias:            caregiver-sync
Store password:   CGSync2026#SecureKey
Key password:     CGSync2026#SecureKey
Algoritmo:        RSA 2048 bit, SHA256withRSA
Validità:         10.000 giorni (fino al 19 dicembre 2053)
Fingerprint SHA-256:
  55:B2:98:5B:02:4C:9C:21:1E:3E:71:97:B6:48:3E:32:
  25:02:4D:B9:6E:8A:B0:EC:5A:1D:54:EF:1A:EF:CE:F1
Owner:  CN=Caregiver Sync Assistiti, OU=Mobile,
        O=Caregiver Sync, L=Milano, ST=IT, C=IT
```

## 🚀 Passi per la pubblicazione su Google Play Console

### 1) Account (una tantum)
- https://play.google.com/console
- Registrazione: **25 USD una tantum**
- Verifica identità con documento

### 2) Crea la nuova app
- **Crea app** → Nome: **Caregiver Sync**, Lingua principale: Italiano, App gratuita

### 3) Compila queste sezioni (obbligatorie prima del rollout)
| Sezione | Cosa fare |
|---|---|
| **Scheda del Play Store** | Usa i testi in `MARKETING.md` + carica icona 512×512, feature graphic 1024×500, ≥2 screenshot |
| **Sicurezza dei dati** | Segui esattamente il template in `DATA_SAFETY.md` |
| **Classificazione contenuti** | Compila il questionario (probabilmente 13+) |
| **Pubblico e contenuti** | 18+ (contenuti sanitari) |
| **Norme sulla privacy** | Serve URL pubblico → pubblica `PRIVACY_POLICY.md` su GitHub Pages / Notion e incolla l'URL |

### 4) Upload dell'AAB
- **Produzione** → **Crea nuova release** → trascina `caregiver-sync-v1.1.1.aab`
- Nota release: *"Prima versione. Registrazione assistiti, diario clinico condiviso, generazione consegna con IA, cancellazione dati GDPR-compliant."*
- Rivedi → **Avvia rollout in produzione**

### 5) Attesa
Prima revisione: **2-7 giorni lavorativi**. Poi l'app appare su Google Play.

## 📲 Testare l'APK sul telefono prima di pubblicare

1. Trasferisci `caregiver-sync-v1.1.1.apk` sul tuo Android (USB / Drive / email)
2. Impostazioni → App → Accesso speciale → Installa app sconosciute → autorizza il tuo file manager
3. Apri il file APK dal telefono → **Installa**
4. **IMPORTANTE**: l'app fa chiamate a `https://app-release-config.emergent.host`. Se il backend è offline, l'app mostra schermo bianco.

## ⚙️ Ambiente di build (per riferimento)

Il file AAB è stato compilato in questo ambiente con:
- OpenJDK 17
- Android Command-line Tools + Build-Tools 35.0.0 + Platform-tools
- Capacitor 6 + AGP 8.7 + Gradle 8.11
- `aapt2` v2.19-11948202 (via qemu-x86_64 su ARM64 host)

## 🆘 Cosa NON dimenticare

- ✅ **Backup della keystore `.jks`** in almeno 2 posti (Drive/Dropbox + password manager)
- ✅ Aggiornare `versionCode` (2, 3, ...) e `versionName` a ogni nuova release
- ✅ Backend Emergent **deve rimanere online** o l'app non funziona
- ✅ Sezione "Sicurezza dati" Play: dichiara raccolta dati sanitari + cancellazione in-app disponibile
- ✅ Privacy policy deve avere URL pubblico stabile (no localhost, no preview URL)
