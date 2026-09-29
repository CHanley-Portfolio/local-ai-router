"""rename benchmark run git commit field

Revision ID: b14cf72161b1
Revises: 47339f26ea7f
Create Date: 2026-09-28 19:04:57.877279

"""
from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = 'b14cf72161b1'
down_revision: Union[str, Sequence[str], None] = '47339f26ea7f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
