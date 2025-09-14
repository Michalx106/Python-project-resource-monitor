from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class BaseUsage:
    """Dane o użyciu zasobu."""

    percent: float


class BaseMonitor(ABC):
    """
    Abstrakcyjna klasa bazowa dla wszystkich monitorów.
    """

    @abstractmethod
    def get_usage(self) -> BaseUsage:
        """
        Zwraca dane o użyciu danego zasobu jako obiekt lub listę obiektów
        ``BaseUsage``.
        """
        pass
