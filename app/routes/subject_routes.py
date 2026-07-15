from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.services.subject_service import SubjectService
from app.utils.decorators import role_required

subject_bp = Blueprint("subjects", __name__, url_prefix="/api/subjects")


@subject_bp.route("", methods=["GET"])
@jwt_required()
def get_subjects():
    """Return all subjects."""
    return SubjectService.get_all()


@subject_bp.route("/<int:subject_id>", methods=["GET"])
@jwt_required()
def get_subject(subject_id):
    """Return a single subject by ID."""
    return SubjectService.get_by_id(subject_id)


@subject_bp.route("", methods=["POST"])
@jwt_required()
@role_required("Teacher", "Admin")
def create_subject():
    """Create a new subject (Teacher/Admin only)."""
    return SubjectService.create(request.get_json(silent=True))


@subject_bp.route("/<int:subject_id>", methods=["PUT"])
@jwt_required()
@role_required("Teacher", "Admin")
def update_subject(subject_id):
    """Update a subject (Teacher/Admin only)."""
    return SubjectService.update(subject_id, request.get_json(silent=True))


@subject_bp.route("/<int:subject_id>", methods=["DELETE"])
@jwt_required()
@role_required("Teacher", "Admin")
def delete_subject(subject_id):
    """Delete a subject (Teacher/Admin only)."""
    return SubjectService.delete(subject_id)
