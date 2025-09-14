import psutil
from types import SimpleNamespace

from monitor.process_monitor import ProcessMonitor


def test_get_top_processes_cpu(monkeypatch):
    processes = [
        SimpleNamespace(info={"pid": 1, "name": "a", "cpu_percent": 10.0, "memory_percent": 5.0}),
        SimpleNamespace(info={"pid": 2, "name": "b", "cpu_percent": 50.0, "memory_percent": 15.0}),
        SimpleNamespace(info={"pid": 3, "name": "c", "cpu_percent": 20.0, "memory_percent": 25.0}),
    ]
    monkeypatch.setattr(psutil, "process_iter", lambda attrs: iter(processes))
    monitor = ProcessMonitor()
    result = monitor.get_top_processes(top_n=2, sort_by="cpu")
    assert [p.pid for p in result] == [2, 3]


def test_get_top_processes_memory(monkeypatch):
    processes = [
        SimpleNamespace(info={"pid": 1, "name": "a", "cpu_percent": 10.0, "memory_percent": 5.0}),
        SimpleNamespace(info={"pid": 2, "name": "b", "cpu_percent": 50.0, "memory_percent": 15.0}),
        SimpleNamespace(info={"pid": 3, "name": "c", "cpu_percent": 20.0, "memory_percent": 25.0}),
    ]
    monkeypatch.setattr(psutil, "process_iter", lambda attrs: iter(processes))
    monitor = ProcessMonitor()
    result = monitor.get_top_processes(top_n=2, sort_by="memory")
    assert [p.pid for p in result] == [3, 2]


def test_get_top_processes_ignores_errors(monkeypatch):
    class BadProc:
        def __init__(self, exc):
            self._exc = exc

        @property
        def info(self):
            raise self._exc

    good = SimpleNamespace(info={"pid": 1, "name": "a", "cpu_percent": 10.0, "memory_percent": 5.0})
    bad = BadProc(psutil.NoSuchProcess(2))
    monkeypatch.setattr(psutil, "process_iter", lambda attrs: iter([bad, good]))
    monitor = ProcessMonitor()
    result = monitor.get_top_processes(top_n=5)
    assert [p.pid for p in result] == [1]

