"""v0.16.0 migration - Add personal_records table

Revision ID: 4d5e6f7a8b9c
Revises: 3c4d5e6f7a8b
Create Date: 2025-10-11 14:35:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "4d5e6f7a8b9c"
down_revision: Union[str, None] = "3c4d5e6f7a8b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create personal_records table
    op.create_table(
        "personal_records",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=False,
            comment="User ID that the PR belongs to",
        ),
        sa.Column(
            "activity_id",
            sa.Integer(),
            nullable=False,
            comment="Activity ID that set this PR",
        ),
        sa.Column(
            "activity_type",
            sa.Integer(),
            nullable=False,
            comment="Activity type (1 - run, 4 - ride, 8 - swim, 19 - strength training, etc.)",
        ),
        sa.Column(
            "pr_date",
            sa.DateTime(),
            nullable=False,
            comment="Date when the PR was set",
        ),
        sa.Column(
            "metric",
            sa.String(length=100),
            nullable=False,
            comment="PR metric (e.g., 'fastest_5km', 'longest_distance', 'squat_1rm')",
        ),
        sa.Column(
            "value",
            sa.DECIMAL(precision=20, scale=10),
            nullable=False,
            comment="PR value (time in seconds, distance in meters, weight in kg, etc.)",
        ),
        sa.Column(
            "unit",
            sa.String(length=50),
            nullable=False,
            comment="Unit of measurement (e.g., 'seconds', 'meters', 'kg', 'watts')",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["activity_id"],
            ["activities.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes
    op.create_index(
        "ix_personal_records_user_id",
        "personal_records",
        ["user_id"],
    )
    op.create_index(
        "ix_personal_records_activity_id",
        "personal_records",
        ["activity_id"],
    )
    op.create_index(
        "ix_personal_records_activity_type",
        "personal_records",
        ["activity_type"],
    )
    op.create_index(
        "ix_personal_records_metric",
        "personal_records",
        ["metric"],
    )


def downgrade() -> None:
    # Drop indexes
    op.drop_index("ix_personal_records_metric", table_name="personal_records")
    op.drop_index("ix_personal_records_activity_type", table_name="personal_records")
    op.drop_index("ix_personal_records_activity_id", table_name="personal_records")
    op.drop_index("ix_personal_records_user_id", table_name="personal_records")

    # Drop table
    op.drop_table("personal_records")
