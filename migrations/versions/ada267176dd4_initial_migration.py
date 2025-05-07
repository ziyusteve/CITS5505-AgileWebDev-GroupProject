"""Initial migration

Revision ID: ada267176dd4
Revises:
Create Date: 2025-05-04 19:21:54.148825

"""

# revision identifiers, used by Alembic.
revision = "ada267176dd4"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Initial migration does not make any changes,
    # only marks the current database state
    pass


def downgrade():
    # Initial migration does not make any changes,
    # no need for rollback operations
    pass
