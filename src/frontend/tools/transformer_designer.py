"""Transformer Designer Tool - Separate Window"""
from PySide6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QSpinBox, QDoubleSpinBox,
    QGroupBox, QFormLayout, QWidget, QToolBar, QStatusBar, QScrollArea
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QIcon


class TransformerDesignerWindow(QMainWindow):
    """Transformer Designer Tool in separate window"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Transformer Designer Tool")
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
        toolbar = QToolBar("Transformer Toolbar")
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
        title = QLabel("Transformer Design Calculator")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        main_layout.addWidget(title)
        
        # Input Parameters Group
        input_group = QGroupBox("Design Parameters")
        input_layout = QFormLayout()
        
        self.power_spinbox = QDoubleSpinBox()
        self.power_spinbox.setMinimum(0.1)
        self.power_spinbox.setMaximum(100000)
        self.power_spinbox.setValue(10)
        self.power_spinbox.setSuffix(" kVA")
        input_layout.addRow("Power Rating:", self.power_spinbox)
        
        self.primary_voltage = QDoubleSpinBox()
        self.primary_voltage.setMinimum(110)
        self.primary_voltage.setMaximum(765000)
        self.primary_voltage.setValue(480)
        self.primary_voltage.setSuffix(" V")
        input_layout.addRow("Primary Voltage:", self.primary_voltage)
        
        self.secondary_voltage = QDoubleSpinBox()
        self.secondary_voltage.setMinimum(12)
        self.secondary_voltage.setMaximum(765000)
        self.secondary_voltage.setValue(240)
        self.secondary_voltage.setSuffix(" V")
        input_layout.addRow("Secondary Voltage:", self.secondary_voltage)
        
        self.frequency = QComboBox()
        self.frequency.addItems(["50 Hz", "60 Hz"])
        input_layout.addRow("Frequency:", self.frequency)
        
        self.efficiency = QDoubleSpinBox()
        self.efficiency.setMinimum(80)
        self.efficiency.setMaximum(99.9)
        self.efficiency.setValue(96)
        self.efficiency.setSuffix(" %")
        input_layout.addRow("Efficiency:", self.efficiency)
        
        self.type = QComboBox()
        self.type.addItems(["Step-Down", "Step-Up", "Isolation"])
        input_layout.addRow("Transformer Type:", self.type)
        
        self.cooling = QComboBox()
        self.cooling.addItems(["Oil-Immersed", "Dry-Type", "Cast-Resin"])
        input_layout.addRow("Cooling Method:", self.cooling)
        
        self.impedance = QDoubleSpinBox()
        self.impedance.setMinimum(1)
        self.impedance.setMaximum(50)
        self.impedance.setValue(5.75)
        self.impedance.setSuffix(" %")
        input_layout.addRow("Impedance Voltage:", self.impedance)
        
        self.phase = QComboBox()
        self.phase.addItems(["3-Phase", "Single-Phase"])
        input_layout.addRow("Phase Configuration:", self.phase)
        
        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)
        
        # Results Group
        results_group = QGroupBox("Calculated Results")
        results_layout = QFormLayout()
        
        self.primary_current = QLineEdit()
        self.primary_current.setReadOnly(True)
        results_layout.addRow("Primary Current:", self.primary_current)
        
        self.secondary_current = QLineEdit()
        self.secondary_current.setReadOnly(True)
        results_layout.addRow("Secondary Current:", self.secondary_current)
        
        self.turns_ratio = QLineEdit()
        self.turns_ratio.setReadOnly(True)
        results_layout.addRow("Turns Ratio (Np/Ns):", self.turns_ratio)
        
        self.core_area = QLineEdit()
        self.core_area.setReadOnly(True)
        results_layout.addRow("Core Cross-Section:", self.core_area)
        
        self.impedance_voltage = QLineEdit()
        self.impedance_voltage.setReadOnly(True)
        results_layout.addRow("Impedance Voltage:", self.impedance_voltage)
        
        self.losses = QLineEdit()
        self.losses.setReadOnly(True)
        results_layout.addRow("Estimated Losses:", self.losses)
        
        self.weight = QLineEdit()
        self.weight.setReadOnly(True)
        results_layout.addRow("Estimated Weight:", self.weight)
        
        results_group.setLayout(results_layout)
        main_layout.addWidget(results_group)
        
        # Standards table
        table_group = QGroupBox("Standard Transformer Ratings")
        table_layout = QVBoxLayout()
        
        self.standards_table = QTableWidget()
        self.standards_table.setColumnCount(3)
        self.standards_table.setHorizontalHeaderLabels(["Rating (kVA)", "Primary (V)", "Secondary (V)"])
        self.standards_table.setColumnWidth(0, 150)
        self.standards_table.setColumnWidth(1, 200)
        self.standards_table.setColumnWidth(2, 200)
        self.standards_table.setMaximumHeight(200)
        
        # Add standard ratings
        standard_ratings = [
            ("10", "480", "240"),
            ("15", "480", "240"),
            ("25", "480", "240"),
            ("50", "480", "240"),
            ("75", "480", "240"),
            ("100", "480", "240"),
        ]
        
        for i, (kva, pv, sv) in enumerate(standard_ratings):
            self.standards_table.insertRow(i)
            self.standards_table.setItem(i, 0, QTableWidgetItem(kva))
            self.standards_table.setItem(i, 1, QTableWidgetItem(pv))
            self.standards_table.setItem(i, 2, QTableWidgetItem(sv))
        
        table_layout.addWidget(self.standards_table)
        table_group.setLayout(table_layout)
        main_layout.addWidget(table_group)
        
        main_layout.addStretch()
        
        # Status bar
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Ready")
    
    def _calculate(self):
        """Calculate transformer parameters"""
        try:
            power = self.power_spinbox.value()
            v_primary = self.primary_voltage.value()
            v_secondary = self.secondary_voltage.value()
            
            # Calculate currents
            i_primary = (power * 1000) / v_primary
            i_secondary = (power * 1000) / v_secondary
            
            # Calculate turns ratio
            turns_ratio = v_primary / v_secondary
            
            # Estimate core area (simplified)
            core_area = (power * 1000) / (4.44 * 50 * 1.5)
            
            # Losses
            efficiency = self.efficiency.value()
            losses = power * (100 - efficiency) / 100
            
            # Estimate weight (oil-immersed, ~10 kg per kVA for larger transformers)
            weight = power * 0.8 if power < 50 else power * 0.6
            
            self.primary_current.setText(f"{i_primary:.2f} A")
            self.secondary_current.setText(f"{i_secondary:.2f} A")
            self.turns_ratio.setText(f"{turns_ratio:.2f}")
            self.core_area.setText(f"{core_area:.2f} cm²")
            self.impedance_voltage.setText(f"{self.impedance.value():.2f} %")
            self.losses.setText(f"{losses:.2f} kW")
            self.weight.setText(f"{weight:.1f} kg")
            
            self.statusBar().showMessage(f"✓ Calculation complete for {power} kVA transformer")
        except Exception as e:
            self.statusBar().showMessage(f"❌ Error: {str(e)}")
    
    def _clear_all(self):
        """Clear all fields"""
        self.primary_current.clear()
        self.secondary_current.clear()
        self.turns_ratio.clear()
        self.core_area.clear()
        self.impedance_voltage.clear()
        self.losses.clear()
        self.weight.clear()
        self.statusBar().showMessage("Cleared")
    
    def _export(self):
        """Export design to file"""
        self.statusBar().showMessage("Export feature - Coming soon")
