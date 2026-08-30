"""Синхронный клиент."""

from __future__ import annotations

import time
from typing import Any

import httpx

from .. import logs, resources
from ..errors import TransportError
from ..operation import Operation
from ..retry import should_retry
from ..transport import parse_response
from .base import BaseClient
from .response import read_json

__all__ = ["YooKassa"]


class YooKassa(BaseClient):
    """Синхронный клиент ЮKassa.

    Пример:

        with YooKassa(shop_id="123456", secret_key="live_...") as kassa:
            payment = kassa.payments.create({
                "amount": {"value": "100.00", "currency": "RUB"},
                "confirmation": {
                    "type": "redirect",
                    "return_url": "https://example.com/done",
                },
                "capture": True,
            })
            print(payment.confirmation_url)

    Без конструкции with соединения закроются при сборке мусора. Для скриптов
    это нормально, в долгоживущем процессе лучше закрывать явно вызовом close.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._http = httpx.Client(base_url=self._api_url, timeout=self._timeout)

        self.payments = resources.Payments(self)
        self.refunds = resources.Refunds(self)
        self.receipts = resources.Receipts(self)
        self.payouts = resources.Payouts(self)
        self.webhooks = resources.Webhooks(self)
        self.settings = resources.Settings(self)
        self.payment_methods = resources.PaymentMethods(self)
        self.deals = resources.Deals(self)
        self.invoices = resources.Invoices(self)
        self.personal_data = resources.PersonalData(self)
        self.self_employed = resources.SelfEmployed(self)
        self.pos_links = resources.PosLinks(self)
        self.sbp_banks = resources.SbpBanks(self)

    def send(self, operation: Operation) -> Any:
        """Выполнить операцию.

        Обычно вызывается через ресурсы, напрямую нужен только для эндпоинтов,
        которых ещё нет в библиотеке.
        """
        request = self._prepare(operation)
        last_error: Exception | None = None

        for attempt in range(1, self._retry.attempts + 1):
            logs.log_request(
                request.method, request.path, request.headers, request.body
            )
            started = time.monotonic()
            try:
                response = self._http.request(
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
                logs.log_transport_error(
                    request.method, request.path, attempt, str(exc)
                )
                last_error = TransportError(f"Запрос к ЮKassa не удался: {exc}")
                if attempt < self._retry.attempts:
                    delay = self._retry.delay(attempt)
                    logs.log_retry(
                        request.method, request.path, attempt, delay, "нет ответа"
                    )
                    time.sleep(delay)
                    continue
                raise last_error from exc

            payload = read_json(response)
            logs.log_response(
                request.method,
                request.path,
                response.status_code,
                time.monotonic() - started,
                payload,
                attempt,
            )
            try:
                return operation.parse(parse_response(response.status_code, payload))
            except Exception as exc:
                last_error = exc
                if should_retry(exc) and attempt < self._retry.attempts:
                    delay = self._retry.delay(attempt)
                    logs.log_retry(
                        request.method, request.path, attempt, delay, type(exc).__name__
                    )
                    time.sleep(delay)
                    continue
                raise

        # Сюда можно попасть только при attempts <= 0, что запрещено
        # в BaseClient: там стоит max(1, retries).
        raise RuntimeError(  # pragma: no cover
            "Цикл повторов завершился без результата"
        ) from last_error

    def close(self) -> None:
        """Закрыть соединения."""
        self._http.close()

    def __enter__(self) -> YooKassa:
        return self

    def __exit__(self, *exc_info: Any) -> None:
        self.close()
