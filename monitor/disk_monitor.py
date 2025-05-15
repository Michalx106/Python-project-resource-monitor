import psutil
from .base_monitor import BaseMonitor

class DiskMonitor(BaseMonitor):
    """Monitor wielu dysków."""

    def __init__(self):
        self.partitions = self._get_partitions()

    def _get_partitions(self) -> list[str]:
        """Zwraca listę punktów montowania (Windows: 'C:\\', Linux: '/')."""
        return [p.mountpoint for p in psutil.disk_partitions(all=False) if 'cdrom' not in p.opts.lower()]
    
    def get_usage(self) -> float:
        raise NotImplementedError("Użyj get_all_usages() zamiast get_usage() dla wielu dysków.")

    def get_all_usages(self) -> dict[str, float]:
        """Zwraca zajętość procentową dla każdego dysku."""
        usage = {}
        for mount in self.partitions:
            try:
                percent = psutil.disk_usage(mount).percent
                usage[mount] = percent
            except PermissionError:
                usage[mount] = -1.0
        return usage
