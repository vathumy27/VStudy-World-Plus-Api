from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.services.study_resource_service import StudyResourceService
from app.models.lesson import Lesson
from app.models.subject import Subject
from app.utils.response import error_response, success_response

study_resource_bp = Blueprint(
    "study_resources", __name__, url_prefix="/api/study-resources"
)


@study_resource_bp.route("", methods=["GET"])
@jwt_required()
def list_study_resources():
    """Search/filter stored AI study resources."""
    try:
        grade = request.args.get("grade", type=int)
        subject_id = request.args.get("subject_id", type=int)
        subject = request.args.get("subject")
        unit = request.args.get("unit") or request.args.get("unit_number")
        resource_type = request.args.get("resource_type")
        q = request.args.get("q") or request.args.get("search")
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)

        items, total = StudyResourceService.search(
            grade=grade,
            subject_id=subject_id,
            subject_name=subject,
            unit_number=unit,
            resource_type=resource_type,
            q=q,
            page=page,
            per_page=per_page,
        )
        return success_response(
            "Study resources retrieved",
            {
                "items": [r.to_dict(include_subject=True, include_lesson=True) for r in items],
                "total": total,
                "page": page,
                "per_page": per_page,
            },
        )
    except Exception as exc:
        return error_response(f"Failed to load study resources: {exc}", 500)


@study_resource_bp.route("/<int:resource_id>", methods=["GET"])
@jwt_required()
def get_study_resource(resource_id):
    resource = StudyResourceService.get_by_id(resource_id)
    if not resource:
        return error_response("Study resource not found", 404)
    return success_response(
        "Study resource retrieved",
        resource.to_dict(include_lesson=True, include_subject=True),
    )


@study_resource_bp.route("/lesson/<int:lesson_id>", methods=["GET"])
@jwt_required()
def get_resources_for_lesson(lesson_id):
    """Return stored notes for a lesson; generate once if missing (non-Math)."""
    lesson = Lesson.query.get(lesson_id)
    if not lesson:
        return error_response("Lesson not found", 404)

    subject_name = (lesson.subject.name if lesson.subject else "").lower()
    if "math" in subject_name:
        return success_response(
            "Mathematics uses subject-level resources only",
            {
                "lesson_id": lesson_id,
                "resources": [],
                "message": (
                    "Open the Mathematics subject page for textbooks, "
                    "formula sheets, and practice materials."
                ),
            },
        )

    regenerate = request.args.get("regenerate", "false").lower() == "true"
    try:
        StudyResourceService.ensure_for_lesson(lesson, regenerate=regenerate)
    except Exception as exc:
        return error_response(f"Could not prepare study notes: {exc}", 500)

    resources = StudyResourceService.get_for_lesson(lesson_id)
    if not resources:
        return error_response(
            "No study resources available for this lesson yet.",
            404,
        )

    return success_response(
        "Lesson study resources retrieved",
        {
            "lesson_id": lesson_id,
            "resources": [r.to_dict() for r in resources],
        },
    )


@study_resource_bp.route("/subject/<int:subject_id>", methods=["GET"])
@jwt_required()
def get_resources_for_subject(subject_id):
    """List resources for a subject; auto-seed Math packs when needed."""
    subject = Subject.query.get(subject_id)
    if not subject:
        return error_response("Subject not found", 404)

    grade = request.args.get("grade", type=int)
    name = subject.name.lower()

    try:
        if "math" in name:
            grades = [grade] if grade else [10, 11]
            for g in grades:
                StudyResourceService.ensure_math_resources(subject, g)
    except Exception as exc:
        return error_response(f"Could not prepare subject resources: {exc}", 500)

    items, total = StudyResourceService.search(
        subject_id=subject_id,
        grade=grade,
        page=request.args.get("page", 1, type=int),
        per_page=request.args.get("per_page", 50, type=int),
        q=request.args.get("q"),
        unit_number=request.args.get("unit"),
        resource_type=request.args.get("resource_type"),
    )
    return success_response(
        "Subject study resources retrieved",
        {
            "subject_id": subject_id,
            "items": [r.to_dict(include_lesson=True) for r in items],
            "total": total,
        },
    )


@study_resource_bp.route("/smart-search", methods=["GET"])
@jwt_required()
def smart_search_lessons():
    """Bilingual + fuzzy lesson search for the smart search bar."""
    q = (request.args.get("q") or request.args.get("search") or "").strip()
    if not q:
        return error_response("தேடல் சொல்லை உள்ளிடுங்கள்.", 400)
    try:
        grade = request.args.get("grade", type=int)
        subject_id = request.args.get("subject_id", type=int)
        limit = request.args.get("limit", 20, type=int)
        results = StudyResourceService.smart_lesson_search(
            q, grade=grade, subject_id=subject_id, limit=min(50, max(1, limit))
        )
        return success_response(
            "Smart search results",
            {
                "query": q,
                "results": results,
                "total": len(results),
                "ai_fallback": len(results) == 0,
                "ai_hint": (
                    None
                    if results
                    else (
                        "பொருத்தமான பாடம் இல்லை. AI உதவியாளரிடம் இந்தக் கேள்வியைக் கேளுங்கள் — "
                        "கிடைக்கும் படிப்பு வளங்களைக் கொண்டு விளக்கம் தருவார்."
                    )
                ),
            },
        )
    except Exception as exc:
        return error_response(f"தேடல் தோல்வி: {exc}", 500)


@study_resource_bp.route("/generate", methods=["POST"])
@jwt_required()
def generate_all_resources():
    """Admin-style bulk generate into DB (idempotent unless regenerate=true)."""
    data = request.get_json(silent=True) or {}
    regenerate = bool(data.get("regenerate", False))
    grades = data.get("grades") or [10, 11]
    try:
        grades = [int(g) for g in grades]
        stats = StudyResourceService.generate_all(
            regenerate=regenerate, grades=tuple(grades)
        )
        return success_response("Study resources generated", stats)
    except Exception as exc:
        return error_response(f"Generation failed: {exc}", 500)
