"""Chat router — dispatches to emotion / mentor / knowledge modules."""

from app.chat.intent import detect_intent


class ChatRouter:
    """Routes messages to the correct backend module based on intent."""

    @staticmethod
    async def route(message: str, user_id: int) -> dict:
        intent, confidence = detect_intent(message)

        trace = {"route": intent, "confidence": round(confidence, 2)}

        if intent == "emotion":
            return await ChatRouter._handle_emotion(message, trace)
        elif intent == "mentor":
            return await ChatRouter._handle_mentor(message, trace)
        else:
            return await ChatRouter._handle_knowledge(message, trace)

    @staticmethod
    async def _handle_emotion(message: str, trace: dict) -> dict:
        from app.emotion.detector import emotion_detector
        from app.emotion.prompt_builder import prompt_builder
        from app.ai.service import ai_service

        emo = emotion_detector.detect(message)
        msgs = prompt_builder.build(message, emo, None)
        answer = await ai_service.chat(msgs)

        return dict(
            intent="emotion",
            answer=answer,
            trace=dict(route="emotion", confidence=trace["confidence"],
                       emotion=emo.emotion, persona_used=emo.emotion),
        )

    @staticmethod
    async def _handle_mentor(message: str, trace: dict) -> dict:
        from app.rag.retrieval import knowledge_qa

        # Extract keywords as query for mentor search
        query = message[:100]
        try:
            rag = await knowledge_qa.ask(query, top_k=3, similarity_threshold=0.15)
            answer = rag.get("answer", "No mentor match found.")
            sources = rag.get("sources", [])
        except Exception:
            answer = "Mentor search unavailable."
            sources = []

        return dict(
            intent="mentor",
            answer=answer,
            trace=dict(route="mentor", confidence=trace["confidence"], sources=sources),
        )

    @staticmethod
    async def _handle_knowledge(message: str, trace: dict) -> dict:
        from app.rag.retrieval import knowledge_qa

        try:
            rag = await knowledge_qa.ask(message, top_k=5, similarity_threshold=0.15)
            answer = rag.get("answer", "No results.")
            retrieval = rag.get("retrieval_trace")
        except Exception:
            answer = "Knowledge search unavailable."
            retrieval = None

        return dict(
            intent="knowledge",
            answer=answer,
            trace=dict(route="knowledge", confidence=trace["confidence"],
                       retrieval_trace=retrieval),
        )


chat_router = ChatRouter()
