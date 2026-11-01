# Pubblicare Caregiver Senior su App Store con Codemagic (senza Mac)

Tempo totale: circa 1 ora di lavoro tuo + 20 minuti di compilazione + revisione Apple (1-3 giorni).
Il file `codemagic.yaml` è già pronto nel progetto: non devi modificarlo.

---

## 1. Attendi la conferma Apple
Arriva un'email "Welcome to the Apple Developer Program" (24-48 ore dopo il pagamento).
Finché non arriva, i passi successivi non funzionano.

## 2. Registra l'identificativo dell'app (5 min)
1. Vai su https://developer.apple.com/account/resources/identifiers
2. Premi **+** → **App IDs** → **App** → Continua
3. Descrizione: `Caregiver Senior` · Bundle ID **Explicit**: `com.caregiversync.app`
4. Lascia le capacità predefinite (In-App Purchase è già incluso) → **Register**

## 3. Crea l'app in App Store Connect (5 min)
1. https://appstoreconnect.apple.com → **App** → **+** → **Nuova app**
2. Piattaforma **iOS** · Nome **Caregiver Senior** · Lingua **Italiano**
3. Bundle ID: `com.caregiversync.app` · SKU: `caregiversenior` · Accesso completo
4. Apri l'app appena creata → **Informazioni app** → copia l'**Apple ID** (un numero di 10 cifre, es. `6741234567`). Ti serve al punto 7.

## 4. Crea la chiave API per Codemagic (5 min)
1. App Store Connect → **Utenti e accesso** → **Integrazioni** → **App Store Connect API**
2. Premi **+** (Genera chiave API) · Nome `Codemagic` · Accesso **App Manager** → Genera
3. Annota **Issuer ID** (in alto) e **ID chiave**
4. **Scarica la chiave** (file `.p8`) — si può scaricare UNA sola volta, conservala

## 5. Salva il progetto su GitHub
1. Qui in chat premi **Save to GitHub**
2. ⚠️ Scegli un repository **PRIVATO** (contiene la chiave di firma Android)

## 6. Collega Codemagic (10 min)
1. Vai su https://codemagic.io → **Sign up with GitHub** (piano gratuito: 500 minuti/mese)
2. **Add application** → GitHub → scegli il repository → tipo progetto **Ionic Capacitor App** / "codemagic.yaml"
3. In alto a destra → **Team settings** → **Team integrations** → **Developer Portal** → **Connect**
   - Nome della chiave: **`Caregiver Senior ASC`** (esattamente così)
   - Issuer ID, Key ID e file `.p8` del punto 4 → Save

## 7. Firma dell'app (10 min)
1. Codemagic → **Team settings** → **codemagic.yaml settings** → **Code signing identities**
2. Scheda **iOS certificates** → **Generate certificate** → tipo **Apple Distribution**, chiave `Caregiver Senior ASC` → dai un nome (es. `distribution`) → Create
3. Vai su https://developer.apple.com/account/resources/profiles → **+** → **App Store Connect** → App ID `com.caregiversync.app` → seleziona il certificato appena creato → nome `Caregiver Senior AppStore` → Generate
4. Torna su Codemagic → scheda **iOS provisioning profiles** → **Fetch profiles** → seleziona `Caregiver Senior AppStore` → Download selected

## 8. Variabili (2 min)
Codemagic → la tua app → **Environment variables** → crea il gruppo **`caregiver_senior`** con:
| Nome | Valore | Secret |
|---|---|---|
| `APP_STORE_APPLE_ID` | il numero del punto 3 | no |
| `REACT_APP_RC_IOS_KEY` | chiave pubblica RevenueCat iOS (`appl_...`) — facoltativa, vedi nota | sì |

> Senza `REACT_APP_RC_IOS_KEY` l'app funziona (prova 30 giorni e codici convenzione) ma i pulsanti "Abbonati" su iPhone restano disattivati. Puoi aggiungerla dopo e ricompilare.

## 9. Avvia la compilazione
1. Codemagic → la tua app → **Start new build**
2. Branch `main` · Workflow **Caregiver Senior iOS - App Store** → Start
3. Dopo ~20 minuti la build compare in App Store Connect → **TestFlight** (Apple la elabora per 10-30 minuti)

Se la build fallisce: scarica il log dalla pagina della build e mandamelo.

## 10. Invia in revisione
1. App Store Connect → l'app → **Distribuzione** → versione 1.6.0
2. Compila i testi con `APP_STORE_LISTING.md` (nome, sottotitolo "Anziani & Cronici", descrizione, parole chiave, privacy)
3. Carica gli screenshot della cartella `screenshots-ios`
4. Crea i 2 abbonamenti (`premium_monthly` 4,99 €, `premium_yearly` 49,90 €)
5. Sezione **Build** → scegli la build arrivata da Codemagic
6. **Note per la revisione**: inserisci un codice convenzione di test (crealo in `/admin`, es. `APPLEREVIEW`)
7. **Aggiungi per la revisione** → **Invia**

Quando Apple approva, mandami il link dell'App Store: lo inserisco nella pagina di download dei QR.
