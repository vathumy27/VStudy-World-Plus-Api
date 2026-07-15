from marshmallow import Schema, ValidationError, fields, validates, validates_schema


class QuizGenerateSchema(Schema):
    """Schema for AI quiz generation request."""

    lesson_id = fields.Int(load_default=None)
    topic = fields.Str(load_default=None)
    num_questions = fields.Int(load_default=5)

    @validates_schema
    def validate_lesson_or_topic(self, data, **_kwargs):
        if not data.get("lesson_id") and not data.get("topic"):
            raise ValidationError(
                "Either lesson_id or topic is required.",
                field_name="topic",
            )

    @validates("num_questions")
    def validate_num_questions(self, value):
        if value < 1 or value > 20:
            raise ValidationError("Number of questions must be between 1 and 20.")

    @validates("topic")
    def validate_topic(self, value):
        if value is not None and not value.strip():
            raise ValidationError("Topic cannot be empty.")


class QuizSubmitSchema(Schema):
    """Schema for quiz submission."""

    quiz_id = fields.Int(required=True)
    answers = fields.Dict(keys=fields.Str(), values=fields.Str(), required=True)

    @validates("answers")
    def validate_answers(self, value):
        if not value:
            raise ValidationError("At least one answer is required.")
