"""${message}

Revision ID: ${up_revision}
Revises: ${repr(down_revision)}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa

${imports or ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade():
    ${upgrades or "pass"}


def downgrade():
    ${downgrades or "pass"}
