from app.extensions import db
from app.models.lesson import Lesson
from app.models.subject import Subject
from app.schemas.lesson_schema import LessonCreateSchema, LessonUpdateSchema
from app.utils.response import error_response, success_response


class LessonService:
    """Business logic for lesson management."""

    @staticmethod
    def _format_validation_errors(err):
        messages = []
        for field, field_errors in err.messages.items():
            for message in field_errors:
                messages.append(f"{field}: {message}")
        return "; ".join(messages)

    @staticmethod
    def get_all(subject_id=None):
        query = Lesson.query
        if subject_id is not None:
            query = query.filter_by(subject_id=subject_id)

        lessons = query.order_by(Lesson.created_at.desc()).all()
        return success_response(
            "Lessons retrieved successfully.",
            {"lessons": [lesson.to_dict() for lesson in lessons]},
        )

    @staticmethod
    def get_by_id(lesson_id):
        lesson = db.session.get(Lesson, lesson_id)
        if not lesson:
            return error_response("Lesson not found.", status_code=404)

        return success_response(
            "Lesson retrieved successfully.",
            {"lesson": lesson.to_dict(include_subject=True)},
        )

    @staticmethod
    def create(data):
        schema = LessonCreateSchema()
        try:
            validated = schema.load(data or {})
        except Exception as err:
            return error_response(
                LessonService._format_validation_errors(err),
                status_code=400,
            )

        subject = db.session.get(Subject, validated["subject_id"])
        if not subject:
            return error_response("Subject not found.", status_code=404)

        lesson = Lesson(
            subject_id=validated["subject_id"],
            title=validated["title"].strip(),
            description=validated.get("description"),
            content=validated.get("content"),
            summary=validated.get("summary"),
            video_url=validated.get("video_url"),
        )

        try:
            db.session.add(lesson)
            db.session.commit()
            return success_response(
                "Lesson created successfully.",
                {"lesson": lesson.to_dict()},
                status_code=201,
            )
        except Exception:
            db.session.rollback()
            return error_response(
                "An internal server error occurred.", status_code=500
            )

    @staticmethod
    def update(lesson_id, data):
        schema = LessonUpdateSchema()
        try:
            validated = schema.load(data or {})
        except Exception as err:
            return error_response(
                LessonService._format_validation_errors(err),
                status_code=400,
            )

        lesson = db.session.get(Lesson, lesson_id)
        if not lesson:
            return error_response("Lesson not found.", status_code=404)

        if "subject_id" in validated:
            subject = db.session.get(Subject, validated["subject_id"])
            if not subject:
                return error_response("Subject not found.", status_code=404)
            lesson.subject_id = validated["subject_id"]

        if "title" in validated:
            lesson.title = validated["title"].strip()
        if "description" in validated:
            lesson.description = validated["description"]
        if "content" in validated:
            lesson.content = validated["content"]
        if "summary" in validated:
            lesson.summary = validated["summary"]
        if "video_url" in validated:
            lesson.video_url = validated["video_url"]

        try:
            db.session.commit()
            return success_response(
                "Lesson updated successfully.",
                {"lesson": lesson.to_dict()},
            )
        except Exception:
            db.session.rollback()
            return error_response(
                "An internal server error occurred.", status_code=500
            )

    @staticmethod
    def delete(lesson_id):
        lesson = db.session.get(Lesson, lesson_id)
        if not lesson:
            return error_response("Lesson not found.", status_code=404)

        try:
            db.session.delete(lesson)
            db.session.commit()
            return success_response("Lesson deleted successfully.")
        except Exception:
            db.session.rollback()
            return error_response(
                "An internal server error occurred.", status_code=500
            )
