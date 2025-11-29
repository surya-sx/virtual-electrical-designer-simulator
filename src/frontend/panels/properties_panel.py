"""
Advanced Properties Panel - Component customization with grouped categories
Shows properties in grouped categories with validators and unit support
"""

from PySide6.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QHBoxLayout, 
    QTreeWidget, QTreeWidgetItem, QLineEdit, QDoubleSpinBox,
    QComboBox, QLabel, QPushButton, QSpinBox, QCheckBox,
    QFileDialog, QMessageBox, QTabWidget, QScrollArea
)
from PySide6.QtGui import QFont, QIcon, QColor
from PySide6.QtCore import Qt, Signal, QSize
from dataclasses import dataclass
from typing import Dict, Any, List, Callable
import json


@dataclass
class PropertyDef:
    """Property definition with validation"""
    name: str
    category: str  # "Electrical", "Physical", "Simulation", "Advanced"
    dtype: str  # "float", "int", "string", "bool", "select", "file"
    value: Any
    unit: str = ""
    min_val: float = None
    max_val: float = None
    step: float = 0.1
    options: List[str] = None  # For select type
    validator: Callable = None
    tooltip: str = ""
    description: str = ""  # Detailed description
    instruction: str = ""  # How to use/edit this property


class PropertiesPanel(QDockWidget):
    """Advanced properties panel for component customization"""
    
    property_changed = Signal(str, str, Any)  # component_id, property_name, value
    
    PROPERTY_DEFINITIONS = {
        # Resistor properties
        "Resistor": [
            PropertyDef("Resistance", "Electrical", "float", 1000, "Ω", 0.1, 1e9, 10,
                       tooltip="Resistor value", description="Resistance opposes current flow. Measured in Ohms (Ω).",
                       instruction="Enter value and select appropriate unit. E.g., 1k = 1000Ω, 1M = 1,000,000Ω"),
            PropertyDef("Tolerance", "Electrical", "float", 5, "%", 0.1, 20, 0.1,
                       tooltip="Manufacturing tolerance", description="How much the actual resistance can vary from the specified value.",
                       instruction="Common tolerances: 1% (precision), 5% (standard), 10% (loose). Higher precision costs more."),
            PropertyDef("Power Rating", "Electrical", "float", 0.25, "W", 0.01, 1000, 0.01,
                       tooltip="Maximum power dissipation", description="Maximum power the resistor can safely dissipate without damage.",
                       instruction="Common ratings: 0.125W, 0.25W, 0.5W, 1W, 2W, 5W. Higher power = larger physical size."),
            PropertyDef("Temperature Coefficient", "Electrical", "float", 100, "ppm/°C", -500, 500, 1,
                       tooltip="Resistance change with temperature", description="How much resistance changes with temperature in parts per million per °C.",
                       instruction="Lower values indicate better temperature stability. Metal film resistors typically 25-100 ppm/°C."),
            PropertyDef("Package Type", "Physical", "select", "1206", "", options=["0402", "0603", "0805", "1206", "1210", "1812", "2512"],
                       tooltip="SMD package size", description="Physical size of the surface-mount component (in inches × 100).",
                       instruction="Smaller packages (0402) fit tighter layouts but harder to hand-solder. Larger packages easier to work with."),
            PropertyDef("Manufacturer", "Physical", "string", "Generic",
                       tooltip="Component manufacturer", description="Company that manufactures this specific resistor.",
                       instruction="Common manufacturers: Vishay, Yageo, Panasonic, Rohm. Check datasheets for exact specifications."),
            PropertyDef("Part Number", "Physical", "string", "",
                       tooltip="Manufacturer part number", description="Unique identifier from the manufacturer for ordering.",
                       instruction="Example: 'RN73H2ATTD1003B25' - needed for accurate ordering and specifications."),
        ],
        # Capacitor properties
        "Capacitor": [
            PropertyDef("Capacitance", "Electrical", "float", 1e-6, "F", 1e-12, 1, 1e-9,
                       tooltip="Capacitor value", description="Ability to store electrical energy. Measured in Farads (F).",
                       instruction="Use prefixes: pF (pico=1e-12), nF (nano=1e-9), µF (micro=1e-6), mF (milli=1e-3)"),
            PropertyDef("Voltage Rating", "Electrical", "float", 50, "V", 1, 10000, 5,
                       tooltip="Maximum voltage", description="Maximum voltage the capacitor can safely withstand.",
                       instruction="Always use capacitor with rating higher than circuit voltage. Common: 5V, 10V, 16V, 25V, 50V, 100V"),
            PropertyDef("ESR", "Electrical", "float", 0.1, "Ω", 0.001, 10, 0.01,
                       tooltip="Equivalent Series Resistance", description="Internal resistance that causes power loss and heat generation.",
                       instruction="Lower ESR is better for high-frequency applications. Ceramic: 5-100mΩ, Aluminum: 50-500mΩ"),
            PropertyDef("Dielectric", "Electrical", "select", "Ceramic", "", options=["Ceramic", "Film", "Electrolytic", "Tantalum", "Mica"],
                       tooltip="Dielectric material", description="Material between capacitor plates - affects performance and characteristics.",
                       instruction="Ceramic: compact, cheap. Film: stable, low ESR. Electrolytic: high capacitance. Tantalum: small, expensive. Mica: precision."),
            PropertyDef("Temperature Coefficient", "Electrical", "float", 100, "ppm/°C", -500, 500, 1,
                       tooltip="Capacitance change with temperature", description="How capacitance varies with temperature.",
                       instruction="Ceramic: ±5% typical. Film: ±0.1-1%. Stable temperature coefficient important for precision circuits."),
            PropertyDef("Package Type", "Physical", "select", "1206", "", options=["0402", "0603", "0805", "1206", "1210"],
                       tooltip="SMD package size", description="Physical size of the capacitor package.",
                       instruction="0402/0603 for compact designs. 1206+ for larger capacitances and easier hand assembly."),
        ],
        # Inductor properties
        "Inductor": [
            PropertyDef("Inductance", "Electrical", "float", 1e-3, "H", 1e-9, 1000, 1e-6,
                       tooltip="Inductor value", description="Ability to store energy in a magnetic field. Measured in Henries (H).",
                       instruction="Prefixes: nH (nano), µH (micro), mH (milli). Example: 1mH = 0.001H, 10µH = 0.00001H"),
            PropertyDef("DCR", "Electrical", "float", 1, "Ω", 0.001, 100, 0.01,
                       tooltip="DC Resistance", description="Wire resistance of the inductor coil.",
                       instruction="Lower DCR reduces power loss. Thick wire = lower DCR but larger inductor. Typical: 0.01-10Ω"),
            PropertyDef("Saturation Current", "Electrical", "float", 1, "A", 0.001, 1000, 0.1,
                       tooltip="Maximum safe current", description="Current above which inductance degrades due to core saturation.",
                       instruction="Operating current should be ~80% of saturation current. Higher current rating needed for power applications."),
            PropertyDef("Core Type", "Physical", "select", "Air", "", options=["Air", "Ferrite", "Iron Powder", "Laminated"],
                       tooltip="Core material", description="Material inside the coil that affects inductance and performance.",
                       instruction="Air: no saturation. Ferrite: compact, high µ. Iron Powder: moderate saturation. Laminated: large power inductors."),
            PropertyDef("Q Factor", "Electrical", "float", 100, "", 1, 10000, 10,
                       tooltip="Quality factor", description="Ratio of energy stored to energy lost per cycle. Higher is better.",
                       instruction="Q > 50: high quality. Lower Q at higher frequencies. Air core > ferrite for RF applications."),
        ],
        # Diode properties
        "Diode": [
            PropertyDef("Forward Voltage", "Electrical", "float", 0.7, "V", 0.1, 5, 0.1,
                       tooltip="Voltage drop when conducting", description="Voltage drop across diode when current flows in forward direction.",
                       instruction="Silicon: ~0.6-0.7V. Schottky: ~0.3-0.4V. Germanium: ~0.3V. Higher current slightly increases drop."),
            PropertyDef("Forward Current", "Electrical", "float", 1, "A", 0.001, 1000, 0.1,
                       tooltip="Rated forward current", description="Maximum continuous current the diode can handle safely.",
                       instruction="Common: 100mA (small signal), 1A (general purpose), 10A+ (power). Higher current = larger package."),
            PropertyDef("Reverse Leakage", "Electrical", "float", 1e-6, "A", 1e-12, 1e-3, 1e-9,
                       tooltip="Current when reverse biased", description="Small current that flows when diode is reverse biased (off).",
                       instruction="Smaller leakage is better. Affects circuit accuracy. Silicon: µA range, Germanium: higher leakage."),
            PropertyDef("Junction Capacitance", "Electrical", "float", 10e-12, "F", 1e-12, 1e-6, 1e-12,
                       tooltip="Diode junction capacitance", description="Capacitance at the PN junction affecting high-frequency performance.",
                       instruction="Matters in RF/high-speed circuits. Varactor diodes use this effect. Typical: pF range."),
            PropertyDef("Diode Type", "Electrical", "select", "Standard", "", options=["Standard", "Fast", "Schottky", "Zener", "LED"],
                       tooltip="Diode category", description="Different types optimized for different applications.",
                       instruction="Standard: general use. Fast: low reverse recovery. Schottky: low forward voltage. Zener: voltage regulation. LED: light emission."),
        ],
        # Transistor (BJT) properties
        "BJT": [
            PropertyDef("Type", "Electrical", "select", "NPN", "", options=["NPN", "PNP"],
                       tooltip="Transistor type", description="NPN uses electrons (faster), PNP uses holes (slower but complementary).",
                       instruction="NPN for high-side switching, PNP for low-side. Complementary pairs: 2N2222/2N2907, 2N3904/2N3906"),
            PropertyDef("Vce Max", "Electrical", "float", 50, "V", 1, 1000, 5,
                       tooltip="Maximum collector-emitter voltage", description="Maximum voltage that can be applied between collector and emitter.",
                       instruction="Design margin: operate at 80% max. Common: 20V, 40V, 100V, 400V+. Higher rating for power stages."),
            PropertyDef("Ic Max", "Electrical", "float", 1, "A", 0.001, 100, 0.1,
                       tooltip="Maximum collector current", description="Maximum continuous current through the transistor.",
                       instruction="Small signal: mA range. Power transistors: Amperes. Design with 50% safety margin."),
            PropertyDef("Vbe", "Electrical", "float", 0.7, "V", 0.1, 2, 0.05,
                       tooltip="Base-emitter forward voltage", description="Voltage needed to turn transistor on.",
                       instruction="NPN: ~0.6-0.7V. PNP: ~-0.6 to -0.7V. Slightly increases with current."),
            PropertyDef("Hfe", "Electrical", "float", 100, "", 10, 10000, 50,
                       tooltip="Current gain (β)", description="Amplification factor - Ic/Ib. How much base current controls collector current.",
                       instruction="Small signal: 50-300. Power: 10-100. Higher Hfe = less base current needed but more variation between parts."),
            PropertyDef("ft", "Electrical", "float", 100e6, "Hz", 1e6, 10e9, 10e6,
                       tooltip="Transition frequency", description="Frequency where current gain drops to unity (1).",
                       instruction="High frequency cutoff. 2N3904: 300MHz. 2N2222: 900MHz. For audio: 100MHz+ is plenty."),
            PropertyDef("Cob", "Electrical", "float", 5e-12, "F", 1e-12, 1e-9, 1e-12,
                       tooltip="Output (base-collector) capacitance", description="Capacitance between base and collector affecting switching speed.",
                       instruction="Lower Cob = faster switching. Typically pF range. Affects RC time constants in circuits."),
        ],
        # Op-Amp properties
        "OpAmp": [
            PropertyDef("Gain-Bandwidth", "Electrical", "float", 1e6, "Hz", 1e3, 1e9, 1e5,
                       tooltip="Gain-bandwidth product", description="Product of DC gain and -3dB bandwidth. Higher allows faster operation.",
                       instruction="TL072: 4MHz. LM358: 1MHz. OPA2134: 10MHz. Choose based on signal frequency needs."),
            PropertyDef("Supply Voltage", "Electrical", "float", 15, "V", 1, 100, 1,
                       tooltip="Operating supply voltage", description="Voltage(s) required to power the op-amp.",
                       instruction="Single: 5V, 9V, 12V, 15V, 30V. Dual (±V): ±5V, ±12V, ±15V. Check absolute maximum ratings."),
            PropertyDef("Input Impedance", "Electrical", "float", 1e6, "Ω", 1e3, 1e12, 1e6,
                       tooltip="Input impedance", description="Resistance seen at the input. Higher is better for input loading.",
                       instruction="JFET/CMOS input: 10TΩ+. Bipolar input: 1-10MΩ. Affects source impedance requirements."),
            PropertyDef("Output Impedance", "Electrical", "float", 75, "Ω", 1, 1e6, 10,
                       tooltip="Output impedance", description="Internal resistance of the output. Lower allows driving heavier loads.",
                       instruction="Typical: 50-100Ω open-loop. Use feedback to lower. Lower impedance = more current available."),
            PropertyDef("Slew Rate", "Electrical", "float", 1e6, "V/s", 1e3, 1e9, 1e5,
                       tooltip="Maximum rate of output voltage change", description="How fast the output can change voltage. Higher = less distortion.",
                       instruction="For bandwidth f: need SR > 2π*f*Vpp. Audio: 0.5V/µs fine. High frequency: 10+ V/µs."),
            PropertyDef("CMRR", "Electrical", "float", 80, "dB", 20, 160, 5,
                       tooltip="Common-Mode Rejection Ratio", description="How much the op-amp rejects signals common to both inputs. Higher is better.",
                       instruction="Typical: 80-100dB. Each 20dB = 10× improvement. Higher CMRR = better noise immunity."),
            PropertyDef("PSRR", "Electrical", "float", 80, "dB", 20, 160, 5,
                       tooltip="Power Supply Rejection Ratio", description="How much supply voltage noise is rejected. Higher is better.",
                       instruction="Similar to CMRR but for supply lines. Lower PSRR = need better power supply filtering."),
        ],
        # Voltage Source properties
        "VoltageSource": [
            PropertyDef("Voltage", "Electrical", "float", 5, "V", -1e6, 1e6, 0.1,
                       tooltip="Source voltage value", description="Output voltage of the source.",
                       instruction="Positive for sources above ground, negative for below. Can be DC value or peak AC value."),
            PropertyDef("Impedance", "Electrical", "float", 0, "Ω", 0, 1e6, 0.1,
                       tooltip="Internal source impedance", description="Internal resistance that limits current and causes voltage drop under load.",
                       instruction="Ideal source: 0Ω. Real sources: ohms to kΩ. Higher impedance = voltage drops more with load current."),
            PropertyDef("Type", "Electrical", "select", "DC", "", options=["DC", "AC", "Pulse", "Exponential"],
                       tooltip="Waveform type", description="Shape of the voltage output over time.",
                       instruction="DC: constant. AC: sinusoidal. Pulse: square wave. Exponential: rising/falling exponential."),
        ],
        # Current Source properties
        "CurrentSource": [
            PropertyDef("Current", "Electrical", "float", 1, "A", -1e6, 1e6, 0.01,
                       tooltip="Source current value", description="Output current of the source.",
                       instruction="Positive for sources flowing out, negative for flowing in. Can be DC or peak AC value."),
            PropertyDef("Type", "Electrical", "select", "DC", "", options=["DC", "AC", "Pulse", "Exponential"],
                       tooltip="Waveform type", description="Shape of the current output over time.",
                       instruction="DC: constant. AC: sinusoidal. Pulse: square wave. Exponential: rising/falling exponential."),
        ],
    }
    
    def __init__(self):
        super().__init__("Component Properties")
        self.setObjectName("PropertiesPanel")
        self.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
        
        # Main widget
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Current component label
        self.component_label = QLabel("No component selected")
        font = QFont("Segoe UI")
        font.setPointSize(10)
        font.setBold(True)
        self.component_label.setFont(font)
        self.component_label.setStyleSheet("color: #2c5aa0; background: #f0f0f0; padding: 8px; border-radius: 4px;")
        layout.addWidget(self.component_label)
        
        # Info panel for descriptions and instructions
        self.info_panel = QWidget()
        info_layout = QVBoxLayout(self.info_panel)
        info_layout.setContentsMargins(5, 5, 5, 5)
        info_layout.setSpacing(3)
        
        self.description_label = QLabel("Select a property to see details")
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("color: #555; font-size: 10px; background: #f9f9f9; padding: 6px; border-radius: 3px;")
        info_layout.addWidget(self.description_label)
        
        self.instruction_label = QLabel("")
        self.instruction_label.setWordWrap(True)
        self.instruction_label.setStyleSheet("color: #2c5aa0; font-size: 9px; background: #e3f2fd; padding: 6px; border-radius: 3px; font-style: italic;")
        self.instruction_label.setVisible(False)
        info_layout.addWidget(self.instruction_label)
        
        self.info_panel.setMaximumHeight(80)
        layout.addWidget(self.info_panel)
        
        # Tabs for different property categories
        self.tabs = QTabWidget()
        
        # Create tabs for property categories
        self.property_widgets = {}
        self.current_component = None
        self.current_properties = {}
        
        # Electrical tab
        self.electrical_scroll = QScrollArea()
        self.electrical_scroll.setWidgetResizable(True)
        self.electrical_tree = self._create_property_tree()
        self.electrical_scroll.setWidget(self.electrical_tree)
        self.tabs.addTab(self.electrical_scroll, "Electrical")
        
        # Physical tab
        self.physical_scroll = QScrollArea()
        self.physical_scroll.setWidgetResizable(True)
        self.physical_tree = self._create_property_tree()
        self.physical_scroll.setWidget(self.physical_tree)
        self.tabs.addTab(self.physical_scroll, "Physical")
        
        # Simulation tab
        self.simulation_scroll = QScrollArea()
        self.simulation_scroll.setWidgetResizable(True)
        self.simulation_tree = self._create_property_tree()
        self.simulation_scroll.setWidget(self.simulation_tree)
        self.tabs.addTab(self.simulation_scroll, "Simulation")
        
        # Advanced tab
        self.advanced_scroll = QScrollArea()
        self.advanced_scroll.setWidgetResizable(True)
        self.advanced_tree = self._create_property_tree()
        self.advanced_scroll.setWidget(self.advanced_tree)
        self.tabs.addTab(self.advanced_scroll, "Advanced")
        
        layout.addWidget(self.tabs)
        
        # Button bar
        button_layout = QHBoxLayout()
        
        self.reset_btn = QPushButton("Reset to Defaults")
        self.reset_btn.setToolTip("Reset all properties to default values")
        self.reset_btn.clicked.connect(self._reset_properties)
        button_layout.addWidget(self.reset_btn)
        
        self.import_btn = QPushButton("Import")
        self.import_btn.setToolTip("Import properties from file")
        self.import_btn.clicked.connect(self._import_properties)
        button_layout.addWidget(self.import_btn)
        
        self.export_btn = QPushButton("Export")
        self.export_btn.setToolTip("Export properties to file")
        self.export_btn.clicked.connect(self._export_properties)
        button_layout.addWidget(self.export_btn)
        
        layout.addLayout(button_layout)
        
        # Set main widget
        self.setWidget(main_widget)
        self.setMinimumWidth(300)
        self.setStyleSheet("""
            QDockWidget {
                background: #ffffff;
            }
            QLabel {
                color: #333;
            }
            QPushButton {
                background: #4CAF50;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #45a049;
            }
            QPushButton:pressed {
                background: #3d8b40;
            }
        """)
    
    def _create_property_tree(self):
        """Create a tree widget for properties"""
        tree = QTreeWidget()
        tree.setColumnCount(2)
        tree.setHeaderLabels(["Property", "Value"])
        tree.setColumnWidth(0, 150)
        tree.setColumnWidth(1, 150)
        tree.itemClicked.connect(self._on_property_selected)
        tree.itemSelectionChanged.connect(self._on_property_selected)
        tree.setStyleSheet("""
            QTreeWidget {
                background: #ffffff;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            QTreeWidget::item {
                padding: 4px;
            }
            QTreeWidget::item:selected {
                background: #e3f2fd;
            }
        """)
        return tree
    
    def load_component_properties(self, component_id: str, component_type: str, properties: Dict[str, Any] = None):
        """Load properties for selected component"""
        self.current_component = component_id
        self.component_label.setText(f"Component: {component_type} (ID: {component_id[:8]}...)")
        
        # Get property definitions
        prop_defs = self.PROPERTY_DEFINITIONS.get(component_type, [])
        
        if not prop_defs:
            self._clear_trees()
            return
        
        # Organize properties by category
        categorized = {}
        for prop_def in prop_defs:
            category = prop_def.category
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(prop_def)
        
        # Store current properties
        self.current_properties = {p.name: p for p in prop_defs}
        
        # Populate trees
        self._populate_tree_with_properties(self.electrical_tree, categorized.get("Electrical", []), properties)
        self._populate_tree_with_properties(self.physical_tree, categorized.get("Physical", []), properties)
        self._populate_tree_with_properties(self.simulation_tree, categorized.get("Simulation", []), properties)
        self._populate_tree_with_properties(self.advanced_tree, categorized.get("Advanced", []), properties)
    
    def _populate_tree_with_properties(self, tree: QTreeWidget, prop_defs: List[PropertyDef], properties: Dict = None):
        """Populate tree widget with properties"""
        tree.clear()
        
        for prop_def in prop_defs:
            item = QTreeWidgetItem()
            item.setText(0, f"{prop_def.name} ({prop_def.unit})" if prop_def.unit else prop_def.name)
            
            # Store property definition in item for later access
            item.property_def = prop_def
            
            # Get value from properties or use default
            value = properties.get(prop_def.name, prop_def.value) if properties else prop_def.value
            
            # Create value widget based on type
            if prop_def.dtype == "float":
                widget = QDoubleSpinBox()
                if prop_def.min_val is not None:
                    widget.setMinimum(prop_def.min_val)
                if prop_def.max_val is not None:
                    widget.setMaximum(prop_def.max_val)
                widget.setSingleStep(prop_def.step)
                widget.setValue(float(value))
                widget.setToolTip(prop_def.tooltip)
                
            elif prop_def.dtype == "int":
                widget = QSpinBox()
                if prop_def.min_val is not None:
                    widget.setMinimum(int(prop_def.min_val))
                if prop_def.max_val is not None:
                    widget.setMaximum(int(prop_def.max_val))
                widget.setSingleStep(int(prop_def.step))
                widget.setValue(int(value))
                widget.setToolTip(prop_def.tooltip)
                
            elif prop_def.dtype == "bool":
                widget = QCheckBox()
                widget.setChecked(bool(value))
                widget.setToolTip(prop_def.tooltip)
                
            elif prop_def.dtype == "select":
                widget = QComboBox()
                if prop_def.options:
                    widget.addItems(prop_def.options)
                widget.setCurrentText(str(value))
                widget.setToolTip(prop_def.tooltip)
                
            else:  # string or default
                widget = QLineEdit()
                widget.setText(str(value))
                widget.setToolTip(prop_def.tooltip)
            
            # Store reference for later
            widget.property_name = prop_def.name
            
            # Connect changes
            if isinstance(widget, QDoubleSpinBox):
                widget.valueChanged.connect(lambda v: self._on_property_changed(prop_def.name, v))
            elif isinstance(widget, QSpinBox):
                widget.valueChanged.connect(lambda v: self._on_property_changed(prop_def.name, v))
            elif isinstance(widget, QCheckBox):
                widget.stateChanged.connect(lambda v: self._on_property_changed(prop_def.name, widget.isChecked()))
            elif isinstance(widget, QComboBox):
                widget.currentTextChanged.connect(lambda v: self._on_property_changed(prop_def.name, v))
            else:
                widget.textChanged.connect(lambda v: self._on_property_changed(prop_def.name, v))
            
            tree.setItemWidget(item, 1, widget)
            tree.addTopLevelItem(item)
    
    def _on_property_changed(self, property_name: str, value: Any):
        """Handle property value change"""
        if self.current_component:
            self.property_changed.emit(self.current_component, property_name, value)
    
    def _on_property_selected(self):
        """Handle property selection - display description and instructions"""
        # Get selected item from current tab
        current_tree = None
        if self.tabs.currentWidget() == self.electrical_scroll:
            current_tree = self.electrical_tree
        elif self.tabs.currentWidget() == self.physical_scroll:
            current_tree = self.physical_tree
        elif self.tabs.currentWidget() == self.simulation_scroll:
            current_tree = self.simulation_tree
        elif self.tabs.currentWidget() == self.advanced_scroll:
            current_tree = self.advanced_tree
        
        if not current_tree:
            return
        
        selected_items = current_tree.selectedItems()
        if selected_items:
            item = selected_items[0]
            if hasattr(item, 'property_def'):
                prop_def = item.property_def
                
                # Update description and instruction labels
                if prop_def.description:
                    self.description_label.setText(f"<b>{prop_def.name}:</b> {prop_def.description}")
                else:
                    self.description_label.setText(f"<b>{prop_def.name}</b>")
                
                if prop_def.instruction:
                    self.instruction_label.setText(f"💡 {prop_def.instruction}")
                    self.instruction_label.setVisible(True)
                else:
                    self.instruction_label.setVisible(False)
        else:
            self.description_label.setText("Select a property to see details")
            self.instruction_label.setVisible(False)
    
    def _clear_trees(self):
        """Clear all property trees"""
        self.electrical_tree.clear()
        self.physical_tree.clear()
        self.simulation_tree.clear()
        self.advanced_tree.clear()
    
    def _reset_properties(self):
        """Reset all properties to defaults"""
        if self.current_component:
            QMessageBox.information(self, "Reset", "Properties reset to default values")
            # TODO: Implement reset logic
    
    def _import_properties(self):
        """Import properties from JSON file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Properties", "", "JSON Files (*.json)"
        )
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    props = json.load(f)
                QMessageBox.information(self, "Success", "Properties imported successfully")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to import: {str(e)}")
    
    def _export_properties(self):
        """Export properties to JSON file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Properties", "", "JSON Files (*.json)"
        )
        if file_path:
            try:
                props = {}
                for name, prop_def in self.current_properties.items():
                    props[name] = prop_def.value
                with open(file_path, 'w') as f:
                    json.dump(props, f, indent=2)
                QMessageBox.information(self, "Success", "Properties exported successfully")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export: {str(e)}")
