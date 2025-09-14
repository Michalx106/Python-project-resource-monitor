import types


def test_process_monitor_returns_top_processes(monkeypatch):
    from monitor import process_monitor as pm

    class MockProcess:
        def __init__(self, pid, name, cpu, mem):
            self.pid = pid
            self.info = {"pid": pid, "name": name}
            self._cpu = cpu
            self._mem = mem

        def cpu_percent(self, interval=None):
            return self._cpu

        def memory_percent(self):
            return self._mem

    processes = [
        MockProcess(1, "a", 10.0, 5.0),
        MockProcess(2, "b", 50.0, 3.0),
        MockProcess(3, "c", 20.0, 7.0),
    ]

    monkeypatch.setattr(pm.psutil, "process_iter", lambda attrs: processes)

    m = pm.ProcessMonitor(top_n=2)
    top_cpu = m.get_usage()
    assert [p.pid for p in top_cpu] == [2, 3]

    top_mem = m.get_usage(sort_by="memory")
    assert [p.pid for p in top_mem] == [3, 1]
