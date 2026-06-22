"""Test mentor recommendation."""
import uuid
from fastapi.testclient import TestClient
from app.main import app

c = TestClient(app)
u = "rec_" + uuid.uuid4().hex[:4]

# Register two teachers with cards
c.post("/api/v1/auth/register", json={"username": u, "email": u + "@t.com", "password": "1", "confirm_password": "1", "role": "teacher"})
r = c.post("/api/v1/auth/login", json={"username": u, "password": "1"})
t = r.json()["data"]["access_token"]
h = {"Authorization": "Bearer " + t}
c.post("/api/v1/mentor/me", json={"real_name": "Dr.AI", "research_direction": "AI, deep learning, NLP", "introduction": "Expert in AI and machine learning.", "college_id": 1}, headers=h)

v = u + "_2"
c.post("/api/v1/auth/register", json={"username": v, "email": v + "@t.com", "password": "1", "confirm_password": "1", "role": "teacher"})
r2 = c.post("/api/v1/auth/login", json={"username": v, "password": "1"})
h2 = {"Authorization": "Bearer " + r2.json()["data"]["access_token"]}
c.post("/api/v1/mentor/me", json={"real_name": "Dr.DB", "research_direction": "database systems, SQL", "introduction": "Expert in distributed databases.", "college_id": 2}, headers=h2)

# Test 1: query=ai, no college
r = c.get("/api/v1/mentor/recommend?query=ai", headers=h)
print("Test 1 - query=ai, no college:")
for x in r.json()["data"]:
    print(f"  {x['name']} score={x['score']} [{x['match_reason']}]")

# Test 2: query=database, college_id=2
r = c.get("/api/v1/mentor/recommend?query=database&college_id=2", headers=h)
print("Test 2 - query=database, college=2:")
for x in r.json()["data"]:
    print(f"  {x['name']} score={x['score']} [{x['match_reason']}]")

# Test 3: query=python (no match)
r = c.get("/api/v1/mentor/recommend?query=python", headers=h)
print(f"Test 3 - query=python: {len(r.json()['data'])} results")
