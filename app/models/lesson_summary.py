from app.extensions import db
from app.utils.time_utils import utc_now


class LessonSummary(db.Model):
    """AI-generated summary stored for a lesson."""

    __tablename__ = "lesson_summaries"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lesson_id = db.Column(
        db.Integer, db.ForeignKey("lessons.id"), nullable=True, index=True
    )
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    summary_text = db.Column(db.Text, nullable=False)
    source_content = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)

    lesson = db.relationship("Lesson", back_populates="summaries")
    user = db.relationship("User", back_populates="lesson_summaries")

    def to_dict(self):
        return {
            "id": self.id,
            "lesson_id": self.lesson_id,
            "user_id": self.user_id,
            "summary_text": self.summary_text,
            "source_content": self.source_content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
