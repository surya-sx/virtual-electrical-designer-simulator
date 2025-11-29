"""
Reports Panel - professional report generation and multi-format export
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QTextEdit, QPushButton, QHBoxLayout,
    QFileDialog, QMessageBox, QComboBox, QLabel, QProgressBar
)
from PySide6.QtCore import Signal, Qt


class ReportsPanel(QWidget):
    """Panel for generating and exporting professional reports"""
    
    # Signals
    export_started = Signal()
    export_finished = Signal(bool)  # success flag
    
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Report generation toolbar
        toolbar = QHBoxLayout()
        
        self.generate_button = QPushButton("Generate Reports")
        self.generate_button.clicked.connect(self._generate_reports)
        toolbar.addWidget(self.generate_button)
        
        toolbar.addWidget(QLabel("Export Format:"))
        self.export_format_combo = QComboBox()
        self.export_format_combo.addItems(["HTML", "PDF", "JSON", "CSV"])
        toolbar.addWidget(self.export_format_combo)
        
        self.export_button = QPushButton("Export")
        self.export_button.clicked.connect(self._export_report)
        toolbar.addWidget(self.export_button)
        
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Tabbed reports
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Summary tab
        self.summary_view = QTextEdit()
        self.summary_view.setReadOnly(True)
        self.summary_view.setPlaceholderText("Click 'Generate Reports' to create summary...")
        self.tabs.addTab(self.summary_view, "Summary")
        
        # BOM tab
        self.bom_view = QTextEdit()
        self.bom_view.setReadOnly(True)
        self.bom_view.setPlaceholderText("Click 'Generate Reports' to create BOM...")
        self.tabs.addTab(self.bom_view, "Bill of Materials")
        
        # Results tab
        self.results_view = QTextEdit()
        self.results_view.setReadOnly(True)
        self.results_view.setPlaceholderText("Simulation results will appear here...")
        self.tabs.addTab(self.results_view, "Simulation Results")
        
        # Data storage
        self.report_data = {
            "summary": "",
            "bom": "",
            "results": ""
        }
        self.report_generator = None
        self.circuit_data = None
        self.simulation_data = None
    
    def set_report_generator(self, generator):
        """Set the report generator instance"""
        self.report_generator = generator
    
    def set_circuit_data(self, circuit_data: dict):
        """Set circuit data for report generation"""
        self.circuit_data = circuit_data
    
    def set_simulation_data(self, sim_type: str, sim_data: dict):
        """Set simulation data for report generation"""
        self.simulation_data = {"type": sim_type, "data": sim_data}
    
    def _generate_reports(self):
        """Generate all reports"""
        if not self.report_generator or not self.circuit_data:
            QMessageBox.warning(self, "Generate Reports", "No circuit data available")
            return
        
        try:
            # Extract circuit components and wires
            components = self.circuit_data.get("components", {})
            wires = self.circuit_data.get("wires", {})
            
            # Generate summary
            self.report_data["summary"] = self.report_generator.build_summary(
                components, wires
            )
            self.summary_view.setPlainText(self.report_data["summary"])
            
            # Generate BOM
            self.report_data["bom"] = self.report_generator.build_bom(components)
            self.bom_view.setPlainText(self.report_data["bom"])
            
            # Generate simulation results if available
            if self.simulation_data:
                self.report_data["results"] = self.report_generator.build_simulation_results(
                    self.simulation_data["type"],
                    self.simulation_data["data"]
                )
                self.results_view.setPlainText(self.report_data["results"])
            
            self.tabs.setCurrentIndex(0)  # Show summary tab
            
        except Exception as e:
            QMessageBox.critical(self, "Generate Reports", f"Error: {str(e)}")
    
    def _export_report(self):
        """Export reports in selected format"""
        if not any(self.report_data.values()):
            QMessageBox.warning(self, "Export", "Generate reports first")
            return
        
        export_format = self.export_format_combo.currentText()
        
        if export_format == "HTML":
            filename, _ = QFileDialog.getSaveFileName(
                self, "Export as HTML", "",
                "HTML Files (*.html)"
            )
            if filename:
                self.export_started.emit()
                success = self.report_generator.export_html(
                    self.report_data["summary"],
                    self.report_data["bom"],
                    self.report_data["results"],
                    filename
                )
                self.export_finished.emit(success)
                if success:
                    QMessageBox.information(self, "Export", f"Report exported to {filename}")
        
        elif export_format == "PDF":
            filename, _ = QFileDialog.getSaveFileName(
                self, "Export as PDF", "",
                "PDF Files (*.pdf)"
            )
            if filename:
                self.export_started.emit()
                success = self.report_generator.export_pdf(
                    self.report_data["summary"],
                    self.report_data["bom"],
                    self.report_data["results"],
                    filename
                )
                self.export_finished.emit(success)
                if success:
                    QMessageBox.information(self, "Export", f"Report exported to {filename}")
        
        elif export_format == "JSON":
            filename, _ = QFileDialog.getSaveFileName(
                self, "Export as JSON", "",
                "JSON Files (*.json)"
            )
            if filename:
                self.export_started.emit()
                success = self.report_generator.export_json(
                    self.report_data,
                    filename
                )
                self.export_finished.emit(success)
                if success:
                    QMessageBox.information(self, "Export", f"Report exported to {filename}")
        
        elif export_format == "CSV":
            filename, _ = QFileDialog.getSaveFileName(
                self, "Export BOM as CSV", "",
                "CSV Files (*.csv)"
            )
            if filename:
                self.export_started.emit()
                # Parse BOM for CSV export
                bom_items = self._parse_bom_for_csv()
                success = self.report_generator.export_csv(bom_items, filename)
                self.export_finished.emit(success)
                if success:
                    QMessageBox.information(self, "Export", f"BOM exported to {filename}")
    
    def _parse_bom_for_csv(self):
        """Parse BOM text for CSV export"""
        items = []
        lines = self.report_data["bom"].split("\n")
        
        in_table = False
        for line in lines:
            if line.startswith("-" * 20):
                in_table = True
                continue
            
            if in_table and line.strip():
                parts = line.split()
                if len(parts) >= 2:
                    items.append({
                        "name": parts[0] if parts else "",
                        "type": parts[1] if len(parts) > 1 else "",
                        "value": parts[2] if len(parts) > 2 else "-",
                        "quantity": parts[3] if len(parts) > 3 else "1",
                    })
        
        return items
