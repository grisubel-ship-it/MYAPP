# Iteration 5: admin CSV report + PDF flyer per convention code, trial-ending status
import os
import random
import uuid
import pytest
import requests
from pathlib import Path

if not os.environ.get("REACT_APP_BACKEND_URL"):
    for line in Path("/app/frontend/.env").read_text().splitlines():
        if line.startswith("REACT_APP_BACKEND_URL="):
            os.environ["REACT_APP_BACKEND_URL"] = line.split("=", 1)[1].strip()

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL").rstrip("/")
API = f"{BASE_URL}/api"
ADMIN_PASSWORD = "CgSync-B7N4D7pf"


def _ip():
    return f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"


@pytest.fixture(scope="module")
def token():
    r = requests.post(f"{API}/admin/login", json={"password": ADMIN_PASSWORD}, headers={"X-Forwarded-For": _ip()}, timeout=15)
    assert r.status_code == 200, r.text
    return r.json()["token"]


@pytest.fixture(scope="module")
def h(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="module")
def temp_code(h):
    code = f"TESTRPT{uuid.uuid4().hex[:5].upper()}"
    r = requests.post(f"{API}/admin/conventions", json={"cooperative_name": "Coop TEST Àèé; virgola, \"q\"", "code": code, "max_uses": 5, "duration_months": 1}, headers=h)
    assert r.status_code == 201, r.text
    users = [f"u_TEST_rpt_{uuid.uuid4().hex[:6]}" for _ in range(2)]
    for u in users:
        rr = requests.post(f"{API}/conventions/redeem", json={"code": code, "app_user_id": u})
        assert rr.status_code == 200, rr.text
    yield code, users
    requests.delete(f"{API}/admin/conventions/{code}", headers=h)


# --- CSV report ---
class TestReportCSV:
    def test_requires_token(self):
        r = requests.get(f"{API}/admin/conventions/AURORA2026/report.csv")
        assert r.status_code == 401

    def test_bad_token(self):
        r = requests.get(f"{API}/admin/conventions/AURORA2026/report.csv", headers={"Authorization": "Bearer x.y.z"})
        assert r.status_code == 401

    def test_unknown_code_404(self, h):
        r = requests.get(f"{API}/admin/conventions/NOPE_XYZ_999/report.csv", headers=h)
        assert r.status_code == 404

    def test_aurora_report(self, h):
        r = requests.get(f"{API}/admin/conventions/AURORA2026/report.csv", headers=h)
        assert r.status_code == 200, r.text
        assert r.headers["content-type"].startswith("text/csv")
        assert 'filename="attivazioni-AURORA2026.csv"' in r.headers.get("content-disposition", "")
        assert r.content.startswith(b"\xef\xbb\xbf")
        text = r.content.decode("utf-8-sig")
        lines = [l for l in text.splitlines()]
        assert lines[0].startswith("Cooperativa;")
        assert lines[1] == "Codice;AURORA2026"
        assert lines[2].startswith("Attivazioni;")
        assert lines[3].startswith("Durata Premium (mesi);")
        assert "N.;ID utente;Data attivazione;Scadenza Premium;Stato" in lines
        # demo redemption row (u_demo_a was migrated to d_testdevice1 in iteration 6)
        assert any(l.startswith("1;") for l in lines)

    def test_lowercase_code_works(self, h):
        r = requests.get(f"{API}/admin/conventions/aurora2026/report.csv", headers=h)
        assert r.status_code == 200

    def test_temp_report_rows(self, h, temp_code):
        code, users = temp_code
        r = requests.get(f"{API}/admin/conventions/{code}/report.csv", headers=h)
        assert r.status_code == 200
        text = r.content.decode("utf-8-sig")
        lines = text.splitlines()
        assert "Attivazioni;2 / 5" in lines
        idx = lines.index("N.;ID utente;Data attivazione;Scadenza Premium;Stato")
        rows = [l for l in lines[idx + 1:] if l.strip()]
        assert len(rows) == 2
        for i, (row, u) in enumerate(zip(rows, users), 1):
            parts = row.split(";")
            assert parts[0] == str(i) and parts[1] == u and parts[4] == "Attivo"
            assert len(parts[2]) == 16 and parts[2][2] == "/"
        # semicolon in coop name must be quoted
        assert lines[0].startswith('Cooperativa;"Coop TEST')


# --- PDF flyer ---
class TestFlyer:
    def test_requires_token(self):
        assert requests.get(f"{API}/admin/conventions/AURORA2026/flyer.pdf").status_code == 401

    def test_unknown_404(self, h):
        assert requests.get(f"{API}/admin/conventions/NOPE_XYZ_999/flyer.pdf", headers=h).status_code == 404

    def test_aurora_flyer(self, h):
        r = requests.get(f"{API}/admin/conventions/AURORA2026/flyer.pdf", headers=h, timeout=30)
        assert r.status_code == 200
        assert r.headers["content-type"] == "application/pdf"
        assert r.content.startswith(b"%PDF")
        assert 'filename="volantino-AURORA2026.pdf"' in r.headers.get("content-disposition", "")
        assert len(r.content) > 5000

    def test_temp_flyer_special_chars(self, h, temp_code):
        code, _ = temp_code
        r = requests.get(f"{API}/admin/conventions/{code}/flyer.pdf", headers=h, timeout=30)
        assert r.status_code == 200 and r.content.startswith(b"%PDF")


# --- trial status ---
class TestTrialStatus:
    def test_ending_demo(self):
        d = requests.get(f"{API}/access/status", params={"app_user_id": "u_ending_demo"}).json()
        assert d["reason"] == "trial" and d["access"] is True
        assert 1 <= d["trial_days_left"] <= 3

    def test_expired_demo(self):
        d = requests.get(f"{API}/access/status", params={"app_user_id": "u_expired_demo"}).json()
        assert d["access"] is False and d["reason"] == "expired"

    def test_fresh_user(self):
        d = requests.get(f"{API}/access/status", params={"app_user_id": f"u_TEST_fresh_{uuid.uuid4().hex[:6]}"}).json()
        assert d["reason"] == "trial" and d["trial_days_left"] == 30
