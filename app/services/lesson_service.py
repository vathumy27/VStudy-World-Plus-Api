from sqlalchemy import or_

from app.extensions import db
from app.models.lesson import Lesson
from app.models.study_resource import StudyResource
from app.models.subject import Subject
from app.schemas.lesson_schema import LessonCreateSchema, LessonUpdateSchema
from app.utils.response import error_response, success_response
from app.utils.search_utils import expand_query_terms


SUBJECT_NAME_TO_KEY = {
    "history": "history",
    "geography": "geography",
    "mathematics": "mathematics",
    "science": "science",
}


class LessonService:
    """Business logic for lesson management."""

    @staticmethod
    def _format_validation_errors(err):
        messages = []
        raw = getattr(err, "messages", None)
        if isinstance(raw, dict):
            for field, field_errors in raw.items():
                errors = (
                    field_errors
                    if isinstance(field_errors, (list, tuple))
                    else [field_errors]
                )
                for message in errors:
                    messages.append(f"{field}: {message}")
            return "; ".join(messages)
        return str(err)

    @staticmethod
    def get_all(
        subject_id=None,
        grade=None,
        unit=None,
        language=None,
        search=None,
        subject_name=None,
        page=1,
        per_page=20,
    ):
        query = Lesson.query.join(Subject, Lesson.subject_id == Subject.id)

        if subject_id is not None:
            query = query.filter(Lesson.subject_id == subject_id)
        if grade is not None:
            query = query.filter(Lesson.grade == grade)
        if unit:
            query = query.filter(Lesson.unit_number.ilike(f"%{unit.strip()}%"))
        if language:
            query = query.filter(Lesson.language.ilike(f"%{language.strip()}%"))
        if subject_name:
            query = query.filter(Subject.name.ilike(f"%{subject_name.strip()}%"))
        if search:
            terms = expand_query_terms(search)
            keywords_text = db.cast(StudyResource.keywords, db.String)
            clauses = []
            for term in terms[:20]:
                like = f"%{term}%"
                clauses.extend(
                    [
                        Lesson.title.ilike(like),
                        Lesson.description.ilike(like),
                        Lesson.unit_number.ilike(like),
                        Subject.name.ilike(like),
                        keywords_text.ilike(like),
                        StudyResource.title.ilike(like),
                        StudyResource.short_notes.ilike(like),
                        StudyResource.summary.ilike(like),
                    ]
                )
            query = (
                query.outerjoin(StudyResource, StudyResource.lesson_id == Lesson.id)
                .filter(or_(*clauses) if clauses else True)
                .distinct()
            )

        page = max(1, int(page or 1))
        per_page = max(1, min(100, int(per_page or 20)))

        total = query.count()
        lessons = (
            query.order_by(Lesson.grade.asc(), Lesson.unit_number.asc(), Lesson.id.asc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )

        # Attach Tamil display title from study resources when available
        lesson_payloads = []
        for lesson in lessons:
            data = lesson.to_dict(include_subject=True)
            note = StudyResource.query.filter_by(
                lesson_id=lesson.id, resource_type="lesson_notes"
            ).first()
            if note:
                data["display_title"] = note.title
                data["has_study_notes"] = True
                data["study_language"] = note.language
            else:
                data["display_title"] = lesson.title
                data["has_study_notes"] = False
            lesson_payloads.append(data)

        return success_response(
            "Lessons retrieved successfully.",
            {
                "lessons": lesson_payloads,
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": total,
                    "total_pages": (total + per_page - 1) // per_page,
                },
            },
        )

    @staticmethod
    def get_by_id(lesson_id):
        lesson = db.session.get(Lesson, lesson_id)
        if not lesson:
            return error_response("Lesson not found.", status_code=404)

        data = lesson.to_dict(include_subject=True)
        note = StudyResource.query.filter_by(
            lesson_id=lesson.id, resource_type="lesson_notes"
        ).first()
        if note:
            data["display_title"] = note.title
            data["has_study_notes"] = True
            data["study_language"] = note.language
        else:
            data["display_title"] = lesson.title
            data["has_study_notes"] = False

        return success_response(
            "Lesson retrieved successfully.",
            {"lesson": data},
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
            grade=validated.get("grade"),
            unit_number=validated.get("unit_number"),
            language=validated.get("language"),
            pdf_url=validated.get("pdf_url"),
            image_url=validated.get("image_url"),
            resource_url=validated.get("resource_url"),
            download_url=validated.get("download_url"),
            source_url=validated.get("source_url"),
            source_provider=validated.get("source_provider"),
            resource_links=validated.get("resource_links") or [],
        )

        try:
            db.session.add(lesson)
            db.session.commit()
            return success_response(
                "Lesson created successfully.",
                {"lesson": lesson.to_dict(include_subject=True)},
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

        scalar_fields = [
            "title",
            "description",
            "content",
            "summary",
            "video_url",
            "grade",
            "unit_number",
            "language",
            "pdf_url",
            "image_url",
            "resource_url",
            "download_url",
            "source_url",
            "source_provider",
            "resource_links",
        ]
        for field in scalar_fields:
            if field in validated:
                value = validated[field]
                if field == "title" and value is not None:
                    value = value.strip()
                setattr(lesson, field, value)

        try:
            db.session.commit()
            return success_response(
                "Lesson updated successfully.",
                {"lesson": lesson.to_dict(include_subject=True)},
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
