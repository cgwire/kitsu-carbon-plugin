"""Create carbon factors table

Revision ID: 001_initial
Revises:
Create Date: 2026-02-23

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils
import uuid

# revision identifiers, used by Alembic.
revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "plugin_carbon_factors",
        sa.Column(
            "id",
            sqlalchemy_utils.types.uuid.UUIDType(binary=False),
            default=uuid.uuid4,
            primary_key=True,
        ),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("country_code", sa.String(2), nullable=False, unique=True),
        sa.Column("country_name", sa.String(80), nullable=False),
        sa.Column("rendering_co2e", sa.Float(), nullable=False),
        sa.Column("workbench_co2e", sa.Float(), nullable=False),
    )


def downgrade():
    op.drop_table("plugin_carbon_factors")
