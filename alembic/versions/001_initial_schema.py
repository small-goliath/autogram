"""Initial schema

Revision ID: 001
Revises:
Create Date: 2025-10-30

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create admin table
    op.create_table(
        "admin",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("password", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_admin_username"), "admin", ["username"], unique=True)

    # Create sns_raise_user table
    op.create_table(
        "sns_raise_user",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_sns_raise_user_username"), "sns_raise_user", ["username"], unique=True
    )

    # Create helper table
    op.create_table(
        "helper",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("instagram_username", sa.String(length=100), nullable=False),
        sa.Column("instagram_password", sa.String(length=255), nullable=False),
        sa.Column("session_data", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("last_used_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_helper_instagram_username"),
        "helper",
        ["instagram_username"],
        unique=True,
    )

    # Create request_by_week table
    op.create_table(
        "request_by_week",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("instagram_link", sa.String(length=500), nullable=False),
        sa.Column("week_start_date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["username"], ["sns_raise_user.username"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_request_by_week_username", "request_by_week", ["username"], unique=False
    )
    op.create_index(
        "idx_request_by_week_week_start_date",
        "request_by_week",
        ["week_start_date"],
        unique=False,
    )

    # Create user_action_verification table
    op.create_table(
        "user_action_verification",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("instagram_link", sa.String(length=500), nullable=False),
        sa.Column("link_owner_username", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["username"], ["sns_raise_user.username"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["link_owner_username"], ["sns_raise_user.username"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_user_action_verification_username",
        "user_action_verification",
        ["username"],
        unique=False,
    )
    op.create_index(
        "idx_user_action_verification_link",
        "user_action_verification",
        ["instagram_link"],
        unique=False,
    )

    # Create consumer table
    op.create_table(
        "consumer",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("instagram_username", sa.String(length=100), nullable=False),
        sa.Column(
            "status",
            sa.Enum("pending", "active", "inactive", name="statusenum"),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_consumer_instagram_username"),
        "consumer",
        ["instagram_username"],
        unique=True,
    )

    # Create producer table
    op.create_table(
        "producer",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("instagram_username", sa.String(length=100), nullable=False),
        sa.Column("instagram_password", sa.String(length=255), nullable=False),
        sa.Column("verification_code", sa.String(length=50), nullable=True),
        sa.Column("session_data", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("pending", "active", "inactive", name="statusenum"),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("last_used_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_producer_instagram_username"),
        "producer",
        ["instagram_username"],
        unique=True,
    )

    # Create announcement table
    op.create_table(
        "announcement",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("kakao_openchat_link", sa.String(length=500), nullable=True),
        sa.Column("kakao_qr_code_url", sa.String(length=500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("announcement")
    op.drop_table("producer")
    op.drop_table("consumer")
    op.drop_table("user_action_verification")
    op.drop_table("request_by_week")
    op.drop_table("helper")
    op.drop_table("sns_raise_user")
    op.drop_table("admin")
