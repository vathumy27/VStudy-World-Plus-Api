from app.extensions import db
from app.utils.time_utils import utc_now


class LessonVideo(db.Model):
    """AI-generated or uploaded video for a lesson."""

    __tablename__ = "lesson_videos"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lesson_id = db.Column(
        db.Integer, db.ForeignKey("lessons.id"), nullable=False, index=True
    )
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    title = db.Column(db.String(200), nullable=False)
    video_url = db.Column(db.String(500), nullable=False)
    duration_seconds = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)

    lesson = db.relationship("Lesson", back_populates="videos")
    user = db.relationship("User", back_populates="lesson_videos")

    def to_dict(self):
        return {
            "id": self.id,
            "lesson_id": self.lesson_id,
            "user_id": self.user_id,
            "title": self.title,
            "video_url": self.video_url,
            "duration_seconds": self.duration_seconds,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
