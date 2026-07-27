# Guida completa: pubblicazione app Expo su Google Play tramite EAS

Guida step-by-step per portare la tua app Expo/React Native in produzione su Google Play Store usando **EAS Build** ed **EAS Submit**.

---

## Prerequisiti

- Progetto Expo/React Native già inizializzato (`npx create-expo-app`).
- **Node.js 20+** e **npm/yarn** installati.
- Un account gratuito su **https://expo.dev**.
- Un account **Google Play Console** (una tantum: **25 USD**).
- Icona master **1024×1024 PNG** pronta.

---

## 1. Installa gli strumenti

```bash
# CLI di Expo/EAS in globale
npm install -g eas-cli

# Verifica versione (>= 12)
eas --version

# Login su Expo
eas login
```

---

## 2. Copia i file di configurazione

Nel root del tuo progetto Expo, copia:

- `app.json` → sostituisce quello esistente
- `eas.json` → nuovo file
- `assets/*.png` → cartella con icone e splash

### Personalizzazioni obbligatorie in `app.json`

Apri `app.json` e modifica:

| Chiave                         | Cosa metterci                                              |
|--------------------------------|------------------------------------------------------------|
| `expo.name`                    | Nome visualizzato (es. "Cronici")                          |
| `expo.slug`                    | Slug URL-safe (es. "cronici")                              |
| `expo.owner`                   | Il tuo username Expo (visibile su expo.dev)                |
| `expo.android.package`         | Package name unico (es. `com.tuazienda.cronici`)           |
| `expo.ios.bundleIdentifier`    | Uguale al package Android                                  |
| `expo.extra.eas.projectId`     | Verrà popolato al primo `eas build` (o `eas init`)         |
| `expo.updates.url`             | Verrà popolato automaticamente                             |

> ⚠️ **Il package name Android non è più modificabile una volta pubblicato su Google Play.** Sceglilo con cura.

---

## 3. Genera icone e splash screen

### Opzione A — Metodo veloce (raccomandato)

1. Prepara **un unico file 1024×1024 PNG** con il tuo logo su sfondo trasparente.
2. Vai su https://expo-assets-generator.vercel.app
3. Carica il PNG → scarica lo zip → estrai i file nella cartella `assets/` del progetto.

### Opzione B — Manuale (Figma)

Usa il template ufficiale Expo:
https://www.figma.com/community/file/1155362909441341285

Esporta come PNG:
- `icon.png` (1024×1024)
- `adaptive-icon.png` (1024×1024, logo nel 66% centrale)
- `splash.png` (1284×2778, logo centrato)
- `notification-icon.png` (96×96, solo bianco su alpha)
- `favicon.png` (48×48)

### Opzione C — ImageMagick da CLI

Vedi `assets/README_ASSETS.md` per gli snippet pronti.

---

## 4. Inizializza il progetto EAS

Dalla root del progetto:

```bash
eas init
```

Questo comando:
- Crea il progetto su expo.dev
- Popola automaticamente `expo.extra.eas.projectId` in `app.json`
- Popola `expo.updates.url`

---

## 5. Configura le credenziali Android

EAS può gestire automaticamente la **keystore** di firma:

```bash
eas credentials
```

Seleziona: `Android` → `production` → `Set up a new keystore` → `Generate new keystore`.

> ✅ Expo salva il keystore sui suoi server (cifrato). Puoi scaricarlo in qualsiasi momento con `eas credentials`. Se lo perdi, **non potrai più aggiornare l'app su Google Play**: fai anche un backup locale.

---

## 6. Build di produzione (AAB)

```bash
eas build --platform android --profile production
```

Cosa succede:
- EAS invia il codice ai server di build.
- Compila un **Android App Bundle (.aab)** — obbligatorio per Google Play dal 2021.
- Al termine (10-25 min) ti dà un link per scaricare il file.
- Il `versionCode` viene incrementato automaticamente (`autoIncrement: true` in `eas.json`).

### Controlla lo stato
```bash
eas build:list --platform android --limit 5
```

---

## 7. Prima pubblicazione manuale su Google Play

Alla **primissima pubblicazione** devi caricare l'AAB manualmente (Google richiede la creazione della scheda app dal browser):

1. Vai su https://play.google.com/console
2. **Crea app** → compila nome, lingua predefinita, gratuita/a pagamento.
3. Compila obbligatoriamente:
   - **Scheda del Play Store** (descrizione, screenshot minimo 2, feature graphic 1024×500, icona 512×512)
   - **Classificazione dei contenuti**
   - **Pubblico di destinazione**
   - **Sicurezza dei dati**
   - **Norme sulla privacy** (URL pubblico)
4. Vai in **Produzione** → **Crea nuova release** → carica l'`.aab` scaricato da EAS.
5. Invia per revisione (2-7 giorni la prima volta).

---

## 8. Aggiornamenti automatici futuri (EAS Submit)

Dopo la prima pubblicazione manuale, puoi automatizzare tutti gli aggiornamenti successivi.

### 8.1 Ottieni il service account JSON di Google

1. https://play.google.com/console → **Impostazioni** → **Accesso API**
2. Collega un progetto Google Cloud (o creane uno nuovo).
3. **Crea account di servizio** → assegna il ruolo **Amministratore delle release**.
4. Genera una chiave **JSON** → salvala come `google-service-account.json` nella root del progetto.
5. **Aggiungila a `.gitignore`** — è una chiave privata!

```bash
echo "google-service-account.json" >> .gitignore
```

### 8.2 Build + submit in un solo comando

```bash
eas build --platform android --profile production --auto-submit
```

Oppure separatamente:

```bash
eas build --platform android --profile production
eas submit --platform android --profile production --latest
```

Con `releaseStatus: "draft"` (già impostato in `eas.json`) la release viene caricata come bozza: la controlli manualmente sulla Play Console prima di promuoverla in produzione. Cambia in `"completed"` se vuoi rilascio automatico.

---

## 9. Comandi rapidi — Cheat sheet

```bash
# Setup una tantum
npm install -g eas-cli
eas login
eas init
eas credentials                                    # crea keystore Android

# Build di test interno (APK installabile diretto)
eas build --platform android --profile preview

# Build produzione (AAB per Google Play)
eas build --platform android --profile production

# Build + submit automatico
eas build --platform android --profile production --auto-submit

# Submit dell'ultima build già fatta
eas submit --platform android --profile production --latest

# Stato build
eas build:list --platform android --limit 5

# Aggiornamento OTA (senza ricompilare — solo JS/asset)
eas update --branch production --message "Fix bug X"
```

---

## 10. Incrementare la versione per un update

Prima di ogni nuova build di produzione, aggiorna in `app.json`:

```json
{
  "expo": {
    "version": "1.0.1"   // <-- incrementa questa (visibile all'utente)
  }
}
```

Il `versionCode` Android viene incrementato **in automatico** da EAS grazie a `autoIncrement: true` nel profilo `production` di `eas.json`.

---

## 11. Errori comuni

| Errore                                                | Soluzione                                                                 |
|-------------------------------------------------------|---------------------------------------------------------------------------|
| `Package name already in use`                         | Cambia `expo.android.package` in `app.json`                              |
| `versionCode must be greater than X`                  | `autoIncrement: true` in `eas.json` (già impostato)                       |
| `Icon is not square / must be 1024x1024`              | Rigenera `icon.png` esattamente 1024×1024 PNG                             |
| `App icon shown as white square in notification`      | `notification-icon.png` deve essere **solo bianco su trasparenza**        |
| `Adaptive icon appears cropped`                       | Metti il logo nel 66% centrale, aggiungi padding 170px                    |
| `Missing service account JSON`                        | Segui step 8.1 e metti il file nella root del progetto                    |
| `Your app is not compliant with Google Play policies` | Compila la sezione "Sicurezza dei dati" e "Classificazione contenuti"     |

---

## 12. Riferimenti ufficiali

- Documentazione EAS Build: https://docs.expo.dev/build/introduction/
- EAS Submit Android: https://docs.expo.dev/submit/android/
- Icone e splash: https://docs.expo.dev/develop/user-interface/splash-screen-and-app-icon/
- Google Play Console: https://play.google.com/console

---

**Fine guida.** Buona pubblicazione! 🚀
