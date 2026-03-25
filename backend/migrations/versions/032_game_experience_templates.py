"""Add game experience templates for authored runtime content.

Revision ID: 032
Revises: 031
Create Date: 2026-03-25 23:30:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = '032'
down_revision = '031'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'game_experience_templates',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('key', sa.String(length=120), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('experience_type', sa.String(length=32), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=False),
        sa.Column('style_profile', sa.String(length=80), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('current_version', sa.Integer(), nullable=False),
        sa.Column('published_version', sa.Integer(), nullable=True),
        sa.Column('draft_payload', sa.JSON(), nullable=False),
        sa.Column('published_payload', sa.JSON(), nullable=True),
        sa.Column('created_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('updated_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('published_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('published_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_game_experience_templates_key', 'game_experience_templates', ['key'], unique=True)
    op.create_index('ix_game_experience_templates_status', 'game_experience_templates', ['status'], unique=False)
    op.create_index('ix_game_experience_templates_type_status', 'game_experience_templates', ['experience_type', 'status'], unique=False)


def downgrade():
    op.drop_index('ix_game_experience_templates_type_status', table_name='game_experience_templates')
    op.drop_index('ix_game_experience_templates_status', table_name='game_experience_templates')
    op.drop_index('ix_game_experience_templates_key', table_name='game_experience_templates')
    op.drop_table('game_experience_templates')
