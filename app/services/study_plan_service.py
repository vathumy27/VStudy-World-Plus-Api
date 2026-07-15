from datetime import date, timedelta

from app.extensions import db
from app.models.study_plan import StudyPlan
from app.models.user import User
from app.schemas.study_plan_schema import StudyPlanGenerateSchema
from app.utils.openai_client import OpenAIClient
from app.utils.response import error_response, success_response


class StudyPlanService:
    """Business logic for exam study plan generation."""

    @staticmethod
    def _format_validation_errors(err):
        messages = []
        for field, field_errors in err.messages.items():
            for message in field_errors:
                messages.append(f"{field}: {message}")
        return "; ".join(messages)

    @staticmethod
    def _generate_mock_plan(title, exam_date, subjects, hours_per_day, focus_areas):
        days_until_exam = 14
        if exam_date:
            delta = (exam_date - date.today()).days
            days_until_exam = max(delta, 1)

        schedule = []
        subject_list = subjects or ["General Revision"]
        for day in range(1, min(days_until_exam + 1, 15)):
            subject = subject_list[(day - 1) % len(subject_list)]
            schedule.append(
                {
                    "day": day,
                    "date": (date.today() + timedelta(days=day - 1)).isoformat(),
                    "subject": subject,
                    "topics": focus_areas or [f"{subject} - Chapter {day}"],
                    "hours": hours_per_day,
                    "tasks": [
                        f"Review {subject} notes",
                        "Practice past paper questions",
                        "Use AI quiz for self-assessment",
                    ],
                }
            )

        return {
            "title": title,
            "total_days": len(schedule),
            "hours_per_day": hours_per_day,
            "subjects": subject_list,
            "focus_areas": focus_areas,
            "schedule": schedule,
            "tips": [
                "Study in short focused sessions",
                "Take breaks every 45 minutes",
                "Review mistakes from quizzes daily",
                "Sleep well before the exam",
            ],
        }

    @staticmethod
    def generate(user_id, data):
        schema = StudyPlanGenerateSchema()
        try:
            validated = schema.load(data or {})
        except Exception as err:
            return error_response(
                StudyPlanService._format_validation_errors(err),
                status_code=400,
            )

        user = db.session.get(User, int(user_id))
        if not user:
            return error_response("User not found.", status_code=404)

        title = validated["title"].strip()
        exam_date = validated.get("exam_date")
        subjects = validated.get("subjects", [])
        hours_per_day = validated["hours_per_day"]
        focus_areas = validated.get("focus_areas", [])

        ai_prompt = (
            f"Create a study plan titled '{title}' for exam on {exam_date}. "
            f"Subjects: {subjects}. Focus: {focus_areas}. "
            f"Study {hours_per_day} hours per day. Return structured JSON."
        )
        ai_plan = OpenAIClient.generate_text(
            ai_prompt,
            system_message="You are an exam preparation coach for school students.",
        )

        if ai_plan:
            try:
                import json

                plan_data = json.loads(ai_plan)
            except Exception:
                plan_data = StudyPlanService._generate_mock_plan(
                    title, exam_date, subjects, hours_per_day, focus_areas
                )
        else:
            plan_data = StudyPlanService._generate_mock_plan(
                title, exam_date, subjects, hours_per_day, focus_areas
            )

        study_plan = StudyPlan(
            user_id=int(user_id),
            title=title,
            exam_date=exam_date,
            plan_data=plan_data,
        )

        try:
            db.session.add(study_plan)
            db.session.commit()
            return success_response(
                "Study plan generated successfully.",
                {"study_plan": study_plan.to_dict()},
                status_code=201,
            )
        except Exception:
            db.session.rollback()
            return error_response(
                "An internal server error occurred.", status_code=500
            )

    @staticmethod
    def get_by_user(user_id, requester_id, requester_role):
        target_user_id = int(user_id)
        requester_id = int(requester_id)

        if target_user_id != requester_id and requester_role not in (
            "Teacher",
            "Admin",
        ):
            return error_response(
                "You do not have permission to view this study plan.",
                status_code=403,
            )

        user = db.session.get(User, target_user_id)
        if not user:
            return error_response("User not found.", status_code=404)

        plans = (
            StudyPlan.query.filter_by(user_id=target_user_id)
            .order_by(StudyPlan.created_at.desc())
            .all()
        )

        return success_response(
            "Study plans retrieved successfully.",
            {"study_plans": [plan.to_dict() for plan in plans]},
        )
