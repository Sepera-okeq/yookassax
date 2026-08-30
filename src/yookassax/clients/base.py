"""Общая часть клиентов: ключи, адрес, политика повторов."""

from __future__ import annotations

from .._version import __version__
from ..credentials import Credentials
from ..operation import Operation
from ..retry import RetryPolicy
from ..transport import DEFAULT_API_URL, PreparedRequest, prepare_request

__all__ = ["BaseClient", "USER_AGENT"]

USER_AGENT = f"yookassax/{__version__}"


class BaseClient:
    """То, что одинаково у синхронного и асинхронного клиентов."""

    def __init__(
        self,
        *,
        shop_id: str | int | None = None,
        secret_key: str | None = None,
        oauth_token: str | None = None,
        api_url: str = DEFAULT_API_URL,
        timeout: float = 30.0,
        retries: int = 3,
    ) -> None:
        """Собрать клиент.

        Аргументы:
            shop_id: идентификатор магазина.
            secret_key: секретный ключ магазина.
            oauth_token: токен доступа к чужому магазину. Задаётся вместо
                пары shop_id и secret_key.
            api_url: базовый адрес API. Меняют только в тестах.
            timeout: таймаут одного запроса в секундах.
            retries: сколько всего попыток делать, считая первую.
        """
        self._credentials = Credentials.build(shop_id, secret_key, oauth_token)
        self._api_url = api_url.rstrip("/")
        self._timeout = timeout
        self._retry = RetryPolicy(attempts=max(1, retries))

    def _prepare(self, operation: Operation) -> PreparedRequest:
        return prepare_request(
            operation,
            self._credentials,
            user_agent=USER_AGENT,
        )
