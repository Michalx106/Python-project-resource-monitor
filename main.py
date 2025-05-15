import time
import matplotlib.pyplot as plt
from monitor.cpu_monitor import CPUMonitor
from monitor.memory_monitor import MemoryMonitor
from monitor.utils import safe_call


@safe_call
def log_usage(monitor, label: str) -> float:
    usage = monitor.get_usage()
    print(f"{label} Usage: {usage}%")
    return usage


def main():
    cpu = CPUMonitor()
    memory = MemoryMonitor()

    cpu_data = []
    mem_data = []
    timestamps = []

    for i in range(10):  # przykładowe 10 pomiarów co sekundę
        cpu_usage = log_usage(cpu, "CPU")
        mem_usage = log_usage(memory, "Memory")

        cpu_data.append(cpu_usage)
        mem_data.append(mem_usage)
        timestamps.append(i)

        time.sleep(1)

    # wykres
    plt.plot(timestamps, cpu_data, label="CPU Usage")
    plt.plot(timestamps, mem_data, label="Memory Usage")
    plt.xlabel("Czas (s)")
    plt.ylabel("Użycie (%)")
    plt.title("Monitorowanie CPU i RAM")
    plt.legend()
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    main()
