"""
Script Editor Module - Comprehensive Python script editing and execution
Sub-modules organized by responsibility for easy maintenance and testing

Components:
- enhanced_script_editor.py: Main window with UI
- syntax_highlighter.py: Python syntax highlighting
- script_engine.py: Execution engine with debugging
- syntax_completer.py: Autocomplete and snippets
- variable_explorer.py: Variable inspection and watching
"""

from .enhanced_script_editor import EnhancedScriptEditorWindow
from .syntax_highlighter import PythonSyntaxHighlighter
from .syntax_completer import PythonCompleter, SnippetCompleter, CompletionHelper, SmartCompleter
from .variable_explorer import VariableExplorer

__all__ = [
    'EnhancedScriptEditorWindow',
    'PythonSyntaxHighlighter',
    'PythonCompleter',
    'SnippetCompleter',
    'CompletionHelper',
    'SmartCompleter',
    'VariableExplorer',
]
