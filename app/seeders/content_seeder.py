"""Seed sample subjects and lessons for local demos."""

from app.extensions import db
from app.models.lesson import Lesson
from app.models.subject import Subject

SAMPLE_SUBJECTS = [
    {
        "name": "Mathematics",
        "description": "Algebra, geometry, and problem solving for O/L and A/L.",
        "image": "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=800",
        "lessons": [
            {
                "title": "Introduction to Algebra",
                "description": "Variables, expressions, and simple equations.",
                "content": "Algebra uses letters to represent unknown numbers. An equation keeps both sides equal. Example: 2x + 4 = 10 means x = 3.",
            },
            {
                "title": "Linear Equations",
                "description": "Solve one-variable linear equations step by step.",
                "content": "To solve ax + b = c, isolate x: ax = c - b, then x = (c - b) / a. Always check by substitution.",
            },
        ],
    },
    {
        "name": "Geography",
        "description": "Maps, climate, and earth systems.",
        "image": "https://images.unsplash.com/photo-1526778548025-fa2f459cd5c1?w=800",
        "lessons": [
            {
                "title": "Reading Maps",
                "description": "Latitude, longitude, and map symbols.",
                "content": "Latitude lines run east-west. Longitude lines run north-south. The equator is 0 degrees latitude.",
            }
        ],
    },
    {
        "name": "History",
        "description": "World and Sri Lankan history highlights.",
        "image": "https://images.unsplash.com/photo-1461360370896-922624d12aa1?w=800",
        "lessons": [
            {
                "title": "Ancient Civilizations",
                "description": "Early societies and how they shaped the modern world.",
                "content": "Ancient civilizations developed writing, farming, and cities. Studying them helps us understand culture and change over time.",
            }
        ],
    },
]


def seed_sample_content() -> dict:
    created_subjects = 0
    created_lessons = 0

    for item in SAMPLE_SUBJECTS:
        subject = Subject.query.filter_by(name=item["name"]).first()
        if not subject:
            subject = Subject(
                name=item["name"],
                description=item["description"],
                image=item["image"],
            )
            db.session.add(subject)
            db.session.flush()
            created_subjects += 1

        for lesson_data in item["lessons"]:
            existing = Lesson.query.filter_by(
                subject_id=subject.id, title=lesson_data["title"]
            ).first()
            if existing:
                continue
            lesson = Lesson(
                subject_id=subject.id,
                title=lesson_data["title"],
                description=lesson_data["description"],
                content=lesson_data["content"],
            )
            db.session.add(lesson)
            created_lessons += 1

    db.session.commit()
    return {
        "subjects_created": created_subjects,
        "lessons_created": created_lessons,
        "subjects_total": Subject.query.count(),
        "lessons_total": Lesson.query.count(),
    }
