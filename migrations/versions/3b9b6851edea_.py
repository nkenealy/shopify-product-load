"""empty message

Revision ID: 3b9b6851edea
Revises: 4d8fec5335d2
Create Date: 2014-09-06 16:29:12.179353

"""

# revision identifiers, used by Alembic.
revision = '3b9b6851edea'
down_revision = '4d8fec5335d2'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('products', sa.Column('author_id', sa.Integer(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('products', 'author_id')
    ### end Alembic commands ###
