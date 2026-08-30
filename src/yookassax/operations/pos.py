"""Операции с кассовыми ссылками и справочником СБП."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ..models import Page, PosLink, SbpBank
from ..operation import Operation

__all__ = [
    "pos_link_activate",
    "pos_link_change_recipient",
    "pos_link_create",
    "pos_link_deactivate",
    "pos_link_get",
    "sbp_bank_list",
]

POS_LINKS_PATH = "/pos_links"


def pos_link_create(
    params: Mapping[str, Any],
    *,
    idempotency_key: str | None = None,
) -> Operation:
    """Создать ссылку на оплату в кассе."""
    return Operation(
        method="POST",
        path=POS_LINKS_PATH,
        body=params,
        parse=PosLink.from_api,
        idempotent=True,
        idempotency_key=idempotency_key,
    )


def pos_link_get(pos_link_id: str) -> Operation:
    """Запросить кассовую ссылку."""
    return Operation(
        method="GET",
        path=f"{POS_LINKS_PATH}/{pos_link_id}",
        parse=PosLink.from_api,
    )


def pos_link_activate(
    pos_link_id: str,
    *,
    idempotency_key: str | None = None,
) -> Operation:
    """Активировать кассовую ссылку."""
    return Operation(
        method="POST",
        path=f"{POS_LINKS_PATH}/{pos_link_id}/activate",
        body={},
        parse=PosLink.from_api,
        idempotent=True,
        idempotency_key=idempotency_key,
    )


def pos_link_deactivate(
    pos_link_id: str,
    *,
    idempotency_key: str | None = None,
) -> Operation:
    """Деактивировать кассовую ссылку."""
    return Operation(
        method="POST",
        path=f"{POS_LINKS_PATH}/{pos_link_id}/deactivate",
        body={},
        parse=PosLink.from_api,
        idempotent=True,
        idempotency_key=idempotency_key,
    )


def pos_link_change_recipient(
    pos_link_id: str,
    params: Mapping[str, Any],
    *,
    idempotency_key: str | None = None,
) -> Operation:
    """Сменить получателя по кассовой ссылке."""
    return Operation(
        method="POST",
        # Метод называется change_recipient, а путь в API просто /recipient.
        # Сверено с официальной спецификацией OpenAPI.
        path=f"{POS_LINKS_PATH}/{pos_link_id}/recipient",
        body=params,
        parse=PosLink.from_api,
        idempotent=True,
        idempotency_key=idempotency_key,
    )


def sbp_bank_list() -> Operation:
    """Справочник банков СБП."""
    return Operation(
        method="GET",
        path="/sbp_banks",
        parse=lambda payload: Page.of(SbpBank, payload),
    )
