from app.extensions import db
from app.utils.time_utils import utc_now


class Progress(db.Model):
    """Student learning progress tracking."""

    __tablename__ = "progress"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    lesson_id = db.Column(
        db.Integer, db.ForeignKey("lessons.id"), nullable=True, index=True
    )
    subject_id = db.Column(
        db.Integer, db.ForeignKey("subjects.id"), nullable=True, index=True
    )
    status = db.Column(db.String(50), nullable=False, default="in_progress")
    completion_percentage = db.Column(db.Float, nullable=False, default=0.0)
    time_spent_minutes = db.Column(db.Integer, nullable=False, default=0)
    last_accessed_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=utc_now, onupdate=utc_now, nullable=False
    )

    user = db.relationship("User", back_populates="progress_records")
    lesson = db.relationship("Lesson", back_populates="progress_records")
    subject = db.relationship("Subject", back_populates="progress_records")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "lesson_id": self.lesson_id,
            "subject_id": self.subject_id,
            "status": self.status,
            "completion_percentage": self.completion_percentage,
            "time_spent_minutes": self.time_spent_minutes,
            "last_accessed_at": (
                self.last_accessed_at.isoformat() if self.last_accessed_at else None
            ),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
