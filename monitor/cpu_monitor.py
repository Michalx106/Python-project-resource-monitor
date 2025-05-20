import psutil
from .base_monitor import BaseMonitor
from .base_usage import CPUUsage


class CPUMonitor(BaseMonitor):
    """Monitor CPU."""

    def get_usage(self) -> CPUUsage:
        return CPUUsage(percent=psutil.cpu_percent(interval=1))
