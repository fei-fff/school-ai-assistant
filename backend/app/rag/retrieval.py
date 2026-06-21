"""Knowledge QA pipeline — retrieval-augmented generation closed loop."""

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
    """Determine similarity threshold based on embedding provider.

    Priority: .env RAG_MIN_THRESHOLD > provider default.
    - mock / deepseek (hash-based embedding) → 0.15
    - openai (real embedding) → 0.30
    - else → 0.20
    """
    if settings.RAG_MIN_THRESHOLD > 0:
        return settings.RAG_MIN_THRESHOLD

    emb = settings.EMBEDDING_PROVIDER
    if emb in ("mock", "deepseek"):
        return 0.15
    elif emb == "openai":
        return 0.30
    else:
        return 0.20


class KnowledgeQA:
    def __init__(self, store: VectorStore | None = None):
        self._store = store or vector_store

    async def ask(
        self, query: str, top_k: int = 5, *,
        similarity_threshold: float | None = None,
        history: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        # Determine effective threshold
        effective_threshold = similarity_threshold if similarity_threshold is not None else _get_effective_threshold()
        logger.info(
            "KnowledgeQA: provider=%s, RAG_MIN_THRESHOLD=%.4f, effective_threshold=%.4f",
            settings.EMBEDDING_PROVIDER, settings.RAG_MIN_THRESHOLD, effective_threshold,
        )

        # Stage 0: Store diagnostics
        store_details = await self._store.get_details()
        store_size = store_details.get("total_chunks", 0)
        _debug_log("STORE state: %s", store_details)

        if store_size == 0:
            return {
                "answer": "知识库中未找到与您问题相关的内容，请尝试换一种方式提问。",
                "sources": [], "scores": [], "context_used": "", "chunk_count": 0,
                "retrieval_trace": {},
                "debug_trace": {"store_size": 0, "store_details": store_details, "error": "vector store is empty"},
            }

        # Stage 1: Query embedding
        _debug_log("STAGE1: embedding query len=%d", len(query))
        query_vectors = await ai_service.embed([query])
        query_embedding = query_vectors[0]
        q_norm = _vector_norm(query_embedding)
        q_preview = [round(x, 6) for x in query_embedding[:10]]
        _debug_log("Query vec: dim=%d norm=%.6f", len(query_embedding), q_norm)
        if q_norm == 0.0:
            _debug_log("WARNING: query vector norm is ZERO")

        # Stage 2: Vector search
        _debug_log("STAGE2: search top_k=%d", top_k)
        results = await self._store.search(query_embedding, top_k=top_k)
        _debug_log("Raw results: %d", len(results))
        for i, r in enumerate(results):
            cn = _vector_norm(r.chunk.embedding)
            _debug_log("  [%d] chunk=%s score=%.6f chunk_norm=%.6f", i, r.chunk.id, r.score, cn)

        # Stage 3: Threshold filter
        before_count = len(results)
        filtered = [r for r in results if r.score >= effective_threshold]
        after_count = len(filtered)
        rejected = [r for r in results if r.score < effective_threshold]
        _debug_log("STAGE3: threshold=%.4f (provider=%s) before=%d after=%d rejected=%d",
                    effective_threshold, settings.EMBEDDING_PROVIDER, before_count, after_count, len(rejected))
        for r in rejected:
            _debug_log("  REJECTED chunk=%s score=%.6f < %.4f", r.chunk.id, r.score, effective_threshold)
        if after_count == 0 and before_count > 0:
            best = max(results, key=lambda r: r.score)
            logger.warning(
                "ALL CHUNKS FILTERED. Best=%.6f < threshold=%.4f (provider=%s). "
                "Set RAG_MIN_THRESHOLD=%.4f in .env or lower similarity_threshold.",
                best.score, effective_threshold, settings.EMBEDDING_PROVIDER, best.score,
            )

        # Build debug_trace
        debug_trace = {
            "query_text": query[:200],
            "query_vector_norm": round(q_norm, 6),
            "query_vector_dim": len(query_embedding),
            "query_vector_sample": q_preview,
            "top_k_raw": [{"chunk_id": r.chunk.id, "score": round(r.score, 6),
                            "chunk_norm": round(_vector_norm(r.chunk.embedding), 6)}
                           for r in results],
            "threshold": effective_threshold,
            "threshold_source": "env" if similarity_threshold is None and settings.RAG_MIN_THRESHOLD > 0
                                else ("provider_" + settings.EMBEDDING_PROVIDER)
                                if similarity_threshold is None else "manual",
            "provider_type": settings.EMBEDDING_PROVIDER,
            "before_filter_count": before_count,
            "after_filter_count": after_count,
            "rejected_count": len(rejected),
            "rejected_scores": [round(r.score, 6) for r in rejected[:10]],
            "vector_store_size": store_size,
            "vector_store_details": store_details,
        }

        retrieval_trace = self._build_retrieval_trace(query, results, filtered)

        if not filtered:
            return {
                "answer": "知识库中未找到与您问题相关的内容，请尝试换一种方式提问。",
                "sources": [], "scores": [], "context_used": "", "chunk_count": 0,
                "retrieval_trace": retrieval_trace,
                "debug_trace": debug_trace,
            }

        # Stage 4: Context + Generate
        _debug_log("STAGE4: context from %d chunks", after_count)
        context = self._build_context(filtered)
        answer = await ai_service.knowledge_chat(question=query, context=context, history=history)

        sources = [r.to_dict() for r in filtered]
        scores = [round(r.score, 4) for r in filtered]

        return {
            "answer": answer, "sources": sources, "scores": scores,
            "context_used": context, "chunk_count": after_count,
            "retrieval_trace": retrieval_trace, "debug_trace": debug_trace,
        }

    async def is_ready(self) -> bool:
        count = await self._store.count()
        return count > 0

    @staticmethod
    def _build_context(results: list[SearchResult]) -> str:
        parts: list[str] = []
        for i, r in enumerate(results, 1):
            doc_id = r.chunk.document_id
            title = r.chunk.metadata.get("title", "未知文档")
            parts.append(f"[来源 {i} | 文档: {title} (ID:{doc_id})]\n{r.chunk.content}")
        return "\n\n---\n\n".join(parts)

    @staticmethod
    def _build_retrieval_trace(
        query: str, all_results: list[SearchResult], filtered: list[SearchResult],
    ) -> dict[str, Any]:
        filtered_ids = {r.chunk.id for r in filtered}
        query_keywords = _extract_keywords(query)
        traces: list[dict[str, Any]] = []
        for r in all_results:
            chunk_kw = _extract_keywords(r.chunk.content[:500])
            overlapping = query_keywords & chunk_kw
            match_reason = (f"关键词匹配: {', '.join(sorted(overlapping)[:5])}" if overlapping
                           else "语义相似度高（向量空间近邻）" if r.score >= 0.5
                           else f"语义相似度较低 ({r.score:.3f})")
            traces.append({
                "chunk_id": r.chunk.id, "similarity_score": round(r.score, 4),
                "source_document": r.chunk.metadata.get("title", f"doc_{r.chunk.document_id}"),
                "source_document_id": r.chunk.document_id,
                "chunk_index": r.chunk.metadata.get("chunk_index", 0),
                "match_reason": match_reason,
                "overlapping_keywords": sorted(overlapping)[:10] if overlapping else [],
                "used": r.chunk.id in filtered_ids,
                "content_preview": r.chunk.content[:120],
            })
        return {
            "query": query, "query_keywords": sorted(query_keywords),
            "total_retrieved": len(all_results), "total_used": len(filtered),
            "threshold": 0.3, "chunks": traces,
        }


_STOP_WORDS: set[str] = {
    "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一",
    "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着",
    "没有", "看", "好", "自己", "这", "他", "她", "它", "们", "那", "什么",
    "怎么", "如何", "哪里", "哪", "吗", "呢", "吧", "啊", "哦", "嗯",
    "可以", "能够", "应该", "需要", "如果", "因为", "所以", "但是", "而且",
    "然后", "之后", "之前", "已经", "正在", "将", "把", "被", "让",
    "对", "从", "以", "之", "与", "及", "或", "等", "等等",
}


def _extract_keywords(text: str, min_len: int = 2) -> set[str]:
    tokens: set[str] = set()
    en_words = re.findall(r"[a-zA-Z0-9_+\-*/=<>.]{2,}", text)
    tokens.update(w.lower() for w in en_words if len(w) >= min_len)
    chinese_chars = re.findall(r"[\u4e00-\u9fff]", text)
    for i in range(len(chinese_chars) - 1):
        bigram = chinese_chars[i] + chinese_chars[i + 1]
        if bigram not in _STOP_WORDS:
            tokens.add(bigram)
    return tokens


knowledge_qa = KnowledgeQA()
