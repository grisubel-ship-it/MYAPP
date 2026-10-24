# Privacy Policy — Caregiver Senior

**Ultimo aggiornamento**: 3 agosto 2026
**App**: Caregiver Senior v1.0.0
**Titolare del trattamento**: Caregiver Senior (Italia) — email: `supporto@caregiversync.example`

> ⚠️ **Prima di pubblicare**: sostituisci i placeholder tra `[…]` con i tuoi dati reali (ragione sociale, indirizzo, email, PEC).

---

## 1. Introduzione

Caregiver Senior è un'applicazione mobile pensata per aiutare i familiari, le badanti, gli OSS e gli infermieri domiciliari a coordinare la cura di persone anziane o affette da patologie croniche. La presente Privacy Policy descrive **quali dati raccogliamo, come li utilizziamo, con chi li condividiamo e quali diritti hai**, in conformità al **Regolamento UE 2016/679 (GDPR)** e al **D. Lgs. 196/2003** italiano.

Utilizzando l'app dichiari di aver letto e compreso questa informativa.

---

## 2. Titolare del trattamento

- **Ragione sociale**: [inserire il tuo nome o azienda]
- **Indirizzo**: [inserire indirizzo completo]
- **Email di contatto**: `supporto@caregiversync.example`
- **PEC** (se applicabile): `[inserire PEC]`

Non abbiamo l'obbligo di nominare un DPO (Data Protection Officer) ai sensi dell'art. 37 GDPR, ma puoi contattarci per qualsiasi richiesta sulla privacy all'indirizzo email indicato sopra.

---

## 3. Dati personali che raccogliamo

Caregiver Senior raccoglie **esclusivamente i dati che tu, come caregiver, inserisci volontariamente nell'app** relativi all'assistito che stai seguendo. L'app **non richiede la creazione di un account, non raccoglie email, non traccia la tua posizione, non accede ai contatti né alla galleria**.

### 3.1 Dati inseriti dall'utente

| Categoria | Dati raccolti | Base giuridica |
|---|---|---|
| **Profilo assistito** | Nome, patologia principale (opzionale), anno di nascita (opzionale), note libere | Consenso esplicito (art. 6.1.a + art. 9.2.a GDPR) |
| **Diario clinico** | Voci di tipo *parametro vitale, farmaco, sintomo, nota*, ognuna con etichetta, valore, unità di misura, data/ora | Consenso esplicito (art. 9.2.a GDPR) |

I dati relativi alla salute sono classificati come **"categorie particolari di dati personali"** (art. 9 GDPR). Il trattamento è lecito solo perché tu, come caregiver o come persona autorizzata dall'assistito, hai fornito consenso esplicito inserendo tali informazioni nell'app.

### 3.2 Dati NON raccolti

Caregiver Senior **NON raccoglie**:
- ❌ Il tuo nome, email, numero di telefono o indirizzo
- ❌ La tua posizione geografica (né precisa né approssimata)
- ❌ Identificatori pubblicitari (IDFA, AAID)
- ❌ Cronologia di navigazione web
- ❌ Contenuti di rubrica, galleria, calendario, SMS
- ❌ Dati biometrici
- ❌ Dati finanziari o di pagamento

### 3.3 Dati tecnici del dispositivo

L'app comunica con il nostro server via HTTPS e nei log tecnici del server sono temporaneamente registrati:
- Indirizzo IP dell'utente (conservato **max 30 giorni** per finalità di sicurezza)
- Tipo di richiesta API (senza contenuto)
- Codici di stato di risposta

Questi dati non sono associati a un profilo utente e sono usati esclusivamente per sicurezza operativa (rilevamento abusi, debug tecnico) come consentito dall'art. 6.1.f GDPR (legittimo interesse).

---

## 4. Come vengono utilizzati i dati

I dati che inserisci nell'app vengono utilizzati esclusivamente per:

1. **Fornire il servizio** di diario clinico condiviso: registrare, visualizzare, modificare ed eliminare le voci del diario e i profili degli assistiti.
2. **Generare la nota di passaggio consegne con IA** (solo se attivi esplicitamente la funzione — vedi §5).
3. **Statistiche di gestione dati** (contatori mostrati in Impostazioni), calcolate localmente sul server dell'app.

**Non utilizziamo mai i tuoi dati per**:
- ❌ Pubblicità o profilazione commerciale
- ❌ Vendita a terze parti
- ❌ Ricerca clinica senza il tuo consenso separato
- ❌ Addestramento di modelli di intelligenza artificiale (vedi §5)

---

## 5. Elaborazione dei dati tramite Intelligenza Artificiale

### 5.1 Come funziona la generazione dei consegne con IA

Quando premi **"Genera consegna con IA"** nella schermata di dettaglio di un assistito, l'app:

1. Recupera le voci del diario delle **ultime 8, 12, 24 o 72 ore** (secondo la tua scelta) del solo assistito visualizzato.
2. Invia queste voci al modello linguistico **Claude Sonnet 4.6 di Anthropic PBC** attraverso il proxy tecnico gestito da **Emergent** (`https://integrations.emergentagent.com`).
3. Il modello produce un testo strutturato in italiano di massimo 300 parole che riassume il turno.
4. Il testo viene mostrato all'interno dell'app e puoi copiarlo negli appunti.

### 5.2 Cosa viene inviato ad Anthropic

- Nome dell'assistito, patologia dichiarata, anno di nascita
- Elenco delle voci del diario del periodo scelto (etichetta, valore, unità, orario)
- Un prompt di sistema che istruisce il modello a **non fornire consigli medici o diagnosi**

### 5.3 Garanzie sull'utilizzo dei dati da parte di Anthropic

Secondo la [Privacy Policy di Anthropic](https://www.anthropic.com/legal/privacy) e i termini API commerciali:

- ✅ **I dati inviati all'API di Anthropic non sono utilizzati per addestrare i loro modelli** (a differenza dell'uso via web chat di Claude).
- ✅ I dati sono conservati **massimo 30 giorni** per fini di "abuse monitoring", poi cancellati automaticamente.
- ✅ I dati sono elaborati esclusivamente per generare la risposta richiesta.
- ✅ Anthropic è certificata GDPR con Standard Contractual Clauses per il trasferimento dati extra-UE (USA).

### 5.4 La funzione IA è facoltativa

Puoi utilizzare tutte le altre funzioni dell'app **senza mai attivare la funzione IA**. In tal caso, nessun dato del diario verrà mai inviato a un fornitore di modelli linguistici.

### 5.5 Limiti della funzione IA

L'IA di Caregiver Senior **non è un dispositivo medico**, non fornisce diagnosi, non prescrive terapie, non sostituisce il parere del medico. È esclusivamente uno strumento di supporto alla comunicazione tra caregiver. Ogni decisione clinica deve essere presa in accordo con il medico curante dell'assistito.

---

## 6. Con chi condividiamo i dati

I dati inseriti nell'app **NON vengono condivisi con inserzionisti, broker di dati o partner commerciali**. I dati sono comunicati esclusivamente ai seguenti soggetti, ognuno responsabile del trattamento per la propria porzione:

| Soggetto | Ruolo | Dati trattati | Finalità |
|---|---|---|---|
| **Emergent** (piattaforma hosting) | Responsabile del trattamento (art. 28 GDPR) | Tutti i dati inseriti nell'app + log tecnici | Hosting del backend, database MongoDB, proxy API IA |
| **Anthropic PBC** | Sub-responsabile (solo se attivi la funzione IA) | Voci del diario del periodo scelto + profilo assistito | Generazione della nota di consegna |

I server di Emergent sono localizzati in [inserire regione — es. Unione Europea / USA]. Se sono negli USA, il trasferimento avviene sulla base delle **Standard Contractual Clauses** (SCC) approvate dalla Commissione Europea.

---

## 7. Come conserviamo i dati

- I dati sono archiviati in un **database MongoDB** gestito da Emergent, con crittografia at-rest a livello di disco.
- Le comunicazioni tra l'app e il server avvengono in HTTPS (TLS 1.2+) con Perfect Forward Secrecy.
- L'accesso al database è limitato al personale tecnico autorizzato e protetto da password/chiavi API.
- Non conserviamo backup permanenti dei tuoi dati oltre quanto necessario per fornire il servizio.

---

## 8. Per quanto tempo conserviamo i dati

- **Voci del diario e profili assistiti**: fino a quando **tu** decidi di cancellarli dall'app (vedi §10). Non applichiamo cancellazione automatica.
- **Log tecnici del server**: max 30 giorni, poi cancellati automaticamente.
- **Input alle API di Anthropic**: max 30 giorni presso Anthropic (per abuse monitoring), poi cancellati.
- **Output dell'IA**: se non lo copi o salvi, esiste solo nella schermata della sessione corrente e viene perso alla chiusura dell'app.

---

## 9. I tuoi diritti (GDPR)

In qualsiasi momento hai il diritto di:

| Diritto | Come esercitarlo |
|---|---|
| **Accesso** (art. 15 GDPR) | Vedere in-app tutti i dati raccolti; per richiesta formale scrivi a `supporto@caregiversync.example` |
| **Rettifica** (art. 16 GDPR) | Modifica direttamente le voci dall'app |
| **Cancellazione / diritto all'oblio** (art. 17 GDPR) | In-app: Impostazioni → Gestione dati → Reset totale. La cancellazione è **immediata e definitiva** |
| **Limitazione del trattamento** (art. 18 GDPR) | Scrivi a `supporto@caregiversync.example` |
| **Portabilità** (art. 20 GDPR) | Su richiesta forniamo un export JSON delle tue voci entro 30 giorni |
| **Opposizione** (art. 21 GDPR) | Puoi disinstallare l'app in ogni momento. Nessun dato viene poi elaborato ulteriormente |
| **Revoca del consenso** (art. 7 GDPR) | Cancella i dati dall'app; la revoca non pregiudica la liceità dei trattamenti precedenti |
| **Reclamo al Garante Privacy** | Puoi rivolgerti al [Garante per la Protezione dei Dati Personali](https://www.garanteprivacy.it) |

<a id="cancellazione"></a>
### 9.1 Come richiedere la cancellazione dei dati

**Modalità 1 — In-app (raccomandata, cancellazione immediata)**:
1. Apri Caregiver Senior
2. Tocca l'icona ingranaggio in alto a destra
3. Scorri fino alla sezione **"Zona pericolosa"**
4. Tocca **"Reset totale dell'app"**
5. Conferma → tutti i tuoi dati vengono eliminati dal server immediatamente

**Modalità 2 — Via email**:
Invia una richiesta a `supporto@caregiversync.example` indicando "Richiesta cancellazione dati Caregiver Senior". Rispondiamo entro 30 giorni ai sensi dell'art. 12 GDPR.

---

## 10. Sicurezza

Adottiamo misure tecniche e organizzative adeguate al rischio (art. 32 GDPR):
- Crittografia in transito (HTTPS TLS 1.2+)
- Autenticazione e autorizzazione degli accessi lato server
- Isolamento del database e principio del privilegio minimo
- Monitoraggio dei log di sicurezza
- Nessuna esposizione pubblica del database

Nonostante questi accorgimenti, nessun sistema è invulnerabile al 100%. In caso di violazione dei dati che possa comportare rischi per i tuoi diritti e libertà, ti notificheremo entro 72 ore ai sensi dell'art. 33 GDPR.

---

## 11. Minori

Caregiver Senior **NON è destinata a minori di 18 anni**. Se sei minorenne, non usare l'app. Se veniamo a conoscenza del fatto che un minorenne ha inserito dati, li cancelleremo tempestivamente. Segnala all'indirizzo `supporto@caregiversync.example`.

---

## 12. Cookie e tracciamento

L'app **non utilizza cookie** né tecnologie di tracciamento equivalenti. Non utilizziamo Google Analytics, Firebase Analytics, Facebook SDK, o strumenti simili.

---

## 13. Modifiche a questa Privacy Policy

Possiamo aggiornare questa Privacy Policy per riflettere modifiche legali, tecniche o funzionali. La versione aggiornata sarà pubblicata a questo indirizzo con la data di ultima modifica in cima. Ti invitiamo a rileggerla periodicamente. Nelle modifiche sostanziali, ti informeremo tramite notifica in-app.

---

## 14. Contatti

Per qualsiasi domanda o richiesta relativa alla privacy:

- 📧 Email: `supporto@caregiversync.example`
- 🌐 Sito web: `https://caregiversync.example`
- ✉️ Indirizzo postale: [inserire indirizzo completo]

---

## 15. Foro competente

Per qualsiasi controversia relativa al trattamento dei dati personali il foro competente è quello di [inserire città], salvo diverso obbligo di legge previsto per il consumatore ai sensi del D. Lgs. 206/2005.

---

**Grazie per usare Caregiver Senior in modo consapevole. La tua fiducia è il nostro impegno.** ❤️
