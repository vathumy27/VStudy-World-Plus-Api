from flask import Blueprint, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from app.services.chat_service import ChatService

chat_bp = Blueprint("chat", __name__, url_prefix="/api/chat")


@chat_bp.route("/ask", methods=["POST"])
@jwt_required()
def ask():
    """Ask the AI chatbot a question."""
    user_id = get_jwt_identity()
    return ChatService.ask(user_id, request.get_json(silent=True))


@chat_bp.route("/history", methods=["GET"])
@jwt_required()
def get_history():
    """Return chat history for the authenticated user."""
    user_id = get_jwt_identity()
    return ChatService.get_history(user_id)
