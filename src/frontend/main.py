"""
Main application entry point for Virtual Electrical Designer & Simulator
"""
import sys
import os
from pathlib import Path

# Suppress Qt font warnings before importing
os.environ['QT_DEBUG_PLUGINS'] = '0'
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = ''

# Import and install message handler BEFORE QApplication
from PySide6.QtCore import QtMsgType, qInstallMessageHandler

def qt_message_handler(msg_type, context, message):
    """Suppress Qt font warnings"""
    if "QFont::setPointSize" in message or "QBackingStore" in message or "QPaintDevice" in message:
        return

qInstallMessageHandler(qt_message_handler)

# NOW import QApplication
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

# Add src directory to path
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

from frontend.ui.main_window import MainWindow


def main():
    """Initialize and run the application"""
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("Virtual Electrical Designer & Simulator")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("VED")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
