from dataclasses import dataclass

from .base_monitor import BaseMonitor, BaseUsage

try:
    import GPUtil
    GPU_BACKEND = "gputil"
except ImportError:
    try:
        import wmi
        GPU_BACKEND = "wmi"
    except ImportError:
        GPU_BACKEND = None


@dataclass
class GPUUsage(BaseUsage):
    """Przechowuje informacje o użyciu GPU."""

    name: str


class GPUMonitor(BaseMonitor):
    """
    Monitor GPU.
    Sprawdza dostępność GPU i zwraca informacje o jego użyciu.
    Jeśli nie można znaleźć GPU, zwraca pustą listę.
    """
    def __init__(self):
        """
        Inicjalizuje monitor GPU.
        Sprawdza, czy dostępne są biblioteki do monitorowania GPU.
        """
        self.available = GPU_BACKEND is not None

    def get_usage(self) -> list[GPUUsage]:
        """
        Zwraca listę obiektów GPUUsage dla wszystkich dostępnych GPU.
        Jeśli GPU nie jest dostępne, zwraca pustą listę.
        """
        if not self.available:
            return []

        if GPU_BACKEND == "gputil":
            usages = []
            for gpu in GPUtil.getGPUs():
                usages.append(GPUUsage(name=gpu.name, percent=gpu.load * 100))
            return usages

        elif GPU_BACKEND == "wmi":
            w = wmi.WMI(namespace="root\\cimv2")
            usages = []
            for gpu in (
                w.Win32_PerfFormattedData_GPUPerformanceCounters_GPUEngine()
            ):
                name = getattr(gpu, "Name", "GPU")
                try:
                    load = float(getattr(gpu, "UtilizationPercentage", 0.0))
                except (ValueError, AttributeError):
                    load = 0.0
                usages.append(GPUUsage(name=name, percent=load))
            return usages

        return []
