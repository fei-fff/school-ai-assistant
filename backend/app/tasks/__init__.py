"""RAG task execution layer — synchronous pipeline for document processing.

Pipeline order:
    parser_task → summary_task → classification_task → embedding_task

Usage:
    from app.tasks.pipeline import run_pipeline
    result = await run_pipeline(document_id, db_session)

Each task is an independent async function that receives a KnowledgeDocument
ORM object, mutates its status fields, and returns it. The pipeline orchestrator
commits after each stage so partial progress is persisted even on later failure.
"""

from app.tasks.parser_task import run_parser_task
from app.tasks.summary_task import run_summary_task
from app.tasks.classification_task import run_classification_task
from app.tasks.embedding_task import run_embedding_task
from app.tasks.pipeline import run_pipeline, run_single_task

__all__ = [
    "run_parser_task",
    "run_summary_task",
    "run_classification_task",
    "run_embedding_task",
    "run_pipeline",
    "run_single_task",
]
