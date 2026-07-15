from marshmallow import Schema, ValidationError, fields, validates, validates_schema


class LessonSchema(Schema):
    """Schema for lesson serialization."""

    id = fields.Int(dump_only=True)
    subject_id = fields.Int()
    title = fields.Str()
    description = fields.Str(allow_none=True)
    content = fields.Str(allow_none=True)
    summary = fields.Str(allow_none=True)
    video_url = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class LessonCreateSchema(Schema):
    """Schema for creating a lesson."""

    subject_id = fields.Int(required=True)
    title = fields.Str(required=True)
    description = fields.Str(load_default=None)
    content = fields.Str(load_default=None)
    summary = fields.Str(load_default=None)
    video_url = fields.Str(load_default=None)

    @validates("title")
    def validate_title(self, value):
        if not value or not value.strip():
            raise ValidationError("Lesson title is required.")


class LessonUpdateSchema(Schema):
    """Schema for updating a lesson."""

    subject_id = fields.Int()
    title = fields.Str()
    description = fields.Str(allow_none=True)
    content = fields.Str(allow_none=True)
    summary = fields.Str(allow_none=True)
    video_url = fields.Str(allow_none=True)

    @validates_schema
    def validate_at_least_one_field(self, data, **_kwargs):
        if not data:
            raise ValidationError("At least one field is required to update.")

    @validates("title")
    def validate_title(self, value):
        if value is not None and not value.strip():
            raise ValidationError("Lesson title cannot be empty.")
