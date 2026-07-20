from marshmallow import Schema, ValidationError, fields, validates


class MapMarkingSchema(Schema):
    """Schema for geography map marking submission."""

    activity_id = fields.Int(required=True)
    markings = fields.List(fields.Dict(), required=True)

    @validates("markings")
    def validate_markings(self, value, **kwargs):
        if not value:
            raise ValidationError("At least one marking is required.")
