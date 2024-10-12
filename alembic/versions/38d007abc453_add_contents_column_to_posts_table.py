"""add contents column to posts table

Revision ID: 38d007abc453
Revises: 301f1751859c
Create Date: 2024-10-12 12:38:30.100354

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '38d007abc453'
down_revision: Union[str, None] = '301f1751859c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('content', sa.String(), nullable=False))
    pass


def downgrade() -> None:
    op.drop_column('posts', 'content')
    pass
