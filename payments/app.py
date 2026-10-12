from __future__ import annotations

import logging

from typing import Annotated
from collections.abc import AsyncGenerator
from uuid import UUID

from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession

from faststream.rabbit import RabbitBroker

from fastapi import FastAPI, Header, Depends, HTTPException
from fastapi import status

from .types import OutboxStatusEnum
from .tables import PaymentRecord, OutboxRecord, async_session_maker
from .models import CreatePaymentModel, CreatePaymentResponseModel, PaymentModel
from .consumer import broker, payments_queue
from .settings import settings


logger = logging.getLogger('uvicorn.error')


async def check_api_key(
    x_api_key: Annotated[str, Header(alias="X-API-Key")],
) -> None:
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_broker() -> AsyncGenerator[RabbitBroker, None]:
    async with broker:
        yield broker


type Session = Annotated[AsyncSession, Depends(get_async_session)]
type Broker = Annotated[RabbitBroker, Depends(get_broker)]


app = FastAPI(
    dependencies=[
        Depends(check_api_key),
    ],
)


@app.post("/api/v1/payments", status_code=status.HTTP_202_ACCEPTED)
async def create_payment(
    session: Session,
    broker_: Broker,
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key")],
    data: CreatePaymentModel,
) -> CreatePaymentResponseModel:
    stmt = (
        exists()
        .where(PaymentRecord.idempotency_key == idempotency_key)
        .select()
    )
    if (await session.execute(stmt)).scalar_one():
        logger.info(f"Payment with idempotency-key='{idempotency_key}' already exist")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
        )

    logger.info("Start first outbox pattern phase")
    payment_record = PaymentRecord(
        idempotency_key=idempotency_key, **data.model_dump(mode="python")
    )
    outbox_record = OutboxRecord(data=data.model_dump(mode="json"))

    session.add_all([payment_record, outbox_record])
    await session.commit()

    logger.info("First phase outbox pattern complete")
    logger.info("Start second outbox pattern phase")

    outbox_record.status = OutboxStatusEnum.SENT

    logger.info("Publish message")
    await broker_.publish(
        str(payment_record.payment_id),
        queue=payments_queue,
    )
    await session.commit()

    logger.info("First phase outbox pattern complete")

    return CreatePaymentResponseModel.model_validate(payment_record)


@app.get("/api/v1/payments/{payment_id}")
async def get_payment(session: Session, payment_id: UUID) -> PaymentModel:
    stmt = select(PaymentRecord).where(PaymentRecord.payment_id == payment_id).limit(1)
    row = (await session.execute(stmt)).first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return PaymentModel.model_validate(row[0])