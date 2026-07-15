from functools import wraps

from flask_jwt_extended import get_jwt, verify_jwt_in_request

from app.utils.response import error_response


def role_required(*allowed_roles):
    """Restrict access to users with one of the specified roles."""

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get("role")

            if user_role not in allowed_roles:
                return error_response(
                    "You do not have permission to perform this action.",
                    status_code=403,
                )

            return fn(*args, **kwargs)

        return wrapper

    return decorator


def get_current_user_role():
    """Return the role from the current JWT claims."""
    claims = get_jwt()
    return claims.get("role")
