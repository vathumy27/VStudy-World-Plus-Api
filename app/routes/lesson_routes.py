from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.services.lesson_service import LessonService
from app.utils.decorators import role_required

lesson_bp = Blueprint("lessons", __name__, url_prefix="/api/lessons")


@lesson_bp.route("", methods=["GET"])
@jwt_required()
def get_lessons():
    """Return all lessons, optionally filtered by subject_id query param."""
    subject_id = request.args.get("subject_id", type=int)
    return LessonService.get_all(subject_id=subject_id)


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
