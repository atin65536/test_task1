from __future__ import annotations

from typing import Any

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from .types import CurrencyType, StatusType


class PaymentModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    payment_id: UUID
    sum: Decimal
    currency: CurrencyType
    description: str
    meta: dict[str, Any] | None
    status: StatusType
    idempotency_key: str
    webhook_url: str
    created_at: datetime
    processed_at: datetime | None


class CreatePaymentModel(BaseModel):
    sum: Decimal
    currency: CurrencyType
    description: str
    meta: dict[str, Any] | None = None
    webhook_url: str


class CreatePaymentResponseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    payment_id: UUID
    status: StatusType
    created_at: datetime