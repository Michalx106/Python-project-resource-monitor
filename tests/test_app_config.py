from types import SimpleNamespace
from unittest.mock import MagicMock

import main


def dummy_build_gui(self):
    self.ani = main.animation.FuncAnimation(None, self.update_plot, interval=self.update_interval_ms)


def make_root():
    root = MagicMock()
    root.title = lambda *_: None
    root.geometry = lambda *_: None
    return root


def patch_monitors(monkeypatch):
    monkeypatch.setattr(
        main,
        "CPUMonitor",
        lambda: MagicMock(get_usage=lambda: SimpleNamespace(percent=0)),
    )
    monkeypatch.setattr(
        main,
        "MemoryMonitor",
        lambda: MagicMock(get_usage=lambda: SimpleNamespace(percent=0)),
    )
    monkeypatch.setattr(main, "DiskMonitor", lambda: MagicMock(get_usage=lambda: []))
    monkeypatch.setattr(main, "GPUMonitor", lambda: MagicMock(get_usage=lambda: []))
    monkeypatch.setattr(
        main,
        "NetworkMonitor",
        lambda: MagicMock(
            get_usage=lambda: SimpleNamespace(upload_kbps=0, download_kbps=0)
        ),
    )


def test_custom_config(monkeypatch):
    patch_monitors(monkeypatch)
    monkeypatch.setattr(main.ResourceMonitorApp, "build_gui", dummy_build_gui)
    captured = {}

    def fake_anim(fig, func, interval):
        captured["interval"] = interval
        class Dummy:
            def __init__(self, interval):
                self.event_source = SimpleNamespace(interval=interval)
        return Dummy(interval)

    monkeypatch.setattr(main.animation, "FuncAnimation", fake_anim)
    app = main.ResourceMonitorApp(make_root(), update_interval_ms=500, history_length=30)
    assert app.update_interval_ms == 500
    assert app.history_length == 30
    assert captured["interval"] == 500

    app.x_data = list(range(30))
    app.cpu_data = list(range(30))
    app.ram_data = list(range(30))
    app.network_data = {"NET_UP": list(range(30)), "NET_DOWN": list(range(30))}
    app.update_plot(None)
    assert len(app.x_data) == 30
