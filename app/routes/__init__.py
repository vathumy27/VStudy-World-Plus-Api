from app.routes.ai_routes import ai_bp
from app.routes.auth_routes import auth_bp
from app.routes.chat_routes import chat_bp
from app.routes.geography_routes import geo_bp
from app.routes.lesson_routes import lesson_bp
from app.routes.math_routes import math_bp
from app.routes.progress_routes import progress_bp
from app.routes.quiz_routes import quiz_bp
from app.routes.study_plan_routes import study_plan_bp
from app.routes.subject_routes import subject_bp


def register_blueprints(app):
    """Register all application blueprints."""
    app.register_blueprint(auth_bp)
    app.register_blueprint(subject_bp)
    app.register_blueprint(lesson_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(progress_bp)
    app.register_blueprint(geo_bp)
    app.register_blueprint(math_bp)
    app.register_blueprint(study_plan_bp)
    app.register_blueprint(chat_bp)
