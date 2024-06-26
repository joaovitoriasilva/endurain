"""Remove access_tokens table

Revision ID: 0ab200a7f196
Revises: 5fd61bc55e09
Create Date: 2024-05-24 13:39:50.917676

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '0ab200a7f196'
down_revision: Union[str, None] = '5fd61bc55e09'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    # Drop the foreign key constraint first
    op.drop_constraint('access_tokens_ibfk_1', 'access_tokens', type_='foreignkey')
    # Then drop the index
    op.drop_index('ix_access_tokens_user_id', table_name='access_tokens')
    op.drop_table('access_tokens')
    op.alter_column('users_integrations', 'user_id',
               existing_type=mysql.INTEGER(display_width=11),
               comment='User ID that the integration belongs',
               existing_comment='User ID that the token belongs',
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users_integrations', 'user_id',
               existing_type=mysql.INTEGER(display_width=11),
               comment='User ID that the token belongs',
               existing_comment='User ID that the integration belongs',
               existing_nullable=False)
    op.create_table('access_tokens',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('token', mysql.VARCHAR(length=256), nullable=False, comment='User token'),
    sa.Column('user_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False, comment='User ID that the token belongs'),
    sa.Column('created_at', mysql.DATETIME(), nullable=False, comment='Token creation date (date)'),
    sa.Column('expires_at', mysql.DATETIME(), nullable=False, comment='Token expiration date (date)'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='access_tokens_ibfk_1', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_general_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    # Recreate the index first
    op.create_index('ix_access_tokens_user_id', 'access_tokens', ['user_id'])
    # Then recreate the foreign key constraint
    op.create_foreign_key('access_tokens_ibfk_1', 'access_tokens', 'users', ['user_id'], ['id'])
    # ### end Alembic commands ###
