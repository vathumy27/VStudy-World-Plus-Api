from app.extensions import db
from app.models.math import MathPractice, MathSolution
from app.schemas.math_schema import MathCheckSchema, MathSolveSchema
from app.utils.openai_client import OpenAIClient
from app.utils.response import error_response, success_response


class MathService:
    """Business logic for mathematics learning support."""

    DEFAULT_PRACTICE = [
        {
            "topic": "algebra",
            "difficulty": "easy",
            "problem_text": "Solve for x: 2x + 5 = 15",
            "solution": "x = 5",
            "hints": ["Subtract 5 from both sides", "Divide both sides by 2"],
        },
        {
            "topic": "geometry",
            "difficulty": "medium",
            "problem_text": "Find the area of a rectangle with length 8 cm and width 5 cm.",
            "solution": "40 cm²",
            "hints": ["Area = length × width"],
        },
        {
            "topic": "arithmetic",
            "difficulty": "easy",
            "problem_text": "What is 15% of 200?",
            "solution": "30",
            "hints": ["Convert percentage to decimal: 0.15 × 200"],
        },
    ]

    @staticmethod
    def _format_validation_errors(err):
        messages = []
        raw = getattr(err, "messages", None)
        if isinstance(raw, dict):
            for field, field_errors in raw.items():
                errors = field_errors if isinstance(field_errors, (list, tuple)) else [field_errors]
                for message in errors:
                    messages.append(f"{field}: {message}")
            return "; ".join(messages)
        return str(err)

    @staticmethod
    def _normalize_answer(answer):
        return answer.strip().lower().replace(" ", "")

    @staticmethod
    def _ensure_practice_problems():
        if MathPractice.query.count() == 0:
            for item in MathService.DEFAULT_PRACTICE:
                practice = MathPractice(**item)
                db.session.add(practice)
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()

    @staticmethod
    def solve(user_id, data):
        schema = MathSolveSchema()
        try:
            validated = schema.load(data or {})
        except Exception as err:
            return error_response(
                MathService._format_validation_errors(err),
                status_code=400,
            )

        problem = validated["problem_text"].strip()
        show_steps = validated["show_steps"]

        ai_prompt = (
            f"Solve this math problem step by step for a school student: {problem}"
        )
        ai_solution = OpenAIClient.generate_text(
            ai_prompt,
            system_message="You are a helpful math tutor for school students.",
        )

        if ai_solution:
            solution_text = ai_solution
            steps = solution_text.split("\n") if show_steps else None
        else:
            solution_text = (
                f"To solve '{problem}', identify the operation type, "
                "apply the correct formula or method, and simplify step by step."
            )
            steps = [
                "Step 1: Read the problem carefully and identify what is asked.",
                "Step 2: Choose the appropriate formula or method.",
                "Step 3: Substitute values and calculate.",
                "Step 4: Verify your answer makes sense.",
            ] if show_steps else None

        record = MathSolution(
            user_id=int(user_id),
            practice_id=None,
            problem_text=problem,
            user_answer="",
            is_correct=False,
            steps=steps,
        )

        try:
            db.session.add(record)
            db.session.commit()
            return success_response(
                "Math problem solved successfully.",
                {
                    "problem": problem,
                    "solution": solution_text,
                    "steps": steps,
                    "solution_id": record.id,
                },
            )
        except Exception:
            db.session.rollback()
            return error_response(
                "An internal server error occurred.", status_code=500
            )

    @staticmethod
    def get_practice(topic=None, difficulty=None):
        MathService._ensure_practice_problems()

        practices = MathPractice.query
        if topic:
            practices = practices.filter_by(topic=topic)
        if difficulty:
            practices = practices.filter_by(difficulty=difficulty)

        results = practices.order_by(MathPractice.created_at.desc()).all()
        return success_response(
            "Math practice problems retrieved successfully.",
            {"problems": [p.to_dict() for p in results]},
        )

    @staticmethod
    def check_answer(user_id, data):
        schema = MathCheckSchema()
        try:
            validated = schema.load(data or {})
        except Exception as err:
            return error_response(
                MathService._format_validation_errors(err),
                status_code=400,
            )

        correct_answer = None
        practice = None

        if validated.get("practice_id"):
            practice = db.session.get(MathPractice, validated["practice_id"])
            if not practice:
                return error_response(
                    "Practice problem not found.", status_code=404
                )
            correct_answer = practice.solution

        user_answer = validated["user_answer"].strip()
        problem = validated["problem_text"].strip()

        if not correct_answer:
            ai_prompt = (
                f"What is the correct answer to: {problem}? "
                "Reply with only the final answer."
            )
            correct_answer = OpenAIClient.generate_text(ai_prompt) or "See solution steps"

        is_correct = (
            MathService._normalize_answer(user_answer)
            == MathService._normalize_answer(correct_answer)
        )

        feedback = (
            "Correct! Well done."
            if is_correct
            else f"Incorrect. The correct answer is: {correct_answer}"
        )

        record = MathSolution(
            user_id=int(user_id),
            practice_id=practice.id if practice else None,
            problem_text=problem,
            user_answer=user_answer,
            is_correct=is_correct,
            steps=None,
        )

        try:
            db.session.add(record)
            db.session.commit()
            return success_response(
                "Answer checked successfully.",
                {
                    "is_correct": is_correct,
                    "user_answer": user_answer,
                    "correct_answer": correct_answer,
                    "feedback": feedback,
                    "solution_id": record.id,
                },
            )
        except Exception:
            db.session.rollback()
            return error_response(
                "An internal server error occurred.", status_code=500
            )
