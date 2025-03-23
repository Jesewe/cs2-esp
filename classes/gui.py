import os
import logging
import keyboard
import pyMeow as overlay
from PyQt6.QtWidgets import (
    QMainWindow, QLabel, QWidget, QVBoxLayout, QHBoxLayout,
    QFormLayout, QCheckBox, QDoubleSpinBox, QComboBox,
    QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt, QUrl, QSize, QThread, pyqtSlot
from PyQt6.QtGui import QIcon, QDesktopServices

from classes.utils import resource_path, check_for_updates
from classes.cs2esp import OverlayWorker
from classes.config import overlay_settings, COLOR_CHOICES, CURRENT_VERSION

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """
    Main application window for the CS2 ESP overlay.
    Provides a UI to adjust overlay settings, start/stop the overlay,
    and check for updates.
    """
    def __init__(self) -> None:
        super().__init__()
        self.repo_url: str = "github.com/Jesewe/cs2-esp"
        self.setWindowTitle(f"CS2 ESP | {self.repo_url}")
        self.set_app_icon(resource_path("src/img/icon.ico"))
        self.setFixedSize(600, 500)
        self.overlay_thread: QThread | None = None
        self.overlay_worker: OverlayWorker | None = None
        self.init_ui()
        self.apply_stylesheet(resource_path('src/styles.css'))
        self.setup_hotkeys()

    def setup_hotkeys(self) -> None:
        """
        Sets up global hotkeys for starting (F6) and stopping (F7) the overlay.
        """
        try:
            keyboard.add_hotkey("F6", self.start_overlay)
            keyboard.add_hotkey("F7", self.stop_overlay)
        except Exception as e:
            logger.error("Failed to register hotkeys: %s", e)

    def apply_stylesheet(self, stylesheet_path: str) -> None:
        """
        Applies a custom stylesheet to the main window.
        """
        try:
            with open(stylesheet_path, 'r', encoding='utf-8') as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            logger.error("Failed to load stylesheet (%s): %s", stylesheet_path, e)

    def set_app_icon(self, icon_path: str) -> None:
        """
        Sets the application icon if the file exists.
        """
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            logger.warning("Icon not found at %s, skipping.", icon_path)

    def create_icon_button(self, relative_path: str, tooltip: str, url: str, custom_style: str | None = None) -> QPushButton:
        """
        Create a flat icon button that opens the provided URL when clicked.
        """
        btn = QPushButton()
        btn.setIcon(QIcon(resource_path(relative_path)))
        btn.setIconSize(QSize(24, 24))
        btn.setFlat(True)
        btn.setToolTip(tooltip)
        if custom_style:
            btn.setStyleSheet(custom_style)
        btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(url)))
        return btn

    def init_ui(self) -> None:
        """
        Initializes the user interface components.
        """
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()

        # Header section with title and icon buttons
        header_layout = self.create_header_layout()
        main_layout.addLayout(header_layout)

        # Form section with various overlay settings
        form_layout = self.create_form_layout()
        main_layout.addLayout(form_layout)

        # Buttons section for overlay control and updates
        button_layout = self.create_button_layout()
        main_layout.addLayout(button_layout)

        main_widget.setLayout(main_layout)

    def create_header_layout(self) -> QHBoxLayout:
        """
        Creates the header layout containing the app title and icon buttons.
        """
        header_layout = QHBoxLayout()

        title_label = QLabel(f"CS2 ESP {CURRENT_VERSION}")
        title_label.setStyleSheet("color: #D5006D; font-size: 22px; font-weight: bold;")
        header_layout.addWidget(title_label)

        icon_layout = QHBoxLayout()
        icon_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        icon_layout.addWidget(self.create_icon_button('src/img/telegram_icon.png',
                                                      "Join our Telegram channel",
                                                      "https://t.me/cs2_jesewe"))
        icon_layout.addWidget(self.create_icon_button('src/img/github_icon.png',
                                                      "Visit our GitHub repository",
                                                      "https://github.com/Jesewe/cs2-esp"))

        update_url = check_for_updates(CURRENT_VERSION)
        if update_url:
            update_style = (
                "QPushButton { background-color: #333333; border-radius: 12px; border: 2px solid #D5006D; } "
                "QPushButton:hover { background-color: #444444; }"
            )
            update_btn = self.create_icon_button('src/img/update_icon.png',
                                                 "New update available! Click to download.",
                                                 update_url,
                                                 custom_style=update_style)
            icon_layout.addWidget(update_btn)

        header_layout.addLayout(icon_layout)
        return header_layout

    def create_form_layout(self) -> QFormLayout:
        """
        Creates the form layout containing overlay settings controls.
        """
        form_layout = QFormLayout()

        # Snaplines options
        self.snaplines_checkbox = QCheckBox("Draw Snaplines")
        self.snaplines_checkbox.setChecked(overlay_settings.draw_snaplines)
        form_layout.addRow("Snaplines:", self.snaplines_checkbox)

        self.snaplines_color_combo = QComboBox()
        for name, hexcode in COLOR_CHOICES.items():
            self.snaplines_color_combo.addItem(name, hexcode)
        default_snap = next(
            (name for name, hexcode in COLOR_CHOICES.items()
             if hexcode == overlay_settings.snaplines_color_hex), "Black"
        )
        self.snaplines_color_combo.setCurrentText(default_snap)
        form_layout.addRow("Snaplines Color:", self.snaplines_color_combo)

        # Box line thickness
        self.thickness_spinbox = QDoubleSpinBox()
        self.thickness_spinbox.setRange(0.5, 5.0)
        self.thickness_spinbox.setSingleStep(0.1)
        self.thickness_spinbox.setValue(overlay_settings.box_line_thickness)
        form_layout.addRow("Box Line Thickness:", self.thickness_spinbox)

        # Box color options
        self.box_color_combo = QComboBox()
        for name, hexcode in COLOR_CHOICES.items():
            self.box_color_combo.addItem(name, hexcode)
        default_box = next(
            (name for name, hexcode in COLOR_CHOICES.items()
             if hexcode == overlay_settings.box_color_hex), "Orange"
        )
        self.box_color_combo.setCurrentText(default_box)
        form_layout.addRow("Box Color:", self.box_color_combo)

        # Text color options
        self.text_color_combo = QComboBox()
        for name, hexcode in COLOR_CHOICES.items():
            self.text_color_combo.addItem(name, hexcode)
        default_text = next(
            (name for name, hexcode in COLOR_CHOICES.items()
             if hexcode == overlay_settings.text_color_hex), "White"
        )
        self.text_color_combo.setCurrentText(default_text)
        form_layout.addRow("Text Color:", self.text_color_combo)

        # Health numbers option
        self.health_numbers_checkbox = QCheckBox("Draw Health Numbers")
        self.health_numbers_checkbox.setChecked(overlay_settings.draw_health_numbers)
        form_layout.addRow("Health Numbers:", self.health_numbers_checkbox)

        # Transliteration option
        self.translit_checkbox = QCheckBox("Use Transliteration")
        self.translit_checkbox.setChecked(overlay_settings.use_transliteration)
        form_layout.addRow("Transliteration:", self.translit_checkbox)

        # Teammates options
        self.teammates_checkbox = QCheckBox("Draw Teammates")
        self.teammates_checkbox.setChecked(overlay_settings.draw_teammates)
        form_layout.addRow("Teammates:", self.teammates_checkbox)

        self.teammate_color_combo = QComboBox()
        for name, hexcode in COLOR_CHOICES.items():
            self.teammate_color_combo.addItem(name, hexcode)
        default_team = next(
            (name for name, hexcode in COLOR_CHOICES.items()
             if hexcode == overlay_settings.teammate_color_hex), "Cyan"
        )
        self.teammate_color_combo.setCurrentText(default_team)
        form_layout.addRow("Teammate Color:", self.teammate_color_combo)

        # Connect UI changes to update settings
        self.snaplines_checkbox.stateChanged.connect(self.update_settings)
        self.snaplines_color_combo.currentIndexChanged.connect(self.update_settings)
        self.thickness_spinbox.valueChanged.connect(self.update_settings)
        self.box_color_combo.currentIndexChanged.connect(self.update_settings)
        self.text_color_combo.currentIndexChanged.connect(self.update_settings)
        self.health_numbers_checkbox.stateChanged.connect(self.update_settings)
        self.translit_checkbox.stateChanged.connect(self.update_settings)
        self.teammates_checkbox.stateChanged.connect(self.update_settings)
        self.teammate_color_combo.currentIndexChanged.connect(self.update_settings)

        return form_layout

    def create_button_layout(self) -> QHBoxLayout:
        """
        Creates the layout containing control buttons for starting/stopping the overlay and checking for updates.
        """
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(30, 0, 30, 0)

        self.start_button = QPushButton("Start Overlay")
        self.stop_button = QPushButton("Stop Overlay")
        self.stop_button.setEnabled(False)

        self.start_button.clicked.connect(self.start_overlay)
        self.stop_button.clicked.connect(self.stop_overlay)

        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)

        return button_layout

    @pyqtSlot()
    def update_settings(self) -> None:
        """
        Updates overlay settings based on the current UI input values.
        """
        overlay_settings.draw_snaplines = self.snaplines_checkbox.isChecked()
        overlay_settings.snaplines_color_hex = self.snaplines_color_combo.currentData() or "#000000"
        overlay_settings.box_line_thickness = self.thickness_spinbox.value()
        overlay_settings.box_color_hex = self.box_color_combo.currentData() or "#FFA500"
        overlay_settings.text_color_hex = self.text_color_combo.currentData() or "#FFFFFF"
        overlay_settings.draw_health_numbers = self.health_numbers_checkbox.isChecked()
        overlay_settings.use_transliteration = self.translit_checkbox.isChecked()
        overlay_settings.draw_teammates = self.teammates_checkbox.isChecked()
        overlay_settings.teammate_color_hex = self.teammate_color_combo.currentData() or "#00FFFF"
        overlay_settings.save()

    @pyqtSlot()
    def start_overlay(self) -> None:
        """
        Starts the overlay worker thread if it is not already running.
        """
        if self.overlay_thread is not None and self.overlay_thread.isRunning():
            logger.debug("Overlay already running.")
            return

        try:
            self.overlay_thread = QThread()
            self.overlay_worker = OverlayWorker()
            self.overlay_worker.moveToThread(self.overlay_thread)
            self.overlay_worker.errorOccurred.connect(self.on_overlay_error)
            self.overlay_thread.started.connect(self.overlay_worker.run)
            self.overlay_thread.finished.connect(self.overlay_thread.deleteLater)
            self.overlay_thread.finished.connect(lambda: setattr(self, 'overlay_thread', None))
            self.overlay_thread.start()

            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            logger.info("Overlay started.")
        except Exception as e:
            logger.exception("Failed to start overlay: %s", e)
            self.on_overlay_error(str(e))

    @pyqtSlot()
    def stop_overlay(self) -> None:
        """
        Stops the overlay worker and resets the UI buttons.
        """
        try:
            if self.overlay_worker:
                self.overlay_worker.stop()
            if self.overlay_thread:
                self.overlay_thread.quit()
                self.overlay_thread.wait()
                logger.info("Overlay stopped.")
        except RuntimeError as e:
            logger.error("Error stopping overlay worker: %s", e)
        finally:
            self.overlay_worker = None
            self.overlay_thread = None

        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    @pyqtSlot(str)
    def on_overlay_error(self, error_message: str) -> None:
        """
        Handles overlay errors by showing an error dialog and stopping the overlay.
        """
        QMessageBox.critical(self, "Overlay Error", error_message)
        self.stop_overlay()

    def closeEvent(self, event) -> None:
        """
        Ensures that the overlay is stopped and hotkeys are removed upon closing the application.
        """
        self.stop_overlay()
        try:
            keyboard.remove_hotkey("F6")
            keyboard.remove_hotkey("F7")
        except Exception as e:
            logger.error("Error removing hotkeys: %s", e)
        overlay.overlay_close()
        event.accept()