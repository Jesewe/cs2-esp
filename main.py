import sys
from PyQt6.QtWidgets import QApplication
from classes.gui import MainWindow

def main():
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()