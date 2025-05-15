import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button
from monitor.cpu_monitor import CPUMonitor
from monitor.memory_monitor import MemoryMonitor
from monitor.utils import safe_call

cpu_monitor = CPUMonitor()
mem_monitor = MemoryMonitor()

x_data = []
cpu_data = []
mem_data = []
is_running = [True]  # ułatwia zmianę stanu wewnątrz funkcji

fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.2)  # zostaw miejsce na przycisk

line1, = ax.plot([], [], label="CPU Usage (%)")
line2, = ax.plot([], [], label="RAM Usage (%)")
ax.set_ylim(0, 100)
ax.set_xlim(0, 60)
ax.set_xlabel("Czas (s)")
ax.set_ylabel("Użycie (%)")
ax.set_title("Monitorowanie CPU i RAM - na żywo")
ax.legend()
ax.grid(True)

@safe_call
def update(frame):
    if not is_running[0]:
        return line1, line2

    x_data.append(frame)
    cpu_data.append(cpu_monitor.get_usage())
    mem_data.append(mem_monitor.get_usage())

    # Tylko ostatnie 60 sekund
    if len(x_data) > 60:
        x_data.pop(0)
        cpu_data.pop(0)
        mem_data.pop(0)

    line1.set_data(x_data, cpu_data)
    line2.set_data(x_data, mem_data)
    ax.set_xlim(max(0, frame - 60), frame + 1)
    return line1, line2

# Przyciski
ax_button = plt.axes([0.4, 0.05, 0.2, 0.075])
button = Button(ax_button, 'Start/Stop')

def toggle(event):
    is_running[0] = not is_running[0]

button.on_clicked(toggle)

ani = animation.FuncAnimation(fig, update, interval=1000)
plt.show()
