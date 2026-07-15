from marshmallow import Schema, ValidationError, fields, validates


class StudyPlanGenerateSchema(Schema):
    """Schema for generating a study plan."""

    title = fields.Str(required=True)
    exam_date = fields.Date(load_default=None)
    subjects = fields.List(fields.Str(), load_default=list)
    hours_per_day = fields.Int(load_default=2)
    focus_areas = fields.List(fields.Str(), load_default=list)

    @validates("title")
    def validate_title(self, value):
        if not value or not value.strip():
            raise ValidationError("Study plan title is required.")

    @validates("hours_per_day")
    def validate_hours(self, value):
        if value < 1 or value > 12:
            raise ValidationError("Hours per day must be between 1 and 12.")
