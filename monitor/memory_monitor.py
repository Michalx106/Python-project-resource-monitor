import psutil
from .base_monitor import BaseMonitor, BaseUsage

class MemoryUsage(BaseUsage):
    def __init__(self, percent: float, used: float, total: float):
        self.percent = percent
        self.used = used
        self.total = total

class MemoryMonitor(BaseMonitor):
    """Monitor pamięci RAM."""

    def get_usage(self) -> MemoryUsage:
        mem = psutil.virtual_memory()
        return MemoryUsage(percent=mem.percent, used=mem.used, total=mem.total)
