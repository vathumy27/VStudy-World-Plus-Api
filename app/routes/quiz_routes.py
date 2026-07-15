from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.services.quiz_service import QuizService

quiz_bp = Blueprint("quiz", __name__, url_prefix="/api/quiz")


@quiz_bp.route("/generate", methods=["POST"])
@jwt_required()
def generate_quiz():
    """Generate an AI-powered quiz."""
    user_id = get_jwt_identity()
    return QuizService.generate(user_id, request.get_json(silent=True))


@quiz_bp.route("/<int:quiz_id>", methods=["GET"])
@jwt_required()
def get_quiz(quiz_id):
    """Return quiz details by ID."""
    return QuizService.get_by_id(quiz_id)


@quiz_bp.route("/submit", methods=["POST"])
@jwt_required()
def submit_quiz():
    """Submit quiz answers and receive score."""
    user_id = get_jwt_identity()
    return QuizService.submit(user_id, request.get_json(silent=True))
