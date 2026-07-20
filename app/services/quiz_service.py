import json
import random

from app.extensions import db
from app.models.lesson import Lesson
from app.models.quiz import Quiz, QuizQuestion, QuizResult
from app.models.user import User
from app.schemas.quiz_schema import QuizGenerateSchema, QuizSubmitSchema
from app.utils.openai_client import OpenAIClient
from app.utils.response import error_response, success_response


class QuizService:
    """Business logic for quiz generation and submission."""

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
    def _generate_mock_questions(topic, num_questions):
        questions = []
        for i in range(1, num_questions + 1):
            questions.append(
                {
                    "question_text": f"What is an important concept about {topic}? (Question {i})",
                    "options": {
                        "A": f"Key fact A about {topic}",
                        "B": f"Key fact B about {topic}",
                        "C": f"Key fact C about {topic}",
                        "D": f"Key fact D about {topic}",
                    },
                    "correct_answer": random.choice(["A", "B", "C", "D"]),
                    "points": 1,
                }
            )
        return questions

    @staticmethod
    def generate(user_id, data):
        schema = QuizGenerateSchema()
        try:
            validated = schema.load(data or {})
        except Exception as err:
            return error_response(
                QuizService._format_validation_errors(err),
                status_code=400,
            )

        lesson = None
        topic = validated.get("topic")

        if validated.get("lesson_id"):
            lesson = db.session.get(Lesson, validated["lesson_id"])
            if not lesson:
                return error_response("Lesson not found.", status_code=404)
            topic = lesson.title

        if not topic:
            return error_response(
                "Either lesson_id or topic is required.", status_code=400
            )

        num_questions = validated["num_questions"]
        ai_prompt = (
            f"Generate {num_questions} multiple choice quiz questions about '{topic}'. "
            "Return JSON array with question_text, options (A-D), correct_answer, points."
        )
        ai_response = OpenAIClient.generate_text(
            ai_prompt,
            system_message="You are an educational quiz generator for school students.",
        )

        if ai_response:
            try:
                questions_data = json.loads(ai_response)
            except json.JSONDecodeError:
                questions_data = QuizService._generate_mock_questions(
                    topic, num_questions
                )
        else:
            questions_data = QuizService._generate_mock_questions(
                topic, num_questions
            )

        quiz = Quiz(
            lesson_id=lesson.id if lesson else None,
            user_id=int(user_id),
            title=f"Quiz: {topic}",
            total_questions=len(questions_data),
        )

        try:
            db.session.add(quiz)
            db.session.flush()

            for q_data in questions_data:
                question = QuizQuestion(
                    quiz_id=quiz.id,
                    question_text=q_data["question_text"],
                    options=q_data["options"],
                    correct_answer=q_data["correct_answer"],
                    points=q_data.get("points", 1),
                )
                db.session.add(question)

            db.session.commit()
            return success_response(
                "Quiz generated successfully.",
                {"quiz": quiz.to_dict(include_questions=True)},
                status_code=201,
            )
        except Exception:
            db.session.rollback()
            return error_response(
                "An internal server error occurred.", status_code=500
            )

    @staticmethod
    def get_by_id(quiz_id):
        quiz = db.session.get(Quiz, quiz_id)
        if not quiz:
            return error_response("Quiz not found.", status_code=404)

        return success_response(
            "Quiz retrieved successfully.",
            {"quiz": quiz.to_dict(include_questions=True)},
        )

    @staticmethod
    def submit(user_id, data):
        schema = QuizSubmitSchema()
        try:
            validated = schema.load(data or {})
        except Exception as err:
            return error_response(
                QuizService._format_validation_errors(err),
                status_code=400,
            )

        quiz = db.session.get(Quiz, validated["quiz_id"])
        if not quiz:
            return error_response("Quiz not found.", status_code=404)

        user = db.session.get(User, int(user_id))
        if not user:
            return error_response("User not found.", status_code=404)

        score = 0
        total_score = 0
        evaluated_answers = {}

        for question in quiz.questions:
            total_score += question.points
            q_key = str(question.id)
            user_answer = validated["answers"].get(q_key)
            is_correct = user_answer == question.correct_answer
            if is_correct:
                score += question.points
            evaluated_answers[q_key] = {
                "user_answer": user_answer,
                "correct_answer": question.correct_answer,
                "is_correct": is_correct,
                "points": question.points if is_correct else 0,
            }

        percentage = round((score / total_score * 100), 2) if total_score > 0 else 0.0

        result = QuizResult(
            quiz_id=quiz.id,
            user_id=int(user_id),
            score=score,
            total_score=total_score,
            percentage=percentage,
            answers=evaluated_answers,
        )

        try:
            db.session.add(result)
            db.session.commit()
            return success_response(
                "Quiz submitted successfully.",
                {"result": result.to_dict()},
                status_code=201,
            )
        except Exception:
            db.session.rollback()
            return error_response(
                "An internal server error occurred.", status_code=500
            )
