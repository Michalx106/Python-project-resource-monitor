from abc import ABC, abstractmethod


class BaseMonitor(ABC):
    """Abstrakcyjna klasa bazowa dla monitorów zasobów."""

    @abstractmethod
    def get_usage(self) -> float:
        """Zwraca poziom użycia danego zasobu."""
        pass
