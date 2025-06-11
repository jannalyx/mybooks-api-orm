"""Alterar relação Pedido-Pagamento para 1:1

Revision ID: d4048bf9920c
Revises: '54d192e2e1b0'
Create Date: 2025-06-11 19:45:35.155088

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel


revision = 'd4048bf9920c'
down_revision = '54d192e2e1b0'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('autor', 'biografia',
               existing_type=sa.TEXT(),
               type_=sqlmodel.sql.sqltypes.AutoString(),
               existing_nullable=True)
    op.create_unique_constraint(None, 'pagamento', ['pedido_id'])
 

def downgrade():
    op.drop_constraint(None, 'pagamento', type_='unique')
    op.alter_column('autor', 'biografia',
               existing_type=sqlmodel.sql.sqltypes.AutoString(),
               type_=sa.TEXT(),
               existing_nullable=True)
   