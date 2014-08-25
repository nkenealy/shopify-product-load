"""empty message

Revision ID: 4821e8095cb3
Revises: 4ffc981e8ac8
Create Date: 2014-08-25 06:34:40.299906

"""

# revision identifiers, used by Alembic.
revision = '4821e8095cb3'
down_revision = '4ffc981e8ac8'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('SKU', sa.Text(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('posts', 'SKU')
    ### end Alembic commands ###
