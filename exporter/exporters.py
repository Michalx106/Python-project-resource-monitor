import csv
from typing import List, Dict


class Exporter:
    """
    Abstrakcyjna klasa bazowa dla eksporterów danych metryk.

    Pozwala na eksport danych do pliku (np. CSV) dla różnych rodzajów metryk.
    """
    def export(self, filename: str, x_data: List[int], y_data: List[float]):
        """
        Eksportuje dane do pliku. Funkcja do nadpisania przez klasy potomne.
        """
        raise NotImplementedError("Exporter must implement export method")


class CPUExporter(Exporter):
    """
    Eksporter danych o użyciu CPU do pliku CSV.
    """
    def export(self, filename: str, x_data: List[int], y_data: List[float]):
        """
        Eksportuje dane CPU do pliku CSV.
        """
        self._write_csv(filename, x_data, y_data, "CPU (%)")

    def _write_csv(self, filename, x_data, y_data, label):
        """
        Pomocnicza metoda do zapisu danych do pliku CSV.

        Args:
            filename: Nazwa pliku.
            x_data: Oś czasu.
            y_data: Wartości metryki.
            label: Etykieta kolumny.
        """
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Czas (s)", label])
            for x, y in zip(x_data, y_data):
                writer.writerow([x, y])


class RAMExporter(Exporter):
    """
    Eksporter danych o użyciu RAM do pliku CSV.
    """
    def export(self, filename: str, x_data: List[int], y_data: List[float]):
        """
        Eksportuje dane RAM do pliku CSV.
        """
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Czas (s)", "RAM (%)"])
            for x, y in zip(x_data, y_data):
                writer.writerow([x, y])


class DiskExporter(Exporter):
    """
    Eksporter danych o użyciu dysku do pliku CSV.

    Args:
        mount: Punkt montowania dysku.
    """
    def __init__(self, mount: str):
        self.mount = mount

    def export(self, filename: str, x_data: List[int], y_data: List[float]):
        """
        Eksportuje dane dysku do pliku CSV.
        """
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Czas (s)", f"Dysk {self.mount} (%)"])
            for x, y in zip(x_data, y_data):
                writer.writerow([x, y])


class GPUExporter(Exporter):
    """
    Eksporter danych o użyciu GPU do pliku CSV.

    Args:
        name: Nazwa GPU.
    """
    def __init__(self, name: str):
        self.name = name

    def export(self, filename: str, x_data: List[int], y_data: List[float]):
        """
        Eksportuje dane GPU do pliku CSV.
        """
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Czas (s)", f"GPU {self.name} (%)"])
            for x, y in zip(x_data, y_data):
                writer.writerow([x, y])


class NetworkExporter(Exporter):
    """
    Eksporter danych o przesyłanych danych sieciowych do pliku CSV.

    Args:
        label: Nazwa metryki (NET_UP/NET_DOWN).
    """
    def __init__(self, label: str):
        self.label = label  # NET_UP or NET_DOWN

    def export(self, filename: str, x_data: List[int], y_data: List[float]):
        """
        Eksportuje dane sieci do pliku CSV.
        """
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Czas (s)", f"{self.label} (KB/s)"])
            for x, y in zip(x_data, y_data):
                writer.writerow([x, y])


class MultiMetricExporter(Exporter):
    """
    Eksporter wielu metryk jednocześnie do jednego pliku CSV.
    """
    def export(
        self,
        filename: str,
        x_data: List[int],
        metrics: Dict[str, List[float]]
    ):
        """
        Eksportuje dane wielu metryk do pliku CSV.

        Args:
            filename: Nazwa pliku.
            x_data: Oś czasu.
            metrics: Słownik metryk (nazwa: lista wartości).
        """
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            header = ["Czas (s)"] + list(metrics.keys())
            writer.writerow(header)

            for i in range(len(x_data)):
                row = [x_data[i]] + [
                    metrics[key][i] if i < len(metrics[key])
                    else ''
                    for key in metrics
                ]
                writer.writerow(row)
