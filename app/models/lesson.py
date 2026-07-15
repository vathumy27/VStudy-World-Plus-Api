from app.extensions import db
from app.utils.time_utils import utc_now


class Lesson(db.Model):
    """Lesson belonging to a subject."""

    __tablename__ = "lessons"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject_id = db.Column(
        db.Integer, db.ForeignKey("subjects.id"), nullable=False, index=True
    )
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    content = db.Column(db.Text, nullable=True)
    summary = db.Column(db.Text, nullable=True)
    video_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=utc_now, onupdate=utc_now, nullable=False
    )

    subject = db.relationship("Subject", back_populates="lessons")
    videos = db.relationship(
        "LessonVideo", back_populates="lesson", cascade="all, delete-orphan"
    )
    summaries = db.relationship(
        "LessonSummary", back_populates="lesson", cascade="all, delete-orphan"
    )
    quizzes = db.relationship(
        "Quiz", back_populates="lesson", cascade="all, delete-orphan"
    )
    progress_records = db.relationship(
        "Progress", back_populates="lesson", cascade="all, delete-orphan"
    )

    def to_dict(self, include_subject=False):
        """Serialize lesson data."""
        data = {
            "id": self.id,
            "subject_id": self.subject_id,
            "title": self.title,
            "description": self.description,
            "content": self.content,
            "summary": self.summary,
            "video_url": self.video_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_subject and self.subject:
            data["subject"] = self.subject.to_dict()
        return data
