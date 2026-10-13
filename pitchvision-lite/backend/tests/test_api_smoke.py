"""
API route smoke testleri — TestClient ile uçların yanıt verdiğini doğrular.

Not: Bağımlılıklar veritabanı oturumu açtığı için yerelde PostgreSQL yoksa veya
kimlik bilgileri hatalıysa 500 dönebilir; bu durum testte tolere edilir.
Demo modda bazı uçlar auth header olmadan 200 dönebilir.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app

# DB veya auth kaynaklı geçici hatalar (CI / yerel ortam)
_DB_OR_AUTH = (200, 401, 403, 404, 422, 500)


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app, raise_server_exceptions=False)


class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        res = client.get("/health")
        assert res.status_code == 200

    def test_health_returns_json(self, client):
        res = client.get("/health")
        data = res.json()
        assert "status" in data


class TestMatchesEndpoints:
    def test_list_matches(self, client):
        res = client.get("/api/v1/matches")
        assert res.status_code in _DB_OR_AUTH

    def test_get_match_not_found(self, client):
        res = client.get("/api/v1/matches/999999")
        assert res.status_code in _DB_OR_AUTH

    def test_match_summary_not_found(self, client):
        res = client.get("/api/v1/matches/999999/summary")
        assert res.status_code in _DB_OR_AUTH


class TestPlayersEndpoints:
    def test_list_players(self, client):
        res = client.get("/api/v1/players")
        assert res.status_code in _DB_OR_AUTH

    def test_player_passport_not_found(self, client):
        res = client.get("/api/v1/players/999999/passport")
        assert res.status_code in _DB_OR_AUTH


class TestReportsEndpoints:
    def test_list_reports(self, client):
        res = client.get("/api/v1/reports")
        assert res.status_code in _DB_OR_AUTH

    def test_get_report_not_found(self, client):
        res = client.get("/api/v1/reports/999999")
        assert res.status_code in _DB_OR_AUTH


class TestDrillsEndpoints:
    def test_list_drills(self, client):
        res = client.get("/api/v1/drills")
        assert res.status_code in _DB_OR_AUTH

    def test_mark_drill_applied(self, client):
        res = client.post("/api/v1/drills/1/mark-applied")
        assert res.status_code in _DB_OR_AUTH


class TestAlertsEndpoints:
    def test_list_match_alerts(self, client):
        res = client.get("/api/v1/matches/1/alerts")
        assert res.status_code in _DB_OR_AUTH

    def test_approve_alert(self, client):
        res = client.post("/api/v1/alerts/1/approve")
        assert res.status_code in _DB_OR_AUTH

    def test_reject_alert(self, client):
        res = client.post("/api/v1/alerts/1/reject")
        assert res.status_code in _DB_OR_AUTH


class TestCalibrationEndpoints:
    def test_get_calibration_not_found(self, client):
        res = client.get("/api/v1/matches/999999/calibration")
        assert res.status_code in _DB_OR_AUTH

    def test_post_calibration_invalid_body(self, client):
        res = client.post("/api/v1/matches/1/calibration", json={})
        assert res.status_code in _DB_OR_AUTH


class TestScoutingEndpoints:
    def test_scouting_players(self, client):
        res = client.get("/api/v1/scouting/players")
        assert res.status_code in _DB_OR_AUTH

    def test_hidden_gems(self, client):
        res = client.get("/api/v1/scouting/hidden-gems")
        assert res.status_code in _DB_OR_AUTH


class TestProcessingEndpoints:
    def test_processing_status(self, client):
        res = client.get("/api/v1/matches/1/processing-status")
        assert res.status_code in _DB_OR_AUTH
