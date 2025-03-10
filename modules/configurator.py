import json
import os
import logging

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

class Configurator:
    def __init__(self, config_path: str, separate_files: bool = False):
        self.config_path = config_path
        self.separate_files = separate_files
        self.config_data = {}
        self.plugins = {}  # słownik z pluginami, kluczem będzie nazwa modułu
        self.load_config()

    def load_config(self):
        if self.separate_files:
            # Obsługa oddzielnych plików – uproszczona wersja
            return
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    self.config_data = json.load(f)
            except Exception as e:
                logging.error("Nie można wczytać konfiguracji: %s", e)

    def save_config(self):
        if self.separate_files:
            return
        try:
            with open(self.config_path, "w") as f:
                json.dump(self.config_data, f, indent=4)
        except Exception as e:
            logging.error("Błąd zapisu konfiguracji: %s", e)

    def get(self, module: str, key: str, default=None):
        return self.config_data.get(module, {}).get(key, default)

    def set(self, module: str, key: str, value):
        if module not in self.config_data:
            self.config_data[module] = {}
        self.config_data[module][key] = value
        self.save_config()

    def register_plugin(self, module_name: str, default_config: dict):
        if module_name not in self.config_data:
            self.config_data[module_name] = default_config
            logging.info("Plugin %s zainicjowany domyślnymi ustawieniami.", module_name)
            self.save_config()
        self.plugins[module_name] = default_config

    def reset_module(self, module: str):
        if module in self.config_data:
            del self.config_data[module]
            self.save_config()

    def reset_key(self, module: str, key: str, new_value=None):
        if module in self.config_data and key in self.config_data[module]:
            old_value = self.config_data[module][key]
            if new_value is None:
                del self.config_data[module][key]
                logging.info("Zresetowano klucz: %s w zestawie: %s (poprzednia wartość: %s)", key, module, old_value)
            else:
                try:
                    # Jeśli stara wartość była liczbą, spróbuj przekształcić nową wartość na float
                    new_value_converted = float(new_value)
                except ValueError:
                    new_value_converted = new_value
                self.config_data[module][key] = new_value_converted
                logging.info("Zmieniono klucz: %s w zestawie: %s z %s na %s", key, module, old_value, new_value_converted)
            self.save_config()

    def reset_all(self):
        self.config_data = {}
        self.save_config()
