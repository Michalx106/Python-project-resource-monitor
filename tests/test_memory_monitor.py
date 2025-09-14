def test_memory_monitor_uses_virtual_memory(monkeypatch):
    from monitor import memory_monitor as mm

    class Mem:
        percent = 73.5
        used = 1024
        total = 2048

    monkeypatch.setattr(mm.psutil, "virtual_memory", lambda: Mem)

    m = mm.MemoryMonitor()
    usage = m.get_usage()
    assert usage == mm.MemoryUsage(percent=73.5, used=1024, total=2048)

