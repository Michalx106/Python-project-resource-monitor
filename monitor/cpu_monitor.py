import psutil
from .base_monitor import BaseMonitor, BaseUsage


class CPUUsage(BaseUsage):
    """
    Przechowuje informacje o aktualnym wykorzystaniu CPU.
    """
    def __init__(self, percent: float):
        self.percent = percent


class CPUMonitor(BaseMonitor):
    """
    Monitor CPU.
    """
    def get_usage(self) -> CPUUsage:
        """
        Zwraca dane o aktualnym użyciu CPU.
        """
        return CPUUsage(percent=psutil.cpu_percent(interval=1))
