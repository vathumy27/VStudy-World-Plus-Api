from app.extensions import db
from app.models.geography import GeographyActivity, MapSubmission
from app.schemas.geography_schema import MapMarkingSchema
from app.utils.response import error_response, success_response


class GeographyService:
    """Business logic for geography map activities."""

    DEFAULT_MAPS = [
        {
            "id": "world",
            "name": "World Map",
            "description": "Interactive world map for locating countries and continents.",
            "regions": ["Asia", "Europe", "Africa", "Americas", "Oceania"],
        },
        {
            "id": "sri_lanka",
            "name": "Sri Lanka Map",
            "description": "Map of Sri Lanka for provinces and major cities.",
            "regions": [
                "Western",
                "Central",
                "Southern",
                "Northern",
                "Eastern",
                "North Western",
                "North Central",
                "Uva",
                "Sabaragamuwa",
            ],
        },
        {
            "id": "asia",
            "name": "Asia Map",
            "description": "Map of Asian countries and capitals.",
            "regions": ["South Asia", "East Asia", "Southeast Asia", "Central Asia"],
        },
    ]

    @staticmethod
    def _format_validation_errors(err):
        messages = []
        for field, field_errors in err.messages.items():
            for message in field_errors:
                messages.append(f"{field}: {message}")
        return "; ".join(messages)

    @staticmethod
    def get_maps():
        return success_response(
            "Maps retrieved successfully.",
            {"maps": GeographyService.DEFAULT_MAPS},
        )

    @staticmethod
    def get_activities():
        activities = GeographyActivity.query.order_by(
            GeographyActivity.created_at.desc()
        ).all()

        if not activities:
            default_activities = [
                GeographyActivity(
                    title="Locate Countries in South Asia",
                    description="Mark the correct locations of South Asian countries.",
                    map_type="asia",
                    difficulty="easy",
                    activity_data={
                        "targets": ["Sri Lanka", "India", "Pakistan", "Bangladesh"],
                        "instructions": "Click on the map to mark each country.",
                    },
                ),
                GeographyActivity(
                    title="Sri Lanka Provinces",
                    description="Identify all provinces of Sri Lanka.",
                    map_type="sri_lanka",
                    difficulty="medium",
                    activity_data={
                        "targets": ["Western", "Central", "Southern"],
                        "instructions": "Mark the province locations on the map.",
                    },
                ),
            ]
            try:
                for activity in default_activities:
                    db.session.add(activity)
                db.session.commit()
                activities = default_activities
            except Exception:
                db.session.rollback()

        return success_response(
            "Geography activities retrieved successfully.",
            {"activities": [a.to_dict() for a in activities]},
        )

    @staticmethod
    def submit_marking(user_id, data):
        schema = MapMarkingSchema()
        try:
            validated = schema.load(data or {})
        except Exception as err:
            return error_response(
                GeographyService._format_validation_errors(err),
                status_code=400,
            )

        activity = db.session.get(GeographyActivity, validated["activity_id"])
        if not activity:
            return error_response("Activity not found.", status_code=404)

        targets = activity.activity_data.get("targets", [])
        markings = validated["markings"]
        correct_count = 0

        for marking in markings:
            label = marking.get("label", "")
            if label in targets:
                correct_count += 1

        total_targets = len(targets) if targets else len(markings)
        score = (
            round((correct_count / total_targets) * 100, 2)
            if total_targets > 0
            else 0.0
        )

        feedback = (
            f"You marked {correct_count} out of {total_targets} locations correctly. "
            "Keep practicing to improve your geography skills!"
        )

        submission = MapSubmission(
            user_id=int(user_id),
            activity_id=activity.id,
            markings=markings,
            score=score,
            feedback=feedback,
        )

        try:
            db.session.add(submission)
            db.session.commit()
            return success_response(
                "Map marking submitted successfully.",
                {"submission": submission.to_dict()},
                status_code=201,
            )
        except Exception:
            db.session.rollback()
            return error_response(
                "An internal server error occurred.", status_code=500
            )
