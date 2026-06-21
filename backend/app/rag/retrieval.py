"""Knowledge QA pipeline — standardized RAG retrieval with explainable traces.

Output: { answer, sources, scores, chunk_count, context_used, retrieval_trace }
"""

import logging
import math
import re
from typing import Any

from app.ai.service import ai_service
from app.core.config import settings
from app.rag.vector_store import VectorStore, SearchResult, vector_store

logger = logging.getLogger(__name__)


def _debug_log(msg: str, *args: Any) -> None:
    if settings.RAG_DEBUG:
        logger.info("[RAG_DEBUG] " + msg, *args)


def _vector_norm(vec: list[float]) -> float:
    return math.sqrt(sum(v * v for v in vec))


def _get_effective_threshold() -> float:
    if settings.RAG_MIN_THRESHOLD > 0:
        return settings.RAG_MIN_THRESHOLD
    emb = settings.EMBEDDING_PROVIDER
    if emb in ("mock", "deepseek"):
        return 0.15
    elif emb == "openai":
        return 0.30
    return 0.20


def _threshold_source(similarity_threshold: float | None) -> str:
    if similarity_threshold is not None:
        return "manual"
    if settings.RAG_MIN_THRESHOLD > 0:
        return f"env(RAG_MIN_THRESHOLD={settings.RAG_MIN_THRESHOLD})"
    return f"provider_default({settings.EMBEDDING_PROVIDER})"


class KnowledgeQA:

    def __init__(self, store: VectorStore | None = None):
        self._store = store or vector_store

    async def ask(
        self, query: str, top_k: int = 5, *,
        similarity_threshold: float | None = None,
        history: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        effective_threshold = (
            similarity_threshold if similarity_threshold is not None
            else _get_effective_threshold()
        )

        store_details = await self._store.get_details()
        store_size = store_details.get("total_chunks", 0)

        if store_size == 0:
            return self._empty_response(query, effective_threshold, store_details)

        query_vectors = await ai_service.embed([query])
        query_embedding = query_vectors[0]
        q_norm = _vector_norm(query_embedding)

        results = await self._store.search(query_embedding, top_k=top_k)
        filtered, rejected = self._apply_threshold(results, effective_threshold)

        if not filtered:
            return self._no_match_response(query, results, effective_threshold, store_details, q_norm)

        context = self._build_context(filtered)
        answer = await ai_service.knowledge_chat(question=query, context=context, history=history)

        return self._build_response(answer, query, results, filtered, rejected,
                                     effective_threshold, _threshold_source(similarity_threshold),
                                     store_details, q_norm, query_embedding, context)

    async def is_ready(self) -> bool:
        return await self._store.count() > 0

    # ── Helpers ─────────────────────────────────

    @staticmethod
    def _apply_threshold(results: list[SearchResult], threshold: float):
        filtered = [r for r in results if r.score >= threshold]
        rejected = []
        for r in results:
            if r.score < threshold:
                rejected.append({
                    "chunk_id": r.chunk.id,
                    "score": round(r.score, 6),
                    "threshold": threshold,
                    "reason": f"score {r.score:.6f} < threshold {threshold}",
                    "content_preview": r.chunk.content[:100],
                })
        return filtered, rejected

    @staticmethod
    def _build_context(results: list[SearchResult]) -> str:
        parts = []
        for i, r in enumerate(results, 1):
            doc_id = r.chunk.document_id
            title = r.chunk.metadata.get("title", "unknown")
            parts.append(f"[Source {i} | Doc: {title} (ID:{doc_id})]\n{r.chunk.content}")
        return "\n\n---\n\n".join(parts)

    def _empty_response(self, query, threshold, store_details):
        return {
            "answer": "Knowledge base is empty. Upload and process a document first.",
            "sources": [],
            "scores": [],
            "chunk_count": 0,
            "context_used": "",
            "retrieval_trace": {
                "query": query,
                "embedding_model": settings.EMBEDDING_PROVIDER,
                "embedding_dim": settings.EMBEDDING_DIMENSION,
                "vector_store_type": store_details.get("backend", "unknown"),
                "vector_store_size": 0,
                "query_vector_norm": 0.0,
                "top_k_raw": [],
                "filtered_chunks": [],
                "rejected_chunks": [],
                "similarity_scores": [],
                "threshold": threshold,
                "threshold_source": _threshold_source(None),
                "final_context": [],
                "error": "vector_store_empty",
            },
        }

    def _no_match_response(self, query, results, threshold, store_details, q_norm):
        _, rejected = self._apply_threshold(results, threshold)
        return {
            "answer": "No matching content found. Try rephrasing or lower the threshold.",
            "sources": [],
            "scores": [],
            "chunk_count": 0,
            "context_used": "",
            "retrieval_trace": {
                "query": query,
                "embedding_model": settings.EMBEDDING_PROVIDER,
                "embedding_dim": settings.EMBEDDING_DIMENSION,
                "vector_store_type": store_details.get("backend", "unknown"),
                "vector_store_size": store_details.get("total_chunks", 0),
                "query_vector_norm": round(q_norm, 6),
                "top_k_raw": [{"chunk_id": r.chunk.id, "score": round(r.score, 6)} for r in results],
                "filtered_chunks": [],
                "rejected_chunks": rejected,
                "similarity_scores": [round(r.score, 6) for r in results],
                "threshold": threshold,
                "threshold_source": _threshold_source(None),
                "final_context": [],
                "error": "all_chunks_filtered",
            },
        }

    def _build_response(self, answer, query, results, filtered, rejected,
                        threshold, threshold_source, store_details, q_norm,
                        query_embedding, context):
        sources = [r.to_dict() for r in filtered]
        scores = [round(r.score, 4) for r in filtered]
        q_preview = [round(x, 6) for x in query_embedding[:10]]

        return {
            "answer": answer,
            "sources": sources,
            "scores": scores,
            "chunk_count": len(filtered),
            "context_used": context,
            "retrieval_trace": {
                "query": query,
                "embedding_model": settings.EMBEDDING_PROVIDER,
                "embedding_dim": settings.EMBEDDING_DIMENSION,
                "vector_store_type": store_details.get("backend", "unknown"),
                "vector_store_size": store_details.get("total_chunks", 0),
                "query_vector_norm": round(q_norm, 6),
                "query_vector_sample": q_preview,
                "top_k_raw": [{
                    "chunk_id": r.chunk.id,
                    "score": round(r.score, 6),
                    "chunk_norm": round(_vector_norm(r.chunk.embedding), 6),
                    "document_id": r.chunk.document_id,
                    "content_preview": r.chunk.content[:120],
                } for r in results],
                "filtered_chunks": [{
                    "chunk_id": r.chunk.id,
                    "score": round(r.score, 4),
                    "document_id": r.chunk.document_id,
                    "document_title": r.chunk.metadata.get("title", "unknown"),
                } for r in filtered],
                "rejected_chunks": rejected,
                "similarity_scores": sorted([round(r.score, 6) for r in results], reverse=True),
                "threshold": threshold,
                "threshold_source": threshold_source,
                "final_context": context.split("\n\n---\n\n") if context else [],
            },
        }


_STOP_WORDS = {"the","a","an","is","are","was","were","be","been","of","in","to","for","with","on","at","by","from","this","that","it","and","or","but","not","no"}


def _extract_keywords(text: str, min_len: int = 2) -> set[str]:
    tokens = set()
    for w in re.findall(r"[a-zA-Z0-9_+\-*/=<>.]{2,}", text):
        wl = w.lower()
        if len(wl) >= min_len and wl not in _STOP_WORDS:
            tokens.add(wl)
    return tokens


knowledge_qa = KnowledgeQA()
