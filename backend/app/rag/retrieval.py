"""Knowledge QA pipeline — config-driven, single-threshold RAG retrieval."""

import logging
import math
from typing import Any

from app.ai.service import ai_service
from app.core.config import settings
from app.rag.vector_store import VectorStore, SearchResult, vector_store

logger = logging.getLogger(__name__)


def _vector_norm(vec: list[float]) -> float:
    return math.sqrt(sum(v * v for v in vec))


class KnowledgeQA:

    def __init__(self, store: VectorStore | None = None):
        self._store = store or vector_store

    async def ask(
        self, query: str, top_k: int | None = None, *,
        similarity_threshold: float | None = None,
        history: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        top_k = top_k or settings.RAG_TOP_K
        threshold = similarity_threshold if similarity_threshold is not None else settings.RAG_THRESHOLD

        store_details = await self._store.get_details()
        store_size = store_details.get("total_chunks", 0)

        if store_size == 0:
            return self._empty_response(query, threshold, store_details)

        query_vectors = await ai_service.embed([query])
        query_embedding = query_vectors[0]
        q_norm = _vector_norm(query_embedding)
        results = await self._store.search(query_embedding, top_k=top_k)
        filtered, rejected = self._apply_threshold(results, threshold)

        if not filtered:
            return self._no_match_response(query, results, threshold, store_details, q_norm)

        context = self._build_context(filtered)
        answer = await ai_service.knowledge_chat(question=query, context=context, history=history)
        return self._build_response(answer, query, results, filtered, rejected,
                                     threshold, store_details, q_norm, query_embedding, context)

    async def is_ready(self) -> bool:
        return await self._store.count() > 0

    @staticmethod
    def _apply_threshold(results, threshold):
        filtered = [r for r in results if r.score >= threshold]
        rejected = [dict(chunk_id=r.chunk.id, score=round(r.score, 6), threshold=threshold,
                         reason=f"score {r.score:.6f} < threshold {threshold}")
                    for r in results if r.score < threshold]
        return filtered, rejected

    @staticmethod
    def _build_context(results):
        return "\n\n---\n\n".join(
            f"[Source {i} | Doc: {r.chunk.metadata.get('title','unknown')} "
            f"(ID:{r.chunk.document_id})]\n{r.chunk.content}"
            for i, r in enumerate(results, 1))

    def _empty_response(self, query, threshold, store_details):
        tr = self._trace_base(query, threshold, store_details, error="vector_store_empty")
        return dict(answer="Knowledge base is empty.", sources=[], scores=[],
                    chunk_count=0, context_used="", retrieval_trace=tr)

    def _no_match_response(self, query, results, threshold, store_details, q_norm):
        _, rejected = self._apply_threshold(results, threshold)
        raw = [dict(chunk_id=r.chunk.id, score=round(r.score, 6)) for r in results]
        tr = self._trace_base(query, threshold, store_details, q_norm=q_norm,
                              raw=raw, rejected=rejected, error="all_chunks_filtered")
        return dict(answer="No matching content found.", sources=[], scores=[],
                    chunk_count=0, context_used="", retrieval_trace=tr)

    def _build_response(self, answer, query, results, filtered, rejected,
                        threshold, store_details, q_norm, query_embedding, context):
        raw_trace = [dict(chunk_id=r.chunk.id, score=round(r.score, 6),
                          chunk_norm=round(_vector_norm(r.chunk.embedding), 6),
                          document_id=r.chunk.document_id,
                          content_preview=r.chunk.content[:120]) for r in results]
        filtered_trace = [dict(chunk_id=r.chunk.id, score=round(r.score, 4),
                               document_id=r.chunk.document_id,
                               document_title=r.chunk.metadata.get("title", "unknown"))
                          for r in filtered]
        tr = self._trace_base(query, threshold, store_details, q_norm=q_norm,
                              raw=raw_trace, filtered=filtered_trace, rejected=rejected)
        tr["final_context"] = context.split("\n\n---\n\n") if context else []
        return dict(answer=answer, sources=[r.to_dict() for r in filtered],
                    scores=[round(r.score, 4) for r in filtered], chunk_count=len(filtered),
                    context_used=context, retrieval_trace=tr)

    @staticmethod
    def _trace_base(query, threshold, store_details, *, q_norm=0.0, raw=None,
                    filtered=None, rejected=None, error=None):
        result = dict(
            query=query,
            embedding_model=settings.EMBEDDING_PROVIDER,
            embedding_dim=settings.EMBEDDING_DIMENSION,
            vector_store_type=store_details.get("backend", "unknown"),
            vector_store_size=store_details.get("total_chunks", 0),
            query_vector_norm=round(q_norm, 6),
            threshold_used=threshold,
            raw_count=len(raw) if raw else 0,
            filtered_count=len(filtered) if filtered else 0,
            raw_scores=sorted([r["score"] for r in (raw or [])], reverse=True),
            top_k_raw=raw or [],
            filtered_chunks=filtered or [],
            rejected_chunks=rejected or [],
            similarity_scores=sorted([r["score"] for r in (raw or [])], reverse=True),
            threshold=threshold,
        )
        if error:
            result["error"] = error
        return result


knowledge_qa = KnowledgeQA()
