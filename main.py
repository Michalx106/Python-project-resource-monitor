import math
from typing import Dict, List
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation

from monitor.cpu_monitor import CPUMonitor
from monitor.memory_monitor import MemoryMonitor
from monitor.disk_monitor import DiskMonitor
from monitor.gpu_monitor import GPUMonitor
from monitor.network_monitor import NetworkMonitor
from monitor.utils import safe_call

from exporter.exporters import (
    Exporter,
    CPUExporter, RAMExporter, DiskExporter, GPUExporter,
    NetworkExporter, MultiMetricExporter
)


class ResourceMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitor zasobów systemowych")
        self.root.geometry("1200x800")

        # Inicjalizacja monitorów
        self.cpu = CPUMonitor()
        self.ram = MemoryMonitor()
        self.gpu = GPUMonitor()
        self.disk = DiskMonitor()
        self.network = NetworkMonitor()

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
        self.network_data: Dict[str, List[float]] = {"NET_UP": [], "NET_DOWN": []}

        self.disk_mounts = list(self.disk_data.keys())
        self.fig = None
        self.ax = []
        self.lines = {}
        self.fills = {}

        self.build_gui()

    def build_gui(self):
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

        export_btn = ttk.Button(
            frame,
            text="Eksportuj do CSV",
            command=self.export_selected
        )
        export_btn.pack(side=tk.LEFT, padx=5)

        # Układ wykresów
        metrics_count = 2 + len(self.disk_mounts) + len(self.gpu.get_usage()) + 2
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
            interval=1000
        )

    def init_plot(self, label, color, data_buffer, idx):
        line, = self.ax[idx].plot([], [], label=label, color=color)
        fill = self.ax[idx].fill_between([], [], [], color=color, alpha=0.3)
        self.ax[idx].set_ylim(0, 100)
        self.ax[idx].set_title(label)
        self.ax[idx].set_ylabel(label)
        self.ax[idx].legend()
        self.ax[idx].grid(True)
        self.lines[label] = line
        self.fills[label] = fill
        return idx + 1

    @safe_call
    def update_plot(self, frame):
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

        if len(self.x_data) > 60:
            self.x_data.pop(0)
            self.cpu_data.pop(0)
            self.ram_data.pop(0)
            for key in self.disk_data:
                self.disk_data[key].pop(0)
            for key in self.gpu_data:
                self.gpu_data[key].pop(0)
            for key in self.network_data:
                self.network_data[key].pop(0)

        self.frame_count += 1
        self.refresh_plot("CPU", self.cpu_data)
        self.refresh_plot("RAM", self.ram_data)
        for k in self.disk_data:
            self.refresh_plot(f"DISK_{k}", self.disk_data[k])
        for k in self.gpu_data:
            self.refresh_plot(f"GPU_{k}", self.gpu_data[k])
        for k in self.network_data:
            self.refresh_plot(k, self.network_data[k])

        for ax in self.ax:
            ax.set_xlim(max(0, self.frame_count - 60), self.frame_count + 1)

        self.canvas.draw()

    def refresh_plot(self, label, data):
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

    def export_selected(self):
        key = self.selected_metric.get()
        exporter: Exporter

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
                **self.network_data
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

# To do:
# - Add error handling for file operations
# - Add cpu cores usage
# - Add