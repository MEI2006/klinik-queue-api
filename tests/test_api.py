
import pytest
from fastapi.testclient import TestClient

from main import app
from app.database import get_db
from app import database


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(
        database, "DB_PATH", tmp_path / "test_klinik.db"
    )

    with TestClient(app) as test_client:
        yield test_client


def buat_pasien(client, nama="Andi", poli="Umum"):
    return client.post(
        "/api/v1/queues",
        json={
            "nama_pasien": nama,
            "poli": poli,
            "keluhan": "Demam",
        },
    )


def test_home(client):
    response = client.get("/")
    assert response.status_code == 200


def test_daftar_pasien(client):
    response = buat_pasien(client)

    assert response.status_code == 201
    assert response.json()["nama_pasien"] == "Andi"
    assert response.json()["nomor_antrian"] == 1
    assert response.json()["status"] == "menunggu"


def test_nomor_antrian_bertambah(client):
    pertama = buat_pasien(client, "Andi").json()
    kedua = buat_pasien(client, "Budi").json()

    assert pertama["nomor_antrian"] == 1
    assert kedua["nomor_antrian"] == 2


def test_nomor_antrian_terpisah_per_poli(client):
    umum = buat_pasien(client, "Andi", "Umum").json()
    gigi = buat_pasien(client, "Budi", "Gigi").json()

    assert umum["nomor_antrian"] == 1
    assert gigi["nomor_antrian"] == 1


def test_daftar_antrian_hari_ini(client):
    buat_pasien(client)

    response = client.get("/api/v1/queues/today")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_panggil_pasien_berikutnya(client):
    buat_pasien(client, "Andi")
    buat_pasien(client, "Budi")

    response = client.post(
        "/api/v1/queues/call-next?poli=Umum"
    )

    assert response.status_code == 200
    assert response.json()["nama_pasien"] == "Andi"
    assert response.json()["status"] == "dipanggil"


def test_tidak_ada_antrian_menunggu(client):
    response = client.post(
        "/api/v1/queues/call-next?poli=Umum"
    )

    assert response.status_code == 404


def test_ubah_status_pasien(client):
    pasien = buat_pasien(client).json()

    response = client.patch(
        f"/api/v1/queues/{pasien['id']}/status",
        json={"status": "selesai"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "selesai"


def test_status_tidak_valid(client):
    pasien = buat_pasien(client).json()

    response = client.patch(
        f"/api/v1/queues/{pasien['id']}/status",
        json={"status": "tidur"},
    )

    assert response.status_code == 422


def test_pasien_tidak_ditemukan(client):
    response = client.get("/api/v1/queues/999")

    assert response.status_code == 404


def test_nama_pasien_tidak_valid(client):
    response = client.post(
        "/api/v1/queues",
        json={
            "nama_pasien": "A",
            "poli": "Umum",
            "keluhan": "",
        },
    )

    assert response.status_code == 422


def test_ringkasan_antrian(client):
    buat_pasien(client, "Andi")
    buat_pasien(client, "Budi")

    response = client.get("/api/v1/summary/today")
    data = response.json()

    assert response.status_code == 200
    assert data["total_antrian"] == 2
    assert data["menunggu"] == 2
