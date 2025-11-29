"""
Base Window Classes - Shared functionality for all windows
Reduces code duplication and ensures consistency
"""

from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent, QIcon
from typing import Optional, Dict, Any


class BaseWindow(QMainWindow):
    """Base class for all application windows with common functionality"""
    
    def __init__(self, title: str = "Window", width: int = 800, height: int = 600, parent=None):
        """
        Initialize base window
        
        Args:
            title: Window title
            width: Window width
            height: Window height
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setGeometry(100, 100, width, height)
        
        # Track unsaved changes
        self.has_unsaved_changes = False
        
        # Settings
        self.settings: Dict[str, Any] = {}
        
        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_layout = QVBoxLayout(self.central_widget)
        self.central_layout.setContentsMargins(0, 0, 0, 0)
    
    def set_title(self, title: str, unsaved: bool = False):
        """Set window title with unsaved indicator"""
        if unsaved:
            self.setWindowTitle(f"{title} *")
        else:
            self.setWindowTitle(title)
    
    def mark_unsaved(self):
        """Mark window as having unsaved changes"""
        self.has_unsaved_changes = True
    
    def mark_saved(self):
        """Mark window as saved"""
        self.has_unsaved_changes = False
    
    def ask_save_changes(self) -> int:
        """
        Ask user if they want to save changes
        
        Returns:
            QMessageBox response code
        """
        if not self.has_unsaved_changes:
            return QMessageBox.No
        
        reply = QMessageBox.question(
            self,
            "Unsaved Changes",
            "Do you want to save your changes?",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
        )
        
        return reply
    
    def save_settings(self):
        """Save window settings (override in subclasses)"""
        pass
    
    def load_settings(self):
        """Load window settings (override in subclasses)"""
        pass
    
    def apply_theme(self, theme: str):
        """Apply theme to window (override in subclasses)"""
        pass
    
    def closeEvent(self, event: QCloseEvent):
        """Handle window close"""
        if self.has_unsaved_changes:
            reply = self.ask_save_changes()
            
            if reply == QMessageBox.Save:
                self.save_settings()
            elif reply == QMessageBox.Cancel:
                event.ignore()
                return
        
        event.accept()


class FloatingToolWindow(BaseWindow):
    """Base class for floating tool windows"""
    
    def __init__(self, title: str = "Tool", width: int = 400, height: int = 600, parent=None):
        super().__init__(title, width, height, parent)
        
        # Set window flags for floating
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        
        # Apply floating window style
        self._apply_floating_style()
    
    def _apply_floating_style(self):
        """Apply style for floating window"""
        self.setStyleSheet("""
            QMainWindow {
                background: #ffffff;
                border: 1px solid #999;
            }
            QToolBar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                          stop:0 #ffffff, stop:1 #f0f0f0);
                border-bottom: 1px solid #bbb;
            }
        """)


class DockableWindow(BaseWindow):
    """Base class for dockable windows that can be embedded"""
    
    def __init__(self, title: str = "Panel", width: int = 300, height: int = 400, parent=None):
        super().__init__(title, width, height, parent)
        self.is_docked = False
    
    def set_docked(self, docked: bool):
        """Set docked state"""
        self.is_docked = docked
        
        if docked:
            self.setWindowFlags(Qt.Widget)
        else:
            self.setWindowFlags(Qt.Window)


class TabWindow(BaseWindow):
    """Base class for multi-tab windows"""
    
    def __init__(self, title: str = "Tabs", width: int = 1000, height: int = 700, parent=None):
        super().__init__(title, width, height, parent)
        
        # Import here to avoid circular imports
        from PySide6.QtWidgets import QTabWidget
        
        self.tabs = QTabWidget()
        self.central_layout.addWidget(self.tabs)
    
    def add_tab(self, widget: QWidget, title: str, icon: Optional[QIcon] = None):
        """Add tab"""
        if icon:
            self.tabs.addTab(widget, icon, title)
        else:
            self.tabs.addTab(widget, title)
    
    def remove_tab(self, index: int):
        """Remove tab by index"""
        self.tabs.removeTab(index)
    
    def get_current_tab(self) -> QWidget:
        """Get current tab widget"""
        return self.tabs.currentWidget()


class WindowManager:
    """Manage application windows"""
    
    def __init__(self):
        self.windows: Dict[str, BaseWindow] = {}
    
    def register_window(self, name: str, window: BaseWindow):
        """Register window"""
        self.windows[name] = window
    
    def unregister_window(self, name: str):
        """Unregister window"""
        if name in self.windows:
            del self.windows[name]
    
    def get_window(self, name: str) -> Optional[BaseWindow]:
        """Get window by name"""
        return self.windows.get(name)
    
    def activate_window(self, name: str):
        """Activate window by name"""
        window = self.get_window(name)
        if window:
            window.raise_()
            window.activateWindow()
    
    def close_all_windows(self):
        """Close all managed windows"""
        for window in list(self.windows.values()):
            window.close()
    
    def save_all_settings(self):
        """Save settings for all windows"""
        for window in self.windows.values():
            window.save_settings()
    
    def load_all_settings(self):
        """Load settings for all windows"""
        for window in self.windows.values():
            window.load_settings()
    
    def apply_theme_to_all(self, theme: str):
        """Apply theme to all windows"""
        for window in self.windows.values():
            window.apply_theme(theme)
