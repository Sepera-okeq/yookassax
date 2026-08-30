"""Настройки магазина и подписки на уведомления."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, ClassVar

from .base import Model, ModelClass
from .common import Amount

__all__ = ["Me", "Webhook"]


@dataclass(slots=True)
class Me(Model):
    """Ответ GET /me: кто мы для ЮKassa.

    Поле test показывает, тестовый ли магазин. Полезно проверять на старте:
    боевые ключи в тестовом окружении и наоборот выясняются иначе только при
    первом платеже.
    """

    account_id: str | None = None
    status: str | None = None
    test: bool | None = None
    fiscalization: dict[str, Any] | None = None
    fiscalization_enabled: bool | None = None
    payment_methods: list[str] | None = None
    payout_methods: list[str] | None = None
    itn: str | None = None
    name: str | None = None
    payout_balance: Amount | None = None

    nested_models: ClassVar[dict[str, ModelClass]] = {"payout_balance": Amount}


@dataclass(slots=True)
class Webhook(Model):
    """Подписка на уведомление.

    Не путать с самим уведомлением: его разбор находится в пакете webhooks.
    """

    id: str | None = None
    event: str | None = None
    url: str | None = None
