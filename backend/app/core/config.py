"""Unified application configuration — single source of truth."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Campus AI Assistant"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True
    RAG_DEBUG: bool = False

    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/campus_assistant?charset=utf8mb4"
    SECRET_KEY: str = "change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    AI_PROVIDER: str = "mock"
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_CHAT_MODEL: str = "gpt-4o"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"
    DEEPSEEK_CHAT_MODEL: str = "deepseek-chat"
    QWEN_API_KEY: str = ""
    QWEN_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    QWEN_CHAT_MODEL: str = "qwen-turbo"
    GLM_API_KEY: str = ""
    GLM_BASE_URL: str = "https://open.bigmodel.cn/api/paas/v4"
    GLM_CHAT_MODEL: str = "glm-4"
    GEMINI_API_KEY: str = ""
    GEMINI_CHAT_MODEL: str = "gemini-pro"

    EMBEDDING_PROVIDER: str = "mock"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSION: int = 1536
    EMBEDDING_CHUNK_SIZE: int = 1500
    EMBEDDING_CHUNK_OVERLAP: int = 200

    PARSER_MAX_CONTENT_LENGTH: int = 32000

    RAG_TOP_K: int = 5
    RAG_THRESHOLD: float = 0.15

    VECTOR_DB: str = "mock"
    CHROMA_PERSIST_DIR: str = "./chroma_data"
    CHROMA_COLLECTION_NAME: str = "campus_knowledge"

    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 50
    ALLOWED_UPLOAD_TYPES: str = "pdf,docx,txt,md,csv,pptx"

    LOG_DIR: str = "./logs"
    LOG_LEVEL: str = "INFO"
    LOG_ROTATION_DAYS: int = 7

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
