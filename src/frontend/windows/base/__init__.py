"""
Base Windows Module - Shared base classes for window types
Provides common functionality to avoid code duplication

Components:
- base_window.py: BaseWindow, FloatingToolWindow, DockableWindow, TabWindow, WindowManager
"""

from .base_window import BaseWindow, FloatingToolWindow, DockableWindow, TabWindow, WindowManager

__all__ = [
    'BaseWindow',
    'FloatingToolWindow',
    'DockableWindow',
    'TabWindow',
    'WindowManager',
]
