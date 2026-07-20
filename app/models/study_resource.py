from app.extensions import db
from app.utils.time_utils import utc_now


class StudyResource(db.Model):
    """
    Original AI study materials for Grade 10/11 lessons (Tamil).

    - History / Geography / Science → lesson-linked notes
    - Mathematics → subject-level resources only (no lesson notes)
    """

    __tablename__ = "study_resources"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject_id = db.Column(
        db.Integer, db.ForeignKey("subjects.id"), nullable=False, index=True
    )
    lesson_id = db.Column(
        db.Integer, db.ForeignKey("lessons.id"), nullable=True, index=True
    )

    grade = db.Column(db.Integer, nullable=False, index=True)
    unit_number = db.Column(db.String(50), nullable=True, index=True)
    title = db.Column(db.String(250), nullable=False)
    resource_type = db.Column(
        db.String(50), nullable=False, default="lesson_notes", index=True
    )

    short_notes = db.Column(db.Text, nullable=True)
    easy_explanation = db.Column(db.Text, nullable=True)
    key_points = db.Column(db.JSON, nullable=True)
    definitions = db.Column(db.JSON, nullable=True)
    dates = db.Column(db.JSON, nullable=True)
    maps_locations = db.Column(db.JSON, nullable=True)
    scientific_concepts = db.Column(db.JSON, nullable=True)
    formulae = db.Column(db.JSON, nullable=True)
    summary = db.Column(db.Text, nullable=True)
    exam_tips = db.Column(db.JSON, nullable=True)
    study_tips = db.Column(db.JSON, nullable=True)
    important_questions = db.Column(db.JSON, nullable=True)
    revision_notes = db.Column(db.Text, nullable=True)
    keywords = db.Column(db.JSON, nullable=True)
    resource_links = db.Column(db.JSON, nullable=True)

    language = db.Column(db.String(20), nullable=True, default="Tamil")
    generated_by = db.Column(db.String(50), nullable=True, default="vstudy_ai")

    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=utc_now, onupdate=utc_now, nullable=False
    )

    subject = db.relationship("Subject", backref="study_resources")
    lesson = db.relationship("Lesson", backref="study_resources")

    def to_dict(self, include_lesson=False, include_subject=False):
        data = {
            "id": self.id,
            "subject_id": self.subject_id,
            "lesson_id": self.lesson_id,
            "grade": self.grade,
            "unit_number": self.unit_number,
            "title": self.title,
            "resource_type": self.resource_type,
            "short_notes": self.short_notes,
            "easy_explanation": self.easy_explanation,
            "key_points": self.key_points or [],
            "definitions": self.definitions or [],
            "dates": self.dates or [],
            "maps_locations": self.maps_locations or [],
            "scientific_concepts": self.scientific_concepts or [],
            "formulae": self.formulae or [],
            "summary": self.summary,
            "exam_tips": self.exam_tips or [],
            "study_tips": self.study_tips or [],
            "important_questions": self.important_questions or [],
            "revision_notes": self.revision_notes,
            "keywords": self.keywords or [],
            "resource_links": self.resource_links or [],
            "language": self.language,
            "generated_by": self.generated_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_lesson and self.lesson:
            data["lesson"] = {
                "id": self.lesson.id,
                "title": self.lesson.title,
                "grade": self.lesson.grade,
                "unit_number": self.lesson.unit_number,
            }
        if include_subject and self.subject:
            data["subject"] = self.subject.to_dict()
        return data
