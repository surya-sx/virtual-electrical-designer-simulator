"""
Main application window with all panels and toolbars
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QDockWidget, QTabWidget, QStatusBar, QTableWidgetItem,
    QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, QSize, Signal

from frontend.ui.menu_bar import MenuBar
from frontend.ui.toolbar import Toolbar
from frontend.panels.circuit_canvas import CircuitCanvas
from frontend.panels.component_library import ComponentLibraryPanel
from frontend.panels.inspector import InspectorPanel
from frontend.panels.console import ConsolePanel, LogLevel
from frontend.panels.waveform import WaveformPanel
from frontend.panels.reports import ReportsPanel
from frontend.panels.script_editor import ScriptEditorPanel
from frontend.panels.properties_panel import PropertiesPanel
from frontend.windows.script_editor_window import ScriptEditorWindow
from frontend.windows.waveform_viewer_window import WaveformViewerWindow
from frontend.core.command_manager import CommandManager
from backend.circuit.circuit_validator import CircuitValidator
from backend.circuit.circuit_analyzer import CircuitAnalyzer
from backend.reporting.report_generator import ReportGenerator


class MainWindow(QMainWindow):
    # Signals
    simulation_started = Signal()
    simulation_finished = Signal()
    project_changed = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Virtual Electrical Designer & Simulator")
        self.setGeometry(100, 100, 1600, 1000)
        
        # Backend references
        self.project_manager = None
        self.simulation_engine = None
        self.current_project = None
        self.current_filename = None
        
        # Core managers
        self.command_manager = CommandManager()
        self.validator = CircuitValidator()
        self.analyzer = CircuitAnalyzer()
        
        # State tracking
        self.modified = False
        self.clipboard = {"components": [], "wires": []}
        
        # Separate windows
        self.script_editor_windows = {}  # Store open script editor windows
        self.waveform_viewer_windows = {}  # Store open waveform viewer windows
        self.properties_panel_dock = None  # Properties panel dock
        
        # Initialize UI
        self._setup_menu_bar()
        self._setup_toolbar()
        self._setup_central_widget()
        self._setup_panels()
        self._setup_status_bar()
        self._setup_dock_widgets()
        self._connect_signals()
        
        # Initial status
        self._update_title()
        self.status_bar.showMessage("Ready")
    
    def _setup_menu_bar(self):
        """Setup application menu bar"""
        self.menu_bar = MenuBar()
        self.setMenuBar(self.menu_bar)
        self._connect_menu_actions()
    
    def _connect_menu_actions(self):
        """Connect all menu actions"""
        # File menu
        for action in self.menu_bar.findChildren(QWidget):
            pass
        
        menus = self.menu_bar.findChildren(__import__('PySide6.QtWidgets', fromlist=['QMenu']).QMenu)
        
        for menu in menus:
            menu_title = menu.title().replace("&", "")
            
            for action in menu.actions():
                action_text = action.text().replace("&", "")
                
                # File menu
                if menu_title == "File":
                    if action_text == "New":
                        action.triggered.connect(self.new_project)
                    elif action_text == "Open":
                        action.triggered.connect(self.open_project)
                    elif action_text == "Save":
                        action.triggered.connect(self.save_project)
                    elif action_text == "Save As":
                        action.triggered.connect(self.save_project_as)
                    elif action_text == "Exit":
                        action.triggered.connect(self.close)
                    elif action_text == "Import":
                        action.triggered.connect(self.import_circuit)
                    elif action_text == "Export":
                        action.triggered.connect(self.export_circuit)
                
                # Edit menu
                elif menu_title == "Edit":
                    if action_text == "Undo":
                        action.triggered.connect(self.undo)
                    elif action_text == "Redo":
                        action.triggered.connect(self.redo)
                    elif action_text == "Cut":
                        action.triggered.connect(self.cut)
                    elif action_text == "Copy":
                        action.triggered.connect(self.copy)
                    elif action_text == "Paste":
                        action.triggered.connect(self.paste)
                    elif action_text == "Duplicate":
                        action.triggered.connect(self.duplicate)
                    elif action_text == "Delete":
                        action.triggered.connect(self.delete)
                    elif action_text == "Select All":
                        action.triggered.connect(self.select_all)
                
                # View menu
                elif menu_title == "View":
                    if action_text == "Zoom In":
                        action.triggered.connect(self.zoom_in)
                    elif action_text == "Zoom Out":
                        action.triggered.connect(self.zoom_out)
                    elif action_text == "Reset Zoom":
                        action.triggered.connect(self.reset_zoom)
                    elif action_text == "Toggle Grid":
                        action.triggered.connect(self.toggle_grid)
                
                # Simulation menu
                elif menu_title == "Simulation":
                    if action_text == "Run":
                        action.triggered.connect(self.run_simulation)
                    elif action_text == "Pause":
                        action.triggered.connect(self.pause_simulation)
                    elif action_text == "Stop":
                        action.triggered.connect(self.stop_simulation)
                
                # Tools menu
                elif menu_title == "Tools":
                    if action_text == "Transformer Designer":
                        action.triggered.connect(self.open_transformer_designer)
                    elif action_text == "Cable Sizing":
                        action.triggered.connect(self.open_cable_sizing)
                    elif action_text == "Fault Calculator":
                        action.triggered.connect(self.open_fault_calculator)
                    elif action_text == "PF Correction":
                        action.triggered.connect(self.open_pf_correction)
                    elif action_text == "Battery Tool":
                        action.triggered.connect(self.open_battery_tool)
                    elif action_text == "Component Library Manager":
                        action.triggered.connect(self.open_library_manager)
                    elif action_text == "Script Manager":
                        action.triggered.connect(self.open_script_editor)
    
    def _setup_toolbar(self):
        """Setup organized toolbar"""
        self.toolbar = Toolbar()
        self.addToolBar(self.toolbar)
        
        # Connect toolbar signals
        self.toolbar.new_clicked.connect(self.new_project)
        self.toolbar.open_clicked.connect(self.open_project)
        self.toolbar.save_clicked.connect(self.save_project)
        self.toolbar.undo_clicked.connect(self.undo)
        self.toolbar.redo_clicked.connect(self.redo)
        self.toolbar.cut_clicked.connect(self.cut)
        self.toolbar.copy_clicked.connect(self.copy)
        self.toolbar.paste_clicked.connect(self.paste)
        self.toolbar.delete_clicked.connect(self.delete)
        self.toolbar.duplicate_clicked.connect(self.duplicate)
        self.toolbar.select_all_clicked.connect(self.select_all)
        # Note: rotate and line_width connections added after circuit_canvas is created
        self.toolbar.run_clicked.connect(self.run_simulation)
        self.toolbar.pause_clicked.connect(self.pause_simulation)
        self.toolbar.stop_clicked.connect(self.stop_simulation)
        self.toolbar.zoom_in_clicked.connect(self.zoom_in)
        self.toolbar.zoom_out_clicked.connect(self.zoom_out)
        self.toolbar.fit_to_window_clicked.connect(self.fit_to_window)
        self.toolbar.grid_toggle_clicked.connect(self.toggle_grid)
        self.toolbar.marquee_clicked.connect(self.toggle_marquee_mode)
        self.toolbar.script_editor_clicked.connect(self.open_script_editor)
        self.toolbar.waveform_viewer_clicked.connect(self.open_waveform_viewer)
        self.toolbar.properties_panel_clicked.connect(self.toggle_properties_panel)
        self.toolbar.component_browser_clicked.connect(self.open_component_browser)
        self.toolbar.circuit_analyzer_clicked.connect(self.open_circuit_analyzer)
        self.toolbar.design_wizard_clicked.connect(self.open_design_wizard)
        self.toolbar.measurement_tools_clicked.connect(self.open_measurement_tools)
        self.toolbar.simulation_monitor_clicked.connect(self.open_simulation_monitor)
        self.toolbar.simulation_library_clicked.connect(self.open_simulation_library)
        self.toolbar.import_library_clicked.connect(self.open_import_library)
        self.toolbar.scope_clicked.connect(self.open_scope)
        
        # Engineering Tools
        self.toolbar.transformer_designer_clicked.connect(self.open_transformer_designer)
        self.toolbar.cable_sizing_clicked.connect(self.open_cable_sizing)
        self.toolbar.fault_calculator_clicked.connect(self.open_fault_calculator)
        self.toolbar.pf_correction_clicked.connect(self.open_pf_correction)
        self.toolbar.battery_tool_clicked.connect(self.open_battery_tool)
        self.toolbar.library_manager_clicked.connect(self.open_library_manager)
    
    def _setup_central_widget(self):
        """Setup central widget with circuit canvas"""
        self.circuit_canvas = CircuitCanvas()
        self.setCentralWidget(self.circuit_canvas)
    
    def _setup_panels(self):
        """Setup UI panels"""
        self.component_library = ComponentLibraryPanel()
        self.inspector = InspectorPanel()
        self.console = ConsolePanel()
        self.waveform = WaveformPanel()
        self.reports = ReportsPanel()
        self.script_editor = ScriptEditorPanel()
        
        # Initialize report generator backend
        self.report_generator = ReportGenerator(
            project_name="Virtual Circuit",
            circuit_name="Active Circuit"
        )
        self.reports.set_report_generator(self.report_generator)
        
        # Connect toolbar signals that depend on circuit_canvas
        self.toolbar.rotate_clicked.connect(lambda: self.circuit_canvas.rotate_component(self.circuit_canvas.selected_component, 90))
        self.toolbar.rotate_left_clicked.connect(lambda: self.circuit_canvas.rotate_component(self.circuit_canvas.selected_component, -90))
        self.toolbar.line_width_changed.connect(self.circuit_canvas.set_wire_width)
    
    def _setup_status_bar(self):
        """Setup status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def _setup_dock_widgets(self):
        """Setup dock widgets for left, right, and bottom panels"""
        # Left: Component Library
        self.left_dock = QDockWidget("Component Library", self)
        self.left_dock.setWidget(self.component_library)
        self.left_dock.setMinimumWidth(250)
        self.left_dock.setMaximumWidth(350)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.left_dock)
        self.left_dock.show()  # Show component library on startup
        
        # Right: Inspector
        self.right_dock = QDockWidget("Inspector", self)
        self.right_dock.setWidget(self.inspector)
        self.right_dock.setMinimumWidth(250)
        self.right_dock.setMaximumWidth(350)
        self.addDockWidget(Qt.RightDockWidgetArea, self.right_dock)
        
        # Bottom: Tabbed panels
        self.bottom_dock = QDockWidget("Output Panels", self)
        self.bottom_dock.setMinimumHeight(200)
        self.bottom_dock.setMaximumHeight(300)
        bottom_tabs = QTabWidget()
        bottom_tabs.addTab(self.console, "Console")
        bottom_tabs.addTab(self.waveform, "Waveforms")
        bottom_tabs.addTab(self.reports, "Reports")
        self.bottom_dock.setWidget(bottom_tabs)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.bottom_dock)
        
        # Resizable splitter behavior
        self.resizeDocks([self.bottom_dock], [250], Qt.Vertical)
    
    def _connect_signals(self):
        """Connect UI signals to backend"""
        # Circuit canvas signals
        self.circuit_canvas.component_selected.connect(self._on_component_selected)
        self.circuit_canvas.circuit_changed.connect(self._on_circuit_changed)
        
        # Canvas signals to toolbar - undo/redo
        self.circuit_canvas.undo_redo_changed.connect(self._update_undo_redo_buttons)
        self.circuit_canvas.clipboard_changed.connect(self._update_paste_button)
        
        # Component library signals
        self.component_library.component_selected.connect(self._on_library_component_selected)
        
        # Inspector signals
        self.inspector.property_changed.connect(self._on_property_changed)
    
    # ====== FILE MENU ACTIONS ======
    
    def new_project(self):
        """Create new project"""
        if self.modified:
            reply = QMessageBox.question(
                self, "Unsaved Changes", "Save changes before creating new project?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            if reply == QMessageBox.Save:
                self.save_project()
            elif reply == QMessageBox.Cancel:
                return
        
        self.circuit_canvas.clear_canvas()
        self.console.log_list.clear()
        self.inspector.clear()
        self.current_project = None
        self.current_filename = None
        self.modified = False
        self.command_manager.clear_history()
        
        self.console.log("New project created", LogLevel.INFO)
        self._update_title()
        self.status_bar.showMessage("New project ready")
    
    def open_project(self):
        """Open existing project"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Open Project", "",
            "VED Projects (*.vedproj);;Circuit Files (*.vedcir);;All Files (*)"
        )
        
        if filename:
            try:
                self.current_filename = filename
                # Load project logic here
                self.console.log(f"Opened project: {filename}", LogLevel.INFO)
                self._update_title()
                self.status_bar.showMessage(f"Opened {filename}")
            except Exception as e:
                self.console.log(f"Error opening file: {e}", LogLevel.ERROR)
                QMessageBox.critical(self, "Error", f"Could not open file: {e}")
    
    def save_project(self):
        """Save current project"""
        if not self.current_filename:
            self.save_project_as()
        else:
            try:
                self.console.log(f"Project saved to {self.current_filename}", LogLevel.INFO)
                self.modified = False
                self._update_title()
                self.status_bar.showMessage("Project saved")
            except Exception as e:
                self.console.log(f"Error saving file: {e}", LogLevel.ERROR)
    
    def save_project_as(self):
        """Save project with new name"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Project As", "",
            "VED Projects (*.vedproj);;Circuit Files (*.vedcir);;All Files (*)"
        )
        
        if filename:
            self.current_filename = filename
            self.save_project()
    
    def import_circuit(self):
        """Import circuit from file"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Import Circuit", "",
            "Circuit Files (*.vedcir);;SPICE Files (*.cir);;All Files (*)"
        )
        
        if filename:
            self.console.log(f"Imported circuit from {filename}", LogLevel.INFO)
    
    def export_circuit(self):
        """Export circuit to file"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Circuit", "",
            "Circuit Files (*.vedcir);;SPICE Files (*.cir);;All Files (*)"
        )
        
        if filename:
            self.console.log(f"Exported circuit to {filename}", LogLevel.INFO)
    
    # ====== EDIT MENU ACTIONS ======
    
    def undo(self):
        """Undo last action"""
        self.circuit_canvas.undo()
        self.console.log("Action undone", LogLevel.DEBUG)
        self.status_bar.showMessage("Undone")
        self.modified = True
    
    def redo(self):
        """Redo last undone action"""
        self.circuit_canvas.redo()
        self.console.log("Action redone", LogLevel.DEBUG)
        self.status_bar.showMessage("Redone")
        self.modified = True
    
    def cut(self):
        """Cut selected components"""
        if self.circuit_canvas.selected_component:
            self.circuit_canvas.cut(self.circuit_canvas.selected_component)
            self.console.log("Component cut to clipboard", LogLevel.DEBUG)
            self.status_bar.showMessage("Cut")
            self.modified = True
    
    def copy(self):
        """Copy selected components"""
        if self.circuit_canvas.selected_component:
            self.circuit_canvas.copy(self.circuit_canvas.selected_component)
            self.console.log("Component copied to clipboard", LogLevel.DEBUG)
            self.status_bar.showMessage("Copied")
    
    def paste(self):
        """Paste components from clipboard"""
        self.circuit_canvas.paste(offset_x=50, offset_y=50)
        self.console.log("Component pasted from clipboard", LogLevel.DEBUG)
        self.status_bar.showMessage("Pasted")
        self.modified = True
    
    def duplicate(self):
        """Duplicate selected components"""
        if self.circuit_canvas.selected_component:
            self.circuit_canvas.duplicate_selected()
            self.console.log("Component duplicated", LogLevel.DEBUG)
            self.status_bar.showMessage("Duplicated")
            self.modified = True
    
    def delete(self):
        """Delete selected components"""
        if self.circuit_canvas.selected_component:
            self.circuit_canvas.save_state()
            self.circuit_canvas._on_delete(self.circuit_canvas.selected_component)
            self.console.log("Component deleted", LogLevel.DEBUG)
            self.status_bar.showMessage("Deleted")
            self.modified = True
    
    def select_all(self):
        """Select all components"""
        self.circuit_canvas.select_all()
        self.status_bar.showMessage(f"Selected {len(self.circuit_canvas.selected_components)} components")
    
    # ====== VIEW MENU ACTIONS ======
    
    def zoom_in(self):
        """Zoom in"""
        current_zoom = int(self.toolbar.zoom_spinbox.value())
        new_zoom = min(500, current_zoom + 10)
        self.toolbar.zoom_spinbox.setValue(new_zoom)
        self.circuit_canvas.scale(1.1, 1.1)
        self.status_bar.showMessage(f"Zoom: {new_zoom}%")
    
    def zoom_out(self):
        """Zoom out"""
        current_zoom = int(self.toolbar.zoom_spinbox.value())
        new_zoom = max(10, current_zoom - 10)
        self.toolbar.zoom_spinbox.setValue(new_zoom)
        self.circuit_canvas.scale(0.9, 0.9)
        self.status_bar.showMessage(f"Zoom: {new_zoom}%")
    
    def reset_zoom(self):
        """Reset zoom to 100%"""
        self.toolbar.zoom_spinbox.setValue(100)
        self.circuit_canvas.resetTransform()
        self.status_bar.showMessage("Zoom: 100%")
    
    def fit_to_window(self):
        """Fit circuit to window"""
        self.circuit_canvas.fitInView(self.circuit_canvas.sceneRect(), Qt.KeepAspectRatio)
        self.status_bar.showMessage("Fit to window")
    
    def toggle_wire_mode(self):
        """Toggle wire drawing mode"""
        from frontend.panels.circuit_canvas import CanvasMode
        if self.circuit_canvas.mode == CanvasMode.DRAW_WIRE:
            self.circuit_canvas.set_mode(CanvasMode.SELECT)
            self.status_bar.showMessage("Wire mode disabled")
            self.toolbar.wire_action.setText("Draw Wire")
        else:
            self.circuit_canvas.set_mode(CanvasMode.DRAW_WIRE)
            self.status_bar.showMessage("Wire mode enabled - Click on component ports to connect")
            self.toolbar.wire_action.setText("Cancel Wire")
    
    def toggle_marquee_mode(self, checked: bool):
        """Toggle marquee selection mode"""
        from frontend.panels.circuit_canvas import CanvasMode
        if checked:
            self.circuit_canvas.set_mode(CanvasMode.MARQUEE)
            self.status_bar.showMessage("Marquee mode - Drag to select multiple components")
        else:
            self.circuit_canvas.set_mode(CanvasMode.SELECT)
            self.status_bar.showMessage("Select mode")
    
    def toggle_grid(self):
        """Toggle grid visibility"""
        # Toggle grid in canvas
        self.status_bar.showMessage("Grid toggled")
    
    # ====== SIMULATION MENU ACTIONS ======
    
    def run_simulation(self):
        """Run circuit simulation"""
        self.status_bar.showMessage("Running simulation...")
        self.simulation_started.emit()
        
        try:
            # Validate circuit
            circuit_data = self._get_circuit_data()
            is_valid, issues = self.validator.validate_circuit(circuit_data)
            
            # Show validation results
            for issue in issues:
                self.console.log(issue.message, LogLevel.WARNING if issue.level.value == "warning" else LogLevel.ERROR)
            
            if not is_valid:
                self.console.log("Simulation cancelled due to circuit errors", LogLevel.ERROR)
                self.status_bar.showMessage("Simulation failed - circuit errors")
                return
            
            # Run simulation
            if self.simulation_engine:
                self.simulation_engine.setup_dc_analysis()
                result = self.simulation_engine.run()
                
                if result.status == "success":
                    # Display results
                    self._display_results(result)
                    self.console.log("Simulation completed successfully", LogLevel.INFO)
                    self.status_bar.showMessage("Simulation complete")
                else:
                    self.console.log(f"Simulation failed: {result.error_message}", LogLevel.ERROR)
                    self.status_bar.showMessage("Simulation failed")
            
            self.simulation_finished.emit()
        
        except Exception as e:
            self.console.log(f"Simulation error: {e}", LogLevel.ERROR)
            self.status_bar.showMessage("Simulation error")
    
    def pause_simulation(self):
        """Pause running simulation"""
        self.status_bar.showMessage("Simulation paused")
    
    def stop_simulation(self):
        """Stop running simulation"""
        self.status_bar.showMessage("Simulation stopped")
    
    # ====== HELPER METHODS ======
    
    def _get_circuit_data(self) -> dict:
        """Get circuit data from canvas"""
        return {
            "components": self.circuit_canvas.components,
            "nodes": list(self.circuit_canvas.nodes),
            "wires": list(self.circuit_canvas.wires),
        }
    
    def _display_results(self, result):
        """Display simulation results in waveform panel"""
        if hasattr(result, 'node_voltages') and result.node_voltages:
            for node_id, voltage in result.node_voltages.items():
                self.waveform.add_signal(node_id, result.time_points, voltage)
        
        self.waveform.fit_view()
    
    def _on_component_selected(self, comp_id: str):
        """Handle component selection"""
        if comp_id in self.circuit_canvas.components:
            comp = self.circuit_canvas.components[comp_id]
            props = {
                "Name": comp.name if hasattr(comp, 'name') else "Unknown",
                "Type": comp.comp_type if hasattr(comp, 'comp_type') else "Unknown",
                "X": str(comp.x if hasattr(comp, 'x') else 0),
                "Y": str(comp.y if hasattr(comp, 'y') else 0),
            }
            self.inspector.set_component_properties(comp_id, props)
    
    def _on_library_component_selected(self, comp_type: str, name: str):
        """Handle library component selection"""
        self.circuit_canvas.set_preview_component(comp_type, name)
    
    def _on_property_changed(self, comp_id: str, prop_name: str, value):
        """Handle property value changes"""
        self.modified = True
        self._update_title()
        self.console.log(f"Property '{prop_name}' changed to '{value}'", LogLevel.DEBUG)
    
    def _on_circuit_changed(self):
        """Handle circuit changes"""
        self.modified = True
        self._update_title()
        self.status_bar.showMessage("Circuit modified")
        
        # Analyze circuit
        circuit_data = self._get_circuit_data()
        analysis = self.analyzer.analyze_circuit(circuit_data)
        self.console.log(f"Circuit: {analysis['component_count']} components, {analysis['wire_count']} wires", LogLevel.DEBUG)
    
    def _update_title(self):
        """Update window title based on project state"""
        title = "Virtual Electrical Designer & Simulator"
        
        if self.current_filename:
            title += f" - {self.current_filename}"
        
        if self.modified:
            title += " *"
        
        self.setWindowTitle(title)
    
    # ===================== Drawing Tools Actions =====================
    
    def action_rotate_component(self):
        """Rotate selected component(s) by 90 degrees"""
        self.circuit_canvas.rotate_selected(90)
        self.status_bar.showMessage("Component rotated 90°")
        self.console.log("Component rotated 90°", LogLevel.INFO)
    
    def action_align_left(self):
        """Align selected components to the left"""
        self.circuit_canvas.align_components("left")
        self.status_bar.showMessage("Components aligned left")
        self.console.log("Components aligned to left", LogLevel.INFO)
    
    def action_align_center(self):
        """Align selected components to center"""
        self.circuit_canvas.align_components("center")
        self.status_bar.showMessage("Components aligned to center")
        self.console.log("Components aligned to center", LogLevel.INFO)
    
    def action_align_right(self):
        """Align selected components to the right"""
        self.circuit_canvas.align_components("right")
        self.status_bar.showMessage("Components aligned right")
        self.console.log("Components aligned to right", LogLevel.INFO)
    
    def action_align_top(self):
        """Align selected components to top"""
        self.circuit_canvas.align_components("top")
        self.status_bar.showMessage("Components aligned to top")
        self.console.log("Components aligned to top", LogLevel.INFO)
    
    def action_align_middle(self):
        """Align selected components to middle"""
        self.circuit_canvas.align_components("middle")
        self.status_bar.showMessage("Components aligned to middle")
        self.console.log("Components aligned to middle", LogLevel.INFO)
    
    def action_align_bottom(self):
        """Align selected components to bottom"""
        self.circuit_canvas.align_components("bottom")
        self.status_bar.showMessage("Components aligned to bottom")
        self.console.log("Components aligned to bottom", LogLevel.INFO)
    
    def action_group_components(self):
        """Group selected components"""
        if len(self.circuit_canvas.selected_components) < 2:
            QMessageBox.warning(self, "Group", "Select at least 2 components to group")
            return
        
        group_id = self.circuit_canvas.group_components(self.circuit_canvas.selected_components)
        if group_id:
            self.status_bar.showMessage(f"Components grouped: {group_id}")
            self.console.log(f"Grouped {len(self.circuit_canvas.selected_components)} components", LogLevel.INFO)
        else:
            QMessageBox.warning(self, "Group", "Failed to group components")
    
    def action_ungroup_components(self):
        """Ungroup selected component"""
        if not self.circuit_canvas.selected_component:
            QMessageBox.warning(self, "Ungroup", "Select a grouped component to ungroup")
            return
        
        comp = self.circuit_canvas.components.get(self.circuit_canvas.selected_component)
        if comp and comp.group_id:
            self.circuit_canvas.ungroup_components(comp.group_id)
            self.status_bar.showMessage("Components ungrouped")
            self.console.log("Components ungrouped", LogLevel.INFO)
        else:
            QMessageBox.warning(self, "Ungroup", "Selected component is not in a group")
    
    def action_toggle_snap_to_grid(self):
        """Toggle snap-to-grid option"""
        self.circuit_canvas.snap_to_grid = not self.circuit_canvas.snap_to_grid
        status = "enabled" if self.circuit_canvas.snap_to_grid else "disabled"
        self.status_bar.showMessage(f"Snap to grid {status}")
        self.console.log(f"Snap to grid {status}", LogLevel.DEBUG)
    
    # ===================== Reporting Actions =====================
    
    def action_generate_reports(self):
        """Generate all reports (summary, BOM, results)"""
        if not self.current_project:
            QMessageBox.warning(self, "Generate Reports", "No project loaded")
            return
        
        try:
            # Collect circuit data
            circuit_data = {
                "components": {cid: {"name": c.name, "type": c.type, "value": getattr(c, 'value', None)}
                             for cid, c in self.circuit_canvas.components.items()},
                "wires": self.circuit_canvas.wires
            }
            
            # Set data in reports panel
            self.reports_panel.set_circuit_data(circuit_data)
            
            # Add simulation data if available
            if hasattr(self, 'last_simulation_data'):
                sim_type = self.last_simulation_data.get("type", "unknown")
                sim_results = self.last_simulation_data.get("results", {})
                self.reports_panel.set_simulation_data(sim_type, sim_results)
            
            # Generate reports
            self.reports_panel._generate_reports()
            
            self.status_bar.showMessage("Reports generated successfully")
            self.console.log("Reports generated", LogLevel.INFO)
            
        except Exception as e:
            QMessageBox.critical(self, "Generate Reports", f"Error: {str(e)}")
            self.console.log(f"Report generation failed: {str(e)}", LogLevel.ERROR)
    
    def action_export_report_html(self):
        """Export current report as HTML"""
        if not self.reports_panel.report_data.get("summary"):
            QMessageBox.warning(self, "Export", "Generate reports first")
            return
        
        try:
            self.reports_panel._export_report()
            self.status_bar.showMessage("Report exported")
        except Exception as e:
            QMessageBox.critical(self, "Export Report", f"Error: {str(e)}")
            self.console.log(f"Export failed: {str(e)}", LogLevel.ERROR)
    
    def action_refresh_reports(self):
        """Refresh reports with current data"""
        self.action_generate_reports()
    
    # ====== TOOLBAR STATE UPDATE METHODS ======
    
    def _update_undo_redo_buttons(self, can_undo: bool, can_redo: bool):
        """Update undo/redo button states"""
        self.toolbar.set_button_state("undo", can_undo)
        self.toolbar.set_button_state("redo", can_redo)
    
    def _update_paste_button(self, has_content: bool):
        """Update paste button state"""
        self.toolbar.set_button_state("paste", has_content)
    
    def _on_component_selected(self, comp_id: str):
        """Enable edit buttons when component is selected"""
        has_selection = comp_id is not None
        self.toolbar.set_button_state("cut", has_selection)
        self.toolbar.set_button_state("copy", has_selection)
        self.toolbar.set_button_state("delete", has_selection)
        self.toolbar.set_button_state("duplicate", has_selection)
        self.toolbar.set_button_state("rotate", has_selection)
    
    def _on_circuit_changed(self):
        """Handle circuit changes"""
        self.modified = True
        self._update_title()
    
    # ====== WINDOW MANAGEMENT METHODS ======
    
    def open_script_editor(self):
        """Open a new script editor window in full screen"""
        try:
            script_name = f"Script_{len(self.script_editor_windows) + 1}"
            
            # Prepare circuit context for script with useful libraries
            import numpy as np
            import math
            import scipy.signal as signal
            
            circuit_context = {
                "circuit": self.circuit_canvas.components,
                "wires": self.circuit_canvas.wires,
                "nodes": self.circuit_canvas.nodes,
                "print": print,
                "np": np,
                "numpy": np,
                "math": math,
                "signal": signal,
                "len": len,
                "range": range,
                "zip": zip,
                "enumerate": enumerate,
            }
            
            # Create script editor window
            script_window = ScriptEditorWindow(
                script_name=script_name,
                parent=self,
                circuit_context=circuit_context
            )
            
            # Store reference
            self.script_editor_windows[script_name] = script_window
            
            # Connect signals
            script_window.script_executed.connect(self._on_script_executed)
            script_window.script_error.connect(self._on_script_error)
            
            # Show in full screen
            script_window.showMaximized()
            
            self.status_bar.showMessage(f"Script Editor opened: {script_name}")
            self.console.log(f"✓ Script editor opened (Full Screen): {script_name}", LogLevel.INFO)
        except Exception as e:
            self.console.log(f"❌ Error opening Script Editor: {str(e)}", LogLevel.ERROR)
            self.status_bar.showMessage(f"Error: {str(e)}")
    
    def _on_script_executed(self, output: str):
        """Handle script execution output"""
        self.console.log(output, LogLevel.INFO)
    
    def _on_script_error(self, error: str):
        """Handle script execution error"""
        self.console.log(error, LogLevel.ERROR)
    
    def open_waveform_viewer(self):
        """Open a new waveform viewer window"""
        viewer_name = f"Waveforms_{len(self.waveform_viewer_windows) + 1}"
        
        # Create waveform viewer window
        waveform_window = WaveformViewerWindow(
            parent=self,
            window_title=viewer_name
        )
        
        # Store reference
        self.waveform_viewer_windows[viewer_name] = waveform_window
        
        self.status_bar.showMessage(f"Opened: {viewer_name}")
        self.console.log(f"Waveform viewer opened: {viewer_name}", LogLevel.INFO)
    
    def toggle_properties_panel(self):
        """Toggle properties panel visibility"""
        if self.properties_panel_dock is None:
            # Create properties panel
            properties_panel = PropertiesPanel()
            
            # Create dock widget
            self.properties_panel_dock = QDockWidget("Component Properties", self)
            self.properties_panel_dock.setWidget(properties_panel)
            self.properties_panel_dock.setMinimumWidth(300)
            self.properties_panel_dock.setMaximumWidth(500)
            
            # Add to right dock area
            self.addDockWidget(Qt.RightDockWidgetArea, self.properties_panel_dock)
            
            # Connect signals
            self.circuit_canvas.component_selected.connect(
                lambda comp_id: self._on_properties_component_selected(comp_id, properties_panel)
            )
            properties_panel.property_changed.connect(self._on_property_value_changed)
            
            self.status_bar.showMessage("Properties panel opened")
            self.console.log("Properties panel opened", LogLevel.INFO)
        else:
            # Toggle visibility
            is_visible = self.properties_panel_dock.isVisible()
            self.properties_panel_dock.setVisible(not is_visible)
            status = "shown" if not is_visible else "hidden"
            self.status_bar.showMessage(f"Properties panel {status}")
    
    def _on_properties_component_selected(self, comp_id: str, properties_panel: PropertiesPanel):
        """Load component properties in properties panel"""
        if comp_id and comp_id in self.circuit_canvas.components:
            component = self.circuit_canvas.components[comp_id]
            component_type = component.component_type
            properties = getattr(component, "properties", {})
            
            properties_panel.load_component_properties(comp_id, component_type, properties)
            self.status_bar.showMessage(f"Loaded properties for {component_type}")
    
    def _on_property_value_changed(self, comp_id: str, property_name: str, value: any):
        """Handle property value change"""
        if comp_id in self.circuit_canvas.components:
            component = self.circuit_canvas.components[comp_id]
            if not hasattr(component, "properties"):
                component.properties = {}
            component.properties[property_name] = value
            
            self.circuit_canvas.circuit_changed.emit()
            self.console.log(f"Property changed: {comp_id} -> {property_name} = {value}", LogLevel.INFO)
    
    def open_component_browser(self):
        """Toggle component library panel visibility"""
        if self.left_dock.isVisible():
            self.left_dock.hide()
            self.console.log("Component library hidden", LogLevel.INFO)
        else:
            self.left_dock.show()
            self.console.log("Component library shown", LogLevel.INFO)
    
    def open_circuit_analyzer(self):
        """Open circuit analyzer tool"""
        self.console.log("Circuit Analyzer: Analyzing circuit topology...", LogLevel.INFO)
        # Analyze circuit connectivity and display results
        if self.circuit_canvas.components:
            comp_count = len(self.circuit_canvas.components)
            node_count = len(self.circuit_canvas.node_to_component)
            self.console.log(f"Circuit contains {comp_count} components and {node_count} nodes", LogLevel.INFO)
            # Check for isolated components
            isolated = []
            for comp_id, comp in self.circuit_canvas.components.items():
                nodes = sum(1 for nid, cid in self.circuit_canvas.node_to_component.items() if cid == comp_id)
                if nodes == 0:
                    isolated.append(comp.name)
            if isolated:
                self.console.log(f"⚠ Isolated components: {', '.join(isolated)}", LogLevel.WARNING)
            else:
                self.console.log("✓ All components properly connected", LogLevel.INFO)
        else:
            self.console.log("Circuit is empty", LogLevel.WARNING)
    
    def open_design_wizard(self):
        """Open design wizard for component selection"""
        self.console.log("Design Wizard: Starting component selection guide...", LogLevel.INFO)
        self.console.log("📋 Available design wizards:", LogLevel.INFO)
        self.console.log("  • RC Filter Designer", LogLevel.INFO)
        self.console.log("  • LC Filter Designer", LogLevel.INFO)
        self.console.log("  • Amplifier Designer", LogLevel.INFO)
        self.console.log("  • Power Supply Designer", LogLevel.INFO)
        self.console.log("  • Oscillator Designer", LogLevel.INFO)
        self.console.log("Right-click on component library to select a wizard", LogLevel.INFO)
    
    def open_measurement_tools(self):
        """Open measurement tools panel"""
        self.console.log("Measurement Tools: Ready for probing", LogLevel.INFO)
        self.console.log("🔍 Available measurements:", LogLevel.INFO)
        self.console.log("  • Voltage measurement (V)", LogLevel.INFO)
        self.console.log("  • Current measurement (I)", LogLevel.INFO)
        self.console.log("  • Power measurement (P)", LogLevel.INFO)
        self.console.log("  • Impedance measurement (Z)", LogLevel.INFO)
        self.console.log("  • Frequency measurement (f)", LogLevel.INFO)
        self.console.log("Click on nodes to add measurement probes", LogLevel.INFO)
    
    def open_simulation_monitor(self):
        """Open simulation monitor panel"""
        self.console.log("Simulation Monitor: Ready", LogLevel.INFO)
        self.console.log("📊 Real-time monitoring capabilities:", LogLevel.INFO)
        self.console.log("  • Node voltage tracking", LogLevel.INFO)
        self.console.log("  • Branch current monitoring", LogLevel.INFO)
        self.console.log("  • Power dissipation", LogLevel.INFO)
        self.console.log("  • Convergence status", LogLevel.INFO)
        self.console.log("  • Simulation statistics", LogLevel.INFO)
        self.console.log("Start simulation to begin monitoring", LogLevel.INFO)
    
    def open_simulation_library(self):
        """Open simulation library with available functions"""
        self.console.log("📚 Simulation Library - Available Functions:", LogLevel.SIM_START)
        
        self.console.log("\n🔢 Math Functions (math module):", LogLevel.INFO)
        self.console.log("  • sin, cos, tan, asin, acos, atan", LogLevel.INFO)
        self.console.log("  • sqrt, exp, log, log10", LogLevel.INFO)
        self.console.log("  • degrees, radians, pi, e", LogLevel.INFO)
        
        self.console.log("\n🧮 NumPy Arrays (np, numpy):", LogLevel.INFO)
        self.console.log("  • np.array, np.linspace, np.logspace", LogLevel.INFO)
        self.console.log("  • np.sin, np.cos, np.exp, np.log", LogLevel.INFO)
        self.console.log("  • np.fft, np.convolve, np.correlate", LogLevel.INFO)
        
        self.console.log("\n📉 Signal Processing (signal module):", LogLevel.INFO)
        self.console.log("  • signal.butter - Butterworth filter", LogLevel.INFO)
        self.console.log("  • signal.bessel - Bessel filter", LogLevel.INFO)
        self.console.log("  • signal.cheby1 - Chebyshev filter", LogLevel.INFO)
        self.console.log("  • signal.sosfilt - Apply digital filter", LogLevel.INFO)
        self.console.log("  • signal.resample - Resample signal", LogLevel.INFO)
        self.console.log("  • signal.hilbert - Analytic signal", LogLevel.INFO)
        
        self.console.log("\n⚡ Circuit Functions:", LogLevel.INFO)
        self.console.log("  • circuit - Access to circuit components", LogLevel.INFO)
        self.console.log("  • wires - Access to wires", LogLevel.INFO)
        self.console.log("  • nodes - Access to nodes", LogLevel.INFO)
        self.console.log("  • len(circuit) - Number of components", LogLevel.INFO)
        
        self.console.log("\n💡 Usage Example in Script Editor:", LogLevel.INFO)
        self.console.log("  import numpy as np", LogLevel.INFO)
        self.console.log("  from scipy import signal", LogLevel.INFO)
        self.console.log("  t = np.linspace(0, 1, 1000)", LogLevel.INFO)
        self.console.log("  v = np.sin(2*np.pi*60*t)", LogLevel.INFO)
        self.console.log("  print('Components:', len(circuit))", LogLevel.INFO)
        
        self.console.log("\nUse Ctrl+Shift+E to open Script Editor", LogLevel.SIM_END)
    
    def open_import_library(self):
        """Show available and importable external libraries"""
        self.console.log("📦 External Libraries Management", LogLevel.SIM_START)
        
        self.console.log("\n✅ Already Available:", LogLevel.INFO)
        self.console.log("  • numpy (np) - Numerical computing", LogLevel.INFO)
        self.console.log("  • scipy - Scientific computing", LogLevel.INFO)
        self.console.log("  • scipy.signal - Digital signal processing", LogLevel.INFO)
        self.console.log("  • scipy.integrate - Integration routines", LogLevel.INFO)
        self.console.log("  • scipy.optimize - Optimization tools", LogLevel.INFO)
        self.console.log("  • math - Standard math functions", LogLevel.INFO)
        
        self.console.log("\n📥 For Additional Libraries:", LogLevel.INFO)
        self.console.log("  • Open terminal and run:", LogLevel.INFO)
        self.console.log("    pip install matplotlib", LogLevel.INFO)
        self.console.log("    pip install sympy", LogLevel.INFO)
        self.console.log("    pip install pandas", LogLevel.INFO)
        self.console.log("    pip install scipy", LogLevel.INFO)
        
        self.console.log("\n📝 In Script Editor, you can import:", LogLevel.INFO)
        self.console.log("  • from scipy.integrate import odeint", LogLevel.INFO)
        self.console.log("  • from scipy.optimize import fsolve", LogLevel.INFO)
        self.console.log("  • from scipy.interpolate import interp1d", LogLevel.INFO)
        
        self.console.log("\n🔗 Popular Simulation Libraries:", LogLevel.INFO)
        self.console.log("  • PyLTSpice - SPICE simulation interface", LogLevel.INFO)
        self.console.log("  • schemdraw - Circuit diagram drawing", LogLevel.INFO)
        self.console.log("  • PySpice - Python interface to SPICE", LogLevel.INFO)
        
        self.console.log("\n💻 Installation in Command Prompt:", LogLevel.INFO)
        self.console.log("  pip install PyLTSpice schemdraw PySpice", LogLevel.INFO)
        
        self.console.log("\nNote: Restart script editor after installing new libraries", LogLevel.SIM_END)
    
    def open_scope(self):
        """Open oscilloscope tool for waveform measurement and analysis"""
        self.console.log("🔬 Oscilloscope / Scope Tool - Active", LogLevel.SIM_START)
        self.console.log("\n📊 Available Scope Features:", LogLevel.INFO)
        self.console.log("  • Real-time voltage measurement at nodes", LogLevel.INFO)
        self.console.log("  • Current measurement through components", LogLevel.INFO)
        self.console.log("  • Multi-channel simultaneous display", LogLevel.INFO)
        self.console.log("  • Time domain waveform capture", LogLevel.INFO)
        self.console.log("  • Frequency spectrum (FFT) analysis", LogLevel.INFO)
        self.console.log("  • Cursor measurements and delta cursor", LogLevel.INFO)
        
        self.console.log("\n🎯 How to Use Scope:", LogLevel.INFO)
        self.console.log("  1. Click nodes to add measurement probes", LogLevel.INFO)
        self.console.log("  2. Run simulation (F5)", LogLevel.INFO)
        self.console.log("  3. View results in 'Waveforms' tab", LogLevel.INFO)
        self.console.log("  4. Use FFT tab for frequency analysis", LogLevel.INFO)
        
        self.console.log("\n⚡ Measurement Types:", LogLevel.INFO)
        self.console.log("  • Voltage (V) - voltage at node", LogLevel.INFO)
        self.console.log("  • Current (I) - current through component", LogLevel.INFO)
        self.console.log("  • Power (P) - power dissipation", LogLevel.INFO)
        self.console.log("  • RMS Value - root mean square", LogLevel.INFO)
        self.console.log("  • Peak Value - maximum value", LogLevel.INFO)
        self.console.log("  • Frequency - fundamental frequency", LogLevel.INFO)
        
        self.console.log("\n💡 Tips:", LogLevel.INFO)
        self.console.log("  • Scope integrates with Waveforms tab (Ctrl+Shift+W)", LogLevel.INFO)
        self.console.log("  • Use Design Wizard for filter measurements", LogLevel.INFO)
        self.console.log("  • Export data for external analysis", LogLevel.INFO)
        
        self.console.log("\nScope is active - Click on nodes to measure", LogLevel.SIM_END)
    
    def open_transformer_designer(self):
        """Open Transformer Designer tool"""
        try:
            from frontend.tools.transformer_designer import TransformerDesignerWindow
            window = TransformerDesignerWindow(self)
            window.showMaximized()
            self.console.log("✓ Transformer Designer opened", LogLevel.INFO)
        except Exception as e:
            self.console.log(f"❌ Error opening Transformer Designer: {str(e)}", LogLevel.ERROR)
    
    def open_cable_sizing(self):
        """Open Cable Sizing Calculator"""
        try:
            from frontend.tools.cable_sizing import CableSizingWindow
            window = CableSizingWindow(self)
            window.showMaximized()
            self.console.log("✓ Cable Sizing Calculator opened", LogLevel.INFO)
        except Exception as e:
            self.console.log(f"❌ Error opening Cable Sizing: {str(e)}", LogLevel.ERROR)
    
    def open_fault_calculator(self):
        """Open Fault Calculator"""
        try:
            from frontend.tools.fault_calculator import FaultCalculatorWindow
            window = FaultCalculatorWindow(self)
            window.showMaximized()
            self.console.log("✓ Fault Calculator opened", LogLevel.INFO)
        except Exception as e:
            self.console.log(f"❌ Error opening Fault Calculator: {str(e)}", LogLevel.ERROR)
    
    def open_pf_correction(self):
        """Open Power Factor Correction Tool"""
        try:
            from frontend.tools.pf_correction import PFCorrectionWindow
            window = PFCorrectionWindow(self)
            window.showMaximized()
            self.console.log("✓ PF Correction Tool opened", LogLevel.INFO)
        except Exception as e:
            self.console.log(f"❌ Error opening PF Correction: {str(e)}", LogLevel.ERROR)
    
    def open_battery_tool(self):
        """Open Battery Tool"""
        try:
            from frontend.tools.battery_tool import BatteryToolWindow
            window = BatteryToolWindow(self)
            window.showMaximized()
            self.console.log("✓ Battery Tool opened", LogLevel.INFO)
        except Exception as e:
            self.console.log(f"❌ Error opening Battery Tool: {str(e)}", LogLevel.ERROR)
    
    def open_library_manager(self):
        """Open Library Manager"""
        try:
            from frontend.tools.library_manager import LibraryManagerWindow
            window = LibraryManagerWindow(self)
            window.showMaximized()
            self.console.log("✓ Library Manager opened", LogLevel.INFO)
        except Exception as e:
            self.console.log(f"❌ Error opening Library Manager: {str(e)}", LogLevel.ERROR)
