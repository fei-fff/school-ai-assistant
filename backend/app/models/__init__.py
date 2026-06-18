"""Import all models so Alembic and Base.metadata can discover them."""

from app.models.user import User, UserRole, UserStatus
from app.models.chat_history import ChatHistory
from app.models.emotion_record import EmotionRecord
from app.models.college import College
from app.models.teacher_profile import TeacherProfile
from app.models.knowledge_category import KnowledgeCategory
from app.models.knowledge_document import KnowledgeDocument

# TODO: Add future models here
# - training_records (model evaluation logs)
# - system_config (key-value settings)
