"""
Variable Explorer - Watch and inspect variables during script execution
Provides real-time inspection of variable types, values, and memory usage
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QPushButton, QLineEdit, QLabel, QComboBox, QCheckBox, QHeaderView
)
from PySide6.QtGui import QFont, QIcon, QColor
from PySide6.QtCore import Qt, QTimer
from typing import Dict, Any, List, Optional
import sys


class VariableExplorer(QWidget):
    """Explore and watch variables in script execution context"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.watched_variables: Dict[str, Any] = {}
        self.execution_context: Dict[str, Any] = {}
        self.refresh_interval = 200  # ms
        
        self.setWindowTitle("Variable Explorer")
        self.setGeometry(100, 100, 500, 600)
        
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Search and filter
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter variables...")
        self.search_input.textChanged.connect(self._on_search_changed)
        search_layout.addWidget(self.search_input)
        
        layout.addLayout(search_layout)
        
        # Filter options
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Show:"))
        
        self.type_filter = QComboBox()
        self.type_filter.addItems([
            "All Types",
            "Built-ins",
            "Functions",
            "Classes",
            "Modules",
            "Primitives (int, float, str, bool)",
            "Collections (list, dict, tuple, set)"
        ])
        self.type_filter.currentTextChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(self.type_filter)
        
        self.show_private_cb = QCheckBox("Private")
        self.show_private_cb.setChecked(False)
        self.show_private_cb.stateChanged.connect(self._refresh_tree)
        filter_layout.addWidget(self.show_private_cb)
        
        self.show_magic_cb = QCheckBox("Magic")
        self.show_magic_cb.setChecked(False)
        self.show_magic_cb.stateChanged.connect(self._refresh_tree)
        filter_layout.addWidget(self.show_magic_cb)
        
        layout.addLayout(filter_layout)
        
        # Variable tree
        tree_label = QLabel("Variables:")
        layout.addWidget(tree_label)
        
        self.var_tree = QTreeWidget()
        self.var_tree.setHeaderLabels(["Variable", "Type", "Value", "Size"])
        self.var_tree.setColumnCount(4)
        self.var_tree.itemSelectionChanged.connect(self._on_item_selected)
        self.var_tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.var_tree.header().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.var_tree)
        
        # Details panel
        details_label = QLabel("Details:")
        layout.addWidget(details_label)
        
        self.details_tree = QTreeWidget()
        self.details_tree.setHeaderLabels(["Property", "Value"])
        self.details_tree.setMaximumHeight(180)
        self.details_tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.details_tree)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._refresh_tree)
        button_layout.addWidget(refresh_btn)
        
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self._clear_watches)
        button_layout.addWidget(clear_btn)
        
        copy_btn = QPushButton("Copy Value")
        copy_btn.clicked.connect(self._copy_value)
        button_layout.addWidget(copy_btn)
        
        layout.addLayout(button_layout)
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._refresh_tree)
    
    def _apply_styles(self):
        """Apply custom styles"""
        self.setStyleSheet("""
            QTreeWidget {
                background: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px;
                font-family: 'Courier New';
                font-size: 10px;
            }
            QTreeWidget::item {
                padding: 2px;
            }
            QTreeWidget::item:selected {
                background: #e0e7ff;
            }
            QLineEdit {
                background: #ffffff;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px;
                font-family: 'Courier New';
            }
            QPushButton {
                background: #007bff;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #0056b3;
            }
            QPushButton:pressed {
                background: #004085;
            }
        """)
    
    def update_context(self, context: Dict[str, Any]):
        """Update execution context with new variables"""
        self.execution_context = context
        self._refresh_tree()
    
    def start_monitoring(self):
        """Start auto-refresh of variables"""
        self.refresh_timer.start(self.refresh_interval)
    
    def stop_monitoring(self):
        """Stop auto-refresh"""
        self.refresh_timer.stop()
    
    def add_watch(self, variable_name: str):
        """Add variable to watch list"""
        if variable_name not in self.watched_variables:
            self.watched_variables[variable_name] = None
            self._refresh_tree()
    
    def remove_watch(self, variable_name: str):
        """Remove variable from watch list"""
        if variable_name in self.watched_variables:
            del self.watched_variables[variable_name]
            self._refresh_tree()
    
    def _refresh_tree(self):
        """Refresh variable tree"""
        self.var_tree.clear()
        self.details_tree.clear()
        
        # Filter variables
        variables = self._filter_variables()
        
        # Add variables to tree
        for var_name, var_value in variables.items():
            item = self._create_tree_item(var_name, var_value)
            self.var_tree.addTopLevelItem(item)
    
    def _filter_variables(self) -> Dict[str, Any]:
        """Filter variables based on current filters"""
        filtered = {}
        
        for var_name, var_value in self.execution_context.items():
            # Skip private/magic if not checked
            if var_name.startswith('_'):
                if var_name.startswith('__'):
                    if not self.show_magic_cb.isChecked():
                        continue
                else:
                    if not self.show_private_cb.isChecked():
                        continue
            
            # Apply search filter
            search_text = self.search_input.text().lower()
            if search_text and search_text not in var_name.lower():
                continue
            
            # Apply type filter
            type_filter = self.type_filter.currentText()
            if type_filter != "All Types":
                if not self._matches_type_filter(var_value, type_filter):
                    continue
            
            filtered[var_name] = var_value
        
        return filtered
    
    def _matches_type_filter(self, value: Any, type_filter: str) -> bool:
        """Check if value matches type filter"""
        type_name = type(value).__name__
        
        if type_filter == "Built-ins":
            return type_name in ('int', 'float', 'str', 'bool', 'NoneType')
        
        elif type_filter == "Functions":
            return callable(value) and not isinstance(value, type)
        
        elif type_filter == "Classes":
            return isinstance(value, type)
        
        elif type_filter == "Modules":
            return type_name == 'module'
        
        elif type_filter == "Primitives (int, float, str, bool)":
            return type_name in ('int', 'float', 'str', 'bool')
        
        elif type_filter == "Collections (list, dict, tuple, set)":
            return type_name in ('list', 'dict', 'tuple', 'set')
        
        return True
    
    def _create_tree_item(self, var_name: str, var_value: Any) -> QTreeWidgetItem:
        """Create tree item for variable"""
        type_name = type(var_value).__name__
        
        # Truncate value representation
        try:
            value_str = repr(var_value)
            if len(value_str) > 50:
                value_str = value_str[:47] + "..."
        except:
            value_str = "<unrepresentable>"
        
        # Get size
        try:
            size_bytes = sys.getsizeof(var_value)
            size_str = self._format_size(size_bytes)
        except:
            size_str = "?"
        
        # Create item
        item = QTreeWidgetItem([var_name, type_name, value_str, size_str])
        
        # Color code by type
        self._color_item_by_type(item, var_value)
        
        # Add nested items for collections
        if isinstance(var_value, (list, tuple)):
            self._add_collection_items(item, var_value, max_items=10)
        elif isinstance(var_value, dict):
            self._add_dict_items(item, var_value, max_items=10)
        
        return item
    
    def _color_item_by_type(self, item: QTreeWidgetItem, value: Any):
        """Color code item by type"""
        type_name = type(value).__name__
        
        colors = {
            'int': '#0066cc',      # Blue
            'float': '#0066cc',    # Blue
            'str': '#009900',      # Green
            'bool': '#cc6600',     # Orange
            'NoneType': '#999999', # Gray
            'list': '#9933cc',     # Purple
            'dict': '#9933cc',     # Purple
            'tuple': '#9933cc',    # Purple
            'set': '#9933cc',      # Purple
            'function': '#cc0000', # Red
            'method': '#cc0000',   # Red
        }
        
        color = colors.get(type_name, '#333333')  # Default dark gray
        item.setForeground(0, QColor(color))
    
    def _add_collection_items(self, parent: QTreeWidgetItem, collection, max_items: int):
        """Add items for list/tuple"""
        for i, item_value in enumerate(collection[:max_items]):
            if i >= max_items:
                parent.addChild(QTreeWidgetItem(["...", "", f"({len(collection) - max_items} more items)"]))
                break
            
            type_name = type(item_value).__name__
            try:
                value_str = repr(item_value)
                if len(value_str) > 50:
                    value_str = value_str[:47] + "..."
            except:
                value_str = "<unrepresentable>"
            
            child = QTreeWidgetItem([f"[{i}]", type_name, value_str])
            parent.addChild(child)
    
    def _add_dict_items(self, parent: QTreeWidgetItem, d: dict, max_items: int):
        """Add items for dict"""
        for i, (key, value) in enumerate(d.items()):
            if i >= max_items:
                parent.addChild(QTreeWidgetItem(["...", "", f"({len(d) - max_items} more items)"]))
                break
            
            type_name = type(value).__name__
            try:
                value_str = repr(value)
                if len(value_str) > 50:
                    value_str = value_str[:47] + "..."
            except:
                value_str = "<unrepresentable>"
            
            try:
                key_str = repr(key)
                if len(key_str) > 30:
                    key_str = key_str[:27] + "..."
            except:
                key_str = "<unrepresentable>"
            
            child = QTreeWidgetItem([key_str, type_name, value_str])
            parent.addChild(child)
    
    def _format_size(self, size_bytes: int) -> str:
        """Format byte size to human readable"""
        for unit in ('B', 'KB', 'MB', 'GB'):
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
    
    def _on_search_changed(self):
        """Handle search text change"""
        self._refresh_tree()
    
    def _on_filter_changed(self):
        """Handle filter change"""
        self._refresh_tree()
    
    def _on_item_selected(self):
        """Show details of selected variable"""
        items = self.var_tree.selectedItems()
        if not items:
            return
        
        item = items[0]
        var_name = item.text(0)
        
        # Find variable in context
        var_value = self.execution_context.get(var_name)
        
        if var_value is None:
            return
        
        # Show details
        self.details_tree.clear()
        
        # Basic info
        type_item = QTreeWidgetItem(["Type", type(var_value).__name__])
        self.details_tree.addTopLevelItem(type_item)
        
        # Value
        try:
            value_str = repr(var_value)
        except:
            value_str = "<unrepresentable>"
        
        value_item = QTreeWidgetItem(["Value", value_str])
        self.details_tree.addTopLevelItem(value_item)
        
        # Size
        try:
            size = sys.getsizeof(var_value)
            size_item = QTreeWidgetItem(["Size", self._format_size(size)])
            self.details_tree.addTopLevelItem(size_item)
        except:
            pass
        
        # Attributes
        try:
            attrs = dir(var_value)
            if attrs:
                attrs_item = QTreeWidgetItem(["Attributes", f"({len(attrs)} items)"])
                for attr_name in attrs[:20]:
                    attr_item = QTreeWidgetItem([attr_name, ""])
                    attrs_item.addChild(attr_item)
                self.details_tree.addTopLevelItem(attrs_item)
        except:
            pass
    
    def _clear_watches(self):
        """Clear all watches"""
        self.watched_variables.clear()
        self._refresh_tree()
    
    def _copy_value(self):
        """Copy selected value to clipboard"""
        items = self.var_tree.selectedItems()
        if not items:
            return
        
        item = items[0]
        value_text = item.text(2)
        
        # Copy to clipboard
        from PySide6.QtGui import QClipboard
        from PySide6.QtWidgets import QApplication
        
        clipboard = QApplication.clipboard()
        clipboard.setText(value_text)
