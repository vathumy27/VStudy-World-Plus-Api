from flask import Flask, jsonify
from flask_cors import CORS
from sqlalchemy.exc import OperationalError, ProgrammingError

from app.config import Config
from app.extensions import db, jwt, jwt_blocklist, migrate
from app.routes import register_blueprints
from app.utils.logger import setup_logging


def create_app():
    """Application factory for VStudy World Plus API."""
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    setup_logging(app)

    from app.models import (  # noqa: F401
        ChatHistory,
        GeographyActivity,
        Lesson,
        LessonSummary,
        LessonVideo,
        MapSubmission,
        MathPractice,
        MathSolution,
        Progress,
        Quiz,
        QuizQuestion,
        QuizResult,
        StudyPlan,
        Subject,
        User,
    )

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(_jwt_header, jwt_payload):
        return jwt_payload["jti"] in jwt_blocklist

    @jwt.expired_token_loader
    def expired_token_callback(_jwt_header, _jwt_payload):
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Token has expired. Please log in again.",
                    "data": {},
                }
            ),
            401,
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(_error):
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Invalid authentication token.",
                    "data": {},
                }
            ),
            401,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(_error):
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Authorization token is required.",
                    "data": {},
                }
            ),
            401,
        )

    register_blueprints(app)

    @app.route("/", methods=["GET"])
    def api_home():
        return jsonify(
            {
                "success": True,
                "message": "Welcome to VStudy World Plus API",
                "data": {
                    "project": "VStudy World Plus",
                    "tagline": "Learn Smarter. Understand Better.",
                    "version": "1.0.0",
                    "endpoints": {
                        "auth": {
                            "register": "POST /api/auth/register",
                            "login": "POST /api/auth/login",
                            "me": "GET /api/auth/me",
                            "profile": "PUT /api/auth/profile",
                            "email": "PUT /api/auth/email",
                            "password": "PUT /api/auth/password",
                            "logout": "POST /api/auth/logout",
                        },
                        "subjects": "/api/subjects",
                        "lessons": "/api/lessons",
                        "ai": {
                            "summarize": "POST /api/ai/summarize",
                            "explain": "POST /api/ai/explain",
                            "generate_video": "POST /api/ai/generate-video",
                        },
                        "quiz": {
                            "generate": "POST /api/quiz/generate",
                            "get": "GET /api/quiz/<id>",
                            "submit": "POST /api/quiz/submit",
                        },
                        "progress": {
                            "get": "GET /api/progress/<userId>",
                            "update": "POST /api/progress/update",
                        },
                        "geography": {
                            "maps": "GET /api/geo/maps",
                            "marking": "POST /api/geo/marking",
                            "activities": "GET /api/geo/activities",
                        },
                        "math": {
                            "solve": "POST /api/math/solve",
                            "practice": "GET /api/math/practice",
                            "check": "POST /api/math/check",
                        },
                        "study_plan": {
                            "generate": "POST /api/study-plan/generate",
                            "get": "GET /api/study-plan/<userId>",
                        },
                        "chat": {
                            "ask": "POST /api/chat/ask",
                            "history": "GET /api/chat/history",
                        },
                    },
                },
            }
        )

    @app.errorhandler(404)
    def not_found(_error):
        return (
            jsonify(
                {
                    "success": False,
                    "message": "The requested resource was not found.",
                    "data": {},
                }
            ),
            404,
        )

    @app.errorhandler(405)
    def method_not_allowed(_error):
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Method not allowed for this endpoint.",
                    "data": {},
                }
            ),
            405,
        )

    @app.errorhandler(OperationalError)
    def handle_operational_error(err):
        db.session.rollback()
        orig = getattr(err, "orig", None)
        code = orig.args[0] if orig and orig.args else None
        if code == 1049:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Invalid database name configured.",
                        "data": {},
                    }
                ),
                500,
            )
        if code in (2003, 2002):
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "MySQL server is not running or not reachable.",
                        "data": {},
                    }
                ),
                503,
            )
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Database connection failed.",
                    "data": {},
                }
            ),
            500,
        )

    @app.errorhandler(ProgrammingError)
    def handle_programming_error(_err):
        db.session.rollback()
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Database schema error. Run migrations.",
                    "data": {},
                }
            ),
            500,
        )

    @app.errorhandler(500)
    def handle_internal_error(_err):
        return (
            jsonify(
                {
                    "success": False,
                    "message": "An internal server error occurred.",
                    "data": {},
                }
            ),
            500,
        )

    return app
