from app.extensions import db
from app.utils.time_utils import utc_now


class StudyPlan(db.Model):
    """AI-generated exam study plan for a student."""

    __tablename__ = "study_plans"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    title = db.Column(db.String(200), nullable=False)
    exam_date = db.Column(db.Date, nullable=True)
    plan_data = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=utc_now, onupdate=utc_now, nullable=False
    )

    user = db.relationship("User", back_populates="study_plans")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "exam_date": (
                self.exam_date.isoformat() if self.exam_date else None
            ),
            "plan_data": self.plan_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
