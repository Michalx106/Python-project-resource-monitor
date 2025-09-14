from dataclasses import dataclass
from time import time

import psutil

from .base_monitor import BaseMonitor, BaseUsage


@dataclass
class NetworkUsage(BaseUsage):
    """Przechowuje informacje o aktualnym użyciu sieci."""

    upload_kbps: float
    download_kbps: float


class NetworkMonitor(BaseMonitor):
    """
    Monitor sieci.
    """
    def __init__(self):
        """
        Inicjalizuje monitor sieci, ustawiając początkowe wartości.
        """
        self.last_bytes_sent = psutil.net_io_counters().bytes_sent
        self.last_bytes_recv = psutil.net_io_counters().bytes_recv
        self.last_time = time()

    def get_usage(self) -> NetworkUsage:
        """
        Zwraca dane o aktualnym użyciu sieci jako obiekt NetworkUsage.
        """
        current_time = time()
        current_sent = psutil.net_io_counters().bytes_sent
        current_recv = psutil.net_io_counters().bytes_recv

        elapsed = current_time - self.last_time
        if elapsed == 0:
            return NetworkUsage(percent=0.0, upload_kbps=0.0, download_kbps=0.0)

        upload_speed = (
            (current_sent - self.last_bytes_sent) / elapsed / 1024
        )  # KB/s
        download_speed = (
            (current_recv - self.last_bytes_recv) / elapsed / 1024
        )  # KB/s

        self.last_bytes_sent = current_sent
        self.last_bytes_recv = current_recv
        self.last_time = current_time

        stats = psutil.net_if_stats()
        total_speed_mbps = sum(s.speed for s in stats.values() if s.speed > 0)
        if total_speed_mbps <= 0:
            percent = 0.0
        else:
            max_kbps = total_speed_mbps * 128  # Mbps -> KB/s
            current_kbps = upload_speed + download_speed
            percent = (current_kbps / max_kbps) * 100

        return NetworkUsage(
            percent=percent, upload_kbps=upload_speed, download_kbps=download_speed
        )
