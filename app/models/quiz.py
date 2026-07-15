from app.extensions import db
from app.utils.time_utils import utc_now


class Quiz(db.Model):
    """Quiz generated for a lesson or topic."""

    __tablename__ = "quizzes"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lesson_id = db.Column(
        db.Integer, db.ForeignKey("lessons.id"), nullable=True, index=True
    )
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    title = db.Column(db.String(200), nullable=False)
    total_questions = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)

    lesson = db.relationship("Lesson", back_populates="quizzes")
    user = db.relationship("User", back_populates="quizzes")
    questions = db.relationship(
        "QuizQuestion", back_populates="quiz", cascade="all, delete-orphan"
    )
    results = db.relationship(
        "QuizResult", back_populates="quiz", cascade="all, delete-orphan"
    )

    def to_dict(self, include_questions=False):
        data = {
            "id": self.id,
            "lesson_id": self.lesson_id,
            "user_id": self.user_id,
            "title": self.title,
            "total_questions": self.total_questions,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_questions:
            data["questions"] = [q.to_dict() for q in self.questions]
        return data


class QuizQuestion(db.Model):
    """Individual question within a quiz."""

    __tablename__ = "quiz_questions"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quiz_id = db.Column(
        db.Integer, db.ForeignKey("quizzes.id"), nullable=False, index=True
    )
    question_text = db.Column(db.Text, nullable=False)
    options = db.Column(db.JSON, nullable=False)
    correct_answer = db.Column(db.String(255), nullable=False)
    points = db.Column(db.Integer, nullable=False, default=1)

    quiz = db.relationship("Quiz", back_populates="questions")

    def to_dict(self, include_answer=False):
        data = {
            "id": self.id,
            "quiz_id": self.quiz_id,
            "question_text": self.question_text,
            "options": self.options,
            "points": self.points,
        }
        if include_answer:
            data["correct_answer"] = self.correct_answer
        return data


class QuizResult(db.Model):
    """Student quiz submission and score."""

    __tablename__ = "quiz_results"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quiz_id = db.Column(
        db.Integer, db.ForeignKey("quizzes.id"), nullable=False, index=True
    )
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    score = db.Column(db.Integer, nullable=False, default=0)
    total_score = db.Column(db.Integer, nullable=False, default=0)
    percentage = db.Column(db.Float, nullable=False, default=0.0)
    answers = db.Column(db.JSON, nullable=False)
    submitted_at = db.Column(db.DateTime, default=utc_now, nullable=False)

    quiz = db.relationship("Quiz", back_populates="results")
    user = db.relationship("User", back_populates="quiz_results")

    def to_dict(self):
        return {
            "id": self.id,
            "quiz_id": self.quiz_id,
            "user_id": self.user_id,
            "score": self.score,
            "total_score": self.total_score,
            "percentage": self.percentage,
            "answers": self.answers,
            "submitted_at": (
                self.submitted_at.isoformat() if self.submitted_at else None
            ),
        }
