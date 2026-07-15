from flask import Blueprint, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from app.services.study_plan_service import StudyPlanService

study_plan_bp = Blueprint("study_plan", __name__, url_prefix="/api/study-plan")


@study_plan_bp.route("/generate", methods=["POST"])
@jwt_required()
def generate_study_plan():
    """Generate an AI-powered exam study plan."""
    user_id = get_jwt_identity()
    return StudyPlanService.generate(user_id, request.get_json(silent=True))


@study_plan_bp.route("/<int:user_id>", methods=["GET"])
@jwt_required()
def get_study_plan(user_id):
    """Return study plans for a user."""
    requester_id = get_jwt_identity()
    requester_role = get_jwt().get("role")
    return StudyPlanService.get_by_user(user_id, requester_id, requester_role)
