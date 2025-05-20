from abc import ABC, abstractmethod
from .base_usage import BaseUsage


class BaseMonitor(ABC):
    """Abstrakcyjna klasa bazowa dla wszystkich monitorów."""

    @abstractmethod
    def get_usage(self) -> BaseUsage:
        """Zwraca dane o użyciu danego zasobu jako obiekt."""
        pass
