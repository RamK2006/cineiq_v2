"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2026-05-09

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('clerk_id', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('display_name', sa.String(), nullable=True),
        sa.Column('taste_vector', postgresql.ARRAY(sa.Float()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('clerk_id')
    )
    op.create_index('ix_users_clerk_id', 'users', ['clerk_id'])

    # Create ratings table
    op.create_table(
        'ratings',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tmdb_id', sa.Integer(), nullable=False),
        sa.Column('rating', sa.Float(), nullable=False),
        sa.Column('watched_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('source', sa.Enum('manual', 'import', 'implicit', name='ratingsource'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_ratings_user_id', 'ratings', ['user_id'])
    op.create_index('ix_ratings_tmdb_id', 'ratings', ['tmdb_id'])

    # Create watch_sessions table
    op.create_table(
        'watch_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('room_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('host_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tmdb_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('max_participants', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['host_user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('room_id')
    )
    op.create_index('ix_watch_sessions_room_id', 'watch_sessions', ['room_id'])

    # Create watch_participants table
    op.create_table(
        'watch_participants',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('left_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['watch_sessions.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_watch_participants_session_id', 'watch_participants', ['session_id'])

    # Create import_jobs table
    op.create_table(
        'import_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('source', sa.Enum('letterboxd', 'trakt', name='importsource'), nullable=False),
        sa.Column('status', sa.Enum('pending', 'processing', 'completed', 'failed', name='importstatus'), nullable=True),
        sa.Column('total_items', sa.Integer(), nullable=True),
        sa.Column('processed_items', sa.Integer(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_import_jobs_user_id', 'import_jobs', ['user_id'])

    # Create movies cache table
    op.create_table(
        'movies',
        sa.Column('tmdb_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('overview', sa.Text(), nullable=True),
        sa.Column('release_date', sa.String(), nullable=True),
        sa.Column('genres', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('director', sa.String(), nullable=True),
        sa.Column('cast', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('poster_path', sa.String(), nullable=True),
        sa.Column('backdrop_path', sa.String(), nullable=True),
        sa.Column('runtime', sa.Integer(), nullable=True),
        sa.Column('vote_average', sa.Float(), nullable=True),
        sa.Column('vote_count', sa.Integer(), nullable=True),
        sa.Column('popularity', sa.Float(), nullable=True),
        sa.Column('keywords', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('cached_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('tmdb_id')
    )


def downgrade() -> None:
    op.drop_table('movies')
    op.drop_index('ix_import_jobs_user_id')
    op.drop_table('import_jobs')
    op.drop_index('ix_watch_participants_session_id')
    op.drop_table('watch_participants')
    op.drop_index('ix_watch_sessions_room_id')
    op.drop_table('watch_sessions')
    op.drop_index('ix_ratings_tmdb_id')
    op.drop_index('ix_ratings_user_id')
    op.drop_table('ratings')
    op.drop_index('ix_users_clerk_id')
    op.drop_table('users')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS ratingsource')
    op.execute('DROP TYPE IF EXISTS importsource')
    op.execute('DROP TYPE IF EXISTS importstatus')
