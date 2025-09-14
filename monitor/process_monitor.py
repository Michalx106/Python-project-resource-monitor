from dataclasses import dataclass
from typing import List

import psutil


@dataclass
class ProcessUsage:
    """Informacje o pojedynczym procesie."""

    pid: int
    name: str
    cpu_percent: float
    memory_percent: float


class ProcessMonitor:
    """Monitor zwracający listę procesów o najwyższym użyciu zasobów."""

    def get_top_processes(
        self, top_n: int = 5, sort_by: str = "cpu"
    ) -> List[ProcessUsage]:
        """Zwraca listę procesów posortowaną wg zużycia CPU lub pamięci RAM.

        Args:
            top_n: maksymalna liczba procesów do zwrócenia.
            sort_by: kryterium sortowania ("cpu" lub "memory").
        """
        processes: List[ProcessUsage] = []
        for proc in psutil.process_iter(
            ["pid", "name", "cpu_percent", "memory_percent"]
        ):
            try:
                info = proc.info
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
            processes.append(
                ProcessUsage(
                    pid=info.get("pid", 0),
                    name=info.get("name", ""),
                    cpu_percent=info.get("cpu_percent", 0.0),
                    memory_percent=info.get("memory_percent", 0.0),
                )
            )

        key = (
            (lambda p: p.memory_percent)
            if sort_by == "memory"
            else (lambda p: p.cpu_percent)
        )
        processes.sort(key=key, reverse=True)
        return processes[:top_n]
