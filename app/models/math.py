from app.extensions import db
from app.utils.time_utils import utc_now


class MathPractice(db.Model):
    """Mathematics practice problem."""

    __tablename__ = "math_practice"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    topic = db.Column(db.String(100), nullable=False, index=True)
    difficulty = db.Column(db.String(20), nullable=False, default="medium")
    problem_text = db.Column(db.Text, nullable=False)
    solution = db.Column(db.Text, nullable=False)
    hints = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)

    solutions = db.relationship(
        "MathSolution", back_populates="practice", cascade="all, delete-orphan"
    )

    def to_dict(self, include_solution=False):
        data = {
            "id": self.id,
            "topic": self.topic,
            "difficulty": self.difficulty,
            "problem_text": self.problem_text,
            "hints": self.hints,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_solution:
            data["solution"] = self.solution
        return data


class MathSolution(db.Model):
    """Student math problem solution attempt."""

    __tablename__ = "math_solutions"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    practice_id = db.Column(
        db.Integer, db.ForeignKey("math_practice.id"), nullable=True, index=True
    )
    problem_text = db.Column(db.Text, nullable=False)
    user_answer = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False, default=False)
    steps = db.Column(db.JSON, nullable=True)
    solved_at = db.Column(db.DateTime, default=utc_now, nullable=False)

    user = db.relationship("User", back_populates="math_solutions")
    practice = db.relationship("MathPractice", back_populates="solutions")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "practice_id": self.practice_id,
            "problem_text": self.problem_text,
            "user_answer": self.user_answer,
            "is_correct": self.is_correct,
            "steps": self.steps,
            "solved_at": self.solved_at.isoformat() if self.solved_at else None,
        }
