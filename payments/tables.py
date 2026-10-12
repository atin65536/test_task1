from __future__ import annotations

from typing import Any

from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import String, TEXT, DECIMAL, TIMESTAMP, UUID as UUIDColumn
from sqlalchemy.dialects.postgresql import ENUM as PGENUM, JSONB as PGJSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from .types import CurrencyEnum, StatusEnum, OutboxStatusEnum
from .settings import settings


class BaseTable(DeclarativeBase): ...


class PaymentRecord(MappedAsDataclass, BaseTable):
    __tablename__ = "payments"

    sum: Mapped[Decimal] = mapped_column(name="sum", type_=DECIMAL)
    currency: Mapped[CurrencyEnum] = mapped_column(
        name="currency",
        type_=PGENUM(CurrencyEnum),
    )
    description: Mapped[str] = mapped_column(name="description", type_=TEXT)
    meta: Mapped[dict[str, Any] | None] = mapped_column(
        name="meta",
        type_=PGJSONB,
        nullable=True,
    )
    idempotency_key: Mapped[str] = mapped_column(
        name="idempotency_key",
        type_=String(4096),
        unique=True,
    )
    webhook_url: Mapped[str] = mapped_column(
        name="webhook_url",
        type_=String(4096),
    )

    status: Mapped[StatusEnum] = mapped_column(
        name="status",
        type_=PGENUM(StatusEnum),
        default=StatusEnum.PENDING,
    )
    created_at: Mapped[datetime] = mapped_column(
        name="created_at",
        type_=TIMESTAMP,
        default_factory=datetime.now,
    )
    processed_at: Mapped[datetime | None] = mapped_column(
        name="processed_at",
        type_=TIMESTAMP,
        nullable=True,
        default=None,
    )
    payment_id: Mapped[UUID] = mapped_column(
        primary_key=True,
        name="payment_id",
        type_=UUIDColumn,
        default_factory=uuid4,
    )


class OutboxRecord(MappedAsDataclass, BaseTable):
    __tablename__ = "outbox"

    data: Mapped[dict[str, Any] | None] = mapped_column(
        name="data",
        type_=PGJSONB,
        nullable=True,
    )

    status: Mapped[OutboxStatusEnum] = mapped_column(
        name="status",
        type_=PGENUM(OutboxStatusEnum),
        default=OutboxStatusEnum.NEW,
    )
    outbox_id: Mapped[UUID] = mapped_column(
        primary_key=True,
        name="outbox_id",
        type_=UUIDColumn,
        default_factory=uuid4,
    )


engine = create_async_engine(settings.database_dsn)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
