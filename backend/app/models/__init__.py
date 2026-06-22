"""Import all models for Alembic / Base.metadata discovery."""

from app.models.user import User, UserRole, UserStatus
from app.models.chat_history import ChatHistory
from app.models.emotion_record import EmotionRecord
from app.models.college import College
from app.models.teacher_profile import TeacherProfile
from app.models.knowledge_category import KnowledgeCategory
from app.models.knowledge_document import KnowledgeDocument
from app.models.user_profile import UserProfile
