# 📱 Caregiver Sync — File Android pronti

## 🎯 File generati

| File | Dimensione | Uso |
|---|---|---|
| **`caregiver-sync-v1.0.0.aab`** | 3.5 MB | ⭐ Da caricare su **Google Play Console** |
| `caregiver-sync-v1.0.0.apk` | 3.6 MB | Per installare direttamente sul tuo telefono (test) |
| `caregiver-sync-release.jks` | 2.7 KB | 🔐 **Keystore di firma — CONSERVA E FAI BACKUP!** |

## 🔐 Credenziali keystore (COPIALE IN UN POSTO SICURO)

```
Keystore file:  caregiver-sync-release.jks
Alias:          caregiver-sync
Store password: CaregiverSync2026!
Key password:   CaregiverSync2026!
Algoritmo:      RSA 2048, SHA256
Validità:       27 anni (fino al 17 dic 2053)
Fingerprint SHA-256:
  59:57:C0:1B:3D:2A:19:A6:74:EF:78:0B:38:AE:C7:19:
  1D:1F:F6:F8:FF:DF:88:2A:ED:25:A3:35:04:FB:4F:02
```

> ⚠️ **CRITICO**: Se perdi la keystore o le password non potrai più pubblicare aggiornamenti dell'app. Salvale in un password manager (1Password, Bitwarden) e fai una copia della `.jks` in cloud (Google Drive, Dropbox).

## 📤 Come pubblicare su Google Play

### 1. Crea account Google Play Console (una tantum)
- Vai su https://play.google.com/console
- Registrazione: **25 USD una tantum**
- Compila i tuoi dati fiscali (per app gratuite non serve pagamento setup)

### 2. Crea la scheda app
- **Crea app** → Nome: "Caregiver Sync", Lingua: Italiano, Gratuita
- Compila (obbligatorio):
  - **Scheda del Play Store**
    - Descrizione breve (max 80 caratteri): *"Diario clinico condiviso per assistiti anziani e cronici"*
    - Descrizione lunga (usa il testo suggerito dal PDF)
    - Icona app: PNG 512×512
    - Feature graphic: PNG 1024×500
    - Almeno 2 screenshot: 1080×1920 (usa Android Studio emulator o `adb screencap` dal tuo telefono)
  - **Classificazione contenuti** → completa il questionario (probabilmente "3+" o "13+")
  - **Sicurezza dei dati** → dichiara:
    - Raccogli dati sanitari (nome, condizioni mediche)
    - Dati crittografati in transito ✅
    - **Cancellazione dati disponibile in-app** ✅ (già implementata: Impostazioni → Reset totale)
    - Nessuna condivisione con terzi
  - **Pubblico e contenuti** → 18+ (per contenuti sanitari)
  - **Norme sulla privacy** → serve URL pubblico
    - Soluzione veloce: crea un file `privacy.md` su GitHub Pages con testo di privacy standard GDPR

### 3. Carica l'AAB
- Menu laterale → **Produzione** → **Crea nuova release**
- Trascina `caregiver-sync-v1.0.0.aab`
- Note release: *"Prima versione. Registrazione assistiti, diario clinico condiviso (parametri, farmaci, sintomi, note), cancellazione dati GDPR-compliant."*
- Rivedi → **Avvia rollout in produzione**

### 4. Attesa revisione
- Prima revisione: **2-7 giorni lavorativi**
- Riceverai email quando l'app è live sul Play Store

## 📲 Testare l'APK sul tuo telefono (opzionale ma consigliato)

1. Trasferisci `caregiver-sync-v1.0.0.apk` sul tuo telefono Android (via cavo USB o email/Drive)
2. Sul telefono: **Impostazioni** → **App** → **Accesso speciale** → **Installa app sconosciute** → attiva per il tuo file manager
3. Apri il file APK e installa
4. Prima di aprirlo: assicurati che il backend sia raggiungibile su https://app-release-config.emergent.host

> Nota: L'APK punta al backend di produzione. Se lo spegni, l'app mostra schermo bianco.

## 🔁 Come rilasciare aggiornamenti in futuro

Prima di ricompilare, modifica **`/app/frontend/android/app/build.gradle`**:

```gradle
versionCode 2         // incrementa ad ogni release
versionName "1.0.1"   // versione visibile all'utente
```

Poi rilancia (nell'ambiente Emergent, sblocchiamo l'ambiente e rifacciamo il build). Google Play richiede `versionCode` sempre crescente.

## ⚙️ Configurazione tecnica applicata

- **appId / applicationId**: `com.caregiversync.app`
- **App name**: Caregiver Sync
- **minSdkVersion**: 22 (Android 5.1+)
- **targetSdkVersion**: 34 (Android 14)
- **Backend URL** (impresso nel bundle): `https://app-release-config.emergent.host`
- **Splash screen**: teal `#0F766E`, 1.2s
- **Package**: Capacitor 6 (WebView Chromium nativo)
- **Firma**: RSA 2048 SHA-256 (release keystore)

## 🆘 Se qualcosa non va

- **App si apre ma schermo bianco** → il backend non risponde. Verifica https://app-release-config.emergent.host è live.
- **"App non installata"** all'installazione dell'APK → hai già una versione con firma diversa installata. Disinstallala prima.
- **Google Play rifiuta l'AAB con "Missing 64-bit"** → questo AAB include già arm64-v8a via Capacitor default. Se accade, contattami.
- **Google Play chiede la Play App Signing** → è **obbligatorio** per le nuove app: attiva "Play App Signing" e Google gestirà una chiave di upload separata. La tua keystore diventerà la chiave di upload.

---

**File AAB pronto**: `/app/release/caregiver-sync-v1.0.0.aab` — scaricalo e caricalo su Google Play. Buona pubblicazione! 🚀
