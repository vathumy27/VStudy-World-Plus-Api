from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.services.ai_service import AIService

ai_bp = Blueprint("ai", __name__, url_prefix="/api/ai")


@ai_bp.route("/summarize", methods=["POST"])
@jwt_required()
def summarize():
    """Generate a summary from lesson content."""
    user_id = get_jwt_identity()
    return AIService.summarize(request.get_json(silent=True), user_id=user_id)


@ai_bp.route("/explain", methods=["POST"])
@jwt_required()
def explain():
    """Generate an easy explanation for a topic."""
    user_id = get_jwt_identity()
    return AIService.explain(request.get_json(silent=True), user_id=user_id)


@ai_bp.route("/generate-video", methods=["POST"])
@jwt_required()
def generate_video():
    """Generate a story-based history video."""
    user_id = get_jwt_identity()
    return AIService.generate_video(request.get_json(silent=True), user_id=user_id)
