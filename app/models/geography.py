from app.extensions import db
from app.utils.time_utils import utc_now


class GeographyActivity(db.Model):
    """Interactive geography map activity."""

    __tablename__ = "geography_activities"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    map_type = db.Column(db.String(50), nullable=False, default="world")
    difficulty = db.Column(db.String(20), nullable=False, default="medium")
    activity_data = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)

    submissions = db.relationship(
        "MapSubmission", back_populates="activity", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "map_type": self.map_type,
            "difficulty": self.difficulty,
            "activity_data": self.activity_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class MapSubmission(db.Model):
    """Student map marking submission for a geography activity."""

    __tablename__ = "map_submissions"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    activity_id = db.Column(
        db.Integer,
        db.ForeignKey("geography_activities.id"),
        nullable=False,
        index=True,
    )
    markings = db.Column(db.JSON, nullable=False)
    score = db.Column(db.Float, nullable=False, default=0.0)
    feedback = db.Column(db.Text, nullable=True)
    submitted_at = db.Column(db.DateTime, default=utc_now, nullable=False)

    user = db.relationship("User", back_populates="map_submissions")
    activity = db.relationship("GeographyActivity", back_populates="submissions")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "activity_id": self.activity_id,
            "markings": self.markings,
            "score": self.score,
            "feedback": self.feedback,
            "submitted_at": (
                self.submitted_at.isoformat() if self.submitted_at else None
            ),
        }
