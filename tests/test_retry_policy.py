"""Политика повторов."""

from __future__ import annotations

from yookassax import BadRequest, NotFound, RateLimited, ResponseProcessing, ServerError
from yookassax.retry import RetryPolicy, should_retry


def test_transient_errors_are_retried():
    assert should_retry(ResponseProcessing()) is True
    assert should_retry(RateLimited()) is True
    assert should_retry(ServerError()) is True


def test_client_errors_are_not_retried():
    """Второй такой же запрос даст такой же ответ."""
    assert should_retry(BadRequest()) is False
    assert should_retry(NotFound()) is False


def test_backoff_grows_exponentially():
    policy = RetryPolicy(attempts=5, backoff=1.0, max_backoff=100.0)

    first = policy.delay(1)
    second = policy.delay(2)
    third = policy.delay(3)

    # Дрожание держит паузу в пределах половины базового значения,
    # поэтому сравниваем диапазоны, а не точные числа.
    assert 0.5 <= first <= 1.0
    assert 1.0 <= second <= 2.0
    assert 2.0 <= third <= 4.0


def test_backoff_is_capped():
    policy = RetryPolicy(attempts=10, backoff=1.0, max_backoff=5.0)

    assert policy.delay(10) <= 5.0


def test_jitter_spreads_concurrent_clients():
    """Иначе пачка клиентов пойдёт на второй круг одновременно."""
    policy = RetryPolicy(backoff=1.0)

    delays = {policy.delay(1) for _ in range(20)}

    assert len(delays) > 1
