from marshmallow import Schema, ValidationError, fields, validates


class ChatAskSchema(Schema):
    """Schema for AI chatbot question."""

    question = fields.Str(required=True)

    @validates("question")
    def validate_question(self, value, **kwargs):
        if not value or not value.strip():
            raise ValidationError("Question is required.")
        if len(value) > 2000:
            raise ValidationError("Question must not exceed 2000 characters.")
