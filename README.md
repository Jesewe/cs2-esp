<div align="center">
  <img src="src/img/icon.ico" alt="CS2 ESP" width="200" height="200">
  <h1>CS2 ESP</h1>
  <p>An advanced overlay for Counter-Strike 2 that highlights enemy players and teammates with customizable settings. (Works only in windowed or fullscreen windowed)</p>

![Downloads](https://img.shields.io/github/downloads/jesewe/cs2-esp/total?style=for-the-badge&logo=github&color=D5006D)
![Platforms](https://img.shields.io/badge/platform-Windows-blue?style=for-the-badge&logo=windows&color=D5006D)
![License](https://img.shields.io/github/license/jesewe/cs2-esp?style=for-the-badge&color=D5006D)

<a href="#features"><strong>Features</strong></a> •
<a href="#installation"><strong>Installation</strong></a> •
<a href="#usage"><strong>Usage</strong></a> •
<a href="#configuration"><strong>Configuration</strong></a> •
<a href="#troubleshooting"><strong>Troubleshooting</strong></a> •
<a href="#contributing"><strong>Contributing</strong></a>

</div>

---

## Features

- **Dynamic ESP Overlay:**  
  Displays boxes around enemy players and (optionally) teammates, with a vertical health bar that changes color based on health level (red for 0–20%, yellow for 20–50%, green for 50–100%).

- **Custom Nickname Display:**  
  Renders the player's nickname (with optional transliteration from Cyrillic to Latin) above the box.

- **Snaplines:**  
  Optionally draws lines from the screen center to enemy positions, customizable in color.

- **Minimap Overlay:**  
  Provides a top-left positioned minimap showing entity positions for enhanced spatial awareness, with adjustable size.

- **Global Hotkeys:**  
  Use **F6** to start and **F7** to stop the overlay—these hotkeys function globally, even when the application is not in focus.

- **Customizable Settings:**  
  Adjust overlay settings (e.g., colors, line thickness, teammate visibility, minimap size, and FPS optimization) via an intuitive **DearPyGui** interface.  
  Changes are automatically saved to `%LOCALAPPDATA%\Requests\ItsJesewe\esp_config.json`.

- **Automatic Update Check:**  
  Checks for updates from the GitHub repository on startup and notifies you if a new version is available.

- **Robust Error Handling:**  
  If the game process (`cs2.exe`) is not found or an error occurs, a popup displays a clear error message instead of crashing.

- **Modular Code Structure:**  
  Organized into modules (`utils.py`, `config.py`, `cs2esp.py`, `gui.py`, and `main.py`) for improved readability and maintainability.

---

## Installation

### Prerequisites

- **Python 64-bit:**  
  A 64-bit version of Python is required for the overlay and memory-reading libraries.

- **PyMeow Module:**  
  PyMeow is essential for rendering the overlay.  
  Download the latest `pyMeow*.zip` from the [PyMeow GitHub Releases page](https://github.com/qb-0/pyMeow/releases) and install it:

  ```bash
  pip install pyMeow*.zip
  ```

### Option 1: Clone the Repository

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/Jesewe/cs2-esp.git
   cd cs2-esp
   ```

2. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Script:**
   ```bash
   python main.py
   ```

### Option 2: Download Pre-Built Executable

Download the latest pre-built executable from the [Releases](https://github.com/jesewe/cs2-esp/releases/latest) page and run it directly.

**Note:** This project requires Python version >= 3.8 and < 3.12.5.

---

## Usage

- **Starting the Overlay:**  
  Launch the application:

  - Click the **Start Overlay** button in the GUI or press **F6**.
  - If `cs2.exe` is not running, a popup will display an error message.

- **Stopping the Overlay:**  
  Click the **Stop Overlay** button or press **F7**.

- **Customizing Settings:**  
  Use the DearPyGui interface to tweak settings (e.g., box color, text color, line thickness, teammate visibility, minimap size).  
  Changes are automatically saved to `%LOCALAPPDATA%\Requests\ItsJesewe\esp_config.json`.

---

## Configuration

The configuration file is located at:  
`%LOCALAPPDATA%\Requests\ItsJesewe\esp_config.json`

- Automatically created and updated with new settings keys on load.
- Saved whenever settings are modified in the GUI.

---

## Troubleshooting

- **Game Process Not Found:**  
  If you see `pymem.exception.ProcessNotFound`, ensure **Counter-Strike 2 (cs2.exe)** is running before starting the overlay.

- **Insufficient Privileges:**  
  Global hotkeys and memory reading may need administrative rights. Run the application as an administrator if issues arise.

- **Unexpected Crashes:**  
  Verify all dependencies are correctly installed and check for interference from antivirus or security software.

---

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on the [GitHub repository](https://github.com/Jesewe/cs2-esp).

## Disclaimer

This script is for educational purposes only. Using cheats or hacks in online games is against the terms of service of most games and can result in bans or other penalties. Use this script at your own risk.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
