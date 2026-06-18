"""Knowledge QA API — RAG retrieval-augmented question answering."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.rag.retrieval import knowledge_qa
from app.utils.response import ok

router = APIRouter(prefix="/qa", tags=["知识问答"])


@router.post("/ask", summary="知识库问答")
async def ask_question(
    question: str = Query(..., description="用户问题"),
    top_k: int = Query(5, ge=1, le=20, description="检索片段数"),
    similarity_threshold: float = Query(
        0.3, ge=0.0, le=1.0, description="最低相似度阈值"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Ask a question and get an answer grounded in the knowledge base.

    调用链:
        query → embed → vector search → context → AI generate → result

    返回:
        answer: AI 生成的回答
        sources: 引用来源列表 (chunk_id, document_id, content, score, metadata)
        scores: 各来源的相似度分数
        context_used: 拼接后输入 LLM 的上下文
        chunk_count: 检索到的片段数
    """
    # Check readiness
    ready = await knowledge_qa.is_ready()
    if not ready:
        return ok(
            data={
                "answer": "知识库尚未初始化，请先上传并处理文档。",
                "sources": [],
                "scores": [],
                "context_used": "",
                "chunk_count": 0,
            },
            message="向量库为空",
        )

    result = await knowledge_qa.ask(
        query=question,
        top_k=top_k,
        similarity_threshold=similarity_threshold,
    )

    return ok(data=result)
