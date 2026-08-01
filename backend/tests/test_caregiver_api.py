"""Backend regression tests for Caregiver Sync delete/restore flows."""
import os
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://app-release-config.preview.emergentagent.com").rstrip("/")
API = f"{BASE_URL}/api"


@pytest.fixture(scope="module")
def client():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    yield s
    # Cleanup: wipe test data
    try:
        s.delete(f"{API}/data/wipe", timeout=10)
    except Exception:
        pass


@pytest.fixture(autouse=True)
def _wipe_before(client):
    # ensure clean state per test
    client.delete(f"{API}/data/wipe", timeout=10)
    yield


# ---------- Health ----------
def test_root(client):
    r = client.get(f"{API}/")
    assert r.status_code == 200
    assert "Caregiver Sync" in r.json().get("message", "")


# ---------- Patients CRUD ----------
def test_create_and_list_patient(client):
    payload = {"name": "TEST_Maria", "pathology": "Ipertensione", "birth_year": 1942}
    r = client.post(f"{API}/patients", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["name"] == "TEST_Maria"
    assert data["pathology"] == "Ipertensione"
    assert data["birth_year"] == 1942
    assert "id" in data

    # verify persistence
    r2 = client.get(f"{API}/patients")
    assert r2.status_code == 200
    assert any(p["id"] == data["id"] for p in r2.json())

    r3 = client.get(f"{API}/patients/{data['id']}")
    assert r3.status_code == 200
    assert r3.json()["name"] == "TEST_Maria"


def test_get_nonexistent_patient(client):
    r = client.get(f"{API}/patients/nonexistent-id")
    assert r.status_code == 404


# ---------- Entries CRUD ----------
def test_entries_flow(client):
    p = client.post(f"{API}/patients", json={"name": "TEST_P"}).json()
    pid = p["id"]

    # Create three entries
    for kind, label, value, unit in [
        ("vital", "Pressione", "140/90", "mmHg"),
        ("medication", "Metformina", "500", "mg"),
        ("symptom", "Vertigini", None, None),
    ]:
        r = client.post(f"{API}/entries", json={
            "patient_id": pid, "kind": kind, "label": label, "value": value, "unit": unit,
        })
        assert r.status_code == 201, r.text
        assert r.json()["kind"] == kind

    r = client.get(f"{API}/entries?patient_id={pid}")
    assert r.status_code == 200
    entries = r.json()
    assert len(entries) == 3


def test_entry_reject_bad_patient(client):
    r = client.post(f"{API}/entries", json={
        "patient_id": "no-such", "kind": "vital", "label": "X"
    })
    assert r.status_code == 404


# ---------- Delete + Restore entry (Undo) ----------
def test_delete_and_restore_entry(client):
    p = client.post(f"{API}/patients", json={"name": "TEST_R"}).json()
    e = client.post(f"{API}/entries", json={
        "patient_id": p["id"], "kind": "vital", "label": "HR", "value": "80"
    }).json()

    d = client.delete(f"{API}/entries/{e['id']}")
    assert d.status_code == 200
    body = d.json()
    assert body["deleted"] is True
    assert body["entry"]["id"] == e["id"]

    # verify gone
    lst = client.get(f"{API}/entries?patient_id={p['id']}").json()
    assert lst == []

    # restore
    r = client.post(f"{API}/entries/restore", json={"entry": body["entry"]})
    assert r.status_code == 200
    lst2 = client.get(f"{API}/entries?patient_id={p['id']}").json()
    assert len(lst2) == 1
    assert lst2[0]["id"] == e["id"]


# ---------- Delete + Restore patient ----------
def test_delete_and_restore_patient(client):
    p = client.post(f"{API}/patients", json={"name": "TEST_Del"}).json()
    client.post(f"{API}/entries", json={"patient_id": p["id"], "kind": "note", "label": "n1"})
    client.post(f"{API}/entries", json={"patient_id": p["id"], "kind": "vital", "label": "v1"})

    d = client.delete(f"{API}/patients/{p['id']}")
    assert d.status_code == 200
    body = d.json()
    assert body["deleted"] is True
    assert body["patient"]["id"] == p["id"]
    assert len(body["entries"]) == 2

    # Patient should be gone
    assert client.get(f"{API}/patients/{p['id']}").status_code == 404
    assert client.get(f"{API}/entries?patient_id={p['id']}").json() == []

    # Restore
    r = client.post(f"{API}/patients/restore", json={
        "patient": body["patient"], "entries": body["entries"]
    })
    assert r.status_code == 200
    assert client.get(f"{API}/patients/{p['id']}").status_code == 200
    assert len(client.get(f"{API}/entries?patient_id={p['id']}").json()) == 2


# ---------- Bulk delete ----------
def test_bulk_delete_by_kind(client):
    p = client.post(f"{API}/patients", json={"name": "TEST_B"}).json()
    for k in ["vital", "vital", "medication"]:
        client.post(f"{API}/entries", json={"patient_id": p["id"], "kind": k, "label": k})

    r = client.post(f"{API}/entries/bulk-delete", json={"patient_id": p["id"], "kind": "vital"})
    assert r.status_code == 200
    assert r.json()["count"] == 2

    remaining = client.get(f"{API}/entries?patient_id={p['id']}").json()
    assert len(remaining) == 1
    assert remaining[0]["kind"] == "medication"


def test_bulk_delete_missing_patient_id(client):
    r = client.post(f"{API}/entries/bulk-delete", json={"kind": "vital"})
    assert r.status_code == 400


# ---------- Stats + collection wipes ----------
def test_stats_and_collection_and_wipe(client):
    p = client.post(f"{API}/patients", json={"name": "TEST_S"}).json()
    for k in ["vital", "medication", "symptom", "note"]:
        client.post(f"{API}/entries", json={"patient_id": p["id"], "kind": k, "label": k})

    s = client.get(f"{API}/data/stats").json()
    assert s["patients"] == 1
    assert s["entries"] == 4
    assert s["vitals"] == 1
    assert s["medications"] == 1
    assert s["symptoms"] == 1
    assert s["notes"] == 1

    # Clear only entries; patient must remain
    r = client.delete(f"{API}/data/collection/entries")
    assert r.status_code == 200
    s = client.get(f"{API}/data/stats").json()
    assert s["patients"] == 1
    assert s["entries"] == 0

    # Re-add and clear patients (also wipes entries)
    client.post(f"{API}/entries", json={"patient_id": p["id"], "kind": "vital", "label": "x"})
    r = client.delete(f"{API}/data/collection/patients")
    assert r.status_code == 200
    s = client.get(f"{API}/data/stats").json()
    assert s["patients"] == 0
    assert s["entries"] == 0

    # Invalid collection name
    r = client.delete(f"{API}/data/collection/foo")
    assert r.status_code == 400


def test_wipe_all(client):
    client.post(f"{API}/patients", json={"name": "TEST_W"})
    r = client.delete(f"{API}/data/wipe")
    assert r.status_code == 200
    assert r.json()["wiped"] is True
    s = client.get(f"{API}/data/stats").json()
    assert s["patients"] == 0
    assert s["entries"] == 0
