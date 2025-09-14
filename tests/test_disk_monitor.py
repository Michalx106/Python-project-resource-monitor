from collections import namedtuple


def test_disk_monitor_collects_per_mount(monkeypatch):
    from monitor import disk_monitor as dm

    Part = namedtuple("Part", ["mountpoint", "opts"])

    parts = [
        Part("/", "rw"),
        Part("/data", "rw"),
    ]

    class DU:
        def __init__(self, percent, used, total):
            self.percent = percent
            self.used = used
            self.total = total

    def fake_disk_usage(mp):
        if mp == "/":
            return DU(11.0, 100, 1000)
        return DU(22.0, 200, 2000)

    monkeypatch.setattr(dm.psutil, "disk_partitions", lambda: parts)
    monkeypatch.setattr(dm.psutil, "disk_usage", fake_disk_usage)

    m = dm.DiskMonitor()
    usages = m.get_usage()
    mounts = {u.mount for u in usages}
    assert mounts == {"/", "/data"}
    percents = {u.mount: u.percent for u in usages}
    assert percents["/"] == 11.0
    assert percents["/data"] == 22.0


def test_get_mounts_filters_cdrom(monkeypatch):
    from monitor import disk_monitor as dm
    Part = namedtuple("Part", ["mountpoint", "opts"])
    parts = [Part("/", "rw"), Part("/media/cdrom", "ro,cdrom")]
    monkeypatch.setattr(dm.psutil, "disk_partitions", lambda **kwargs: parts)
    mounts = dm.DiskMonitor.get_mounts()
    assert "/" in mounts
    assert not any("cdrom" in m for m in mounts)

