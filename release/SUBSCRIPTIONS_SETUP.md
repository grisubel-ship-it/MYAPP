# 💳 Setup Abbonamenti Pro — Google Play + RevenueCat

Guida operativa per attivare gli acquisti in-app della v1.2.0. Il **codice è già pronto e integrato** nell'AAB. Servono solo le configurazioni sui portali esterni.

**Tempo stimato**: 60-90 minuti attivi, poi 24h di sync tra Play Console e RevenueCat.

---

## 📋 Precondizioni

- ✅ Account Google Play Console attivo (pagati i 25 USD, identità verificata)
- ✅ App **`com.caregiversync.assistiti`** già creata su Play Console
- ✅ Almeno **una release caricata** in un track (interno, chiuso o produzione)
- ⏳ **Da creare**: account gratuito su https://app.revenuecat.com

---

## STEP 1 — Configura i prodotti su Google Play Console

**Play Console → Monetizza con Play → Prodotti → Abbonamenti**

### 1.1 Crea il prodotto abbonamento

- Clicca **Crea abbonamento**
- **ID prodotto**: `pro` (⚠️ deve essere esattamente questo — è quello che il codice si aspetta)
- **Nome**: `Caregiver Senior Pro`
- **Descrizione**: `Consegne IA illimitate, assistiti illimitati, grafici andamento completi. Prova gratuita di 7 giorni.`
- Vantaggi (bullet):
  - Consegne con IA illimitate
  - Assistiti illimitati
  - Grafici andamento completi
  - Supporto prioritario
- **Salva**

### 1.2 Crea i due piani base

Sotto il prodotto `pro`, clicca **Aggiungi piano base**:

**Piano mensile**
- **ID piano**: `monthly`
- Tipo di rinnovo: **Rinnovo automatico**
- Periodo di fatturazione: **1 mese**
- Prezzo: **4,99 EUR** per l'Italia (Play calcola automaticamente le altre valute)
- Paesi/regioni: Italia + eventuali altri
- **Attiva** il piano

**Piano annuale**
- **ID piano**: `annual`
- Rinnovo automatico
- Periodo: **1 anno**
- Prezzo: **39,99 EUR**
- Paesi: uguali al mensile
- **Attiva**

### 1.3 Aggiungi il periodo di prova (offerta)

Per **entrambi** i piani base, clicca **Aggiungi offerta**:

- **ID offerta**: `trial7d`
- Idoneità: **Acquisizione di nuovi clienti** (solo primo utente)
- Fase di prezzo: **Prova gratuita**, durata **7 giorni**
- Dopo la prova → prezzo del piano base
- **Attiva** l'offerta

### 1.4 Pubblica la configurazione

⚠️ Requisito Play Console: per acquistare in test, la configurazione dei prodotti deve essere **pubblicata nel track di test** (interno o chiuso). Fai una release nel track "Interno" con l'AAB v1.2.0 che include i prodotti.

---

## STEP 2 — Configura RevenueCat

### 2.1 Crea account RevenueCat

- Vai su https://app.revenuecat.com/signup
- Registrati (gratuito fino a $10.000/mese di ricavi)
- Crea un nuovo **progetto**: `Caregiver Senior`

### 2.2 Aggiungi l'app Android

Dal progetto: **Project Settings → Apps → + New**
- Piattaforma: **Google Play Store**
- App Name: `Caregiver Senior Android`
- Package name: `com.caregiversync.assistiti`
- **Google Play Service Account** ⬅️ ci serve il JSON

### 2.3 Ottieni il Service Account JSON di Google Cloud

Percorso: **Play Console → Configurazione → Accesso API → Crea account di servizio**

1. Ti reindirizza su Google Cloud Console → crea nuovo service account:
   - Nome: `revenuecat-sync`
   - Ruolo: nessuno per ora (i permessi si danno lato Play Console)
2. Sul service account creato → **Chiavi → Aggiungi chiave → JSON** → scarica il file
3. Torna in **Play Console → Accesso API**, refresh
4. Concedi al service account **almeno**:
   - ✅ Visualizza informazioni finanziarie (visualizzazione)
   - ✅ Gestisci ordini e abbonamenti
   - ✅ Visualizza dati app

### 2.4 Carica il JSON in RevenueCat

- Torna nella pagina di RevenueCat → App Android
- Carica il JSON del service account
- **Salva** e attendi ~24 ore per il primo sync (Google impiega tempo la prima volta)

### 2.5 Ottieni la chiave pubblica RevenueCat Android

- **Project Settings → API Keys**
- Copia la **Public Android SDK Key** (formato: `goog_XXXXXXXXXXXXX`)

**⬅️ SERVE QUESTA CHIAVE PER LA PROSSIMA BUILD**

### 2.6 Configura i prodotti su RevenueCat

**Products → + New**:
1. Product 1:
   - Store: Google Play
   - Product ID: `pro:monthly` (formato SubscriptionID:BasePlanID)
   - Type: Auto-renewable subscription
2. Product 2:
   - Product ID: `pro:annual`

**Entitlements → + New**:
- ID: `pro_access` (⚠️ esattamente così — è nell'entitlement_ids del codice)
- Associa **entrambi** i prodotti sopra

**Offerings → default**:
- Package `$rc_monthly` → Product `pro:monthly`
- Package `$rc_annual` → Product `pro:annual`
- Marca come **Current offering**

---

## STEP 3 — Configura il webhook RevenueCat → tuo backend

**Integrations → + New → Custom Webhook**

- **URL**: `https://app-release-config.emergent.host/api/webhooks/revenuecat`
- **Authorization header**: `Bearer TUO_SEGRETO_LUNGO_QUI` (genera un token random es. `openssl rand -hex 32`)
- **Method**: POST
- Copia il segreto → sarà il valore di `RC_WEBHOOK_SECRET` sul backend

### 3.1 Configura il segreto sul backend Emergent

Vai su Emergent Dashboard → tuo progetto → Environment Variables → **Aggiungi**:
```
RC_WEBHOOK_SECRET=TUO_SEGRETO_LUNGO_QUI
```
Poi **redeploy** produzione così il backend legge la nuova variabile.

**Verifica webhook**: da RevenueCat clicca **Send test event**. Sul tuo backend cerca nei log:
```
{"status": "processed"}
```

---

## STEP 4 — Ricompila l'APK/AAB con la chiave RevenueCat

**Aggiungi in `frontend/.env.production`**:
```
REACT_APP_RC_ANDROID_KEY=goog_LA_TUA_CHIAVE_DA_STEP_2.5
```

Poi:
```bash
cd /app/frontend
yarn build
cd android
./gradlew bundleRelease assembleRelease
```

Il nuovo AAB v1.2.1 (bump versionCode a 6 e versionName a 1.2.1) è pronto per essere ricaricato su Play Console.

---

## STEP 5 — Test dell'acquisto (importantissimo)

### 5.1 Configura account tester in Play Console

**Play Console → Setup → License testing** → aggiungi il tuo account Google (quello del telefono con cui testerai).

### 5.2 Track "Interno" con l'AAB v1.2.1

- **Test → Test interno → Crea traccia**
- Aggiungi il tuo account tester
- Carica `caregiver-sync-v1.2.1.aab`
- Ottieni il link opt-in della Play Store per il tuo tester

### 5.3 Installa dall'opt-in link

Sul telefono → clicca link → installa app dal Play Store (**non** l'APK sideloaded, altrimenti Play Billing non funziona!).

### 5.4 Effettua l'acquisto

- Apri l'app → tocca il badge **Pro** in header
- Vedrai i due pacchetti con prezzo (mensile 4,99€ / annuale 39,99€)
- Tocca **Prova gratis** → dialog Play → conferma
- Attendi ~10 secondi
- Il webhook aggiorna il backend → l'app mostra "Sei un utente Pro"
- Genera più di 3 handover IA per verificare che il limite sia rimosso

### 5.5 Test scenari

- **Cancellazione**: Play Store → Abbonamenti → Caregiver Senior → Annulla — accesso mantenuto fino a scadenza
- **Restore**: reinstalla l'app → Pro → **Ripristina acquisti** → torna Pro
- **Scadenza forzata**: Play Console → **Play Billing Lab** per simulare scadenza in 3-5 minuti invece che 30 giorni

---

## 🚨 Cose critiche da ricordare

| ⚠️ | Cosa |
|---|---|
| L'entitlement ID **deve** essere `pro_access` | Cambiato = codice non riconosce Pro |
| Il product ID **deve** essere `pro` (non `Pro` o `PRO`) | Case-sensitive |
| **Il primo sync Play↔RevenueCat richiede fino a 24h** | Non testare subito, aspetta |
| L'app **deve** essere installata dal Play Store (opt-in link) | APK sideloaded non ha Play Billing attivo |
| L'utente tester **deve** essere in "License testing" | Altrimenti gli viene addebitato davvero |
| **Non usare l'account Play Console per test** | Google blocca acquisti sull'account editore |

---

## 📊 Cosa succede in produzione

1. Utente apre app → registra assistiti (Free tier)
2. Genera 3 consegne IA nel mese → alla 4a riceve errore 402 + toast "Passa a Pro"
3. Va su `/pro`, vede i pacchetti dinamici da RevenueCat, sceglie
4. Play Billing gestisce il pagamento con carta Visa/Mastercard/Google Pay salvate sul suo account Google
5. RevenueCat invia webhook al backend → `db.subscriptions.pro_active = true`
6. L'app polling ogni 3s dopo l'acquisto vede l'aggiornamento → sblocca UI Pro
7. Rinnovo automatico ogni mese/anno gestito da Google Play, webhook aggiorna il backend
8. Se l'utente annulla, Play Store lo notifica, il webhook `CANCELLATION` mantiene l'accesso fino a `expires_at`, poi il webhook `EXPIRATION` disattiva

---

## 💰 Costi

- **RevenueCat**: gratuito fino a $10.000/mese di ricavi tracciati (poi 1%). Puoi cambiare piano quando vuoi.
- **Google Play Billing**: 15% sul primo €1M annuo, poi 30%. Per subscription auto-renewing dopo il 1° anno la fee scende al 15%.
- **Anthropic API** (le consegne IA Pro consumate): dipende dal volume. Ogni consegna ~$0.02. Con 100 utenti Pro che generano 30 consegne/mese = ~$60/mese di API cost — assorbito dai 4,99€/mese abbonamento.

---

## 🆘 Problemi comuni

| Sintomo | Causa | Soluzione |
|---|---|---|
| Paywall dice "Offerte non disponibili" | Prodotti Play non pubblicati o non sync | Attendi 24h, verifica track "Interno" pubblicato |
| Errore 400 al tap "Prova gratis" | Package name non corrisponde | Verifica `com.caregiversync.assistiti` in RC dashboard |
| Webhook 401 unauthorized | RC_WEBHOOK_SECRET non impostato | Aggiungi env var sul backend + redeploy |
| Pro non si attiva dopo acquisto | Webhook non arriva o entitlement_id sbagliato | Verifica `pro_access` in RC + URL webhook |
| Test purchase addebita realmente | Account tester non in License testing | Aggiungi in Play Console → Setup → License testing |

Buon rilascio! 💚
