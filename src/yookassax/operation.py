"""Описание одной операции API.

Операции описаны один раз в пакете operations и исполняются обоими клиентами.
Благодаря этому синхронный и асинхронный режимы не могут разойтись в логике:
различается только способ сходить в сеть.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

__all__ = ["Operation"]


def _identity(payload: dict[str, Any]) -> Any:
    return payload


@dataclass(frozen=True, slots=True)
class Operation:
    """Что послать в API и как разобрать ответ.

    Атрибуты:
        method: HTTP-метод.
        path: путь относительно базового адреса, например "/payments".
        body: тело запроса, уже готовое к сериализации в JSON.
        params: параметры строки запроса, None-значения отбрасываются.
        parse: функция, превращающая тело ответа в модель.
        idempotent: операция меняет состояние, нужен ключ идемпотентности.
        idempotency_key: свой ключ; если не задан, клиент сгенерирует.
    """

    method: str
    path: str
    body: Mapping[str, Any] | None = None
    params: Mapping[str, Any] | None = None
    parse: Callable[[dict[str, Any]], Any] = _identity
    idempotent: bool = False
    idempotency_key: str | None = None
