import math
from typing import Dict, List
import tkinter as tk
from tkinter import messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation

from monitor.cpu_monitor import CPUMonitor
from monitor.memory_monitor import MemoryMonitor
from monitor.disk_monitor import DiskMonitor
from monitor.gpu_monitor import GPUMonitor
from monitor.network_monitor import NetworkMonitor
from monitor.process_monitor import ProcessMonitor
from monitor.utils import safe_call

from exporter.exporters import (
    Exporter,
    CPUExporter, RAMExporter, DiskExporter, GPUExporter,
    NetworkExporter, MultiMetricExporter, JSONExporter
)

from config import load_config, save_config


class ResourceMonitorApp:
    """
    Główna klasa aplikacji monitorującej zasoby systemowe z interfejsem GUI.

    Inicjalizuje i obsługuje monitory CPU, RAM, dysków, GPU oraz sieci.
    Wyświetla dane w postaci wykresów oraz umożliwia eksport wybranych
    metryk do pliku CSV.
    """
    def __init__(
        self,
        root,
        update_interval_ms: int = 1000,
        history_length: int = 60,
    ):
        """
        Inicjalizuje aplikację, monitory oraz bufory danych, buduje GUI.

        Args:
            root: Obiekt głównego okna tkinter.
            update_interval_ms: Czas odświeżania wykresów w milisekundach.
            history_length: Liczba ostatnich próbek przechowywanych w buforze.
        """
        self.root = root
        self.root.title("Monitor zasobów systemowych")
        self.root.geometry("1200x800")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        config = load_config()
        self.update_interval_ms = config.get("update_interval_ms", update_interval_ms)
        self.history_length = config.get("history_length", history_length)
        self.cpu_threshold_var = tk.StringVar(
            master=self.root, value=str(config.get("cpu_threshold", 90))
        )
        self.ram_threshold_var = tk.StringVar(
            master=self.root, value=str(config.get("ram_threshold", 90))
        )

        # Inicjalizacja monitorów
        self.cpu = CPUMonitor()
        self.ram = MemoryMonitor()
        self.gpu = GPUMonitor()
        self.disk = DiskMonitor()
        self.network = NetworkMonitor()
        self.process_monitor = ProcessMonitor()

        # Bufory danych
        self.frame_count = 0
        self.x_data: List[int] = []
        self.cpu_data: List[float] = []
        self.ram_data: List[float] = []
        self.disk_data: Dict[str, List[float]] = {
            d.mount: []
            for d in self.disk.get_usage()
        }
        self.gpu_data: Dict[str, List[float]] = {}
        self.network_data: Dict[str, List[float]] = {
            "NET_UP": [], "NET_DOWN": []
        }
        self.process_tree = None

        self.disk_mounts = list(self.disk_data.keys())
        self.fig = None
        self.ax = []
        self.lines = {}
        self.fills = {}

        self.build_gui()

    def build_gui(self):
        """
        Buduje i rozmieszcza elementy graficzne interfejsu użytkownika.
        Inicjalizuje wykresy i kontrolki wyboru oraz eksportu metryk.
        """
        # Lista rozwijana + przycisk eksportu
        frame = ttk.Frame(self.root)
        frame.pack(pady=10)

        self.selected_metric = tk.StringVar()
        options = (
            ["CPU", "RAM"]
            + [f"DISK_{m}" for m in self.disk_mounts]
            + [f"GPU_{g.name}" for g in self.gpu.get_usage()]
            + ["NET_UP", "NET_DOWN", "WSZYSTKO"]
        )

        self.metric_menu = ttk.Combobox(
            frame,
            textvariable=self.selected_metric,
            values=options
        )
        self.metric_menu.set("CPU")
        self.metric_menu.pack(side=tk.LEFT, padx=5)

        self.export_format_var = tk.StringVar(value="CSV")
        export_format_menu = ttk.Combobox(
            frame,
            textvariable=self.export_format_var,
            values=["CSV", "JSON"],
            width=6
        )
        export_format_menu.pack(side=tk.LEFT, padx=5)

        export_btn = ttk.Button(
            frame,
            text="Eksportuj",
            command=self.export_selected
        )
        export_btn.pack(side=tk.LEFT, padx=5)

        settings = ttk.Frame(self.root)
        settings.pack(pady=5)

        ttk.Label(settings, text="Interwał (ms)").pack(side=tk.LEFT, padx=5)
        self.interval_var = tk.StringVar(value=str(self.update_interval_ms))
        ttk.Entry(settings, textvariable=self.interval_var, width=7).pack(side=tk.LEFT)

        ttk.Label(settings, text="Długość historii").pack(side=tk.LEFT, padx=5)
        self.history_var = tk.StringVar(value=str(self.history_length))
        ttk.Entry(settings, textvariable=self.history_var, width=7).pack(side=tk.LEFT)

        apply_btn = ttk.Button(settings, text="Zastosuj", command=self.apply_settings)
        apply_btn.pack(side=tk.LEFT, padx=5)

        process_frame = ttk.Frame(self.root)
        process_frame.pack(pady=5, fill=tk.BOTH)

        self.process_tree = ttk.Treeview(
            process_frame,
            columns=("pid", "cpu", "ram"),
            show="headings",
            height=5,
        )
        self.process_tree.heading("pid", text="PID")
        self.process_tree.heading("cpu", text="CPU %")
        self.process_tree.heading("ram", text="RAM %")
        self.process_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        thresholds = ttk.Frame(process_frame)
        thresholds.pack(side=tk.RIGHT, padx=5)

        ttk.Label(thresholds, text="CPU próg (%)").pack(side=tk.LEFT)
        ttk.Entry(thresholds, textvariable=self.cpu_threshold_var, width=5).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Label(thresholds, text="RAM próg (%)").pack(side=tk.LEFT)
        ttk.Entry(thresholds, textvariable=self.ram_threshold_var, width=5).pack(
            side=tk.LEFT, padx=2
        )

        # Układ wykresów
        metrics_count = (
            2
            + len(self.disk_mounts)
            + len(self.gpu.get_usage())
            + 2
        )
        cols = math.ceil(math.sqrt(metrics_count))
        rows = math.ceil(metrics_count / cols)
        self.fig, axs = plt.subplots(rows, cols, figsize=(cols * 5, rows * 3))
        self.fig.tight_layout(pad=3.0)
        self.ax = axs.flatten()

        plot_idx = 0
        plot_idx = self.init_plot("CPU", "blue", self.cpu_data, plot_idx)
        plot_idx = self.init_plot("RAM", "green", self.ram_data, plot_idx)

        for mount in self.disk_mounts:
            plot_idx = self.init_plot(
                f"DISK_{mount}", "orange",
                self.disk_data[mount],
                plot_idx
            )

        for g in self.gpu.get_usage():
            name = f"GPU_{g.name}"
            self.gpu_data[g.name] = []
            plot_idx = self.init_plot(
                name,
                "purple",
                self.gpu_data[g.name],
                plot_idx
            )

        for net in ["NET_UP", "NET_DOWN"]:
            plot_idx = self.init_plot(
                net,
                "brown",
                self.network_data[net],
                plot_idx
            )

        for i in range(plot_idx, len(self.ax)):
            self.ax[i].axis("off")

        self.ax[-1].set_xlabel("Czas (s)")
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.ani = animation.FuncAnimation(
            self.fig,
            self.update_plot,
            interval=self.update_interval_ms
        )

    def apply_settings(self):
        """Aktualizuje parametry interwału odświeżania i długości historii."""
        try:
            self.update_interval_ms = int(self.interval_var.get())
            self.history_length = int(self.history_var.get())
        except ValueError:
            return
        if hasattr(self, "ani") and self.ani:
            self.ani.event_source.interval = self.update_interval_ms
        self.trim_buffers()

    def trim_buffers(self):
        """Przycina bufory danych do ustalonej długości historii."""
        if len(self.x_data) > self.history_length:
            excess = len(self.x_data) - self.history_length
            del self.x_data[:excess]
            del self.cpu_data[:excess]
            del self.ram_data[:excess]
            for key in self.disk_data:
                del self.disk_data[key][:excess]
            for key in self.gpu_data:
                del self.gpu_data[key][:excess]
            for key in self.network_data:
                del self.network_data[key][:excess]

    def init_plot(self, label, color, data_buffer, idx):
        """
        Tworzy nowy wykres dla danej metryki.

        Args:
            label: Nazwa metryki.
            color: Kolor wykresu.
            data_buffer: Bufor z danymi.
            idx: Indeks wykresu na siatce matplotlib.

        Returns:
            Nowy indeks wykresu.
        """
        line, = self.ax[idx].plot([], [], label=label, color=color)
        fill = self.ax[idx].fill_between([], [], [], color=color, alpha=0.3)
        self.ax[idx].set_ylim(0, 100)
        self.ax[idx].set_title(label)
        self.ax[idx].set_ylabel("%")
        self.ax[idx].grid(True)
        self.lines[label] = line
        self.fills[label] = fill
        return idx + 1

    @safe_call()
    def update_plot(self, frame):
        """
        Aktualizuje dane oraz rysuje wykresy w regularnych odstępach czasu.
        Funkcja jest wywoływana co sekundę przez animację matplotlib.
        Args:
            frame: Numer aktualnej klatki animacji (ignorowany).
        """
        self.x_data.append(self.frame_count)
        self.cpu_data.append(self.cpu.get_usage().percent)
        self.ram_data.append(self.ram.get_usage().percent)

        for usage in self.disk.get_usage():
            self.disk_data[usage.mount].append(usage.percent)

        for usage in self.gpu.get_usage():
            self.gpu_data[usage.name].append(usage.percent)

        net = self.network.get_usage()
        self.network_data["NET_UP"].append(net.upload_kbps)
        self.network_data["NET_DOWN"].append(net.download_kbps)

        self.trim_buffers()

        self.frame_count += 1
        self.refresh_plot("CPU", self.cpu_data)
        self.refresh_plot("RAM", self.ram_data)
        for k in self.disk_data:
            self.refresh_plot(f"DISK_{k}", self.disk_data[k])
        for k in self.gpu_data:
            self.refresh_plot(f"GPU_{k}", self.gpu_data[k])
        for k in self.network_data:
            self.refresh_plot(k, self.network_data[k])

        processes = self.process_monitor.get_top_processes()
        if self.process_tree:
            self.process_tree.delete(*self.process_tree.get_children())
            for p in processes:
                self.process_tree.insert(
                    "", tk.END, values=(p.pid, f"{p.cpu_percent:.1f}", f"{p.memory_percent:.1f}")
                )

        try:
            cpu_thr = float(self.cpu_threshold_var.get())
        except (ValueError, AttributeError):
            cpu_thr = None
        try:
            ram_thr = float(self.ram_threshold_var.get())
        except (ValueError, AttributeError):
            ram_thr = None

        if (cpu_thr is not None) or (ram_thr is not None):
            for p in processes:
                if (
                    (cpu_thr is not None and p.cpu_percent > cpu_thr)
                    or (ram_thr is not None and p.memory_percent > ram_thr)
                ):
                    messagebox.showwarning(
                        "Próg przekroczony",
                        f"Proces {p.name} (PID {p.pid}) przekracza próg",
                    )
                    break

        for ax in self.ax:
            ax.set_xlim(
                max(0, self.frame_count - self.history_length),
                self.frame_count + 1,
            )

        self.canvas.draw()

    def refresh_plot(self, label, data):
        """
        Aktualizuje pojedynczy wykres na podstawie nowo zebranych danych.

        Args:
            label: Nazwa metryki.
            data: Bufor z danymi dla metryki.
        """
        if len(data) != len(self.x_data):
            return
        line = self.lines[label]
        line.set_data(self.x_data, data)
        if self.fills[label]:
            self.fills[label].remove()
        self.fills[label] = line.axes.fill_between(
            self.x_data,
            data,
            alpha=0.3,
            color=line.get_color()
        )

    def on_close(self) -> None:
        """Handle application shutdown and persist settings."""
        try:
            cpu_thr = int(self.cpu_threshold_var.get())
        except (ValueError, tk.TclError):
            cpu_thr = 90
        try:
            ram_thr = int(self.ram_threshold_var.get())
        except (ValueError, tk.TclError):
            ram_thr = 90
        save_config(
            {
                "update_interval_ms": self.update_interval_ms,
                "history_length": self.history_length,
                "cpu_threshold": cpu_thr,
                "ram_threshold": ram_thr,
            }
        )
        safe_call()(self.root.destroy)()

    def export_selected(self):
        """
        Eksportuje wybraną przez użytkownika metrykę do pliku CSV lub JSON.
        Obsługuje eksport pojedynczych oraz wszystkich metryk naraz.
        """
        key = self.selected_metric.get()
        fmt = self.export_format_var.get()
        exporter: Exporter

        if fmt == "JSON":
            exporter = JSONExporter()
            if key == "WSZYSTKO":
                data = {
                    "CPU": self.cpu_data,
                    "RAM": self.ram_data,
                    **{f"DISK_{k}": v for k, v in self.disk_data.items()},
                    **{f"GPU_{k}": v for k, v in self.gpu_data.items()},
                    **self.network_data,
                }
                exporter.export("all_metrics.json", self.x_data, data)
                return
            elif key == "CPU":
                data = {"CPU": self.cpu_data}
            elif key == "RAM":
                data = {"RAM": self.ram_data}
            elif key.startswith("DISK_"):
                mount = key.split("_", 1)[1]
                data = {f"DISK_{mount}": self.disk_data[mount]}
            elif key.startswith("GPU_"):
                name = key.split("_", 1)[1]
                data = {f"GPU_{name}": self.gpu_data[name]}
            elif key in ["NET_UP", "NET_DOWN"]:
                data = {key: self.network_data[key]}
            else:
                return

            exporter.export(f"{key.lower()}_data.json", self.x_data, data)
            return

        if key == "CPU":
            exporter = CPUExporter()
            data = self.cpu_data
        elif key == "RAM":
            exporter = RAMExporter()
            data = self.ram_data
        elif key.startswith("DISK_"):
            mount = key.split("_", 1)[1]
            exporter = DiskExporter(mount)
            data = self.disk_data[mount]
        elif key.startswith("GPU_"):
            name = key.split("_", 1)[1]
            exporter = GPUExporter(name)
            data = self.gpu_data[name]
        elif key in ["NET_UP", "NET_DOWN"]:
            exporter = NetworkExporter(key)
            data = self.network_data[key]
        elif key == "WSZYSTKO":
            exporter = MultiMetricExporter()
            data = {
                "CPU": self.cpu_data,
                "RAM": self.ram_data,
                **{f"DISK_{k}": v for k, v in self.disk_data.items()},
                **{f"GPU_{k}": v for k, v in self.gpu_data.items()},
                **self.network_data,
            }
            exporter.export("all_metrics.csv", self.x_data, data)
            return
        else:
            return

        exporter.export(f"{key.lower()}_data.csv", self.x_data, data)


if __name__ == "__main__":
    root = tk.Tk()
    app = ResourceMonitorApp(root)
    root.mainloop()
