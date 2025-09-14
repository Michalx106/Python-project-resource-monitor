from types import SimpleNamespace
from unittest.mock import MagicMock

import config
import main


def dummy_build_gui(self):
    self.ani = main.animation.FuncAnimation(
        None, self.update_plot, interval=self.update_interval_ms
    )


def make_root():
    root = MagicMock()
    root.title = lambda *_: None
    root.geometry = lambda *_: None
    root.protocol = lambda *_: None
    root.destroy = lambda: None
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


def test_custom_config(monkeypatch, tmp_path):
    patch_monitors(monkeypatch)
    monkeypatch.setattr(main.ResourceMonitorApp, "build_gui", dummy_build_gui)
    monkeypatch.setattr(config, "CONFIG_FILE", tmp_path / "config.json")

    def fake_anim(fig, func, interval):
        return SimpleNamespace(event_source=SimpleNamespace(interval=interval))

    monkeypatch.setattr(main.animation, "FuncAnimation", fake_anim)
    app = main.ResourceMonitorApp(make_root(), update_interval_ms=500, history_length=30)
    assert app.update_interval_ms == 500
    assert app.history_length == 30
    assert app.ani.event_source.interval == 500

    app.x_data = list(range(30))
    app.cpu_data = list(range(30))
    app.ram_data = list(range(30))
    app.network_data = {"NET_UP": list(range(30)), "NET_DOWN": list(range(30))}
    app.update_plot(None)
    assert len(app.x_data) == 30


def test_save_and_load_config(monkeypatch, tmp_path):
    patch_monitors(monkeypatch)
    monkeypatch.setattr(main.ResourceMonitorApp, "build_gui", dummy_build_gui)
    monkeypatch.setattr(
        main.animation,
        "FuncAnimation",
        lambda *a, **k: SimpleNamespace(
            event_source=SimpleNamespace(interval=k.get("interval"))
        ),
    )
    monkeypatch.setattr(config, "CONFIG_FILE", tmp_path / "config.json")

    app1 = main.ResourceMonitorApp(make_root())
    app1.update_interval_ms = 1500
    app1.history_length = 20
    app1.cpu_threshold_var.set("75")
    app1.ram_threshold_var.set("65")
    app1.on_close()

    app2 = main.ResourceMonitorApp(make_root())
    assert app2.update_interval_ms == 1500
    assert app2.history_length == 20
    assert app2.cpu_threshold_var.get() == "75"
    assert app2.ram_threshold_var.get() == "65"

