"""v0.14.1 migration - Add TSS support

Revision ID: tss_support_001
Revises: 86b2e24e227e
Create Date: 2024-12-08 22:30:00.000000

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = "tss_support_001"
down_revision: Union[str, None] = "86b2e24e227e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add TSS column to activities table
    op.add_column('activities', 
        sa.Column('tss', sa.Integer(), nullable=True, comment='Training Stress Score (TSS) for the activity')
    )
    
    # Add threshold fields to users table for TSS calculations
    op.add_column('users', 
        sa.Column('ftp', sa.Integer(), nullable=True, comment='Functional Threshold Power (FTP) in watts for TSS calculation')
    )
    op.add_column('users', 
        sa.Column('lthr', sa.Integer(), nullable=True, comment='Lactate Threshold Heart Rate (LTHR) in bpm for hrTSS calculation')
    )
    op.add_column('users', 
        sa.Column('run_threshold_pace', sa.DECIMAL(precision=20, scale=10), nullable=True, comment='Running threshold pace in seconds per meter for rTSS calculation')
    )
    op.add_column('users', 
        sa.Column('swim_threshold_pace', sa.DECIMAL(precision=20, scale=10), nullable=True, comment='Swimming threshold pace in seconds per meter for sTSS calculation')
    )
    
    # Add migration record if it doesn't exist 
    connection = op.get_bind()
    
    # Check if migration 6 record exists
    result = connection.execute(text("SELECT COUNT(*) FROM migrations WHERE id = 6")).scalar()
    
    if result == 0:
        # Insert migration 6 record
        connection.execute(text("""
            INSERT INTO migrations (id, name, description, executed) 
            VALUES (6, 'TSS Support Migration', 'Add TSS calculation support with user threshold settings', 0)
        """))


def downgrade() -> None:
    # Remove columns from users table
    op.drop_column('users', 'swim_threshold_pace')
    op.drop_column('users', 'run_threshold_pace')
    op.drop_column('users', 'lthr')
    op.drop_column('users', 'ftp')
    
    # Remove TSS column from activities table
    op.drop_column('activities', 'tss')
    
    # Remove migration record
    connection = op.get_bind()
    connection.execute(text("DELETE FROM migrations WHERE id = 6"))