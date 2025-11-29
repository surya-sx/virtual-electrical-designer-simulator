"""
Organized Toolbar for Virtual Electrical Designer & Simulator
Organized sections: File, Edit, Drawing, Simulation, View, Tools
"""

from PySide6.QtWidgets import QToolBar, QSpinBox, QDoubleSpinBox, QLabel, QComboBox
from PySide6.QtGui import QIcon, QFont
from PySide6.QtCore import Qt, Signal, QSize


class Toolbar(QToolBar):
    """Organized toolbar with sections"""
    
    # File signals
    new_clicked = Signal()
    open_clicked = Signal()
    save_clicked = Signal()
    
    # Edit signals
    undo_clicked = Signal()
    redo_clicked = Signal()
    cut_clicked = Signal()
    copy_clicked = Signal()
    paste_clicked = Signal()
    delete_clicked = Signal()
    duplicate_clicked = Signal()
    
    # Drawing signals
    marquee_clicked = Signal(bool)
    select_all_clicked = Signal()
    rotate_clicked = Signal()
    rotate_left_clicked = Signal()
    line_width_changed = Signal(int)
    
    # Simulation signals
    run_clicked = Signal()
    pause_clicked = Signal()
    stop_clicked = Signal()
    time_changed = Signal(float)
    
    # View signals
    zoom_in_clicked = Signal()
    zoom_out_clicked = Signal()
    fit_to_window_clicked = Signal()
    grid_toggle_clicked = Signal()
    
    # Tools signals
    script_editor_clicked = Signal()
    library_manager_clicked = Signal()
    transformer_designer_clicked = Signal()
    cable_sizing_clicked = Signal()
    fault_calculator_clicked = Signal()
    pf_correction_clicked = Signal()
    battery_tool_clicked = Signal()
    waveform_viewer_clicked = Signal()
    properties_panel_clicked = Signal()
    component_browser_clicked = Signal()
    circuit_analyzer_clicked = Signal()
    design_wizard_clicked = Signal()
    measurement_tools_clicked = Signal()
    simulation_monitor_clicked = Signal()
    simulation_library_clicked = Signal()
    import_library_clicked = Signal()
    scope_clicked = Signal()
    
    def __init__(self):
        super().__init__("Toolbar")
        self.setObjectName("Toolbar")
        self.setMovable(False)
        self.setIconSize(QSize(20, 20))
        self.setFloatable(False)
        
        # Clean, simple styling
        self.setStyleSheet("""
            QToolBar {
                background: #f5f5f5;
                border-bottom: 1px solid #d0d0d0;
                spacing: 5px;
                padding: 5px;
            }
            QToolButton {
                background: transparent;
                border: 1px solid transparent;
                border-radius: 3px;
                padding: 3px 5px;
                margin: 1px;
                font-size: 11px;
            }
            QToolButton:hover {
                background: #e3f2fd;
                border: 1px solid #90caf9;
            }
            QToolButton:pressed {
                background: #bbdefb;
            }
            QToolButton:checked {
                background: #64b5f6;
                color: white;
            }
            QLabel {
                font-size: 10px;
                font-weight: bold;
                color: #1976d2;
                margin: 0px 8px;
            }
            QSpinBox, QDoubleSpinBox, QComboBox {
                font-size: 10px;
                padding: 2px;
                border: 1px solid #bbb;
                border-radius: 2px;
            }
        """)
        
        def icon(name):
            return QIcon.fromTheme(name) if QIcon.hasThemeIcon(name) else QIcon()
        
        # FILE SECTION
        self.addWidget(self._make_label("FILE"))
        self.new_action = self.addAction(icon("document-new"), "New")
        self.new_action.setToolTip("New Project (Ctrl+N)")
        self.new_action.setShortcut("Ctrl+N")
        
        self.open_action = self.addAction(icon("document-open"), "Open")
        self.open_action.setToolTip("Open Project (Ctrl+O)")
        self.open_action.setShortcut("Ctrl+O")
        
        self.save_action = self.addAction(icon("document-save"), "Save")
        self.save_action.setToolTip("Save Project (Ctrl+S)")
        self.save_action.setShortcut("Ctrl+S")
        self.addSeparator()
        
        # EDIT SECTION
        self.addWidget(self._make_label("EDIT"))
        self.undo_action = self.addAction(icon("edit-undo"), "Undo")
        self.undo_action.setToolTip("Undo (Ctrl+Z)")
        self.undo_action.setShortcut("Ctrl+Z")
        self.undo_action.setEnabled(False)
        
        self.redo_action = self.addAction(icon("edit-redo"), "Redo")
        self.redo_action.setToolTip("Redo (Ctrl+Y)")
        self.redo_action.setShortcut("Ctrl+Y")
        self.redo_action.setEnabled(False)
        
        self.cut_action = self.addAction(icon("edit-cut"), "Cut")
        self.cut_action.setToolTip("Cut (Ctrl+X)")
        self.cut_action.setShortcut("Ctrl+X")
        self.cut_action.setEnabled(False)
        
        self.copy_action = self.addAction(icon("edit-copy"), "Copy")
        self.copy_action.setToolTip("Copy (Ctrl+C)")
        self.copy_action.setShortcut("Ctrl+C")
        self.copy_action.setEnabled(False)
        
        self.paste_action = self.addAction(icon("edit-paste"), "Paste")
        self.paste_action.setToolTip("Paste (Ctrl+V)")
        self.paste_action.setShortcut("Ctrl+V")
        self.paste_action.setEnabled(False)
        
        self.delete_action = self.addAction(icon("edit-delete"), "Delete")
        self.delete_action.setToolTip("Delete (Del)")
        self.delete_action.setShortcut("Delete")
        self.delete_action.setEnabled(False)
        
        self.duplicate_action = self.addAction(icon("edit-duplicate"), "Duplicate")
        self.duplicate_action.setToolTip("Duplicate (Ctrl+D)")
        self.duplicate_action.setShortcut("Ctrl+D")
        self.duplicate_action.setEnabled(False)
        self.addSeparator()
        
        # DRAWING SECTION
        self.addWidget(self._make_label("DRAWING"))
        self.marquee_action = self.addAction(icon("edit-select-all"), "Select")
        self.marquee_action.setToolTip("Marquee Select (M)")
        self.marquee_action.setShortcut("M")
        self.marquee_action.setCheckable(True)
        
        self.select_all_action = self.addAction(icon("edit-select-all"), "Select All")
        self.select_all_action.setToolTip("Select All (Ctrl+A)")
        self.select_all_action.setShortcut("Ctrl+A")
        
        self.rotate_action = self.addAction(icon("object-rotate-right"), "Rotate")
        self.rotate_action.setToolTip("Rotate 90° CW (R)")
        self.rotate_action.setShortcut("R")
        self.rotate_action.setEnabled(False)
        
        self.rotate_left_action = self.addAction(icon("object-rotate-left"), "Rotate L")
        self.rotate_left_action.setToolTip("Rotate 90° CCW (Shift+R)")
        self.rotate_left_action.setShortcut("Shift+R")
        self.rotate_left_action.setEnabled(False)
        
        self.addWidget(QLabel("Line Width:"))
        self.line_width_spinbox = QSpinBox()
        self.line_width_spinbox.setMinimum(1)
        self.line_width_spinbox.setMaximum(10)
        self.line_width_spinbox.setValue(2)
        self.line_width_spinbox.setFixedWidth(50)
        self.line_width_spinbox.setToolTip("Wire/line thickness")
        self.addWidget(self.line_width_spinbox)
        self.addSeparator()
        
        # SIMULATION SECTION
        self.addWidget(self._make_label("SIMULATION"))
        self.run_action = self.addAction(icon("media-playback-start"), "Run")
        self.run_action.setToolTip("Run Simulation (F5)")
        self.run_action.setShortcut("F5")
        
        self.pause_action = self.addAction(icon("media-playback-pause"), "Pause")
        self.pause_action.setToolTip("Pause (F6)")
        self.pause_action.setShortcut("F6")
        self.pause_action.setEnabled(False)
        
        self.stop_action = self.addAction(icon("media-playback-stop"), "Stop")
        self.stop_action.setToolTip("Stop (F7)")
        self.stop_action.setShortcut("F7")
        self.stop_action.setEnabled(False)
        
        self.addWidget(QLabel("Duration:"))
        self.duration_spinbox = QDoubleSpinBox()
        self.duration_spinbox.setMinimum(0.001)
        self.duration_spinbox.setMaximum(1000.0)
        self.duration_spinbox.setValue(1.0)
        self.duration_spinbox.setSuffix("s")
        self.duration_spinbox.setFixedWidth(70)
        self.duration_spinbox.setToolTip("Simulation duration (seconds)")
        self.addWidget(self.duration_spinbox)
        
        self.addWidget(QLabel("Step:"))
        self.timestep_spinbox = QDoubleSpinBox()
        self.timestep_spinbox.setMinimum(0.0001)
        self.timestep_spinbox.setMaximum(0.1)
        self.timestep_spinbox.setValue(0.001)
        self.timestep_spinbox.setSuffix("s")
        self.timestep_spinbox.setFixedWidth(70)
        self.timestep_spinbox.setToolTip("Time step (seconds)")
        self.addWidget(self.timestep_spinbox)
        
        self.addWidget(QLabel("Type:"))
        self.sim_type_combo = QComboBox()
        self.sim_type_combo.addItems(["DC", "AC", "Transient"])
        self.sim_type_combo.setFixedWidth(80)
        self.sim_type_combo.setToolTip("Simulation type")
        self.addWidget(self.sim_type_combo)
        self.addSeparator()
        
        # VIEW SECTION
        self.addWidget(self._make_label("VIEW"))
        self.zoom_in_action = self.addAction(icon("zoom-in"), "Zoom In")
        self.zoom_in_action.setToolTip("Zoom In (Ctrl++)")
        self.zoom_in_action.setShortcut("Ctrl++")
        
        self.zoom_out_action = self.addAction(icon("zoom-out"), "Zoom Out")
        self.zoom_out_action.setToolTip("Zoom Out (Ctrl+-)")
        self.zoom_out_action.setShortcut("Ctrl+-")
        
        self.fit_window_action = self.addAction(icon("zoom-fit-best"), "Fit")
        self.fit_window_action.setToolTip("Fit to Window")
        
        self.grid_toggle_action = self.addAction(icon("view-grid"), "Grid")
        self.grid_toggle_action.setToolTip("Toggle Grid")
        self.grid_toggle_action.setCheckable(True)
        self.grid_toggle_action.setChecked(True)
        self.addSeparator()
        
        # TOOLS SECTION
        self.addWidget(self._make_label("TOOLS"))
        
        # Engineering Design Tools (Top Section)
        self.transformer_designer_action = self.addAction(icon("system-search"), "Transformer")
        self.transformer_designer_action.setToolTip("Transformer Designer (Ctrl+Shift+T)")
        self.transformer_designer_action.setShortcut("Ctrl+Shift+T")
        
        self.cable_sizing_action = self.addAction(icon("format-text-italic"), "Cable Sizing")
        self.cable_sizing_action.setToolTip("Cable Sizing Calculator (Ctrl+Shift+C)")
        self.cable_sizing_action.setShortcut("Ctrl+Shift+C")
        
        self.fault_calculator_action = self.addAction(icon("dialog-warning"), "Fault Calc")
        self.fault_calculator_action.setToolTip("Fault Calculator (Ctrl+Shift+F)")
        self.fault_calculator_action.setShortcut("Ctrl+Shift+F")
        
        self.pf_correction_action = self.addAction(icon("chart-line"), "PF Correct")
        self.pf_correction_action.setToolTip("PF Correction Tool (Ctrl+Shift+G)")
        self.pf_correction_action.setShortcut("Ctrl+Shift+G")
        
        self.battery_tool_action = self.addAction(icon("battery"), "Battery")
        self.battery_tool_action.setToolTip("Battery Tool (Ctrl+Shift+Y)")
        self.battery_tool_action.setShortcut("Ctrl+Shift+Y")
        
        self.library_manager_action = self.addAction(icon("folder"), "Libraries")
        self.library_manager_action.setToolTip("Library Manager (Ctrl+Shift+K)")
        self.library_manager_action.setShortcut("Ctrl+Shift+K")
        
        self.addSeparator()
        
        # Main tools
        self.script_editor_action = self.addAction(icon("text-editor"), "Script Editor")
        self.script_editor_action.setToolTip("Script Editor (Ctrl+Shift+E)")
        self.script_editor_action.setShortcut("Ctrl+Shift+E")
        
        self.component_browser_action = self.addAction(icon("system-file-manager"), "Library")
        self.component_browser_action.setToolTip("Component Library (Ctrl+Shift+B)")
        self.component_browser_action.setShortcut("Ctrl+Shift+B")
        
        self.waveform_viewer_action = self.addAction(icon("image-jpeg"), "Waveforms")
        self.waveform_viewer_action.setToolTip("Waveform Viewer (Ctrl+Shift+W)")
        self.waveform_viewer_action.setShortcut("Ctrl+Shift+W")
        
        self.scope_action = self.addAction(icon("document-preview"), "Scope")
        self.scope_action.setToolTip("Oscilloscope (Ctrl+Shift+S)")
        self.scope_action.setShortcut("Ctrl+Shift+S")
        
        self.properties_panel_action = self.addAction(icon("document-properties"), "Properties")
        self.properties_panel_action.setToolTip("Properties Panel (Ctrl+Shift+P)")
        self.properties_panel_action.setShortcut("Ctrl+Shift+P")
        
        self.addSeparator()
        
        self.circuit_analyzer_action = self.addAction(icon("dialog-information"), "Analyzer")
        self.circuit_analyzer_action.setToolTip("Circuit Analyzer (Ctrl+Shift+A)")
        self.circuit_analyzer_action.setShortcut("Ctrl+Shift+A")
        
        self.design_wizard_action = self.addAction(icon("dialog-question"), "Wizard")
        self.design_wizard_action.setToolTip("Design Wizard (Ctrl+Shift+D)")
        self.design_wizard_action.setShortcut("Ctrl+Shift+D")
        
        self.measurement_tools_action = self.addAction(icon("measure"), "Measure")
        self.measurement_tools_action.setToolTip("Measurement Tools (Ctrl+Shift+M)")
        self.measurement_tools_action.setShortcut("Ctrl+Shift+M")
        
        self.simulation_monitor_action = self.addAction(icon("media-playback-start"), "Monitor")
        self.simulation_monitor_action.setToolTip("Simulation Monitor (Ctrl+Shift+O)")
        self.simulation_monitor_action.setShortcut("Ctrl+Shift+O")
        
        self.addSeparator()
        
        self.simulation_library_action = self.addAction(icon("office-database"), "Sim Library")
        self.simulation_library_action.setToolTip("Simulation Library (Ctrl+Shift+L)")
        self.simulation_library_action.setShortcut("Ctrl+Shift+L")
        
        self.import_library_action = self.addAction(icon("document-import"), "Import Lib")
        self.import_library_action.setToolTip("Import Libraries (Ctrl+Shift+I)")
        self.import_library_action.setShortcut("Ctrl+Shift+I")
        
        # Connect signals
        self._connect_signals()
        self.duplicate_action.setShortcut("Ctrl+D")
        self.duplicate_action.setEnabled(False)
    
    def _make_label(self, text: str):
        """Create a section label"""
        label = QLabel(text)
        font = QFont()
        font.setPointSize(9)
        font.setBold(True)
        label.setFont(font)
        label.setStyleSheet("color: #1976d2;")
        return label
    
    def _connect_signals(self):
        """Connect toolbar actions to signals"""
        self.new_action.triggered.connect(self.new_clicked)
        self.open_action.triggered.connect(self.open_clicked)
        self.save_action.triggered.connect(self.save_clicked)
        self.undo_action.triggered.connect(self.undo_clicked)
        self.redo_action.triggered.connect(self.redo_clicked)
        self.cut_action.triggered.connect(self.cut_clicked)
        self.copy_action.triggered.connect(self.copy_clicked)
        self.paste_action.triggered.connect(self.paste_clicked)
        self.delete_action.triggered.connect(self.delete_clicked)
        self.duplicate_action.triggered.connect(self.duplicate_clicked)
        self.marquee_action.triggered.connect(lambda checked: self.marquee_clicked.emit(checked))
        self.select_all_action.triggered.connect(self.select_all_clicked)
        self.rotate_action.triggered.connect(self.rotate_clicked)
        self.rotate_left_action.triggered.connect(self.rotate_left_clicked)
        self.line_width_spinbox.valueChanged.connect(self.line_width_changed)
        self.run_action.triggered.connect(self.run_clicked)
        self.pause_action.triggered.connect(self.pause_clicked)
        self.stop_action.triggered.connect(self.stop_clicked)
        self.zoom_in_action.triggered.connect(self.zoom_in_clicked)
        self.zoom_out_action.triggered.connect(self.zoom_out_clicked)
        self.fit_window_action.triggered.connect(self.fit_to_window_clicked)
        self.grid_toggle_action.triggered.connect(self.grid_toggle_clicked)
        self.script_editor_action.triggered.connect(self.script_editor_clicked)
        self.library_manager_action.triggered.connect(self.library_manager_clicked)
        self.transformer_designer_action.triggered.connect(self.transformer_designer_clicked)
        self.cable_sizing_action.triggered.connect(self.cable_sizing_clicked)
        self.fault_calculator_action.triggered.connect(self.fault_calculator_clicked)
        self.pf_correction_action.triggered.connect(self.pf_correction_clicked)
        self.battery_tool_action.triggered.connect(self.battery_tool_clicked)
        self.waveform_viewer_action.triggered.connect(self.waveform_viewer_clicked)
        self.properties_panel_action.triggered.connect(self.properties_panel_clicked)
        self.component_browser_action.triggered.connect(self.component_browser_clicked)
        self.circuit_analyzer_action.triggered.connect(self.circuit_analyzer_clicked)
        self.design_wizard_action.triggered.connect(self.design_wizard_clicked)
        self.measurement_tools_action.triggered.connect(self.measurement_tools_clicked)
        self.simulation_monitor_action.triggered.connect(self.simulation_monitor_clicked)
        self.simulation_library_action.triggered.connect(self.simulation_library_clicked)
        self.import_library_action.triggered.connect(self.import_library_clicked)
        self.scope_action.triggered.connect(self.scope_clicked)
    
    def set_button_state(self, button_name: str, enabled: bool):
        """Enable or disable toolbar button"""
        action_map = {
            "undo": self.undo_action,
            "redo": self.redo_action,
            "cut": self.cut_action,
            "copy": self.copy_action,
            "paste": self.paste_action,
            "delete": self.delete_action,
            "duplicate": self.duplicate_action,
            "rotate": self.rotate_action,
            "rotate_left": self.rotate_left_action,
        }
        if button_name in action_map:
            action_map[button_name].setEnabled(enabled)
    
    def get_sim_parameters(self):
        """Get current simulation parameters"""
        return {
            "duration": self.duration_spinbox.value(),
            "timestep": self.timestep_spinbox.value(),
            "type": self.sim_type_combo.currentText(),
        }
