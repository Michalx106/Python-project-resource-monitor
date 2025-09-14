import psutil
from dataclasses import dataclass
from typing import List
from .base_monitor import BaseMonitor, BaseUsage


@dataclass
class ProcessUsage(BaseUsage):
    """Reprezentuje informacje o użyciu CPU i RAM przez proces."""

    pid: int
    name: str
    percent: float
    memory: float


class ProcessMonitor(BaseMonitor):
    """Monitor procesów zwracający listę najbardziej obciążających procesów."""

    def __init__(self, top_n: int = 5):
        self.top_n = top_n

    def get_usage(self, sort_by: str = "cpu") -> List[ProcessUsage]:
        """Zwraca listę procesów posortowaną według użycia CPU lub RAM."""
        processes: List[ProcessUsage] = []
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                cpu = proc.cpu_percent(interval=None)
                mem = proc.memory_percent()
                processes.append(
                    ProcessUsage(proc.pid, proc.info.get("name", ""), cpu, mem)
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        key = (lambda p: p.percent) if sort_by == "cpu" else (lambda p: p.memory)
        processes.sort(key=key, reverse=True)
        return processes[: self.top_n]
