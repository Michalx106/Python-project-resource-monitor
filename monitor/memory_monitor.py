import psutil
from .base_monitor import BaseMonitor
from .base_usage import MemoryUsage


class MemoryMonitor(BaseMonitor):
    """Monitor pamięci RAM."""

    def get_usage(self) -> MemoryUsage:
        mem = psutil.virtual_memory()
        return MemoryUsage(percent=mem.percent, used=mem.used, total=mem.total)
