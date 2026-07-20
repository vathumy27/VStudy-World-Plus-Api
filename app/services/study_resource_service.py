from __future__ import annotations

from sqlalchemy import or_

from app.extensions import db
from app.models.lesson import Lesson
from app.models.study_resource import StudyResource
from app.models.subject import Subject
from app.services.study_resource_generator import (
    build_math_resources,
    generate_lesson_notes,
)
from app.utils.search_utils import expand_query_terms, text_matches


NOTE_SUBJECTS = {"history", "geography", "science"}
MATH_ALIASES = {"mathematics", "maths", "math"}


def _subject_key(name: str) -> str:
    return (name or "").strip().lower()


def _apply_payload(resource: StudyResource, payload: dict, *, lesson: Lesson | None = None):
    for field, value in payload.items():
        if hasattr(resource, field):
            setattr(resource, field, value)
    if lesson:
        resource.subject_id = lesson.subject_id
        resource.lesson_id = lesson.id
        resource.grade = int(lesson.grade or 10)
        resource.unit_number = lesson.unit_number
        if payload.get("title"):
            resource.title = payload["title"]
        else:
            resource.title = lesson.title
    resource.language = payload.get("language") or "Tamil"
    resource.resource_type = resource.resource_type or "lesson_notes"


class StudyResourceService:
    """CRUD + generation for AI study resources stored in the local DB."""

    @staticmethod
    def get_by_id(resource_id: int):
        return db.session.get(StudyResource, resource_id)

    @staticmethod
    def get_for_lesson(lesson_id: int):
        return (
            StudyResource.query.filter_by(lesson_id=lesson_id)
            .order_by(StudyResource.id.asc())
            .all()
        )

    @staticmethod
    def search(
        *,
        grade=None,
        subject_id=None,
        subject_name=None,
        unit_number=None,
        resource_type=None,
        q=None,
        page=1,
        per_page=20,
    ):
        query = StudyResource.query

        if grade is not None:
            query = query.filter(StudyResource.grade == int(grade))
        if subject_id is not None:
            query = query.filter(StudyResource.subject_id == int(subject_id))
        if unit_number:
            query = query.filter(StudyResource.unit_number == str(unit_number))
        if resource_type:
            query = query.filter(StudyResource.resource_type == resource_type)

        if subject_name:
            subject = Subject.query.filter(
                Subject.name.ilike(f"%{subject_name}%")
            ).first()
            if subject:
                query = query.filter(StudyResource.subject_id == subject.id)
            else:
                return [], 0

        if q:
            terms = expand_query_terms(q)
            keywords_text = db.cast(StudyResource.keywords, db.String)
            clauses = []
            for term in terms[:20]:
                like = f"%{term}%"
                clauses.append(StudyResource.title.ilike(like))
                clauses.append(StudyResource.short_notes.ilike(like))
                clauses.append(StudyResource.summary.ilike(like))
                clauses.append(StudyResource.revision_notes.ilike(like))
                clauses.append(StudyResource.easy_explanation.ilike(like))
                clauses.append(keywords_text.ilike(like))
            if clauses:
                query = query.filter(or_(*clauses))

        total = query.count()
        page = max(1, int(page or 1))
        per_page = min(100, max(1, int(per_page or 20)))
        items = (
            query.order_by(
                StudyResource.grade.asc(),
                StudyResource.subject_id.asc(),
                StudyResource.unit_number.asc(),
                StudyResource.title.asc(),
            )
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return items, total

    @staticmethod
    def smart_lesson_search(q: str, *, grade=None, subject_id=None, limit=20):
        """
        Search lessons via study resources + lesson titles with bilingual/fuzzy terms.
        Returns lesson dicts with matched Tamil resource title when available.
        """
        terms = expand_query_terms(q)
        if not terms:
            return []

        query = Lesson.query.join(Subject, Lesson.subject_id == Subject.id)
        if grade is not None:
            query = query.filter(Lesson.grade == int(grade))
        if subject_id is not None:
            query = query.filter(Lesson.subject_id == int(subject_id))

        # Fast SQL prefilter with expanded terms
        keywords_text = db.cast(StudyResource.keywords, db.String)
        sql_clauses = []
        for term in terms[:16]:
            like = f"%{term}%"
            sql_clauses.extend(
                [
                    Lesson.title.ilike(like),
                    Lesson.description.ilike(like),
                    Subject.name.ilike(like),
                    StudyResource.title.ilike(like),
                    keywords_text.ilike(like),
                    StudyResource.short_notes.ilike(like),
                ]
            )
        candidates = (
            query.outerjoin(StudyResource, StudyResource.lesson_id == Lesson.id)
            .filter(or_(*sql_clauses))
            .distinct()
            .limit(80)
            .all()
        )

        # If SQL found nothing, broaden to grade-filtered lessons and fuzzy-match in Python
        if not candidates:
            broad = Lesson.query
            if grade is not None:
                broad = broad.filter(Lesson.grade == int(grade))
            if subject_id is not None:
                broad = broad.filter(Lesson.subject_id == int(subject_id))
            candidates = broad.limit(200).all()

        scored = []
        for lesson in candidates:
            resources = StudyResource.query.filter_by(lesson_id=lesson.id).all()
            haystacks = [
                lesson.title,
                lesson.description,
                lesson.subject.name if lesson.subject else "",
            ]
            for res in resources:
                haystacks.extend(
                    [
                        res.title,
                        res.short_notes,
                        res.summary,
                        " ".join(res.keywords or []),
                    ]
                )
            blob = " ".join(h for h in haystacks if h)
            if text_matches(blob, terms):
                tamil_title = next(
                    (r.title for r in resources if r.language == "Tamil"),
                    resources[0].title if resources else lesson.title,
                )
                scored.append(
                    {
                        "id": lesson.id,
                        "title": lesson.title,
                        "display_title": tamil_title,
                        "description": lesson.description,
                        "grade": lesson.grade,
                        "unit_number": lesson.unit_number,
                        "subject_id": lesson.subject_id,
                        "subject": lesson.subject.to_dict() if lesson.subject else None,
                        "has_notes": bool(resources),
                    }
                )
            if len(scored) >= limit:
                break
        return scored

    @staticmethod
    def find_related_resources(question: str, limit: int = 3):
        """Find study resources relevant to an AI question."""
        terms = expand_query_terms(question)
        if not terms:
            return []

        keywords_text = db.cast(StudyResource.keywords, db.String)
        clauses = []
        for term in terms[:16]:
            like = f"%{term}%"
            clauses.extend(
                [
                    StudyResource.title.ilike(like),
                    StudyResource.short_notes.ilike(like),
                    StudyResource.summary.ilike(like),
                    StudyResource.easy_explanation.ilike(like),
                    keywords_text.ilike(like),
                ]
            )
        rows = (
            StudyResource.query.filter(or_(*clauses))
            .order_by(StudyResource.updated_at.desc())
            .limit(40)
            .all()
        )
        matched = []
        for row in rows:
            blob = " ".join(
                [
                    row.title or "",
                    row.short_notes or "",
                    row.summary or "",
                    row.easy_explanation or "",
                    " ".join(row.keywords or []),
                ]
            )
            if text_matches(blob, terms):
                matched.append(row)
            if len(matched) >= limit:
                break
        return matched

    @staticmethod
    def ensure_for_lesson(lesson: Lesson, regenerate: bool = False):
        """Create and store Tamil notes for a History/Geography/Science lesson."""
        if not lesson or not lesson.subject:
            return None

        subject_name = lesson.subject.name
        key = _subject_key(subject_name)
        if key not in NOTE_SUBJECTS:
            return None

        existing = StudyResource.query.filter_by(
            lesson_id=lesson.id, resource_type="lesson_notes"
        ).first()

        # Force refresh when stored notes are still English
        needs_tamil = bool(
            existing
            and (
                (existing.language or "").lower() != "tamil"
                or not existing.easy_explanation
            )
        )
        if existing and not regenerate and not needs_tamil:
            return existing

        payload = generate_lesson_notes(
            title=lesson.title,
            subject_name=subject_name,
            grade=int(lesson.grade or 10),
            unit_number=lesson.unit_number,
        )

        if existing:
            _apply_payload(existing, payload, lesson=lesson)
            existing.resource_type = "lesson_notes"
            db.session.commit()
            return existing

        resource = StudyResource(resource_type="lesson_notes")
        _apply_payload(resource, payload, lesson=lesson)
        db.session.add(resource)
        db.session.commit()
        return resource

    @staticmethod
    def ensure_math_resources(subject: Subject, grade: int, regenerate: bool = False):
        """Store Mathematics resource packs per grade (Tamil, no per-lesson notes)."""
        key = _subject_key(subject.name)
        if key not in MATH_ALIASES and "math" not in key:
            return []

        created = []
        packs = build_math_resources(int(grade))
        for pack in packs:
            existing = StudyResource.query.filter_by(
                subject_id=subject.id,
                lesson_id=None,
                grade=int(grade),
                resource_type=pack["resource_type"],
            ).first()

            needs_tamil = bool(
                existing
                and (
                    (existing.language or "").lower() != "tamil"
                    or not existing.easy_explanation
                )
            )
            if existing and not regenerate and not needs_tamil:
                created.append(existing)
                continue
            if existing:
                _apply_payload(existing, pack)
                existing.resource_type = pack["resource_type"]
                existing.grade = int(grade)
                existing.subject_id = subject.id
                existing.lesson_id = None
                db.session.commit()
                created.append(existing)
                continue

            resource = StudyResource(
                subject_id=subject.id,
                lesson_id=None,
                grade=int(grade),
                resource_type=pack["resource_type"],
            )
            _apply_payload(resource, pack)
            db.session.add(resource)
            created.append(resource)
        db.session.commit()
        return created

    @staticmethod
    def generate_all(*, regenerate: bool = False, grades=(10, 11)):
        stats = {
            "lesson_notes_created": 0,
            "lesson_notes_skipped": 0,
            "math_resources": 0,
            "errors": [],
        }

        subjects = Subject.query.all()
        for subject in subjects:
            key = _subject_key(subject.name)

            if key in MATH_ALIASES or "math" in key:
                for grade in grades:
                    packs = StudyResourceService.ensure_math_resources(
                        subject, grade, regenerate=regenerate
                    )
                    stats["math_resources"] += len(packs)
                continue

            if key not in NOTE_SUBJECTS:
                continue

            lessons = Lesson.query.filter(
                Lesson.subject_id == subject.id,
                Lesson.grade.in_(list(grades)),
            ).all()
            for lesson in lessons:
                try:
                    before = StudyResource.query.filter_by(
                        lesson_id=lesson.id, resource_type="lesson_notes"
                    ).first()
                    was_english = before and (before.language or "").lower() != "tamil"
                    resource = StudyResourceService.ensure_for_lesson(
                        lesson, regenerate=regenerate
                    )
                    if resource and (regenerate or not before or was_english):
                        stats["lesson_notes_created"] += 1
                    else:
                        stats["lesson_notes_skipped"] += 1
                except Exception as exc:  # pragma: no cover
                    stats["errors"].append(
                        {"lesson_id": lesson.id, "error": str(exc)}
                    )

        return stats
