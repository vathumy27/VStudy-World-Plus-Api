from app.extensions import db
from app.models.lesson import Lesson
from app.models.progress import Progress
from app.models.subject import Subject
from app.models.user import User
from app.schemas.progress_schema import ProgressUpdateSchema
from app.utils.response import error_response, success_response
from app.utils.time_utils import utc_now


class ProgressService:
    """Business logic for student progress tracking."""

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
    def get_by_user(user_id, requester_id, requester_role):
        target_user_id = int(user_id)
        requester_id = int(requester_id)

        if target_user_id != requester_id and requester_role not in (
            "Teacher",
            "Admin",
        ):
            return error_response(
                "You do not have permission to view this progress.",
                status_code=403,
            )

        user = db.session.get(User, target_user_id)
        if not user:
            return error_response("User not found.", status_code=404)

        records = (
            Progress.query.filter_by(user_id=target_user_id)
            .order_by(Progress.updated_at.desc())
            .all()
        )

        total_completion = 0.0
        if records:
            total_completion = round(
                sum(r.completion_percentage for r in records) / len(records), 2
            )

        return success_response(
            "Progress retrieved successfully.",
            {
                "user_id": target_user_id,
                "total_records": len(records),
                "average_completion": total_completion,
                "progress": [record.to_dict() for record in records],
            },
        )

    @staticmethod
    def update(user_id, data):
        schema = ProgressUpdateSchema()
        try:
            validated = schema.load(data or {})
        except Exception as err:
            return error_response(
                ProgressService._format_validation_errors(err),
                status_code=400,
            )

        user = db.session.get(User, int(user_id))
        if not user:
            return error_response("User not found.", status_code=404)

        lesson_id = validated.get("lesson_id")
        subject_id = validated.get("subject_id")

        if lesson_id:
            lesson = db.session.get(Lesson, lesson_id)
            if not lesson:
                return error_response("Lesson not found.", status_code=404)
            subject_id = lesson.subject_id

        if subject_id:
            subject = db.session.get(Subject, subject_id)
            if not subject:
                return error_response("Subject not found.", status_code=404)

        progress = Progress.query.filter_by(
            user_id=int(user_id),
            lesson_id=lesson_id,
            subject_id=subject_id,
        ).first()

        if not progress:
            progress = Progress(
                user_id=int(user_id),
                lesson_id=lesson_id,
                subject_id=subject_id,
            )
            db.session.add(progress)

        if "status" in validated:
            progress.status = validated["status"]
        if "completion_percentage" in validated:
            progress.completion_percentage = validated["completion_percentage"]
        if "time_spent_minutes" in validated:
            progress.time_spent_minutes += validated["time_spent_minutes"]

        progress.last_accessed_at = utc_now()
        progress.updated_at = utc_now()

        try:
            db.session.commit()
            return success_response(
                "Progress updated successfully.",
                {"progress": progress.to_dict()},
            )
        except Exception:
            db.session.rollback()
            return error_response(
                "An internal server error occurred.", status_code=500
            )
