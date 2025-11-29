"""Power Factor Correction Tool - Separate Window"""
from PySide6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QGroupBox, QFormLayout, QDoubleSpinBox, QWidget,
    QToolBar, QStatusBar, QScrollArea
)
from PySide6.QtCore import QSize
from PySide6.QtGui import QFont


class PFCorrectionWindow(QMainWindow):
    """Tool for power factor correction and capacitor sizing"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Power Factor Correction")
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
        toolbar = QToolBar("PF Correction Toolbar")
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
        title = QLabel("Power Factor Correction Calculator")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        main_layout.addWidget(title)
        
        # Input Parameters Group
        input_group = QGroupBox("Load Parameters")
        input_layout = QFormLayout()
        
        self.real_power = QDoubleSpinBox()
        self.real_power.setMinimum(0.1)
        self.real_power.setMaximum(100000)
        self.real_power.setValue(100)
        self.real_power.setSuffix(" kW")
        input_layout.addRow("Real Power (P):", self.real_power)
        
        self.voltage = QDoubleSpinBox()
        self.voltage.setMinimum(12)
        self.voltage.setMaximum(765000)
        self.voltage.setValue(480)
        self.voltage.setSuffix(" V")
        input_layout.addRow("Voltage:", self.voltage)
        
        self.current_pf = QDoubleSpinBox()
        self.current_pf.setMinimum(0.5)
        self.current_pf.setMaximum(1.0)
        self.current_pf.setValue(0.80)
        self.current_pf.setDecimals(3)
        input_layout.addRow("Current Power Factor:", self.current_pf)
        
        self.target_pf = QDoubleSpinBox()
        self.target_pf.setMinimum(0.5)
        self.target_pf.setMaximum(1.0)
        self.target_pf.setValue(0.95)
        self.target_pf.setDecimals(3)
        input_layout.addRow("Target Power Factor:", self.target_pf)
        
        self.system_type = QComboBox()
        self.system_type.addItems(["Single Phase", "3-Phase"])
        input_layout.addRow("System Type:", self.system_type)
        
        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)
        
        # Results Group
        results_group = QGroupBox("Correction Requirements")
        results_layout = QFormLayout()
        
        self.reactive_power_before = QLineEdit()
        self.reactive_power_before.setReadOnly(True)
        results_layout.addRow("Reactive Power Before:", self.reactive_power_before)
        
        self.reactive_power_after = QLineEdit()
        self.reactive_power_after.setReadOnly(True)
        results_layout.addRow("Reactive Power After:", self.reactive_power_after)
        
        self.required_reactive = QLineEdit()
        self.required_reactive.setReadOnly(True)
        results_layout.addRow("Required Reactive (Qc):", self.required_reactive)
        
        self.capacitor_size = QLineEdit()
        self.capacitor_size.setReadOnly(True)
        results_layout.addRow("Capacitor Bank Size:", self.capacitor_size)
        
        self.single_capacitor = QLineEdit()
        self.single_capacitor.setReadOnly(True)
        results_layout.addRow("Single Capacitor (std):", self.single_capacitor)
        
        results_group.setLayout(results_layout)
        main_layout.addWidget(results_group)
        
        main_layout.addStretch()
        
        # Status bar
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Ready")
    
    def _calculate(self):
        """Calculate power factor correction"""
        try:
            import math
            
            p = self.real_power.value()
            v = self.voltage.value()
            pf_current = self.current_pf.value()
            pf_target = self.target_pf.value()
            
            # Calculate angles
            angle_current = math.acos(pf_current)
            angle_target = math.acos(pf_target)
            
            # Reactive power before correction
            q_before = p * math.tan(angle_current)
            
            # Reactive power after correction
            q_after = p * math.tan(angle_target)
            
            # Required reactive power
            qc = q_before - q_after
            
            # For 3-phase system, divide by 3
            if self.system_type.currentText() == "3-Phase":
                qc = qc / 3
                v = v / 1.732  # Line to neutral voltage
            
            # Capacitor size in µF
            xc = (v ** 2) / (qc * 1000)
            c = 1 / (2 * math.pi * 50 * xc) * 1e6  # Assuming 50 Hz
            
            # Standard capacitor values
            standard_caps = [5, 10, 15, 20, 25, 30, 40, 50, 60, 75, 100, 150, 200]
            nearest_cap = min(standard_caps, key=lambda x: abs(x - c))
            
            self.reactive_power_before.setText(f"{q_before:.2f} kVAR")
            self.reactive_power_after.setText(f"{q_after:.2f} kVAR")
            self.required_reactive.setText(f"{qc:.2f} kVAR")
            self.capacitor_size.setText(f"{c:.2f} µF")
            self.single_capacitor.setText(f"{nearest_cap} µF")
            
            self.statusBar().showMessage(f"✓ Calculation complete - {nearest_cap} µF capacitor recommended")
        except Exception as e:
            self.statusBar().showMessage(f"❌ Error: {str(e)}")
    
    def _clear_all(self):
        """Clear all fields"""
        self.reactive_power_before.clear()
        self.reactive_power_after.clear()
        self.required_reactive.clear()
        self.capacitor_size.clear()
        self.single_capacitor.clear()
        self.statusBar().showMessage("Cleared")
    
    def _export(self):
        """Export design to file"""
        self.statusBar().showMessage("Export feature - Coming soon")
