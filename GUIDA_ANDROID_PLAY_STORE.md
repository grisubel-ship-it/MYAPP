# Da web app React → APK/AAB per Google Play (Capacitor)

Guida pratica per prendere questa app **così com'è** e trasformarla in un file Android nativo caricabile su Google Play Store.

> **Metodo scelto**: [Capacitor](https://capacitorjs.com) di Ionic — impacchetta la tua React app in un contenitore nativo Android usando WebView. È lo stesso approccio usato da migliaia di app pubblicate sul Play Store (es. Sworkit, HomeAdvisor).

---

## 📋 Cosa ti serve sulla tua macchina locale

| Requisito | Versione | Come installarlo |
|---|---|---|
| **Node.js** | 20+ (22 raccomandato) | https://nodejs.org |
| **Java JDK** | 17 | `brew install openjdk@17` su Mac / winget su Windows |
| **Android Studio** | Meerkat o più recente | https://developer.android.com/studio |
| **Yarn** | qualsiasi | `npm install -g yarn` |

Dopo aver installato Android Studio:
1. Aprilo una volta → **More Actions** → **SDK Manager**
2. Installa **Android SDK 34** (o superiore) + **Build-Tools** + **Platform-Tools**
3. Aggiungi al tuo `~/.zshrc` o `~/.bashrc`:
   ```bash
   export ANDROID_HOME=$HOME/Library/Android/sdk   # Mac
   # export ANDROID_HOME=$HOME/Android/Sdk         # Linux
   export PATH=$PATH:$ANDROID_HOME/platform-tools:$ANDROID_HOME/emulator
   ```

---

## 🚀 Step 1 — Scarica il progetto sul tuo PC

Usa la funzione **"Save to GitHub"** nella chat Emergent per esportare il codice, poi clonalo localmente:

```bash
git clone https://github.com/TUO-USER/caregiver-sync.git
cd caregiver-sync/frontend
yarn install
```

---

## 🚀 Step 2 — Verifica il backend URL di produzione

Controlla che `frontend/.env.production` contenga l'URL del backend deployato:

```
REACT_APP_BACKEND_URL=https://app-release-config.emergent.host
```

> Questo valore viene "cotto" dentro il bundle JavaScript al momento del build.
> Se cambi backend in futuro devi rifare il build.

---

## 🚀 Step 3 — Build produzione del React

Dalla cartella `frontend/`:

```bash
yarn build
```

Genera la cartella `build/` che Capacitor userà come sorgente.

---

## 🚀 Step 4 — Aggiungi la piattaforma Android

**Solo la prima volta** (crea la cartella `android/` con il progetto nativo):

```bash
npx cap add android
```

> Suggerimento: aggiungi `frontend/android/` al `.gitignore` se non vuoi committare tutto il progetto Android, oppure committalo se preferisci tenere sotto controllo la config nativa.

Per ogni build successiva, sincronizza le modifiche del web nel progetto Android:

```bash
yarn build
npx cap sync android
```

---

## 🚀 Step 5 — Personalizza icona e splash

Nel progetto React hai già una palette teal `#0F766E`. Per generare **tutte le dimensioni Android** in una volta:

```bash
# Prepara una singola icona 1024×1024 PNG
# Salvala in: frontend/resources/icon.png
# Prepara uno splash 2732×2732 PNG con logo centrato
# Salvalo in: frontend/resources/splash.png

# Installa il generatore
npm install -g @capacitor/assets

# Genera icone e splash per Android in automatico
npx capacitor-assets generate --android
```

Questo popola `android/app/src/main/res/` con **tutte le densità** (mdpi, hdpi, xhdpi, xxhdpi, xxxhdpi) e l'icona adattiva.

---

## 🚀 Step 6 — Apri il progetto in Android Studio

```bash
npx cap open android
```

Al primo avvio Gradle scarica ~1 GB di dipendenze — **è normale**, aspetta.

### Configurazioni obbligatorie da fare in Android Studio

Apri `android/app/build.gradle` e verifica:

```gradle
android {
    namespace "com.tuazienda.caregiversync"
    defaultConfig {
        applicationId "com.tuazienda.caregiversync"   // stesso di capacitor.config.ts
        minSdkVersion 22
        targetSdkVersion 34
        versionCode 1                                  // incrementa a ogni release
        versionName "1.0.0"                            // versione visibile all'utente
    }
}
```

---

## 🚀 Step 7 — Genera la keystore di firma (una tantum)

Google Play richiede che ogni release sia firmata. Genera la tua chiave:

```bash
keytool -genkey -v \
  -keystore ~/caregiver-sync-release.jks \
  -alias caregiver-sync \
  -keyalg RSA -keysize 2048 -validity 10000
```

Ti chiederà una password → **conservala in un password manager**. Se la perdi non potrai più aggiornare l'app.

Poi crea `android/keystore.properties` (NON committarlo!):

```properties
storePassword=LA_TUA_PASSWORD
keyPassword=LA_TUA_PASSWORD
keyAlias=caregiver-sync
storeFile=/percorso/assoluto/caregiver-sync-release.jks
```

E aggiungi in `android/app/build.gradle`, in cima al blocco `android { }`:

```gradle
def keystorePropertiesFile = rootProject.file("keystore.properties")
def keystoreProperties = new Properties()
keystoreProperties.load(new FileInputStream(keystorePropertiesFile))

android {
    signingConfigs {
        release {
            keyAlias keystoreProperties['keyAlias']
            keyPassword keystoreProperties['keyPassword']
            storeFile file(keystoreProperties['storeFile'])
            storePassword keystoreProperties['storePassword']
        }
    }
    buildTypes {
        release {
            signingConfig signingConfigs.release
            minifyEnabled true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
}
```

Aggiungi al `.gitignore` (dentro `android/`):
```
keystore.properties
*.jks
```

---

## 🎯 Step 8 — Genera il file per Google Play

Google Play accetta solo **Android App Bundle (.aab)**, non più APK.

### Da Android Studio (metodo grafico)
1. Menu **Build** → **Generate Signed Bundle / APK…**
2. Scegli **Android App Bundle**
3. Seleziona la keystore creata al passo 7
4. Build variant: **release**
5. Clicca **Finish** → attendi ~2 minuti
6. Il file lo trovi in: `android/app/release/app-release.aab`

### Da riga di comando (metodo veloce, per CI/CD)
```bash
cd android
./gradlew bundleRelease
```
File generato in: `android/app/build/outputs/bundle/release/app-release.aab`

### Se vuoi anche un APK di test da installare direttamente
```bash
cd android
./gradlew assembleRelease
# → android/app/build/outputs/apk/release/app-release.apk
```

Trasferisci l'APK sul telefono e installalo per fare un test finale prima di caricare l'AAB sul Play Store.

---

## 📤 Step 9 — Carica su Google Play Console

1. Vai su https://play.google.com/console → paga **25 USD una tantum**
2. **Crea app** → nome "Caregiver Sync", lingua "Italiano", gratuita
3. Compila le sezioni obbligatorie:
   - **Scheda del Play Store**: descrizione, 2+ screenshot (usa il tuo simulatore Android o `adb screencap`), feature graphic 1024×500, icona 512×512
   - **Classificazione contenuti** (compila il questionario)
   - **Pubblico e contenuti** → seleziona 18+ (dati sanitari)
   - **Sicurezza dei dati** → dichiara: raccolta dati sanitari, cancellazione disponibile in-app ✅ (già implementata!), no condivisione con terzi
   - **Norme sulla privacy** → serve un URL pubblico (puoi ospitare un semplice `.md` su GitHub Pages)
4. Vai su **Produzione** → **Crea nuova release**
5. Carica `app-release.aab` → **Rivedi release** → **Avvia rollout**

Prima revisione: 2-7 giorni.

---

## 🔁 Step 10 — Ciclo di aggiornamento

Per rilasciare un update:

```bash
# 1) Modifica il codice React
# 2) Incrementa versionCode e versionName in android/app/build.gradle
#    versionCode 2
#    versionName "1.0.1"

# 3) Rebuild + sync
yarn build && npx cap sync android

# 4) Genera nuovo bundle
cd android && ./gradlew bundleRelease

# 5) Carica su Play Console → Produzione → nuova release
```

---

## ⚠️ Note importanti per l'app "Caregiver Sync"

### Backend deve restare online
Il file APK contiene solo il frontend. Tutte le chiamate a `/api/...` vanno al server di produzione. **Se il backend va offline, l'app non funziona.**
- Assicurati che il deployment Emergent resti attivo
- Considera un piano di backup per il DB MongoDB

### Contenuti sanitari — attenzione alle policy
Google Play ha regole specifiche per app medicali. **Non dichiarare mai "diagnosi" o "cura"** — resta su "supporto organizzativo alla cura". Il PDF del tuo progetto già suggerisce questo posizionamento (coordination/logistics vs medical device).

### Cancellazione dati richiesta da Google (già implementata!)
Google Play richiede che le app che raccolgono dati offrano:
- ✅ **Cancellazione dati in-app** → il tuo pulsante "Reset totale" in Impostazioni copre esattamente questo requisito
- ✅ **Cancellazione account** → attualmente non hai account, ma se aggiungerai auth dovrai implementare anche questo

Nella **Sicurezza dei dati** della Play Console dichiara esplicitamente: *"Gli utenti possono richiedere la cancellazione dei loro dati direttamente dall'app in Impostazioni → Gestione dati → Reset totale."*

---

## 🆘 Errori comuni

| Errore | Soluzione |
|---|---|
| `SDK location not found` | Crea `android/local.properties` con `sdk.dir=/path/to/Android/Sdk` |
| `Gradle build failed` — memoria | Aumenta a 4GB: modifica `android/gradle.properties` → `org.gradle.jvmargs=-Xmx4096m` |
| `Package name already used` | Cambia `appId` in `capacitor.config.ts` E `applicationId` in `build.gradle`, poi `npx cap sync` |
| App si apre ma **schermo bianco** | Il webview non raggiunge il backend. Controlla `.env.production` e rifai `yarn build && npx cap sync android` |
| App **cache vecchia** dopo update | Su Android Studio: Build → Clean Project + Rebuild |

---

## 📌 Cheat sheet — comandi ricorrenti

```bash
# Nuova build → sync → apri in Android Studio
yarn build && npx cap sync android && npx cap open android

# Build AAB in un colpo (con Android Studio già aperto una volta)
yarn build && npx cap sync android && cd android && ./gradlew bundleRelease

# Test rapido su un device Android connesso via USB
yarn build && npx cap sync android && npx cap run android
```

---

**Fatto!** In circa 30 minuti hai il tuo `.aab` pronto per il Play Store.

Se preferisci un approccio 100% cloud (senza installare Android Studio localmente) posso guidarti anche verso **PWABuilder** o **EAS Build con bare workflow** — ma per un'app React web esistente, Capacitor + Android Studio locale è la strada più affidabile e veloce.
