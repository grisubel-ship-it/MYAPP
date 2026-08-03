# 🔒 Modulo "Sicurezza dei Dati" — Google Play Console

Compila esattamente queste risposte nella sezione **App Content → Data safety** della Play Console. Sono conformi al comportamento reale di Caregiver Sync v1.0.0.

---

## 1) Data collection and security overview

### La tua app raccoglie o condivide dati utente richiesti dal Play Store?
**✅ Sì**

### Tutti i dati raccolti sono crittografati durante il transito?
**✅ Sì** — tutte le comunicazioni tra l'app e il backend avvengono via HTTPS (TLS 1.2/1.3).

### La tua app fornisce un modo agli utenti per chiedere la cancellazione dei loro dati?
**✅ Sì, in-app** — Impostazioni → Gestione dati:
- Svuota diario clinico
- Elimina tutti gli assistiti
- **Reset totale dell'app** (elimina TUTTI i dati dell'utente dal server)

Percorso in-app da citare: `Impostazioni → Zona pericolosa → Reset totale dell'app`

---

## 2) Elenco dettagliato dei dati raccolti

### 🩺 Dati sanitari e fitness — *Health and fitness*

#### Info sulla salute (Health info)
| Attributo | Valore |
|---|---|
| Raccolti? | ✅ Sì |
| Condivisi con terze parti? | ✅ Sì (solo con Anthropic per la funzione IA — vedi §4) |
| Obbligatori o opzionali? | Opzionali (l'utente sceglie cosa registrare) |
| Scopo dell'utilizzo | Funzionalità dell'app, Analisi non pubblicitaria |
| Crittografia in transito | ✅ Sì (HTTPS) |
| Cancellazione richiedibile dall'utente | ✅ Sì (in-app) |

Cosa raccolgli concretamente:
- Nome dell'assistito (inserito dal caregiver)
- Patologia principale (testo libero)
- Anno di nascita
- Note libere del profilo assistito
- Voci del diario clinico: parametri vitali (pressione, glicemia, temperatura, ecc.), farmaci somministrati con dose, sintomi osservati, note del turno

### 🚫 Dati personali NON raccolti
Confermare le seguenti sezioni come **"No, la mia app non raccoglie/condivide"**:
- Personal info (nome utente app, email, telefono, indirizzo, età, gender) — l'app v1.0.0 non ha autenticazione
- Financial info
- Location (approssimata o precisa)
- Web browsing history
- App activity (interazioni in-app)
- App info and performance
- Device or other IDs
- Contacts
- Photos and videos
- Audio files
- Files and docs
- Calendar
- Messages
- Personal identifiers (email, ID governativi, ecc.)

---

## 3) Pratiche di sicurezza

| Domanda Play Console | Risposta |
|---|---|
| I dati sono crittografati in transito? | ✅ Sì (HTTPS TLS 1.2+) |
| Segui le linee guida Play Families Policy? | ✅ Sì |
| L'utente può richiedere la cancellazione dei dati? | ✅ Sì, in-app |
| Hai una URL politica di cancellazione dati? | Sì (link al Privacy Policy) |

### URL cancellazione dati (Data deletion URL)
> Google richiede un URL pubblico che spieghi come richiedere la cancellazione. Nel Privacy Policy hai già una sezione dedicata — usa un anchor link:
>
> `https://TUO_DOMINIO/privacy#cancellazione`
>
> In alternativa puoi indicare che la cancellazione è disponibile solo in-app (opzione supportata da Google).

---

## 4) Condivisione con terze parti (dettaglio funzione IA)

Quando l'utente attiva la funzione **"Genera consegna con IA"**, il contenuto delle voci del diario delle ultime N ore viene inviato al modello linguistico **Claude Sonnet 4.6 di Anthropic PBC** (via Emergent LLM proxy) per generare il testo del passaggio consegne.

### Domanda: "Are these data shared with third parties?"
**✅ Sì** — condivisi con Anthropic PBC (Emergent proxy) esclusivamente per elaborazione della richiesta IA.

### Dettagli da inserire:
| Campo | Valore |
|---|---|
| Fornitore | Anthropic (via Emergent) |
| Tipo di dati condivisi | Voci diario clinico (Health info) |
| Scopo | Funzionalità dell'app (generazione handover) |
| Obbligatorio? | ❌ No (l'utente sceglie se usare la funzione) |
| Anthropic conserva i dati? | Secondo la privacy policy di Anthropic, gli input API non vengono usati per addestramento del modello e sono conservati max 30 giorni per abuse monitoring, poi eliminati |
| Riferimento | https://www.anthropic.com/legal/privacy |

---

## 5) Verifica sicurezza dati Google (Data safety declaration)

Copia-incolla nel campo di testo "Additional details" della sezione Data safety:

```
Caregiver Sync raccoglie i dati inseriti dall'utente relativi all'assistito
(nome, patologia, anno di nascita, note del profilo) e le voci del diario
clinico (parametri vitali, farmaci, sintomi, note). Tutti i dati sono
trasmessi via HTTPS e archiviati in un database MongoDB gestito dallo
sviluppatore.

Su richiesta esplicita dell'utente, il contenuto delle ultime N ore del
diario viene inviato al modello linguistico Claude di Anthropic (via
proxy Emergent) per generare una nota di passaggio consegne. Anthropic
non utilizza questi dati per addestrare il proprio modello.

L'utente può cancellare in qualsiasi momento singole voci, intere
collezioni, o effettuare un reset totale dei propri dati dal menu
Impostazioni. La cancellazione dal server è definitiva e immediata.

Nessun dato viene condiviso con inserzionisti pubblicitari. Nessun
tracking analytics di terze parti è attivo nell'app.
```

---

## 6) Checklist finale prima di inviare

- [ ] Nella pagina Data safety hai **NON** dichiarato "Personal info" (l'app non raccoglie nome utente / email)
- [ ] Hai **dichiarato** "Health info" con crittografia in transito ✅
- [ ] Hai **dichiarato** la condivisione con Anthropic per la funzione IA
- [ ] Hai indicato che la cancellazione è disponibile in-app
- [ ] Hai inserito l'URL della Privacy Policy pubblicamente accessibile
- [ ] La descrizione lunga (Marketing) menziona chiaramente l'uso dell'IA per la generazione consegne

Salva → Anteprima → Invia per la revisione.
