"""Knowledge QA pipeline — retrieval-augmented generation closed loop.

Flow:
    query -> embed -> search vector store -> build context -> AI generate -> result
"""

import logging
import re
from typing import Any

from app.ai.service import ai_service
from app.rag.vector_store import VectorStore, SearchResult, vector_store

logger = logging.getLogger(__name__)


class KnowledgeQA:
    """RAG retrieval-augmented QA pipeline.

    Usage:
        qa = KnowledgeQA()
        result = await qa.ask("什么是红黑树？", top_k=5)
    """

    def __init__(self, store: VectorStore | None = None):
        self._store = store or vector_store

    async def ask(
        self,
        query: str,
        top_k: int = 5,
        *,
        similarity_threshold: float = 0.3,
        history: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        """Answer a question using the RAG knowledge base.

        Args:
            query: User question.
            top_k: Number of top-matching chunks to retrieve.
            similarity_threshold: Minimum similarity score to include.
            history: Optional conversation history.

        Returns:
            Dict with keys:
                answer          — AI-generated answer
                sources         — list of source info dicts
                scores          — list of similarity scores
                context_used    — context text fed to the LLM
                chunk_count     — number of chunks retrieved
                retrieval_trace — detailed per-chunk retrieval trace
        """
        # 1. Embed the query
        logger.info("KnowledgeQA: embedding query (length=%d)", len(query))
        query_vectors = await ai_service.embed([query])
        query_embedding = query_vectors[0]

        # 2. Search vector store
        results = await self._store.search(query_embedding, top_k=top_k)
        logger.info("KnowledgeQA: retrieved %d chunks", len(results))

        # 3. Filter by similarity threshold
        filtered = [r for r in results if r.score >= similarity_threshold]

        # Build retrieval trace (all results, before filtering)
        retrieval_trace = self._build_retrieval_trace(query, results, filtered)

        if not filtered:
            return {
                "answer": "知识库中未找到与您问题相关的内容，请尝试换一种方式提问。",
                "sources": [],
                "scores": [],
                "context_used": "",
                "chunk_count": 0,
                "retrieval_trace": retrieval_trace,
            }

        # 4. Build context string
        context = self._build_context(filtered)

        # 5. Generate answer via AIService
        answer = await ai_service.knowledge_chat(
            question=query,
            context=context,
            history=history,
        )

        # 6. Build structured result
        sources = [r.to_dict() for r in filtered]
        scores = [round(r.score, 4) for r in filtered]

        return {
            "answer": answer,
            "sources": sources,
            "scores": scores,
            "context_used": context,
            "chunk_count": len(filtered),
            "retrieval_trace": retrieval_trace,
        }

    async def is_ready(self) -> bool:
        count = await self._store.count()
        return count > 0

    # ── Helpers ────────────────────────────────

    @staticmethod
    def _build_context(results: list[SearchResult]) -> str:
        parts: list[str] = []
        for i, r in enumerate(results, 1):
            doc_id = r.chunk.document_id
            title = r.chunk.metadata.get("title", "未知文档")
            parts.append(
                f"[来源 {i} | 文档: {title} (ID:{doc_id})]\n{r.chunk.content}"
            )
        return "\n\n---\n\n".join(parts)

    @staticmethod
    def _build_retrieval_trace(
        query: str,
        all_results: list[SearchResult],
        filtered: list[SearchResult],
    ) -> dict[str, Any]:
        filtered_ids = {r.chunk.id for r in filtered}
        query_keywords = _extract_keywords(query)

        traces: list[dict[str, Any]] = []
        for r in all_results:
            chunk_kw = _extract_keywords(r.chunk.content[:500])
            overlapping = query_keywords & chunk_kw

            if overlapping:
                match_reason = f"关键词匹配: {', '.join(sorted(overlapping)[:5])}"
            elif r.score >= 0.5:
                match_reason = "语义相似度高（向量空间近邻）"
            else:
                match_reason = f"语义相似度较低 ({r.score:.3f})"

            traces.append({
                "chunk_id": r.chunk.id,
                "similarity_score": round(r.score, 4),
                "source_document": r.chunk.metadata.get("title", f"doc_{r.chunk.document_id}"),
                "source_document_id": r.chunk.document_id,
                "chunk_index": r.chunk.metadata.get("chunk_index", 0),
                "match_reason": match_reason,
                "overlapping_keywords": sorted(overlapping)[:10] if overlapping else [],
                "used": r.chunk.id in filtered_ids,
                "content_preview": r.chunk.content[:120],
            })

        return {
            "query": query,
            "query_keywords": sorted(query_keywords),
            "total_retrieved": len(all_results),
            "total_used": len(filtered),
            "threshold": 0.3,
            "chunks": traces,
        }


# ── Keyword extraction ─────────────────────────

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


# ── Singleton ─────────────────────────────────

knowledge_qa = KnowledgeQA()
