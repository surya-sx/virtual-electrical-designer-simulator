"""Fault Calculator Tool - Separate Window"""
from PySide6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QGroupBox, QFormLayout, QDoubleSpinBox, QWidget,
    QToolBar, QStatusBar, QScrollArea
)
from PySide6.QtCore import QSize
from PySide6.QtGui import QFont


class FaultCalculatorWindow(QMainWindow):
    """Tool for calculating short circuit and fault currents"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Fault Calculator")
        self.setGeometry(100, 100, 900, 800)
        self.setMinimumSize(900, 800)
        
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
        toolbar = QToolBar("Fault Calculator Toolbar")
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
        title = QLabel("Short Circuit & Fault Calculator")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        main_layout.addWidget(title)
        
        # Input Parameters Group
        input_group = QGroupBox("System Parameters")
        input_layout = QFormLayout()
        
        self.system_voltage = QDoubleSpinBox()
        self.system_voltage.setMinimum(12)
        self.system_voltage.setMaximum(765000)
        self.system_voltage.setValue(480)
        self.system_voltage.setSuffix(" V")
        input_layout.addRow("System Voltage:", self.system_voltage)
        
        self.system_power = QDoubleSpinBox()
        self.system_power.setMinimum(0.1)
        self.system_power.setMaximum(100000)
        self.system_power.setValue(500)
        self.system_power.setSuffix(" MVA")
        input_layout.addRow("System Power (MVA):", self.system_power)
        
        self.x_r_ratio = QDoubleSpinBox()
        self.x_r_ratio.setMinimum(0.1)
        self.x_r_ratio.setMaximum(50)
        self.x_r_ratio.setValue(10)
        input_layout.addRow("X/R Ratio:", self.x_r_ratio)
        
        self.fault_type = QComboBox()
        self.fault_type.addItems(["3-Phase", "Line-to-Line", "Line-to-Ground"])
        input_layout.addRow("Fault Type:", self.fault_type)
        
        self.transformer_impedance = QDoubleSpinBox()
        self.transformer_impedance.setMinimum(1)
        self.transformer_impedance.setMaximum(50)
        self.transformer_impedance.setValue(5.75)
        self.transformer_impedance.setSuffix(" %")
        input_layout.addRow("Transformer Impedance:", self.transformer_impedance)
        
        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)
        
        # Results Group
        results_group = QGroupBox("Fault Analysis Results")
        results_layout = QFormLayout()
        
        self.short_circuit_current = QLineEdit()
        self.short_circuit_current.setReadOnly(True)
        results_layout.addRow("Short Circuit Current:", self.short_circuit_current)
        
        self.symmetrical_current = QLineEdit()
        self.symmetrical_current.setReadOnly(True)
        results_layout.addRow("Symmetrical Current:", self.symmetrical_current)
        
        self.asymmetrical_current = QLineEdit()
        self.asymmetrical_current.setReadOnly(True)
        results_layout.addRow("Asymmetrical Current:", self.asymmetrical_current)
        
        self.breaking_capacity = QLineEdit()
        self.breaking_capacity.setReadOnly(True)
        results_layout.addRow("Required Breaking Capacity:", self.breaking_capacity)
        
        results_group.setLayout(results_layout)
        main_layout.addWidget(results_group)
        
        main_layout.addStretch()
        
        # Status bar
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Ready")
    
    def _calculate(self):
        """Calculate fault currents"""
        try:
            voltage = self.system_voltage.value()
            power = self.system_power.value()
            x_r = self.x_r_ratio.value()
            z_tx = self.transformer_impedance.value() / 100
            
            # Base impedance
            z_base = (voltage ** 2) / (power * 1000)
            
            # System impedance from MVA
            z_system = z_base
            
            # Total impedance
            z_total = z_system + z_tx
            
            # 3-phase short circuit current
            i_sc_3ph = (voltage * 1000) / (z_total * 1.732)
            
            # Apply X/R ratio for asymmetrical current
            import math
            asymmetry_factor = 1.5 * math.exp(-x_r / 1.5)
            i_asymmetrical = i_sc_3ph * asymmetry_factor
            
            fault_type = self.fault_type.currentText()
            
            # Adjust for fault type
            if fault_type == "Line-to-Line":
                i_sc_3ph = i_sc_3ph * 0.866
            elif fault_type == "Line-to-Ground":
                i_sc_3ph = i_sc_3ph * 0.5
            
            self.short_circuit_current.setText(f"{i_sc_3ph:.2f} A")
            self.symmetrical_current.setText(f"{i_sc_3ph:.2f} A")
            self.asymmetrical_current.setText(f"{i_asymmetrical:.2f} A")
            self.breaking_capacity.setText(f"{i_asymmetrical * 1.25:.2f} A")
            
            self.statusBar().showMessage(f"✓ Calculation complete - {i_sc_3ph:.2f} A short circuit current")
        except Exception as e:
            self.statusBar().showMessage(f"❌ Error: {str(e)}")
    
    def _clear_all(self):
        """Clear all fields"""
        self.short_circuit_current.clear()
        self.symmetrical_current.clear()
        self.asymmetrical_current.clear()
        self.breaking_capacity.clear()
        self.statusBar().showMessage("Cleared")
    
    def _export(self):
        """Export design to file"""
        self.statusBar().showMessage("Export feature - Coming soon")
