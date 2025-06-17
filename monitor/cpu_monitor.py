import psutil
from .base_monitor import BaseMonitor, BaseUsage


class CPUUsage(BaseUsage):
    def __init__(self, percent: float):
        self.percent = percent


class CPUMonitor(BaseMonitor):
    """Monitor CPU."""

    def get_usage(self) -> CPUUsage:
        return CPUUsage(percent=psutil.cpu_percent(interval=1))
