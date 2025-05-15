import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
from monitor.cpu_monitor import CPUMonitor
from monitor.memory_monitor import MemoryMonitor
from monitor.disk_monitor import DiskMonitor
from monitor.utils import safe_call
import math

class ResourceMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitor CPU, RAM i Dysków")
        self.root.geometry("1000x900")

        self.cpu = CPUMonitor()
        self.mem = MemoryMonitor()
        self.disk_monitor = DiskMonitor()
        self.disk_mounts = self.disk_monitor.partitions

        self.running = True
        self.frame_count = 0

        self.x_data = []
        self.cpu_data = []
        self.mem_data = []
        self.disk_data = {mount: [] for mount in self.disk_mounts}

        self.build_gui()

    def build_gui(self):
        self.toggle_btn = ttk.Button(self.root, text="Stop", command=self.toggle)
        self.toggle_btn.pack(pady=10)

        total_plots = 2 + len(self.disk_mounts)
        cols = math.ceil(math.sqrt(total_plots))
        rows = math.ceil(total_plots / cols)

        self.fig, self.ax = plt.subplots(rows, cols, figsize=(cols * 5, rows * 3))
        self.fig.tight_layout(pad=3.5)
        self.ax = self.ax.flatten()

        plot_idx = 0

        self.line_cpu, = self.ax[plot_idx].plot([], [], label="CPU (%)", color="blue")
        self.fill_cpu = self.ax[plot_idx].fill_between([], [], [], color="blue", alpha=0.3)
        self.ax[plot_idx].set_ylim(0, 100)
        self.ax[plot_idx].set_title("Użycie CPU")
        self.ax[plot_idx].set_ylabel("CPU")
        self.ax[plot_idx].legend()
        self.ax[plot_idx].grid(True)
        plot_idx += 1

        self.line_mem, = self.ax[plot_idx].plot([], [], label="RAM (%)", color="green")
        self.fill_mem = self.ax[plot_idx].fill_between([], [], [], color="green", alpha=0.3)
        self.ax[plot_idx].set_ylim(0, 100)
        self.ax[plot_idx].set_title("Użycie RAM")
        self.ax[plot_idx].set_ylabel("RAM")
        self.ax[plot_idx].legend()
        self.ax[plot_idx].grid(True)
        plot_idx += 1

        self.disk_lines = {}
        self.disk_fills = {}

        for mount in self.disk_mounts:
            ax = self.ax[plot_idx]
            line, = ax.plot([], [], label=f"{mount} (%)", color="orange")
            fill = ax.fill_between([], [], [], color="orange", alpha=0.3)
            ax.set_ylim(0, 100)
            ax.set_title(f"Dysk {mount}")
            ax.set_ylabel("Dysk")
            ax.legend()
            ax.grid(True)
            self.disk_lines[mount] = line
            self.disk_fills[mount] = fill
            plot_idx += 1

        for i in range(plot_idx, len(self.ax)):
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
        self.cpu_data.append(self.cpu.get_usage())
        self.mem_data.append(self.mem.get_usage())
        disk_usages = self.disk_monitor.get_all_usages()
        for mount in self.disk_mounts:
            self.disk_data[mount].append(disk_usages[mount])

        if len(self.x_data) > 60:
            self.x_data.pop(0)
            self.cpu_data.pop(0)
            self.mem_data.pop(0)
            for mount in self.disk_mounts:
                self.disk_data[mount].pop(0)

        self.frame_count += 1

        self.line_cpu.set_data(self.x_data, self.cpu_data)
        self.fill_cpu.remove()
        self.fill_cpu = self.line_cpu.axes.fill_between(self.x_data, self.cpu_data, color="blue", alpha=0.3)

        self.line_mem.set_data(self.x_data, self.mem_data)
        self.fill_mem.remove()
        self.fill_mem = self.line_mem.axes.fill_between(self.x_data, self.mem_data, color="green", alpha=0.3)

        for mount in self.disk_mounts:
            line = self.disk_lines[mount]
            data = self.disk_data[mount]
            line.set_data(self.x_data, data)
            self.disk_fills[mount].remove()
            self.disk_fills[mount] = line.axes.fill_between(self.x_data, data, color="orange", alpha=0.3)

        for ax in self.ax:
            ax.set_xlim(max(0, self.frame_count - 60), self.frame_count + 1)

        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = ResourceMonitorApp(root)
    root.mainloop()
