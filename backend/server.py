from fastapi import FastAPI, APIRouter, HTTPException, Request, status
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
from access import build_router as build_access_router


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI(title="Caregiver Senior API")
api_router = APIRouter(prefix="/api")


# ---------- Models ----------
def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Patient(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    pathology: Optional[str] = None
    birth_year: Optional[int] = None
    notes: Optional[str] = None
    created_at: str = Field(default_factory=iso_now)


class PatientCreate(BaseModel):
    name: str
    pathology: Optional[str] = None
    birth_year: Optional[int] = None
    notes: Optional[str] = None


class Entry(BaseModel):
    """Voce del diario clinico: parametro vitale, farmaco, sintomo, nota."""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    patient_id: str
    kind: str  # 'vital' | 'medication' | 'symptom' | 'note'
    label: str
    value: Optional[str] = None
    unit: Optional[str] = None
    created_at: str = Field(default_factory=iso_now)


class EntryCreate(BaseModel):
    patient_id: str
    kind: str
    label: str
    value: Optional[str] = None
    unit: Optional[str] = None


class EntryUpdate(BaseModel):
    kind: Optional[str] = None
    label: Optional[str] = None
    value: Optional[str] = None
    unit: Optional[str] = None


class Handover(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    patient_id: str
    hours: int
    text: str
    entries_count: int = 0
    created_at: str = Field(default_factory=iso_now)


# ---------- Routes ----------
@api_router.get("/")
async def root():
    return {"message": "Caregiver Senior API online"}


# ----- Patients -----
@api_router.post("/patients", response_model=Patient, status_code=201)
async def create_patient(payload: PatientCreate):
    patient = Patient(**payload.model_dump())
    await db.patients.insert_one(patient.model_dump())
    return patient


@api_router.get("/patients", response_model=List[Patient])
async def list_patients():
    docs = await db.patients.find({}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    return docs


@api_router.get("/patients/{patient_id}", response_model=Patient)
async def get_patient(patient_id: str):
    doc = await db.patients.find_one({"id": patient_id}, {"_id": 0})
    if not doc:
        raise HTTPException(404, "Paziente non trovato")
    return doc


@api_router.delete("/patients/{patient_id}", status_code=200)
async def delete_patient(patient_id: str):
    """Elimina paziente + tutte le sue voci di diario (restituisce il paziente e le entries per Undo)."""
    patient = await db.patients.find_one({"id": patient_id}, {"_id": 0})
    if not patient:
        raise HTTPException(404, "Paziente non trovato")
    entries = await db.entries.find({"patient_id": patient_id}, {"_id": 0}).to_list(10000)
    await db.entries.delete_many({"patient_id": patient_id})
    await db.patients.delete_one({"id": patient_id})
    return {"deleted": True, "patient": patient, "entries": entries}


@api_router.post("/patients/restore")
async def restore_patient(payload: dict):
    """Ripristina un paziente eliminato + le sue entries (usato dall'Undo)."""
    patient = payload.get("patient")
    entries = payload.get("entries", [])
    if not patient:
        raise HTTPException(400, "Payload non valido")
    await db.patients.insert_one(patient)
    if entries:
        await db.entries.insert_many(entries)
    return {"restored": True}


# ----- Entries (diario clinico) -----
@api_router.post("/entries", response_model=Entry, status_code=201)
async def create_entry(payload: EntryCreate):
    # Verifica paziente
    if not await db.patients.find_one({"id": payload.patient_id}):
        raise HTTPException(404, "Paziente non trovato")
    entry = Entry(**payload.model_dump())
    await db.entries.insert_one(entry.model_dump())
    return entry


@api_router.get("/entries", response_model=List[Entry])
async def list_entries(patient_id: Optional[str] = None):
    query = {"patient_id": patient_id} if patient_id else {}
    docs = await db.entries.find(query, {"_id": 0}).sort("created_at", -1).to_list(1000)
    return docs


@api_router.delete("/entries/{entry_id}", status_code=200)
async def delete_entry(entry_id: str):
    doc = await db.entries.find_one({"id": entry_id}, {"_id": 0})
    if not doc:
        raise HTTPException(404, "Voce non trovata")
    await db.entries.delete_one({"id": entry_id})
    return {"deleted": True, "entry": doc}


@api_router.patch("/entries/{entry_id}", response_model=Entry)
async def update_entry(entry_id: str, payload: EntryUpdate):
    """Modifica una voce esistente del diario."""
    doc = await db.entries.find_one({"id": entry_id}, {"_id": 0})
    if not doc:
        raise HTTPException(404, "Voce non trovata")
    updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
    if not updates:
        return doc
    updates["updated_at"] = iso_now()
    await db.entries.update_one({"id": entry_id}, {"$set": updates})
    return await db.entries.find_one({"id": entry_id}, {"_id": 0})


@api_router.post("/entries/restore")
async def restore_entry(payload: dict):
    entry = payload.get("entry")
    if not entry:
        raise HTTPException(400, "Payload non valido")
    await db.entries.insert_one(entry)
    return {"restored": True}


@api_router.post("/entries/bulk-delete")
async def bulk_delete_entries(payload: dict):
    """Elimina tutte le entries di un paziente per una specifica tipologia (vital/medication/...)."""
    patient_id = payload.get("patient_id")
    kind = payload.get("kind")
    if not patient_id:
        raise HTTPException(400, "patient_id obbligatorio")
    query = {"patient_id": patient_id}
    if kind:
        query["kind"] = kind
    result = await db.entries.delete_many(query)
    return {"deleted": True, "count": result.deleted_count}


# ----- Data management -----
@api_router.get("/data/stats")
async def data_stats():
    return {
        "patients": await db.patients.count_documents({}),
        "entries": await db.entries.count_documents({}),
        "vitals": await db.entries.count_documents({"kind": "vital"}),
        "medications": await db.entries.count_documents({"kind": "medication"}),
        "symptoms": await db.entries.count_documents({"kind": "symptom"}),
        "notes": await db.entries.count_documents({"kind": "note"}),
    }


@api_router.delete("/data/collection/{name}")
async def clear_collection(name: str):
    """Svuota una singola collezione: patients | entries."""
    if name not in ("patients", "entries"):
        raise HTTPException(400, "Collezione non valida")
    if name == "patients":
        # Cancellando i pazienti ha senso cancellare anche le loro entries
        r1 = await db.entries.delete_many({})
        r2 = await db.patients.delete_many({})
        return {"deleted": True, "patients": r2.deleted_count, "entries": r1.deleted_count}
    r = await db.entries.delete_many({})
    return {"deleted": True, "entries": r.deleted_count}


@api_router.delete("/data/wipe")
async def wipe_all():
    """Reset totale: cancella TUTTI i dati dell'app (diritto all'oblio GDPR)."""
    p = await db.patients.delete_many({})
    e = await db.entries.delete_many({})
    return {"wiped": True, "patients": p.deleted_count, "entries": e.deleted_count}


# ============================================================
# SUBSCRIPTIONS — RevenueCat + Google Play Billing
# ============================================================
FREE_HANDOVER_LIMIT_MONTHLY = 3


@api_router.get("/subscription/entitlement")
async def get_entitlement(app_user_id: str):
    """Fonte di verità server-side sullo stato Pro dell'utente,
    aggiornata dal webhook RevenueCat."""
    doc = await db.subscriptions.find_one({"app_user_id": app_user_id}, {"_id": 0})
    if not doc:
        return {"pro": False, "expires_at": None, "product_id": None}
    now = datetime.now(timezone.utc)
    expires_at = doc.get("expires_at")
    expires_dt = None
    if expires_at:
        try:
            expires_dt = datetime.fromisoformat(expires_at)
        except Exception:
            expires_dt = None
    pro_active = bool(doc.get("pro_active")) and (expires_dt is None or expires_dt > now)
    return {
        "pro": pro_active,
        "expires_at": expires_at,
        "product_id": doc.get("product_id"),
        "event_type": doc.get("event_type"),
    }


@api_router.get("/subscription/usage")
async def usage(app_user_id: str):
    """Contatore handover IA nel mese corrente + stato Pro."""
    month_start = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    count = await db.handovers.count_documents({
        "app_user_id": app_user_id,
        "created_at": {"$gte": month_start.isoformat()},
    })
    ent = await get_entitlement(app_user_id)
    return {
        "handovers_this_month": count,
        "free_limit": FREE_HANDOVER_LIMIT_MONTHLY,
        "is_pro": ent["pro"],
        "remaining": None if ent["pro"] else max(0, FREE_HANDOVER_LIMIT_MONTHLY - count),
    }


@api_router.post("/webhooks/revenuecat")
async def revenuecat_webhook(request: Request):
    """Riceve eventi RevenueCat (INITIAL_PURCHASE, RENEWAL, CANCELLATION,
    EXPIRATION, BILLING_ISSUE, ecc.) e aggiorna la proiezione MongoDB."""
    import hmac
    import hashlib
    import time as time_mod

    raw = await request.body()
    secret = os.environ.get("RC_WEBHOOK_SECRET", "")
    header = (
        request.headers.get("X-RevenueCat-Webhook-Signature")
        or request.headers.get("Authorization", "")
    )

    if secret:
        valid = False
        try:
            if "v1=" in header:
                parts = dict(item.split("=", 1) for item in header.split(","))
                ts = int(parts["t"])
                if abs(time_mod.time() - ts) < 300:
                    signed = f"{ts}.".encode() + raw
                    expected = hmac.new(secret.encode(), signed, hashlib.sha256).hexdigest()
                    valid = hmac.compare_digest(expected, parts["v1"])
            elif header.startswith("Bearer "):
                valid = hmac.compare_digest(header.split(" ", 1)[1], secret)
        except Exception:
            valid = False
        if not valid:
            raise HTTPException(401, "invalid webhook signature")

    payload = await request.json()
    event = payload.get("event", {})
    event_id = event.get("id")
    app_user_id = event.get("app_user_id")
    if not event_id or not app_user_id:
        raise HTTPException(400, "invalid event payload")

    if await db.rc_events.find_one({"event_id": event_id}):
        return {"status": "duplicate"}
    await db.rc_events.insert_one({
        "event_id": event_id,
        "received_at": iso_now(),
        "type": event.get("type"),
        "app_user_id": app_user_id,
    })

    entitlement_ids = event.get("entitlement_ids") or []
    if "pro_access" not in entitlement_ids:
        return {"status": "ignored"}

    event_type = event.get("type")
    expiration_ms = event.get("expiration_at_ms")
    expiration_iso = None
    expires_dt = None
    if expiration_ms:
        expires_dt = datetime.fromtimestamp(expiration_ms / 1000, tz=timezone.utc)
        expiration_iso = expires_dt.isoformat()

    now = datetime.now(timezone.utc)
    if event_type in ("EXPIRATION", "REFUND", "SUBSCRIPTION_PAUSED"):
        pro_active = False
    elif event_type in ("INITIAL_PURCHASE", "RENEWAL", "UNCANCELLATION", "PRODUCT_CHANGE", "CANCELLATION", "BILLING_ISSUE"):
        pro_active = bool(expires_dt and expires_dt > now)
    else:
        return {"status": "recorded"}

    await db.subscriptions.update_one(
        {"app_user_id": app_user_id},
        {"$set": {
            "app_user_id": app_user_id,
            "pro_active": pro_active,
            "expires_at": expiration_iso,
            "event_type": event_type,
            "updated_at": iso_now(),
            "store": event.get("store"),
            "product_id": event.get("product_id"),
        }},
        upsert=True,
    )
    return {"status": "processed"}


access_router = build_access_router(db, get_entitlement)


# ----- AI: Handover note generation -----
class HandoverRequest(BaseModel):
    patient_id: str
    hours: Optional[int] = 24
    app_user_id: Optional[str] = None  # per gating Free/Pro


@api_router.post("/ai/handover")
async def ai_handover(payload: HandoverRequest):
    """Genera una nota di consegna. Gating: max 3/mese per utenti Free."""
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    from datetime import timedelta

    if payload.app_user_id:
        acc = await access_router.compute_access(payload.app_user_id)
        if not acc["access"]:
            raise HTTPException(
                status_code=402,
                detail={
                    "code": "pro_required",
                    "message": "La prova gratuita è terminata. Abbonati o inserisci un codice convenzione.",
                },
            )

    patient = await db.patients.find_one({"id": payload.patient_id}, {"_id": 0})
    if not patient:
        raise HTTPException(404, "Assistito non trovato")

    cutoff = (datetime.now(timezone.utc) - timedelta(hours=payload.hours)).isoformat()
    entries = await db.entries.find(
        {"patient_id": payload.patient_id, "created_at": {"$gte": cutoff}},
        {"_id": 0},
    ).sort("created_at", 1).to_list(500)

    if not entries:
        return {
            "handover": f"Nelle ultime {payload.hours}h non ci sono voci di diario registrate per {patient['name']}. Nulla da segnalare.",
            "entries_count": 0,
        }

    kind_it = {"vital": "Parametro", "medication": "Farmaco", "symptom": "Sintomo", "note": "Nota"}
    lines = []
    for e in entries:
        try:
            t = datetime.fromisoformat(e["created_at"]).strftime("%H:%M")
        except Exception:
            t = ""
        val = f" {e.get('value', '')} {e.get('unit', '')}".strip()
        lines.append(f"- [{t}] {kind_it.get(e['kind'], e['kind'])}: {e['label']}{(' — ' + val) if val else ''}")

    diary_text = "\n".join(lines)

    system_msg = (
        "Sei un assistente per caregiver (familiari e badanti) che aiuta a redigere la "
        "nota di passaggio consegne fra turni. Riassumi in italiano il diario delle ultime "
        "ore in modo chiaro, ordinato, empatico e utile per chi prende il turno. "
        "NON dare consigli medici, NON diagnosticare. Segnala solo quello che è stato "
        "annotato, evidenzia eventuali sintomi o parametri anomali (senza interpretarli "
        "clinicamente) e ricorda i farmaci somministrati. Struttura la risposta in "
        "3-5 paragrafi brevi: 1) Riepilogo generale del turno, 2) Farmaci somministrati, "
        "3) Parametri rilevati, 4) Sintomi/note, 5) Cosa monitorare nel prossimo turno. "
        "Se un blocco è vuoto, ometterlo. Tono professionale ma caloroso. Max 300 parole."
    )

    user_prompt = (
        f"Assistito: {patient['name']}"
        f"{' — Patologia: ' + patient['pathology'] if patient.get('pathology') else ''}"
        f"{' — Anno di nascita: ' + str(patient['birth_year']) if patient.get('birth_year') else ''}\n\n"
        f"Diario delle ultime {payload.hours} ore:\n{diary_text}"
    )

    try:
        chat = LlmChat(
            api_key=os.environ["EMERGENT_LLM_KEY"],
            session_id=f"handover-{payload.patient_id}-{int(datetime.now().timestamp())}",
            system_message=system_msg,
        ).with_model("anthropic", "claude-sonnet-4-6")

        result = await chat.send_message(UserMessage(text=user_prompt))
        text = result if isinstance(result, str) else str(result)
    except Exception as ex:
        logger.exception("AI handover failed")
        raise HTTPException(502, f"Servizio IA non disponibile: {ex}")

    # Salva l'handover generato per lo storico
    handover = Handover(
        patient_id=payload.patient_id,
        hours=payload.hours,
        text=text.strip(),
        entries_count=len(entries),
    )
    doc = handover.model_dump()
    if payload.app_user_id:
        doc["app_user_id"] = payload.app_user_id
    await db.handovers.insert_one(doc)

    return {
        "id": handover.id,
        "handover": handover.text,
        "entries_count": handover.entries_count,
        "created_at": handover.created_at,
    }


# ----- Handovers history -----
@api_router.get("/handovers", response_model=List[Handover])
async def list_handovers(patient_id: Optional[str] = None, limit: int = 50):
    query = {"patient_id": patient_id} if patient_id else {}
    docs = await db.handovers.find(query, {"_id": 0}).sort("created_at", -1).to_list(limit)
    return docs


@api_router.delete("/handovers/{handover_id}")
async def delete_handover(handover_id: str):
    doc = await db.handovers.find_one({"id": handover_id}, {"_id": 0})
    if not doc:
        raise HTTPException(404, "Consegna non trovata")
    await db.handovers.delete_one({"id": handover_id})
    return {"deleted": True, "handover": doc}


# ----- Trend (parametri vitali nel tempo) -----
@api_router.get("/patients/{patient_id}/trend")
async def patient_trend(patient_id: str, label: Optional[str] = None, days: int = 30):
    """Ritorna una serie storica di valori numerici per un parametro vitale.
    Se `label` non è specificato, ritorna la lista delle label disponibili."""
    from datetime import timedelta
    import re

    if not await db.patients.find_one({"id": patient_id}):
        raise HTTPException(404, "Paziente non trovato")

    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    q = {"patient_id": patient_id, "kind": "vital", "created_at": {"$gte": cutoff}}
    docs = await db.entries.find(q, {"_id": 0}).sort("created_at", 1).to_list(2000)

    if label is None:
        labels = sorted({d["label"] for d in docs})
        return {"labels": labels}

    def parse_num(v):
        if not v:
            return None
        # Estrae il primo numero (es. "145/85" -> 145, "36.5" -> 36.5)
        m = re.search(r"[-+]?\d*\.?\d+", str(v))
        return float(m.group()) if m else None

    def parse_second(v):
        if not v:
            return None
        # Per pressione tipo "145/85" -> 85
        m = re.findall(r"[-+]?\d*\.?\d+", str(v))
        return float(m[1]) if len(m) > 1 else None

    series = []
    for d in docs:
        if d["label"].lower() != label.lower():
            continue
        n1 = parse_num(d.get("value"))
        n2 = parse_second(d.get("value"))
        if n1 is None:
            continue
        point = {"t": d["created_at"], "value": n1, "raw": d.get("value"), "unit": d.get("unit")}
        if n2 is not None:
            point["value2"] = n2
        series.append(point)

    return {"label": label, "unit": (series[0]["unit"] if series else None), "series": series}


# ----- Static release downloads -----
RELEASE_DIR = Path("/app/release")
ALLOWED_DOWNLOADS = {
    "google-play-kit.zip": "application/zip",
    "google-play-kit-v1.2.4.zip": "application/zip",
    "google-play-kit-v1.2.5.zip": "application/zip",
    "google-play-kit-v1.2.6.zip": "application/zip",
    "google-play-kit-v1.2.7.zip": "application/zip",
    "google-play-kit-v1.2.8.zip": "application/zip",
    "screenshots-playstore.zip": "application/zip",
    "screenshots-playstore-safe.zip": "application/zip",
    "caregiver-sync-v1.2.1.aab": "application/octet-stream",
    "caregiver-sync-v1.2.1.apk": "application/vnd.android.package-archive",
    "caregiver-sync-v1.2.3.aab": "application/octet-stream",
    "caregiver-sync-v1.2.4.aab": "application/octet-stream",
    "caregiver-sync-v1.2.4.apk": "application/vnd.android.package-archive",
    "caregiver-sync-v1.2.5.aab": "application/octet-stream",
    "caregiver-sync-v1.2.5.apk": "application/vnd.android.package-archive",
    "caregiver-sync-v1.2.6.aab": "application/octet-stream",
    "caregiver-sync-v1.2.6.apk": "application/vnd.android.package-archive",
    "caregiver-sync-v1.2.7.aab": "application/octet-stream",
    "caregiver-sync-v1.2.7.apk": "application/vnd.android.package-archive",
    "caregiver-sync-v1.2.8.aab": "application/octet-stream",
    "caregiver-sync-v1.2.8.apk": "application/vnd.android.package-archive",
    "caregiver-sync-v1.2.9.aab": "application/octet-stream",
    "caregiver-sync-v1.2.9.apk": "application/vnd.android.package-archive",
    "caregiver-sync-v1.3.0.aab": "application/octet-stream",
    "caregiver-sync-v1.3.0.apk": "application/vnd.android.package-archive",
    "caregiver-sync-v1.3.1.aab": "application/octet-stream",
    "caregiver-sync-v1.3.1.apk": "application/vnd.android.package-archive",
    "caregiver-senior-v1.6.1.aab": "application/octet-stream",
    "caregiver-senior-v1.6.1.apk": "application/vnd.android.package-archive",
    "caregiver-senior-v1.6.0.aab": "application/octet-stream",
    "caregiver-senior-v1.6.0.apk": "application/vnd.android.package-archive",
    "google-play-kit-v1.6.0.zip": "application/zip",
    "caregiver-sync-v1.5.1.aab": "application/octet-stream",
    "caregiver-sync-v1.5.1.apk": "application/vnd.android.package-archive",
    "caregiver-sync-v1.5.0.aab": "application/octet-stream",
    "caregiver-sync-v1.5.0.apk": "application/vnd.android.package-archive",
    "caregiver-sync-v1.4.1.aab": "application/octet-stream",
    "caregiver-sync-v1.4.1.apk": "application/vnd.android.package-archive",
    "caregiver-sync-v1.4.0.aab": "application/octet-stream",
    "caregiver-sync-v1.4.0.apk": "application/vnd.android.package-archive",
    "caregiver-sync-v1.3.2.aab": "application/octet-stream",
    "caregiver-sync-v1.3.2.apk": "application/vnd.android.package-archive",
    "google-play-kit-v1.3.1.zip": "application/zip",
    "google-play-kit-v1.3.2.zip": "application/zip",
    "caregiver-sync-release.jks": "application/octet-stream",
    "screenshots.zip": "application/zip",
    "SORGENTE_CODICE.zip": "application/zip",
    "README.md": "text/markdown; charset=utf-8",
    "PLAY_CONSOLE_CHECKLIST.md": "text/markdown; charset=utf-8",
    "MARKETING.md": "text/markdown; charset=utf-8",
    "DATA_SAFETY.md": "text/markdown; charset=utf-8",
    "PRIVACY_POLICY.md": "text/markdown; charset=utf-8",
    "SUBSCRIPTIONS_SETUP.md": "text/markdown; charset=utf-8",
    "ios-project.zip": "application/zip",
    "logo-caregiver-sync.png": "image/png",
    "logo-caregiver-senior.png": "image/png",
    "feature-graphic-1024x500.png": "image/png",
    "APP_STORE_LISTING.md": "text/markdown; charset=utf-8",
    "IOS_BUILD_GUIDE.md": "text/markdown; charset=utf-8",
    "FIVERR_UPWORK_JOB.md": "text/markdown; charset=utf-8",
    "volantino-caregiver-senior-playstore.pdf": "application/pdf",
    "volantino-caregiver-senior-beta.pdf": "application/pdf",
    "volantino-esempio-cooperativa.pdf": "application/pdf",
    "volantino-caregiver-sync-playstore.pdf": "application/pdf",
    "volantino-caregiver-sync-beta.pdf": "application/pdf",
}


@api_router.get("/download/{filename}")
async def download_release_file(filename: str):
    """Scarica un file di release. Whitelist per sicurezza."""
    if filename not in ALLOWED_DOWNLOADS:
        raise HTTPException(404, "File non disponibile")
    file_path = RELEASE_DIR / filename
    if not file_path.exists():
        raise HTTPException(404, "File non trovato sul server")
    return FileResponse(
        path=str(file_path),
        media_type=ALLOWED_DOWNLOADS[filename],
        filename=filename,
    )


@api_router.get("/downloads")
async def list_downloads():
    """Elenco leggibile dei file scaricabili con URL diretti."""
    base = os.environ.get("PUBLIC_URL", "").rstrip("/")
    items = []
    for name in ALLOWED_DOWNLOADS:
        f = RELEASE_DIR / name
        if f.exists():
            items.append({
                "name": name,
                "size_bytes": f.stat().st_size,
                "url": f"{base}/api/download/{name}" if base else f"/api/download/{name}",
            })
    return {"files": items}


app.include_router(api_router)
app.include_router(access_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=False,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
