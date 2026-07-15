import bcrypt

from app.extensions import db
from app.utils.time_utils import utc_now


class User(db.Model):
    """User account for students, teachers, and admins."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True, index=True)
    password = db.Column(db.String(255), nullable=False)
    school = db.Column(db.String(150), nullable=True)
    grade = db.Column(db.String(20), nullable=True)
    role = db.Column(db.String(20), nullable=False, default="Student")
    profile_image = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=utc_now, onupdate=utc_now, nullable=False
    )

    lesson_videos = db.relationship("LessonVideo", back_populates="user")
    lesson_summaries = db.relationship("LessonSummary", back_populates="user")
    quizzes = db.relationship("Quiz", back_populates="user")
    quiz_results = db.relationship("QuizResult", back_populates="user")
    progress_records = db.relationship("Progress", back_populates="user")
    study_plans = db.relationship("StudyPlan", back_populates="user")
    chat_history = db.relationship("ChatHistory", back_populates="user")
    map_submissions = db.relationship("MapSubmission", back_populates="user")
    math_solutions = db.relationship("MathSolution", back_populates="user")

    def set_password(self, plain_password):
        """Hash and store the user's password using bcrypt."""
        salt = bcrypt.gensalt()
        self.password = bcrypt.hashpw(
            plain_password.encode("utf-8"), salt
        ).decode("utf-8")

    def check_password(self, plain_password):
        """Verify a plain-text password against the stored bcrypt hash."""
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), self.password.encode("utf-8")
        )

    def to_dict(self):
        """Serialize user data (excludes password)."""
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "school": self.school,
            "grade": self.grade,
            "role": self.role,
            "profile_image": self.profile_image,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
