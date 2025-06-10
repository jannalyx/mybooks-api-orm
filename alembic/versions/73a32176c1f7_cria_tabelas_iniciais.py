"""cria tabelas iniciais

Revision ID: 73a32176c1f7
Revises: None
Create Date: 2025-06-09 23:08:17.520835

"""
from alembic import op
import sqlalchemy as sa


revision = '73a32176c1f7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('autor',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('data_nascimento', sa.Date(), nullable=False),
        sa.Column('nacionalidade', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('editora',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(), nullable=False),
        sa.Column('endereco', sa.String(), nullable=False),
        sa.Column('telefone', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('usuario',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('cpf', sa.String(), nullable=False),
        sa.Column('data_cadastro', sa.Date(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('livro',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('titulo', sa.String(), nullable=False),
        sa.Column('preco', sa.Float(), nullable=False),
        sa.Column('genero', sa.String(), nullable=False),
        sa.Column('autor_id', sa.Integer(), nullable=True),
        sa.Column('editora_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['autor_id'], ['autor.id'], ),
        sa.ForeignKeyConstraint(['editora_id'], ['editora.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('pedido',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('usuario_id', sa.Integer(), nullable=True),
        sa.Column('data_pedido', sa.Date(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('valor_total', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuario.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('pagamento',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('pedido_id', sa.Integer(), nullable=True),
        sa.Column('data_pagamento', sa.Date(), nullable=False),
        sa.Column('valor', sa.Float(), nullable=False),
        sa.Column('forma_pagamento', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['pedido_id'], ['pedido.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('pedidolivrolink',
        sa.Column('pedido_id', sa.Integer(), nullable=False),
        sa.Column('livro_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['livro_id'], ['livro.id'], ),
        sa.ForeignKeyConstraint(['pedido_id'], ['pedido.id'], ),
        sa.PrimaryKeyConstraint('pedido_id', 'livro_id')
    )


def downgrade():
    op.drop_table('pedidolivrolink')
    op.drop_table('pagamento')
    op.drop_table('pedido')
    op.drop_table('livro')
    op.drop_table('usuario')
    op.drop_table('editora')
    op.drop_table('autor')
  
