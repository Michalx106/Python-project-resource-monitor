from dataclasses import dataclass

import psutil

from .base_monitor import BaseMonitor, BaseUsage


@dataclass
class CPUUsage(BaseUsage):
    """Przechowuje informacje o aktualnym wykorzystaniu CPU."""


class CPUMonitor(BaseMonitor):
    """
    Monitor CPU.
    """
    def get_usage(self) -> CPUUsage:
        """
        Zwraca dane o aktualnym użyciu CPU.
        """
        return CPUUsage(percent=psutil.cpu_percent(interval=1))
