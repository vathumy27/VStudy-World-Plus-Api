from app.extensions import db
from app.models.lesson_summary import LessonSummary
from app.models.lesson_video import LessonVideo
from app.schemas.ai_schema import ExplainSchema, GenerateVideoSchema, SummarizeSchema
from app.utils.openai_client import OpenAIClient
from app.utils.response import error_response, success_response


class AIService:
    """AI study helper service with OpenAI integration and mock fallback."""

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
    def summarize(data, user_id=None):
        schema = SummarizeSchema()
        try:
            validated = schema.load(data or {})
        except Exception as err:
            return error_response(
                AIService._format_validation_errors(err),
                status_code=400,
            )

        content = validated["lesson_content"].strip()
        lesson_id = (data or {}).get("lesson_id")

        ai_prompt = (
            f"Summarize this lesson content for a school student in simple language:\n\n"
            f"{content}"
        )
        summary = OpenAIClient.generate_text(
            ai_prompt,
            system_message="You are an educational summarizer for school students.",
        )

        if not summary:
            word_count = len(content.split())
            preview = content[:120] + ("..." if len(content) > 120 else "")
            summary = (
                f"This lesson covers key concepts in approximately {word_count} words. "
                f"Main idea: {preview} "
                "Study tip: Read each section carefully, note important terms, "
                "and try explaining the topic in your own words."
            )

        if user_id:
            record = LessonSummary(
                lesson_id=lesson_id,
                user_id=int(user_id),
                summary_text=summary,
                source_content=content,
            )
            try:
                db.session.add(record)
                db.session.commit()
            except Exception:
                db.session.rollback()

        return success_response(
            "Lesson summarized successfully.",
            {"summary": summary},
        )

    @staticmethod
    def explain(data, user_id=None):
        schema = ExplainSchema()
        try:
            validated = schema.load(data or {})
        except Exception as err:
            return error_response(
                AIService._format_validation_errors(err),
                status_code=400,
            )

        topic = validated["topic"].strip()

        ai_prompt = f"Explain '{topic}' in simple language for a school student."
        explanation = OpenAIClient.generate_text(
            ai_prompt,
            system_message="You are a friendly tutor who explains topics simply.",
        )

        if not explanation:
            explanation = (
                f"Let's understand '{topic}' in a simple way.\n\n"
                f"1. What is it? '{topic}' is an important concept in your syllabus.\n"
                f"2. Why does it matter? It helps you connect ideas and answer exam questions.\n"
                f"3. How to remember it? Use examples, draw diagrams, and teach a friend.\n"
                f"4. Quick tip: Break '{topic}' into smaller parts and study one part at a time."
            )

        return success_response(
            "Topic explained successfully.",
            {"explanation": explanation},
        )

    @staticmethod
    def generate_video(data, user_id=None):
        schema = GenerateVideoSchema()
        try:
            validated = schema.load(data or {})
        except Exception as err:
            return error_response(
                AIService._format_validation_errors(err),
                status_code=400,
            )

        history_lesson = validated["history_lesson"].strip()
        lesson_id = (data or {}).get("lesson_id")

        ai_prompt = (
            f"Create a short story-based video script outline for this history lesson: "
            f"{history_lesson}"
        )
        script = OpenAIClient.generate_text(
            ai_prompt,
            system_message="You create engaging history story scripts for students.",
        )

        lesson_snippet = history_lesson[:50].replace(" ", "-").lower()
        video_url = (
            f"https://vstudy-world-plus.example.com/videos/history/"
            f"story-{lesson_snippet}-demo.mp4"
        )
        title = "Story-based History Lesson"
        duration_seconds = 180

        if user_id:
            record = LessonVideo(
                lesson_id=lesson_id,
                user_id=int(user_id),
                title=title,
                video_url=video_url,
                duration_seconds=duration_seconds,
            )
            try:
                db.session.add(record)
                db.session.commit()
            except Exception:
                db.session.rollback()

        response_data = {
            "video_url": video_url,
            "title": title,
            "duration_seconds": duration_seconds,
        }
        if script:
            response_data["script_outline"] = script
        else:
            response_data["note"] = (
                "Mock video URL generated. Configure OPENAI_API_KEY for AI script generation."
            )

        return success_response(
            "History video generated successfully.",
            response_data,
        )
