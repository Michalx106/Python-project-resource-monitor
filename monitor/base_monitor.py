from abc import ABC, abstractmethod

class BaseUsage(ABC):
    """Abstrakcyjna klasa danych o użyciu zasobu."""
    percent: float

class BaseMonitor(ABC):
    """Abstrakcyjna klasa bazowa dla wszystkich monitorów."""

    @abstractmethod
    def get_usage(self) -> BaseUsage:
        """Zwraca dane o użyciu danego zasobu jako obiekt."""
        pass
