import platform
import os

def print_hardware_config():
    print("=== HARDWARE CONFIGURATION ===")
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"OS Version: {platform.version()}")
    print(f"Architecture: {platform.machine()}")
    print(f"Processor: {platform.processor()}")
    print(f"CPU Cores (logical): {os.cpu_count()}")

