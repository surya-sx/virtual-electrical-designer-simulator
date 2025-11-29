"""
Enhanced Script Editor Window - Main UI for script editing and execution
Features: Syntax highlighting, autocomplete, debugging, variable inspector
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QMessageBox, QFileDialog,
    QSplitter, QStatusBar, QToolBar, QTabWidget, QListWidget,
    QListWidgetItem, QLineEdit, QComboBox, QSpinBox, QCheckBox,
    QProgressBar
)
from PySide6.QtGui import QFont, QIcon, QTextCursor, QColor
from PySide6.QtCore import Qt, Signal, QSize, QTimer, QRect
from typing import Dict, Any, Optional
import json
import os
from pathlib import Path

from .syntax_highlighter import PythonSyntaxHighlighter
from src.backend.scripting.script_engine import ScriptExecutionThread, ScriptDebugger, VariableInspector


class EnhancedScriptEditorWindow(QMainWindow):
    """Enhanced script editor with debugging, profiling, and variable inspection"""
    
    # Signals
    script_executed = Signal(str)  # script output
    script_error = Signal(str)  # script error
    
    def __init__(self, script_name: str = "Script", parent=None, circuit_context: Dict = None):
        super().__init__(parent)
        self.script_name = script_name
        self.circuit_context = circuit_context or {}
        self.current_file: Optional[Path] = None
        self.execution_thread: Optional[ScriptExecutionThread] = None
        self.is_running = False
        self.has_unsaved_changes = False
        
        # Debugger
        self.debugger = ScriptDebugger()
        
        # Inspector
        self.inspector = VariableInspector()
        
        # Settings
        self.settings = self._load_settings()
        
        self.setWindowTitle(f"Script Editor - {script_name}")
        self.setWindowIcon(QIcon.fromTheme("text-editor"))
        self.setGeometry(100, 100, 1200, 800)
        
        self._setup_ui()
        self._apply_styles()
        self.show()
    
    def _setup_ui(self):
        """Setup UI components"""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Toolbar
        self._setup_toolbar()
        
        # Main splitter (editor and panels)
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side: Editor
        left_widget = self._create_editor_panel()
        splitter.addWidget(left_widget)
        
        # Right side: Tabs (Output, Variables, Breakpoints)
        self.right_tabs = QTabWidget()
        
        # Output tab
        self.output_panel = self._create_output_panel()
        self.right_tabs.addTab(self.output_panel, "Output")
        
        # Variables tab
        self.variables_panel = self._create_variables_panel()
        self.right_tabs.addTab(self.variables_panel, "Variables")
        
        # Breakpoints tab
        self.breakpoints_panel = self._create_breakpoints_panel()
        self.right_tabs.addTab(self.breakpoints_panel, "Breakpoints")
        
        splitter.addWidget(self.right_tabs)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter)
        
        # Status bar
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Ready")
        
        # Timer for auto-save
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self._auto_save)
        self.auto_save_timer.start(30000)  # 30 seconds
    
    def _setup_toolbar(self):
        """Setup toolbar with file and execution controls"""
        toolbar = QToolBar("Script Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # File operations
        self.new_btn = toolbar.addAction("New")
        self.new_btn.triggered.connect(self._new_script)
        self.new_btn.setShortcut("Ctrl+N")
        
        self.open_btn = toolbar.addAction("Open")
        self.open_btn.triggered.connect(self._open_script)
        self.open_btn.setShortcut("Ctrl+O")
        
        self.save_btn = toolbar.addAction("Save")
        self.save_btn.triggered.connect(self._save_script)
        self.save_btn.setShortcut("Ctrl+S")
        
        self.save_as_btn = toolbar.addAction("Save As")
        self.save_as_btn.triggered.connect(self._save_script_as)
        
        toolbar.addSeparator()
        
        # Execution controls
        self.run_btn = toolbar.addAction("Run (F5)")
        self.run_btn.setToolTip("Execute script")
        self.run_btn.triggered.connect(self._run_script)
        self.run_btn.setShortcut("F5")
        
        self.stop_btn = toolbar.addAction("Stop (F8)")
        self.stop_btn.setToolTip("Stop execution")
        self.stop_btn.triggered.connect(self._stop_script)
        self.stop_btn.setShortcut("F8")
        self.stop_btn.setEnabled(False)
        
        toolbar.addSeparator()
        
        # Debug controls
        self.debug_btn = toolbar.addAction("Debug (F9)")
        self.debug_btn.setToolTip("Start debugging")
        self.debug_btn.triggered.connect(self._start_debug)
        self.debug_btn.setShortcut("F9")
        
        toolbar.addSeparator()
        
        # Tools
        self.clear_output_btn = toolbar.addAction("Clear Output")
        self.clear_output_btn.triggered.connect(self._clear_output)
        
        self.format_btn = toolbar.addAction("Format Code")
        self.format_btn.triggered.connect(self._format_code)
        
        self.lint_btn = toolbar.addAction("Lint")
        self.lint_btn.triggered.connect(self._lint_code)
        
        toolbar.addSeparator()
        
        # Settings
        toolbar.addWidget(QLabel("Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light", "High Contrast"])
        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)
        toolbar.addWidget(self.theme_combo)
        
        toolbar.addWidget(QLabel("Font Size:"))
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setMinimum(8)
        self.font_size_spin.setMaximum(24)
        self.font_size_spin.setValue(11)
        self.font_size_spin.valueChanged.connect(self._on_font_size_changed)
        toolbar.addWidget(self.font_size_spin)
        
        # Auto-save checkbox
        self.auto_save_cb = QCheckBox("Auto-save")
        self.auto_save_cb.setChecked(True)
        toolbar.addWidget(self.auto_save_cb)
    
    def _create_editor_panel(self) -> QWidget:
        """Create editor panel with line numbers and syntax highlighting"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Editor label
        label = QLabel("Python Script Editor:")
        layout.addWidget(label)
        
        # Editor
        self.editor = QTextEdit()
        self.editor.setFont(QFont("Courier New", self.font_size_spin.value()))
        self.editor.setAcceptRichText(False)
        self.editor.setPlaceholderText("# Write your Python script here\n# Access circuit via 'circuit' and 'wires' variables\n\nprint('Hello from script!')")
        
        # Apply syntax highlighting
        self.highlighter = PythonSyntaxHighlighter(self.editor.document())
        
        # Connect text changes
        self.editor.textChanged.connect(self._on_text_changed)
        
        layout.addWidget(self.editor)
        return widget
    
    def _create_output_panel(self) -> QWidget:
        """Create output display panel"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        label = QLabel("Output / Results:")
        layout.addWidget(label)
        
        self.output = QTextEdit()
        self.output.setFont(QFont("Courier New", 10))
        self.output.setReadOnly(True)
        
        layout.addWidget(self.output)
        
        # Execution time label
        self.exec_time_label = QLabel("Execution time: -")
        layout.addWidget(self.exec_time_label)
        
        return widget
    
    def _create_variables_panel(self) -> QWidget:
        """Create variable inspector panel"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Search bar
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.var_search = QLineEdit()
        self.var_search.setPlaceholderText("Variable name...")
        self.var_search.textChanged.connect(self._filter_variables)
        search_layout.addWidget(self.var_search)
        layout.addLayout(search_layout)
        
        # Variables list
        self.variables_list = QListWidget()
        layout.addWidget(self.variables_list)
        
        # Variable details
        self.var_details = QTextEdit()
        self.var_details.setReadOnly(True)
        self.var_details.setMaximumHeight(150)
        layout.addWidget(self.var_details)
        
        self.variables_list.itemSelectionChanged.connect(self._on_variable_selected)
        
        return widget
    
    def _create_breakpoints_panel(self) -> QWidget:
        """Create breakpoints panel"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        label = QLabel("Breakpoints:")
        layout.addWidget(label)
        
        self.breakpoints_list = QListWidget()
        layout.addWidget(self.breakpoints_list)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        add_bp_btn = QPushButton("Add Breakpoint")
        add_bp_btn.clicked.connect(self._add_breakpoint)
        btn_layout.addWidget(add_bp_btn)
        
        remove_bp_btn = QPushButton("Remove")
        remove_bp_btn.clicked.connect(self._remove_breakpoint)
        btn_layout.addWidget(remove_bp_btn)
        
        clear_bp_btn = QPushButton("Clear All")
        clear_bp_btn.clicked.connect(self._clear_breakpoints)
        btn_layout.addWidget(clear_bp_btn)
        
        layout.addLayout(btn_layout)
        
        return widget
    
    def _apply_styles(self):
        """Apply custom styles"""
        self.setStyleSheet("""
            QMainWindow {
                background: #ffffff;
            }
            QTextEdit {
                background: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px;
                font-family: 'Courier New';
            }
            QLabel {
                font-weight: bold;
                color: #333;
            }
            QToolBar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ffffff, stop:1 #f0f0f0);
                border-bottom: 1px solid #bbb;
                spacing: 5px;
            }
            QToolButton {
                background: transparent;
                border-radius: 4px;
                padding: 4px 8px;
            }
            QToolButton:hover {
                background: #e0e7ff;
            }
            QToolButton:pressed {
                background: #d0d7ff;
            }
        """)
    
    # File operations
    def _new_script(self):
        """Create new script"""
        if self.has_unsaved_changes:
            reply = QMessageBox.question(
                self, "New Script",
                "Current script has unsaved changes. Clear it?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        self.editor.clear()
        self.current_file = None
        self.has_unsaved_changes = False
        self.setWindowTitle(f"Script Editor - Untitled")
        self.statusBar().showMessage("New script created")
    
    def _open_script(self):
        """Open script from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Script", "", "Python Files (*.py);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.editor.setText(content)
                self.current_file = Path(file_path)
                self.has_unsaved_changes = False
                self.setWindowTitle(f"Script Editor - {self.current_file.name}")
                self.statusBar().showMessage(f"Opened: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open file: {str(e)}")
    
    def _save_script(self):
        """Save script to file"""
        if not self.current_file:
            self._save_script_as()
            return
        
        try:
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(self.editor.toPlainText())
            self.has_unsaved_changes = False
            self.statusBar().showMessage(f"Saved: {self.current_file}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")
    
    def _save_script_as(self):
        """Save script as new file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Script", "", "Python Files (*.py)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.editor.toPlainText())
                self.current_file = Path(file_path)
                self.has_unsaved_changes = False
                self.setWindowTitle(f"Script Editor - {self.current_file.name}")
                self.statusBar().showMessage(f"Saved: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")
    
    def _auto_save(self):
        """Auto-save script if enabled"""
        if self.auto_save_cb.isChecked() and self.has_unsaved_changes and self.current_file:
            self._save_script()
    
    # Execution
    def _run_script(self):
        """Execute script"""
        if self.is_running:
            QMessageBox.warning(self, "Running", "Script is already running")
            return
        
        script_code = self.editor.toPlainText()
        if not script_code.strip():
            QMessageBox.warning(self, "Empty", "Script is empty")
            return
        
        self.output.clear()
        self.output.append("Running script...\n")
        self.statusBar().showMessage("Executing script...")
        self.is_running = True
        self.run_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        # Create execution context
        exec_context = {
            **self.circuit_context,
            "__name__": "__main__",
        }
        
        # Create and start execution thread
        self.execution_thread = ScriptExecutionThread(script_code, exec_context)
        self.execution_thread.output_received.connect(self._on_script_output)
        self.execution_thread.error_occurred.connect(self._on_script_error)
        self.execution_thread.execution_finished.connect(self._on_script_finished)
        self.execution_thread.start()
    
    def _stop_script(self):
        """Stop script execution"""
        if self.execution_thread and self.execution_thread.isRunning():
            self.execution_thread.stop()
            self.execution_thread.wait()
            self._on_script_finished(False)
    
    def _on_script_output(self, output: str):
        """Handle script output"""
        self.output.append(output)
        self.script_executed.emit(output)
    
    def _on_script_error(self, error: str):
        """Handle script error"""
        self.output.setTextColor(QColor(200, 0, 0))
        self.output.append(error)
        self.output.setTextColor(QColor(0, 0, 0))
        self.script_error.emit(error)
    
    def _on_script_finished(self, success: bool):
        """Handle script completion"""
        self.is_running = False
        self.run_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
        if self.execution_thread:
            exec_time = self.execution_thread.get_execution_time()
            self.exec_time_label.setText(f"Execution time: {exec_time:.4f}s")
        
        status = "Execution completed successfully" if success else "Execution failed"
        self.statusBar().showMessage(status)
        self.output.append(f"\n[{status}]")
    
    # Debugging
    def _start_debug(self):
        """Start debugging mode"""
        self.statusBar().showMessage("Debug mode: Not yet implemented")
        QMessageBox.information(self, "Debugging", "Debugger feature coming soon!")
    
    # Tools
    def _clear_output(self):
        """Clear output window"""
        self.output.clear()
        self.statusBar().showMessage("Output cleared")
    
    def _format_code(self):
        """Format Python code"""
        # TODO: Implement code formatting with autopep8
        QMessageBox.information(self, "Format", "Code formatter coming soon!")
    
    def _lint_code(self):
        """Lint Python code"""
        # TODO: Implement linting with pylint
        QMessageBox.information(self, "Lint", "Code linter coming soon!")
    
    # Variable inspection
    def _filter_variables(self, text: str):
        """Filter variables by name"""
        # TODO: Implement filtering
        pass
    
    def _on_variable_selected(self):
        """Show details of selected variable"""
        # TODO: Implement variable details display
        pass
    
    # Breakpoints
    def _add_breakpoint(self):
        """Add breakpoint"""
        # TODO: Implement breakpoint management
        pass
    
    def _remove_breakpoint(self):
        """Remove breakpoint"""
        # TODO: Implement breakpoint removal
        pass
    
    def _clear_breakpoints(self):
        """Clear all breakpoints"""
        self.breakpoints_list.clear()
        self.debugger.breakpoints.clear()
    
    # Settings
    def _on_theme_changed(self, theme: str):
        """Handle theme change"""
        # TODO: Implement theme switching
        pass
    
    def _on_font_size_changed(self, size: int):
        """Handle font size change"""
        self.editor.setFont(QFont("Courier New", size))
    
    def _on_text_changed(self):
        """Handle text changes"""
        self.has_unsaved_changes = True
    
    def _load_settings(self) -> Dict:
        """Load editor settings"""
        # TODO: Load from config file
        return {
            "font_size": 11,
            "theme": "Light",
            "auto_save": True,
        }
    
    def closeEvent(self, event):
        """Handle window close"""
        if self.has_unsaved_changes:
            reply = QMessageBox.question(
                self, "Unsaved Changes",
                "Script has unsaved changes. Save before closing?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Save:
                self._save_script()
            elif reply == QMessageBox.Cancel:
                event.ignore()
                return
        
        if self.execution_thread and self.execution_thread.isRunning():
            self.execution_thread.stop()
            self.execution_thread.wait()
        
        self.auto_save_timer.stop()
        event.accept()
