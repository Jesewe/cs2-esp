import os
import json
from pyMeow import get_color, fade_color

# Define the current version of the application.
CURRENT_VERSION = "v1.0.1.1"

# Define the configuration directory and file.
CONFIG_DIR = os.path.join(os.environ.get("LOCALAPPDATA", "."), "Requests", "ItsJesewe")
CONFIG_FILE = os.path.join(CONFIG_DIR, "esp_config.json")

# Default configuration values.
DEFAULT_CONFIG = {
    "draw_snaplines": False,
    "snaplines_color_hex": "#FFFFFF", # Default snaplines color (White)
    "box_line_thickness": 1.2,        # Default box line thickness
    "box_color_hex": "#FFA500",       # Default enemy box outline (Orange)
    "text_color_hex": "#FFFFFF",      # Default text color (White)
    "draw_health_numbers": False,     # Whether to display health numbers
    "use_transliteration": True,      # Whether to use transliteration for player names
    "draw_teammates": False,          # Whether to display ESP for teammates
    "teammate_color_hex": "#00FFFF"   # Default teammate box outline (Cyan)
}

class OverlaySettings:
    def __init__(self):
        self.draw_snaplines = DEFAULT_CONFIG["draw_snaplines"]
        self.snaplines_color_hex = DEFAULT_CONFIG["snaplines_color_hex"]
        self.box_line_thickness = DEFAULT_CONFIG["box_line_thickness"]
        self.box_color_hex = DEFAULT_CONFIG["box_color_hex"]
        self.text_color_hex = DEFAULT_CONFIG["text_color_hex"]
        self.draw_health_numbers = DEFAULT_CONFIG["draw_health_numbers"]
        self.use_transliteration = DEFAULT_CONFIG["use_transliteration"]
        self.draw_teammates = DEFAULT_CONFIG["draw_teammates"]
        self.teammate_color_hex = DEFAULT_CONFIG["teammate_color_hex"]
        self.load()

    def load(self) -> None:
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    data = json.load(f)
                if OverlaySettings._update_config(DEFAULT_CONFIG, data):
                    with open(CONFIG_FILE, "w") as f:
                        json.dump(data, f, indent=4)
                self.draw_snaplines = data.get("draw_snaplines", self.draw_snaplines)
                self.snaplines_color_hex = data.get("snaplines_color_hex", self.snaplines_color_hex)
                self.box_line_thickness = data.get("box_line_thickness", self.box_line_thickness)
                self.box_color_hex = data.get("box_color_hex", self.box_color_hex)
                self.text_color_hex = data.get("text_color_hex", self.text_color_hex)
                self.draw_health_numbers = data.get("draw_health_numbers", self.draw_health_numbers)
                self.use_transliteration = data.get("use_transliteration", self.use_transliteration)
                self.draw_teammates = data.get("draw_teammates", self.draw_teammates)
                self.teammate_color_hex = data.get("teammate_color_hex", self.teammate_color_hex)
            except Exception as e:
                print("Error loading config:", e)
        else:
            self.save()

    def save(self) -> None:
        try:
            data = {
                "draw_snaplines": self.draw_snaplines,
                "snaplines_color_hex": self.snaplines_color_hex,
                "box_line_thickness": self.box_line_thickness,
                "box_color_hex": self.box_color_hex,
                "text_color_hex": self.text_color_hex,
                "draw_health_numbers": self.draw_health_numbers,
                "use_transliteration": self.use_transliteration,
                "draw_teammates": self.draw_teammates,
                "teammate_color_hex": self.teammate_color_hex,
            }
            with open(CONFIG_FILE, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print("Error saving config:", e)

    @classmethod
    def _update_config(cls, default: dict, current: dict) -> bool:
        """
        Recursively update `current` with missing keys from `default`.
        Returns True if any keys were added.
        """
        updated = False
        for key, value in default.items():
            if key not in current:
                current[key] = value
                updated = True
            elif isinstance(value, dict) and isinstance(current.get(key), dict):
                if cls._update_config(value, current[key]):
                    updated = True
        return updated

overlay_settings = OverlaySettings()

COLOR_CHOICES = {
    "Orange": "#FFA500",
    "Red": "#FF0000",
    "Green": "#00FF00",
    "Blue": "#0000FF",
    "White": "#FFFFFF",
    "Black": "#000000",
    "Cyan": "#00FFFF",
    "Yellow": "#FFFF00"
}

class Offsets:
    m_pBoneArray = 496  # Default value.
    # Other offsets will be loaded dynamically.

class Colors:
    orange = get_color("orange")
    black = get_color("black")
    cyan = get_color("cyan")
    white = get_color("white")
    grey = fade_color(get_color("#242625"), 0.7)
    red = get_color("red")
    green = get_color("green")
    blue = get_color("blue")
    yellow = get_color("yellow")