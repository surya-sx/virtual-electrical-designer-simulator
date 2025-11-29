"""Windows - Separate application windows"""

from .script_editor_window import ScriptEditorWindow, PythonSyntaxHighlighter
from .waveform_viewer_window import WaveformViewerWindow, WaveformData

__all__ = [
    "ScriptEditorWindow",
    "PythonSyntaxHighlighter",
    "WaveformViewerWindow",
    "WaveformData",
]
