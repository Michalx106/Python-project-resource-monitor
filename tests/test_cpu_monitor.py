def test_cpu_monitor_reports_mocked_value(monkeypatch):
    from monitor import cpu_monitor as cm

    # Mock psutil.cpu_percent used inside the module
    monkeypatch.setattr(cm.psutil, "cpu_percent", lambda interval=1: 42.0)

    m = cm.CPUMonitor()
    usage = m.get_usage()
    assert usage == cm.CPUUsage(percent=42.0)

