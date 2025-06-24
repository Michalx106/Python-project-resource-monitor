import functools
from typing import Callable


def safe_call(func: Callable) -> Callable:
    """
    Dekorator obsługujący wyjątki przy wywołaniach monitorów.
    Jeśli wystąpi błąd, zwraca -1.0 zamiast przerywać działanie programu.
    Args:
        func: Funkcja do dekorowania.
    Returns:
        Funkcja dekorowana, która obsługuje wyjątki.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        """
        Funkcja opakowująca, która obsługuje wyjątki.
        Args:
            *args: Argumenty pozycyjne przekazywane do funkcji.
            **kwargs: Argumenty nazwane przekazywane do funkcji.
        Returns:
            Wynik funkcji lub -1.0 w przypadku błędu.
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Błąd podczas wykonywania {func.__name__}: {e}")
            return -1.0
    return wrapper
