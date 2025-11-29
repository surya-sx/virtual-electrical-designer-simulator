"""
Component Library Panel - organized list view of components by category
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QTreeWidget, QTreeWidgetItem
from PySide6.QtCore import Qt, Signal, QMimeData, QSize
from PySide6.QtGui import QDrag


class DraggableTreeWidget(QTreeWidget):
    """Tree widget with custom drag-and-drop support"""
    
    def mouseMoveEvent(self, event):
        """Handle drag initiation on mouse move"""
        if event.buttons() == Qt.LeftButton:
            item = self.itemAt(event.pos())
            if item and item.parent() is not None:  # Not a category
                comp_type = item.data(0, Qt.UserRole + 1)
                comp_name = item.data(0, Qt.UserRole + 2)
                
                if comp_type and comp_name:
                    mime = QMimeData()
                    mime.setText(f"{comp_type}|{comp_name}")
                    mime.setData("component/type", comp_type.encode())
                    mime.setData("component/name", comp_name.encode())
                    
                    drag = QDrag(self)
                    drag.setMimeData(mime)
                    drag.exec(Qt.CopyAction)
                    return
        
        super().mouseMoveEvent(event)


class ComponentLibraryPanel(QWidget):
    """Panel displaying available components in organized categories"""
    
    # Signals
    component_selected = Signal(str, str)  # component_type, component_name
    
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        self.setLayout(layout)
        
        # Search bar
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search components...")
        self.search_box.setMinimumHeight(32)
        self.search_box.setStyleSheet("""
            QLineEdit {
                border: 2px solid #90caf9;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
                font-weight: bold;
            }
        """)
        self.search_box.textChanged.connect(self._filter_components)
        layout.addWidget(self.search_box)
        
        # Component tree
        self.tree = DraggableTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setStyleSheet("""
            QTreeWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background: white;
            }
            QTreeWidget::item {
                padding: 4px;
                height: 24px;
            }
            QTreeWidget::item:hover {
                background: #e3f2fd;
            }
            QTreeWidget::item:selected {
                background: #bbdefb;
            }
        """)
        self.tree.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.tree.setDragEnabled(True)
        layout.addWidget(self.tree)
        
        # Initialize storage dictionaries
        self.all_items = {}
        self.components_list = {}
        
        # Populate with components
        self._populate_components()
        self.tree.expandAll()
    
    def _populate_components(self):
        """Populate component tree with categories"""
        components_by_category = {
            "Passive Components": [
                ("Passive", "Resistor"),
                ("Passive", "Capacitor"),
                ("Passive", "Inductor"),
                ("Passive", "Ground"),
                ("Passive", "Variable Resistor"),
                ("Passive", "Potentiometer"),
                ("Passive", "Trimmer"),
                ("Passive", "Thermistor NTC"),
                ("Passive", "Thermistor PTC"),
                ("Passive", "Varistor"),
                ("Passive", "Ferrite Bead"),
            ],
            "Power Sources": [
                ("Active", "DC Source"),
                ("Active", "AC Source"),
                ("Active", "Battery"),
                ("Active", "Battery Cell"),
                ("Active", "Current Source"),
                ("Active", "Voltage Divider"),
                ("Active", "Power Supply"),
            ],
            "Semiconductors - Diodes": [
                ("Semiconductor", "Diode"),
                ("Semiconductor", "LED"),
                ("Semiconductor", "Zener Diode"),
                ("Semiconductor", "Schottky Diode"),
                ("Semiconductor", "Photo Diode"),
                ("Semiconductor", "Tunnel Diode"),
                ("Semiconductor", "Bridge Rectifier"),
                ("Semiconductor", "Varactor Diode"),
                ("Semiconductor", "Gunn Diode"),
            ],
            "Semiconductors - Transistors": [
                ("Semiconductor", "BJT"),
                ("Semiconductor", "BJT NPN"),
                ("Semiconductor", "BJT PNP"),
                ("Semiconductor", "MOSFET"),
                ("Semiconductor", "MOSFET N-Channel"),
                ("Semiconductor", "MOSFET P-Channel"),
                ("Semiconductor", "JFET"),
                ("Semiconductor", "IGBT"),
                ("Semiconductor", "Thyristor"),
                ("Semiconductor", "SCR"),
                ("Semiconductor", "TRIAC"),
                ("Semiconductor", "DIAC"),
            ],
            "Integrated Circuits": [
                ("IC", "Op-Amp"),
                ("IC", "741 Op-Amp"),
                ("IC", "Comparator"),
                ("IC", "Amplifier"),
                ("IC", "Voltage Regulator"),
                ("IC", "Timer 555"),
                ("IC", "Multiplexer"),
                ("IC", "Demultiplexer"),
                ("IC", "Decoder"),
                ("IC", "Encoder"),
                ("IC", "Latch"),
                ("IC", "Flip-Flop"),
                ("IC", "Counter"),
                ("IC", "Shift Register"),
                ("IC", "RAM"),
                ("IC", "ROM"),
                ("IC", "EPROM"),
                ("IC", "EEPROM"),
                ("IC", "Flash Memory"),
                ("IC", "Microcontroller"),
                ("IC", "Processor"),
                ("IC", "DSP"),
                ("IC", "PLC"),
                ("IC", "FPGA"),
                ("IC", "Oscillator"),
                ("IC", "Clock Generator"),
                ("IC", "PLL"),
            ],
            "Logic Gates & Circuits": [
                ("Logic", "AND Gate"),
                ("Logic", "OR Gate"),
                ("Logic", "NOT Gate"),
                ("Logic", "NAND Gate"),
                ("Logic", "NOR Gate"),
                ("Logic", "XOR Gate"),
                ("Logic", "XNOR Gate"),
                ("Logic", "Inverter"),
                ("Logic", "Buffer"),
                ("Logic", "Adder"),
                ("Logic", "Subtractor"),
                ("Logic", "Multiplier"),
                ("Logic", "Divider"),
            ],
            "RF & Microwave": [
                ("RF", "Antenna"),
                ("RF", "RF Amplifier"),
                ("RF", "RF Mixer"),
                ("RF", "RF Filter"),
                ("RF", "Balun"),
                ("RF", "Transformer (RF)"),
                ("RF", "Transmission Line"),
                ("RF", "Waveguide"),
                ("RF", "Oscillator (RF)"),
                ("RF", "Phase Shifter"),
                ("RF", "Attenuator"),
                ("RF", "Isolator"),
                ("RF", "Circulator"),
            ],
            "Controls & Protection": [
                ("Control", "Switch"),
                ("Control", "Relay"),
                ("Control", "Contactor"),
                ("Control", "Fuse"),
                ("Control", "Circuit Breaker"),
                ("Control", "Push Button"),
                ("Control", "Limit Switch"),
                ("Control", "Flow Switch"),
                ("Control", "Pressure Switch"),
                ("Control", "Temperature Switch"),
                ("Control", "Level Switch"),
                ("Control", "Thermal Overload"),
                ("Control", "GFCI"),
                ("Control", "Surge Protector"),
                ("Control", "Crowbar"),
                ("Control", "Klystron"),
            ],
            "Power Equipment": [
                ("Power", "Transformer"),
                ("Power", "Auto-Transformer"),
                ("Power", "Current Transformer"),
                ("Power", "Potential Transformer"),
                ("Power", "Motor"),
                ("Power", "AC Motor"),
                ("Power", "DC Motor"),
                ("Power", "Stepper Motor"),
                ("Power", "Servo Motor"),
                ("Power", "Generator"),
                ("Power", "AC Generator"),
                ("Power", "DC Generator"),
                ("Power", "Alternator"),
                ("Power", "Rectifier"),
                ("Power", "Filter"),
                ("Power", "Capacitor (Power)"),
                ("Power", "Inductor (Large)"),
                ("Power", "Choke"),
            ],
            "Measurement": [
                ("Measurement", "Ammeter"),
                ("Measurement", "Voltmeter"),
                ("Measurement", "Wattmeter"),
                ("Measurement", "Ohmmeter"),
                ("Measurement", "Multimeter"),
                ("Measurement", "Frequency Counter"),
                ("Measurement", "Oscilloscope"),
                ("Measurement", "Power Meter"),
                ("Measurement", "Clamp Meter"),
                ("Measurement", "Megohmmeter"),
                ("Measurement", "LCR Meter"),
                ("Measurement", "Network Analyzer"),
                ("Measurement", "Spectrum Analyzer"),
            ],
            "Sensors": [
                ("Sensor", "Temperature Sensor"),
                ("Sensor", "Pressure Sensor"),
                ("Sensor", "Motion Sensor (PIR)"),
                ("Sensor", "Light Sensor (LDR)"),
                ("Sensor", "Humidity Sensor"),
                ("Sensor", "Hall Effect Sensor"),
                ("Sensor", "Proximity Sensor"),
                ("Sensor", "Load Cell"),
                ("Sensor", "Accelerometer"),
                ("Sensor", "Gyroscope"),
                ("Sensor", "Magnetometer"),
                ("Sensor", "Ultrasonic Sensor"),
                ("Sensor", "Infrared Sensor"),
                ("Sensor", "Gas Sensor"),
                ("Sensor", "PH Sensor"),
                ("Sensor", "Flow Meter"),
                ("Sensor", "Level Sensor"),
                ("Sensor", "Image Sensor"),
            ],
            "Connectors & Cables": [
                ("Passive", "Wire"),
                ("Passive", "Connector"),
                ("Passive", "Connector (D-Sub)"),
                ("Passive", "Connector (RCA)"),
                ("Passive", "Connector (BNC)"),
                ("Passive", "Connector (USB)"),
                ("Passive", "Connector (Ethernet)"),
                ("Passive", "Plug"),
                ("Passive", "Socket"),
                ("Passive", "Terminal Block"),
                ("Passive", "Bus Bar"),
                ("Passive", "Coaxial Cable"),
                ("Passive", "Shielded Cable"),
            ],
            "Displays": [
                ("Display", "LED (Single)"),
                ("Display", "LED Array"),
                ("Display", "7-Segment Display"),
                ("Display", "16-Segment Display"),
                ("Display", "Dot Matrix Display"),
                ("Display", "LCD Display"),
                ("Display", "OLED Display"),
                ("Display", "E-Ink Display"),
                ("Display", "Touchscreen"),
            ],
            "Electromechanical": [
                ("Electromechanical", "Solenoid"),
                ("Electromechanical", "Electromagnet"),
                ("Electromechanical", "Buzzer"),
                ("Electromechanical", "Speaker"),
                ("Electromechanical", "Microphone"),
                ("Electromechanical", "Headphones"),
                ("Electromechanical", "Motor (Linear)"),
                ("Electromechanical", "Actuator"),
            ],
            "Cables & Interconnects": [
                ("Passive", "Single Wire"),
                ("Passive", "Cable Pair"),
                ("Passive", "Twisted Pair"),
                ("Passive", "Ribbon Cable"),
                ("Passive", "Ladder Cable"),
                ("Passive", "Multicore Cable"),
            ],
            "Miscellaneous": [
                ("Misc", "Crystal"),
                ("Misc", "Crystal Oscillator"),
                ("Misc", "Ceramic Resonator"),
                ("Misc", "Antenna"),
                ("Misc", "Heat Sink"),
                ("Misc", "Light Source"),
                ("Misc", "Fuse Holder"),
                ("Misc", "Socket (IC)"),
                ("Misc", "PCB Trace"),
                ("Misc", "Via"),
                ("Misc", "Mounting Pad"),
            ],
        }
        
        for category, items in components_by_category.items():
            cat_item = QTreeWidgetItem([category])
            cat_item.setData(0, Qt.UserRole, "category")
            self.tree.addTopLevelItem(cat_item)
            self.all_items[category] = cat_item
            
            for comp_type, comp_name in items:
                comp_item = QTreeWidgetItem([comp_name])
                comp_item.setData(0, Qt.UserRole + 1, comp_type)
                comp_item.setData(0, Qt.UserRole + 2, comp_name)
                
                # Add tooltip with component description
                tooltip = self._get_component_description(comp_name)
                comp_item.setToolTip(0, tooltip)
                
                cat_item.addChild(comp_item)
                self.all_items[comp_name] = comp_item
                self.components_list[comp_name] = (comp_type, comp_name)
        
        self.tree.expandAll()
    
    def _filter_components(self, text: str):
        """Filter components based on search text"""
        text_lower = text.lower()
        
        # Hide/show categories and items based on search
        for cat_name, cat_item in list(self.all_items.items()):
            if cat_item.data(0, Qt.UserRole) == "category":
                # Check if any child matches
                any_child_visible = False
                for i in range(cat_item.childCount()):
                    child = cat_item.child(i)
                    child_name = child.text(0).lower()
                    matches = text_lower in child_name
                    child.setHidden(not matches)
                    if matches:
                        any_child_visible = True
                
                cat_item.setHidden(not any_child_visible)
    
    def _get_component_description(self, comp_name: str) -> str:
        """Get component description for tooltip"""
        descriptions = {
            # Passive
            "Resistor": "🔌 Resistor - Resists current flow, dissipates power as heat\nPorts: 2 (two-terminal)",
            "Capacitor": "🔌 Capacitor - Stores electrical energy, blocks DC\nPorts: 2 (two-terminal)",
            "Inductor": "🔌 Inductor - Stores energy in magnetic field, opposes current change\nPorts: 2 (two-terminal)",
            "Ground": "🔌 Ground/Reference - Reference point for circuit voltages\nPorts: 1 (one-terminal connection)",
            "Potentiometer": "🔌 Variable Resistor - Adjustable resistance up to rated value\nPorts: 3 (sliding contact)",
            
            # Active
            "DC Source": "⚡ DC Voltage Source - Provides constant DC voltage\nPorts: 2 (+ positive, - negative)",
            "AC Source": "⚡ AC Voltage Source - Provides alternating voltage\nPorts: 2 (two-terminal)",
            "Battery": "🔋 Battery - Chemical energy to electrical energy source\nPorts: 2 (+ positive, - negative)",
            "Current Source": "⚡ Current Source - Supplies constant current\nPorts: 2 (two-terminal)",
            
            # Semiconductors
            "Diode": "💻 Diode - Conducts one direction, blocks reverse\nPorts: 2 (Anode +, Cathode -)",
            "LED": "💡 LED - Light Emitting Diode, conducts and emits light\nPorts: 2 (Anode +, Cathode -)",
            "Zener Diode": "💻 Zener Diode - Regulates voltage by conducting backward\nPorts: 2 (Anode +, Cathode -)",
            "BJT NPN": "💻 BJT NPN Transistor - Amplifies/switches signals\nPorts: 3 (Base, Collector, Emitter)",
            "MOSFET N-Channel": "💻 N-Channel MOSFET - Fast switching transistor\nPorts: 3 (Gate, Drain, Source)",
            "SCR": "💻 Silicon Controlled Rectifier - Power switching device\nPorts: 3 (Gate, Anode, Cathode)",
            
            # ICs
            "Op-Amp": "🔧 Operational Amplifier - Voltage amplification\nPorts: 5 (2 inputs, 1 output, 2 power)",
            "Multiplexer": "🔧 Multiplexer - Selects one input from many\nPorts: Multiple (data in, select, output)",
            "Demultiplexer": "🔧 Demultiplexer - Routes one input to many outputs\nPorts: Multiple (input, select, data out)",
            "Timer 555": "🔧 555 Timer IC - Generates pulses/oscillations\nPorts: 8 (DIP-8 package)",
            "Microcontroller": "🔧 Microcontroller - Programmable logic processor\nPorts: Multiple",
            
            # Logic
            "AND Gate": "🔧 AND Gate - Output high if all inputs high\nPorts: 2+ inputs, 1 output",
            "OR Gate": "🔧 OR Gate - Output high if any input high\nPorts: 2+ inputs, 1 output",
            "NOT Gate": "🔧 NOT Gate - Inverts input signal\nPorts: 1 input, 1 output",
            "NAND Gate": "🔧 NAND Gate - Inverted AND gate\nPorts: 2+ inputs, 1 output",
            
            # Measurement
            "Ammeter": "📊 Ammeter - Measures current (connects in series)\nPorts: 2 (two-terminal)",
            "Voltmeter": "📊 Voltmeter - Measures voltage (connects in parallel)\nPorts: 2 (two-terminal)",
            "Wattmeter": "📊 Wattmeter - Measures power\nPorts: 2+ (multiple)",
            
            # Power
            "Transformer": "⚡ Transformer - Steps voltage up/down via induction\nPorts: 4 (primary 2, secondary 2)",
            "Motor": "⚡ Motor - Converts electrical to mechanical energy\nPorts: 2+ (power connections)",
            "Generator": "⚡ Generator - Converts mechanical to electrical energy\nPorts: 2+ (power output)",
            
            # Control
            "Switch": "🔌 Switch - Manually connects/disconnects circuit\nPorts: 2 (two-terminal)",
            "Relay": "🔌 Relay - Electromagnetically controlled switch\nPorts: Multiple",
            "Fuse": "🔌 Fuse - Opens circuit if current exceeds rating\nPorts: 2 (two-terminal)",
            "Circuit Breaker": "🔌 Circuit Breaker - Automatically opens on overcurrent\nPorts: 2 (two-terminal)",
        }
        
        return descriptions.get(comp_name, f"📦 {comp_name}\nDouble-click to place on canvas")
    
    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle double-click on component item"""
        comp_type = item.data(0, Qt.UserRole + 1)
        comp_name = item.data(0, Qt.UserRole + 2)
        
        if comp_type and comp_name:
            self.component_selected.emit(comp_type, comp_name)
