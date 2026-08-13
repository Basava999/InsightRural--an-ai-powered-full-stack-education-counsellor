"""API endpoint tests."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


def test_recommend_endpoint():
    r = client.post("/api/v1/predict/recommend", json={
        "rank": 5000, "category": "GM", "branch": "CSE", "city": "Bangalore"
    })
    assert r.status_code == 200
    data = r.json()
    assert "safe" in data
    assert "confidence" in data
    assert data["engine_version"] == "3.0.0"


def test_city_constraint():
    r = client.post("/api/v1/predict/recommend", json={
        "rank": 8000, "category": "GM", "branch": "CSE", "city": "Bangalore"
    })
    data = r.json()
    all_recs = data["safe"] + data["moderate"] + data["ambitious"]
    for rec in all_recs:
        loc = rec["location"].lower()
        assert "bangalore" in loc or "bengaluru" in loc


def test_chat_endpoint():
    r = client.post("/api/v1/chat/", json={
        "message": "My rank is 5000, suggest CSE colleges in Bangalore",
        "profile": {"rank": 5000, "category": "GM", "branch": "CSE", "city": "Bangalore"}
    })
    assert r.status_code == 200
    assert "answer" in r.json()
    assert r.json()["engine_used"].startswith("deterministic")
