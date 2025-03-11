import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

class Configurator:
    def __init__(self, config_path: Path, separate_files: bool = False):
        self.config_path = config_path
        self.separate_files = separate_files
        self.config_data = {}
        self.plugins = {}  # Dictionary for registered plugins
        self.load_config()

    def load_config(self) -> None:
        if self.separate_files:
            return
        if self.config_path.exists():
            try:
                with self.config_path.open("r", encoding="utf-8") as f:
                    self.config_data = json.load(f)
            except Exception as e:
                logging.error("Could not load configuration: %s", e)

    def save_config(self) -> None:
        if self.separate_files:
            return
        try:
            with self.config_path.open("w", encoding="utf-8") as f:
                json.dump(self.config_data, f, indent=4)
        except Exception as e:
            logging.error("Error saving configuration: %s", e)

    def get(self, module: str, key: str, default=None):
        return self.config_data.get(module, {}).get(key, default)

    def set(self, module: str, key: str, value) -> None:
        if module not in self.config_data:
            self.config_data[module] = {}
        self.config_data[module][key] = value
        self.save_config()

    def register_plugin(self, module_name: str, default_config: dict) -> None:
        if module_name not in self.config_data:
            self.config_data[module_name] = default_config
            logging.info("Plugin %s initialized with default settings.", module_name)
            self.save_config()
        self.plugins[module_name] = default_config

    def reset_module(self, module: str) -> None:
        if module in self.config_data:
            del self.config_data[module]
            self.save_config()

    def reset_key(self, module: str, key: str, new_value=None) -> None:
        if module in self.config_data and key in self.config_data[module]:
            old_value = self.config_data[module][key]
            if new_value is None:
                del self.config_data[module][key]
                logging.info("Reset key: %s in set: %s (previous value: %s)", key, module, old_value)
            else:
                try:
                    new_value_converted = float(new_value)
                except ValueError:
                    new_value_converted = new_value
                self.config_data[module][key] = new_value_converted
                logging.info("Changed key: %s in set: %s from %s to %s", key, module, old_value, new_value_converted)
            self.save_config()

    def reset_all(self) -> None:
        self.config_data = {}
        self.save_config()
