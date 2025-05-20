# main.py (GUI) – wszystkie monitory jako instancje klasy bazowej
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
import math
from typing import List
from monitor.base_monitor import BaseMonitor
from monitor.cpu_monitor import CPUMonitor
from monitor.memory_monitor import MemoryMonitor
from monitor.disk_monitor import DiskMonitor
from monitor.utils import safe_call

class ResourceMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitor CPU, RAM i Dysków")
        self.root.geometry("1000x900")

        # lista wszystkich monitorów jako BaseMonitor
        self.monitors: List[BaseMonitor] = [CPUMonitor(), MemoryMonitor(), DiskMonitor()]

        # dane dla GUI
        self.disk_mounts = DiskMonitor.get_mounts()
        self.running = True
        self.frame_count = 0

        self.x_data = []
        self.resource_data = {
            "CPU": [],
            "RAM": [],
            **{mount: [] for mount in self.disk_mounts}
        }

        self.build_gui()

    def build_gui(self):
        self.toggle_btn = ttk.Button(self.root, text="Stop", command=self.toggle)
        self.toggle_btn.pack(pady=10)

        total_plots = len(self.resource_data)
        cols = math.ceil(math.sqrt(total_plots))
        rows = math.ceil(total_plots / cols)

        self.fig, self.ax = plt.subplots(rows, cols, figsize=(cols * 5, rows * 3))
        self.fig.tight_layout(pad=3.5)
        self.ax = self.ax.flatten()

        self.lines = {}
        self.fills = {}

        for idx, key in enumerate(self.resource_data):
            ax = self.ax[idx]
            color = "blue" if key == "CPU" else "green" if key == "RAM" else "orange"
            line, = ax.plot([], [], label=f"{key} (%)", color=color)
            self.lines[key] = line
            self.fills[key] = None

            ax.set_ylim(0, 100)
            ax.set_title(f"Użycie {key}")
            ax.set_ylabel(key)
            ax.legend()
            ax.grid(True)

        for i in range(len(self.resource_data), len(self.ax)):
            self.ax[i].axis("off")

        self.ax[-1].set_xlabel("Czas (s)")

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.ani = animation.FuncAnimation(self.fig, self.update_plot, interval=1000)

    def toggle(self):
        self.running = not self.running
        self.toggle_btn.config(text="Start" if not self.running else "Stop")

    @safe_call
    def update_plot(self, frame):
        if not self.running:
            return

        self.x_data.append(self.frame_count)

        for monitor in self.monitors:
            usage = monitor.get_usage()
            if isinstance(usage, list):  # DiskMonitor
                for disk in usage:
                    if disk.mount in self.resource_data:
                        self.resource_data[disk.mount].append(disk.percent)
            else:
                name = "CPU" if hasattr(usage, 'used') is False else "RAM"
                self.resource_data[name].append(usage.percent)

        if len(self.x_data) > 60:
            self.x_data.pop(0)
            for key in self.resource_data:
                if self.resource_data[key]:
                    self.resource_data[key].pop(0)

        self.frame_count += 1

        for key, data in self.resource_data.items():
            if len(self.x_data) == len(data):
                line = self.lines[key]
                line.set_data(self.x_data, data)
                if self.fills[key]:
                    self.fills[key].remove()
                color = line.get_color()
                self.fills[key] = line.axes.fill_between(self.x_data, data, color=color, alpha=0.3)

        for ax in self.ax:
            ax.set_xlim(max(0, self.frame_count - 60), self.frame_count + 1)

        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = ResourceMonitorApp(root)
    root.mainloop()
