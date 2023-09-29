"""init

Revision ID: e6e6d2b05ad9
Revises: 
Create Date: 2023-09-29 20:10:55.984048

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e6e6d2b05ad9"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "organizations",
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.Column(
            "telephone_numbers", sa.ARRAY(sa.String(length=128)), nullable=True
        ),
        sa.Column("identifier_id", sa.String(length=16), nullable=False),
        sa.Column("pk_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.PrimaryKeyConstraint("pk_id"),
        schema="custom_schema",
    )
    op.create_index(
        op.f("ix_custom_schema_organizations_identifier_id"),
        "organizations",
        ["identifier_id"],
        unique=True,
        schema="custom_schema",
    )
    op.create_table(
        "persons",
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("features", sa.ARRAY(sa.String(length=128)), nullable=True),
        sa.Column("identifier_id", sa.String(length=16), nullable=False),
        sa.Column("pk_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.PrimaryKeyConstraint("pk_id"),
        schema="custom_schema",
    )
    op.create_index(
        op.f("ix_custom_schema_persons_identifier_id"),
        "persons",
        ["identifier_id"],
        unique=False,
        schema="custom_schema",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(
        op.f("ix_custom_schema_persons_identifier_id"),
        table_name="persons",
        schema="custom_schema",
    )
    op.drop_table("persons", schema="custom_schema")
    op.drop_index(
        op.f("ix_custom_schema_organizations_identifier_id"),
        table_name="organizations",
        schema="custom_schema",
    )
    op.drop_table("organizations", schema="custom_schema")
    # ### end Alembic commands ###