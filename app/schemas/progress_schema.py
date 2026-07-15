from marshmallow import Schema, ValidationError, fields, validates, validates_schema


class ProgressUpdateSchema(Schema):
    """Schema for updating student progress."""

    lesson_id = fields.Int(load_default=None)
    subject_id = fields.Int(load_default=None)
    status = fields.Str(load_default=None)
    completion_percentage = fields.Float(load_default=None)
    time_spent_minutes = fields.Int(load_default=None)

    @validates_schema
    def validate_at_least_one_field(self, data, **_kwargs):
        if not data:
            raise ValidationError("At least one field is required to update.")

    @validates("status")
    def validate_status(self, value):
        if value is not None:
            allowed = ("not_started", "in_progress", "completed")
            if value not in allowed:
                raise ValidationError(
                    f"Status must be one of: {', '.join(allowed)}."
                )

    @validates("completion_percentage")
    def validate_completion(self, value):
        if value is not None and (value < 0 or value > 100):
            raise ValidationError(
                "Completion percentage must be between 0 and 100."
            )
