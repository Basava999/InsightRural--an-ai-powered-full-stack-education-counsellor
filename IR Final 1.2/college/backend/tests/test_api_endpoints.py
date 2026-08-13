# ==============================================================================
# InsightRural — API Endpoint Integration Tests
# ==============================================================================

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def test_client():
    """Create a FastAPI test client."""
    from main import app
    return TestClient(app)


class TestHealthEndpoints:
    """Test health check and metadata endpoints."""

    def test_health_check(self, test_client):
        """GET /api/health returns healthy status."""
        response = test_client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "services" in data
        assert "database" in data

    def test_branches(self, test_client):
        """GET /api/branches returns a list."""
        response = test_client.get("/api/branches")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_locations(self, test_client):
        """GET /api/locations returns a list."""
        response = test_client.get("/api/locations")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_statistics(self, test_client):
        """GET /api/statistics returns counts."""
        response = test_client.get("/api/statistics")
        assert response.status_code == 200
        data = response.json()
        assert "total_colleges" in data
        assert "total_locations" in data
        assert "total_branches" in data

    def test_ai_status(self, test_client):
        """GET /api/ai/status returns service matrix."""
        response = test_client.get("/api/ai/status")
        assert response.status_code == 200
        data = response.json()
        assert "ai_modules_available" in data
        assert "pipeline" in data

    def test_search_suggestions_short_query(self, test_client):
        """GET /api/search/suggestions with short query returns empty."""
        response = test_client.get("/api/search/suggestions?q=a")
        assert response.status_code == 200
        assert response.json() == []


class TestCollegeEndpoints:
    """Test college search and retrieval."""

    def test_colleges_list(self, test_client):
        """GET /api/colleges returns paginated list."""
        response = test_client.get("/api/colleges")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "items" in data
        assert "page" in data

    def test_colleges_with_search(self, test_client):
        """GET /api/colleges with search query."""
        response = test_client.get("/api/colleges?q=bangalore")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    def test_colleges_pagination(self, test_client):
        """GET /api/colleges with page and limit."""
        response = test_client.get("/api/colleges?page=1&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert data["limit"] == 5


class TestAdmissionEndpoints:
    """Test admission probability and prediction endpoints."""

    def test_admission_probability_valid(self, test_client):
        """POST /api/admission-probability with valid data."""
        response = test_client.post(
            "/api/admission-probability",
            json={"rank": 5000, "previous_cutoff": 10000, "category": "OPEN"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "probability" in data

    def test_admission_probability_missing_data(self, test_client):
        """POST /api/admission-probability without required fields."""
        response = test_client.post("/api/admission-probability", json={})
        assert response.status_code in (400, 422)

    def test_admission_probability_batch(self, test_client):
        """POST /api/admission-probability with multiple colleges."""
        response = test_client.post(
            "/api/admission-probability",
            json={
                "rank": 5000,
                "colleges": [
                    {"college": "RV College", "branch": "CSE", "cutoff": 3000},
                    {"college": "BMS College", "branch": "CSE", "cutoff": 6000},
                ],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["results"]) == 2


class TestSimulationEndpoints:
    """Test KEA simulation endpoints."""

    def test_simulate_valid(self, test_client):
        """POST /api/v2/simulate with valid data."""
        response = test_client.post(
            "/api/v2/simulate",
            json={
                "kcet_rank": 5000,
                "category": "GM",
                "gender": "Male",
                "branch_preference": ["CSE", "ISE"],
            },
        )
        # May be 200 or 503 depending on engine availability
        assert response.status_code in (200, 503)


class TestCareerEndpoints:
    """Test career simulation endpoints."""

    def test_simulate_career(self, test_client):
        """POST /api/simulate-career with valid data."""
        response = test_client.post(
            "/api/simulate-career",
            json={"rank": 5000, "category": "GM", "branch": "CSE"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data

    def test_simulate_career_missing_fields(self, test_client):
        """POST /api/simulate-career with missing required fields."""
        response = test_client.post("/api/simulate-career", json={"rank": 5000})
        assert response.status_code in (400, 422)


class TestReportEndpoints:
    """Test report status endpoint."""

    def test_report_status(self, test_client):
        """GET /api/report/status returns availability."""
        response = test_client.get("/api/report/status")
        assert response.status_code == 200
        data = response.json()
        assert "pdf_available" in data


class TestAuthEndpoints:
    """Test authentication endpoints."""

    def test_auth_signup_missing_fields(self, test_client):
        """POST /api/auth/signup with missing fields."""
        response = test_client.post(
            "/api/auth/signup", json={"email": "", "password": ""}
        )
        assert response.status_code in (400, 422)

    def test_auth_login_invalid_credentials(self, test_client):
        """POST /api/auth/login with invalid credentials."""
        response = test_client.post(
            "/api/auth/login",
            json={"email": "nonexistent@test.com", "password": "wrong"},
        )
        assert response.status_code in (401, 500)

    def test_auth_me_no_token(self, test_client):
        """GET /api/auth/me without token returns 401."""
        response = test_client.get("/api/auth/me")
        assert response.status_code in (401, 422)


class TestRiskEndpoints:
    """Test risk analyzer endpoints."""

    def test_risk_analysis(self, test_client):
        """POST /api/analyze/risk with valid data."""
        response = test_client.post(
            "/api/analyze/risk",
            json={
                "exam": "KCET",
                "rank": 5000,
                "category": "GM",
                "branch": "CSE",
                "interests": ["coding", "programming"],
                "income": 500000,
            },
        )
        # May be 200 or 503 depending on risk analyzer availability
        assert response.status_code in (200, 503)
