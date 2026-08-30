"""Исключения библиотеки.

Иерархия повторяет коды ответа API ЮKassa, поэтому ловить можно и широко
(YooKassaError), и точечно (RateLimited). Каждая ошибка несёт разобранное тело
ответа: code, description, parameter и идентификатор запроса. Это ровно то, что
стоит писать в лог и показывать поддержке.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

__all__ = [
    "APIError",
    "BadRequest",
    "ConfigurationError",
    "Forbidden",
    "Gone",
    "NotFound",
    "RateLimited",
    "ResponseProcessing",
    "ServerError",
    "TransportError",
    "Unauthorized",
    "YooKassaError",
    "error_for_status",
]


class YooKassaError(Exception):
    """Базовая ошибка библиотеки. Ловите её, если детали не важны."""


class ConfigurationError(YooKassaError):
    """Клиент собран неверно.

    Например, не передали ключи или задали одновременно OAuth-токен и пару
    shop_id + secret_key. Поднимается при создании клиента, а не при первом
    платеже, чтобы ошибка настройки не всплыла в проде.
    """


class TransportError(YooKassaError):
    """Ответа не было вообще: таймаут, обрыв соединения, сбой DNS.

    Отдельный тип нужен для платежей. Если создание платежа упало с
    TransportError, неизвестно, создан платёж или нет. Повторять такой запрос
    можно только с тем же ключом идемпотентности, иначе возникнет второй
    платёж. Клиент так и делает.
    """


class APIError(YooKassaError):
    """API ответило ошибкой. Тело ответа разобрано в поля."""

    status: int = 0

    def __init__(
        self,
        payload: Mapping[str, Any] | None = None,
        *,
        status: int | None = None,
    ) -> None:
        self.payload: dict[str, Any] = dict(payload or {})
        if status is not None:
            self.status = status

        self.code: str | None = self.payload.get("code")
        self.description: str | None = self.payload.get("description")
        self.parameter: str | None = self.payload.get("parameter")
        self.request_id: str | None = self.payload.get("id")

        super().__init__(self._build_message())

    def _build_message(self) -> str:
        parts = [f"HTTP {self.status}"]
        if self.code:
            parts.append(self.code)
        if self.description:
            parts.append(self.description)
        if self.parameter:
            parts.append(f"параметр: {self.parameter}")
        return ", ".join(parts)


class BadRequest(APIError):
    """400. Запрос не прошёл валидацию, смотрите поле parameter."""

    status = 400


class Unauthorized(APIError):
    """401. Ключ неверен, отозван или не того типа.

    Частая причина: в клиент передали секретный ключ магазина там, где нужен
    OAuth-токен, или наоборот.
    """

    status = 401


class Forbidden(APIError):
    """403. Магазину не разрешена эта операция.

    Самый частый случай: для магазина не включены рекуррентные платежи. Тогда
    касса откажет и в сохранении способа оплаты, и в списании по нему.
    """

    status = 403


class NotFound(APIError):
    """404. Объекта с таким идентификатором нет."""

    status = 404


class Gone(APIError):
    """410. Объект удалён безвозвратно."""

    status = 410


class RateLimited(APIError):
    """429. Слишком много запросов. Клиент повторяет такие сам."""

    status = 429


class ResponseProcessing(APIError):
    """202. Запрос принят, но ещё обрабатывается.

    Это не отказ: ЮKassa просит повторить тот же запрос позже. Клиент повторяет
    сам, и до вызывающего кода ошибка доходит, только если попытки кончились.
    """

    status = 202


class ServerError(APIError):
    """500. Сбой на стороне ЮKassa, состояние операции неизвестно."""

    status = 500


_ERROR_BY_STATUS: dict[int, type[APIError]] = {
    202: ResponseProcessing,
    400: BadRequest,
    401: Unauthorized,
    403: Forbidden,
    404: NotFound,
    410: Gone,
    429: RateLimited,
    500: ServerError,
}


def error_for_status(
    status: int,
    payload: Mapping[str, Any] | None,
) -> APIError:
    """Подобрать класс исключения по коду ответа.

    Неизвестный код заворачивается в APIError с сохранением реального статуса,
    чтобы новые коды не терялись.
    """
    error_class = _ERROR_BY_STATUS.get(status)
    if error_class is not None:
        return error_class(payload)
    return APIError(payload, status=status)
