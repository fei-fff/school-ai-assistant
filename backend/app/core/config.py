"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ---- Application ----
    APP_NAME: str = "校园智能助手"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True

    # ---- Database ----
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/campus_assistant?charset=utf8mb4"

    # ---- JWT ----
    SECRET_KEY: str = "change-me-to-a-random-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # ---- CORS ----
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    # ---- AI Provider ----
    AI_PROVIDER: str = "mock"  # mock / openai / deepseek / qwen / glm / gemini

    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_CHAT_MODEL: str = "gpt-4o"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # DeepSeek
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"
    DEEPSEEK_CHAT_MODEL: str = "deepseek-chat"

    # Qwen
    QWEN_API_KEY: str = ""
    QWEN_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    QWEN_CHAT_MODEL: str = "qwen-turbo"

    # GLM
    GLM_API_KEY: str = ""
    GLM_BASE_URL: str = "https://open.bigmodel.cn/api/paas/v4"
    GLM_CHAT_MODEL: str = "glm-4"

    # Gemini
    GEMINI_API_KEY: str = ""
    GEMINI_CHAT_MODEL: str = "gemini-pro"

    # ---- Embedding ----
    EMBEDDING_PROVIDER: str = "mock"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSION: int = 1536

    # ---- Vector DB ----
    VECTOR_DB_TYPE: str = "chromadb"
    CHROMA_PERSIST_DIR: str = "./chroma_data"

    # ---- Upload ----
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 50
    ALLOWED_UPLOAD_TYPES: str = "pdf,docx,txt,md,csv,pptx"

    # ---- Logging ----
    LOG_DIR: str = "./logs"
    LOG_LEVEL: str = "INFO"
    LOG_ROTATION_DAYS: int = 7

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
