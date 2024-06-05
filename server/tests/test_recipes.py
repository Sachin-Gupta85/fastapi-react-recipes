"""API tests for the Recipes service (in-memory mongomock)."""
import mongomock
import pytest
from fastapi.testclient import TestClient

from app.db import get_db
from app.main import app


@pytest.fixture
def client():
    db = mongomock.MongoClient()["testdb"]
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def _mk(client, **kw):
    body = {"title": "Dish", "ingredients": ["egg"], "steps": ["mix"], "minutes": 10, "tags": []}
    body.update(kw)
    return client.post("/api/recipes", json=body).json()


def test_create_defaults_rating_none(client):
    r = _mk(client)
    assert r["avg_rating"] is None and r["rating_count"] == 0


def test_search_ingredient_and_max_minutes(client):
    _mk(client, title="Omelette", ingredients=["egg", "cheese"], minutes=8)
    _mk(client, title="Stew", ingredients=["beef", "carrot"], minutes=90)
    assert [r["title"] for r in client.get("/api/recipes?ingredient=egg").json()] == ["Omelette"]
    assert [r["title"] for r in client.get("/api/recipes?max_minutes=30").json()] == ["Omelette"]
    assert [r["title"] for r in client.get("/api/recipes?q=stew").json()] == ["Stew"]


def test_rating_averages(client):
    rid = _mk(client)["id"]
    client.post(f"/api/recipes/{rid}/rate", json={"rating": 5})
    out = client.post(f"/api/recipes/{rid}/rate", json={"rating": 2}).json()
    assert out["rating_count"] == 2 and out["avg_rating"] == 3.5


def test_rating_bounds(client):
    rid = _mk(client)["id"]
    assert client.post(f"/api/recipes/{rid}/rate", json={"rating": 0}).status_code == 422
    assert client.post(f"/api/recipes/{rid}/rate", json={"rating": 6}).status_code == 422


def test_update_delete_404(client):
    rid = _mk(client)["id"]
    assert client.put(f"/api/recipes/{rid}", json={"title": "New", "ingredients": [], "steps": [], "minutes": 5, "tags": []}).json()["title"] == "New"
    assert client.delete(f"/api/recipes/{rid}").status_code == 204
    assert client.get(f"/api/recipes/{rid}").status_code == 404
