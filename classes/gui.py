import os
import logging
import keyboard
import webbrowser
import threading
import pyMeow as overlay
import dearpygui.dearpygui as dpg

from classes.utils import resource_path, check_for_updates
from classes.cs2esp import OverlayWorker
from classes.config import overlay_settings, COLOR_CHOICES, CURRENT_VERSION

logger = logging.getLogger(__name__)

class MainWindow:
    """
    Main application window for the CS2 ESP overlay using DearPyGui.
    Provides a UI to adjust overlay settings, start/stop the overlay,
    and check for updates.
    """
    def __init__(self) -> None:
        self.repo_url: str = "github.com/Jesewe/cs2-esp"
        self.overlay_thread: threading.Thread | None = None
        self.overlay_worker: OverlayWorker | None = None
        self.overlay_running: bool = False
        
        # Color mapping for DearPyGui (RGB tuples)
        self.color_map = {
            name: self._hex_to_rgb(hex_code) 
            for name, hex_code in COLOR_CHOICES.items()
        }
        
        self.setup_dpg()
        self.setup_hotkeys()

    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """Convert hex color to RGB tuple for DearPyGui."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def _get_color_name_from_hex(self, hex_color: str) -> str:
        """Get color name from hex value."""
        for name, hex_code in COLOR_CHOICES.items():
            if hex_code == hex_color:
                return name
        return "Black"

    def setup_dpg(self) -> None:
        """Initialize DearPyGui context and create the main window."""
        dpg.create_context()
        
        # Setup fonts if available
        self.setup_fonts()
        
        # Create main window
        with dpg.window(
            label=f"CS2 ESP | {self.repo_url}",
            tag="main_window",
            width=600,
            height=500,
            no_resize=True,
            no_collapse=True,
            no_move=False
        ):
            self.create_header_section()
            dpg.add_separator()
            self.create_settings_section()
            dpg.add_separator()
            self.create_control_section()

        # Setup viewport
        dpg.create_viewport(
            title=f"CS2 ESP | {self.repo_url}",
            width=620,
            height=540,
            resizable=False
        )
        
        # Load icon if available
        self.load_app_icon()
        
        # Apply theme
        self.apply_theme()
        
        dpg.setup_dearpygui()

    def setup_fonts(self) -> None:
        """Setup custom fonts if available."""
        try:
            # You can add custom fonts here if needed
            pass
        except Exception as e:
            logger.error("Failed to load fonts: %s", e)

    def load_app_icon(self) -> None:
        """Load application icon if available."""
        icon_path = resource_path("src/img/icon.ico")
        if os.path.exists(icon_path):
            try:
                # DearPyGui doesn't directly support .ico files for viewport icons
                # You would need to convert to supported format or use a different approach
                pass
            except Exception as e:
                logger.error("Failed to load icon: %s", e)

    def apply_theme(self) -> None:
        """Apply custom theme to match the original design."""
        with dpg.theme() as global_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (45, 45, 45, 255))
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (45, 45, 45, 255))
                dpg.add_theme_color(dpg.mvThemeCol_PopupBg, (45, 45, 45, 255))
                dpg.add_theme_color(dpg.mvThemeCol_Border, (213, 0, 109, 255))
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (60, 60, 60, 255))
                dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (70, 70, 70, 255))
                dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (80, 80, 80, 255))
                dpg.add_theme_color(dpg.mvThemeCol_TitleBg, (35, 35, 35, 255))
                dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, (213, 0, 109, 255))
                dpg.add_theme_color(dpg.mvThemeCol_CheckMark, (213, 0, 109, 255))
                dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, (213, 0, 109, 255))
                dpg.add_theme_color(dpg.mvThemeCol_SliderGrabActive, (213, 0, 109, 255))
                dpg.add_theme_color(dpg.mvThemeCol_Button, (60, 60, 60, 255))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (213, 0, 109, 255))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (180, 0, 90, 255))
                dpg.add_theme_color(dpg.mvThemeCol_Header, (60, 60, 60, 255))
                dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (70, 70, 70, 255))
                dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, (80, 80, 80, 255))
                dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255, 255))

        dpg.bind_theme(global_theme)

    def create_header_section(self) -> None:
        """Create the header section with title and icon buttons."""
        with dpg.group(horizontal=True):
            # Title with custom color
            dpg.add_text(f"CS2 ESP {CURRENT_VERSION}")
            dpg.bind_item_theme(dpg.last_item(), self.create_title_theme())
            
            # Spacer to push buttons to the right
            dpg.add_spacer(width=150)
            
            # Icon buttons
            dpg.add_button(
                label="Telegram",
                callback=lambda: self.open_url("https://t.me/cs2_jesewe"),
                width=70
            )
            
            dpg.add_button(
                label="GitHub",
                callback=lambda: self.open_url("https://github.com/Jesewe/cs2-esp"),
                width=70
            )
            
            # Check for updates
            update_url = check_for_updates(CURRENT_VERSION)
            if update_url:
                update_btn = dpg.add_button(
                    label="Update!",
                    callback=lambda: self.open_url(update_url),
                    width=70
                )
                dpg.bind_item_theme(update_btn, self.create_update_button_theme())

    def create_title_theme(self) -> int:
        """Create theme for the title text."""
        with dpg.theme() as title_theme:
            with dpg.theme_component(dpg.mvText):
                dpg.add_theme_color(dpg.mvThemeCol_Text, (213, 0, 109, 255))
        return title_theme

    def create_update_button_theme(self) -> int:
        """Create theme for the update button."""
        with dpg.theme() as update_theme:
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, (51, 51, 51, 255))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (68, 68, 68, 255))
                dpg.add_theme_color(dpg.mvThemeCol_Border, (213, 0, 109, 255))
                dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 2)
        return update_theme

    def create_settings_section(self) -> None:
        """Create the settings section with all overlay options."""
        dpg.add_text("Overlay Settings", color=(213, 0, 109, 255))
        
        with dpg.group():
            # Snaplines settings
            with dpg.group(horizontal=True):
                dpg.add_checkbox(
                    label="Draw Snaplines",
                    tag="snaplines_checkbox",
                    default_value=overlay_settings.draw_snaplines,
                    callback=self.update_settings
                )
                
                dpg.add_combo(
                    items=list(COLOR_CHOICES.keys()),
                    tag="snaplines_color_combo",
                    default_value=self._get_color_name_from_hex(overlay_settings.snaplines_color_hex),
                    width=120,
                    callback=self.update_settings
                )
                dpg.add_text("Snaplines Color")

            dpg.add_spacer(height=5)

            # Bounding box settings
            with dpg.group(horizontal=True):
                if not hasattr(overlay_settings, "enable_box"):
                    overlay_settings.enable_box = True
                    
                dpg.add_checkbox(
                    label="Enable Bounding Box",
                    tag="box_checkbox",
                    default_value=overlay_settings.enable_box,
                    callback=self.update_settings
                )

            with dpg.group(horizontal=True):
                dpg.add_slider_float(
                    label="Box Line Thickness",
                    tag="thickness_slider",
                    default_value=overlay_settings.box_line_thickness,
                    min_value=0.5,
                    max_value=5.0,
                    format="%.1f",
                    width=200,
                    callback=self.update_settings
                )

            with dpg.group(horizontal=True):
                dpg.add_combo(
                    items=list(COLOR_CHOICES.keys()),
                    tag="box_color_combo",
                    default_value=self._get_color_name_from_hex(overlay_settings.box_color_hex),
                    width=120,
                    callback=self.update_settings
                )
                dpg.add_text("Box Color")

            with dpg.group(horizontal=True):
                dpg.add_combo(
                    items=list(COLOR_CHOICES.keys()),
                    tag="text_color_combo",
                    default_value=self._get_color_name_from_hex(overlay_settings.text_color_hex),
                    width=120,
                    callback=self.update_settings
                )
                dpg.add_text("Text Color")

            dpg.add_spacer(height=5)

            # Additional options
            dpg.add_checkbox(
                label="Draw Health Numbers",
                tag="health_numbers_checkbox",
                default_value=overlay_settings.draw_health_numbers,
                callback=self.update_settings
            )

            dpg.add_checkbox(
                label="Use Transliteration",
                tag="translit_checkbox",
                default_value=overlay_settings.use_transliteration,
                callback=self.update_settings
            )

            dpg.add_checkbox(
                label="Draw Teammates",
                tag="teammates_checkbox",
                default_value=overlay_settings.draw_teammates,
                callback=self.update_settings
            )

            with dpg.group(horizontal=True):
                dpg.add_combo(
                    items=list(COLOR_CHOICES.keys()),
                    tag="teammate_color_combo",
                    default_value=self._get_color_name_from_hex(overlay_settings.teammate_color_hex),
                    width=120,
                    callback=self.update_settings
                )
                dpg.add_text("Teammate Color")

    def create_control_section(self) -> None:
        """Create the control section with start/stop buttons."""
        dpg.add_text("Controls", color=(213, 0, 109, 255))
        
        with dpg.group(horizontal=True):
            dpg.add_button(
                label="Start Overlay (F6)",
                tag="start_button",
                callback=self.start_overlay,
                width=150,
                height=40
            )
            
            dpg.add_button(
                label="Stop Overlay (F7)",
                tag="stop_button",
                callback=self.stop_overlay,
                width=150,
                height=40,
                enabled=False
            )

        dpg.add_spacer(height=10)
        dpg.add_text("Hotkeys: F6 to start, F7 to stop", color=(180, 180, 180, 255))

    def setup_hotkeys(self) -> None:
        """Sets up global hotkeys for starting (F6) and stopping (F7) the overlay."""
        try:
            keyboard.add_hotkey("F6", self.start_overlay)
            keyboard.add_hotkey("F7", self.stop_overlay)
        except Exception as e:
            logger.error("Failed to register hotkeys: %s", e)

    def open_url(self, url: str) -> None:
        """Open URL in default browser."""
        webbrowser.open(url)

    def update_settings(self) -> None:
        """Updates overlay settings based on the current UI input values."""
        try:
            overlay_settings.enable_box = dpg.get_value("box_checkbox")
            overlay_settings.draw_snaplines = dpg.get_value("snaplines_checkbox")
            
            snaplines_color_name = dpg.get_value("snaplines_color_combo")
            overlay_settings.snaplines_color_hex = COLOR_CHOICES.get(snaplines_color_name, "#000000")
            
            overlay_settings.box_line_thickness = dpg.get_value("thickness_slider")
            
            box_color_name = dpg.get_value("box_color_combo")
            overlay_settings.box_color_hex = COLOR_CHOICES.get(box_color_name, "#FFA500")
            
            text_color_name = dpg.get_value("text_color_combo")
            overlay_settings.text_color_hex = COLOR_CHOICES.get(text_color_name, "#FFFFFF")
            
            overlay_settings.draw_health_numbers = dpg.get_value("health_numbers_checkbox")
            overlay_settings.use_transliteration = dpg.get_value("translit_checkbox")
            overlay_settings.draw_teammates = dpg.get_value("teammates_checkbox")
            
            teammate_color_name = dpg.get_value("teammate_color_combo")
            overlay_settings.teammate_color_hex = COLOR_CHOICES.get(teammate_color_name, "#00FFFF")
            
            overlay_settings.save()
        except Exception as e:
            logger.error("Error updating settings: %s", e)

    def start_overlay(self) -> None:
        """Starts the overlay worker thread if it is not already running."""
        if self.overlay_running:
            logger.debug("Overlay already running.")
            return

        try:
            # Define callback functions for the worker
            def on_error(error_msg: str):
                logger.error("Overlay error: %s", error_msg)
                self.show_error("Overlay Error", error_msg)
                self._reset_ui_after_stop()
            
            def on_finished():
                logger.info("Overlay finished.")
                self._reset_ui_after_stop()
            
            # Create worker with callbacks
            self.overlay_worker = OverlayWorker(
                error_callback=on_error,
                finished_callback=on_finished
            )
            
            # Start worker in separate thread
            self.overlay_thread = threading.Thread(
                target=self.overlay_worker.run, 
                daemon=True
            )
            self.overlay_thread.start()
            
            self.overlay_running = True
            dpg.configure_item("start_button", enabled=False)
            dpg.configure_item("stop_button", enabled=True)
            logger.info("Overlay started.")
            
        except Exception as e:
            logger.exception("Failed to start overlay: %s", e)
            self.show_error("Overlay Error", str(e))

    def _reset_ui_after_stop(self) -> None:
        """Reset UI state after overlay stops."""
        self.overlay_running = False
        dpg.configure_item("start_button", enabled=True)
        dpg.configure_item("stop_button", enabled=False)

    def stop_overlay(self) -> None:
        """Stops the overlay worker and resets the UI buttons."""
        try:
            if self.overlay_worker:
                self.overlay_worker.stop()
                
            if self.overlay_thread and self.overlay_thread.is_alive():
                self.overlay_thread.join(timeout=2.0)
                
            logger.info("Overlay stopped.")
            
        except Exception as e:
            logger.error("Error stopping overlay worker: %s", e)
        finally:
            self.overlay_worker = None
            self.overlay_thread = None
            self._reset_ui_after_stop()

    def show_error(self, title: str, message: str) -> None:
        """Show error message in a popup."""
        with dpg.window(
            label=title,
            modal=True,
            width=400,
            height=150,
            pos=[100, 100],
            tag="error_popup"
        ):
            dpg.add_text(message)
            dpg.add_spacer(height=20)
            dpg.add_button(
                label="OK",
                callback=lambda: dpg.delete_item("error_popup"),
                width=100
            )

    def show(self) -> None:
        """Show the main window and start the DearPyGui render loop."""
        dpg.show_viewport()
        dpg.set_primary_window("main_window", True)

    def run(self) -> None:
        """Run the main application loop."""
        try:
            dpg.start_dearpygui()
        finally:
            self.cleanup()

    def cleanup(self) -> None:
        """Clean up resources when closing the application."""
        self.stop_overlay()
        try:
            keyboard.remove_hotkey("F6")
            keyboard.remove_hotkey("F7")
        except Exception as e:
            logger.error("Error removing hotkeys: %s", e)
        
        try:
            overlay.overlay_close()
        except Exception as e:
            logger.error("Error closing overlay: %s", e)
            
        dpg.destroy_context()

    def __del__(self) -> None:
        """Destructor to ensure cleanup."""
        self.cleanup()