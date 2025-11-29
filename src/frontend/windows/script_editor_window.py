"""
Script Editor Window - Separate window for Python script editing and execution
Each script window is independent with its own execution context
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QMessageBox, QFileDialog,
    QSplitter, QStatusBar, QToolBar, QComboBox
)
from PySide6.QtGui import QFont, QIcon, QSyntaxHighlighter, QTextDocument, QTextCharFormat, QColor
from PySide6.QtCore import Qt, Signal, QSize, QThread
from typing import Dict, Any, Optional
import json
import sys
import traceback
import io


class PythonSyntaxHighlighter(QSyntaxHighlighter):
    """Python syntax highlighter"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Keywords
        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor(33, 66, 131))  # Dark blue
        self.keyword_format.setFontWeight(700)
        
        # Built-in functions
        self.builtin_format = QTextCharFormat()
        self.builtin_format.setForeground(QColor(152, 104, 1))  # Brown
        
        # Strings
        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor(40, 128, 0))  # Green
        
        # Comments
        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor(128, 128, 128))  # Gray
        self.comment_format.setFontItalic(True)
        
        # Numbers
        self.number_format = QTextCharFormat()
        self.number_format.setForeground(QColor(200, 40, 41))  # Red
    
    def highlightBlock(self, text: str):
        """Highlight text block"""
        # Simple implementation - can be enhanced with regex patterns
        if '#' in text:
            comment_pos = text.find('#')
            self.setFormat(comment_pos, len(text) - comment_pos, self.comment_format)


class ScriptExecutionThread(QThread):
    """Thread for executing scripts without blocking UI"""
    
    finished = Signal()
    output_signal = Signal(str)
    error_signal = Signal(str)
    
    def __init__(self, script_code: str, context: Dict[str, Any]):
        super().__init__()
        self.script_code = script_code
        self.context = context
    
    def run(self):
        """Execute script in separate thread"""
        try:
            # Capture output
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = io.StringIO()
            sys.stderr = io.StringIO()
            
            # Execute script
            exec(self.script_code, self.context)
            
            # Get output
            output = sys.stdout.getvalue()
            if output:
                self.output_signal.emit(output)
            
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            
        except Exception as e:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            self.error_signal.emit(f"Error: {str(e)}\n{traceback.format_exc()}")
        
        finally:
            self.finished.emit()


class ScriptEditorWindow(QMainWindow):
    """Separate window for editing and executing Python scripts"""
    
    # Signals for parent communication
    script_executed = Signal(str)  # script output
    script_error = Signal(str)  # script error
    
    def __init__(self, script_name: str = "Script", parent=None, circuit_context: Dict = None):
        super().__init__(parent)
        self.script_name = script_name
        self.circuit_context = circuit_context or {}
        self.current_file = None
        self.execution_thread = None
        self.is_running = False
        
        self.setWindowTitle(f"Script Editor - {script_name}")
        self.setWindowIcon(QIcon.fromTheme("text-editor"))
        self.setGeometry(100, 100, 900, 700)
        
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Setup UI components"""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Toolbar
        toolbar = QToolBar("Script Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        self.new_btn = toolbar.addAction("New Script")
        self.new_btn.triggered.connect(self._new_script)
        
        self.open_btn = toolbar.addAction("Open")
        self.open_btn.triggered.connect(self._open_script)
        
        self.save_btn = toolbar.addAction("Save")
        self.save_btn.triggered.connect(self._save_script)
        
        self.save_as_btn = toolbar.addAction("Save As")
        self.save_as_btn.triggered.connect(self._save_script_as)
        
        toolbar.addSeparator()
        
        self.run_btn = toolbar.addAction("Run (F5)")
        self.run_btn.setToolTip("Execute script")
        self.run_btn.triggered.connect(self._run_script)
        
        self.stop_btn = toolbar.addAction("Stop (F8)")
        self.stop_btn.setToolTip("Stop execution")
        self.stop_btn.triggered.connect(self._stop_script)
        self.stop_btn.setEnabled(False)
        
        toolbar.addSeparator()
        
        self.clear_output_btn = toolbar.addAction("Clear Output")
        self.clear_output_btn.triggered.connect(self._clear_output)
        
        # Main splitter (editor and output)
        splitter = QSplitter(Qt.Vertical)
        
        # Editor section
        editor_label = QLabel("Python Script Editor:")
        self.editor = QTextEdit()
        self.editor.setFont(QFont("Courier New", 11))
        self.editor.setAcceptRichText(False)
        self.editor.setPlaceholderText("# Write your Python script here\n# Use circuit, components, etc.\n\nprint('Hello from script!')")
        
        # Apply syntax highlighting
        self.highlighter = PythonSyntaxHighlighter(self.editor.document())
        
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.addWidget(editor_label)
        editor_layout.addWidget(self.editor)
        
        # Output section
        output_label = QLabel("Output / Results:")
        self.output = QTextEdit()
        self.output.setFont(QFont("Courier New", 10))
        self.output.setReadOnly(True)
        self.output.setMaximumHeight(200)
        
        output_widget = QWidget()
        output_layout = QVBoxLayout(output_widget)
        output_layout.setContentsMargins(0, 0, 0, 0)
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output)
        
        splitter.addWidget(editor_widget)
        splitter.addWidget(output_widget)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter)
        
        # Status bar
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Ready")
        
        # Keyboard shortcuts
        self.new_btn.setShortcut("Ctrl+N")
        self.open_btn.setShortcut("Ctrl+O")
        self.save_btn.setShortcut("Ctrl+S")
        self.run_btn.setShortcut("F5")
        self.stop_btn.setShortcut("F8")
    
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
    
    def _new_script(self):
        """Create new script"""
        if self.editor.toPlainText().strip():
            reply = QMessageBox.question(
                self, "New Script",
                "Current script has content. Clear it?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        self.editor.clear()
        self.current_file = None
        self.setWindowTitle(f"Script Editor - Untitled")
        self.statusBar().showMessage("New script created")
    
    def _open_script(self):
        """Open script from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Script", "", "Python Files (*.py);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                self.editor.setText(content)
                self.current_file = file_path
                self.setWindowTitle(f"Script Editor - {file_path.split('/')[-1]}")
                self.statusBar().showMessage(f"Opened: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open file: {str(e)}")
    
    def _save_script(self):
        """Save script to file"""
        if not self.current_file:
            self._save_script_as()
            return
        
        try:
            with open(self.current_file, 'w') as f:
                f.write(self.editor.toPlainText())
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
                with open(file_path, 'w') as f:
                    f.write(self.editor.toPlainText())
                self.current_file = file_path
                self.setWindowTitle(f"Script Editor - {file_path.split('/')[-1]}")
                self.statusBar().showMessage(f"Saved: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")
    
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
            "print": self._script_print,
            "__name__": "__main__",
        }
        
        # Create and start execution thread
        self.execution_thread = ScriptExecutionThread(script_code, exec_context)
        self.execution_thread.output_signal.connect(self._on_script_output)
        self.execution_thread.error_signal.connect(self._on_script_error)
        self.execution_thread.finished.connect(self._on_script_finished)
        self.execution_thread.start()
    
    def _stop_script(self):
        """Stop script execution"""
        if self.execution_thread and self.execution_thread.isRunning():
            self.execution_thread.terminate()
            self.execution_thread.wait()
            self._on_script_finished()
    
    def _script_print(self, *args, **kwargs):
        """Capture print output from script"""
        text = " ".join(str(arg) for arg in args)
        self.output_signal.emit(text + "\n")
    
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
    
    def _on_script_finished(self):
        """Handle script completion"""
        self.is_running = False
        self.run_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.statusBar().showMessage("Execution completed")
        self.output.append("\n[Script finished]")
    
    def _clear_output(self):
        """Clear output window"""
        self.output.clear()
        self.statusBar().showMessage("Output cleared")
    
    def get_script_code(self) -> str:
        """Get current script code"""
        return self.editor.toPlainText()
    
    def set_script_code(self, code: str):
        """Set script code"""
        self.editor.setText(code)
    
    def closeEvent(self, event):
        """Handle window close"""
        if self.editor.toPlainText().strip():
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
            self.execution_thread.terminate()
            self.execution_thread.wait()
        
        event.accept()
