import keyboard
import os
import logging
import pyMeow as overlay
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QFormLayout, QCheckBox, QDoubleSpinBox, QComboBox,
    QPushButton, QMessageBox
)
from PyQt6.QtCore import QThread, pyqtSlot
from PyQt6.QtGui import QIcon

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
        self.setGeometry(100, 100, 400, 400)  # Increased height for extra button
        self.overlay_thread: QThread | None = None
        self.overlay_worker: OverlayWorker | None = None
        self.init_ui()
        self.setup_hotkeys()

    def setup_hotkeys(self) -> None:
        """
        Sets up global hotkeys for starting (F6) and stopping (F7) the overlay.
        """
        keyboard.add_hotkey("F6", self.start_overlay)
        keyboard.add_hotkey("F7", self.stop_overlay)

    def set_app_icon(self, icon_path: str) -> None:
        """
        Sets the application icon if the file exists.
        """
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            logger.warning("Icon not found at %s, skipping.", icon_path)

    def init_ui(self) -> None:
        """
        Initializes the user interface components.
        """
        widget = QWidget()
        self.setCentralWidget(widget)
        main_layout = QVBoxLayout()
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

        main_layout.addLayout(form_layout)

        # Buttons layout
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Overlay")
        self.stop_button = QPushButton("Stop Overlay")
        self.stop_button.setEnabled(False)
        self.update_button = QPushButton("Check for Updates")
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.update_button)
        main_layout.addLayout(button_layout)

        widget.setLayout(main_layout)

        # Connect signals to slots
        self.start_button.clicked.connect(self.start_overlay)
        self.stop_button.clicked.connect(self.stop_overlay)
        self.update_button.clicked.connect(self.check_updates)
        self.snaplines_checkbox.stateChanged.connect(self.update_settings)
        self.snaplines_color_combo.currentIndexChanged.connect(self.update_settings)
        self.thickness_spinbox.valueChanged.connect(self.update_settings)
        self.box_color_combo.currentIndexChanged.connect(self.update_settings)
        self.text_color_combo.currentIndexChanged.connect(self.update_settings)
        self.translit_checkbox.stateChanged.connect(self.update_settings)
        self.teammates_checkbox.stateChanged.connect(self.update_settings)
        self.teammate_color_combo.currentIndexChanged.connect(self.update_settings)

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
            return

        try:
            self.overlay_thread = QThread()
            self.overlay_worker = OverlayWorker()
            self.overlay_worker.moveToThread(self.overlay_thread)
            self.overlay_worker.errorOccurred.connect(self.on_overlay_error)
            self.overlay_thread.started.connect(self.overlay_worker.run)
            self.overlay_worker.finished.connect(self.overlay_thread.quit)
            self.overlay_worker.finished.connect(self.overlay_worker.deleteLater)
            self.overlay_thread.finished.connect(self.overlay_thread.deleteLater)
            self.overlay_thread.finished.connect(lambda: setattr(self, 'overlay_thread', None))
            self.overlay_thread.start()
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
        except Exception as e:
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
        except RuntimeError as e:
            logger.error("Overlay worker already deleted: %s", e)
        finally:
            self.overlay_worker = None
            self.overlay_thread = None
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    @pyqtSlot()
    def check_updates(self) -> None:
        """
        Checks for updates by querying GitHub. If a newer version is available,
        displays the update details in a message box.
        """
        update_info = check_for_updates(CURRENT_VERSION)
        if "error" in update_info:
            QMessageBox.critical(self, "Update Error", update_info["error"])
        else:
            if update_info.get("update_available"):
                msg = (
                    f"New version available: {update_info['latest_version']}\n\n"
                )
                QMessageBox.information(self, "Update Available", msg)
            else:
                QMessageBox.information(self, "No Updates", f"You are running the latest version: {CURRENT_VERSION}")

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
        keyboard.remove_hotkey("F6")
        keyboard.remove_hotkey("F7")
        overlay.overlay_close()
        event.accept()