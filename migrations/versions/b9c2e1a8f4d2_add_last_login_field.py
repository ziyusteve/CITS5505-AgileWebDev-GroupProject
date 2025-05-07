"""Add last_login field

Revision ID: b9c2e1a8f4d2
Revises: ada267176dd4
Create Date: 2025-05-05 15:39:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b9c2e1a8f4d2"
down_revision = "ada267176dd4"
branch_labels = None
depends_on = None


def upgrade():
    # Add last_login column to user table
    op.add_column(
        "user", sa.Column("last_login", sa.DateTime(), nullable=True)
    )


def downgrade():
    # Drop last_login column from user table
    op.drop_column("user", "last_login")
