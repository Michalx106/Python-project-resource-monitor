import psutil
from time import time
from .base_monitor import BaseMonitor, BaseUsage


class NetworkUsage(BaseUsage):
    """
    Przechowuje informacje o aktualnym użyciu sieci.
    Args:
        upload_kbps: Prędkość wysyłania danych w KB/s.
        download_kbps: Prędkość pobierania danych w KB/s.
    """
    def __init__(self, upload_kbps: float, download_kbps: float):
        """
        Inicjalizuje obiekt NetworkUsage.
        """
        self.upload_kbps = upload_kbps
        self.download_kbps = download_kbps

    @property
    def percent(self):
        """
        Zwraca procentowe wykorzystanie sieci.
        """
        return 0


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
            return NetworkUsage(0.0, 0.0)

        upload_speed = (
            (current_sent - self.last_bytes_sent) / elapsed / 1024
        )  # KB/s
        download_speed = (
            (current_recv - self.last_bytes_recv) / elapsed / 1024
        )  # KB/s

        self.last_bytes_sent = current_sent
        self.last_bytes_recv = current_recv
        self.last_time = current_time

        return NetworkUsage(upload_speed, download_speed)
