# Caregiver Sync — PRD

## Original Problem Statement
App per la gestione della cura di anziani e persone cronicamente malate ("Caregiver Sync per Anziani e Cronici"). L'utente ha inizialmente chiesto la preparazione alla pubblicazione su Google Play tramite EAS, poi ha richiesto di **aggiungere la cancellazione dei dati** all'app.

## Architecture
- **Backend**: FastAPI + Motor (MongoDB async). Router `/api` con endpoint CRUD per pazienti (`patients`) e voci di diario clinico (`entries` con kind = vital/medication/symptom/note) + endpoint di gestione dati (stats, clear collection, wipe).
- **Frontend**: React 19 + React Router + shadcn/ui + Tailwind + sonner (toast Undo) + AlertDialog (conferme distruttive).
- **DB**: due collezioni MongoDB — `patients`, `entries`.

## User Personas
1. **Familiare/caregiver principale** che coordina la cura dell'assistito
2. **Badante/OSS** che registra parametri e handover
3. **Medico di riferimento** (futuro) per lettura fascicolo

## Core Requirements
- Registrare assistiti (nome, patologia, anno di nascita, note)
- Diario clinico condiviso (parametri vitali, farmaci, sintomi, note)
- **Cancellazione dati completa** con pattern GDPR-compliant:
  - Delete singolo (paziente / entry) con conferma AlertDialog + Undo 5s (sonner toast)
  - Bulk delete per tipologia (tutti i parametri, tutti i farmaci, ...) di un paziente
  - Clear collezione (svuota tutto il diario / tutti gli assistiti)
  - Wipe totale (reset app, diritto all'oblio)
- Conferma distruttiva SEMPRE per dati sanitari

## Implemented (2026-01)
- ✅ Backend endpoints:
  - `POST/GET /api/patients`, `GET/DELETE /api/patients/{id}`, `POST /api/patients/restore`
  - `POST/GET /api/entries`, `DELETE /api/entries/{id}`, `POST /api/entries/restore`, `POST /api/entries/bulk-delete`
  - `GET /api/data/stats`, `DELETE /api/data/collection/{name}`, `DELETE /api/data/wipe`
- ✅ Frontend pages: Lista Assistiti, Nuovo Assistito, Dettaglio Assistito con diario, Impostazioni / Gestione dati
- ✅ Pattern Undo con sonner: delete restituisce l'oggetto → toast con "Annulla" → POST /restore
- ✅ Test end-to-end: 11 test pytest backend + Playwright frontend → **100% pass**
- ✅ Data-testid completi su ogni interazione (vedi report iteration_1.json)
- ✅ UI italiana, palette teal + fonts Fraunces/Nunito Sans

## Prioritized Backlog
### P0 — prima del prossimo release
- Nessuno bloccante

### P1 — prossimi step
- **Autenticazione multi-utente** (familiare, badante, medico) con permessi differenziati
- **Handover digitale** — checklist di passaggio consegne tra turni
- **Alert predittivi** — notifica farmaco in esaurimento / parametro fuori range
- **Export PDF fascicolo** — referti e ricette raggruppati per data/patologia

### P2 — nice to have
- Grafici trend parametri (recharts già in package.json)
- Upload foto referto/ricetta
- Notifiche push (per app mobile)
- Ricerca full-text sul diario
- Portare l'app in Expo/React Native e usare la guida EAS in `/app/eas-publish-guide/` per Google Play

## Known / Deferred
- No auth: qualunque utente può leggere tutti i dati (MVP a utente singolo)
- No pagination: `to_list(1000/10000)` — sufficiente fino a ~1000 assistiti
- `restore` accetta dict raw non validato via Pydantic (minor sec, non exploitabile senza auth)
