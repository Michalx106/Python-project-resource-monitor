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


def test_load_config_defaults(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "CONFIG_FILE", tmp_path / "config.json")
    assert config.load_config() == config.DEFAULT_CONFIG


def test_default_config_when_missing(monkeypatch, tmp_path):
    patch_monitors(monkeypatch)
    monkeypatch.setattr(main.ResourceMonitorApp, "build_gui", dummy_build_gui)
    monkeypatch.setattr(config, "CONFIG_FILE", tmp_path / "config.json")

    def fake_anim(fig, func, interval):
        return SimpleNamespace(event_source=SimpleNamespace(interval=interval))

    monkeypatch.setattr(main.animation, "FuncAnimation", fake_anim)
    app = main.ResourceMonitorApp(make_root(), update_interval_ms=500, history_length=30)
    assert app.update_interval_ms == config.DEFAULT_CONFIG["update_interval_ms"]
    assert app.history_length == config.DEFAULT_CONFIG["history_length"]
    assert app.ani.event_source.interval == config.DEFAULT_CONFIG["update_interval_ms"]

    hl = config.DEFAULT_CONFIG["history_length"]
    app.x_data = list(range(hl))
    app.cpu_data = list(range(hl))
    app.ram_data = list(range(hl))
    app.network_data = {"NET_UP": list(range(hl)), "NET_DOWN": list(range(hl))}
    app.update_plot(None)
    assert len(app.x_data) == hl


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

    safe_call_mock = MagicMock()

    def decorator(func):
        safe_call_mock.decorated_func = func

        def wrapper(*args, **kwargs):
            safe_call_mock.wrapper_called = True
            return func(*args, **kwargs)

        return wrapper

    safe_call_mock.return_value = decorator
    monkeypatch.setattr(main, "safe_call", safe_call_mock)

    root1 = make_root()
    app1 = main.ResourceMonitorApp(root1)
    assert app1.update_interval_ms == config.DEFAULT_CONFIG["update_interval_ms"]
    assert app1.history_length == config.DEFAULT_CONFIG["history_length"]
    assert app1.cpu_threshold_var.get() == str(config.DEFAULT_CONFIG["cpu_threshold"])
    assert app1.ram_threshold_var.get() == str(config.DEFAULT_CONFIG["ram_threshold"])
    app1.update_interval_ms = 1500
    app1.history_length = 20
    app1.cpu_threshold_var.set("75")
    app1.ram_threshold_var.set("65")
    app1.on_close()

    safe_call_mock.assert_called_once_with()
    assert safe_call_mock.decorated_func is root1.destroy
    assert safe_call_mock.wrapper_called
    assert root1.destroy.called

    app2 = main.ResourceMonitorApp(make_root())
    assert app2.update_interval_ms == 1500
    assert app2.history_length == 20
    assert app2.cpu_threshold_var.get() == "75"
    assert app2.ram_threshold_var.get() == "65"

