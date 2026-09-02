# 🍎 Guida iOS — Da progetto Capacitor a App Store

**Situazione**: ho preparato il progetto iOS completo (`ios-project.zip` da 1.7 MB) ma **la compilazione finale RICHIEDE un Mac**. È una regola di Apple, non un mio limite. Ecco tutte le strade possibili.

---

## 🎯 Cosa contiene il file `ios-project.zip`

Un progetto Xcode già configurato con:
- ✅ Bundle ID: `com.caregiversync.assistiti`
- ✅ Version: 1.2.0 (build 5)
- ✅ Nome app: `Caregiver Sync`
- ✅ Tutte le icone iOS (13 dimensioni da 20×20 a 1024×1024)
- ✅ Plugin RevenueCat integrato per acquisti in-app
- ✅ Codice React web già impacchettato

**Manca solo**: la compilazione con Xcode su Mac, l'account Apple Developer, e il caricamento su App Store Connect.

---

## 💰 Costi iOS

- **Apple Developer Program**: 99 € l'anno (versus 25 € una tantum di Google)
- **Mac** (una delle opzioni sotto)
- Commissione App Store: 15% primi $1M/anno, poi 30%

## 🛣️ Le 3 strade per compilare iOS

### 🅰️ Opzione economica ma lenta — Mac in cloud

Servizi tipo **MacinCloud** o **MacStadium**:
- MacinCloud "Managed Server": ~30 $/mese, Mac accessibile via browser/RDP
- Puoi affittarlo solo per pochi mesi mentre pubblichi, poi disdici
- **Pro**: no acquisto, subito operativo
- **Contro**: interfaccia via internet lenta, comunque devi imparare le basi di Xcode

### 🅱️ Freelance una tantum — CONSIGLIATA per te

Un iOS developer freelance ti fa **tutto il lavoro** (Xcode + firma + upload App Store) per **~80-150€ una volta**. Cerca su:
- **Fiverr**: cerca "iOS Capacitor build App Store"
- **Malt** (italiani): sviluppatori mobile a giornata
- **Upwork**: freelance internazionali

Cosa fornirgli:
1. Il file `ios-project.zip`
2. Il tuo Apple ID + password (o meglio: aggiungilo come membro del tuo Apple Developer team con ruolo "Developer")
3. Screenshot, testi, privacy policy (già li hai dal kit Android)

Il freelance ti restituisce **l'app pubblicata su App Store** in 3-7 giorni.

### 🅲️ Mac fisico — Se pensi di aggiornare spesso

**Mac mini M2** da 700€ nuovo o **Mac mini M1 usato** da 400€. Ne vale la pena se prevedi molti aggiornamenti dell'app.

---

## 📋 Step-by-step per chi userà il Mac (te o freelance)

### 1. Prerequisiti sul Mac
- macOS Sonoma o più recente
- **Xcode 15+** (gratis su Mac App Store, ~10 GB download)
- **CocoaPods**: `sudo gem install cocoapods` da Terminal

### 2. Estrai il progetto
- Scompatta `ios-project.zip` in una cartella
- Da Terminal: `cd cartella/ios/App && pod install`
- Aspetta 2-3 minuti che scarichi le dipendenze

### 3. Apri in Xcode
- **Doppio click su `App.xcworkspace`** (⚠️ NON su `App.xcodeproj`)
- Xcode apre il progetto

### 4. Configura la firma
- Selezione target **App** → tab **Signing & Capabilities**
- Team: seleziona il tuo Apple Developer account
- Bundle ID: già impostato (`com.caregiversync.assistiti`)
- Xcode genera automaticamente il **Provisioning Profile**

### 5. Aggiungi la chiave RevenueCat iOS
- Su https://app.revenuecat.com → progetto → aggiungi app iOS → copia la **Public iOS SDK Key** (formato `appl_XXXXX`)
- Nel Mac: apri `/ios/App/App/public/env.js` (o modifica `.env.production` e ricompila)
- Rebuild web: `yarn build && npx cap sync ios`

### 6. Configura i prodotti IAP su App Store Connect
- https://appstoreconnect.apple.com → crea l'app
- Bundle ID uguale al progetto
- Sezione **Abbonamenti** → crea gruppo `Caregiver Sync Pro`
- Prodotto 1 ID: `pro:monthly` — 4,99 € — Auto-renewable — 7 giorni trial
- Prodotto 2 ID: `pro:annual` — 39,99 € — Auto-renewable — 7 giorni trial

### 7. Compila e carica
- In Xcode: menu **Product → Archive**
- Attendi ~5 minuti
- Si apre l'Organizer → clicca **Distribute App → App Store Connect → Upload**
- Attendi email di conferma da Apple (~30 min)

### 8. Pubblica su App Store Connect
- Il build appare in **TestFlight** entro 30 min
- Compila la scheda (screenshot, descrizione — già hai tutto dal kit Android!)
- Submit for Review → attesa **1-3 giorni** revisione Apple

---

## 🔗 Materiale che il freelance ti chiederà

Hai già **tutto** nel kit Android — sono uguali per iOS:

| Cosa | File nel kit |
|---|---|
| Icona 1024×1024 | `store-graphics/icon-1024.png` |
| Screenshot | `screenshots/01-05*.png` (Apple accetta 1290×2796 per iPhone 6.7") |
| Descrizione breve/lunga | `MARKETING.md` |
| Privacy Policy URL | Pubblica `PRIVACY_POLICY.md` come pagina web (uguale ad Android) |
| Data Safety | `DATA_SAFETY.md` (Apple ha domande simili) |
| Bundle ID | `com.caregiversync.assistiti` |
| Progetto Xcode | `ios-project.zip` |

## ⚠️ Nota importante sugli screenshot

Play Store accetta 1080×1920. Apple invece vuole **1290×2796 (iPhone 15 Pro Max)**. Se ti dà problemi, dimmelo e ti rigenero le versioni iOS con le dimensioni giuste.

---

## 🆘 Se scegli il freelance

Testo pronto da incollare nella chat con lui:

```
Ciao, ho un'app Capacitor (React + iOS) già compilata per Android
e pubblicata su Google Play. Ho bisogno di:

1. Compilare il progetto iOS che ti allego (.zip)
2. Configurare firma con il mio Apple Developer account
   (te lo condivido come membro del team)
3. Configurare 2 prodotti IAP su App Store Connect
   (pro:monthly 4,99€, pro:annual 39,99€, 7gg trial)
4. Caricare su App Store e sottomettere per revisione

Bundle ID: com.caregiversync.assistiti
Ho pronti: icona 1024, screenshot, descrizione, privacy policy.
Preventivo? Tempo di consegna?
```

---

## 📥 Download

**Progetto iOS** (1.7 MB):
https://app-release-config.preview.emergentagent.com/api/download/ios-project.zip

**Questa guida**:
https://app-release-config.preview.emergentagent.com/api/download/IOS_BUILD_GUIDE.md

Buon rilascio anche su App Store! 🍎
