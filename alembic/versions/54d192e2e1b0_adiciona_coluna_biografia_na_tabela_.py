"""adiciona coluna biografia na tabela autor

Revision ID: 54d192e2e1b0
Revises: '73a32176c1f7'
Create Date: 2025-06-10 23:38:25.309350

"""
from alembic import op
import sqlalchemy as sa


revision = '54d192e2e1b0'
down_revision = '73a32176c1f7'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('autor', sa.Column('biografia', sa.Text(), nullable=True))


def downgrade():
    op.drop_column('autor', 'biografia')

