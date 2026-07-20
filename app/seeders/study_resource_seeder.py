"""Seed original AI study resources into the local database."""

from app.services.study_resource_service import StudyResourceService


def seed_study_resources(regenerate: bool = False, grades=(10, 11)):
    """Generate and store study notes / Math resource packs once."""
    return StudyResourceService.generate_all(
        regenerate=regenerate, grades=tuple(grades)
    )
