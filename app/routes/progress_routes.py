from flask import Blueprint, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from app.services.progress_service import ProgressService

progress_bp = Blueprint("progress", __name__, url_prefix="/api/progress")


@progress_bp.route("/<int:user_id>", methods=["GET"])
@jwt_required()
def get_progress(user_id):
    """Return learning progress for a user."""
    requester_id = get_jwt_identity()
    requester_role = get_jwt().get("role")
    return ProgressService.get_by_user(user_id, requester_id, requester_role)


@progress_bp.route("/update", methods=["POST"])
@jwt_required()
def update_progress():
    """Update learning progress for the authenticated user."""
    user_id = get_jwt_identity()
    return ProgressService.update(user_id, request.get_json(silent=True))
