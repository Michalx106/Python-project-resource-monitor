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


class GPUUsage(BaseUsage):
    def __init__(self, name: str, percent: float):
        self.name = name
        self.percent = percent


class GPUMonitor(BaseMonitor):
    def __init__(self):
        self.available = GPU_BACKEND is not None

    def get_usage(self) -> list[GPUUsage]:
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
            for gpu in w.Win32_PerfFormattedData_GPUPerformanceCounters_GPUEngine():
                name = getattr(gpu, "Name", "GPU")
                try:
                    load = float(getattr(gpu, "UtilizationPercentage", 0.0))
                except (ValueError, AttributeError):
                    load = 0.0
                usages.append(GPUUsage(name=name, percent=load))
            return usages

        return []
