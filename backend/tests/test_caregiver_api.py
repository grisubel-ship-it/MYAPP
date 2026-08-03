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


# ---------- PATCH /entries/{id} (Edit entry) ----------
def test_patch_entry_updates_fields(client):
    p = client.post(f"{API}/patients", json={"name": "TEST_Edit"}).json()
    e = client.post(f"{API}/entries", json={
        "patient_id": p["id"], "kind": "vital", "label": "Pressione", "value": "140/90", "unit": "mmHg"
    }).json()

    # Update value + unit
    r = client.patch(f"{API}/entries/{e['id']}", json={"value": "130/80", "unit": "mmHg"})
    assert r.status_code == 200, r.text
    updated = r.json()
    assert updated["value"] == "130/80"
    assert updated["label"] == "Pressione"  # unchanged
    assert updated["id"] == e["id"]

    # Verify persistence via GET
    lst = client.get(f"{API}/entries?patient_id={p['id']}").json()
    assert lst[0]["value"] == "130/80"


def test_patch_entry_empty_payload_returns_original(client):
    p = client.post(f"{API}/patients", json={"name": "TEST_Edit2"}).json()
    e = client.post(f"{API}/entries", json={
        "patient_id": p["id"], "kind": "note", "label": "N1", "value": "x"
    }).json()

    r = client.patch(f"{API}/entries/{e['id']}", json={})
    assert r.status_code == 200
    body = r.json()
    assert body["id"] == e["id"]
    assert body["label"] == "N1"
    assert body["value"] == "x"


def test_patch_entry_not_found(client):
    r = client.patch(f"{API}/entries/nonexistent", json={"label": "x"})
    assert r.status_code == 404


# ---------- Handovers history ----------
def test_handovers_list_empty(client):
    r = client.get(f"{API}/handovers?patient_id=nope")
    assert r.status_code == 200
    assert r.json() == []


def test_handover_delete(client):
    # Manually seed a handover doc via patient + entry, but we can't call POST /ai/handover
    # deterministically (needs LLM). Instead we test delete endpoint via 404 path.
    r = client.delete(f"{API}/handovers/nonexistent")
    assert r.status_code == 404


# ---------- Trend endpoint ----------
def test_trend_returns_labels_when_no_label(client):
    p = client.post(f"{API}/patients", json={"name": "TEST_Tr"}).json()
    for label, value in [("Pressione", "145/85"), ("Pressione", "130/80"), ("Glicemia", "110")]:
        client.post(f"{API}/entries", json={
            "patient_id": p["id"], "kind": "vital", "label": label, "value": value, "unit": "x"
        })
    # note (non-vital) should not appear
    client.post(f"{API}/entries", json={
        "patient_id": p["id"], "kind": "note", "label": "Ignora", "value": "42"
    })

    r = client.get(f"{API}/patients/{p['id']}/trend")
    assert r.status_code == 200
    data = r.json()
    assert "labels" in data
    assert set(data["labels"]) == {"Pressione", "Glicemia"}


def test_trend_parses_bp_value_and_value2(client):
    p = client.post(f"{API}/patients", json={"name": "TEST_Tr2"}).json()
    for v in ["145/85", "130/80", "150/95"]:
        client.post(f"{API}/entries", json={
            "patient_id": p["id"], "kind": "vital", "label": "Pressione", "value": v, "unit": "mmHg"
        })

    r = client.get(f"{API}/patients/{p['id']}/trend?label=Pressione")
    assert r.status_code == 200
    data = r.json()
    assert data["label"] == "Pressione"
    assert data["unit"] == "mmHg"
    assert len(data["series"]) == 3
    # First point 145/85
    p0 = data["series"][0]
    assert p0["value"] == 145.0
    assert p0["value2"] == 85.0
    assert p0["raw"] == "145/85"


def test_trend_parses_single_number(client):
    p = client.post(f"{API}/patients", json={"name": "TEST_Tr3"}).json()
    for v in ["36.5", "37.2"]:
        client.post(f"{API}/entries", json={
            "patient_id": p["id"], "kind": "vital", "label": "Temperatura", "value": v, "unit": "°C"
        })

    r = client.get(f"{API}/patients/{p['id']}/trend?label=Temperatura")
    assert r.status_code == 200
    data = r.json()
    assert len(data["series"]) == 2
    assert data["series"][0]["value"] == 36.5
    assert "value2" not in data["series"][0]


def test_trend_case_insensitive_label(client):
    p = client.post(f"{API}/patients", json={"name": "TEST_Tr4"}).json()
    client.post(f"{API}/entries", json={
        "patient_id": p["id"], "kind": "vital", "label": "Pressione", "value": "120/80"
    })
    r = client.get(f"{API}/patients/{p['id']}/trend?label=pressione")
    assert r.status_code == 200
    assert len(r.json()["series"]) == 1


def test_trend_patient_not_found(client):
    r = client.get(f"{API}/patients/nonexistent/trend")
    assert r.status_code == 404


def test_trend_skips_non_numeric_values(client):
    p = client.post(f"{API}/patients", json={"name": "TEST_Tr5"}).json()
    client.post(f"{API}/entries", json={
        "patient_id": p["id"], "kind": "vital", "label": "Note", "value": "senza numero"
    })
    client.post(f"{API}/entries", json={
        "patient_id": p["id"], "kind": "vital", "label": "Note", "value": "42"
    })
    r = client.get(f"{API}/patients/{p['id']}/trend?label=Note")
    assert r.status_code == 200
    assert len(r.json()["series"]) == 1
    assert r.json()["series"][0]["value"] == 42.0
