"""Cable Sizing Tool - Separate Window"""
from PySide6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QGroupBox, QFormLayout, QDoubleSpinBox, QSpinBox, QWidget,
    QToolBar, QStatusBar, QScrollArea, QTableWidget, QTableWidgetItem
)
from PySide6.QtCore import QSize
from PySide6.QtGui import QFont


class CableSizingWindow(QMainWindow):
    """Tool for calculating cable sizes based on current and voltage drop"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cable Sizing Calculator")
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
        toolbar = QToolBar("Cable Sizing Toolbar")
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
        title = QLabel("Cable Sizing Calculator")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        main_layout.addWidget(title)
        
        # Input Parameters Group
        input_group = QGroupBox("Cable Requirements")
        input_layout = QFormLayout()
        
        self.current = QDoubleSpinBox()
        self.current.setMinimum(0.1)
        self.current.setMaximum(10000)
        self.current.setValue(50)
        self.current.setSuffix(" A")
        input_layout.addRow("Load Current:", self.current)
        
        self.voltage = QDoubleSpinBox()
        self.voltage.setMinimum(12)
        self.voltage.setMaximum(765000)
        self.voltage.setValue(480)
        self.voltage.setSuffix(" V")
        input_layout.addRow("Voltage:", self.voltage)
        
        self.distance = QDoubleSpinBox()
        self.distance.setMinimum(1)
        self.distance.setMaximum(10000)
        self.distance.setValue(100)
        self.distance.setSuffix(" m")
        input_layout.addRow("Distance:", self.distance)
        
        self.voltage_drop_percent = QDoubleSpinBox()
        self.voltage_drop_percent.setMinimum(0.5)
        self.voltage_drop_percent.setMaximum(10)
        self.voltage_drop_percent.setValue(3)
        self.voltage_drop_percent.setSuffix(" %")
        input_layout.addRow("Max Voltage Drop:", self.voltage_drop_percent)
        
        self.insulation = QComboBox()
        self.insulation.addItems(["Copper (90°C)", "Copper (60°C)", "Aluminum (90°C)"])
        input_layout.addRow("Conductor Type:", self.insulation)
        
        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)
        
        # Results Group
        results_group = QGroupBox("Cable Specifications")
        results_layout = QFormLayout()
        
        self.cable_size = QLineEdit()
        self.cable_size.setReadOnly(True)
        results_layout.addRow("Recommended Cable Size:", self.cable_size)
        
        self.actual_voltage_drop = QLineEdit()
        self.actual_voltage_drop.setReadOnly(True)
        results_layout.addRow("Actual Voltage Drop:", self.actual_voltage_drop)
        
        self.cable_area = QLineEdit()
        self.cable_area.setReadOnly(True)
        results_layout.addRow("Cross-Sectional Area:", self.cable_area)
        
        self.ampacity = QLineEdit()
        self.ampacity.setReadOnly(True)
        results_layout.addRow("Cable Ampacity:", self.ampacity)
        
        results_group.setLayout(results_layout)
        main_layout.addWidget(input_group)
        
        # Results Group
        results_group = QGroupBox("Cable Specifications")
        results_layout = QFormLayout()
        
        self.cable_size = QLineEdit()
        self.cable_size.setReadOnly(True)
        results_layout.addRow("Recommended Cable Size:", self.cable_size)
        
        self.actual_voltage_drop = QLineEdit()
        self.actual_voltage_drop.setReadOnly(True)
        results_layout.addRow("Actual Voltage Drop:", self.actual_voltage_drop)
        
        self.cable_area = QLineEdit()
        self.cable_area.setReadOnly(True)
        results_layout.addRow("Cross-Sectional Area:", self.cable_area)
        
        self.ampacity = QLineEdit()
        self.ampacity.setReadOnly(True)
        results_layout.addRow("Cable Ampacity:", self.ampacity)
        
        results_group.setLayout(results_layout)
        main_layout.addWidget(results_group)
        
        main_layout.addStretch()
        
        # Status bar
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Ready")
        
        # Buttons
        button_layout = QHBoxLayout()
        
        calculate_btn = QPushButton("Calculate")
        calculate_btn.clicked.connect(self._calculate)
        button_layout.addWidget(calculate_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
    def _calculate(self):
        """Calculate cable sizing"""
        try:
            current = self.current.value()
            voltage = self.voltage.value()
            distance = self.distance.value()
            max_drop_percent = self.voltage_drop_percent.value()
            
            # Standard cable sizes in mm²
            cable_sizes = [1, 1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240, 300, 400, 500, 630]
            
            # Resistivity (ohm·mm²/m) - Copper at 90°C
            resistivity = 0.0225
            
            # Allowed voltage drop (V)
            allowed_drop = (voltage * max_drop_percent) / 100
            
            # Required cross-section area (A = 2 * ρ * L * I / U_drop)
            required_area = (2 * resistivity * distance * current) / allowed_drop
            
            # Find suitable cable size
            suitable_size = None
            for size in cable_sizes:
                if size >= required_area:
                    suitable_size = size
                    break
            
            if suitable_size is None:
                suitable_size = cable_sizes[-1]
            
            # Calculate actual voltage drop
            actual_drop = (2 * resistivity * distance * current) / suitable_size
            actual_drop_percent = (actual_drop / voltage) * 100
            
            self.cable_size.setText(f"{suitable_size} mm²")
            self.actual_voltage_drop.setText(f"{actual_drop:.2f} V ({actual_drop_percent:.2f}%)")
            self.cable_area.setText(f"{suitable_size} mm²")
            self.ampacity.setText(f"~{suitable_size * 5:.0f} A @ 90°C")
            
            self.statusBar().showMessage(f"✓ Calculation complete - {suitable_size} mm² cable recommended")
        except Exception as e:
            self.statusBar().showMessage(f"❌ Error: {str(e)}")
    
    def _clear_all(self):
        """Clear all fields"""
        self.cable_size.clear()
        self.actual_voltage_drop.clear()
        self.cable_area.clear()
        self.ampacity.clear()
        self.statusBar().showMessage("Cleared")
    
    def _export(self):
        """Export design to file"""
        self.statusBar().showMessage("Export feature - Coming soon")
