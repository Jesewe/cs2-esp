import os
import orjson
from pyMeow import get_color, fade_color

# Define the current version of the application.
CURRENT_VERSION = "v1.0.1.1"

# Define the configuration directory and file.
CONFIG_DIR = os.path.join(os.environ.get("LOCALAPPDATA", "."), "Requests", "ItsJesewe")
CONFIG_FILE = os.path.join(CONFIG_DIR, "esp_config.json")

# Default configuration values.
# Note: The minimap position is set to "top_left" and is not changeable by the user through the GUI.
DEFAULT_CONFIG = {
    "draw_snaplines": False,          # Whether to draw snaplines
    "enable_box": True,               # Whether to draw boxes around enemies
    "snaplines_color_hex": "#FFFFFF", # Default snaplines color (White)
    "box_line_thickness": 1.2,        # Default box line thickness
    "box_color_hex": "#FFA500",       # Default enemy box outline (Orange)
    "text_color_hex": "#FFFFFF",      # Default text color (White)
    "draw_health_numbers": False,     # Whether to display health numbers
    "use_transliteration": True,      # Whether to use transliteration for player names
    "draw_teammates": False,          # Whether to display ESP for teammates
    "teammate_color_hex": "#00FFFF",  # Default teammate box outline (Cyan)
    "draw_nicknames": True,           # Whether to draw nicknames
    "enable_minimap": False,          # Whether to enable the minimap overlay
    "minimap_size": 200,              # Size of the minimap (pixels)
    "minimap_position": "top_left",   # Position of the minimap (fixed to "top_left")
    "optimize_fps": False,            # Whether to enable FPS optimization
}

class OverlaySettings:
    CONFIGURABLE_ATTRIBUTES = list(DEFAULT_CONFIG.keys())

    def __init__(self):
        for attr in self.CONFIGURABLE_ATTRIBUTES:
            setattr(self, attr, DEFAULT_CONFIG[attr])
        self.load()

    def load(self) -> None:
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "rb") as f:
                    data = orjson.loads(f.read())
                for attr in self.CONFIGURABLE_ATTRIBUTES:
                    if attr in data:
                        setattr(self, attr, data[attr])
            except Exception as e:
                print("Error loading config:", e)
        else:
            self.save()

    def save(self) -> None:
        try:
            data = {attr: getattr(self, attr) for attr in self.CONFIGURABLE_ATTRIBUTES}
            with open(CONFIG_FILE, "wb") as f:
                f.write(orjson.dumps(data, option=orjson.OPT_INDENT_2))
        except Exception as e:
            print("Error saving config:", e)

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