from flask import Blueprint, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from app.services.geography_service import GeographyService

geo_bp = Blueprint("geo", __name__, url_prefix="/api/geo")


@geo_bp.route("/maps", methods=["GET"])
@jwt_required()
def get_maps():
    """Return available geography maps."""
    return GeographyService.get_maps()


@geo_bp.route("/activities", methods=["GET"])
@jwt_required()
def get_activities():
    """Return geography map activities."""
    return GeographyService.get_activities()


@geo_bp.route("/marking", methods=["POST"])
@jwt_required()
def submit_marking():
    """Submit map markings for a geography activity."""
    user_id = get_jwt_identity()
    return GeographyService.submit_marking(
        user_id, request.get_json(silent=True)
    )
