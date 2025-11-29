"""
Application Configuration Module - Centralized settings and constants
Organized by configuration type for easy customization

Components:
- defaults.py: Default application settings
- themes.py: Theme configurations
- constants.py: Application constants
- settings.py: Runtime settings management
"""

# Application Constants
APP_NAME = "Virtual Electrical Designer"
APP_VERSION = "1.0.0"
APP_AUTHOR = "ElectricalCAD Development Team"
APP_DESCRIPTION = "Comprehensive desktop application for designing and simulating electrical circuits"

# Window Constants
DEFAULT_WINDOW_WIDTH = 1200
DEFAULT_WINDOW_HEIGHT = 800
MIN_WINDOW_WIDTH = 800
MIN_WINDOW_HEIGHT = 600

# File Constants
APP_CONFIG_DIR = "~/.ved"
APP_DATA_DIR = "~/.ved/data"
APP_PROJECTS_DIR = "~/.ved/projects"
APP_LIBRARIES_DIR = "~/.ved/libraries"

# File Extensions
PROJECT_EXTENSION = ".vedproj"
CIRCUIT_EXTENSION = ".vedcir"
LIBRARY_EXTENSION = ".vedlib"
SCRIPT_EXTENSION = ".ved.py"

# Default Settings
DEFAULT_SETTINGS = {
    'theme': 'Light',
    'font_size': 11,
    'auto_save': True,
    'auto_save_interval': 30,  # seconds
    'grid_size': 20,  # pixels
    'snap_to_grid': True,
    'show_grid': True,
    'show_rulers': False,
    'line_width': 2,
    'selection_color': '#0066ff',
    'highlight_color': '#ffff00',
    'background_color': '#ffffff',
}

# UI Constants
TOOLBAR_ICON_SIZE = 24  # pixels
PANEL_MIN_WIDTH = 200  # pixels
PANEL_MAX_WIDTH = 600  # pixels

# Simulation Constants
DEFAULT_SOLVER = 'DC'
DEFAULT_TIME_STEP = 0.001  # seconds
DEFAULT_END_TIME = 1.0  # seconds
MAX_CIRCUIT_NODES = 10000
MAX_CIRCUIT_ELEMENTS = 50000

# Component Library Constants
MAX_COMPONENTS_PER_CATEGORY = 1000
COMPONENT_CACHE_SIZE = 100  # number of components

# Script Constants
SCRIPT_TIMEOUT = 60  # seconds
SCRIPT_MAX_OUTPUT = 1000000  # bytes
SCRIPT_HISTORY_SIZE = 100  # number of scripts

# Export Constants
EXPORT_DPI = 300  # dots per inch
EXPORT_FORMATS = ['PDF', 'PNG', 'SVG', 'CSV', 'JSON']
MAX_EXPORT_SIZE = 100  # MB

# Performance Constants
REFRESH_RATE = 60  # FPS
CACHE_SIZE = 100  # MB
WORKER_THREADS = 4

# Keyboard Shortcuts
SHORTCUTS = {
    'new': 'Ctrl+N',
    'open': 'Ctrl+O',
    'save': 'Ctrl+S',
    'save_as': 'Ctrl+Shift+S',
    'close': 'Ctrl+W',
    'exit': 'Ctrl+Q',
    'undo': 'Ctrl+Z',
    'redo': 'Ctrl+Y',
    'cut': 'Ctrl+X',
    'copy': 'Ctrl+C',
    'paste': 'Ctrl+V',
    'select_all': 'Ctrl+A',
    'delete': 'Delete',
    'duplicate': 'Ctrl+D',
    'run': 'F5',
    'debug': 'F9',
    'stop': 'F8',
    'zoom_in': 'Ctrl++',
    'zoom_out': 'Ctrl+-',
    'fit_all': 'Ctrl+0',
}

# Logging Configuration
LOG_LEVEL = 'INFO'
LOG_FILE = '~/.ved/app.log'
LOG_MAX_SIZE = 10  # MB
LOG_BACKUP_COUNT = 5

# Database Configuration
USE_DATABASE = False
DATABASE_PATH = '~/.ved/app.db'

# Network Configuration
CHECK_UPDATES = True
UPDATE_CHECK_INTERVAL = 86400  # 24 hours in seconds
TELEMETRY_ENABLED = False

# Advanced Options
ENABLE_EXPERIMENTAL_FEATURES = False
DEBUG_MODE = False
VERBOSE_OUTPUT = False
