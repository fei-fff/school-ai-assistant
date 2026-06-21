"""E2E test: verify RAG pipeline end-to-end without a running server."""
import asyncio
import io
import sys
import uuid

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
print("=== RAG E2E TEST ===")

# ─── Step 1: Register teacher ───
uname = "e2e_" + uuid.uuid4().hex[:6]
r = client.post(
    "/api/v1/auth/register",
    json={
        "username": uname,
        "email": uname + "@test.edu",
        "password": "123456",
        "confirm_password": "123456",
        "role": "teacher",
    },
)
assert r.status_code in (200, 201), f"Register failed: {r.text[:200]}"
print(f"[OK] Step 1 - Register: {uname}")

# ─── Step 2: Login ───
r = client.post("/api/v1/auth/login", json={"username": uname, "password": "123456"})
assert r.status_code == 200, f"Login failed: {r.text[:200]}"
token = r.json()["data"]["access_token"]
headers = {"Authorization": "Bearer " + token}
print(f"[OK] Step 2 - Login: token={token[:20]}...")

# ─── Step 3: Upload document ───
test_content = (
    b"Red-Black Tree is a self-balancing BST.\n"
    b"Insert: O(log n) time complexity.\n"
    b"Delete: O(log n) time complexity.\n"
    b"Used in C++ STL map, Java TreeMap, Linux CFS.\n"
)
files = {"file": ("test_rb.txt", io.BytesIO(test_content), "text/plain")}
r = client.post(
    "/api/v1/knowledge/upload",
    files=files,
    params={"title": "Red-Black Tree Notes"},
    headers=headers,
)
data = r.json()
assert r.status_code in (200, 201), f"Upload failed: {r.text[:200]}"
doc_id = data["data"]["id"]
print(f"[OK] Step 3 - Upload: doc_id={doc_id}")

# ─── Step 4: Trigger pipeline ───
r = client.post(f"/api/v1/knowledge/process/{doc_id}", headers=headers)
data = r.json()
process_result = data.get("data", {})
print(f"[OK] Step 4 - Process: http={r.status_code}")
statuses = {
    k: process_result.get(k)
    for k in ["parse_status", "summary_status", "classify_status", "embedding_status"]
}
print(f"  current_step: {process_result.get('current_step')}")
print(f"  statuses: {statuses}")
all_ok = all(v == "success" for v in statuses.values())

# ─── Step 5: Knowledge QA ───
r = client.post(
    "/api/v1/knowledge/query",
    params={"question": "time complexity of insertion", "top_k": 3, "similarity_threshold": 0.1},
    headers=headers,
)
qa_data = r.json().get("data", {})
print(f"[OK] Step 5 - QA: http={r.status_code}")
print(f"  answer: {(qa_data.get('answer') or '')[:100]}")
print(f"  chunk_count: {qa_data.get('chunk_count', 0)}")
print(f"  sources: {len(qa_data.get('sources', []))}")
if qa_data.get("sources"):
    s = qa_data["sources"][0]
    print(f"  top source: score={s.get('score', 0):.4f} doc_id={s.get('document_id', '?')}")

# ─── Step 6: Verify document status ───
r = client.get(f"/api/v1/knowledge/documents/{doc_id}/status", headers=headers)
doc_status = r.json().get("data", {})
print(f"[OK] Step 6 - Status: step={doc_status.get('current_step')}")
print(f"  error_message: {doc_status.get('error_message') or '(none)'}")

# ─── Verify vector store ───
from app.rag.vector_store import vector_store
count = asyncio.get_event_loop().run_until_complete(vector_store.count())
print(f"[OK] Step 7 - Vector store: {count} chunks stored")

# ─── Summary ───
print()
print("=== SUMMARY ===")
print(f"  Pipeline all-success: {all_ok}")
print(f"  QA returned answer:  {bool(qa_data.get('answer'))}")
print(f"  QA has sources:      {len(qa_data.get('sources', [])) > 0}")
print(f"  Vector chunks exist: {count > 0}")
print(f"  Document step:       {doc_status.get('current_step')}")

if all_ok and qa_data.get("answer") and count > 0:
    print("\n>>> VERDICT: RAG pipeline is fully functional. <<<")
else:
    print("\n>>> VERDICT: Some issues found (see above). <<<")
    sys.exit(1)
