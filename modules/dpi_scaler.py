import ctypes
import logging
import platform
import customtkinter as ctk

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

def set_dpi_awareness(mode: str) -> None:
    """Sets DPI awareness based on the operating system."""
    awareness_modes = {
        "Unaware": 0,
        "System": 1,
        "Per-monitor": 2
    }
    if platform.system() == "Windows":
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(awareness_modes.get(mode, 1))
            logging.info("DPI awareness set to %s", mode)
        except AttributeError as e:
            logging.error("Error setting DPI awareness: %s", e)
            try:
                ctypes.windll.user32.SetProcessDPIAware()
                logging.info("DPI awareness set using SetProcessDPIAware")
            except Exception as e2:
                logging.error("DPI awareness not supported: %s", e2)

def detect_scaling_factor() -> float:
    """Detects the DPI scaling factor of the current display."""
    temp_root = ctk.CTk()
    temp_root.geometry("800x600")
    temp_root.update_idletasks()

    real_width = temp_root.winfo_width()
    real_height = temp_root.winfo_height()

    scaling_factor_x = real_width / 800
    scaling_factor_y = real_height / 600
    scaling_factor = (scaling_factor_x + scaling_factor_y) / 2

    temp_root.destroy()
    logging.info("Detected scale: %.2f (X: %.2f, Y: %.2f)", scaling_factor, scaling_factor_x, scaling_factor_y)
    return scaling_factor

class DPIScaler:
    MODULE_NAME = "dpi"
    DEFAULT_CONFIG = {
        "scale_factor": 1.0,
        "awareness": "System"
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

    def apply_scale(self, width: int, height: int) -> tuple[int, int]:
        """Applies the DPI scale factor to given dimensions."""
        return int(width * self.scale_factor), int(height * self.scale_factor)
