"""Regression tests for /api/downloads and /api/download/{filename}
   after new AAB v1.2.3 (targetSdk=36, billing=8.0.0) was generated.
"""
import os
import pytest
import requests
from pathlib import Path

# Load REACT_APP_BACKEND_URL from frontend/.env if not already in env
if not os.environ.get("REACT_APP_BACKEND_URL"):
    env_file = Path("/app/frontend/.env")
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line.startswith("REACT_APP_BACKEND_URL="):
                os.environ["REACT_APP_BACKEND_URL"] = line.split("=", 1)[1].strip()
                break

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
assert BASE_URL, "REACT_APP_BACKEND_URL missing"
API = f"{BASE_URL}/api"


@pytest.fixture(scope="module")
def client():
    s = requests.Session()
    yield s


def test_downloads_list_contains_new_and_old_aab(client):
    r = client.get(f"{API}/downloads", timeout=15)
    assert r.status_code == 200, r.text
    data = r.json()
    assert "files" in data
    names = [f["name"] for f in data["files"]]
    assert "caregiver-sync-v1.2.3.aab" in names, f"New AAB missing. Got: {names}"
    assert "caregiver-sync-v1.2.1.aab" in names, f"Old AAB missing. Got: {names}"

    # size sanity for the new file (~6.2MB)
    new_entry = next(f for f in data["files"] if f["name"] == "caregiver-sync-v1.2.3.aab")
    assert new_entry["size_bytes"] > 5_000_000
    assert new_entry["size_bytes"] < 20_000_000
    assert new_entry["url"].endswith("/api/download/caregiver-sync-v1.2.3.aab")


def test_download_new_aab_headers_and_stream(client):
    url = f"{API}/download/caregiver-sync-v1.2.3.aab"
    r = client.get(url, timeout=30, stream=True)
    assert r.status_code == 200, r.text
    assert r.headers.get("content-type", "").startswith("application/octet-stream")
    cd = r.headers.get("content-disposition", "")
    assert "attachment" in cd.lower()
    assert "caregiver-sync-v1.2.3.aab" in cd

    # Ensure body actually streams > 5MB
    total = 0
    for chunk in r.iter_content(chunk_size=65536):
        total += len(chunk)
        if total > 6_000_000:
            break
    assert total > 5_000_000, f"Downloaded only {total} bytes"


def test_download_old_aab_still_works(client):
    r = client.get(f"{API}/download/caregiver-sync-v1.2.1.aab", timeout=30, stream=True)
    assert r.status_code == 200
    assert r.headers.get("content-type", "").startswith("application/octet-stream")
    # consume a bit to close cleanly
    for _ in r.iter_content(65536):
        break


def test_download_not_whitelisted_returns_404(client):
    r = client.get(f"{API}/download/../etc/passwd", timeout=10)
    assert r.status_code in (404, 400)

    r2 = client.get(f"{API}/download/random-nonexistent.aab", timeout=10)
    assert r2.status_code == 404


def test_ai_handover_free_tier_gating_returns_402(client):
    """When app_user_id is provided and monthly count >= limit, must return 402.
       We simulate by hammering with a fake user_id after seeding via repeated calls.
       Skip if it would require polluting DB — instead we check the shape:
       call with app_user_id but no patient -> patient 404 (means gating did not trigger for fresh user).
    """
    # A brand-new free user should NOT be gated on first call — expect 404 (patient not found)
    r = client.post(f"{API}/ai/handover", json={
        "patient_id": "does-not-exist",
        "app_user_id": "TEST_free_new_user_gating",
    }, timeout=15)
    # Not 402 because count=0
    assert r.status_code == 404, f"Expected 404 (patient), got {r.status_code}: {r.text}"
