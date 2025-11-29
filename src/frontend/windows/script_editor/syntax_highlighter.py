"""
Python Syntax Highlighter - Standalone module for code highlighting
Supports Python keywords, built-ins, strings, comments, numbers
"""

from PySide6.QtGui import QSyntaxHighlighter, QTextDocument, QTextCharFormat, QColor, QFont
from typing import Dict, List, Tuple
import re


class PythonSyntaxHighlighter(QSyntaxHighlighter):
    """Advanced Python syntax highlighter with full language support"""
    
    # Python keywords
    KEYWORDS = [
        'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await',
        'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except',
        'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is',
        'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try',
        'while', 'with', 'yield'
    ]
    
    # Python built-in functions
    BUILTINS = [
        'abs', 'all', 'any', 'ascii', 'bin', 'bool', 'breakpoint', 'bytearray',
        'bytes', 'callable', 'chr', 'classmethod', 'compile', 'complex', 'delattr',
        'dict', 'dir', 'divmod', 'enumerate', 'eval', 'exec', 'filter', 'float',
        'format', 'frozenset', 'getattr', 'globals', 'hasattr', 'hash', 'hex',
        'id', 'input', 'int', 'isinstance', 'issubclass', 'iter', 'len', 'list',
        'locals', 'map', 'max', 'memoryview', 'min', 'next', 'object', 'oct',
        'open', 'ord', 'pow', 'print', 'property', 'range', 'repr', 'reversed',
        'round', 'set', 'setattr', 'slice', 'sorted', 'staticmethod', 'str',
        'sum', 'super', 'tuple', 'type', 'vars', 'zip', '__import__'
    ]
    
    def __init__(self, document: QTextDocument = None):
        super().__init__(document)
        self._init_formats()
    
    def _init_formats(self):
        """Initialize text formatting for different token types"""
        
        # Keywords - bold blue
        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor(33, 66, 200))
        self.keyword_format.setFontWeight(QFont.Bold)
        
        # Built-in functions - brown
        self.builtin_format = QTextCharFormat()
        self.builtin_format.setForeground(QColor(152, 104, 1))
        self.builtin_format.setFontWeight(QFont.Bold)
        
        # Strings - green
        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor(40, 168, 0))
        
        # Comments - gray italic
        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor(128, 128, 128))
        self.comment_format.setFontItalic(True)
        
        # Numbers - red
        self.number_format = QTextCharFormat()
        self.number_format.setForeground(QColor(200, 40, 41))
        
        # Operators - dark gray
        self.operator_format = QTextCharFormat()
        self.operator_format.setForeground(QColor(60, 60, 60))
        self.operator_format.setFontWeight(QFont.Bold)
        
        # Classes - purple
        self.class_format = QTextCharFormat()
        self.class_format.setForeground(QColor(128, 0, 128))
        self.class_format.setFontWeight(QFont.Bold)
        
        # Functions - dark blue
        self.function_format = QTextCharFormat()
        self.function_format.setForeground(QColor(0, 0, 200))
        
        # Decorators - orange
        self.decorator_format = QTextCharFormat()
        self.decorator_format.setForeground(QColor(255, 140, 0))
    
    def highlightBlock(self, text: str):
        """Highlight a single line of text"""
        
        # Handle empty lines
        if not text.strip():
            return
        
        # Highlight comments first (they take precedence)
        self._highlight_comments(text)
        
        # Highlight strings
        self._highlight_strings(text)
        
        # Highlight keywords, builtins, numbers, operators
        self._highlight_other_tokens(text)
    
    def _highlight_comments(self, text: str):
        """Highlight Python comments"""
        comment_index = text.find('#')
        if comment_index >= 0:
            # Check if # is inside a string
            if not self._is_in_string(text, comment_index):
                self.setFormat(comment_index, len(text) - comment_index, self.comment_format)
    
    def _highlight_strings(self, text: str):
        """Highlight Python strings (single, double, triple quotes)"""
        
        # Triple double quotes
        for match in re.finditer(r'""".*?"""', text, re.DOTALL):
            self.setFormat(match.start(), match.end() - match.start(), self.string_format)
        
        # Triple single quotes
        for match in re.finditer(r"'''.*?'''", text, re.DOTALL):
            self.setFormat(match.start(), match.end() - match.start(), self.string_format)
        
        # Double quoted strings
        for match in re.finditer(r'"(?:\\.|[^"\\])*"', text):
            self.setFormat(match.start(), match.end() - match.start(), self.string_format)
        
        # Single quoted strings
        for match in re.finditer(r"'(?:\\.|[^'\\])*'", text):
            self.setFormat(match.start(), match.end() - match.start(), self.string_format)
    
    def _highlight_other_tokens(self, text: str):
        """Highlight keywords, builtins, numbers, operators"""
        
        # Split on whitespace and operators, but keep them
        pattern = r'\b\w+\b|[+\-*/=<>!&|^~(){}[\];:,.]'
        
        for match in re.finditer(pattern, text):
            token = match.group()
            start = match.start()
            length = len(token)
            
            # Skip if inside string or comment
            if self._is_in_string(text, start) or self._is_in_comment(text, start):
                continue
            
            # Check token type
            if token in self.KEYWORDS:
                self.setFormat(start, length, self.keyword_format)
            elif token in self.BUILTINS:
                self.setFormat(start, length, self.builtin_format)
            elif token.isdigit() or self._is_number(token):
                self.setFormat(start, length, self.number_format)
            elif token in '+-*/<>=!&|^~(){}[];:,.':
                self.setFormat(start, length, self.operator_format)
            elif self._is_class_name(text, start):
                self.setFormat(start, length, self.class_format)
            elif self._is_function_name(text, start):
                self.setFormat(start, length, self.function_format)
    
    def _is_in_string(self, text: str, position: int) -> bool:
        """Check if position is inside a string"""
        in_single = False
        in_double = False
        i = 0
        while i < position and i < len(text):
            if text[i] == "'" and (i == 0 or text[i-1] != '\\'):
                in_single = not in_single
            elif text[i] == '"' and (i == 0 or text[i-1] != '\\'):
                in_double = not in_double
            i += 1
        return in_single or in_double
    
    def _is_in_comment(self, text: str, position: int) -> bool:
        """Check if position is inside a comment"""
        comment_pos = text.find('#')
        return comment_pos >= 0 and position > comment_pos
    
    def _is_number(self, token: str) -> bool:
        """Check if token is a number"""
        try:
            float(token)
            return True
        except ValueError:
            return token.endswith(('j', 'J'))  # Complex numbers
    
    def _is_class_name(self, text: str, position: int) -> bool:
        """Check if token is a class definition"""
        # Look for 'class' keyword before this position
        before_text = text[:position].strip()
        return before_text.endswith('class')
    
    def _is_function_name(self, text: str, position: int) -> bool:
        """Check if token is a function definition"""
        # Look for 'def' keyword before this position
        before_text = text[:position].strip()
        return before_text.endswith('def')
