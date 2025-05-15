import functools
from typing import Callable

def safe_call(func: Callable) -> Callable:
    """Dekorator obsługujący wyjątki przy wywołaniach monitorów."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Błąd podczas wykonywania {func.__name__}: {e}")
            return -1.0
    return wrapper
