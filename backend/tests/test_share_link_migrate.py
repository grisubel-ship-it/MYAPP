# Iteration 6: public convention info (/c/{CODE} landing) + device-id migration (/api/access/migrate)
import os
import uuid
from datetime import datetime, timezone, timedelta

import pytest
import requests
from pymongo import MongoClient


def _base():
    url = os.environ.get("REACT_APP_BACKEND_URL")
    if not url:
        for line in open("/app/frontend/.env"):
            if line.startswith("REACT_APP_BACKEND_URL="):
                url = line.split("=", 1)[1].strip()
    return url.rstrip("/")


def _env(key):
    for line in open("/app/backend/.env"):
        if line.startswith(key + "="):
            return line.split("=", 1)[1].strip().strip('"')


API = f"{_base()}/api"
ADMIN_PASSWORD = "CgSync-B7N4D7pf"
db = MongoClient(_env("MONGO_URL"))[_env("DB_NAME")]


def uid(p="u_TEST_mig"):
    return f"{p}_{uuid.uuid4().hex[:10]}"


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
def tmp_code(s, token):
    code = f"TESTINFO{uuid.uuid4().hex[:6].upper()}"
    r = s.post(f"{API}/admin/conventions", json={"cooperative_name": "TEST Coop Info", "code": code, "max_uses": 1, "duration_months": 3},
               headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 201, r.text
    yield code
    s.delete(f"{API}/admin/conventions/{code}", headers={"Authorization": f"Bearer {token}"})
    db.convention_redemptions.delete_many({"code": code})


@pytest.fixture(scope="module", autouse=True)
def cleanup():
    yield
    for c in ("app_users", "convention_redemptions", "handovers", "subscriptions"):
        db[c].delete_many({"app_user_id": {"$regex": "^(u|d)_TEST_mig"}})


# ---- convention info ----
class TestConventionInfo:
    def test_info_upper(self, s):
        r = s.get(f"{API}/conventions/AURORA2026/info")
        assert r.status_code == 200
        d = r.json()
        assert d["code"] == "AURORA2026"
        assert isinstance(d["cooperative_name"], str) and d["cooperative_name"]
        assert d["duration_months"] == 12
        assert isinstance(d["available"], bool)
        assert set(d.keys()) == {"code", "cooperative_name", "duration_months", "available"}

    def test_info_lowercase(self, s):
        r = s.get(f"{API}/conventions/aurora2026/info")
        assert r.status_code == 200 and r.json()["code"] == "AURORA2026"

    def test_info_unknown_404(self, s):
        r = s.get(f"{API}/conventions/NOPE/info")
        assert r.status_code == 404
        assert "detail" in r.json()

    def test_info_available_then_full(self, s, tmp_code):
        assert s.get(f"{API}/conventions/{tmp_code}/info").json()["available"] is True
        r = s.post(f"{API}/conventions/redeem", json={"code": tmp_code, "app_user_id": uid()})
        assert r.status_code == 200, r.text
        d = s.get(f"{API}/conventions/{tmp_code}/info").json()
        assert d["available"] is False and d["duration_months"] == 3

    def test_info_inactive_404(self, s, token, tmp_code):
        h = {"Authorization": f"Bearer {token}"}
        assert s.patch(f"{API}/admin/conventions/{tmp_code}", json={"is_active": False}, headers=h).status_code == 200
        assert s.get(f"{API}/conventions/{tmp_code}/info").status_code == 404
        s.patch(f"{API}/admin/conventions/{tmp_code}", json={"is_active": True}, headers=h)


# ---- migrate ----
def _set_trial(user_id, days_ago):
    db.app_users.update_one({"app_user_id": user_id},
                            {"$set": {"trial_started_at": (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat()}})


class TestMigrate:
    def test_migrate_to_new_id(self, s):
        old, new = uid(), uid("d_TEST_mig")
        s.get(f"{API}/access/status", params={"app_user_id": old})
        _set_trial(old, 10)
        before = db.app_users.find_one({"app_user_id": old})["trial_started_at"]
        db.handovers.insert_one({"app_user_id": old, "TEST": True})
        db.subscriptions.insert_one({"app_user_id": old, "TEST": True})
        r = s.post(f"{API}/access/migrate", json={"from_id": old, "to_id": new})
        assert r.status_code == 200 and r.json()["status"] == "migrated"
        assert db.app_users.find_one({"app_user_id": old}) is None
        assert db.app_users.find_one({"app_user_id": new})["trial_started_at"] == before
        assert db.handovers.count_documents({"app_user_id": new}) == 1
        assert db.subscriptions.count_documents({"app_user_id": new}) == 1
        st = s.get(f"{API}/access/status", params={"app_user_id": new}).json()
        assert st["reason"] == "trial" and st["trial_days_left"] == 20

    def test_migrate_convention_redemptions(self, s):
        old, new = uid(), uid("d_TEST_mig")
        r = s.post(f"{API}/conventions/redeem", json={"code": "AURORA2026", "app_user_id": old})
        if r.status_code == 409:
            pytest.skip("AURORA2026 full")
        assert r.status_code == 200
        r = s.post(f"{API}/access/migrate", json={"from_id": old, "to_id": new})
        assert r.json()["status"] == "migrated"
        assert db.convention_redemptions.count_documents({"app_user_id": new, "code": "AURORA2026"}) == 1
        assert db.convention_redemptions.count_documents({"app_user_id": old}) == 0
        st = s.get(f"{API}/access/status", params={"app_user_id": new}).json()
        assert st["reason"] == "convention" and st["convention"]["code"] == "AURORA2026"
        db.convention_redemptions.delete_many({"app_user_id": new})
        db.convention_codes.update_one({"code": "AURORA2026"}, {"$inc": {"current_uses": -1}})

    def test_migrate_existing_target_keeps_earliest_trial(self, s):
        old, new = uid(), uid("d_TEST_mig")
        s.get(f"{API}/access/status", params={"app_user_id": old})
        s.get(f"{API}/access/status", params={"app_user_id": new})
        _set_trial(old, 25)  # older trial
        _set_trial(new, 1)
        r = s.post(f"{API}/access/migrate", json={"from_id": old, "to_id": new})
        assert r.json()["status"] == "migrated"
        assert db.app_users.find_one({"app_user_id": old}) is None
        st = s.get(f"{API}/access/status", params={"app_user_id": new}).json()
        assert st["trial_days_left"] == 5

    def test_migrate_existing_target_expired_old(self, s):
        old, new = uid(), uid("d_TEST_mig")
        s.get(f"{API}/access/status", params={"app_user_id": old})
        s.get(f"{API}/access/status", params={"app_user_id": new})
        _set_trial(old, 40)
        s.post(f"{API}/access/migrate", json={"from_id": old, "to_id": new})
        st = s.get(f"{API}/access/status", params={"app_user_id": new}).json()
        assert st["access"] is False and st["reason"] == "expired"

    def test_migrate_existing_target_copies_convention(self, s):
        old, new = uid(), uid("d_TEST_mig")
        s.get(f"{API}/access/status", params={"app_user_id": new})
        exp = (datetime.now(timezone.utc) + timedelta(days=100)).isoformat()
        db.app_users.insert_one({"app_user_id": old, "trial_started_at": datetime.now(timezone.utc).isoformat(),
                                 "convention_code": "AURORA2026", "cooperative_name": "X Coop", "convention_expires_at": exp})
        s.post(f"{API}/access/migrate", json={"from_id": old, "to_id": new})
        st = s.get(f"{API}/access/status", params={"app_user_id": new}).json()
        assert st["reason"] == "convention"
        assert st["convention"]["code"] == "AURORA2026" and st["convention"]["cooperative_name"] == "X Coop"

    def test_migrate_target_keeps_own_convention(self, s):
        old, new = uid(), uid("d_TEST_mig")
        now = datetime.now(timezone.utc)
        db.app_users.insert_one({"app_user_id": old, "trial_started_at": now.isoformat(), "convention_code": "OLDC",
                                 "cooperative_name": "Old", "convention_expires_at": (now + timedelta(days=5)).isoformat()})
        db.app_users.insert_one({"app_user_id": new, "trial_started_at": now.isoformat(), "convention_code": "NEWC",
                                 "cooperative_name": "New", "convention_expires_at": (now + timedelta(days=50)).isoformat()})
        s.post(f"{API}/access/migrate", json={"from_id": old, "to_id": new})
        assert db.app_users.find_one({"app_user_id": new})["convention_code"] == "NEWC"

    def test_migrate_same_id_noop(self, s):
        x = uid()
        s.get(f"{API}/access/status", params={"app_user_id": x})
        r = s.post(f"{API}/access/migrate", json={"from_id": x, "to_id": x})
        assert r.status_code == 200 and r.json()["status"] == "noop"
        assert db.app_users.find_one({"app_user_id": x}) is not None

    def test_migrate_unknown_from_noop(self, s):
        new = uid("d_TEST_mig")
        r = s.post(f"{API}/access/migrate", json={"from_id": uid(), "to_id": new})
        assert r.status_code == 200 and r.json()["status"] == "noop"
        assert db.app_users.find_one({"app_user_id": new}) is None

    def test_migrate_validation(self, s):
        r = s.post(f"{API}/access/migrate", json={"from_id": "a", "to_id": "bb"})
        assert r.status_code == 422
