from app.extensions import db


class Subject(db.Model):
    """Academic subject (e.g. Mathematics, History)."""

    __tablename__ = "subjects"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(500), nullable=True)

    lessons = db.relationship(
        "Lesson", back_populates="subject", cascade="all, delete-orphan"
    )
    progress_records = db.relationship(
        "Progress", back_populates="subject", cascade="all, delete-orphan"
    )

    def to_dict(self):
        """Serialize subject data."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "image": self.image,
        }
