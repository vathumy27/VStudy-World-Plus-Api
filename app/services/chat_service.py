from app.extensions import db
from app.models.chat_history import ChatHistory
from app.schemas.chat_schema import ChatAskSchema
from app.services.study_resource_service import StudyResourceService
from app.utils.openai_client import OpenAIClient
from app.utils.response import error_response, success_response
from app.utils.search_utils import contains_tamil


AGENT_SYSTEM = (
    "You are VStudy AI, the educational agent for Sri Lankan Grade 10 and Grade 11 (O/L) students.\n"
    "Rules:\n"
    "1. Answer ONLY questions related to Grade 10/11 History, Geography, Science, or Mathematics syllabus.\n"
    "2. If the question is unrelated (sports news, gossip, hacking, etc.), politely refuse in the user's language "
    "and invite a syllabus question.\n"
    "3. Understand Tamil and English. Reply in the same language as the question. "
    "For difficult concepts, add a short simple Tamil explanation.\n"
    "4. Use the provided LESSON RESOURCES when available. Do not invent fake page numbers.\n"
    "5. Be concise, friendly, give 1–2 examples, and end with a short revision tip or exam tip.\n"
    "6. You may summarise, revise, and help with exam preparation."
)


class ChatService:
    """Business logic for AI chatbot assistant."""

    @staticmethod
    def _format_validation_errors(err):
        messages = []
        raw = getattr(err, "messages", None)
        if isinstance(raw, dict):
            for field, field_errors in raw.items():
                errors = field_errors if isinstance(field_errors, (list, tuple)) else [field_errors]
                for message in errors:
                    messages.append(f"{field}: {message}")
            return "; ".join(messages)
        return str(err)

    @staticmethod
    def _is_off_topic(question: str) -> bool:
        q = (question or "").lower()
        blocked = [
            "hack",
            "password crack",
            "bitcoin tip",
            "dating advice",
            "movie spoiler",
            "lottery number",
        ]
        return any(b in q for b in blocked)

    @staticmethod
    def _build_resource_context(resources) -> str:
        chunks = []
        for res in resources:
            parts = [
                f"Title: {res.title}",
                f"Grade: {res.grade}",
                f"SubjectId: {res.subject_id}",
                f"Short notes: {(res.short_notes or '')[:500]}",
                f"Easy explanation: {(res.easy_explanation or '')[:400]}",
                f"Summary: {(res.summary or '')[:400]}",
            ]
            if res.key_points:
                parts.append("Key points: " + "; ".join(res.key_points[:5]))
            if res.exam_tips:
                parts.append("Exam tips: " + "; ".join(res.exam_tips[:3]))
            chunks.append("\n".join(parts))
        return "\n\n---\n\n".join(chunks)

    @staticmethod
    def _offline_answer(question: str, resources) -> str:
        tamil = contains_tamil(question)
        if ChatService._is_off_topic(question):
            if tamil:
                return (
                    "மன்னிக்கவும் — நான் தரம் 10/11 வரலாறு, புவியியல், விஞ்ஞானம், "
                    "கணிதம் பாடத்திட்டக் கேள்விகளுக்கு மட்டும் உதவுவேன். "
                    "ஒரு பாடத் தலைப்பைக் கேளுங்கள்!"
                )
            return (
                "Sorry — I only help with Grade 10/11 History, Geography, Science, "
                "and Mathematics syllabus questions. Please ask a lesson topic!"
            )

        if resources:
            res = resources[0]
            points = "\n".join(f"• {p}" for p in (res.key_points or [])[:4])
            tips = "\n".join(f"• {t}" for t in (res.exam_tips or [])[:2])
            questions = "\n".join(f"• {q}" for q in (res.important_questions or [])[:2])
            if tamil or (res.language or "").lower() == "tamil":
                return (
                    f"உங்கள் கேள்வி 「{question[:120]}」 தொடர்பாக VStudy பாட வளம் கிடைத்தது.\n\n"
                    f"📚 {res.title} (தரம் {res.grade})\n\n"
                    f"குறுகிய குறிப்புகள்:\n{(res.short_notes or '')[:450]}\n\n"
                    f"எளிய விளக்கம்:\n{(res.easy_explanation or '')[:350]}\n\n"
                    f"முக்கியப் புள்ளிகள்:\n{points or '• பாடக் குறிப்புகளைப் படியுங்கள்'}\n\n"
                    f"சுருக்கம்:\n{(res.summary or '')[:300]}\n\n"
                    f"தேர்வுக் குறிப்புகள்:\n{tips or '• கட்டளைச் சொற்களைக் கவனியுங்கள்'}\n\n"
                    f"பயிற்சி வினாக்கள்:\n{questions or '• தலைப்பை வரையறுத்து ஒரு உதாரணம் தாருங்கள்'}\n\n"
                    f"திருத்தம்:\n{(res.revision_notes or '')[:280]}\n\n"
                    "மேலும் விவரம் வேண்டுமா? தலைப்பைக் குறிப்பிட்டு மீண்டும் கேளுங்கள்."
                )
            return (
                f"I found a VStudy lesson resource for “{question[:120]}”.\n\n"
                f"📚 {res.title} (Grade {res.grade})\n\n"
                f"Short notes:\n{(res.short_notes or '')[:450]}\n\n"
                f"Easy explanation:\n{(res.easy_explanation or '')[:350]}\n\n"
                f"Key points:\n{points}\n\n"
                f"Summary:\n{(res.summary or '')[:300]}\n\n"
                f"Exam tips:\n{tips}\n\n"
                "Ask a follow-up if you want a shorter revision card."
            )

        # No resource match — still give syllabus-scoped study help
        if tamil:
            return (
                f"「{question[:100]}」 பற்றி தற்போது சரியான பாடப் பக்கம் இணைக்கப்படவில்லை. "
                "ஆனால் O/L முறையில் இப்படிப் படியுங்கள்:\n\n"
                "1. தலைப்பை ஒரு வரியில் வரையறுக்கவும்.\n"
                "2. மூன்று முக்கியப் புள்ளிகள் எழுதவும்.\n"
                "3. ஒரு எளிய உதாரணம் சொல்லவும்.\n"
                "4. தேர்வுக்கு 5–6 வரி விடை பயிற்சி செய்யவும்.\n\n"
                "வரலாறு / புவியியல் / விஞ்ஞானம் / கணிதம் தலைப்பைத் தெளிவாகச் சொன்னால் "
                "மேலும் துல்லியமான விளக்கம் தருவேன்."
            )
        return (
            f"I don’t have an exact stored lesson match for “{question[:100]}” yet, "
            "but here’s an O/L study approach:\n\n"
            "1. Define the topic in one sentence.\n"
            "2. List three key points.\n"
            "3. Give one simple example.\n"
            "4. Practise a 5–6 line exam answer.\n\n"
            "Tell me the subject (History / Geography / Science / Maths) and grade "
            "for a more precise explanation."
        )

    @staticmethod
    def ask(user_id, data):
        schema = ChatAskSchema()
        try:
            validated = schema.load(data or {})
        except Exception as err:
            return error_response(
                ChatService._format_validation_errors(err),
                status_code=400,
            )

        question = validated["question"].strip()
        if not question:
            return error_response("கேள்வியை உள்ளிடுங்கள் / Please enter a question.", status_code=400)

        resources = []
        try:
            resources = StudyResourceService.find_related_resources(question, limit=3)
        except Exception:
            resources = []

        context = ChatService._build_resource_context(resources) if resources else "No stored lesson notes matched."
        prompt = (
            f"Student question:\n{question}\n\n"
            f"LESSON RESOURCES (may be empty):\n{context}\n\n"
            "Answer helpfully for O/L Grade 10–11 only."
        )

        ai_answer = None
        try:
            ai_answer = OpenAIClient.generate_text(
                prompt,
                system_message=AGENT_SYSTEM,
                max_tokens=900,
            )
        except Exception:
            ai_answer = None

        if not ai_answer:
            ai_answer = ChatService._offline_answer(question, resources)

        record = ChatHistory(
            user_id=int(user_id),
            question=question,
            answer=ai_answer,
        )

        try:
            db.session.add(record)
            db.session.commit()
            return success_response(
                "Question answered successfully.",
                {
                    "chat": record.to_dict(),
                    "matched_resources": [
                        {
                            "id": r.id,
                            "lesson_id": r.lesson_id,
                            "title": r.title,
                            "grade": r.grade,
                            "subject_id": r.subject_id,
                        }
                        for r in resources
                    ],
                },
            )
        except Exception:
            db.session.rollback()
            return error_response(
                "சேவையகப் பிழை ஏற்பட்டது. சிறிது நேரம் கழித்து முயலவும்.",
                status_code=500,
            )

    @staticmethod
    def get_history(user_id):
        records = (
            ChatHistory.query.filter_by(user_id=int(user_id))
            .order_by(ChatHistory.created_at.desc())
            .limit(50)
            .all()
        )

        return success_response(
            "Chat history retrieved successfully.",
            {"history": [record.to_dict() for record in records]},
        )
