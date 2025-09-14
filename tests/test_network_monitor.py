import types
import pytest


def test_network_monitor_reports_mocked_speeds(monkeypatch):
    from monitor import network_monitor as nm

    counters = [
        types.SimpleNamespace(bytes_sent=1000, bytes_recv=2000),
        types.SimpleNamespace(bytes_sent=1000, bytes_recv=2000),
        types.SimpleNamespace(bytes_sent=1300, bytes_recv=2600),
        types.SimpleNamespace(bytes_sent=1300, bytes_recv=2600),
    ]
    times = [0.0, 1.0]

    monkeypatch.setattr(nm.psutil, "net_io_counters", lambda: counters.pop(0))
    monkeypatch.setattr(nm, "time", lambda: times.pop(0))

    monitor = nm.NetworkMonitor()
    usage = monitor.get_usage()

    assert usage.upload_kbps == pytest.approx(300 / 1024)
    assert usage.download_kbps == pytest.approx(600 / 1024)

