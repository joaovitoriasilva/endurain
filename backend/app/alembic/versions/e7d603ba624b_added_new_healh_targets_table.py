"""Added new healh_targets table

Revision ID: e7d603ba624b
Revises: ccfd790687f5
Create Date: 2024-09-22 13:56:29.135722

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7d603ba624b'
down_revision: Union[str, None] = 'ccfd790687f5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('health_targets',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False, comment='User ID that the health_target belongs'),
    sa.Column('weight', sa.DECIMAL(precision=10, scale=2), nullable=True, comment='Weight in kg'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_health_targets_user_id'), 'health_targets', ['user_id'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_health_targets_user_id'), table_name='health_targets')
    op.drop_table('health_targets')
    # ### end Alembic commands ###