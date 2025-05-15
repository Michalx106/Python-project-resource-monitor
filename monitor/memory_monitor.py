import psutil
from .base_monitor import BaseMonitor


class MemoryMonitor(BaseMonitor):
    """Monitor pamięci RAM."""

    def get_usage(self) -> float:
        """Zwraca procentowe użycie pamięci RAM."""
        return psutil.virtual_memory().percent
