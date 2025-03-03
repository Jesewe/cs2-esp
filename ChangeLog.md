### Summary

- **Modularization:** The project is divided into logical modules.

- **Configuration Management:** The settings are loaded from and saved to `%LOCALAPPDATA%\Requests\ItsJesewe\esp_config.json`. The `_update_config` class method ensures that missing keys are added.

- **Error Handling:** If the target game process (`cs2.exe`) is not found or another error occurs during initialization, an error signal is emitted. The GUI then displays a QMessageBox instead of crashing.

- **Global Hotkeys:** The `keyboard` module registers F6 and F7 as global hotkeys to start and stop the overlay even when the application is not active.

- **Enhanced Drawing:** The overlay displays the nickname above the box and a vertical health progress bar whose color changes with health.
