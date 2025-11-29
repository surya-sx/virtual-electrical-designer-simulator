"""Battery Tool - Separate Window"""
from PySide6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QGroupBox, QFormLayout, QDoubleSpinBox, QSpinBox, QWidget,
    QToolBar, QStatusBar, QScrollArea
)
from PySide6.QtCore import QSize
from PySide6.QtGui import QFont


class BatteryToolWindow(QMainWindow):
    """Tool for battery sizing and discharge calculations"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Battery Tool")
        self.setGeometry(100, 100, 900, 850)
        self.setMinimumSize(900, 850)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the user interface"""
        # Create scrollable main widget
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        main_widget = QWidget()
        scroll.setWidget(main_widget)
        self.setCentralWidget(scroll)
        
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Toolbar
        toolbar = QToolBar("Battery Tool Toolbar")
        toolbar.setIconSize(QSize(20, 20))
        self.addToolBar(toolbar)
        
        clear_btn = toolbar.addAction("Clear")
        clear_btn.triggered.connect(self._clear_all)
        
        calculate_btn = toolbar.addAction("Calculate")
        calculate_btn.triggered.connect(self._calculate)
        
        toolbar.addSeparator()
        
        export_btn = toolbar.addAction("Export")
        export_btn.triggered.connect(self._export)
        
        # Title
        title = QLabel("Battery Sizing & Analysis Tool")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        main_layout.addWidget(title)
        
        # Input Parameters Group
        input_group = QGroupBox("Load Requirements")
        input_layout = QFormLayout()
        
        self.load_power = QDoubleSpinBox()
        self.load_power.setMinimum(0.1)
        self.load_power.setMaximum(100000)
        self.load_power.setValue(5)
        self.load_power.setSuffix(" kW")
        input_layout.addRow("Load Power:", self.load_power)
        
        self.duration = QDoubleSpinBox()
        self.duration.setMinimum(0.1)
        self.duration.setMaximum(1000)
        self.duration.setValue(4)
        self.duration.setSuffix(" hours")
        input_layout.addRow("Duration:", self.duration)
        
        self.system_voltage = QComboBox()
        self.system_voltage.addItems(["12V", "24V", "48V", "120V", "240V", "400V"])
        input_layout.addRow("System Voltage:", self.system_voltage)
        
        self.battery_type = QComboBox()
        self.battery_type.addItems(["Lead-Acid", "Lithium (LiFePO4)", "NiMH", "Solid-State"])
        input_layout.addRow("Battery Type:", self.battery_type)
        
        self.depth_of_discharge = QDoubleSpinBox()
        self.depth_of_discharge.setMinimum(10)
        self.depth_of_discharge.setMaximum(100)
        self.depth_of_discharge.setValue(80)
        self.depth_of_discharge.setSuffix(" %")
        input_layout.addRow("Depth of Discharge:", self.depth_of_discharge)
        
        self.efficiency = QDoubleSpinBox()
        self.efficiency.setMinimum(50)
        self.efficiency.setMaximum(99)
        self.efficiency.setValue(90)
        self.efficiency.setSuffix(" %")
        input_layout.addRow("System Efficiency:", self.efficiency)
        
        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)
        
        # Results Group
        results_group = QGroupBox("Battery Specifications")
        results_layout = QFormLayout()
        
        self.energy_required = QLineEdit()
        self.energy_required.setReadOnly(True)
        results_layout.addRow("Energy Required:", self.energy_required)
        
        self.capacity = QLineEdit()
        self.capacity.setReadOnly(True)
        results_layout.addRow("Battery Capacity (Ah):", self.capacity)
        
        self.battery_cells = QLineEdit()
        self.battery_cells.setReadOnly(True)
        results_layout.addRow("Number of Cells:", self.battery_cells)
        
        self.discharge_current = QLineEdit()
        self.discharge_current.setReadOnly(True)
        results_layout.addRow("Discharge Current:", self.discharge_current)
        
        self.battery_weight = QLineEdit()
        self.battery_weight.setReadOnly(True)
        results_layout.addRow("Estimated Weight:", self.battery_weight)
        
        results_group.setLayout(results_layout)
        main_layout.addWidget(results_group)
        
        main_layout.addStretch()
        
        # Status bar
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Ready")
    
    def _calculate(self):
        """Calculate battery sizing"""
        try:
            power = self.load_power.value()  # kW
            duration = self.duration.value()  # hours
            dod = self.depth_of_discharge.value() / 100
            efficiency = self.efficiency.value() / 100
            
            # Extract voltage as number
            voltage_str = self.system_voltage.currentText()
            voltage = float(voltage_str.replace('V', ''))
            
            # Energy required (kWh)
            energy = power * duration
            
            # Usable capacity (accounting for DoD)
            capacity_ah = (energy * 1000) / (voltage * dod * efficiency)
            
            # Number of cells (assuming ~2V per cell)
            cells = voltage / 2
            
            # Discharge rate (C-rate for 1-hour discharge)
            discharge_current = capacity_ah / duration
            
            # Estimated weight (lead-acid: 18-22 kg per kWh, Li: 5-10 kg/kWh)
            battery_type = self.battery_type.currentText()
            if battery_type == "Lead-Acid":
                weight = energy * 20
            elif battery_type == "Lithium (LiFePO4)":
                weight = energy * 7
            elif battery_type == "NiMH":
                weight = energy * 10
            else:
                weight = energy * 5
            
            self.energy_required.setText(f"{energy:.2f} kWh")
            self.capacity.setText(f"{capacity_ah:.2f} Ah")
            self.battery_cells.setText(f"{int(cells)} cells")
            self.discharge_current.setText(f"{discharge_current:.2f} A")
            self.battery_weight.setText(f"{weight:.2f} kg")
            
            self.statusBar().showMessage(f"✓ Calculation complete - {capacity_ah:.2f} Ah capacity required")
        except Exception as e:
            self.statusBar().showMessage(f"❌ Error: {str(e)}")
    
    def _clear_all(self):
        """Clear all fields"""
        self.energy_required.clear()
        self.capacity.clear()
        self.battery_cells.clear()
        self.discharge_current.clear()
        self.battery_weight.clear()
        self.statusBar().showMessage("Cleared")
    
    def _export(self):
        """Export design to file"""
        self.statusBar().showMessage("Export feature - Coming soon")
