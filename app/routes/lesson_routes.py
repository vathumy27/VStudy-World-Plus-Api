from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.services.lesson_service import LessonService
from app.utils.decorators import role_required

lesson_bp = Blueprint("lessons", __name__, url_prefix="/api/lessons")


def _filters_from_request():
    return {
        "subject_id": request.args.get("subject_id", type=int),
        "grade": request.args.get("grade", type=int),
        "unit": request.args.get("unit"),
        "language": request.args.get("language"),
        "search": request.args.get("search"),
        "page": request.args.get("page", default=1, type=int),
        "per_page": request.args.get("per_page", default=20, type=int),
    }


@lesson_bp.route("", methods=["GET"])
@jwt_required()
def get_lessons():
    """Return lessons with optional filters and pagination."""
    return LessonService.get_all(**_filters_from_request())


@lesson_bp.route("/grade/<int:grade>", methods=["GET"])
@jwt_required()
def get_lessons_by_grade(grade):
    filters = _filters_from_request()
    filters["grade"] = grade
    return LessonService.get_all(**filters)


@lesson_bp.route("/subject/<string:subject_name>", methods=["GET"])
@jwt_required()
def get_lessons_by_subject_name(subject_name):
    filters = _filters_from_request()
    filters["subject_name"] = subject_name
    return LessonService.get_all(**filters)


@lesson_bp.route("/<int:lesson_id>", methods=["GET"])
@jwt_required()
def get_lesson(lesson_id):
    """Return lesson details by ID."""
    return LessonService.get_by_id(lesson_id)


@lesson_bp.route("", methods=["POST"])
@jwt_required()
@role_required("Teacher", "Admin")
def create_lesson():
    """Create a new lesson (Teacher/Admin only)."""
    return LessonService.create(request.get_json(silent=True))


@lesson_bp.route("/<int:lesson_id>", methods=["PUT"])
@jwt_required()
@role_required("Teacher", "Admin")
def update_lesson(lesson_id):
    """Update a lesson (Teacher/Admin only)."""
    return LessonService.update(lesson_id, request.get_json(silent=True))


@lesson_bp.route("/<int:lesson_id>", methods=["DELETE"])
@jwt_required()
@role_required("Teacher", "Admin")
def delete_lesson(lesson_id):
    """Delete a lesson (Teacher/Admin only)."""
    return LessonService.delete(lesson_id)
