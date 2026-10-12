from __future__ import annotations

import asyncio
import random

from pydantic_settings import BaseSettings, SettingsConfigDict

from .tables import PaymentRecord


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PROCESSOR_")

    min_seconds: float = 2
    max_seconds: float = 5
    # error_rate: float = 0.1
    error_rate: float


settings = Settings.model_validate({})


class ProcessError(Exception): ...


class Processor:
    async def process(self, payment_record: PaymentRecord) -> None:
        sleep_delay = (
            settings.min_seconds
            + (
                random.random()
                * (settings.max_seconds - settings.min_seconds)
            )
        )

        await asyncio.sleep(sleep_delay)

        if random.random() > (1 - settings.error_rate):
            raise ProcessError()
