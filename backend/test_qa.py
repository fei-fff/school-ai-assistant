"""System QA — automated acceptance test suite."""
import uuid, json
from fastapi.testclient import TestClient
from app.main import app

c = TestClient(app)
PASS, FAIL, WARN = 0, 0, 0

def check(label, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1; print(f"  [PASS] {label}")
    else:
        FAIL += 1; print(f"  [FAIL] {label}  — {detail}")

def warn(label, detail=""):
    global WARN
    WARN += 1; print(f"  [WARN] {label}  — {detail}")

def register(u, role):
    return c.post("/api/v1/auth/register", json={"username":u,"email":u+"@t.com","password":"123456","confirm_password":"123456","role":role})

def login(u):
    r = c.post("/api/v1/auth/login", json={"username":u,"password":"123456"})
    return r.json()["data"]["access_token"] if r.status_code == 200 else None

# ───── 1. AUTH ─────
print("="*50); print("1. AUTH SYSTEM"); print("="*50)
u1 = "qa_auth_" + uuid.uuid4().hex[:4]
r = register(u1, "student")
check("Register", r.status_code in (200,201), f"status={r.status_code}")
t1 = login(u1)
check("Login returns token", t1 is not None and len(t1) > 20)
check("Token starts with eyJ", t1 and t1.startswith("eyJ"))
r = c.get("/api/v1/auth/me", headers={"Authorization":"Bearer "+t1})
check("GET /me with valid token", r.status_code == 200)
r = c.get("/api/v1/auth/me")
check("GET /me without token → 403", r.status_code == 403)

# ───── 2. PERMISSIONS ─────
print("="*50); print("2. PERMISSIONS"); print("="*50)
su = "qa_stu_" + uuid.uuid4().hex[:4]; register(su, "student"); st = login(su); sh = {"Authorization":"Bearer "+st}
tu = "qa_tch_" + uuid.uuid4().hex[:4]; register(tu, "teacher"); tt = login(tu); th = {"Authorization":"Bearer "+tt}
r = c.post("/api/v1/mentor/me", json={"real_name":"Dr.T"}, headers=th)
check("Teacher creates card", r.status_code == 200, r.json().get("message",""))
r = c.post("/api/v1/mentor/me", json={"real_name":"Hack"}, headers=sh)
check("Student cannot create card", r.status_code != 200, f"status={r.status_code}")
r = c.get("/api/v1/mentor/list", headers=sh)
check("Student can list mentors", r.status_code == 200)
r = c.put("/api/v1/mentor/me", json={"real_name":"Hack"}, headers=sh)
check("Student cannot update card", r.status_code != 200, f"status={r.status_code}")

# ───── 3. MENTOR ─────
print("="*50); print("3. MENTOR SYSTEM"); print("="*50)
r = c.get("/api/v1/mentor/me", headers=th)
check("GET my card", r.status_code == 200)
check("Card has data", r.json().get("data") is not None)
r = c.put("/api/v1/mentor/me", json={"title":"Professor"}, headers=th)
check("Update my card", r.status_code == 200)
r = c.get("/api/v1/mentor/colleges", headers=sh)
check("List colleges", r.status_code == 200 and len(r.json().get("data",[])) > 0)
r = c.get("/api/v1/mentor/recommend?query=AI", headers=sh)
check("Recommend mentors", r.status_code == 200)

# ───── 4. EMOTION AI ─────
print("="*50); print("4. EMOTION AI"); print("="*50)
r = c.post("/api/v1/emotion/chat", json={"message":"I am so stressed"}, headers=sh)
check("Emotion chat returns", r.status_code == 200)
d = r.json().get("data",{})
check("Emotion detected", d.get("emotion") in ("stress","negative","neutral","positive"), d.get("emotion"))
check("Answer non-empty", bool(d.get("answer")))

# ───── 5. RAG ─────
print("="*50); print("5. RAG SYSTEM"); print("="*50)
# Upload + process a document
files = {"file":("qa_rb.txt",b"Red-Black Tree time complexity is O(log n). Insertion and deletion are both O(log n).","text/plain")}
r = c.post("/api/v1/knowledge/upload", files=files, params={"title":"QA RB Test"}, headers=th)
check("Upload document", r.status_code in (200,201))
if r.status_code in (200,201):
    doc_id = r.json()["data"]["id"]
    r = c.post(f"/api/v1/knowledge/process/{doc_id}", headers=th)
    check("Process document", r.status_code == 200)
    d2 = r.json().get("data",{})
    check("Parser success", d2.get("parse_status")=="success", d2.get("parse_status"))
    check("Summary success", d2.get("summary_status")=="success", d2.get("summary_status"))
    check("Classify success", d2.get("classify_status")=="success", d2.get("classify_status"))
    check("Embedding success", d2.get("embedding_status")=="success", d2.get("embedding_status"))
    r = c.post("/api/v1/knowledge/query?question=time+complexity&top_k=3", headers=sh)
    check("QA returns answer", r.status_code == 200)
    qd = r.json().get("data",{})
    check("QA has chunk_count > 0", qd.get("chunk_count",0) > 0)
    check("QA has retrieval_trace", qd.get("retrieval_trace") is not None)
    # Test high threshold
    r = c.post(f"/api/v1/knowledge/query?question=time+complexity&similarity_threshold=0.95", headers=sh)
    check("High threshold → chunk_count=0", r.json().get("data",{}).get("chunk_count",0) == 0)

# ───── 6. USER PROFILE ─────
print("="*50); print("6. USER PROFILE"); print("="*50)
r = c.post("/api/v1/chat", json={"message":"I am stressed about exams","history":[]}, headers=sh)
check("Chat triggers profile update", r.status_code == 200)
import time; time.sleep(0.3)
r = c.get("/api/v1/user/profile/update", json={}, headers=sh)
uid = json.loads(r.text) if r.status_code != 200 else 0
# Find user id for profile check
r2 = c.get("/api/v1/auth/me", headers=sh)
if r2.status_code == 200:
    uid2 = r2.json()["data"]["id"]
    r = c.get(f"/api/v1/user/profile/{uid2}", headers=sh)
    check("Profile exists", r.status_code == 200)
    check("Profile has data", r.json().get("data",{}).get("emotion_state") or r.json().get("data",{}).get("frequent_topics"))

# ───── 7. UNIFIED CHAT ─────
print("="*50); print("7. UNIFIED CHAT"); print("="*50)
tests = [("I am stressed","emotion"),("recommend AI mentor","mentor"),("what is O(log n)","knowledge")]
for msg, exp in tests:
    r = c.post("/api/v1/chat", json={"message":msg}, headers=sh)
    check(f"Intent for '{msg[:20]}' → {exp}", r.json().get("data",{}).get("intent")==exp,
          f"got {r.json().get('data',{}).get('intent')}")
# Multi-turn
h = [{"role":"user","content":"I am stressed"},{"role":"assistant","content":"I understand"}]
r = c.post("/api/v1/chat", json={"message":"what can I do","history":h}, headers=sh)
check("Multi-turn with history", r.status_code == 200 and bool(r.json().get("data",{}).get("answer")))

# ───── 8. PERSISTENCE ─────
print("="*50); print("8. PERSISTENCE"); print("="*50)
r = c.get("/api/v1/mentor/colleges", headers=sh)
check("Colleges persist across requests", r.status_code == 200 and len(r.json().get("data",[])) >= 10)
r = c.get(f"/api/v1/user/profile/{uid2}", headers=sh)
check("Profile persists", r.status_code == 200)

# ───── SUMMARY ─────
print("="*50)
print(f"\nRESULTS: {PASS} passed, {FAIL} failed, {WARN} warnings\n")
if FAIL == 0:
    print(">>> ALL CHECKS PASSED <<<")
else:
    print(f">>> {FAIL} ISSUES FOUND <<<")
