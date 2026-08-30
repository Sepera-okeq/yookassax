"""Сборка запроса и разбор ответа.

Здесь лежит всё, что не зависит от способа сходить в сеть. Синхронный и
асинхронный клиенты вызывают одни и те же функции, поэтому ведут себя
одинаково.
"""

from __future__ import annotations

import uuid
from collections.abc import Mapping
from typing import Any, NamedTuple

from .credentials import Credentials
from .errors import error_for_status
from .operation import Operation

__all__ = ["PreparedRequest", "prepare_request", "parse_response", "DEFAULT_API_URL"]

DEFAULT_API_URL = "https://api.yookassa.ru/v3"


class PreparedRequest(NamedTuple):
    """Готовый к отправке запрос."""

    method: str
    path: str
    params: dict[str, Any]
    headers: dict[str, str]
    body: Mapping[str, Any] | None


def prepare_request(
    operation: Operation,
    credentials: Credentials,
    *,
    user_agent: str,
) -> PreparedRequest:
    """Собрать запрос из описания операции и ключей доступа."""
    headers = {
        "Authorization": credentials.authorization_header(),
        "Accept": "application/json",
        "User-Agent": user_agent,
    }

    if operation.idempotent:
        # Ключ обязателен для всех изменяющих запросов. Без него повтор после
        # обрыва связи создаст второй платёж. Если вызывающий код не передал
        # свой ключ, генерируем его здесь.
        headers["Idempotence-Key"] = operation.idempotency_key or str(uuid.uuid4())

    if operation.body is not None:
        headers["Content-Type"] = "application/json"

    params = {
        key: value
        for key, value in (operation.params or {}).items()
        if value is not None
    }

    return PreparedRequest(
        method=operation.method,
        path=operation.path,
        params=params,
        headers=headers,
        body=operation.body,
    )


def parse_response(status: int, payload: Any) -> dict[str, Any]:
    """Вернуть тело успешного ответа либо поднять исключение.

    Код 202 успехом не считается: ЮKassa приняла запрос, но ещё обрабатывает
    его. Поднимаем ResponseProcessing, чтобы клиент повторил запрос.
    """
    if status == 200:
        return payload if isinstance(payload, dict) else {}

    raise error_for_status(status, payload if isinstance(payload, dict) else None)
