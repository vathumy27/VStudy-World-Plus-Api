# from marshmallow import Schema, ValidationError, fields, validates, validates_schema

# VALID_ROLES = ("Student", "Teacher", "Admin")


# class RegisterSchema(Schema):
#     """Schema for user registration."""

#     full_name = fields.Str(required=True)
#     email = fields.Email(required=True)
#     password = fields.Str(required=True)
#     school = fields.Str(load_default=None)
#     grade = fields.Str(load_default=None)
#     role = fields.Str(load_default="Student")

#     @validates("full_name")
#     def validate_full_name(self, value ,**_kwargs):
#         if not value or not value.strip():
#             raise ValidationError("Full name is required.")

#     @validates("password")
#     def validate_password(self, value):
#         if not value or len(value) < 6:
#             raise ValidationError("Password must be at least 6 characters.")

#     @validates("role")
#     def validate_role(self, value):
#         if value not in VALID_ROLES:
#             raise ValidationError(
#                 f"Role must be one of: {', '.join(VALID_ROLES)}."
#             )


# class LoginSchema(Schema):
#     """Schema for user login."""

#     email = fields.Email(required=True)
#     password = fields.Str(required=True)


# class ProfileUpdateSchema(Schema):
#     """Schema for updating user profile."""

#     full_name = fields.Str()
#     school = fields.Str(allow_none=True)
#     grade = fields.Str(allow_none=True)
#     profile_image = fields.Str(allow_none=True)

#     @validates_schema
#     def validate_at_least_one_field(self, data, **_kwargs):
#         if not data:
#             raise ValidationError("At least one field is required to update.")


# class UserSchema(Schema):
#     """Schema for serializing user data."""

#     id = fields.Int(dump_only=True)
#     full_name = fields.Str()
#     email = fields.Email()
#     school = fields.Str(allow_none=True)
#     grade = fields.Str(allow_none=True)
#     role = fields.Str()
#     profile_image = fields.Str(allow_none=True)
#     created_at = fields.DateTime(dump_only=True)
#     updated_at = fields.DateTime(dump_only=True)
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