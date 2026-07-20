from app.extensions import db
from app.models.subject import Subject
from app.schemas.subject_schema import SubjectCreateSchema, SubjectUpdateSchema
from app.utils.response import error_response, success_response


class SubjectService:
    """Business logic for subject management."""

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
    def get_all():
        subjects = Subject.query.order_by(Subject.name).all()
        return success_response(
            "Subjects retrieved successfully.",
            {"subjects": [s.to_dict() for s in subjects]},
        )

    @staticmethod
    def get_by_id(subject_id):
        subject = db.session.get(Subject, subject_id)
        if not subject:
            return error_response("Subject not found.", status_code=404)

        return success_response(
            "Subject retrieved successfully.",
            {"subject": subject.to_dict()},
        )

    @staticmethod
    def create(data):
        schema = SubjectCreateSchema()
        try:
            validated = schema.load(data or {})
        except Exception as err:
            return error_response(
                SubjectService._format_validation_errors(err),
                status_code=400,
            )

        name = validated["name"].strip()
        if Subject.query.filter_by(name=name).first():
            return error_response("Subject name already exists.", status_code=409)

        subject = Subject(
            name=name,
            description=validated.get("description"),
            image=validated.get("image"),
        )

        try:
            db.session.add(subject)
            db.session.commit()
            return success_response(
                "Subject created successfully.",
                {"subject": subject.to_dict()},
                status_code=201,
            )
        except Exception:
            db.session.rollback()
            return error_response(
                "An internal server error occurred.", status_code=500
            )

    @staticmethod
    def update(subject_id, data):
        schema = SubjectUpdateSchema()
        try:
            validated = schema.load(data or {})
        except Exception as err:
            return error_response(
                SubjectService._format_validation_errors(err),
                status_code=400,
            )

        if not validated:
            return error_response(
                "At least one field is required to update.", status_code=400
            )

        subject = db.session.get(Subject, subject_id)
        if not subject:
            return error_response("Subject not found.", status_code=404)

        if "name" in validated:
            new_name = validated["name"].strip()
            existing = Subject.query.filter_by(name=new_name).first()
            if existing and existing.id != subject.id:
                return error_response("Subject name already exists.", status_code=409)
            subject.name = new_name

        if "description" in validated:
            subject.description = validated["description"]
        if "image" in validated:
            subject.image = validated["image"]

        try:
            db.session.commit()
            return success_response(
                "Subject updated successfully.",
                {"subject": subject.to_dict()},
            )
        except Exception:
            db.session.rollback()
            return error_response(
                "An internal server error occurred.", status_code=500
            )

    @staticmethod
    def delete(subject_id):
        subject = db.session.get(Subject, subject_id)
        if not subject:
            return error_response("Subject not found.", status_code=404)

        try:
            db.session.delete(subject)
            db.session.commit()
            return success_response("Subject deleted successfully.")
        except Exception:
            db.session.rollback()
            return error_response(
                "An internal server error occurred.", status_code=500
            )
