from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.services.lesson_service import LessonService

content_bp = Blueprint("content", __name__, url_prefix="/api")


def _common_filters():
    return {
        "unit": request.args.get("unit"),
        "language": request.args.get("language"),
        "search": request.args.get("search"),
        "page": request.args.get("page", default=1, type=int),
        "per_page": request.args.get("per_page", default=20, type=int),
    }


@content_bp.route("/grades/<int:grade>", methods=["GET"])
@jwt_required()
def lessons_by_grade(grade):
    filters = _common_filters()
    filters["grade"] = grade
    return LessonService.get_all(**filters)


@content_bp.route("/history", methods=["GET"])
@jwt_required()
def lessons_history():
    filters = _common_filters()
    filters["subject_name"] = "History"
    return LessonService.get_all(**filters)


@content_bp.route("/geography", methods=["GET"])
@jwt_required()
def lessons_geography():
    filters = _common_filters()
    filters["subject_name"] = "Geography"
    return LessonService.get_all(**filters)


@content_bp.route("/mathematics", methods=["GET"])
@jwt_required()
def lessons_mathematics():
    filters = _common_filters()
    filters["subject_name"] = "Mathematics"
    return LessonService.get_all(**filters)


@content_bp.route("/science", methods=["GET"])
@jwt_required()
def lessons_science():
    filters = _common_filters()
    filters["subject_name"] = "Science"
    return LessonService.get_all(**filters)
