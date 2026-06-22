"""Dynamic prompt builder — combines persona + emotion + query + RAG context."""

from app.emotion.detector import EmotionResult
from app.emotion.persona import get_persona


class PromptBuilder:
    """Builds the final LLM prompt from emotion, persona, and RAG context."""

    @staticmethod
    def build(
        user_message: str,
        emotion_result: EmotionResult,
        rag_context: str | None = None,
    ) -> list[dict[str, str]]:
        persona = get_persona(emotion_result.emotion)

        system_prompt = (
            f"{persona['style']} "
            f"The user is feeling: {emotion_result.emotion}. "
            f"Respond in Chinese. Keep your response warm and natural, under 300 characters."
        )

        user_prompt = user_message
        if rag_context:
            user_prompt = (
                f"Use the following reference material to help answer:\n\n"
                f"{rag_context}\n\n"
                f"User question: {user_message}"
            )

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]


prompt_builder = PromptBuilder()
