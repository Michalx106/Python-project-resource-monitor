from dataclasses import dataclass

import psutil

from .base_monitor import BaseMonitor, BaseUsage


@dataclass
class MemoryUsage(BaseUsage):
    """Przechowuje informacje o aktualnym wykorzystaniu pamięci RAM."""

    used: float
    total: float


class MemoryMonitor(BaseMonitor):
    """
    Monitor pamięci RAM.
    """
    def get_usage(self) -> MemoryUsage:
        """
        Zwraca dane o użyciu pamięci RAM.
        """
        mem = psutil.virtual_memory()
        return MemoryUsage(percent=mem.percent, used=mem.used, total=mem.total)
