"""Разбор входящего уведомления."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from ..models import Deal, Payment, PaymentMethod, Payout, Refund
from ..models.base import ModelClass

__all__ = ["EVENTS", "Notification", "parse"]

# События, на которые можно подписаться.
EVENTS: tuple[str, ...] = (
    "payment.succeeded",
    "payment.waiting_for_capture",
    "payment.canceled",
    "refund.succeeded",
    "payout.succeeded",
    "payout.canceled",
    "deal.closed",
    # Привязка способа оплаты на нулевую сумму: приходит, когда способ
    # сохранён и по нему можно списывать.
    "payment_method.active",
)

# Первая часть события определяет тип объекта в теле.
_MODEL_BY_OBJECT_TYPE: dict[str, ModelClass] = {
    "payment": Payment,
    "refund": Refund,
    "payout": Payout,
    "deal": Deal,
    "payment_method": PaymentMethod,
}


@dataclass(slots=True)
class Notification:
    """Разобранное уведомление."""

    event: str
    object: Any
    type: str | None = None
    raw: dict[str, Any] | None = None

    @property
    def object_type(self) -> str:
        """Тип объекта: payment, refund, payout, deal или payment_method."""
        return self.event.split(".", 1)[0]

    @property
    def is_payment_succeeded(self) -> bool:
        """Платёж прошёл."""
        return self.event == "payment.succeeded"

    @property
    def is_payment_canceled(self) -> bool:
        """Платёж отменён."""
        return self.event == "payment.canceled"

    @property
    def is_refund_succeeded(self) -> bool:
        """Возврат прошёл."""
        return self.event == "refund.succeeded"

    @property
    def is_payment_method_active(self) -> bool:
        """Способ оплаты привязан, по нему можно списывать."""
        return self.event == "payment_method.active"


def parse(payload: Mapping[str, Any]) -> Notification:
    """Разобрать тело уведомления.

    Неизвестное событие разбор не роняет: поле object останется словарём, а
    приложение само решит, что с ним делать. Это важно, потому что ЮKassa
    добавляет события, а отказ обработать уведомление приводит к бесконечным
    повторам с её стороны.
    """
    data = dict(payload or {})
    event = str(data.get("event") or "")
    body = data.get("object")

    model = _MODEL_BY_OBJECT_TYPE.get(event.split(".", 1)[0])
    if model is not None and isinstance(body, Mapping):
        parsed_object: Any = model.from_api(body)
    else:
        parsed_object = body

    return Notification(
        event=event,
        object=parsed_object,
        type=data.get("type"),
        raw=data,
    )
