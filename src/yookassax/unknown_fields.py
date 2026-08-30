"""Предупреждение о полях, которых нет в моделях.

ЮKassa добавляет поля в ответы молча. Разбор от этого не падает, лишнее
остаётся в raw, но узнать об этом иначе нельзя: приложение годами читает
ответ, в котором появилось что-то новое, и не догадывается.

Отсюда предупреждение. Оно ничего не ломает и ничего не требует: значение
доступно через extra(), а обновление библиотеки просто перенесёт поле в
модель.

Предупреждение выдаётся один раз на пару "модель плюс поле" за время жизни
процесса. Иначе страница из ста платежей дала бы сто одинаковых строк, а лог,
в котором одно и то же повторяется сотнями, читать перестают.
"""

from __future__ import annotations

import sys
import warnings
from collections.abc import Iterable
from pathlib import Path
from types import FrameType

__all__ = [
    "UnknownFieldWarning",
    "forget_unknown_fields",
    "warn_unknown_fields",
]


class UnknownFieldWarning(UserWarning):
    """API вернуло поле, которого нет в модели.

    Обычно означает, что ЮKassa расширила ответ, а библиотека ещё не
    обновилась. Отключается штатным фильтром:

        import warnings
        from yookassax import UnknownFieldWarning

        warnings.filterwarnings("ignore", category=UnknownFieldWarning)
    """


# Пары (модель, поле), о которых уже предупредили.
_reported: set[tuple[str, str]] = set()

# Каталог библиотеки: по нему отличаем свои кадры стека от чужих.
_PACKAGE_ROOT = str(Path(__file__).resolve().parent)


def _caller_stacklevel() -> int:
    """Найти кадр, на котором библиотека кончается и начинается приложение.

    Без этого предупреждение показывает строку внутри yookassax, а полезен
    вызов из кода приложения: именно там видно, какой запрос дал новое поле.
    Глубина вложенности разная (модель верхнего уровня, вложенная модель,
    элемент списка), поэтому фиксированное число здесь не годится.
    """
    # Кадр 1 это сама warn_unknown_fields, ей соответствует stacklevel=1.
    frame: FrameType | None = sys._getframe(1)
    level = 1
    while frame is not None:
        if not frame.f_code.co_filename.startswith(_PACKAGE_ROOT):
            return level
        frame = frame.f_back
        level += 1
    # Весь стек внутри библиотеки: пусть покажет её саму, это лучше падения.
    return 2


def warn_unknown_fields(model: str, names: Iterable[str]) -> None:
    """Предупредить о полях, которых нет в модели.

    Повторы отсеиваются: о каждой паре "модель плюс поле" говорим однажды.
    Гонка двух потоков в худшем случае даст второе такое же предупреждение, и
    это дешевле блокировки на каждом разборе ответа.
    """
    fresh = sorted(name for name in names if (model, name) not in _reported)
    if not fresh:
        return

    _reported.update((model, name) for name in fresh)
    listed = ", ".join(fresh)
    warnings.warn(
        f"{model}: в ответе API есть поля, которых нет в модели: {listed}. "
        f"Значения доступны через extra(), но, возможно, стоит обновить "
        f"yookassax.",
        UnknownFieldWarning,
        stacklevel=_caller_stacklevel(),
    )


def forget_unknown_fields() -> None:
    """Забыть, о чём уже предупреждали.

    Нужно тестам: без сброса второй тест не увидит предупреждения, о котором
    сказал первый.
    """
    _reported.clear()
