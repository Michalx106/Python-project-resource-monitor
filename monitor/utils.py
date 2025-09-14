import functools
import logging
from typing import Any, Callable


def safe_call(default: Any = None) -> Callable:
    """
    Dekorator obsługujący wyjątki przy wywołaniach monitorów.
    Jeśli wystąpi błąd, zwraca ``default`` zamiast przerywać działanie programu.

    Args:
        default: Wartość zwracana w razie wystąpienia wyjątku.

    Returns:
        Dekorator opakowujący funkcję tak, by zwracała wartość domyślną
        w przypadku błędu.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            """
            Funkcja opakowująca, która obsługuje wyjątki.

            Args:
                *args: Argumenty pozycyjne przekazywane do funkcji.
                **kwargs: Argumenty nazwane przekazywane do funkcji.

            Returns:
                Wynik funkcji lub ``default`` w przypadku błędu.
            """
            try:
                return func(*args, **kwargs)
            except Exception:
                logging.exception("Błąd podczas wykonywania %s", func.__name__)
                return default

        return wrapper

    return decorator
