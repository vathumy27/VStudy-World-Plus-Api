from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.services.math_service import MathService

math_bp = Blueprint("math", __name__, url_prefix="/api/math")


@math_bp.route("/solve", methods=["POST"])
@jwt_required()
def solve():
    """Solve a mathematics problem with step-by-step explanation."""
    user_id = get_jwt_identity()
    return MathService.solve(user_id, request.get_json(silent=True))


@math_bp.route("/practice", methods=["GET"])
@jwt_required()
def get_practice():
    """Return math practice problems."""
    topic = request.args.get("topic")
    difficulty = request.args.get("difficulty")
    return MathService.get_practice(topic=topic, difficulty=difficulty)


@math_bp.route("/check", methods=["POST"])
@jwt_required()
def check_answer():
    """Check a student's math answer."""
    user_id = get_jwt_identity()
    return MathService.check_answer(user_id, request.get_json(silent=True))
