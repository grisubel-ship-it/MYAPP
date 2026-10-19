import os
import hmac
import math
import secrets
from datetime import datetime, timezone, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

import csv
import io

import jwt
from fastapi import APIRouter, HTTPException, Request, Depends, Response
from pydantic import BaseModel, Field

from flyer import build_coop_flyer

TRIAL_DAYS = 30
JWT_ALGORITHM = "HS256"
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_MINUTES = 15


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _parse(iso: Optional[str]) -> Optional[datetime]:
    try:
        return datetime.fromisoformat(iso) if iso else None
    except ValueError:
        return None


class RedeemRequest(BaseModel):
    code: str = Field(min_length=3, max_length=40)
    app_user_id: str = Field(min_length=3, max_length=100)


class MigrateRequest(BaseModel):
    from_id: str = Field(min_length=3, max_length=100)
    to_id: str = Field(min_length=3, max_length=100)


class AdminLogin(BaseModel):
    password: str


class ConventionCreate(BaseModel):
    cooperative_name: str = Field(min_length=2, max_length=120)
    code: Optional[str] = Field(default=None, max_length=40)
    max_uses: int = Field(ge=1, le=100000)
    duration_months: int = Field(ge=1, le=120)


class ConventionUpdate(BaseModel):
    is_active: Optional[bool] = None
    max_uses: Optional[int] = Field(default=None, ge=1, le=100000)
    duration_months: Optional[int] = Field(default=None, ge=1, le=120)


def build_router(db, get_entitlement) -> APIRouter:
    router = APIRouter(prefix="/api")

    async def get_or_create_user(app_user_id: str) -> dict:
        await db.app_users.update_one(
            {"app_user_id": app_user_id},
            {"$setOnInsert": {"app_user_id": app_user_id, "trial_started_at": _now().isoformat()}},
            upsert=True,
        )
        return await db.app_users.find_one({"app_user_id": app_user_id}, {"_id": 0})

    async def compute_access(app_user_id: str) -> dict:
        user = await get_or_create_user(app_user_id)
        now = _now()
        ent = await get_entitlement(app_user_id)
        trial_ends = _parse(user["trial_started_at"]) + timedelta(days=TRIAL_DAYS)
        trial_active = trial_ends > now
        conv_exp = _parse(user.get("convention_expires_at"))
        conv_active = bool(conv_exp and conv_exp > now)
        if ent["pro"]:
            reason = "subscription"
        elif conv_active:
            reason = "convention"
        elif trial_active:
            reason = "trial"
        else:
            reason = "expired"
        return {
            "access": reason != "expired",
            "reason": reason,
            "trial_ends_at": trial_ends.isoformat(),
            "trial_days_left": math.ceil((trial_ends - now).total_seconds() / 86400) if trial_active else 0,
            "subscription": ent,
            "convention": {
                "code": user.get("convention_code"),
                "cooperative_name": user.get("cooperative_name"),
                "expires_at": user.get("convention_expires_at"),
                "active": conv_active,
            } if user.get("convention_code") else None,
        }

    router.compute_access = compute_access

    @router.get("/access/status")
    async def access_status(app_user_id: str):
        return await compute_access(app_user_id)

    @router.get("/conventions/{code}/info")
    async def convention_info(code: str):
        conv = await db.convention_codes.find_one({"code": code.strip().upper()}, {"_id": 0})
        if not conv or not conv.get("is_active"):
            raise HTTPException(404, "Codice non valido o non più attivo")
        return {
            "code": conv["code"],
            "cooperative_name": conv["cooperative_name"],
            "duration_months": conv["duration_months"],
            "available": conv["current_uses"] < conv["max_uses"],
        }

    @router.post("/access/migrate")
    async def migrate_user(payload: MigrateRequest):
        """Sposta i dati da un ID d'installazione al nuovo ID legato al telefono."""
        if payload.from_id == payload.to_id:
            return {"status": "noop"}
        old = await db.app_users.find_one({"app_user_id": payload.from_id}, {"_id": 0})
        if not old:
            return {"status": "noop"}
        new = await db.app_users.find_one({"app_user_id": payload.to_id}, {"_id": 0})
        if new:
            upd = {"trial_started_at": min(old["trial_started_at"], new["trial_started_at"])}
            if old.get("convention_code") and not new.get("convention_code"):
                upd.update({k: old[k] for k in ("convention_code", "cooperative_name", "convention_expires_at") if k in old})
            await db.app_users.update_one({"app_user_id": payload.to_id}, {"$set": upd})
            await db.app_users.delete_one({"app_user_id": payload.from_id})
        else:
            await db.app_users.update_one({"app_user_id": payload.from_id}, {"$set": {"app_user_id": payload.to_id}})
        for coll in ("convention_redemptions", "handovers"):
            await db[coll].update_many({"app_user_id": payload.from_id}, {"$set": {"app_user_id": payload.to_id}})
        if not await db.subscriptions.find_one({"app_user_id": payload.to_id}):
            await db.subscriptions.update_one({"app_user_id": payload.from_id}, {"$set": {"app_user_id": payload.to_id}})
        return {"status": "migrated"}

    @router.post("/conventions/redeem")
    async def redeem(payload: RedeemRequest):
        code = payload.code.strip().upper()
        conv = await db.convention_codes.find_one({"code": code}, {"_id": 0})
        if not conv or not conv.get("is_active"):
            raise HTTPException(404, "Codice non valido o non più attivo")
        user = await get_or_create_user(payload.app_user_id)
        if user.get("convention_code") == code and (_parse(user.get("convention_expires_at")) or _now()) > _now():
            return {"status": "already_redeemed", **(await compute_access(payload.app_user_id))}
        updated = await db.convention_codes.find_one_and_update(
            {"code": code, "is_active": True, "$expr": {"$lt": ["$current_uses", "$max_uses"]}},
            {"$inc": {"current_uses": 1}},
        )
        if not updated:
            raise HTTPException(409, "Questo codice ha raggiunto il numero massimo di attivazioni")
        expires = _now() + timedelta(days=30 * conv["duration_months"])
        await db.app_users.update_one(
            {"app_user_id": payload.app_user_id},
            {"$set": {
                "convention_code": code,
                "cooperative_name": conv["cooperative_name"],
                "convention_expires_at": expires.isoformat(),
            }},
        )
        await db.convention_redemptions.insert_one({
            "code": code,
            "app_user_id": payload.app_user_id,
            "cooperative_name": conv["cooperative_name"],
            "redeemed_at": _now().isoformat(),
            "expires_at": expires.isoformat(),
        })
        return {"status": "redeemed", **(await compute_access(payload.app_user_id))}

    # ----- Admin -----
    def secret() -> str:
        return os.environ["JWT_SECRET"]

    async def require_admin(request: Request):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            raise HTTPException(401, "Non autenticato")
        try:
            data = jwt.decode(auth[7:], secret(), algorithms=[JWT_ALGORITHM])
        except jwt.InvalidTokenError:
            raise HTTPException(401, "Sessione scaduta, accedi di nuovo")
        if data.get("role") != "admin":
            raise HTTPException(403, "Accesso negato")

    @router.post("/admin/login")
    async def admin_login(payload: AdminLogin, request: Request):
        ip = (request.headers.get("x-forwarded-for") or (request.client.host if request.client else "?")).split(",")[0].strip()
        rec = await db.login_attempts.find_one({"identifier": ip}) or {}
        locked_until = _parse(rec.get("locked_until"))
        if locked_until and locked_until > _now():
            raise HTTPException(429, "Troppi tentativi. Riprova tra qualche minuto.")
        if not hmac.compare_digest(payload.password.encode(), os.environ["ADMIN_PASSWORD"].encode()):
            count = rec.get("count", 0) + 1
            upd = {"identifier": ip, "count": count}
            if count >= MAX_LOGIN_ATTEMPTS:
                upd = {"identifier": ip, "count": 0, "locked_until": (_now() + timedelta(minutes=LOCKOUT_MINUTES)).isoformat()}
            await db.login_attempts.update_one({"identifier": ip}, {"$set": upd}, upsert=True)
            raise HTTPException(401, "Password errata")
        await db.login_attempts.delete_one({"identifier": ip})
        token = jwt.encode({"role": "admin", "exp": _now() + timedelta(hours=8)}, secret(), algorithm=JWT_ALGORITHM)
        return {"token": token}

    @router.get("/admin/conventions", dependencies=[Depends(require_admin)])
    async def list_conventions():
        return await db.convention_codes.find({}, {"_id": 0}).sort("created_at", -1).to_list(1000)

    @router.post("/admin/conventions", status_code=201, dependencies=[Depends(require_admin)])
    async def create_convention(payload: ConventionCreate):
        code = (payload.code or "").strip().upper().replace(" ", "")
        if not code:
            prefix = "".join(c for c in payload.cooperative_name.upper() if c.isalnum())[:6] or "COOP"
            code = f"{prefix}-{secrets.token_hex(3).upper()}"
        if len(code) < 3:
            raise HTTPException(422, "Codice troppo corto")
        if await db.convention_codes.find_one({"code": code}):
            raise HTTPException(409, "Codice già esistente")
        doc = {
            "code": code,
            "cooperative_name": payload.cooperative_name.strip(),
            "max_uses": payload.max_uses,
            "current_uses": 0,
            "duration_months": payload.duration_months,
            "is_active": True,
            "created_at": _now().isoformat(),
        }
        await db.convention_codes.insert_one(dict(doc))
        return doc

    @router.patch("/admin/conventions/{code}", dependencies=[Depends(require_admin)])
    async def update_convention(code: str, payload: ConventionUpdate):
        upd = {k: v for k, v in payload.model_dump().items() if v is not None}
        if not upd:
            raise HTTPException(422, "Nessuna modifica")
        doc = await db.convention_codes.find_one_and_update(
            {"code": code.upper()}, {"$set": upd}, projection={"_id": 0}, return_document=True
        )
        if not doc:
            raise HTTPException(404, "Codice non trovato")
        return doc

    @router.delete("/admin/conventions/{code}", dependencies=[Depends(require_admin)])
    async def delete_convention(code: str):
        res = await db.convention_codes.delete_one({"code": code.upper()})
        if not res.deleted_count:
            raise HTTPException(404, "Codice non trovato")
        return {"deleted": code.upper()}

    @router.get("/admin/conventions/{code}/redemptions", dependencies=[Depends(require_admin)])
    async def redemptions(code: str):
        return await db.convention_redemptions.find({"code": code.upper()}, {"_id": 0}).sort("redeemed_at", -1).to_list(5000)

    async def _conv_or_404(code: str) -> dict:
        conv = await db.convention_codes.find_one({"code": code.upper()}, {"_id": 0})
        if not conv:
            raise HTTPException(404, "Codice non trovato")
        return conv

    @router.get("/admin/conventions/{code}/report.csv", dependencies=[Depends(require_admin)])
    async def report_csv(code: str):
        conv = await _conv_or_404(code)
        rows = await db.convention_redemptions.find({"code": conv["code"]}, {"_id": 0}).sort("redeemed_at", 1).to_list(100000)
        out = io.StringIO()
        w = csv.writer(out, delimiter=";")
        w.writerow(["Cooperativa", conv["cooperative_name"]])
        w.writerow(["Codice", conv["code"]])
        w.writerow(["Attivazioni", f"{conv['current_uses']} / {conv['max_uses']}"])
        w.writerow(["Durata Premium (mesi)", conv["duration_months"]])
        w.writerow([])
        w.writerow(["N.", "ID utente", "Data attivazione", "Scadenza Premium", "Stato"])
        now = _now()
        rome = ZoneInfo("Europe/Rome")
        for i, r in enumerate(rows, 1):
            exp = _parse(r.get("expires_at"))
            w.writerow([
                i,
                r["app_user_id"],
                _parse(r["redeemed_at"]).astimezone(rome).strftime("%d/%m/%Y %H:%M"),
                exp.astimezone(rome).strftime("%d/%m/%Y") if exp else "",
                "Attivo" if exp and exp > now else "Scaduto",
            ])
        data = "\ufeff" + out.getvalue()
        return Response(data, media_type="text/csv; charset=utf-8", headers={
            "Content-Disposition": f'attachment; filename="attivazioni-{conv["code"]}.csv"'})

    @router.get("/admin/conventions/{code}/flyer.pdf", dependencies=[Depends(require_admin)])
    async def coop_flyer(code: str):
        conv = await _conv_or_404(code)
        pdf = build_coop_flyer(conv["cooperative_name"], conv["code"], conv["duration_months"])
        return Response(pdf, media_type="application/pdf", headers={
            "Content-Disposition": f'attachment; filename="volantino-{conv["code"]}.pdf"'})

    return router
