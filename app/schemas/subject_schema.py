from marshmallow import Schema, ValidationError, fields, validates


class SubjectSchema(Schema):
    """Schema for subject serialization."""

    id = fields.Int(dump_only=True)
    name = fields.Str()
    description = fields.Str(allow_none=True)
    image = fields.Str(allow_none=True)


class SubjectCreateSchema(Schema):
    """Schema for creating a subject."""

    name = fields.Str(required=True)
    description = fields.Str(load_default=None)
    image = fields.Str(load_default=None)

    @validates("name")
    def validate_name(self, value, **kwargs):
        if not value or not value.strip():
            raise ValidationError("Subject name is required.")


class SubjectUpdateSchema(Schema):
    """Schema for updating a subject."""

    name = fields.Str()
    description = fields.Str(allow_none=True)
    image = fields.Str(allow_none=True)

    @validates("name")
    def validate_name(self, value, **kwargs):
        if value is not None and not value.strip():
            raise ValidationError("Subject name cannot be empty.")
