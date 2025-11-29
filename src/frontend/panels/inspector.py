"""
Inspector Panel - displays and edits properties of selected components
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QDoubleSpinBox, QSpinBox, QLineEdit, QComboBox
)
from PySide6.QtCore import Qt, Signal


class InspectorPanel(QWidget):
    """Panel for inspecting and editing component properties"""
    
    # Signals
    property_changed = Signal(str, str, object)  # component_id, property, value
    
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Tabbed interface
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Component properties tab
        self.component_tab = self._create_property_table()
        self.tabs.addTab(self.component_tab, "Component")
        
        # Circuit properties tab
        self.circuit_tab = self._create_property_table()
        self.tabs.addTab(self.circuit_tab, "Circuit")
        
        # Simulation settings tab
        self.simulation_tab = self._create_property_table()
        self.tabs.addTab(self.simulation_tab, "Simulation")
        
        # Button bar
        button_layout = QHBoxLayout()
        self.reset_button = QPushButton("Reset")
        self.apply_button = QPushButton("Apply")
        self.export_button = QPushButton("Export")
        button_layout.addWidget(self.reset_button)
        button_layout.addStretch()
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.export_button)
        layout.addLayout(button_layout)
        
        # Connect signals
        self.apply_button.clicked.connect(self._on_apply_clicked)
        self.reset_button.clicked.connect(self._on_reset_clicked)
        self.export_button.clicked.connect(self._on_export_clicked)
        
        self.current_component = None
    
    def _create_property_table(self):
        """Create an editable property table widget"""
        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Property", "Value"])
        table.horizontalHeader().setStretchLastSection(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.itemChanged.connect(self._on_item_changed)
        return table
    
    def set_component_properties(self, component_id: str, properties: dict):
        """Set properties for inspection"""
        self.current_component = component_id
        self.component_tab.setRowCount(0)
        
        for row, (key, value) in enumerate(properties.items()):
            self.component_tab.insertRow(row)
            
            # Property name (read-only)
            prop_item = QTableWidgetItem(str(key))
            prop_item.setFlags(prop_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.component_tab.setItem(row, 0, prop_item)
            
            # Property value (editable)
            value_item = QTableWidgetItem(str(value))
            self.component_tab.setItem(row, 1, value_item)
    
    def set_circuit_properties(self, properties: dict):
        """Set circuit-wide properties"""
        self.circuit_tab.setRowCount(0)
        
        for row, (key, value) in enumerate(properties.items()):
            self.circuit_tab.insertRow(row)
            
            prop_item = QTableWidgetItem(str(key))
            prop_item.setFlags(prop_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.circuit_tab.setItem(row, 0, prop_item)
            
            value_item = QTableWidgetItem(str(value))
            self.circuit_tab.setItem(row, 1, value_item)
    
    def set_simulation_properties(self, properties: dict):
        """Set simulation parameters"""
        self.simulation_tab.setRowCount(0)
        
        for row, (key, value) in enumerate(properties.items()):
            self.simulation_tab.insertRow(row)
            
            prop_item = QTableWidgetItem(str(key))
            prop_item.setFlags(prop_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.simulation_tab.setItem(row, 0, prop_item)
            
            value_item = QTableWidgetItem(str(value))
            self.simulation_tab.setItem(row, 1, value_item)
    
    def get_component_properties(self) -> dict:
        """Get all component properties from table"""
        props = {}
        
        for row in range(self.component_tab.rowCount()):
            key_item = self.component_tab.item(row, 0)
            value_item = self.component_tab.item(row, 1)
            
            if key_item and value_item:
                key = key_item.text()
                value = value_item.text()
                props[key] = value
        
        return props
    
    def clear(self):
        """Clear all inspector data"""
        self.component_tab.setRowCount(0)
        self.circuit_tab.setRowCount(0)
        self.simulation_tab.setRowCount(0)
        self.current_component = None
    
    def _on_item_changed(self, item: QTableWidgetItem):
        """Handle property value changes"""
        if self.current_component and item.column() == 1:
            row = item.row()
            key_item = self.component_tab.item(row, 0)
            
            if key_item:
                prop_name = key_item.text()
                prop_value = item.text()
                self.property_changed.emit(self.current_component, prop_name, prop_value)
    
    def _on_apply_clicked(self):
        """Apply changes"""
        props = self.get_component_properties()
        if self.current_component:
            for key, value in props.items():
                self.property_changed.emit(self.current_component, key, value)
    
    def _on_reset_clicked(self):
        """Reset changes"""
        self.component_tab.setRowCount(0)
    
    def _on_export_clicked(self):
        """Export properties to file"""
        from PySide6.QtWidgets import QFileDialog
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Properties", "",
            "JSON Files (*.json);;CSV Files (*.csv);;All Files (*)"
        )
        
        if filename:
            props = self.get_component_properties()
            
            if filename.endswith('.json'):
                import json
                with open(filename, 'w') as f:
                    json.dump(props, f, indent=2)
            elif filename.endswith('.csv'):
                import csv
                with open(filename, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Property', 'Value'])
                    for key, value in props.items():
                        writer.writerow([key, value])
