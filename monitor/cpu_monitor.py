import psutil
from .base_monitor import BaseMonitor


class CPUMonitor(BaseMonitor):
    """Monitor CPU."""

    def get_usage(self) -> float:
        """Zwraca procentowe użycie CPU."""
        return psutil.cpu_percent(interval=1)
