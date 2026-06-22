"""Chat router — multi-turn with history + profile auto-update."""

from app.chat.intent import detect_intent


class ChatRouter:

    @staticmethod
    async def route(message: str, user_id: int, history: list[dict] = None,
                    memory_context: str = "") -> dict:
        history = history or []
        intent, confidence = detect_intent(message)
        trace = {"route": intent, "confidence": round(confidence, 2)}

        if intent == "emotion":
            return await ChatRouter._handle_emotion(message, user_id, history, memory_context, trace)
        elif intent == "mentor":
            return await ChatRouter._handle_mentor(message, user_id, history, memory_context, trace)
        else:
            return await ChatRouter._handle_knowledge(message, user_id, history, memory_context, trace)

    @staticmethod
    async def _auto_update_profile(user_id, intent, message, emotion=None):
        from app.database.database import SessionLocal
        from app.crud.user_profile import update_profile
        db = SessionLocal()
        try:
            if intent == "emotion" and emotion:
                update_profile(db, user_id, emotion_state=emotion, frequent_topics=message[:100])
            elif intent == "mentor":
                update_profile(db, user_id, interests=message[:200])
            elif intent == "knowledge":
                update_profile(db, user_id, frequent_topics=message[:200])
        finally:
            db.close()

    @staticmethod
    async def _handle_emotion(message, user_id, history, memory, trace):
        from app.emotion.detector import emotion_detector
        from app.emotion.prompt_builder import prompt_builder
        from app.ai.service import ai_service
        emo = emotion_detector.detect(message)
        msgs = prompt_builder.build(message, emo, None)
        if history:
            msgs[0]["content"] += f" History: {len(history)} turns."
        if memory:
            msgs[0]["content"] += f" Context: {memory}."
        full = msgs[:1] + history[-6:] + msgs[1:]
        answer = await ai_service.chat(full)
        await ChatRouter._auto_update_profile(user_id, "emotion", message, emotion=emo.emotion)
        return dict(intent="emotion", answer=answer,
                    trace=dict(route="emotion", confidence=trace["confidence"], emotion=emo.emotion))

    @staticmethod
    async def _handle_mentor(message, user_id, history, memory, trace):
        from app.ai.service import ai_service

        await ChatRouter._auto_update_profile(user_id, "mentor", message)

        # Use plain chat with mentor-aware system prompt
        system = (
            "You are a campus assistant helping with mentor search. "
            "If the user asks about mentors, guide them to check the mentor system. "
            "Tell them to search by college or research direction, or use the Mentors page. "
            "Respond naturally in Chinese."
        )
        if memory:
            system += f" User context: {memory}."
        msgs = [{"role": "system", "content": system}]
        msgs += history[-6:]
        msgs.append({"role": "user", "content": message})
        answer = await ai_service.chat(msgs)

        return dict(intent="mentor", answer=answer,
                    trace=dict(route="mentor", confidence=trace["confidence"]))

    @staticmethod
    async def _handle_knowledge(message, user_id, history, memory, trace):
        from app.rag.retrieval import knowledge_qa
        from app.ai.service import ai_service

        rag = None
        try:
            rag = await knowledge_qa.ask(message, top_k=5, similarity_threshold=0.15,
                                         history=history[-4:] if history else None)
        except Exception:
            pass

        await ChatRouter._auto_update_profile(user_id, "knowledge", message)

        if rag and rag.get("chunk_count", 0) > 0:
            return dict(intent="knowledge", answer=rag["answer"],
                        trace=dict(route="knowledge", confidence=trace["confidence"],
                                   retrieval_trace=rag.get("retrieval_trace")))

        system = "You are a friendly campus assistant. Respond naturally in Chinese."
        if memory:
            system += f" User context: {memory}."
        msgs = [{"role": "system", "content": system}]
        msgs += history[-8:]
        msgs.append({"role": "user", "content": message})
        answer = await ai_service.chat(msgs)

        return dict(intent="knowledge", answer=answer,
                    trace=dict(route="knowledge", confidence=trace["confidence"],
                               retrieval_trace=None, fallback="plain_chat"))


chat_router = ChatRouter()
