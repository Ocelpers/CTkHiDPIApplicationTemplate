import sys
import os
import argparse
import json
import logging
import customtkinter as ctk

# Dodajemy folder modules do sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, "modules"))

from configurator import Configurator
from dpi_scaler import set_dpi_awareness, DPIScaler

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

# Parsowanie argumentów CLI
parser = argparse.ArgumentParser(description="Aplikacja wielomodułowa z obsługą DPI i konfiguracji")
parser.add_argument("mode", choices=["run", "configuration", "diagnostics"], help="Tryb działania")
group = parser.add_mutually_exclusive_group()
group.add_argument("--reset-all", action="store_true", help="Resetuj całą konfigurację")
group.add_argument("--reset-set", metavar="MODULE", help="Resetuj zestaw konfiguracji dla podanego modułu")
group.add_argument("--reset-set-key", nargs="+", metavar=("MODULE", "KEY", "NEW_VALUE"),
                   help="Resetuj klucz w zestawie konfiguracji (opcjonalnie z nową wartością)")
args = parser.parse_args()

# Inicjalizacja konfiguratora
configurator = Configurator(CONFIG_FILE, separate_files=False)

# Rejestracja pluginu DPI
configurator.register_plugin(DPIScaler.MODULE_NAME, DPIScaler.DEFAULT_CONFIG)
dpi_scaler = DPIScaler(configurator)

# Obsługa trybów CLI
if args.mode == "configuration":
    if args.reset_all:
        configurator.reset_all()
        print("Konfiguracja zresetowana.", flush=True)
        sys.exit(0)
    elif args.reset_set:
        module_name = args.reset_set
        configurator.reset_module(module_name)
        print(f"Zresetowano zestaw: {module_name}", flush=True)
        sys.exit(0)
    elif args.reset_set_key:
        if len(args.reset_set_key) >= 2:
            module_name = args.reset_set_key[0]
            key = args.reset_set_key[1]
            new_value = args.reset_set_key[2] if len(args.reset_set_key) > 2 else None
            configurator.reset_key(module_name, key, new_value)
            print(f"Zresetowano klucz: {key} w zestawie: {module_name}", flush=True)
            sys.exit(0)
        else:
            print("Podaj przynajmniej MODULE i KEY dla --reset-set-key", flush=True)
            sys.exit(1)
    else:
        print("Aktualna konfiguracja:", flush=True)
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

# Tryb run – uruchamiamy aplikację
set_dpi_awareness(configurator.get("dpi", "awareness", "System"))

class App(ctk.CTk):
    def __init__(self, config, dpi_scaler):
        super().__init__()
        self.config = config
        self.dpi_scaler = dpi_scaler

        # Ustal wirtualne wymiary z konfiguracji lub domyślne
        self.virtual_width = configurator.get("app", "window_width", 800)
        self.virtual_height = configurator.get("app", "window_height", 600)

        self.title("Aplikacja z DPI i konfiguracją")
        self.geometry(f"{self.virtual_width}x{self.virtual_height}")
        self.after(100, self.center_window)

        self.label = ctk.CTkLabel(self, text=f"Wymiary (wirtualne): {self.virtual_width}x{self.virtual_height}")
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

        logging.info("Centrowanie okna: %dx%d, ekran: %dx%d, skala: %.2f, x: %d, y: %d",
                     target_width, target_height, screen_width, screen_height, scaling_factor, expected_x, expected_y)

        self.geometry(f"{target_width}x{target_height}+{expected_x}+{expected_y}")

if __name__ == "__main__":
    app = App(configurator.config_data, dpi_scaler)
    app.mainloop()
