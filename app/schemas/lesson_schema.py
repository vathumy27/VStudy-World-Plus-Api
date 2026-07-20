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
    grade = fields.Int(allow_none=True)
    unit_number = fields.Str(allow_none=True)
    language = fields.Str(allow_none=True)
    pdf_url = fields.Str(allow_none=True)
    image_url = fields.Str(allow_none=True)
    resource_url = fields.Str(allow_none=True)
    download_url = fields.Str(allow_none=True)
    source_url = fields.Str(allow_none=True)
    source_provider = fields.Str(allow_none=True)
    resource_links = fields.List(fields.Dict(), allow_none=True)
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
    grade = fields.Int(load_default=None)
    unit_number = fields.Str(load_default=None)
    language = fields.Str(load_default=None)
    pdf_url = fields.Str(load_default=None)
    image_url = fields.Str(load_default=None)
    resource_url = fields.Str(load_default=None)
    download_url = fields.Str(load_default=None)
    source_url = fields.Str(load_default=None)
    source_provider = fields.Str(load_default="e-thaksalawa")
    resource_links = fields.List(fields.Dict(), load_default=list)

    @validates("title")
    def validate_title(self, value, **kwargs):
        if not value or not value.strip():
            raise ValidationError("Lesson title is required.")

    @validates("grade")
    def validate_grade(self, value, **kwargs):
        if value is not None and value not in (10, 11):
            raise ValidationError("Grade must be 10 or 11 for imported content.")


class LessonUpdateSchema(Schema):
    """Schema for updating a lesson."""

    subject_id = fields.Int()
    title = fields.Str()
    description = fields.Str(allow_none=True)
    content = fields.Str(allow_none=True)
    summary = fields.Str(allow_none=True)
    video_url = fields.Str(allow_none=True)
    grade = fields.Int(allow_none=True)
    unit_number = fields.Str(allow_none=True)
    language = fields.Str(allow_none=True)
    pdf_url = fields.Str(allow_none=True)
    image_url = fields.Str(allow_none=True)
    resource_url = fields.Str(allow_none=True)
    download_url = fields.Str(allow_none=True)
    source_url = fields.Str(allow_none=True)
    source_provider = fields.Str(allow_none=True)
    resource_links = fields.List(fields.Dict(), allow_none=True)

    @validates_schema
    def validate_at_least_one_field(self, data, **kwargs):
        if not data:
            raise ValidationError("At least one field is required to update.")

    @validates("title")
    def validate_title(self, value, **kwargs):
        if value is not None and not value.strip():
            raise ValidationError("Lesson title cannot be empty.")
