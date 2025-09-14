import csv


def test_cpu_exporter_writes_csv(tmp_path):
    from exporter.exporters import CPUExporter
    x = [0, 1, 2]
    y = [10.0, 20.0, 30.0]
    out = tmp_path / "cpu.csv"
    CPUExporter().export(str(out), x, y)

    with out.open() as f:
        rows = list(csv.reader(f))
    assert rows[0] == ["Czas (s)", "CPU (%)"]
    assert rows[1] == ["0", "10.0"]
    assert rows[-1] == ["2", "30.0"]


def test_multi_metric_exporter_handles_ragged_data(tmp_path):
    from exporter.exporters import MultiMetricExporter
    x = [0, 1, 2]
    metrics = {"CPU": [1.0, 2.0], "RAM": [50.0]}
    out = tmp_path / "all.csv"
    MultiMetricExporter().export(str(out), x, metrics)

    with out.open() as f:
        rows = list(csv.reader(f))

    assert rows[0] == ["Czas (s)", "CPU", "RAM"]
    # Third row has missing RAM value -> empty string
    assert rows[2] == ["1", "2.0", ""]

