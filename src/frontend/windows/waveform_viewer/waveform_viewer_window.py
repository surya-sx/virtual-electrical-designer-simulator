"""
Waveform Viewer Window - Interactive display for circuit simulation waveforms
Features: Multiple traces, analysis tools, export capabilities
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QSpinBox, QCheckBox, QLabel,
    QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox,
    QSplitter, QStatusBar, QToolBar, QTabWidget, QListWidget,
    QListWidgetItem
)
from PySide6.QtGui import QFont, QIcon, QColor, QTextCursor
from PySide6.QtCore import Qt, Signal, QSize, QTimer
from typing import Dict, List, Optional, Tuple
import numpy as np
from pathlib import Path

try:
    from pyqtgraph import PlotWidget, PlotItem, ViewBox
    HAS_PYQTGRAPH = True
except ImportError:
    HAS_PYQTGRAPH = False

from .waveform_base import WaveformData, WaveformPlotter, WaveformAnalyzer, WaveformProcessor


class PyQtGraphPlotter(WaveformPlotter):
    """Plotter using pyqtgraph for fast rendering"""
    
    def __init__(self, parent=None):
        super().__init__()
        
        if not HAS_PYQTGRAPH:
            raise ImportError("pyqtgraph is required for waveform plotting")
        
        self.plot_widget = PlotWidget(parent)
        self.plot_item = self.plot_widget.getPlotItem()
        self.plot_data_items = {}
        
        # Configure plot
        self.plot_item.setLabel('left', 'Voltage', units='V')
        self.plot_item.setLabel('bottom', 'Time', units='s')
        self.plot_item.showGrid(True, True, alpha=0.3)
    
    def add_waveform(self, waveform: WaveformData):
        """Add waveform to plot"""
        super().add_waveform(waveform)
        
        # Parse color
        if waveform.color.startswith('#'):
            rgb = waveform.color.lstrip('#')
            color = tuple(int(rgb[i:i+2], 16) for i in (0, 2, 4))
        else:
            color = (0, 102, 204)  # Default blue
        
        # Plot
        pen = {'color': color, 'width': 2}
        plot_data = self.plot_item.plot(
            waveform.x_data, waveform.y_data,
            name=waveform.name,
            pen=pen
        )
        
        self.plot_data_items[waveform.name] = plot_data
    
    def remove_waveform(self, waveform_name: str):
        """Remove waveform from plot"""
        super().remove_waveform(waveform_name)
        
        if waveform_name in self.plot_data_items:
            self.plot_item.removeItem(self.plot_data_items[waveform_name])
            del self.plot_data_items[waveform_name]
    
    def update_plot(self):
        """Refresh plot"""
        self.plot_widget.update()
    
    def set_x_range(self, x_min: float, x_max: float):
        """Set X-axis range"""
        self.plot_item.setXRange(x_min, x_max)
    
    def set_y_range(self, y_min: float, y_max: float):
        """Set Y-axis range"""
        self.plot_item.setYRange(y_min, y_max)
    
    def get_plot_widget(self):
        """Get PyQt widget for integration"""
        return self.plot_widget


class EnhancedWaveformViewerWindow(QMainWindow):
    """Enhanced waveform viewer with analysis and export"""
    
    # Signals
    export_requested = Signal(str)  # export format
    analysis_completed = Signal(dict)  # analysis results
    
    def __init__(self, parent=None, waveforms: List[WaveformData] = None):
        super().__init__(parent)
        self.waveforms = waveforms or []
        self.current_waveform: Optional[WaveformData] = None
        self.analyzer = WaveformAnalyzer()
        self.processor = WaveformProcessor()
        
        # Plotter
        try:
            self.plotter = PyQtGraphPlotter(self)
            self.has_plotter = True
        except ImportError:
            self.plotter = None
            self.has_plotter = False
        
        self.setWindowTitle("Waveform Viewer")
        self.setWindowIcon(QIcon.fromTheme("chart-line"))
        self.setGeometry(100, 100, 1400, 800)
        
        self._setup_ui()
        self._apply_styles()
        
        if self.waveforms:
            for waveform in self.waveforms:
                self._add_waveform_to_display(waveform)
        
        self.show()
    
    def _setup_ui(self):
        """Setup UI components"""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Toolbar
        self._setup_toolbar()
        
        # Main splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left: Plot
        if self.has_plotter:
            plot_container = self.plotter.get_plot_widget()
            splitter.addWidget(plot_container)
        else:
            error_label = QLabel("pyqtgraph not available.\nInstall with: pip install pyqtgraph")
            splitter.addWidget(error_label)
        
        # Right: Panels (tabs)
        right_tabs = QTabWidget()
        
        # Waveforms list tab
        self.waveforms_panel = self._create_waveforms_panel()
        right_tabs.addTab(self.waveforms_panel, "Waveforms")
        
        # Analysis tab
        self.analysis_panel = self._create_analysis_panel()
        right_tabs.addTab(self.analysis_panel, "Analysis")
        
        # Processing tab
        self.processing_panel = self._create_processing_panel()
        right_tabs.addTab(self.processing_panel, "Processing")
        
        splitter.addWidget(right_tabs)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter)
        
        # Status bar
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Ready")
    
    def _setup_toolbar(self):
        """Setup toolbar"""
        toolbar = QToolBar("Waveform Toolbar")
        toolbar.setIconSize(QSize(20, 20))
        self.addToolBar(toolbar)
        
        # File operations
        open_btn = toolbar.addAction("Open")
        open_btn.triggered.connect(self._open_waveforms)
        open_btn.setShortcut("Ctrl+O")
        
        save_btn = toolbar.addAction("Save")
        save_btn.triggered.connect(self._save_waveforms)
        save_btn.setShortcut("Ctrl+S")
        
        toolbar.addSeparator()
        
        # View controls
        auto_scale_btn = toolbar.addAction("Auto Scale")
        auto_scale_btn.triggered.connect(self._auto_scale)
        auto_scale_btn.setShortcut("Ctrl+A")
        
        zoom_in_btn = toolbar.addAction("Zoom In")
        zoom_in_btn.triggered.connect(self._zoom_in)
        zoom_in_btn.setShortcut("Ctrl++")
        
        zoom_out_btn = toolbar.addAction("Zoom Out")
        zoom_out_btn.triggered.connect(self._zoom_out)
        zoom_out_btn.setShortcut("Ctrl+-")
        
        toolbar.addSeparator()
        
        # Analysis
        analyze_btn = toolbar.addAction("Analyze")
        analyze_btn.triggered.connect(self._analyze_current)
        
        # Export
        toolbar.addWidget(QLabel("Export:"))
        self.export_format = QComboBox()
        self.export_format.addItems(["CSV", "NumPy (.npy)", "JSON"])
        toolbar.addWidget(self.export_format)
        
        export_btn = toolbar.addAction("Export")
        export_btn.triggered.connect(self._export_waveforms)
        
        toolbar.addStretch()
        
        # Info label
        self.info_label = QLabel("No waveforms loaded")
        toolbar.addWidget(self.info_label)
    
    def _create_waveforms_panel(self) -> QWidget:
        """Create waveforms list panel"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        label = QLabel("Loaded Waveforms:")
        layout.addWidget(label)
        
        # Waveforms list
        self.waveforms_list = QListWidget()
        self.waveforms_list.itemSelectionChanged.connect(self._on_waveform_selected)
        layout.addWidget(self.waveforms_list)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self._remove_waveform)
        btn_layout.addWidget(remove_btn)
        
        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(self._clear_waveforms)
        btn_layout.addWidget(clear_btn)
        
        layout.addLayout(btn_layout)
        
        return widget
    
    def _create_analysis_panel(self) -> QWidget:
        """Create analysis panel"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        label = QLabel("Analysis Results:")
        layout.addWidget(label)
        
        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(2)
        self.results_table.setHorizontalHeaderLabels(["Property", "Value"])
        self.results_table.setMaximumHeight(300)
        layout.addWidget(self.results_table)
        
        # Analysis options
        options_label = QLabel("Options:")
        layout.addWidget(options_label)
        
        options_layout = QVBoxLayout()
        
        # Peak detection
        self.detect_peaks_cb = QCheckBox("Detect Peaks")
        self.detect_peaks_cb.setChecked(True)
        options_layout.addWidget(self.detect_peaks_cb)
        
        # Frequency analysis
        self.freq_analysis_cb = QCheckBox("Frequency Analysis")
        self.freq_analysis_cb.setChecked(True)
        options_layout.addWidget(self.freq_analysis_cb)
        
        # Harmonic analysis
        self.harmonic_analysis_cb = QCheckBox("Harmonic Analysis")
        self.harmonic_analysis_cb.setChecked(True)
        options_layout.addWidget(self.harmonic_analysis_cb)
        
        layout.addLayout(options_layout)
        
        # Analyze button
        analyze_btn = QPushButton("Analyze Selected")
        analyze_btn.clicked.connect(self._analyze_current)
        layout.addWidget(analyze_btn)
        
        layout.addStretch()
        return widget
    
    def _create_processing_panel(self) -> QWidget:
        """Create processing panel"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        label = QLabel("Waveform Processing:")
        layout.addWidget(label)
        
        # Smoothing
        smooth_label = QLabel("Smoothing:")
        layout.addWidget(smooth_label)
        
        smooth_layout = QHBoxLayout()
        smooth_layout.addWidget(QLabel("Window:"))
        
        self.smooth_window = QSpinBox()
        self.smooth_window.setMinimum(3)
        self.smooth_window.setMaximum(51)
        self.smooth_window.setValue(5)
        self.smooth_window.setSingleStep(2)
        smooth_layout.addWidget(self.smooth_window)
        
        smooth_btn = QPushButton("Apply Smooth")
        smooth_btn.clicked.connect(self._apply_smooth)
        smooth_layout.addWidget(smooth_btn)
        
        layout.addLayout(smooth_layout)
        
        # Scaling
        scale_label = QLabel("Scaling:")
        layout.addWidget(scale_label)
        
        scale_layout = QHBoxLayout()
        scale_layout.addWidget(QLabel("Factor:"))
        
        self.scale_factor = QSpinBox()
        self.scale_factor.setMinimum(-100)
        self.scale_factor.setMaximum(100)
        self.scale_factor.setValue(1)
        scale_layout.addWidget(self.scale_factor)
        
        scale_btn = QPushButton("Apply Scale")
        scale_btn.clicked.connect(self._apply_scale)
        scale_layout.addWidget(scale_btn)
        
        layout.addLayout(scale_layout)
        
        # Resampling
        resample_label = QLabel("Resampling:")
        layout.addWidget(resample_label)
        
        resample_layout = QHBoxLayout()
        resample_layout.addWidget(QLabel("Points:"))
        
        self.resample_points = QSpinBox()
        self.resample_points.setMinimum(10)
        self.resample_points.setMaximum(10000)
        self.resample_points.setValue(1000)
        resample_layout.addWidget(self.resample_points)
        
        resample_btn = QPushButton("Resample")
        resample_btn.clicked.connect(self._apply_resample)
        resample_layout.addWidget(resample_btn)
        
        layout.addLayout(resample_layout)
        
        layout.addStretch()
        return widget
    
    def _apply_styles(self):
        """Apply custom styles"""
        self.setStyleSheet("""
            QMainWindow {
                background: #ffffff;
            }
            QLabel {
                font-weight: bold;
                color: #333;
            }
            QTableWidget {
                background: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 10px;
            }
            QListWidget {
                background: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            QPushButton {
                background: #007bff;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #0056b3;
            }
            QPushButton:pressed {
                background: #004085;
            }
        """)
    
    # Public methods
    def add_waveform(self, waveform: WaveformData):
        """Add waveform to viewer"""
        self.waveforms.append(waveform)
        self._add_waveform_to_display(waveform)
    
    def _add_waveform_to_display(self, waveform: WaveformData):
        """Add waveform to display"""
        if self.has_plotter:
            self.plotter.add_waveform(waveform)
        
        # Add to list
        item = QListWidgetItem(waveform.name)
        item.setData(Qt.UserRole, waveform)
        self.waveforms_list.addItem(item)
        
        # Update info
        self._update_info_label()
    
    def _update_info_label(self):
        """Update info label"""
        self.info_label.setText(f"{len(self.waveforms)} waveform(s)")
    
    # Event handlers
    def _on_waveform_selected(self):
        """Handle waveform selection"""
        items = self.waveforms_list.selectedItems()
        if items:
            self.current_waveform = items[0].data(Qt.UserRole)
    
    # Analysis
    def _analyze_current(self):
        """Analyze current waveform"""
        if not self.current_waveform:
            QMessageBox.warning(self, "Select Waveform", "Please select a waveform to analyze")
            return
        
        self.results_table.setRowCount(0)
        results = {}
        row = 0
        
        # Statistics
        stats = self.current_waveform.stats
        for key, value in stats.items():
            results[key.replace('_', ' ').title()] = f"{value:.6f}"
            self.results_table.insertRow(row)
            self.results_table.setItem(row, 0, QTableWidgetItem(key.replace('_', ' ').title()))
            self.results_table.setItem(row, 1, QTableWidgetItem(f"{value:.6f}"))
            row += 1
        
        # Frequency analysis
        if self.freq_analysis_cb.isChecked():
            freq = self.analyzer.compute_frequency(self.current_waveform)
            if freq:
                results['Frequency'] = f"{freq:.6f} Hz"
                self.results_table.insertRow(row)
                self.results_table.setItem(row, 0, QTableWidgetItem("Frequency"))
                self.results_table.setItem(row, 1, QTableWidgetItem(f"{freq:.6f} Hz"))
                row += 1
        
        # THD
        if self.harmonic_analysis_cb.isChecked():
            thd = self.analyzer.compute_thd(self.current_waveform)
            if thd:
                results['THD'] = f"{thd:.2f}%"
                self.results_table.insertRow(row)
                self.results_table.setItem(row, 0, QTableWidgetItem("THD"))
                self.results_table.setItem(row, 1, QTableWidgetItem(f"{thd:.2f}%"))
        
        self.analysis_completed.emit(results)
        self.statusBar().showMessage("Analysis completed")
    
    # Processing
    def _apply_smooth(self):
        """Apply smoothing filter"""
        if not self.current_waveform:
            return
        
        smoothed = self.processor.smooth(self.current_waveform, self.smooth_window.value())
        self.add_waveform(smoothed)
    
    def _apply_scale(self):
        """Apply scaling"""
        if not self.current_waveform:
            return
        
        scaled = self.processor.scale(self.current_waveform, self.scale_factor.value())
        self.add_waveform(scaled)
    
    def _apply_resample(self):
        """Apply resampling"""
        if not self.current_waveform:
            return
        
        resampled = self.processor.resample(self.current_waveform, self.resample_points.value())
        self.add_waveform(resampled)
    
    # File operations
    def _open_waveforms(self):
        """Open waveforms from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Waveforms", "", "NumPy Files (*.npy);;CSV Files (*.csv);;JSON Files (*.json)"
        )
        # TODO: Implement file loading
        pass
    
    def _save_waveforms(self):
        """Save waveforms to file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Waveforms", "", "NumPy Files (*.npy);;CSV Files (*.csv);;JSON Files (*.json)"
        )
        # TODO: Implement file saving
        pass
    
    def _export_waveforms(self):
        """Export waveforms"""
        format_str = self.export_format.currentText()
        self.export_requested.emit(format_str)
        # TODO: Implement export
        pass
    
    # View control
    def _auto_scale(self):
        """Auto-scale plot"""
        if self.has_plotter:
            self.plotter.auto_scale()
    
    def _zoom_in(self):
        """Zoom in"""
        # TODO: Implement zoom
        pass
    
    def _zoom_out(self):
        """Zoom out"""
        # TODO: Implement zoom
        pass
    
    def _remove_waveform(self):
        """Remove selected waveform"""
        items = self.waveforms_list.selectedItems()
        if items:
            waveform = items[0].data(Qt.UserRole)
            self.waveforms.remove(waveform)
            if self.has_plotter:
                self.plotter.remove_waveform(waveform.name)
            self.waveforms_list.takeItem(self.waveforms_list.row(items[0]))
            self._update_info_label()
    
    def _clear_waveforms(self):
        """Clear all waveforms"""
        self.waveforms.clear()
        if self.has_plotter:
            self.plotter.clear_waveforms()
        self.waveforms_list.clear()
        self._update_info_label()
