import sys
import argparse
import json
import logging
import platform
import ctypes
import customtkinter as ctk
from pathlib import Path

# Base directory setup using pathlib
BASE_DIR = Path(__file__).parent
CONFIG_FILE = BASE_DIR / "config.json"

# Importing modules
sys.path.append(str(BASE_DIR / "modules"))
from configurator import Configurator
from dpi_scaler import set_dpi_awareness, DPIScaler

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

# CLI argument parsing
parser = argparse.ArgumentParser(description="Multi-module application with DPI and configuration support")
parser.add_argument("mode", choices=["run", "configuration", "diagnostics"], help="Operation mode")

group = parser.add_mutually_exclusive_group()
group.add_argument("--reset-all", action="store_true", help="Reset all configuration")
group.add_argument("--reset-set", metavar="MODULE", help="Reset configuration set for the given module")
group.add_argument("--reset-set-key", nargs="+", metavar=("MODULE", "KEY", "NEW_VALUE"),
                   help="Reset a key in a configuration set (optionally with a new value)")

# New CLI arguments for exporting/importing config
parser.add_argument("--export-config", metavar="FILE", help="Export configuration to a JSON file")
parser.add_argument("--import-config", metavar="FILE", help="Import configuration from a JSON file")

args = parser.parse_args()

# Initialize Configurator
configurator = Configurator(CONFIG_FILE, separate_files=False)
configurator.register_plugin(DPIScaler.MODULE_NAME, DPIScaler.DEFAULT_CONFIG)
dpi_scaler = DPIScaler(configurator)

# Export configuration function
def export_config(file_path: str) -> None:
    try:
        with open(file_path, "w") as f:
            json.dump(configurator.config_data, f, indent=4)
        print(f"Configuration exported to {file_path}", flush=True)
    except Exception as e:
        logging.error("Failed to export configuration: %s", e)

# Import configuration function
def import_config(file_path: str) -> None:
    try:
        with open(file_path, "r") as f:
            configurator.config_data = json.load(f)
        configurator.save_config()
        print(f"Configuration imported from {file_path}", flush=True)
    except Exception as e:
        logging.error("Failed to import configuration: %s", e)

# Handle CLI modes
if args.mode == "configuration":
    if args.reset_all:
        configurator.reset_all()
        print("Configuration reset.", flush=True)
        sys.exit(0)
    elif args.reset_set:
        configurator.reset_module(args.reset_set)
        print(f"Reset configuration set: {args.reset_set}", flush=True)
        sys.exit(0)
    elif args.reset_set_key:
        if len(args.reset_set_key) >= 2:
            module, key = args.reset_set_key[:2]
            new_value = args.reset_set_key[2] if len(args.reset_set_key) > 2 else None
            configurator.reset_key(module, key, new_value)
            print(f"Reset key: {key} in set: {module}", flush=True)
            sys.exit(0)
        else:
            print("Provide at least MODULE and KEY for --reset-set-key", flush=True)
            sys.exit(1)
    elif args.export_config:
        export_config(args.export_config)
        sys.exit(0)
    elif args.import_config:
        import_config(args.import_config)
        sys.exit(0)
    else:
        print("Current configuration:", flush=True)
        print(json.dumps(configurator.config_data, indent=4), flush=True)
        sys.exit(0)
elif args.mode == "diagnostics":
    root = ctk.CTk()
    root.withdraw()
    print("Diagnostics Report:", flush=True)
    print(f"  - DPIScale Factor: {dpi_scaler.scale_factor}", flush=True)
    print(f"  - Physical Screen: {root.winfo_screenwidth()}x{root.winfo_screenheight()}", flush=True)
    print(f"  - Virtual Screen: {root.winfo_width()}x{root.winfo_height()}", flush=True)
    sys.exit(0)

# Run mode - launch application
set_dpi_awareness(configurator.get("dpi", "awareness", "System"))

class App(ctk.CTk):
    def __init__(self, config, dpi_scaler):
        super().__init__()
        self.config = config
        self.dpi_scaler = dpi_scaler
        self.virtual_width = configurator.get("app", "window_width", 800)
        self.virtual_height = configurator.get("app", "window_height", 600)
        self.title("DPI and Configuration Application")
        self.geometry(f"{self.virtual_width}x{self.virtual_height}")
        self.after(100, self.center_window)
        self.label = ctk.CTkLabel(self, text=f"Dimensions (virtual): {self.virtual_width}x{self.virtual_height}")
        self.label.pack(pady=10)

    def center_window(self):
        self.update_idletasks()
        scaling_factor = configurator.get("dpi", "scale_factor", 1.0)
        target_width = self.virtual_width
        target_height = self.virtual_height
        screen_width = int(self.winfo_screenwidth() / scaling_factor)
        screen_height = int(self.winfo_screenheight() / scaling_factor)
        expected_x = int((screen_width - target_width) / 2 * scaling_factor)
        expected_y = int((screen_height - target_height) / 2 * scaling_factor)

        logging.info("Centering window: %dx%d, screen: %dx%d, scale: %.2f, x: %d, y: %d",
                     target_width, target_height, screen_width, screen_height, scaling_factor, expected_x, expected_y)

        self.geometry(f"{target_width}x{target_height}+{expected_x}+{expected_y}")

if __name__ == "__main__":
    app = App(configurator.config_data, dpi_scaler)
    app.mainloop()