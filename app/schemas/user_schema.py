from marshmallow import Schema, ValidationError, fields, validates, validates_schema

VALID_ROLES = ("Student", "Teacher", "Admin")


class RegisterSchema(Schema):
    """Schema for user registration."""

    full_name = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True)
    school = fields.Str(load_default=None)
    grade = fields.Str(load_default=None)
    role = fields.Str(load_default="Student")

    @validates("full_name")
    def validate_full_name(self, value, **kwargs):
        if not value or not value.strip():
            raise ValidationError("Full name is required.")

    @validates("password")
    def validate_password(self, value, **kwargs):
        if not value or len(value) < 6:
            raise ValidationError("Password must be at least 6 characters.")

    @validates("role")
    def validate_role(self, value, **kwargs):
        if value not in VALID_ROLES:
            raise ValidationError(
                f"Role must be one of: {', '.join(VALID_ROLES)}."
            )


class LoginSchema(Schema):
    """Schema for user login."""

    email = fields.Email(required=True)
    password = fields.Str(required=True)


class ProfileUpdateSchema(Schema):
    full_name = fields.Str()
    school = fields.Str(allow_none=True)
    grade = fields.Str(allow_none=True)
    profile_image = fields.Str(allow_none=True)

    @validates_schema
    def validate_at_least_one_field(self, data, **kwargs):
        if not data:
            raise ValidationError("At least one field is required to update.")


class EmailUpdateSchema(Schema):
    """Schema for changing account email."""

    email = fields.Email(required=True)
    current_password = fields.Str(required=True)

    @validates("current_password")
    def validate_current_password(self, value, **kwargs):
        if not value:
            raise ValidationError("Current password is required.")


class PasswordUpdateSchema(Schema):
    """Schema for changing account password."""

    current_password = fields.Str(required=True)
    new_password = fields.Str(required=True)
    confirm_password = fields.Str(required=True)

    @validates("new_password")
    def validate_new_password(self, value, **kwargs):
        if not value or len(value) < 6:
            raise ValidationError("New password must be at least 6 characters.")

    @validates_schema
    def validate_passwords_match(self, data, **kwargs):
        if data.get("new_password") != data.get("confirm_password"):
            raise ValidationError(
                "New password and confirm password do not match.",
                field_name="confirm_password",
            )
        if data.get("current_password") == data.get("new_password"):
            raise ValidationError(
                "New password must be different from the current password.",
                field_name="new_password",
            )


class UserSchema(Schema):
    """Schema for serializing user data."""

    id = fields.Int(dump_only=True)
    full_name = fields.Str()
    email = fields.Email()
    school = fields.Str(allow_none=True)
    grade = fields.Str(allow_none=True)
    role = fields.Str()
    profile_image = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
