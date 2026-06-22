"""Threshold convergence test."""
import asyncio
import sys
from app.core.config import settings
from app.rag.retrieval import knowledge_qa
from app.rag.vector_store import vector_store

async def main():
    c = await vector_store.count()
    print(f"Store size: {c}")
    print(f"RAG_THRESHOLD: {settings.RAG_THRESHOLD}")
    
    if c == 0:
        print("SKIP: vector store is empty. Run test_e2e.py first.")
        return
    
    r = await knowledge_qa.ask("time complexity of insertion", similarity_threshold=None)
    print(f"chunk_count: {r['chunk_count']}")
    print(f"sources: {len(r['sources'])}")
    print(f"answer: {(r['answer'] or '')[:120]}")
    print(f"threshold in trace: {r['retrieval_trace']['threshold']}")
    
    if settings.RAG_THRESHOLD >= 0.9:
        assert r['chunk_count'] == 0, f"Expected 0 chunks with RAG_THRESHOLD={settings.RAG_THRESHOLD}, got {r['chunk_count']}"
        print("PASS: High threshold correctly filters all chunks")
    else:
        assert r['chunk_count'] > 0, f"Expected >0 chunks, got {r['chunk_count']}"
        print("PASS: Low threshold allows chunks through")

asyncio.get_event_loop().run_until_complete(main())
