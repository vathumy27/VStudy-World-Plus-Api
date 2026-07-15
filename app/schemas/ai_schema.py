from marshmallow import Schema, ValidationError, fields, validates


class SummarizeSchema(Schema):
    """Schema for AI lesson summarization request."""

    lesson_content = fields.Str(required=True)

    @validates("lesson_content")
    def validate_content(self, value):
        if not value or not value.strip():
            raise ValidationError("Lesson content is required.")


class ExplainSchema(Schema):
    """Schema for AI topic explanation request."""

    topic = fields.Str(required=True)

    @validates("topic")
    def validate_topic(self, value):
        if not value or not value.strip():
            raise ValidationError("Topic is required.")


class GenerateVideoSchema(Schema):
    """Schema for AI history video generation request."""

    history_lesson = fields.Str(required=True)

    @validates("history_lesson")
    def validate_history_lesson(self, value):
        if not value or not value.strip():
            raise ValidationError("History lesson content is required.")
