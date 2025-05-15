import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
from monitor.cpu_monitor import CPUMonitor
from monitor.memory_monitor import MemoryMonitor
from monitor.utils import safe_call

class ResourceMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitor CPU i RAM")
        self.root.geometry("900x700")

        self.cpu = CPUMonitor()
        self.mem = MemoryMonitor()
        self.running = True
        self.frame_count = 0

        self.x_data = []
        self.cpu_data = []
        self.mem_data = []

        self.build_gui()

    def build_gui(self):
        self.toggle_btn = ttk.Button(self.root, text="Stop", command=self.toggle)
        self.toggle_btn.pack(pady=10)

        # subploty: 2 wiersze, 1 kolumna
        self.fig, self.ax = plt.subplots(2, 1, figsize=(9, 6), sharex=True)
        self.fig.tight_layout(pad=3.0)

        self.line_cpu, = self.ax[0].plot([], [], label="CPU (%)", color="blue")
        self.ax[0].set_ylim(0, 100)
        self.ax[0].set_ylabel("CPU (%)")
        self.ax[0].set_title("Wykres użycia CPU")
        self.ax[0].legend()
        self.ax[0].grid(True)

        self.line_mem, = self.ax[1].plot([], [], label="RAM (%)", color="green")
        self.ax[1].set_ylim(0, 100)
        self.ax[1].set_ylabel("RAM (%)")
        self.ax[1].set_xlabel("Czas (s)")
        self.ax[1].set_title("Wykres użycia RAM")
        self.ax[1].legend()
        self.ax[1].grid(True)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.ani = animation.FuncAnimation(self.fig, self.update_plot, interval=1000)

    def toggle(self):
        self.running = not self.running
        self.toggle_btn.config(text="Start" if not self.running else "Stop")

    @safe_call
    def update_plot(self, frame):
        if not self.running:
            return self.line_cpu, self.line_mem

        self.x_data.append(self.frame_count)
        self.cpu_data.append(self.cpu.get_usage())
        self.mem_data.append(self.mem.get_usage())

        if len(self.x_data) > 60:
            self.x_data.pop(0)
            self.cpu_data.pop(0)
            self.mem_data.pop(0)

        self.frame_count += 1
        self.line_cpu.set_data(self.x_data, self.cpu_data)
        self.line_mem.set_data(self.x_data, self.mem_data)

        self.ax[0].set_xlim(max(0, self.frame_count - 60), self.frame_count + 1)
        self.ax[1].set_xlim(max(0, self.frame_count - 60), self.frame_count + 1)
        self.canvas.draw()

        return self.line_cpu, self.line_mem

if __name__ == "__main__":
    root = tk.Tk()
    app = ResourceMonitorApp(root)
    root.mainloop()
