import ctypes
import logging
import customtkinter as ctk

def set_dpi_awareness(mode):
    awareness_modes = {
        "Unaware": 0,
        "System": 1,
        "Per-monitor": 2
    }
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(awareness_modes.get(mode, 1))
        logging.info("Ustawiono DPI awareness na %s", mode)
    except AttributeError as e:
        logging.error("Błąd przy ustawianiu DPI awareness: %s", e)
        try:
            ctypes.windll.user32.SetProcessDPIAware()
            logging.info("Ustawiono DPI awareness przez SetProcessDPIAware")
        except Exception as e2:
            logging.error("DPI awareness nie jest obsługiwany: %s", e2)

def detect_scaling_factor():
    temp_root = ctk.CTk()
    temp_root.geometry("800x600")  # znany rozmiar wirtualny
    temp_root.update_idletasks()

    real_width = temp_root.winfo_width()
    real_height = temp_root.winfo_height()

    scaling_factor_x = real_width / 800
    scaling_factor_y = real_height / 600
    scaling_factor = (scaling_factor_x + scaling_factor_y) / 2

    temp_root.destroy()
    logging.info("Wykryta skala: %.2f (X: %.2f, Y: %.2f)", scaling_factor, scaling_factor_x, scaling_factor_y)
    return scaling_factor

class DPIScaler:
    MODULE_NAME = "dpi"
    DEFAULT_CONFIG = {
        "scale_factor": 1.0,      # domyślnie brak skalowania
        "awareness": "System"     # domyślny tryb DPI
    }

    def __init__(self, configurator):
        self.configurator = configurator
        stored_scale = self.configurator.get(self.MODULE_NAME, "scale_factor")
        if stored_scale is None:
            self.scale_factor = detect_scaling_factor()
            self.configurator.set(self.MODULE_NAME, "scale_factor", self.scale_factor)
        else:
            try:
                self.scale_factor = float(stored_scale)
            except ValueError:
                self.scale_factor = detect_scaling_factor()
                self.configurator.set(self.MODULE_NAME, "scale_factor", self.scale_factor)
        logging.info("DPIScaler: scale_factor = %.2f", self.scale_factor)

    def apply_scale(self, width: int, height: int) -> tuple:
        return int(width * self.scale_factor), int(height * self.scale_factor)
