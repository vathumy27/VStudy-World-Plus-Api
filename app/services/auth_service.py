# from flask_jwt_extended import create_access_token

# from app.extensions import db, jwt_blocklist
# from app.models.user import User
# from app.schemas.user_schema import (
#     LoginSchema,
#     ProfileUpdateSchema,
#     RegisterSchema,
# )
# from app.utils.response import error_response, success_response
# from app.utils.time_utils import utc_now


# class AuthService:
#     """Business logic for authentication and user profile management."""

#     @staticmethod
#     def _format_validation_errors(err):
#         """Flatten Marshmallow validation errors into a readable message."""
#         messages = []
#         for field, field_errors in err.messages.items():
#             for message in field_errors:
#                 messages.append(f"{field}: {message}")
#         return "; ".join(messages)

#     @staticmethod
#     def register(data):
#         schema = RegisterSchema()
#         try:
#             validated = schema.load(data or {})
#         except Exception as err:
#             return error_response(
#                 AuthService._format_validation_errors(err),
#                 status_code=400,
#             )

#         email = validated["email"].strip().lower()
#         if User.query.filter_by(email=email).first():
#             return error_response("Email address already exists.", status_code=409)

#         # Only admins can create Teacher/Admin accounts; public registration is Student
#         role = validated.get("role", "Student")
#         if role != "Student":
#             role = "Student"

#         user = User(
#             full_name=validated["full_name"].strip(),
#             email=email,
#             school=validated.get("school"),
#             grade=validated.get("grade"),
#             role=role,
#         )
#         user.set_password(validated["password"])

#         try:
#             db.session.add(user)
#             db.session.commit()
#             return success_response(
#                 "User registered successfully.",
#                 {"user": user.to_dict()},
#                 status_code=201,
#             )
#         except Exception:
#             db.session.rollback()
#             return error_response(
#                 "An internal server error occurred.", status_code=500
#             )

#     @staticmethod
#     def login(data):
#         schema = LoginSchema()
#         try:
#             validated = schema.load(data or {})
#         except Exception as err:
#             return error_response(
#                 AuthService._format_validation_errors(err),
#                 status_code=400,
#             )

#         email = validated["email"].strip().lower()
#         user = User.query.filter_by(email=email).first()

#         if not user or not user.check_password(validated["password"]):
#             return error_response("Invalid email or password.", status_code=401)

#         access_token = create_access_token(
#             identity=str(user.id),
#             additional_claims={"role": user.role},
#         )

#         return success_response(
#             "Login successful.",
#             {
#                 "access_token": access_token,
#                 "user": user.to_dict(),
#             },
#         )

#     @staticmethod
#     def get_current_user(user_id):
#         user = db.session.get(User, int(user_id))
#         if not user:
#             return error_response("User not found.", status_code=404)

#         return success_response("User retrieved successfully.", {"user": user.to_dict()})

#     @staticmethod
#     def update_profile(user_id, data):
#         schema = ProfileUpdateSchema()
#         try:
#             validated = schema.load(data or {})
#         except Exception as err:
#             return error_response(
#                 AuthService._format_validation_errors(err),
#                 status_code=400,
#             )

#         user = db.session.get(User, int(user_id))
#         if not user:
#             return error_response("User not found.", status_code=404)

#         if "full_name" in validated:
#             user.full_name = validated["full_name"].strip()
#         if "school" in validated:
#             user.school = validated["school"]
#         if "grade" in validated:
#             user.grade = validated["grade"]
#         if "profile_image" in validated:
#             user.profile_image = validated["profile_image"]

#         user.updated_at = utc_now()

#         try:
#             db.session.commit()
#             return success_response(
#                 "Profile updated successfully.",
#                 {"user": user.to_dict()},
#             )
#         except Exception:
#             db.session.rollback()
#             return error_response(
#                 "An internal server error occurred.", status_code=500
#             )

#     @staticmethod
#     def logout(jti):
#         """Invalidate the current JWT by adding its JTI to the blocklist."""
#         jwt_blocklist.add(jti)
#         return success_response("Logged out successfully.")
import traceback

from flask_jwt_extended import create_access_token
from marshmallow import ValidationError

from app.extensions import db, jwt_blocklist
from app.models.user import User
from app.schemas.user_schema import (
    LoginSchema,
    ProfileUpdateSchema,
    RegisterSchema,
)
from app.utils.response import error_response, success_response
from app.utils.time_utils import utc_now


class AuthService:
    """Business logic for authentication and user profile management."""

    @staticmethod
    def _format_validation_errors(err):
        """Flatten Marshmallow validation errors into a readable message."""
        messages = []
        for field, field_errors in err.messages.items():
            for message in field_errors:
                messages.append(f"{field}: {message}")
        return "; ".join(messages)

    @staticmethod
    def register(data):
        schema = RegisterSchema()

        try:
            validated = schema.load(data or {})

        except ValidationError as err:
            return error_response(
                AuthService._format_validation_errors(err),
                status_code=400,
            )

        except Exception as err:
            traceback.print_exc()
            return error_response(str(err), status_code=500)

        email = validated["email"].strip().lower()

        if User.query.filter_by(email=email).first():
            return error_response(
                "Email address already exists.",
                status_code=409,
            )

        role = validated.get("role", "Student")
        if role != "Student":
            role = "Student"

        user = User(
            full_name=validated["full_name"].strip(),
            email=email,
            school=validated.get("school"),
            grade=validated.get("grade"),
            role=role,
        )

        user.set_password(validated["password"])

        try:
            db.session.add(user)
            db.session.commit()

            return success_response(
                "User registered successfully.",
                {"user": user.to_dict()},
                status_code=201,
            )

        except Exception as err:
            traceback.print_exc()
            db.session.rollback()

            return error_response(
                str(err),
                status_code=500,
            )

    @staticmethod
    def login(data):
        schema = LoginSchema()

        try:
            validated = schema.load(data or {})

        except ValidationError as err:
            return error_response(
                AuthService._format_validation_errors(err),
                status_code=400,
            )

        except Exception as err:
            traceback.print_exc()
            return error_response(str(err), status_code=500)

        email = validated["email"].strip().lower()
        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(validated["password"]):
            return error_response(
                "Invalid email or password.",
                status_code=401,
            )

        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={"role": user.role},
        )

        return success_response(
            "Login successful.",
            {
                "access_token": access_token,
                "user": user.to_dict(),
            },
        )

    @staticmethod
    def get_current_user(user_id):
        user = db.session.get(User, int(user_id))

        if not user:
            return error_response(
                "User not found.",
                status_code=404,
            )

        return success_response(
            "User retrieved successfully.",
            {"user": user.to_dict()},
        )

    @staticmethod
    def update_profile(user_id, data):
        schema = ProfileUpdateSchema()

        try:
            validated = schema.load(data or {})

        except ValidationError as err:
            return error_response(
                AuthService._format_validation_errors(err),
                status_code=400,
            )

        except Exception as err:
            traceback.print_exc()
            return error_response(str(err), status_code=500)

        user = db.session.get(User, int(user_id))

        if not user:
            return error_response(
                "User not found.",
                status_code=404,
            )

        if "full_name" in validated:
            user.full_name = validated["full_name"].strip()

        if "school" in validated:
            user.school = validated["school"]

        if "grade" in validated:
            user.grade = validated["grade"]

        if "profile_image" in validated:
            user.profile_image = validated["profile_image"]

        user.updated_at = utc_now()

        try:
            db.session.commit()

            return success_response(
                "Profile updated successfully.",
                {"user": user.to_dict()},
            )

        except Exception as err:
            traceback.print_exc()
            db.session.rollback()

            return error_response(
                str(err),
                status_code=500,
            )

    @staticmethod
    def logout(jti):
        """Invalidate the current JWT by adding its JTI to the blocklist."""
        jwt_blocklist.add(jti)

        return success_response(
            "Logged out successfully."
        )