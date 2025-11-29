"""
Waveform Viewer Module - Interactive circuit waveform display and analysis
Sub-modules organized for maintainability and extensibility

Components:
- waveform_base.py: Core waveform data structures and analysis
- waveform_viewer_window.py: Main viewer window with UI
- Extensible design for adding new analysis and processing features
"""

from .waveform_base import WaveformData, WaveformPlotter, WaveformAnalyzer, WaveformProcessor
from .waveform_viewer_window import EnhancedWaveformViewerWindow, PyQtGraphPlotter

__all__ = [
    'WaveformData',
    'WaveformPlotter',
    'WaveformAnalyzer',
    'WaveformProcessor',
    'EnhancedWaveformViewerWindow',
    'PyQtGraphPlotter',
]
