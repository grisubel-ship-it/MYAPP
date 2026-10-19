# Tests for access/trial, admin login + convention CRUD, redeem flow, AI handover 402 gating
import os
import uuid
from datetime import datetime, timezone, timedelta

import pytest
import requests


def _base():
    url = os.environ.get("REACT_APP_BACKEND_URL")
    if not url:
        for line in open("/app/frontend/.env"):
            if line.startswith("REACT_APP_BACKEND_URL="):
                url = line.split("=", 1)[1].strip()
    return url.rstrip("/")


BASE_URL = _base()
API = f"{BASE_URL}/api"
ADMIN_PASSWORD = "CgSync-B7N4D7pf"


def uid(prefix="TEST_u"):
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def ip_header():
    return {"X-Forwarded-For": f"10.{uuid.uuid4().int % 250}.{uuid.uuid4().int % 250}.{uuid.uuid4().int % 250}"}


@pytest.fixture(scope="module")
def s():
    return requests.Session()


@pytest.fixture(scope="module")
def token(s):
    r = s.post(f"{API}/admin/login", json={"password": ADMIN_PASSWORD}, headers=ip_header())
    assert r.status_code == 200, r.text
    return r.json()["token"]


@pytest.fixture(scope="module")
def auth(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="module")
def created_codes(s, auth):
    codes = []
    yield codes
    for c in codes:
        s.delete(f"{API}/admin/conventions/{c}", headers=auth)


def make_code(s, auth, created_codes, **kw):
    body = {"cooperative_name": "TEST_Coop Sole", "max_uses": 2, "duration_months": 3}
    body.update(kw)
    r = s.post(f"{API}/admin/conventions", json=body, headers=auth)
    assert r.status_code == 201, r.text
    created_codes.append(r.json()["code"])
    return r.json()


# ---- Access status ----
class TestAccess:
    def test_new_user_trial(self, s):
        r = s.get(f"{API}/access/status", params={"app_user_id": uid()})
        assert r.status_code == 200
        d = r.json()
        assert d["access"] is True and d["reason"] == "trial" and d["trial_days_left"] == 30
        assert d["convention"] is None

    def test_trial_idempotent(self, s):
        u = uid()
        a = s.get(f"{API}/access/status", params={"app_user_id": u}).json()
        b = s.get(f"{API}/access/status", params={"app_user_id": u}).json()
        assert a["trial_ends_at"] == b["trial_ends_at"]

    def test_expired_demo(self, s):
        d = s.get(f"{API}/access/status", params={"app_user_id": "u_expired_demo"}).json()
        assert d["access"] is False and d["reason"] == "expired" and d["trial_days_left"] == 0

    def test_missing_param(self, s):
        assert s.get(f"{API}/access/status").status_code == 422


# ---- Admin login ----
class TestAdminLogin:
    def test_wrong_password(self, s):
        r = s.post(f"{API}/admin/login", json={"password": "wrong"}, headers=ip_header())
        assert r.status_code == 401

    def test_lockout(self, s):
        h = ip_header()
        codes = [s.post(f"{API}/admin/login", json={"password": "bad"}, headers=h).status_code for _ in range(5)]
        assert codes == [401] * 5
        r = s.post(f"{API}/admin/login", json={"password": "bad"}, headers=h)
        assert r.status_code == 429
        # even correct password is locked out
        r = s.post(f"{API}/admin/login", json={"password": ADMIN_PASSWORD}, headers=h)
        assert r.status_code == 429

    def test_no_token(self, s):
        assert s.get(f"{API}/admin/conventions").status_code == 401
        assert s.post(f"{API}/admin/conventions", json={"cooperative_name": "xx", "max_uses": 1, "duration_months": 1}).status_code == 401
        assert s.patch(f"{API}/admin/conventions/ABC", json={"is_active": False}).status_code == 401
        assert s.delete(f"{API}/admin/conventions/ABC").status_code == 401

    def test_bad_token(self, s):
        r = s.get(f"{API}/admin/conventions", headers={"Authorization": "Bearer garbage"})
        assert r.status_code == 401


# ---- Admin CRUD ----
class TestAdminCrud:
    def test_create_custom_list_patch_delete(self, s, auth, created_codes):
        code = f"TEST{uuid.uuid4().hex[:6]}".lower()
        d = make_code(s, auth, created_codes, code=code)
        assert d["code"] == code.upper() and d["current_uses"] == 0 and d["is_active"] is True
        lst = s.get(f"{API}/admin/conventions", headers=auth).json()
        assert any(c["code"] == code.upper() for c in lst)
        assert all("_id" not in c for c in lst)
        # duplicate (case-insensitive)
        r = s.post(f"{API}/admin/conventions", json={"cooperative_name": "TEST_x", "code": code, "max_uses": 1, "duration_months": 1}, headers=auth)
        assert r.status_code == 409
        # patch
        r = s.patch(f"{API}/admin/conventions/{code}", json={"is_active": False}, headers=auth)
        assert r.status_code == 200 and r.json()["is_active"] is False
        lst = s.get(f"{API}/admin/conventions", headers=auth).json()
        assert [c for c in lst if c["code"] == code.upper()][0]["is_active"] is False
        # delete
        r = s.delete(f"{API}/admin/conventions/{code}", headers=auth)
        assert r.status_code == 200
        r = s.delete(f"{API}/admin/conventions/{code}", headers=auth)
        assert r.status_code == 404

    def test_autogenerate(self, s, auth, created_codes):
        d = make_code(s, auth, created_codes, cooperative_name="TEST Coop Alba")
        assert d["code"].startswith("TESTCO-") and len(d["code"]) == 13

    def test_validation(self, s, auth):
        r = s.post(f"{API}/admin/conventions", json={"cooperative_name": "TEST", "max_uses": 0, "duration_months": 1}, headers=auth)
        assert r.status_code == 422

    def test_patch_missing(self, s, auth):
        r = s.patch(f"{API}/admin/conventions/NOPE_NOT_EXIST", json={"is_active": True}, headers=auth)
        assert r.status_code == 404


# ---- Redeem ----
class TestRedeem:
    def test_redeem_flow(self, s, auth, created_codes):
        conv = make_code(s, auth, created_codes, max_uses=1, duration_months=2)
        u = uid()
        r = s.post(f"{API}/conventions/redeem", json={"code": f"  {conv['code'].lower()} ", "app_user_id": u})
        assert r.status_code == 200, r.text
        d = r.json()
        assert d["status"] == "redeemed" and d["reason"] == "convention" and d["access"] is True
        exp = datetime.fromisoformat(d["convention"]["expires_at"])
        assert abs((exp - (datetime.now(timezone.utc) + timedelta(days=60))).total_seconds()) < 120
        # same user again -> no second use consumed
        r = s.post(f"{API}/conventions/redeem", json={"code": conv["code"], "app_user_id": u})
        assert r.status_code == 200 and r.json()["status"] == "already_redeemed"
        lst = s.get(f"{API}/admin/conventions", headers=auth).json()
        assert [c for c in lst if c["code"] == conv["code"]][0]["current_uses"] == 1
        # another user -> max uses reached
        r = s.post(f"{API}/conventions/redeem", json={"code": conv["code"], "app_user_id": uid()})
        assert r.status_code == 409
        # status endpoint reflects convention
        st = s.get(f"{API}/access/status", params={"app_user_id": u}).json()
        assert st["reason"] == "convention"
        # redemptions list
        red = s.get(f"{API}/admin/conventions/{conv['code']}/redemptions", headers=auth).json()
        assert len(red) == 1 and red[0]["app_user_id"] == u

    def test_invalid_code(self, s):
        r = s.post(f"{API}/conventions/redeem", json={"code": "NOPE-XYZ-999", "app_user_id": uid()})
        assert r.status_code == 404

    def test_inactive_code(self, s, auth, created_codes):
        conv = make_code(s, auth, created_codes)
        s.patch(f"{API}/admin/conventions/{conv['code']}", json={"is_active": False}, headers=auth)
        r = s.post(f"{API}/conventions/redeem", json={"code": conv["code"], "app_user_id": uid()})
        assert r.status_code == 404


# ---- AI handover gating ----
def test_handover_expired_402(s):
    r = s.post(f"{API}/ai/handover", json={"patient_id": "nonexistent", "app_user_id": "u_expired_demo"})
    assert r.status_code == 402
    assert r.json()["detail"]["code"] == "pro_required"
