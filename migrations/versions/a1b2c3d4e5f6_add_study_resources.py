"""add study_resources table for AI study notes

Revision ID: a1b2c3d4e5f6
Revises: 70deebbd96d5
Create Date: 2026-07-20 18:50:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "a1b2c3d4e5f6"
down_revision = "70deebbd96d5"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "study_resources",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("subject_id", sa.Integer(), nullable=False),
        sa.Column("lesson_id", sa.Integer(), nullable=True),
        sa.Column("grade", sa.Integer(), nullable=False),
        sa.Column("unit_number", sa.String(length=50), nullable=True),
        sa.Column("title", sa.String(length=250), nullable=False),
        sa.Column("resource_type", sa.String(length=50), nullable=False),
        sa.Column("short_notes", sa.Text(), nullable=True),
        sa.Column("key_points", sa.JSON(), nullable=True),
        sa.Column("definitions", sa.JSON(), nullable=True),
        sa.Column("dates", sa.JSON(), nullable=True),
        sa.Column("maps_locations", sa.JSON(), nullable=True),
        sa.Column("scientific_concepts", sa.JSON(), nullable=True),
        sa.Column("formulae", sa.JSON(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("exam_tips", sa.JSON(), nullable=True),
        sa.Column("revision_notes", sa.Text(), nullable=True),
        sa.Column("keywords", sa.JSON(), nullable=True),
        sa.Column("resource_links", sa.JSON(), nullable=True),
        sa.Column("language", sa.String(length=20), nullable=True),
        sa.Column("generated_by", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["lesson_id"], ["lessons.id"]),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("study_resources", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_study_resources_grade"), ["grade"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_study_resources_lesson_id"), ["lesson_id"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_study_resources_resource_type"),
            ["resource_type"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_study_resources_subject_id"), ["subject_id"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_study_resources_unit_number"),
            ["unit_number"],
            unique=False,
        )


def downgrade():
    with op.batch_alter_table("study_resources", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_study_resources_unit_number"))
        batch_op.drop_index(batch_op.f("ix_study_resources_subject_id"))
        batch_op.drop_index(batch_op.f("ix_study_resources_resource_type"))
        batch_op.drop_index(batch_op.f("ix_study_resources_lesson_id"))
        batch_op.drop_index(batch_op.f("ix_study_resources_grade"))

    op.drop_table("study_resources")
