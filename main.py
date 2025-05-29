import sys
import logging

from classes.gui import MainWindow

def main() -> None:
    """Main entry point for the CS2 ESP application."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Create and show the main window
        window = MainWindow()
        window.show()
        
        # Start the application loop
        window.run()
        
    except KeyboardInterrupt:
        print("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logging.error("Fatal error: %s", e)
        sys.exit(1)

if __name__ == "__main__":
    main()