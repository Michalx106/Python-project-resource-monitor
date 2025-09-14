import importlib


def test_gpu_monitor_degrades_when_unavailable(monkeypatch):
    import monitor.gpu_monitor as gm

    # Force no backend
    old = gm.GPU_BACKEND
    gm.GPU_BACKEND = None
    try:
        m = gm.GPUMonitor()
        assert m.get_usage() == []
    finally:
        gm.GPU_BACKEND = old


def test_gpu_monitor_gputil_backend(monkeypatch):
    import monitor.gpu_monitor as gm

    class FakeGPU:
        def __init__(self, name, load):
            self.name = name
            self.load = load  # 0..1

    class FakeGPUtil:
        @staticmethod
        def getGPUs():
            return [FakeGPU("FakeRTX", 0.5)]

    # Pretend GPUtil backend is available
    monkeypatch.setattr(gm, "GPU_BACKEND", "gputil")
    monkeypatch.setattr(gm, "GPUtil", FakeGPUtil)

    m = gm.GPUMonitor()
    usages = m.get_usage()
    assert usages == [gm.GPUUsage(name="FakeRTX", percent=50.0)]

