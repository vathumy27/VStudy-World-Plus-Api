from flask import jsonify


def success_response(message="", data=None, status_code=200):
    """Return a standardized success API response."""
    return (
        jsonify(
            {
                "success": True,
                "message": message,
                "data": data if data is not None else {},
            }
        ),
        status_code,
    )


def error_response(message="", data=None, status_code=400):
    """Return a standardized error API response."""
    return (
        jsonify(
            {
                "success": False,
                "message": message,
                "data": data if data is not None else {},
            }
        ),
        status_code,
    )
