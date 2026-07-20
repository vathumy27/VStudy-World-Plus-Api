"""add tamil study resource fields

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-07-20 22:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "b2c3d4e5f6a7"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("study_resources", schema=None) as batch_op:
        batch_op.add_column(sa.Column("easy_explanation", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("study_tips", sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column("important_questions", sa.JSON(), nullable=True))


def downgrade():
    with op.batch_alter_table("study_resources", schema=None) as batch_op:
        batch_op.drop_column("important_questions")
        batch_op.drop_column("study_tips")
        batch_op.drop_column("easy_explanation")
