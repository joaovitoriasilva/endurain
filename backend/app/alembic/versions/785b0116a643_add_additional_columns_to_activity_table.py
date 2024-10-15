"""Add additional columns to activity table

Revision ID: 785b0116a643
Revises: 24e2676546b1
Create Date: 2024-09-20 20:34:04.214393

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '785b0116a643'
down_revision: Union[str, None] = '24e2676546b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('activities', sa.Column('total_elapsed_time', sa.DateTime(), nullable=False, comment='Activity total elapsed time (datetime)'))
    op.add_column('activities', sa.Column('total_timer_time', sa.DateTime(), nullable=False, comment='Activity total timer time (datetime)'))
    op.add_column('activities', sa.Column('workout_feeling', sa.Integer(), nullable=True, comment='Workout feeling (0 to 100)'))
    op.add_column('activities', sa.Column('workout_rpe', sa.Integer(), nullable=True, comment='Workout RPE (10 to 100)'))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('activities', 'workout_rpe')
    op.drop_column('activities', 'workout_feeling')
    op.drop_column('activities', 'total_timer_time')
    op.drop_column('activities', 'total_elapsed_time')
    # ### end Alembic commands ###