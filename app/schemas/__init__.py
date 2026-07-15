from app.schemas.ai_schema import ExplainSchema, GenerateVideoSchema, SummarizeSchema
from app.schemas.chat_schema import ChatAskSchema
from app.schemas.geography_schema import MapMarkingSchema
from app.schemas.lesson_schema import (
    LessonCreateSchema,
    LessonSchema,
    LessonUpdateSchema,
)
from app.schemas.math_schema import MathCheckSchema, MathSolveSchema
from app.schemas.progress_schema import ProgressUpdateSchema
from app.schemas.quiz_schema import QuizGenerateSchema, QuizSubmitSchema
from app.schemas.study_plan_schema import StudyPlanGenerateSchema
from app.schemas.subject_schema import (
    SubjectCreateSchema,
    SubjectSchema,
    SubjectUpdateSchema,
)
from app.schemas.user_schema import (
    LoginSchema,
    ProfileUpdateSchema,
    RegisterSchema,
    UserSchema,
)

__all__ = [
    "RegisterSchema",
    "LoginSchema",
    "ProfileUpdateSchema",
    "UserSchema",
    "SubjectSchema",
    "SubjectCreateSchema",
    "SubjectUpdateSchema",
    "LessonSchema",
    "LessonCreateSchema",
    "LessonUpdateSchema",
    "SummarizeSchema",
    "ExplainSchema",
    "GenerateVideoSchema",
    "QuizGenerateSchema",
    "QuizSubmitSchema",
    "ProgressUpdateSchema",
    "MapMarkingSchema",
    "MathSolveSchema",
    "MathCheckSchema",
    "StudyPlanGenerateSchema",
    "ChatAskSchema",
]
