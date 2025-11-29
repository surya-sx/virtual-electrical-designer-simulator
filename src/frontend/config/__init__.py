"""
Application Configuration Module - Centralized settings and constants
Easy access to all configuration throughout the application

Components:
- constants.py: Application-wide constants
- defaults.py: Default settings and SettingsManager
- themes.py: Theme definitions (future)
"""

from .constants import (
    APP_NAME,
    APP_VERSION,
    APP_AUTHOR,
    APP_DESCRIPTION,
    DEFAULT_SETTINGS,
    SHORTCUTS,
    LOG_LEVEL,
    DEBUG_MODE,
)

from .defaults import DefaultSettings, SettingsManager

__all__ = [
    'APP_NAME',
    'APP_VERSION',
    'APP_AUTHOR',
    'APP_DESCRIPTION',
    'DEFAULT_SETTINGS',
    'SHORTCUTS',
    'LOG_LEVEL',
    'DEBUG_MODE',
    'DefaultSettings',
    'SettingsManager',
]

# Global settings manager instance
_settings_manager = None


def get_settings_manager() -> SettingsManager:
    """Get global settings manager instance"""
    global _settings_manager
    if _settings_manager is None:
        _settings_manager = SettingsManager()
    return _settings_manager


def get_setting(category: str, key: str, default=None):
    """Get setting from global manager"""
    return get_settings_manager().get(category, key, default)


def set_setting(category: str, key: str, value):
    """Set setting in global manager"""
    get_settings_manager().set(category, key, value)


def save_settings():
    """Save settings to disk"""
    get_settings_manager().save_settings()
