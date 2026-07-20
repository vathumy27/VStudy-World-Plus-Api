from marshmallow import Schema, ValidationError, fields, validates


class MathSolveSchema(Schema):
    """Schema for solving a math problem."""

    problem_text = fields.Str(required=True)
    show_steps = fields.Bool(load_default=True)

    @validates("problem_text")
    def validate_problem(self, value, **kwargs):
        if not value or not value.strip():
            raise ValidationError("Problem text is required.")


class MathCheckSchema(Schema):
    """Schema for checking a math answer."""

    practice_id = fields.Int(load_default=None)
    problem_text = fields.Str(required=True)
    user_answer = fields.Str(required=True)

    @validates("problem_text")
    def validate_problem(self, value, **kwargs):
        if not value or not value.strip():
            raise ValidationError("Problem text is required.")

    @validates("user_answer")
    def validate_answer(self, value, **kwargs):
        if not value or not value.strip():
            raise ValidationError("User answer is required.")
