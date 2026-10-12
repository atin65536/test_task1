from __future__ import annotations

from typing import Annotated
from collections.abc import AsyncGenerator
from datetime import datetime
from uuid import UUID

import httpx

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tenacity import retry, wait_exponential, stop_after_attempt

from faststream import FastStream, Logger, Depends
from faststream.exceptions import RejectMessage
from faststream.rabbit import (
    ExchangeType,
    RabbitBroker,
    RabbitExchange,
    RabbitMessage,
    RabbitQueue,
)

from .types import StatusEnum
from .tables import PaymentRecord, async_session_maker
from .processor import Processor, ProcessError
from .settings import settings


broker = RabbitBroker(settings.rabbitmq_dsn)

dead_letter_exchange = RabbitExchange(
    name="payments.dead-letter-exchange",
    type=ExchangeType.DIRECT,
)
dead_letter_queue = RabbitQueue("payments.dead", routing_key="payments.dead")


async def on_startup() -> None:
    await broker.connect()
    exchange = await broker.declare_exchange(dead_letter_exchange)
    queue = await broker.declare_queue(dead_letter_queue)
    await queue.bind(exchange=exchange)


app = FastStream(broker, on_startup=[on_startup])


payments_queue = RabbitQueue(
    "payments.new",
    arguments={
        "x-dead-letter-exchange": "payments.dead-letter-exchange",
        "x-dead-letter-routing-key": "payments.dead",
    },
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


@broker.subscriber(payments_queue)
async def process_payment(
    logger: Logger,
    session: Annotated[AsyncSession, Depends(get_session)],
    payment_id: UUID,
) -> None:
    try:
        logger.info(f"Start process payment '{payment_id}'")

        stmt = select(PaymentRecord).where(PaymentRecord.payment_id == payment_id)
        payment_record: PaymentRecord = (await session.scalars(stmt)).one()

        logger.info(f"Process payment '{payment_id}'")
        processor = Processor()
        try:
            await processor.process(payment_record)
            new_status = StatusEnum.SUCCEEDED
        except ProcessError:
            new_status = StatusEnum.FAILED

        logger.info(f"Update payment status to `{new_status}`")
        payment_record.status = new_status
        payment_record.processed_at = datetime.utcnow()
        await session.commit()

        @retry(stop=stop_after_attempt(3), wait=wait_exponential(0.5))
        async def send_webhook() -> None:
            logger.info(f"Send message to webhook: {payment_record.webhook_url}")
            async with httpx.AsyncClient() as client:
                response = await client.get(payment_record.webhook_url)
                if response.status_code != 200:
                    raise Exception("Invalid webhook status code")

        if new_status == StatusEnum.SUCCEEDED:
            await send_webhook()

        logger.info(f"Payment '{payment_id}' processed")
    except Exception as e:
        raise RejectMessage() from e


