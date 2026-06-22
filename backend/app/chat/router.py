"""Chat router — multi-turn with history support."""

from app.chat.intent import detect_intent


class ChatRouter:

    @staticmethod
    async def route(message: str, user_id: int, history: list[dict] = None,
                    memory_context: str = "") -> dict:
        history = history or []
        intent, confidence = detect_intent(message)
        trace = {"route": intent, "confidence": round(confidence, 2)}

        if intent == "emotion":
            return await ChatRouter._handle_emotion(message, history, memory_context, trace)
        elif intent == "mentor":
            return await ChatRouter._handle_mentor(message, history, memory_context, trace)
        else:
            return await ChatRouter._handle_knowledge(message, history, memory_context, trace)

    @staticmethod
    async def _handle_emotion(message, history, memory, trace):
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

        return dict(intent="emotion", answer=answer,
                    trace=dict(route="emotion", confidence=trace["confidence"], emotion=emo.emotion))

    @staticmethod
    async def _handle_mentor(message, history, memory, trace):
        from app.rag.retrieval import knowledge_qa
        try:
            rag = await knowledge_qa.ask(message, top_k=3, similarity_threshold=0.15,
                                         history=history[-4:] if history else None)
            answer = rag.get("answer", "No results.")
            sources = rag.get("sources", [])
        except Exception:
            answer = "Mentor search unavailable."
            sources = []
        return dict(intent="mentor", answer=answer,
                    trace=dict(route="mentor", confidence=trace["confidence"], sources=sources))

    @staticmethod
    async def _handle_knowledge(message, history, memory, trace):
        from app.rag.retrieval import knowledge_qa
        from app.ai.service import ai_service

        # Try RAG first
        rag = None
        try:
            rag = await knowledge_qa.ask(message, top_k=5, similarity_threshold=0.15,
                                         history=history[-4:] if history else None)
        except Exception:
            pass

        # If RAG found results, use them
        if rag and rag.get("chunk_count", 0) > 0:
            return dict(intent="knowledge", answer=rag["answer"],
                        trace=dict(route="knowledge", confidence=trace["confidence"],
                                   retrieval_trace=rag.get("retrieval_trace")))

        # RAG empty — fall back to plain chat
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
