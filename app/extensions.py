from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()

# In-memory token blocklist for logout (use Redis in multi-instance production)
jwt_blocklist = set()
