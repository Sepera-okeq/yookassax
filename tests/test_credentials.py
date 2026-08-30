"""Проверка сборки учётных данных."""

from __future__ import annotations

import base64

import pytest

from yookassax import ConfigurationError, YooKassa
from yookassax.credentials import Credentials


def test_shop_pair_encodes_to_basic_auth():
    credentials = Credentials.build("123456", "secret", None)
    header = credentials.authorization_header()

    assert header.startswith("Basic ")
    decoded = base64.b64decode(header.removeprefix("Basic ")).decode()
    assert decoded == "123456:secret"


def test_oauth_token_sent_as_bearer():
    credentials = Credentials.build(None, None, "oauth_token_value")

    assert credentials.authorization_header() == "Bearer oauth_token_value"


def test_client_requires_credentials():
    """Ошибка настройки должна всплыть сразу, а не на первом платеже."""
    with pytest.raises(ConfigurationError):
        YooKassa()


def test_both_auth_methods_rejected():
    """OAuth и пара магазина взаимоисключающие, молча выбирать один нельзя."""
    with pytest.raises(ConfigurationError):
        YooKassa(shop_id="1", secret_key="s", oauth_token="t")


def test_shop_id_without_secret_rejected():
    with pytest.raises(ConfigurationError):
        YooKassa(shop_id="123456")
