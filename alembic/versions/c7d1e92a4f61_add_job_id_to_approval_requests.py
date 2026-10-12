"""Add job_id to approval_requests

Revision ID: c7d1e92a4f61
Revises: 8fb511ca7d58
Create Date: 2026-10-12 16:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c7d1e92a4f61'
down_revision: Union[str, None] = '8fb511ca7d58'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('approval_requests', sa.Column('job_id', sa.String(length=36), nullable=True))
    op.create_index(op.f('ix_approval_requests_job_id'), 'approval_requests', ['job_id'], unique=False)
    op.create_foreign_key('fk_approval_requests_job_id', 'approval_requests', 'agent_jobs', ['job_id'], ['id'], ondelete='SET NULL')


def downgrade() -> None:
    op.drop_constraint('fk_approval_requests_job_id', 'approval_requests', type_='foreignkey')
    op.drop_index(op.f('ix_approval_requests_job_id'), table_name='approval_requests')
    op.drop_column('approval_requests', 'job_id')
