<div align="center">
  <img src="src/img/icon.ico" alt="CS2 ESP" width="200" height="200">
  <h1>CS2 ESP</h1>
  <p>An advanced overlay for Counter-Strike 2 that highlights enemy players and teammates with customizable settings. (Works only in windowed or fullscreen windowed) </p>

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
  Renders the player's nickname (with optional transliteration from Cyrillic) above the box.

- **Global Hotkeys:**  
  Use F6 to start and F7 to stop the overlay—these hotkeys work even when the application is not in focus.

- **Customizable Settings:**  
  Adjust overlay settings (such as colors, line thickness, and teammate options) via an intuitive PyQt6 interface.  
  Changes are automatically saved to `%LOCALAPPDATA%\Requests\ItsJesewe\esp_config.json`.

- **Robust Error Handling:**  
  If the target game process (`cs2.exe`) is not found or another error occurs, a clear error message is displayed via a QMessageBox rather than crashing the application.

- **Modular Code Structure:**  
  The project is split into several modules (`utils.py`, `config.py`, `cs2esp.py`, `gui.py`, and `main.py`) for better readability and maintainability.

---

## Installation

**Note:** During testing, I encountered an issue in CS2. When you set a fullscreen resolution (for example, 800x600) and then switch to borderless fullscreen mode, the resolution remains unchanged.

### Prerequisites

- **Python 64-bit:**  
  Make sure you are using a 64-bit version of Python, as the overlay and memory reading libraries require it.

- **PyMeow Module:**  
  PyMeow is a dependency for overlay drawing.
  Visit the [PyMeow GitHub Releases page](https://github.com/qb-0/pyMeow/releases) and download the latest `pyMeow*.zip` release.
  Install PyMeow using pip:
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

Alternatively, download the ready-to-use executable from the [Releases](https://github.com/jesewe/cs2-esp/releases) page. Download the latest version and run the executable directly.

**Note:** This project requires Python version 3.8> but <1.12.5.

---

## Usage

- **Starting the Overlay:**  
  Launch the application.

  - Click the **Start Overlay** button in the GUI or press **F6**.
  - If the game process (`cs2.exe`) is not running, a QMessageBox will display an error message.

- **Stopping the Overlay:**  
  Click the **Stop Overlay** button or press **F7**.

- **Customizing Settings:**  
  Use the GUI controls to adjust settings (such as box color, text color, line thickness, teammate options, etc.).  
  Changes are automatically saved to `%LOCALAPPDATA%\Requests\ItsJesewe\esp_config.json`.

---

## Configuration

The configuration file is stored in:  
`%LOCALAPPDATA%\Requests\ItsJesewe\esp_config.json`

This file is automatically updated with any new keys using a recursive update function when settings are loaded. The file is saved automatically every time you change a setting in the GUI.

---

## Troubleshooting

- **Game Process Not Found:**  
  If you receive an error indicating that the game process is not found (e.g., `pymem.exception.ProcessNotFound`), ensure that **Counter-Strike 2 (cs2.exe)** is running before starting the overlay.

- **Insufficient Privileges:**  
  Global hotkeys and memory reading may require administrative privileges. Try running the application as an administrator if you encounter related issues.

- **Unexpected Crashes:**  
  Make sure all dependencies are installed correctly and that your antivirus or security software is not interfering with the application.

---

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on the [GitHub repository](https://github.com/Jesewe/cs2-esp).

## Disclaimer

This script is for educational purposes only. Using cheats or hacks in online games is against the terms of service of most games and can result in bans or other penalties. Use this script at your own risk.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
