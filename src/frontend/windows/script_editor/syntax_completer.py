"""
Syntax Completer - Autocomplete suggestions for Python script editor
Provides intelligent code completion based on context
"""

from PySide6.QtWidgets import QCompleter, QListWidget, QListWidgetItem, QAbstractItemView
from PySide6.QtGui import QStandardItemModel, QStandardItem, QFont
from PySide6.QtCore import Qt, QStringListModel, QTimer
from typing import List, Set, Dict, Any, Optional
import re
import keyword
import builtins


class PythonCompleter(QCompleter):
    """Custom completer for Python code with context-aware suggestions"""
    
    # Python keywords
    KEYWORDS = set(keyword.kwlist)
    
    # Python builtins
    BUILTINS = set(dir(builtins))
    
    # Common imports
    COMMON_MODULES = {
        'numpy': ['array', 'zeros', 'ones', 'arange', 'linspace', 'sin', 'cos', 'sqrt'],
        'math': ['pi', 'e', 'sin', 'cos', 'sqrt', 'floor', 'ceil'],
        're': ['match', 'search', 'findall', 'sub', 'split'],
        'os': ['path', 'listdir', 'getcwd', 'chdir', 'mkdir'],
        'sys': ['argv', 'exit', 'path', 'version'],
    }
    
    def __init__(self, editor, parent=None):
        super().__init__(parent)
        self.editor = editor
        self.current_context: Dict[str, Any] = {}
        self.imported_modules: Set[str] = set()
        
        # Setup completer
        self.model = QStringListModel()
        self.setModel(self.model)
        self.setCaseSensitivity(Qt.CaseInsensitive)
        self.setCompletionMode(QCompleter.PopupCompletion)
        self.setMaxVisibleItems(10)
        
        # Popup widget
        self.popup = self.popup()
        self.popup.setFont(QFont("Courier New", 9))
    
    def get_completions(self, text: str, line_text: str, position: int) -> List[str]:
        """Get completion suggestions for current position"""
        completions = set()
        
        # Get current word being typed
        word = self._extract_current_word(text, position)
        
        if not word:
            return []
        
        # Context analysis
        prefix = line_text[:line_text.rfind(word)].strip()
        
        # Check for attribute access (e.g., obj.attr)
        if '.' in word:
            completions.update(self._get_attribute_completions(word, prefix))
        
        # Check for import statements
        elif line_text.strip().startswith('import ') or line_text.strip().startswith('from '):
            completions.update(self._get_import_completions(word))
        
        # Check for function definition
        elif line_text.strip().startswith('def '):
            completions.update(self._get_definition_completions(word))
        
        # Check for class definition
        elif line_text.strip().startswith('class '):
            completions.update(self._get_definition_completions(word))
        
        # General completions
        else:
            completions.update(self._get_general_completions(word))
        
        # Filter by prefix
        if word:
            completions = {c for c in completions if c.lower().startswith(word.lower())}
        
        # Sort and return
        return sorted(list(completions), key=lambda x: (len(x), x))[:50]
    
    def _extract_current_word(self, text: str, position: int) -> str:
        """Extract current word being typed"""
        # Find start of word
        start = position - 1
        while start >= 0 and (text[start].isalnum() or text[start] == '_' or text[start] == '.'):
            start -= 1
        start += 1
        
        # Find end of word
        end = position
        while end < len(text) and (text[end].isalnum() or text[end] == '_' or text[end] == '.'):
            end += 1
        
        return text[start:end]
    
    def _get_keyword_completions(self) -> Set[str]:
        """Get keyword completions"""
        return self.KEYWORDS.copy()
    
    def _get_builtin_completions(self) -> Set[str]:
        """Get builtin completions"""
        return {name for name in self.BUILTINS 
                if not name.startswith('_')}
    
    def _get_context_completions(self) -> Set[str]:
        """Get completions from current context"""
        return set(self.current_context.keys())
    
    def _get_general_completions(self, word: str) -> Set[str]:
        """Get general completions"""
        completions = set()
        
        # Add keywords
        completions.update(self._get_keyword_completions())
        
        # Add builtins
        completions.update(self._get_builtin_completions())
        
        # Add context variables
        completions.update(self._get_context_completions())
        
        return completions
    
    def _get_attribute_completions(self, word: str, prefix: str) -> Set[str]:
        """Get completions for attribute access (obj.attr)"""
        completions = set()
        
        parts = word.split('.')
        obj_name = parts[0]
        attr_prefix = parts[-1] if len(parts) > 1 else ""
        
        # Try to get object from context
        obj = self.current_context.get(obj_name)
        
        if obj is not None:
            try:
                # Get object attributes
                attrs = dir(obj)
                completions.update({attr for attr in attrs 
                                  if not attr.startswith('_')})
            except:
                pass
        
        # Check for module attributes
        if obj_name in self.COMMON_MODULES:
            completions.update(self.COMMON_MODULES[obj_name])
        
        return completions
    
    def _get_import_completions(self, word: str) -> Set[str]:
        """Get completions for import statements"""
        completions = set()
        
        # Add common modules
        completions.update(self.COMMON_MODULES.keys())
        
        # Add standard library modules
        standard_modules = [
            'os', 'sys', 're', 'json', 'csv', 'math', 'random',
            'datetime', 'time', 'collections', 'itertools', 'functools',
            'urllib', 'http', 'email', 'threading', 'multiprocessing',
            'subprocess', 'pickle', 'sqlite3', 'logging', 'unittest',
            'pathlib', 'tempfile', 'shutil', 'glob', 'gzip', 'zipfile'
        ]
        completions.update(standard_modules)
        
        return completions
    
    def _get_definition_completions(self, word: str) -> Set[str]:
        """Get completions for function/class definitions"""
        # Don't provide completions for definition names
        return set()
    
    def update_context(self, context: Dict[str, Any]):
        """Update execution context for completions"""
        self.current_context = context
    
    def analyze_imports(self, code: str):
        """Analyze code for import statements"""
        # Find all import statements
        import_pattern = r'^(?:from\s+(\w+)\s+)?import\s+(.+)$'
        
        for line in code.split('\n'):
            line = line.strip()
            match = re.match(import_pattern, line)
            if match:
                module = match.group(1) or match.group(2).split()[0]
                self.imported_modules.add(module)


class SnippetCompleter:
    """Code snippet suggestions and expansion"""
    
    SNIPPETS = {
        'for': 'for {var} in {iterable}:\n    {pass}',
        'if': 'if {condition}:\n    {pass}',
        'while': 'while {condition}:\n    {pass}',
        'def': 'def {name}({args}):\n    """{docstring}"""\n    {pass}',
        'class': 'class {name}:\n    def __init__(self):\n        {pass}',
        'try': 'try:\n    {pass}\nexcept {exception} as {var}:\n    {pass}',
        'with': 'with {context} as {var}:\n    {pass}',
        'lambda': 'lambda {args}: {expression}',
        'list_comp': '[{expr} for {var} in {iterable}]',
        'dict_comp': '{{{key}: {value} for {var} in {iterable}}}',
        'set_comp': '{{{expr} for {var} in {iterable}}}',
        'gen_exp': '({expr} for {var} in {iterable})',
    }
    
    @staticmethod
    def expand_snippet(snippet_name: str, **kwargs) -> str:
        """Expand snippet with provided variables"""
        template = SnippetCompleter.SNIPPETS.get(snippet_name, "")
        
        if not template:
            return ""
        
        # Replace placeholders
        result = template
        for key, value in kwargs.items():
            result = result.replace(f"{{{key}}}", value)
        
        # Replace remaining placeholders with defaults
        result = re.sub(r'\{(\w+)\}', lambda m: f"{{{m.group(1)}}}", result)
        
        return result
    
    @staticmethod
    def get_snippet_names() -> List[str]:
        """Get list of available snippets"""
        return list(SnippetCompleter.SNIPPETS.keys())


class CompletionHelper:
    """Helper class for completion and suggestion logic"""
    
    @staticmethod
    def get_function_signature(func_obj) -> str:
        """Get function signature string"""
        try:
            import inspect
            sig = inspect.signature(func_obj)
            return f"({sig})"
        except:
            return "(...)"
    
    @staticmethod
    def get_docstring(obj) -> str:
        """Get object docstring"""
        try:
            doc = obj.__doc__
            if doc:
                # Return first line
                return doc.split('\n')[0].strip()
        except:
            pass
        return ""
    
    @staticmethod
    def get_type_hint(obj) -> str:
        """Get type hint string"""
        type_name = type(obj).__name__
        
        if isinstance(obj, (int, float, str, bool)):
            return f": {type_name}"
        elif isinstance(obj, (list, tuple, dict, set)):
            return f": {type_name}"
        elif callable(obj):
            return ": callable"
        else:
            return f": {type_name}"
    
    @staticmethod
    def get_completion_info(name: str, obj: Any) -> Dict[str, str]:
        """Get comprehensive info for completion"""
        info = {
            'name': name,
            'type': type(obj).__name__,
            'signature': CompletionHelper.get_function_signature(obj) if callable(obj) else "",
            'docstring': CompletionHelper.get_docstring(obj),
            'hint': CompletionHelper.get_type_hint(obj),
        }
        
        return info


class SmartCompleter:
    """Smart completion with context awareness"""
    
    def __init__(self):
        self.completer = None
        self.snippet_completer = SnippetCompleter()
        self.helper = CompletionHelper()
        self.context: Dict[str, Any] = {}
    
    def get_suggestions(self, code: str, line: str, position: int) -> List[Dict[str, str]]:
        """Get smart suggestions with metadata"""
        suggestions = []
        
        # Get word at cursor
        word_match = re.search(r'\b(\w*)$', line[:position])
        word = word_match.group(1) if word_match else ""
        
        # Check for snippet
        if word and word in self.snippet_completer.SNIPPETS:
            suggestions.append({
                'type': 'snippet',
                'text': word,
                'display': f"{word} (snippet)",
                'insert': self.snippet_completer.expand_snippet(word)
            })
        
        # Get general completions
        # (would integrate with PythonCompleter here)
        
        return suggestions
