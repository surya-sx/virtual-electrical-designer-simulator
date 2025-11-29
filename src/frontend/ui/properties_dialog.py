"""
Component Properties Dialog for Virtual Electrical Designer
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QSpinBox, QDoubleSpinBox, QComboBox, QPushButton, QFormLayout, QGroupBox, QTextEdit
)
from PySide6.QtCore import Qt


# Component descriptions and jobs
COMPONENT_DESCRIPTIONS = {
    "resistor": "Limits current flow. Used to control voltage drops, set bias points, and dissipate power.",
    "capacitor": "Stores electrical charge. Used for filtering, coupling, timing, and energy storage.",
    "inductor": "Stores magnetic energy. Used for filtering, energy storage, and impedance matching.",
    "diode": "One-way valve for current. Used for rectification, protection, and signal routing.",
    "led": "Light-emitting diode. Emits light when forward biased. Used for indicators and displays.",
    "transistor": "Amplifies or switches current. Used for amplification, switching, and digital circuits.",
    "mosfet": "Voltage-controlled switch. Used for high-speed switching and power applications.",
    "jfet": "Junction field-effect transistor. Used for low-noise amplification and switching.",
    "battery": "Provides DC voltage. Power source for circuits.",
    "ac source": "Provides AC voltage. Used for AC circuit analysis and power systems.",
    "ground": "Reference point for voltage measurements. Returns circuit current to source.",
    "switch": "Controls circuit connection manually. Used to connect/disconnect circuit paths.",
    "relay": "Electromagnetic switch. Uses coil to control contacts remotely.",
    "motor": "Converts electrical energy to mechanical motion. Used for mechanical automation.",
    "generator": "Converts mechanical motion to electrical energy.",
    "transformer": "Transfers energy between circuits using inductive coupling. Steps voltage up/down.",
    "op-amp": "High-gain amplifier. Used for signal amplification, filtering, and computational circuits.",
    "ic": "Integrated circuit. Contains many transistors for specific functions (logic, memory, processors).",
    "ammeter": "Measures current. Connected in series with circuit.",
    "voltmeter": "Measures voltage. Connected in parallel with component.",
    "wattmeter": "Measures power consumption.",
    "fuse": "Protective device that breaks circuit if current exceeds rating.",
    "circuit breaker": "Reusable protective device that trips on overcurrent.",
    "antenna": "Radiates or receives electromagnetic waves. Used for wireless communication.",
    "crystal": "Frequency reference oscillator. Used for timing and clock generation.",
    "speaker": "Converts electrical signals to sound waves.",
    "microphone": "Converts sound waves to electrical signals.",
    "led (display)": "Visual indicators for digital or analog information.",
    "sensor": "Detects physical quantities and converts to electrical signals.",
}


class PropertiesDialog(QDialog):
    """Dialog for editing component properties"""
    
    def __init__(self, parent, component_name: str, component_type: str, params: dict = None):
        super().__init__(parent)
        self.setWindowTitle(f"Properties - {component_name}")
        self.setGeometry(200, 200, 500, 600)
        self.component_name = component_name
        self.component_type = component_type
        self.params = params or {}
        self.form_fields = {}
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel(f"{self.component_name}")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #2196F3;")
        layout.addWidget(title)
        
        # Component type and description
        type_label = QLabel(f"Type: {self.component_type}")
        type_label.setStyleSheet("font-style: italic; color: #666;")
        layout.addWidget(type_label)
        
        # Description
        comp_key = self.component_type.lower()
        description = COMPONENT_DESCRIPTIONS.get(comp_key, "Standard electrical component.")
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("background-color: #f5f5f5; padding: 8px; border-radius: 4px;")
        layout.addWidget(desc_label)
        
        layout.addSpacing(10)
        
        # Form layout for properties
        form_layout = QFormLayout()
        
        # Basic properties
        self._add_text_field(form_layout, "Name", self.component_name, False)
        self._add_text_field(form_layout, "Type", self.component_type, False)
        
        # Component-specific properties based on component type
        comp_lower = self.component_type.lower()
        
        if "resistor" in comp_lower or "variable resistor" in comp_lower or "potentiometer" in comp_lower or "trimmer" in comp_lower:
            self._add_double_field(form_layout, "Resistance (Ω)", "resistance", 1000.0)
            self._add_double_field(form_layout, "Tolerance (%)", "tolerance", 5.0)
            self._add_text_field(form_layout, "Color Code", "color_code", "Brown-Black-Red")
            self._add_text_field(form_layout, "Power Rating (W)", "power_rating", "0.25")
        
        elif "thermistor" in comp_lower:
            self._add_text_field(form_layout, "Thermistor Type", "thermistor_type", "NTC/PTC")
            self._add_double_field(form_layout, "Resistance @ 25°C (Ω)", "resistance_25c", 10000.0)
            self._add_double_field(form_layout, "Temperature Coefficient (%/°C)", "temp_coefficient", -4.7)
        
        elif "varistor" in comp_lower:
            self._add_double_field(form_layout, "Varistor Voltage (V)", "varistor_voltage", 470.0)
            self._add_double_field(form_layout, "Clamping Voltage (V)", "clamping_voltage", 650.0)
            self._add_double_field(form_layout, "Max Surge Current (A)", "surge_current", 30.0)
        
        elif "capacitor" in comp_lower:
            self._add_double_field(form_layout, "Capacitance (F)", "capacitance", 1e-6)
            self._add_double_field(form_layout, "Voltage Rating (V)", "voltage_rating", 50.0)
            self._add_combo_field(form_layout, "Type", "capacitor_type", ["Film", "Ceramic", "Electrolytic", "Tantalum", "Mica"])
            self._add_text_field(form_layout, "Tolerance", "tolerance", "±10%")
            self._add_text_field(form_layout, "Temperature Coefficient", "temp_coeff", "X7R")
        
        elif "inductor" in comp_lower:
            self._add_double_field(form_layout, "Inductance (H)", "inductance", 1e-3)
            self._add_double_field(form_layout, "DC Resistance (Ω)", "dc_resistance", 0.5)
            self._add_double_field(form_layout, "Current Rating (A)", "current_rating", 1.0)
            self._add_double_field(form_layout, "Frequency Range (MHz)", "frequency_range", 1.0)
        
        elif "battery" in comp_lower or "dc source" in comp_lower:
            self._add_double_field(form_layout, "Voltage (V)", "voltage", 12.0)
            self._add_double_field(form_layout, "Internal Resistance (Ω)", "internal_resistance", 0.1)
            self._add_text_field(form_layout, "Battery Type", "battery_type", "Alkaline/Li-Ion/Lead-Acid")
            self._add_text_field(form_layout, "Capacity (mAh)", "capacity", "2000")
        
        elif "ac source" in comp_lower or "ac source" in comp_lower:
            self._add_double_field(form_layout, "Amplitude (V)", "amplitude", 230.0)
            self._add_double_field(form_layout, "Frequency (Hz)", "frequency", 50.0)
            self._add_double_field(form_layout, "Phase (°)", "phase", 0.0)
            self._add_combo_field(form_layout, "Waveform", "waveform", ["Sine", "Square", "Triangle", "Sawtooth"])
        
        elif "current source" in comp_lower:
            self._add_double_field(form_layout, "Current (A)", "current", 1.0)
            self._add_double_field(form_layout, "Frequency (Hz)", "frequency", 0.0)
        
        elif "diode" in comp_lower:
            self._add_combo_field(form_layout, "Diode Type", "diode_type", ["Standard", "Zener", "Schottky", "Tunnel", "Varactor", "Photodiode"])
            self._add_double_field(form_layout, "Forward Voltage (V)", "vf", 0.7)
            self._add_double_field(form_layout, "Reverse Voltage (V)", "vr", 100.0)
            self._add_double_field(form_layout, "Max Current (A)", "max_current", 1.0)
            self._add_text_field(form_layout, "Part Number", "part_number", "1N4007")
        
        elif "led" in comp_lower:
            self._add_combo_field(form_layout, "Color", "color", ["Red", "Green", "Blue", "Yellow", "White", "Orange", "UV"])
            self._add_double_field(form_layout, "Forward Voltage (V)", "vf", 2.0)
            self._add_double_field(form_layout, "Max Current (A)", "max_current", 0.02)
            self._add_double_field(form_layout, "Luminous Intensity (mcd)", "brightness", 5000.0)
        
        elif "transistor" in comp_lower or "bjt" in comp_lower:
            self._add_combo_field(form_layout, "Transistor Type", "transistor_type", ["NPN", "PNP"])
            self._add_double_field(form_layout, "Beta (hFE)", "beta", 100.0)
            self._add_double_field(form_layout, "Max VCE (V)", "max_vce", 20.0)
            self._add_double_field(form_layout, "Max IC (A)", "max_ic", 0.5)
            self._add_text_field(form_layout, "Part Number", "part_number", "2N2222")
        
        elif "mosfet" in comp_lower:
            self._add_combo_field(form_layout, "Channel Type", "channel_type", ["N-Channel", "P-Channel"])
            self._add_double_field(form_layout, "VGS(th) - Gate Threshold (V)", "vgs_th", 2.0)
            self._add_double_field(form_layout, "RDS(on) - On Resistance (Ω)", "rds_on", 0.1)
            self._add_double_field(form_layout, "Max ID (A)", "max_id", 30.0)
            self._add_text_field(form_layout, "Part Number", "part_number", "IRF540")
        
        elif "jfet" in comp_lower:
            self._add_combo_field(form_layout, "Channel Type", "channel_type", ["N-Channel", "P-Channel"])
            self._add_double_field(form_layout, "VGS(off) - Pinch-off (V)", "vgs_off", -2.0)
            self._add_double_field(form_layout, "IDSS - Drain Current (mA)", "idss", 10.0)
            self._add_double_field(form_layout, "Noise Figure (dB)", "noise_figure", 0.5)
        
        elif "switch" in comp_lower or "push button" in comp_lower:
            self._add_combo_field(form_layout, "Switch Type", "switch_type", ["SPST", "SPDT", "DPST", "DPDT"])
            self._add_double_field(form_layout, "Contact Resistance (mΩ)", "contact_resistance", 10.0)
            self._add_text_field(form_layout, "Contact Rating", "contact_rating", "10A @ 250VAC")
        
        elif "relay" in comp_lower:
            self._add_double_field(form_layout, "Coil Voltage (V)", "coil_voltage", 12.0)
            self._add_double_field(form_layout, "Coil Resistance (Ω)", "coil_resistance", 100.0)
            self._add_double_field(form_layout, "Coil Power (W)", "coil_power", 0.5)
            self._add_combo_field(form_layout, "Contact Type", "contact_type", ["SPST", "SPDT", "DPDT"])
            self._add_text_field(form_layout, "Contact Rating", "contact_rating", "10A @ 250VAC")
        
        elif "transformer" in comp_lower:
            self._add_double_field(form_layout, "Primary Turns", "primary_turns", 100.0)
            self._add_double_field(form_layout, "Secondary Turns", "secondary_turns", 50.0)
            self._add_double_field(form_layout, "Coupling Coefficient (k)", "coupling", 0.95)
            self._add_double_field(form_layout, "Core Loss (%)", "core_loss", 2.0)
            self._add_text_field(form_layout, "Core Material", "core_material", "Iron/Ferrite")
        
        elif "motor" in comp_lower:
            self._add_combo_field(form_layout, "Motor Type", "motor_type", ["AC", "DC", "Stepper", "Servo", "Linear"])
            self._add_double_field(form_layout, "Power Rating (W)", "power_rating", 1000.0)
            self._add_double_field(form_layout, "Voltage (V)", "voltage", 230.0)
            self._add_double_field(form_layout, "Speed (RPM)", "speed", 1500.0)
            self._add_double_field(form_layout, "Current (A)", "current", 5.0)
        
        elif "generator" in comp_lower:
            self._add_combo_field(form_layout, "Generator Type", "generator_type", ["AC", "DC"])
            self._add_double_field(form_layout, "Power Rating (W)", "power_rating", 1000.0)
            self._add_double_field(form_layout, "Voltage (V)", "voltage", 230.0)
            self._add_double_field(form_layout, "Frequency (Hz)", "frequency", 50.0)
        
        elif "ammeter" in comp_lower:
            self._add_double_field(form_layout, "Max Range (A)", "max_range", 10.0)
            self._add_double_field(form_layout, "Internal Resistance (mΩ)", "internal_resistance", 10.0)
            self._add_combo_field(form_layout, "Type", "ammeter_type", ["Analog", "Digital"])
        
        elif "voltmeter" in comp_lower:
            self._add_double_field(form_layout, "Max Range (V)", "max_range", 1000.0)
            self._add_double_field(form_layout, "Input Impedance (MΩ)", "input_impedance", 10.0)
            self._add_combo_field(form_layout, "Type", "voltmeter_type", ["Analog", "Digital"])
        
        elif "wattmeter" in comp_lower:
            self._add_double_field(form_layout, "Max Power (W)", "max_power", 10000.0)
            self._add_double_field(form_layout, "Voltage Range (V)", "voltage_range", 500.0)
            self._add_double_field(form_layout, "Current Range (A)", "current_range", 20.0)
        
        elif "fuse" in comp_lower:
            self._add_double_field(form_layout, "Rating (A)", "rating", 5.0)
            self._add_text_field(form_layout, "Type", "fuse_type", "Fast/Slow")
            self._add_text_field(form_layout, "Voltage Rating (V)", "voltage_rating", "250/600")
            self._add_text_field(form_layout, "Size", "fuse_size", "5x20mm")
        
        elif "circuit breaker" in comp_lower:
            self._add_double_field(form_layout, "Trip Current (A)", "trip_current", 20.0)
            self._add_double_field(form_layout, "Voltage Rating (V)", "voltage_rating", 250.0)
            self._add_text_field(form_layout, "Trip Characteristic", "trip_characteristic", "Type B/C/D")
        
        elif "op-amp" in comp_lower or "op amp" in comp_lower or "741" in comp_lower:
            self._add_double_field(form_layout, "Open Loop Gain (V/V)", "gain", 100000.0)
            self._add_double_field(form_layout, "Bandwidth (-3dB) (Hz)", "bandwidth", 1e6)
            self._add_double_field(form_layout, "Supply Voltage (V)", "supply_voltage", 15.0)
            self._add_double_field(form_layout, "Input Offset Voltage (mV)", "offset_voltage", 1.0)
            self._add_text_field(form_layout, "Package", "package", "DIP-8/SOIC-8")
        
        elif "ic" in comp_lower or "timer" in comp_lower or "comparator" in comp_lower:
            self._add_text_field(form_layout, "Part Number", "part_number", "555/LM393")
            self._add_text_field(form_layout, "Package", "package", "DIP-8")
            self._add_double_field(form_layout, "Supply Voltage (V)", "supply_voltage", 5.0)
            self._add_text_field(form_layout, "Function", "function", "Timer/Comparator/Counter")
        
        elif "antenna" in comp_lower:
            self._add_text_field(form_layout, "Antenna Type", "antenna_type", "Dipole/Monopole/Patch")
            self._add_double_field(form_layout, "Frequency (MHz)", "frequency", 2400.0)
            self._add_double_field(form_layout, "Gain (dBi)", "gain", 2.0)
            self._add_text_field(form_layout, "Polarization", "polarization", "Vertical/Horizontal")
        
        elif "crystal" in comp_lower:
            self._add_double_field(form_layout, "Frequency (MHz)", "frequency", 16.0)
            self._add_double_field(form_layout, "Load Capacitance (pF)", "load_capacitance", 20.0)
            self._add_text_field(form_layout, "Accuracy (ppm)", "accuracy", "±20")
        
        elif "speaker" in comp_lower or "buzzer" in comp_lower:
            self._add_double_field(form_layout, "Impedance (Ω)", "impedance", 8.0)
            self._add_double_field(form_layout, "Power Rating (W)", "power_rating", 5.0)
            self._add_double_field(form_layout, "Frequency Range (Hz)", "frequency_range", 100.0)
            self._add_text_field(form_layout, "Type", "speaker_type", "Dynamic/Piezo")
        
        elif "sensor" in comp_lower or "temperature" in comp_lower:
            self._add_text_field(form_layout, "Sensor Type", "sensor_type", "Temperature/Pressure/Motion")
            self._add_double_field(form_layout, "Range", "range", 100.0)
            self._add_double_field(form_layout, "Sensitivity", "sensitivity", 10.0)
            self._add_text_field(form_layout, "Output Type", "output_type", "Analog/Digital")
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self._apply_properties)
        
        button_layout.addStretch()
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(apply_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def _add_text_field(self, form_layout, label_text, key, value="", read_only=False):
        """Add a text input field"""
        field = QLineEdit()
        field.setText(str(self.params.get(key, value)))
        field.setReadOnly(read_only)
        form_layout.addRow(label_text, field)
        self.form_fields[key] = field
    
    def _add_double_field(self, form_layout, label_text, key, default=0.0):
        """Add a double spin box field"""
        field = QDoubleSpinBox()
        field.setValue(float(self.params.get(key, default)))
        field.setRange(-1e9, 1e9)
        field.setDecimals(6)
        form_layout.addRow(label_text, field)
        self.form_fields[key] = field
    
    def _add_combo_field(self, form_layout, label_text, key, options):
        """Add a combo box field"""
        field = QComboBox()
        field.addItems(options)
        if key in self.params:
            idx = field.findText(str(self.params[key]))
            if idx >= 0:
                field.setCurrentIndex(idx)
        form_layout.addRow(label_text, field)
        self.form_fields[key] = field
    
    def get_properties(self):
        """Get the current property values"""
        properties = {}
        for key, field in self.form_fields.items():
            if isinstance(field, QLineEdit):
                properties[key] = field.text()
            elif isinstance(field, (QSpinBox, QDoubleSpinBox)):
                properties[key] = field.value()
            elif isinstance(field, QComboBox):
                properties[key] = field.currentText()
        return properties
    
    def _apply_properties(self):
        """Apply properties without closing (internal use)"""
        # This can be extended to update the component in real-time
        pass
