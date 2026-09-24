"""001_initial_schema: Complete schema creation for LawerAI

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-24

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # 2. chat_sessions
    op.create_table(
        'chat_sessions',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('language', sa.String(length=20), nullable=True),
        sa.Column('case_category', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(op.f('ix_chat_sessions_user_id'), 'chat_sessions', ['user_id'], unique=False)

    # 3. messages
    op.create_table(
        'messages',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('session_id', sa.String(length=36), sa.ForeignKey('chat_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('structured_data', sa.JSON(), nullable=True),
        sa.Column('citations', sa.JSON(), nullable=True),
        sa.Column('is_emergency', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(op.f('ix_messages_session_id'), 'messages', ['session_id'], unique=False)

    # 4. case_summaries
    op.create_table(
        'case_summaries',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('session_id', sa.String(length=36), sa.ForeignKey('chat_sessions.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('issue_type', sa.String(length=200), nullable=True),
        sa.Column('parties', sa.String(length=255), nullable=True),
        sa.Column('dates', sa.String(length=255), nullable=True),
        sa.Column('location_province', sa.String(length=100), nullable=True),
        sa.Column('documents_mentioned', sa.JSON(), nullable=True),
        sa.Column('stage', sa.String(length=50), nullable=True),
        sa.Column('applicable_laws', sa.JSON(), nullable=True),
        sa.Column('next_steps', sa.JSON(), nullable=True),
        sa.Column('evidence_checklist', sa.JSON(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )

    # 5. uploaded_documents
    op.create_table(
        'uploaded_documents',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('session_id', sa.String(length=36), sa.ForeignKey('chat_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('file_type', sa.String(length=100), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('extracted_text', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(op.f('ix_uploaded_documents_session_id'), 'uploaded_documents', ['session_id'], unique=False)

    # 6. emergency_logs
    op.create_table(
        'emergency_logs',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('session_id', sa.String(length=36), nullable=True),
        sa.Column('trigger_reason', sa.String(length=100), nullable=False),
        sa.Column('user_message', sa.Text(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=True),
    )

    # 7. feedbacks
    op.create_table(
        'feedbacks',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('session_id', sa.String(length=36), sa.ForeignKey('chat_sessions.id', ondelete='CASCADE'), nullable=True),
        sa.Column('message_id', sa.String(length=36), sa.ForeignKey('messages.id', ondelete='SET NULL'), nullable=True),
        sa.Column('feedback_type', sa.String(length=50), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('query_excerpt', sa.String(length=500), nullable=True),
        sa.Column('citations_flagged', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(op.f('ix_feedbacks_user_id'), 'feedbacks', ['user_id'], unique=False)
    op.create_index(op.f('ix_feedbacks_session_id'), 'feedbacks', ['session_id'], unique=False)
    op.create_index(op.f('ix_feedbacks_message_id'), 'feedbacks', ['message_id'], unique=False)


def downgrade() -> None:
    op.drop_table('feedbacks')
    op.drop_table('emergency_logs')
    op.drop_table('uploaded_documents')
    op.drop_table('case_summaries')
    op.drop_table('messages')
    op.drop_table('chat_sessions')
    op.drop_table('users')
