from types import SimpleNamespace
from unittest.mock import MagicMock

import config
import main


def dummy_build_gui(self) -> None:
    """Minimal GUI setup for tests."""
    self.interval_var = main.tk.StringVar(value=str(self.update_interval_ms))
    self.history_var = main.tk.StringVar(value=str(self.history_length))
    self.ani = main.animation.FuncAnimation(
        None, self.update_plot, interval=self.update_interval_ms
    )


def make_root():
    root = MagicMock()
    root.title = lambda *_: None
    root.geometry = lambda *_: None
    root.protocol = lambda *_: None
    root.destroy = MagicMock()
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

    class DummyVar:
        def __init__(self, master=None, value=""):
            self._value = value

        def get(self):
            return self._value

        def set(self, value):
            self._value = value

    monkeypatch.setattr(main.tk, "StringVar", DummyVar)


def test_negative_values_are_rejected(monkeypatch):
    patch_monitors(monkeypatch)
    monkeypatch.setattr(main.ResourceMonitorApp, "build_gui", dummy_build_gui)

    def fake_anim(fig, func, interval):
        return SimpleNamespace(event_source=SimpleNamespace(interval=interval))

    monkeypatch.setattr(main.animation, "FuncAnimation", fake_anim)

    app = main.ResourceMonitorApp(make_root())
    assert app.update_interval_ms == config.DEFAULT_CONFIG["update_interval_ms"]
    assert app.history_length == config.DEFAULT_CONFIG["history_length"]

    app.interval_var.set("-100")
    app.history_var.set("-5")
    app.apply_settings()

    assert app.update_interval_ms == config.DEFAULT_CONFIG["update_interval_ms"]
    assert app.history_length == config.DEFAULT_CONFIG["history_length"]
    assert app.ani.event_source.interval == config.DEFAULT_CONFIG["update_interval_ms"]

