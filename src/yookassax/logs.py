"""Логи обращений к API.

Пишем стандартным logging, а не loguru или чем-то ещё: библиотека не должна
навязывать приложению логгер. Приложения на loguru подхватывают эти записи
своим InterceptHandler, приложения на logging - как обычно.

По умолчанию у логгера нет обработчика, поэтому пишет он только там, где
логирование настроено. Отдельно включать ничего не нужно:

    import logging
    logging.getLogger("yookassax").setLevel(logging.DEBUG)   # с телами

Что попадает в лог:

    INFO     метод, путь, код ответа, длительность, идентификатор запроса
    WARNING  повторы, обрывы связи, ответы с ошибкой
    DEBUG    то же плюс тело запроса и тело ответа

Чего в логе нет никогда: заголовка Authorization. В нём лежат секретный ключ
магазина или OAuth-токен, а лог живёт дольше и читается шире, чем кажется в
момент отладки. Тела запроса и ответа пишутся только на DEBUG: там персональные
данные плательщика, и их место не в общем логе.
"""

from __future__ import annotations

import json
import logging
from typing import Any

__all__ = ["logger", "log_request", "log_response", "log_retry", "log_transport_error"]

logger = logging.getLogger("yookassax")

# Заголовки, которые нельзя писать в лог ни на каком уровне.
_SECRET_HEADERS = frozenset({"authorization"})


def _safe_headers(headers: dict[str, str]) -> dict[str, str]:
    """Заголовки без секретов."""
    return {
        name: ("<скрыто>" if name.lower() in _SECRET_HEADERS else value)
        for name, value in headers.items()
    }


def _body(payload: Any) -> str:
    """Тело для лога. Нечитаемое не роняет логирование."""
    try:
        return json.dumps(payload, ensure_ascii=False)
    except (TypeError, ValueError):
        return repr(payload)


def log_request(method: str, path: str, headers: dict[str, str], body: Any) -> None:
    """Запрос уходит в ЮKassa."""
    if not logger.isEnabledFor(logging.DEBUG):
        return

    logger.debug(
        "ЮKassa запрос: %s %s, заголовки: %s, тело: %s",
        method,
        path,
        _safe_headers(headers),
        _body(body),
    )


def log_response(
    method: str,
    path: str,
    status: int,
    elapsed: float,
    payload: Any,
    attempt: int,
) -> None:
    """Ответ получен. Код ответа решает, насколько громко об этом сказать."""
    request_id = payload.get("id") if isinstance(payload, dict) else None
    level = logging.INFO if status < 400 else logging.WARNING
    suffix = "" if attempt == 1 else f", попытка {attempt}"

    logger.log(
        level,
        "ЮKassa ответ: %s %s -> %s за %.3f c, id: %s%s",
        method,
        path,
        status,
        elapsed,
        request_id,
        suffix,
    )

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("ЮKassa тело ответа: %s %s -> %s", method, path, _body(payload))


def log_retry(method: str, path: str, attempt: int, delay: float, reason: str) -> None:
    """Повтор запроса. Ключ идемпотентности тот же, второго платежа не будет."""
    logger.warning(
        "ЮKassa повтор: %s %s, попытка %s через %.3f c, причина: %s",
        method,
        path,
        attempt + 1,
        delay,
        reason,
    )


def log_transport_error(method: str, path: str, attempt: int, reason: str) -> None:
    """Ответа не было вообще: состояние операции неизвестно."""
    logger.warning(
        "ЮKassa без ответа: %s %s, попытка %s, причина: %s",
        method,
        path,
        attempt,
        reason,
    )
