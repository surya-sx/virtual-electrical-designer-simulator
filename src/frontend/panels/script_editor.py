"""
Script Editor Panel - Python code editor with syntax highlighting and execution
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel,
    QSplitter, QListWidget, QListWidgetItem, QPlainTextEdit, QComboBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QSyntaxHighlighter, QTextDocument, QTextCharFormat, QColor
import re


class PythonHighlighter(QSyntaxHighlighter):
    """Simple Python syntax highlighter"""
    
    def __init__(self, document: QTextDocument):
        super().__init__(document)
        
        # Define formats
        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor("#0000ff"))
        self.keyword_format.setFontWeight(700)
        
        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor("#008000"))
        
        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor("#808080"))
        self.comment_format.setFontItalic(True)
        
        self.function_format = QTextCharFormat()
        self.function_format.setForeground(QColor("#a020f0"))
        
        # Python keywords
        self.keywords = [
            "def", "class", "import", "from", "if", "else", "elif", "while", "for",
            "try", "except", "finally", "with", "return", "lambda", "and", "or", "not",
            "in", "is", "True", "False", "None", "self", "print"
        ]
    
    def highlightBlock(self, text: str):
        """Highlight Python syntax"""
        # Comments
        comment_index = text.find("#")
        if comment_index >= 0:
            self.setFormat(comment_index, len(text) - comment_index, self.comment_format)
            text = text[:comment_index]
        
        # Keywords
        for keyword in self.keywords:
            pattern = r"\b" + keyword + r"\b"
            for match in re.finditer(pattern, text):
                self.setFormat(match.start(), match.end() - match.start(), self.keyword_format)
        
        # Strings
        for match in re.finditer(r'"[^"]*"', text):
            self.setFormat(match.start(), match.end() - match.start(), self.string_format)
        for match in re.finditer(r"'[^']*'", text):
            self.setFormat(match.start(), match.end() - match.start(), self.string_format)


class ScriptEditorPanel(QWidget):
    """Panel for editing and running Python scripts with circuit integration"""
    
    # Signals
    script_executed = Signal(dict)  # result dictionary
    script_error = Signal(str)  # error message
    
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Toolbar
        toolbar = QHBoxLayout()
        self.run_button = QPushButton("Run Script")
        self.run_button.clicked.connect(self._run_script)
        toolbar.addWidget(self.run_button)
        
        self.clear_vars_button = QPushButton("Clear Variables")
        self.clear_vars_button.clicked.connect(self._clear_variables)
        toolbar.addWidget(self.clear_vars_button)
        
        self.load_example_combo = QComboBox()
        self.load_example_combo.addItem("Load Example...")
        self.load_example_combo.addItem("Circuit Analysis")
        self.load_example_combo.addItem("Component Listing")
        self.load_example_combo.addItem("Simulation")
        self.load_example_combo.currentTextChanged.connect(self._on_example_selected)
        toolbar.addWidget(self.load_example_combo)
        
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # Main splitter
        splitter = QSplitter(Qt.Vertical)
        
        # Text editor with syntax highlighting
        editor_label = QLabel("Python Code:")
        self.text_editor = QPlainTextEdit()
        self.text_editor.setFont(QFont("Courier", 10))
        self.text_editor.setPlaceholderText(
            "# Enter Python code here\n"
            "# Available objects: circuit, simulation\n"
            "# Functions: print(), on_event(), get_variable(), set_variable()\n"
            "# Libraries: math, np (numpy)\n"
            "\n"
            "# Example:\n"
            "# print('Circuit has', len(circuit.components), 'components')"
        )
        
        # Add syntax highlighter
        self.highlighter = PythonHighlighter(self.text_editor.document())
        
        editor_container = QWidget()
        editor_layout = QVBoxLayout()
        editor_layout.addWidget(editor_label)
        editor_layout.addWidget(self.text_editor)
        editor_container.setLayout(editor_layout)
        
        splitter.addWidget(editor_container)
        
        # Output and variables section
        bottom_container = QWidget()
        bottom_layout = QHBoxLayout()
        
        # Output log
        output_section = QWidget()
        output_layout = QVBoxLayout()
        output_layout.addWidget(QLabel("Output:"))
        self.output_log = QPlainTextEdit()
        self.output_log.setReadOnly(True)
        self.output_log.setMaximumHeight(150)
        output_layout.addWidget(self.output_log)
        output_section.setLayout(output_layout)
        
        # Variables section
        var_section = QWidget()
        var_layout = QVBoxLayout()
        var_layout.addWidget(QLabel("Variables:"))
        self.variables_list = QListWidget()
        var_layout.addWidget(self.variables_list)
        var_section.setLayout(var_layout)
        
        bottom_layout.addWidget(output_section, stretch=2)
        bottom_layout.addWidget(var_section, stretch=1)
        bottom_container.setLayout(bottom_layout)
        
        splitter.addWidget(bottom_container)
        splitter.setSizes([300, 150])
        
        layout.addWidget(splitter, stretch=1)
        
        # Runtime reference
        self.script_runtime = None
    
    def set_script_runtime(self, runtime):
        """Set the script runtime reference"""
        self.script_runtime = runtime
    
    def _run_script(self):
        """Execute the script"""
        if not self.script_runtime:
            self.output_log.setPlainText("Error: Script runtime not available")
            return
        
        code = self.text_editor.toPlainText()
        self.output_log.clear()
        
        # Execute script
        result = self.script_runtime.execute_script(code)
        
        # Display output
        self.output_log.setPlainText(result["output"])
        
        if result["error"]:
            self.output_log.appendPlainText(f"\nERROR: {result['error']}")
        
        # Update variables display
        self._update_variables_display(result["variables"])
        
        # Emit signal
        self.script_executed.emit(result)
    
    def _clear_variables(self):
        """Clear all user variables"""
        if self.script_runtime:
            self.script_runtime.clear_variables()
            self.variables_list.clear()
    
    def _update_variables_display(self, variables: dict):
        """Update variables list display"""
        self.variables_list.clear()
        for name, value in variables.items():
            try:
                value_str = str(value)[:50]  # Limit display length
                item_text = f"{name} = {value_str}"
            except:
                item_text = f"{name} = <object>"
            
            item = QListWidgetItem(item_text)
            self.variables_list.addItem(item)
    
    def _on_example_selected(self, example_name: str):
        """Load code example"""
        if example_name == "Circuit Analysis":
            code = '''# List all components in the circuit
if circuit:
    components = circuit.components
    print(f"Total components: {len(components)}")
    for comp_id, comp in components.items():
        print(f"  {comp.name}: {comp.comp_type} at ({comp.x}, {comp.y})")
else:
    print("No circuit loaded")'''
        
        elif example_name == "Component Listing":
            code = '''# Count component types
if circuit:
    type_count = {}
    for comp in circuit.components.values():
        comp_type = comp.comp_type
        type_count[comp_type] = type_count.get(comp_type, 0) + 1
    
    print("Component summary:")
    for comp_type, count in type_count.items():
        print(f"  {comp_type}: {count}")
else:
    print("No circuit loaded")'''
        
        elif example_name == "Simulation":
            code = '''# Check simulation configuration
if simulation:
    print("Simulation modes available:")
    print("  - dc (DC operating point)")
    print("  - ac (AC frequency sweep)")
    print("  - transient (Time-domain)")
    print("  - parametric (Component sweep)")
    print("  - monte_carlo (Tolerance analysis)")
else:
    print("No simulation engine available")'''
        
        else:
            return
        
        self.text_editor.setPlainText(code)
        self.load_example_combo.setCurrentIndex(0)
