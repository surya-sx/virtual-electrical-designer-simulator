"""
Utility Functions Module - Common helpers used throughout the application
Organized by functionality for easy location and reuse
"""

import re
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt


class Validators:
    """Input validation utilities"""
    
    @staticmethod
    def is_valid_identifier(name: str) -> bool:
        """Check if string is valid Python identifier"""
        return name.isidentifier()
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Check if string is valid email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def is_valid_number(value: str, number_type: str = 'float') -> bool:
        """Check if string is valid number
        
        Args:
            value: String to validate
            number_type: 'int', 'float', or 'complex'
        """
        try:
            if number_type == 'int':
                int(value)
            elif number_type == 'float':
                float(value)
            elif number_type == 'complex':
                complex(value)
            else:
                return False
            return True
        except ValueError:
            return False
    
    @staticmethod
    def is_valid_hex_color(color: str) -> bool:
        """Check if string is valid hex color"""
        pattern = r'^#(?:[0-9a-fA-F]{3}){1,2}$'
        return re.match(pattern, color) is not None
    
    @staticmethod
    def validate_range(value: float, min_val: float, max_val: float) -> bool:
        """Check if value is within range"""
        return min_val <= value <= max_val


class Formatters:
    """String and number formatting utilities"""
    
    @staticmethod
    def format_number(value: float, decimal_places: int = 4, scientific: bool = False) -> str:
        """Format number with specified decimal places
        
        Args:
            value: Number to format
            decimal_places: Number of decimal places
            scientific: Use scientific notation
        """
        if scientific:
            return f"{value:.{decimal_places}e}"
        else:
            return f"{value:.{decimal_places}f}"
    
    @staticmethod
    def format_size(size_bytes: int) -> str:
        """Format byte size to human readable"""
        units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
        
        size = float(size_bytes)
        for unit in units:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        
        return f"{size:.2f} PB"
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format duration in seconds to human readable"""
        if seconds < 0.001:
            return f"{seconds*1e6:.2f} µs"
        elif seconds < 1:
            return f"{seconds*1000:.2f} ms"
        elif seconds < 60:
            return f"{seconds:.2f} s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.2f} min"
        else:
            hours = seconds / 3600
            return f"{hours:.2f} h"
    
    @staticmethod
    def format_frequency(hz: float) -> str:
        """Format frequency"""
        if hz < 1000:
            return f"{hz:.2f} Hz"
        elif hz < 1e6:
            return f"{hz/1000:.2f} kHz"
        elif hz < 1e9:
            return f"{hz/1e6:.2f} MHz"
        else:
            return f"{hz/1e9:.2f} GHz"
    
    @staticmethod
    def format_voltage(volts: float) -> str:
        """Format voltage"""
        if abs(volts) < 1:
            return f"{volts*1000:.2f} mV"
        elif abs(volts) < 1000:
            return f"{volts:.2f} V"
        else:
            return f"{volts/1000:.2f} kV"
    
    @staticmethod
    def format_current(amps: float) -> str:
        """Format current"""
        if abs(amps) < 0.001:
            return f"{amps*1e6:.2f} µA"
        elif abs(amps) < 1:
            return f"{amps*1000:.2f} mA"
        else:
            return f"{amps:.2f} A"
    
    @staticmethod
    def format_resistance(ohms: float) -> str:
        """Format resistance"""
        if abs(ohms) < 1000:
            return f"{ohms:.2f} Ω"
        elif abs(ohms) < 1e6:
            return f"{ohms/1000:.2f} kΩ"
        else:
            return f"{ohms/1e6:.2f} MΩ"
    
    @staticmethod
    def format_capacitance(farads: float) -> str:
        """Format capacitance"""
        if abs(farads) < 1e-9:
            return f"{farads*1e12:.2f} pF"
        elif abs(farads) < 1e-6:
            return f"{farads*1e9:.2f} nF"
        elif abs(farads) < 1e-3:
            return f"{farads*1e6:.2f} µF"
        else:
            return f"{farads*1e3:.2f} mF"
    
    @staticmethod
    def format_inductance(henries: float) -> str:
        """Format inductance"""
        if abs(henries) < 1e-6:
            return f"{henries*1e9:.2f} nH"
        elif abs(henries) < 1e-3:
            return f"{henries*1e6:.2f} µH"
        elif abs(henries) < 1:
            return f"{henries*1000:.2f} mH"
        else:
            return f"{henries:.2f} H"


class ThemeManager:
    """Theme and styling management"""
    
    THEMES = {
        'Light': {
            'background': '#ffffff',
            'foreground': '#000000',
            'primary': '#007bff',
            'secondary': '#6c757d',
            'success': '#28a745',
            'danger': '#dc3545',
            'warning': '#ffc107',
            'info': '#17a2b8',
            'border': '#ddd',
            'panel_bg': '#f5f5f5',
        },
        'Dark': {
            'background': '#1e1e1e',
            'foreground': '#e0e0e0',
            'primary': '#0066ff',
            'secondary': '#999999',
            'success': '#00cc00',
            'danger': '#ff3333',
            'warning': '#ffaa00',
            'info': '#00ccff',
            'border': '#444',
            'panel_bg': '#2d2d2d',
        },
        'High Contrast': {
            'background': '#000000',
            'foreground': '#ffffff',
            'primary': '#0000ff',
            'secondary': '#666666',
            'success': '#00ff00',
            'danger': '#ff0000',
            'warning': '#ffff00',
            'info': '#00ffff',
            'border': '#ffffff',
            'panel_bg': '#111111',
        },
    }
    
    @staticmethod
    def get_theme(theme_name: str) -> Dict[str, str]:
        """Get theme dictionary"""
        return ThemeManager.THEMES.get(theme_name, ThemeManager.THEMES['Light'])
    
    @staticmethod
    def get_stylesheet(theme_name: str) -> str:
        """Generate complete stylesheet for theme"""
        theme = ThemeManager.get_theme(theme_name)
        
        stylesheet = f"""
            QMainWindow {{
                background-color: {theme['background']};
                color: {theme['foreground']};
            }}
            QWidget {{
                background-color: {theme['background']};
                color: {theme['foreground']};
            }}
            QTextEdit, QLineEdit {{
                background-color: {theme['panel_bg']};
                border: 1px solid {theme['border']};
                border-radius: 4px;
                padding: 5px;
                color: {theme['foreground']};
            }}
            QPushButton {{
                background-color: {theme['primary']};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {ThemeManager._darken_color(theme['primary'])};
            }}
            QTableWidget, QListWidget, QTreeWidget {{
                background-color: {theme['panel_bg']};
                color: {theme['foreground']};
                border: 1px solid {theme['border']};
            }}
            QHeaderView::section {{
                background-color: {theme['secondary']};
                color: {theme['foreground']};
                border: none;
                padding: 5px;
            }}
        """
        
        return stylesheet
    
    @staticmethod
    def _darken_color(hex_color: str, factor: float = 0.8) -> str:
        """Darken hex color"""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        rgb = tuple(int(c * factor) for c in rgb)
        return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'
    
    @staticmethod
    def color_to_qcolor(hex_color: str) -> QColor:
        """Convert hex color string to QColor"""
        return QColor(hex_color)


class ErrorHandlers:
    """Error handling utilities"""
    
    @staticmethod
    def format_exception(exc: Exception) -> str:
        """Format exception for display"""
        return f"{exc.__class__.__name__}: {str(exc)}"
    
    @staticmethod
    def get_exception_traceback(exc: Exception) -> str:
        """Get full exception traceback"""
        import traceback
        return ''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    
    @staticmethod
    def safe_execute(func, *args, default=None, **kwargs):
        """Safely execute function with error handling"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Error executing {func.__name__}: {e}")
            return default


class FileOperations:
    """File operation utilities"""
    
    @staticmethod
    def load_json(file_path: str) -> Dict:
        """Load JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise IOError(f"Failed to load JSON: {e}")
    
    @staticmethod
    def save_json(file_path: str, data: Dict, pretty: bool = True):
        """Save JSON file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                if pretty:
                    json.dump(data, f, indent=2)
                else:
                    json.dump(data, f)
        except Exception as e:
            raise IOError(f"Failed to save JSON: {e}")
    
    @staticmethod
    def ensure_directory(dir_path: str):
        """Ensure directory exists"""
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def get_file_size(file_path: str) -> int:
        """Get file size in bytes"""
        try:
            return Path(file_path).stat().st_size
        except:
            return 0


class SystemInfo:
    """System information utilities"""
    
    @staticmethod
    def get_platform() -> str:
        """Get OS platform"""
        import sys
        return sys.platform
    
    @staticmethod
    def get_python_version() -> str:
        """Get Python version"""
        import sys
        return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    @staticmethod
    def get_memory_usage() -> Dict[str, float]:
        """Get memory usage statistics"""
        import psutil
        
        try:
            memory = psutil.virtual_memory()
            return {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'percent': memory.percent,
            }
        except:
            return {}
    
    @staticmethod
    def get_cpu_usage() -> float:
        """Get CPU usage percentage"""
        import psutil
        
        try:
            return psutil.cpu_percent(interval=0.1)
        except:
            return 0.0
