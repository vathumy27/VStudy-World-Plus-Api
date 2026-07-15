from flask import Blueprint, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from app.services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new student account."""
    return AuthService.register(request.get_json(silent=True))


@auth_bp.route("/login", methods=["POST"])
def login():
    """Authenticate user and return JWT access token."""
    return AuthService.login(request.get_json(silent=True))


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_me():
    """Return the currently authenticated user."""
    user_id = get_jwt_identity()
    return AuthService.get_current_user(user_id)


@auth_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    """Update the authenticated user's profile."""
    user_id = get_jwt_identity()
    return AuthService.update_profile(user_id, request.get_json(silent=True))


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """Logout user by invalidating the current JWT."""
    jti = get_jwt()["jti"]
    return AuthService.logout(jti)
