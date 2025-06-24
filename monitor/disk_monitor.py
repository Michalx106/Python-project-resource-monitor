import psutil
from .base_monitor import BaseMonitor, BaseUsage
from typing import List


class DiskUsage(BaseUsage):
    """
    Przechowuje informacje o użyciu danego dysku.

    Args:
        percent: Wykorzystanie w procentach.
        used: Ilość użytego miejsca (bajty).
        total: Całkowita pojemność (bajty).
        mount: Punkt montowania dysku.
    """
    def __init__(self, percent: float, used: float, total: float, mount: str):
        """
        Inicjalizuje obiekt DiskUsage.
        """
        self.percent = percent
        self.used = used
        self.total = total
        self.mount = mount


class DiskMonitor(BaseMonitor):
    """
    Monitor dysku.
    """
    def get_usage(self) -> List[DiskUsage]:
        """
        Zwraca listę obiektów DiskUsage dla wszystkich zamontowanych dysków.
        """
        usages = []
        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                usages.append(DiskUsage(
                    percent=usage.percent,
                    used=usage.used,
                    total=usage.total,
                    mount=part.mountpoint
                ))
            except PermissionError:
                continue
        return usages

    @staticmethod
    def get_mounts() -> list[str]:
        """
        Zwraca listę punktów montowania wszystkich dysków,
        z wyjątkiem napędów CD-ROM.
        """
        return [
            p.mountpoint
            for p in psutil.disk_partitions(all=False)
            if 'cdrom' not in p.opts.lower()
        ]
