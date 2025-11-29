"""
Default Application Settings
Can be overridden by user configuration
"""

from typing import Dict, Any
from pathlib import Path


class DefaultSettings:
    """Default application settings"""
    
    # UI Settings
    UI_SETTINGS = {
        'theme': 'Light',
        'font_name': 'Segoe UI',
        'font_size': 11,
        'window_maximized': False,
        'window_width': 1200,
        'window_height': 800,
        'show_toolbar': True,
        'show_statusbar': True,
        'show_panels': True,
        'panel_layout': 'right',  # left, right, bottom
        'recent_files_count': 10,
    }
    
    # Editor Settings
    EDITOR_SETTINGS = {
        'auto_save': True,
        'auto_save_interval': 30,  # seconds
        'show_line_numbers': True,
        'show_whitespace': False,
        'use_tabs': False,
        'tab_width': 4,
        'highlight_matching_braces': True,
        'code_folding': True,
        'minimap': True,
        'word_wrap': False,
        'indent_guides': True,
    }
    
    # Canvas/Drawing Settings
    CANVAS_SETTINGS = {
        'grid_size': 20,  # pixels
        'snap_to_grid': True,
        'show_grid': True,
        'show_rulers': False,
        'grid_color': '#e0e0e0',
        'background_color': '#ffffff',
        'line_width': 2,
        'component_size': 40,  # default component size
        'selection_color': '#0066ff',
        'highlight_color': '#ffff00',
    }
    
    # Simulation Settings
    SIMULATION_SETTINGS = {
        'default_solver': 'DC',  # DC, AC, Transient
        'time_step': 0.001,  # seconds
        'end_time': 1.0,  # seconds
        'max_iterations': 1000,
        'tolerance': 1e-6,
        'use_parallel': True,
        'num_threads': 4,
    }
    
    # Script Settings
    SCRIPT_SETTINGS = {
        'timeout': 60,  # seconds
        'max_output': 1000000,  # bytes
        'history_size': 100,
        'syntax_highlighting': True,
        'auto_complete': True,
        'auto_indent': True,
        'show_execution_time': True,
    }
    
    # Library Settings
    LIBRARY_SETTINGS = {
        'default_library': 'Standard',
        'cache_components': True,
        'cache_size': 100,
        'auto_load_libraries': True,
        'show_deprecated': False,
    }
    
    # Export Settings
    EXPORT_SETTINGS = {
        'default_format': 'PNG',
        'dpi': 300,
        'quality': 95,
        'include_background': True,
        'auto_resize': True,
    }
    
    # Advanced Settings
    ADVANCED_SETTINGS = {
        'enable_experimental': False,
        'debug_mode': False,
        'verbose_output': False,
        'check_updates': True,
        'telemetry': False,
        'log_level': 'INFO',
    }
    
    @classmethod
    def get_all(cls) -> Dict[str, Dict[str, Any]]:
        """Get all default settings"""
        return {
            'ui': cls.UI_SETTINGS,
            'editor': cls.EDITOR_SETTINGS,
            'canvas': cls.CANVAS_SETTINGS,
            'simulation': cls.SIMULATION_SETTINGS,
            'script': cls.SCRIPT_SETTINGS,
            'library': cls.LIBRARY_SETTINGS,
            'export': cls.EXPORT_SETTINGS,
            'advanced': cls.ADVANCED_SETTINGS,
        }
    
    @classmethod
    def get_by_category(cls, category: str) -> Dict[str, Any]:
        """Get defaults for specific category"""
        all_settings = cls.get_all()
        return all_settings.get(category, {})
    
    @classmethod
    def get_setting(cls, category: str, key: str, default=None):
        """Get single setting value"""
        settings = cls.get_by_category(category)
        return settings.get(key, default)


class SettingsManager:
    """Manage application settings with persistence"""
    
    def __init__(self, config_dir: str = None):
        self.config_dir = Path(config_dir or "~/.ved").expanduser()
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "settings.json"
        self.settings = DefaultSettings.get_all().copy()
        self._load_settings()
    
    def _load_settings(self):
        """Load settings from file"""
        import json
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded = json.load(f)
                    # Merge with defaults
                    for category, settings in loaded.items():
                        if category in self.settings:
                            self.settings[category].update(settings)
            except Exception as e:
                print(f"Failed to load settings: {e}")
    
    def save_settings(self):
        """Save settings to file"""
        import json
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Failed to save settings: {e}")
    
    def get(self, category: str, key: str, default=None):
        """Get setting value"""
        if category in self.settings:
            return self.settings[category].get(key, default)
        return default
    
    def set(self, category: str, key: str, value):
        """Set setting value"""
        if category not in self.settings:
            self.settings[category] = {}
        self.settings[category][key] = value
    
    def get_all_in_category(self, category: str) -> Dict[str, Any]:
        """Get all settings in category"""
        return self.settings.get(category, {}).copy()
    
    def reset_to_defaults(self, category: str = None):
        """Reset settings to defaults"""
        if category:
            self.settings[category] = DefaultSettings.get_by_category(category).copy()
        else:
            self.settings = DefaultSettings.get_all().copy()
    
    def export_settings(self, file_path: str):
        """Export settings to file"""
        import json
        
        try:
            with open(file_path, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Failed to export settings: {e}")
    
    def import_settings(self, file_path: str):
        """Import settings from file"""
        import json
        
        try:
            with open(file_path, 'r') as f:
                loaded = json.load(f)
                for category, settings in loaded.items():
                    if category in self.settings:
                        self.settings[category].update(settings)
        except Exception as e:
            print(f"Failed to import settings: {e}")
