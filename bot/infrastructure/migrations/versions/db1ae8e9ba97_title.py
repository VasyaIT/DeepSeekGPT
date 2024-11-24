"""Title

Revision ID: db1ae8e9ba97
Revises: 8792e7ad1a85
Create Date: 2024-11-24 08:34:15.068879

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'db1ae8e9ba97'
down_revision: Union[str, None] = '8792e7ad1a85'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('chats', sa.Column('title', sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('chats', 'title')
    # ### end Alembic commands ###
