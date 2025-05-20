from abc import ABC


class BaseUsage(ABC):
    """Abstrakcyjna klasa danych o użyciu zasobu."""
    percent: float


class CPUUsage(BaseUsage):
    def __init__(self, percent: float):
        self.percent = percent


class MemoryUsage(BaseUsage):
    def __init__(self, percent: float, used: float, total: float):
        self.percent = percent
        self.used = used
        self.total = total


class DiskUsage(BaseUsage):
    def __init__(self, percent: float, used: float, total: float, mount: str):
        self.percent = percent
        self.used = used
        self.total = total
        self.mount = mount
