"""Асинхронный клиент."""

from __future__ import annotations

import asyncio
from typing import Any

import httpx

from .. import resources
from ..errors import TransportError
from ..operation import Operation
from ..retry import should_retry
from ..transport import parse_response
from .base import BaseClient
from .response import read_json

__all__ = ["AsyncYooKassa"]


class AsyncYooKassa(BaseClient):
    """Асинхронный клиент ЮKassa.

    Пример:

        async with AsyncYooKassa(shop_id="123456", secret_key="live_...") as kassa:
            payment = await kassa.payments.create({
                "amount": {"value": "100.00", "currency": "RUB"},
                "confirmation": {
                    "type": "redirect",
                    "return_url": "https://example.com/done",
                },
                "capture": True,
            })

    Этот режим нужен в FastAPI и любом другом асинхронном приложении.
    Синхронный HTTP-вызов внутри асинхронного обработчика останавливает весь
    воркер, а не один запрос: пока идёт обращение к API, процесс не обслуживает
    никого.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._http = httpx.AsyncClient(base_url=self._api_url, timeout=self._timeout)

        self.payments = resources.AsyncPayments(self)
        self.refunds = resources.AsyncRefunds(self)
        self.receipts = resources.AsyncReceipts(self)
        self.payouts = resources.AsyncPayouts(self)
        self.webhooks = resources.AsyncWebhooks(self)
        self.settings = resources.AsyncSettings(self)
        self.payment_methods = resources.AsyncPaymentMethods(self)
        self.deals = resources.AsyncDeals(self)
        self.invoices = resources.AsyncInvoices(self)
        self.personal_data = resources.AsyncPersonalData(self)
        self.self_employed = resources.AsyncSelfEmployed(self)
        self.pos_links = resources.AsyncPosLinks(self)
        self.sbp_banks = resources.AsyncSbpBanks(self)

    async def send(self, operation: Operation) -> Any:
        """Выполнить операцию.

        Обычно вызывается через ресурсы, напрямую нужен только для эндпоинтов,
        которых ещё нет в библиотеке.
        """
        request = self._prepare(operation)
        last_error: Exception | None = None

        for attempt in range(1, self._retry.attempts + 1):
            try:
                response = await self._http.request(
                    request.method,
                    request.path,
                    params=request.params,
                    headers=request.headers,
                    json=request.body,
                )
            except httpx.HTTPError as exc:
                # Ответа нет вообще, состояние операции неизвестно. Повторять
                # можно: ключ идемпотентности в заголовках тот же, поэтому
                # второго платежа не возникнет.
                last_error = TransportError(f"Запрос к ЮKassa не удался: {exc}")
                if attempt < self._retry.attempts:
                    await asyncio.sleep(self._retry.delay(attempt))
                    continue
                raise last_error from exc

            try:
                payload = parse_response(response.status_code, read_json(response))
                return operation.parse(payload)
            except Exception as exc:
                last_error = exc
                if should_retry(exc) and attempt < self._retry.attempts:
                    await asyncio.sleep(self._retry.delay(attempt))
                    continue
                raise

        # Сюда можно попасть только при attempts <= 0, что запрещено
        # в BaseClient: там стоит max(1, retries).
        raise RuntimeError(  # pragma: no cover
            "Цикл повторов завершился без результата"
        ) from last_error

    async def aclose(self) -> None:
        """Закрыть соединения."""
        await self._http.aclose()

    async def __aenter__(self) -> AsyncYooKassa:
        return self

    async def __aexit__(self, *exc_info: Any) -> None:
        await self.aclose()
