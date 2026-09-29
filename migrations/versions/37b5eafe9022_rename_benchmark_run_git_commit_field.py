"""rename benchmark run git commit field

Revision ID: 37b5eafe9022
Revises: b14cf72161b1
Create Date: 2026-09-28 19:22:18.291938

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '37b5eafe9022'
down_revision: Union[str, Sequence[str], None] = 'b14cf72161b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    """
    Rename the benchmark-run Git commit provenance field.

    The original column name tied benchmark history to the runtime router.
    Benchmark execution is now owned by the independent Benchmark Service, so
    the provenance field uses service-neutral terminology.

    Existing values are preserved because this is a column rename rather than
    a drop-and-create operation.
    """

    op.alter_column(
        "benchmark_runs",
        "router_git_commit",
        new_column_name="source_git_commit",
        schema="benchmark",
    )


def downgrade() -> None:
    """
    Restore the original router-specific column name.
    """

    op.alter_column(
        "benchmark_runs",
        "source_git_commit",
        new_column_name="router_git_commit",
        schema="benchmark",
    )
