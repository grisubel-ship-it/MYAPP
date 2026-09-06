# Caregiver Sync — PRD

## Original Problem Statement
App per la gestione della cura di anziani e persone cronicamente malate ("Caregiver Sync per Anziani e Cronici"). Deve supportare la coordinazione fra caregiver (familiari, badanti, OSS) con diario clinico condiviso, generazione automatica di consegne fra turni via IA, e piena gestione dei dati inseriti (creazione, modifica, cancellazione).

## Architecture
- **Backend**: FastAPI + Motor MongoDB async. Router `/api` per patients, entries, handovers, data-management, ai-handover, trend.
- **Frontend**: React 19 + React Router + shadcn/ui + Tailwind + sonner + recharts + Capacitor 6 (Android).
- **AI**: Claude Sonnet 4.6 via Emergent LLM Key (`emergentintegrations` library).
- **Distribuzione**: Google Play Store AAB `com.caregiversync.assistiti` v1.1.0.

## User Personas
1. Familiare caregiver (coordina più figure attorno all'anziano)
2. Badante / OSS (registra parametri, farmaci, sintomi durante il turno)
3. Medico di riferimento (futuro: sola lettura per verifica clinica)

## Core Requirements (implementati)
- ✅ CRUD assistiti (nome, patologia, età, note)
- ✅ Diario clinico multi-tipo (vital/medication/symptom/note) con valore + unità
- ✅ **Modifica voci** dal menu contestuale
- ✅ Cancellazione dati completa: singola con Undo, bulk per tipo, per collezione, wipe totale (GDPR)
- ✅ **Generazione consegna IA** (Claude Sonnet 4.6) con selettore ore (8/12/24/72)
- ✅ **Storico consegne** salvato e consultabile per paziente
- ✅ **Grafico andamento** parametri vitali (30gg, supporto valori doppi tipo BP)
- ✅ Home dashboard con saluto contestuale, stats, ricerca, avatar
- ✅ Menu contestuali ⋮ mobile-first
- ✅ Data-testid completi

## Implementation Timeline
- **2026-01**: MVP con CRUD + delete flows + wipe GDPR
- **2026-01**: v1.0.0 AAB per Google Play (`com.caregiversync.assistiti`, targetSdk 35, versionCode 1)
- **2026-08**: v1.1.0 con feature IA, edit entries, storico handover, trend chart, home ridisegnata (versionCode 2)
- **2026-09**: v1.2.1 rebranding package a `com.caregiversync.app` + RevenueCat + prod URL fixata (versionCode 7)
- **2026-02** (Feb 2026): v1.2.3 aggiornamento requisiti Play Console 2026 → targetSdkVersion=36, compileSdkVersion=36, `com.android.billingclient:billing:8.0.0` (resolutionStrategy forza upgrade da RevenueCat 6.2.1). AAB firmato `/app/release/caregiver-sync-v1.2.3.aab` (versionCode 8). Testing agent iterazione 3 → 27/27 tests pass, nessuna regressione.
- **2026-02**: v1.2.4 chiave RevenueCat reale iniettata (`goog_jcTcoViIwdKAfczoSbGvbXlydYP`) in `.env.production`, AAB rigenerato → `/app/release/caregiver-sync-v1.2.4.aab` (versionCode 9). Chiave verificata dentro il bundle JS embeddato nell'AAB.

## Prioritized Backlog

### P1 (prossime iterazioni)
- **Handover post-generation UX** — distinguere "viewing history" vs "newly generated" nel dialog
- **Multi-utente + auth** — famiglia condivisa, permessi per badante/medico
- **Allerta farmaci in esaurimento** basata sulla frequenza di somministrazione
- **Export PDF fascicolo** per visita medica
- **Refactor App.js in moduli** (1418 righe in un file — critical review lo segnala)

### P2 (nice to have)
- Notifiche push per promemoria (mobile)
- Upload foto referti/ricette con OCR
- Ricerca full-text sul diario
- Domande all'IA sul paziente ("Come sta andando la glicemia?")
- Dark mode

## Known Limitations
- **No auth**: MVP single-tenant — qualunque utente vede tutti i dati
- **Backend deve restare online**: l'APK contiene solo il frontend
- **AI cost**: ogni handover consuma quota della Emergent LLM Key dell'utente

## Google Play — Stato Pubblicazione
- ✅ AAB firmato pronto in `/app/release/caregiver-sync-v1.2.4.aab` (targetSdk 36 + billing 8.0.0 + chiave RevenueCat reale)
- ✅ MARKETING.md con testi (titolo, breve, lunga descrizione)
- ✅ DATA_SAFETY.md pronto per il modulo Play Console
- ✅ PRIVACY_POLICY.md GDPR-compliant con clausola IA
- ✅ Keystore salvata + credenziali documentate in README.md
- ⏳ **Da fare dall'utente**: caricare l'AAB v1.2.3 su Play Console (Internal testing → Production), pubblicare privacy policy URL, caricare screenshot 1080×1920, submit release, configurare RevenueCat con le chiavi reali.
