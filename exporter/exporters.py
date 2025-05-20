import csv
from typing import List

class Exporter:
    def export(self, filename: str, x_data: List[int], y_data: List[float]):
        raise NotImplementedError("Exporter must implement export method")

class CPUExporter(Exporter):
    def export(self, filename: str, x_data: List[int], y_data: List[float]):
        self._write_csv(filename, x_data, y_data, "CPU (%)")

    def _write_csv(self, filename, x_data, y_data, label):
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Czas (s)", label])
            for x, y in zip(x_data, y_data):
                writer.writerow([x, y])

class RAMExporter(Exporter):
    def export(self, filename: str, x_data: List[int], y_data: List[float]):
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Czas (s)", "RAM (%)"])
            for x, y in zip(x_data, y_data):
                writer.writerow([x, y])

class DiskExporter(Exporter):
    def __init__(self, mount: str):
        self.mount = mount

    def export(self, filename: str, x_data: List[int], y_data: List[float]):
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Czas (s)", f"Dysk {self.mount} (%)"])
            for x, y in zip(x_data, y_data):
                writer.writerow([x, y])

class GPUExporter(Exporter):
    def __init__(self, name: str):
        self.name = name

    def export(self, filename: str, x_data: List[int], y_data: List[float]):
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Czas (s)", f"GPU {self.name} (%)"])
            for x, y in zip(x_data, y_data):
                writer.writerow([x, y])