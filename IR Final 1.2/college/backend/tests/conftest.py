# ==============================================================================
# InsightRural — Test Configuration & Fixtures
# ==============================================================================

import sys
import os
import pytest

# Ensure backend is on path
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)


@pytest.fixture(scope="session")
def app():
    """Create FastAPI test app."""
    from main import app as fastapi_app
    return fastapi_app


@pytest.fixture(scope="session")
def client(app):
    """Create test client for FastAPI app."""
    from fastapi.testclient import TestClient
    return TestClient(app)


@pytest.fixture
def sample_student_profile():
    """Standard student profile for testing."""
    return {
        "kcet_rank": 5000,
        "category": "GM",
        "gender": "Male",
        "branch": "CSE",
        "budget": 100000,
        "hostel_needed": False,
        "location_preference": "Bangalore",
        "income": 500000,
    }


@pytest.fixture
def sample_jee_profile():
    """JEE student profile for testing."""
    return {
        "jee_main_rank": 15000,
        "category": "OPEN",
        "preferred_branches": ["CSE", "ECE"],
        "gender": "Male",
    }


@pytest.fixture
def sample_neet_profile():
    """NEET student profile for testing."""
    return {
        "neet_rank": 20000,
        "category": "OBC",
        "preferred_courses": ["MBBS"],
        "gender": "Female",
        "state": "Karnataka",
    }
