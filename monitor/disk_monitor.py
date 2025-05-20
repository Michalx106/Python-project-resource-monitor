import psutil
from .base_monitor import BaseMonitor, BaseUsage
from typing import List

class DiskUsage(BaseUsage):
    def __init__(self, percent: float, used: float, total: float, mount: str):
        self.percent = percent
        self.used = used
        self.total = total
        self.mount = mount

class DiskMonitor(BaseMonitor):
    def get_usage(self) -> List[DiskUsage]:
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
        return [p.mountpoint for p in psutil.disk_partitions(all=False) if 'cdrom' not in p.opts.lower()]
