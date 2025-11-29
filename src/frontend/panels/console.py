"""
Console Panel - log viewer with filtering, export, and simulation tracking
"""
from enum import Enum
from datetime import datetime
from typing import List
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, 
    QComboBox, QPushButton, QLabel, QFileDialog, QProgressBar
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont, QIcon


class LogLevel(Enum):
    """Log message levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    SIM_START = "SIM_START"  # Simulation started
    SIM_END = "SIM_END"      # Simulation ended
    SIM_PROGRESS = "SIM_PROG" # Simulation progress


class ConsolePanel(QWidget):
    """Console for displaying simulation logs and messages with export"""
    
    log_message = Signal(str, LogLevel)
    
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Status bar for simulation info
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("color: #2e7d32; font-weight: bold;")
        status_layout.addWidget(self.status_label)
        
        # Simulation progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumHeight(20)
        self.progress_bar.setVisible(False)
        status_layout.addWidget(self.progress_bar)
        
        layout.addLayout(status_layout)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        # Filter by level - default to Error
        toolbar.addWidget(QLabel("Filter:"))
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "Debug", "Info", "Warning", "Error"])
        self.filter_combo.setCurrentText("Error")  # Default to errors only
        self.filter_combo.currentTextChanged.connect(self._apply_filter)
        toolbar.addWidget(self.filter_combo)
        
        toolbar.addStretch()
        
        # Export button
        export_btn = QPushButton("Export")
        export_btn.clicked.connect(self._export_logs)
        toolbar.addWidget(export_btn)
        
        # Clear button
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self._clear_console)
        toolbar.addWidget(clear_btn)
        
        layout.addLayout(toolbar)
        
        # Log list
        self.log_list = QListWidget()
        self.log_list.setFont(QFont("Courier", 9))
        layout.addWidget(self.log_list)
        
        # Color map for log levels - enhanced with simulation colors
        self.colors = {
            LogLevel.DEBUG: QColor("#808080"),
            LogLevel.INFO: QColor("#000000"),
            LogLevel.WARNING: QColor("#ff8800"),
            LogLevel.ERROR: QColor("#ff0000"),
            LogLevel.SIM_START: QColor("#2e7d32"),   # Green - simulation started
            LogLevel.SIM_END: QColor("#1565c0"),     # Blue - simulation ended
            LogLevel.SIM_PROGRESS: QColor("#0097a7"), # Cyan - progress update
        }
        
        # Store all messages with timestamps
        self.all_messages: List[tuple] = []  # (timestamp, message, level)
        self.current_filter = "All"
        self.is_simulating = False
        
        # Connect signal
        self.log_message.connect(self.log)
    
    def log(self, message: str, level: LogLevel = LogLevel.INFO):
        """Log a message"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]  # Include milliseconds
        self.all_messages.append((timestamp, message, level))
        
        # Update simulation status
        if level == LogLevel.SIM_START:
            self.is_simulating = True
            self.status_label.setText("Status: ▶ Simulating...")
            self.status_label.setStyleSheet("color: #f57c00; font-weight: bold;")
            self.progress_bar.setValue(0)
            self.progress_bar.setVisible(True)
        elif level == LogLevel.SIM_END:
            self.is_simulating = False
            self.status_label.setText("Status: ✓ Simulation Complete")
            self.status_label.setStyleSheet("color: #2e7d32; font-weight: bold;")
            self.progress_bar.setVisible(False)
        elif level == LogLevel.SIM_PROGRESS and self.is_simulating:
            # Try to extract progress percentage from message
            try:
                if "%" in message:
                    progress = int(''.join(filter(str.isdigit, message.split("%")[0].split()[-1])))
                    self.progress_bar.setValue(min(progress, 100))
            except:
                pass
        
        if self._should_show(level):
            # Format message with icons for different levels
            icon_map = {
                LogLevel.DEBUG: "🔧",
                LogLevel.INFO: "ℹ",
                LogLevel.WARNING: "⚠",
                LogLevel.ERROR: "✕",
                LogLevel.SIM_START: "▶",
                LogLevel.SIM_END: "✓",
                LogLevel.SIM_PROGRESS: "→",
            }
            icon = icon_map.get(level, "•")
            display_text = f"[{timestamp}] {icon} [{level.value}] {message}"
            
            item = QListWidgetItem(display_text)
            item.setForeground(self.colors[level])
            item.setData(Qt.UserRole, (timestamp, message, level))
            self.log_list.addItem(item)
            self.log_list.scrollToBottom()
    
    def _should_show(self, level: LogLevel) -> bool:
        """Check if message should be shown based on current filter"""
        if self.current_filter == "All":
            return True
        return level.value.lower() == self.current_filter.lower()
    
    def _apply_filter(self, filter_text: str):
        """Apply filter to log messages"""
        self.current_filter = filter_text
        self.log_list.clear()
        
        # Icon map for different levels
        icon_map = {
            LogLevel.DEBUG: "🔧",
            LogLevel.INFO: "ℹ",
            LogLevel.WARNING: "⚠",
            LogLevel.ERROR: "✕",
            LogLevel.SIM_START: "▶",
            LogLevel.SIM_END: "✓",
            LogLevel.SIM_PROGRESS: "→",
        }
        
        for timestamp, message, level in self.all_messages:
            if self._should_show(level):
                icon = icon_map.get(level, "•")
                display_text = f"[{timestamp}] {icon} [{level.value}] {message}"
                item = QListWidgetItem(display_text)
                item.setForeground(self.colors[level])
                item.setData(Qt.UserRole, (timestamp, message, level))
                self.log_list.addItem(item)
    
    def _clear_console(self):
        """Clear console"""
        self.log_list.clear()
        self.all_messages.clear()
    
    def _export_logs(self):
        """Export logs to file"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Logs", "",
            "Text Files (*.txt);;CSV Files (*.csv);;JSON Files (*.json);;All Files (*)"
        )
        
        if not filename:
            return
        
        try:
            if filename.endswith('.csv'):
                self._export_csv(filename)
            elif filename.endswith('.json'):
                self._export_json(filename)
            else:
                self._export_text(filename)
            
            self.log(f"Logs exported to {filename}", LogLevel.INFO)
        except Exception as e:
            self.log(f"Export failed: {e}", LogLevel.ERROR)
    
    def _export_text(self, filename: str):
        """Export logs as plain text"""
        with open(filename, 'w') as f:
            for timestamp, message, level in self.all_messages:
                f.write(f"[{timestamp}] [{level.value}] {message}\n")
    
    def _export_csv(self, filename: str):
        """Export logs as CSV"""
        import csv
        
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'Level', 'Message'])
            
            for timestamp, message, level in self.all_messages:
                writer.writerow([timestamp, level.value, message])
    
    def _export_json(self, filename: str):
        """Export logs as JSON"""
        import json
        
        data = [
            {
                'timestamp': timestamp,
                'level': level.value,
                'message': message
            }
            for timestamp, message, level in self.all_messages
        ]
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
