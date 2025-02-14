"""v0.9.0 migration

Revision ID: 7217cc0eee8c
Revises: 0158771b9f18
Create Date: 2025-02-12 12:06:28.789923

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "7217cc0eee8c"
down_revision: Union[str, None] = "0158771b9f18"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "server_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "units",
            sa.Integer(),
            nullable=False,
            comment="User units (one digit)(1 - metric, 2 - imperial)",
        ),
        sa.Column(
            "public_shareable_links",
            sa.Boolean(),
            nullable=False,
            comment="Allow public shareable links (true - yes, false - no)",
        ),
        sa.Column(
            "public_shareable_links_user_info",
            sa.Boolean(),
            nullable=False,
            comment="Allow show user info on public shareable links (true - yes, false - no)",
        ),
        sa.CheckConstraint("id = 1", name="single_row_check"),
        sa.PrimaryKeyConstraint("id"),
    )
    # Add the new entry to the server_settings table
    op.execute("""
    INSERT INTO server_settings (id, units, public_shareable_links, public_shareable_links_user_info) VALUES
    (1, 1, FALSE, FALSE);
    """)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("server_settings")
    # ### end Alembic commands ###
