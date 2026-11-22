"""create clicks table

Revision ID: b87a9c31d2e4
Revises: 52141f95f62c
Create Date: 2026-11-22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b87a9c31d2e4"
down_revision: Union[str, Sequence[str], None] = "52141f95f62c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "clicks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("link_id", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("referrer", sa.Text(), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["link_id"], ["links.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_clicks_link_id"), "clicks", ["link_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_clicks_link_id"), table_name="clicks")
    op.drop_table("clicks")
