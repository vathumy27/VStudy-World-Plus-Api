from app.extensions import db
from app.models.chat_history import ChatHistory
from app.schemas.chat_schema import ChatAskSchema
from app.utils.openai_client import OpenAIClient
from app.utils.response import error_response, success_response


class ChatService:
    """Business logic for AI chatbot assistant."""

    @staticmethod
    def _format_validation_errors(err):
        messages = []
        for field, field_errors in err.messages.items():
            for message in field_errors:
                messages.append(f"{field}: {message}")
        return "; ".join(messages)

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

        ai_answer = OpenAIClient.generate_text(
            question,
            system_message=(
                "You are VStudy AI, a friendly learning assistant for school students. "
                "Explain concepts simply and encourage understanding over memorization."
            ),
        )

        if not ai_answer:
            ai_answer = (
                f"Great question about '{question[:80]}'! "
                "Here's a simple way to think about it:\n\n"
                "1. Break the topic into smaller parts.\n"
                "2. Connect it to something you already know.\n"
                "3. Try explaining it in your own words.\n"
                "4. Practice with a quiz to test your understanding.\n\n"
                "Keep asking questions — that's how real learning happens!"
            )

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
                },
            )
        except Exception:
            db.session.rollback()
            return error_response(
                "An internal server error occurred.", status_code=500
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
