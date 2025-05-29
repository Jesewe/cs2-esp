# Contributing to CS2 ESP

Thank you for your interest in contributing to the CS2 ESP project. This guide provides the necessary steps to begin contributing, from setting up your development environment to submitting your first pull request.

## Table of Contents

* [Code of Conduct](#code-of-conduct)
* [Getting Started](#getting-started)
* [Development Setup](#development-setup)
* [Coding Standards](#coding-standards)
* [Submitting Issues](#submitting-issues)
* [Pull Request Process](#pull-request-process)
* [Feature Requests and Feedback](#feature-requests-and-feedback)

---

## Code of Conduct

By contributing to this project, you agree to adhere to the [Code of Conduct](CODE_OF_CONDUCT.md). Please act respectfully, remain constructive, and collaborate positively with others.

## Getting Started

1. **Fork the Repository**: Create a personal fork on GitHub.
2. **Clone Your Fork**:

   ```bash
   git clone https://github.com/your-username/cs2-esp.git
   cd cs2-esp
   ```
3. **Add Upstream Remote**:

   ```bash
   git remote add upstream https://github.com/Jesewe/cs2-esp.git
   ```

## Development Setup

1. **Install Python**: Ensure Python version **>= 3.8 and < 3.12.5** is installed (64-bit required).
2. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

   In addition, install the `pyMeow` module:

   ```bash
   pip install path/to/pyMeow*.zip
   ```
3. **Run the Application**:

   ```bash
   python main.py
   ```

### Testing Changes

* Ensure **Counter-Strike 2** (`cs2.exe`) is running before testing.
* Start the overlay via the GUI or **F6**, and stop it with **F7**.
* Debug logs and configuration changes are saved in:
  `%LOCALAPPDATA%\Requests\ItsJesewe\esp_config.json`

## Coding Standards

Please adhere to the following guidelines for consistency and maintainability:

* **PEP 8**: Follow the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide.
* **Naming**: Use meaningful, descriptive names for variables, classes, and functions.
* **Modular Design**: Follow the existing modular structure (`utils.py`, `config.py`, `cs2esp.py`, `gui.py`, `main.py`).
* **Comments**: Comment complex logic clearly to enhance readability.
* **Error Handling**: Handle exceptions gracefully and provide user-friendly error messages.

### GUI Development

* **DearPyGui**: Use `DearPyGui` for all UI elements. Ensure consistent styling with existing components.
* **Persistent Settings**: Ensure any new settings are automatically saved to and loaded from the configuration file.

## Submitting Issues

When reporting issues, please:

1. Check for existing reports to avoid duplicates.
2. Include a clear description, steps to reproduce, expected behavior, and relevant logs or screenshots.

## Pull Request Process

1. **Create a Branch**:

   ```bash
   git checkout -b feature/your-feature-name
   ```
2. **Commit Your Changes**:

   ```bash
   git commit -m "Brief summary of your changes"
   ```
3. **Push to Your Fork**:

   ```bash
   git push origin feature/your-feature-name
   ```
4. **Open a Pull Request**:
   Submit your pull request via GitHub and include:

   * Purpose of your changes
   * Potential effects on existing functionality
   * Description of how you tested the changes

### Review Process

* All pull requests are subject to code review.
* Please respond promptly to feedback and requested changes.

## Feature Requests and Feedback

We welcome suggestions and new feature ideas. Please open an issue labeled **Feature Request** in the [Issues tab](https://github.com/Jesewe/cs2-esp/issues).

Thank you for helping improve CS2 ESP!
