"""v0.7.0

Revision ID: 446a199ddd37
Revises: 542605083c0c
Create Date: 2024-12-26 21:43:01.958551

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '446a199ddd37'
down_revision: Union[str, None] = '542605083c0c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('activities_garminconnect_activity_id_key', 'activities', type_='unique')
    op.alter_column('users', 'password',
               existing_type=sa.VARCHAR(length=100),
               type_=sa.VARCHAR(length=250),
               existing_comment='User password (hash)',
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'password',
               existing_type=sa.VARCHAR(length=250),
               type_=sa.VARCHAR(length=100),
               existing_comment='User password (hash)',
               existing_nullable=False)
    op.create_unique_constraint('activities_garminconnect_activity_id_key', 'activities', ['garminconnect_activity_id'])
    # ### end Alembic commands ###