from __future__ import annotations

from typing import Literal
from enum import StrEnum

type CurrencyType = Literal["RUB", "USD", "EUR"]
type StatusType = Literal["pending", "succeeded", "failed"]
type OutboxStatusType = Literal["new", "sent"]


class CurrencyEnum(StrEnum):
    RUB = "RUB"
    USD = "USD"
    EUR = "EUR"


class StatusEnum(StrEnum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class OutboxStatusEnum(StrEnum):
    NEW = "new"
    SENT = "sent"
