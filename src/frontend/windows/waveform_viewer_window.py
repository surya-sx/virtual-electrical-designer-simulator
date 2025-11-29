"""
Waveform Viewer Window - Display simulation results with multiple channels
Time domain and frequency domain analysis with zoom/pan controls
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QCheckBox, QSpinBox, QDoubleSpinBox,
    QComboBox, QMessageBox, QScrollArea, QGridLayout, QFrame,
    QToolBar, QStatusBar
)
from PySide6.QtGui import QIcon, QFont
from PySide6.QtCore import Qt, Signal, QSize
import pyqtgraph as pg
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class WaveformData:
    """Container for waveform data"""
    name: str
    time: np.ndarray
    values: np.ndarray
    unit: str = "V"
    color: str = "blue"
    visible: bool = True


class WaveformViewerWindow(QMainWindow):
    """Separate window for viewing simulation results and waveforms"""
    
    # Signals
    waveform_selected = Signal(str)
    zoom_changed = Signal(float)
    
    def __init__(self, parent=None, window_title: str = "Waveform Viewer"):
        super().__init__(parent)
        self.setWindowTitle(window_title)
        self.setWindowIcon(QIcon.fromTheme("image-jpeg"))
        self.setGeometry(150, 150, 1200, 700)
        
        # Data storage
        self.waveforms: Dict[str, WaveformData] = {}
        self.active_waveforms: List[str] = []
        self.current_time_domain = True
        self.zoom_level = 1.0
        
        # Color cycle for multiple waveforms
        self.colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", "#98D8C8", "#F7DC6F"]
        self.color_index = 0
        
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Setup UI components"""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Toolbar
        toolbar = QToolBar("Waveform Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # Display mode
        toolbar.addWidget(QLabel("Display:"))
        self.display_mode = QComboBox()
        self.display_mode.addItems(["Time Domain", "Frequency Domain", "Both"])
        self.display_mode.currentTextChanged.connect(self._on_display_mode_changed)
        toolbar.addWidget(self.display_mode)
        
        toolbar.addSeparator()
        
        # Zoom controls
        toolbar.addWidget(QLabel("Zoom:"))
        self.zoom_slider = QDoubleSpinBox()
        self.zoom_slider.setMinimum(0.1)
        self.zoom_slider.setMaximum(10.0)
        self.zoom_slider.setValue(1.0)
        self.zoom_slider.setSingleStep(0.1)
        self.zoom_slider.setSuffix("x")
        self.zoom_slider.setFixedWidth(80)
        self.zoom_slider.valueChanged.connect(self._on_zoom_changed)
        toolbar.addWidget(self.zoom_slider)
        
        self.fit_btn = toolbar.addAction("Fit to View")
        self.fit_btn.triggered.connect(self._fit_to_view)
        
        toolbar.addSeparator()
        
        # Auto scroll / Pause
        self.auto_scroll_cb = QCheckBox("Auto-scroll")
        self.auto_scroll_cb.setChecked(True)
        toolbar.addWidget(self.auto_scroll_cb)
        
        toolbar.addSeparator()
        
        # Export / Clear
        self.export_btn = toolbar.addAction("Export Data")
        self.export_btn.triggered.connect(self._export_data)
        
        self.clear_btn = toolbar.addAction("Clear All")
        self.clear_btn.triggered.connect(self._clear_all)
        
        # Main content area
        content_layout = QHBoxLayout()
        
        # Left: Plot area (use pyqtgraph)
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setLabel('left', 'Amplitude', units='V')
        self.plot_widget.setLabel('bottom', 'Time', units='s')
        self.plot_widget.setTitle('Simulation Results')
        self.plot_widget.addLegend()
        self.plot_widget.setBackground('w')
        self.plot_widget.showGrid(True, True, 0.2)
        content_layout.addWidget(self.plot_widget, 3)
        
        # Right: Waveform list and controls
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Waveforms list
        right_layout.addWidget(QLabel("Waveforms:"))
        
        self.waveform_list = QScrollArea()
        self.waveform_list.setWidgetResizable(True)
        self.waveform_list_widget = QWidget()
        self.waveform_list_layout = QVBoxLayout(self.waveform_list_widget)
        self.waveform_list_layout.setSpacing(5)
        self.waveform_list.setWidget(self.waveform_list_widget)
        right_layout.addWidget(self.waveform_list)
        
        # Statistics panel
        right_layout.addWidget(QLabel("Statistics:"))
        self.stats_frame = QFrame()
        self.stats_layout = QVBoxLayout(self.stats_frame)
        self.stats_frame.setStyleSheet("border: 1px solid #ddd; border-radius: 4px; padding: 5px;")
        right_layout.addWidget(self.stats_frame)
        
        content_layout.addWidget(right_panel, 1)
        
        main_layout.addLayout(content_layout, 1)
        
        # Status bar
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("No data loaded")
    
    def _apply_styles(self):
        """Apply custom styles"""
        self.setStyleSheet("""
            QMainWindow {
                background: #ffffff;
            }
            QLabel {
                color: #333;
                font-weight: bold;
            }
            QToolBar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ffffff, stop:1 #f0f0f0);
                border-bottom: 1px solid #bbb;
            }
            QToolButton {
                background: transparent;
                border-radius: 4px;
                padding: 4px 8px;
            }
            QToolButton:hover {
                background: #e0e7ff;
            }
            QCheckBox {
                color: #333;
            }
            QComboBox {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 4px;
            }
        """)
    
    def add_waveform(self, name: str, time: np.ndarray, values: np.ndarray, 
                    unit: str = "V", color: Optional[str] = None):
        """Add a waveform to the viewer"""
        if color is None:
            color = self.colors[self.color_index % len(self.colors)]
            self.color_index += 1
        
        waveform = WaveformData(name, time, values, unit, color, True)
        self.waveforms[name] = waveform
        self.active_waveforms.append(name)
        
        # Add to UI
        self._add_waveform_to_ui(name)
        
        # Replot
        self._replot()
        self.statusBar().showMessage(f"Waveform added: {name}")
    
    def _add_waveform_to_ui(self, name: str):
        """Add waveform to list UI"""
        waveform = self.waveforms[name]
        
        # Create checkbox for visibility
        waveform_frame = QFrame()
        waveform_frame.setStyleSheet(f"""
            QFrame {{
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                background: #f9f9f9;
            }}
        """)
        
        waveform_layout = QVBoxLayout(waveform_frame)
        
        # Visibility checkbox
        check_box = QCheckBox(f"{name} ({waveform.unit})")
        check_box.setChecked(True)
        check_box.stateChanged.connect(
            lambda state: self._toggle_waveform(name, state == Qt.Checked)
        )
        waveform_layout.addWidget(check_box)
        
        # Stats for this waveform
        stats_text = f"Min: {waveform.values.min():.6f} | Max: {waveform.values.max():.6f} | Avg: {waveform.values.mean():.6f}"
        stats_label = QLabel(stats_text)
        stats_label.setFont(QFont("Courier New", 8))
        stats_label.setStyleSheet("color: #666;")
        waveform_layout.addWidget(stats_label)
        
        # Color indicator
        color_frame = QFrame()
        color_frame.setStyleSheet(f"background: {waveform.color}; border-radius: 2px;")
        color_frame.setFixedHeight(10)
        waveform_layout.addWidget(color_frame)
        
        self.waveform_list_layout.addWidget(waveform_frame)
    
    def _toggle_waveform(self, name: str, visible: bool):
        """Toggle waveform visibility"""
        if name in self.waveforms:
            self.waveforms[name].visible = visible
            self._replot()
    
    def _replot(self):
        """Redraw plot with active waveforms"""
        self.plot_widget.clear()
        
        if not self.active_waveforms:
            self.statusBar().showMessage("No waveforms to display")
            return
        
        # Plot each active waveform
        for name in self.active_waveforms:
            waveform = self.waveforms[name]
            if waveform.visible:
                self.plot_widget.plot(
                    waveform.time,
                    waveform.values,
                    name=name,
                    pen=pg.mkPen(color=waveform.color, width=2)
                )
        
        # Update statistics
        self._update_statistics()
    
    def _update_statistics(self):
        """Update statistics panel"""
        # Clear old stats
        for i in reversed(range(self.stats_layout.count())): 
            self.stats_layout.itemAt(i).widget().setParent(None)
        
        # Add statistics for each visible waveform
        for name in self.active_waveforms:
            waveform = self.waveforms[name]
            if waveform.visible:
                stats_label = QLabel()
                stats_label.setFont(QFont("Courier New", 9))
                
                min_val = waveform.values.min()
                max_val = waveform.values.max()
                mean_val = waveform.values.mean()
                rms_val = np.sqrt(np.mean(waveform.values**2))
                peak_peak = max_val - min_val
                
                stats_text = f"""<b>{name}</b><br>
                Min: {min_val:.6f} {waveform.unit}<br>
                Max: {max_val:.6f} {waveform.unit}<br>
                Peak-Peak: {peak_peak:.6f} {waveform.unit}<br>
                Avg: {mean_val:.6f} {waveform.unit}<br>
                RMS: {rms_val:.6f} {waveform.unit}"""
                
                stats_label.setText(stats_text)
                self.stats_layout.addWidget(stats_label)
    
    def _on_display_mode_changed(self, mode: str):
        """Handle display mode change"""
        if mode == "Frequency Domain":
            self._show_frequency_domain()
        elif mode == "Time Domain":
            self._replot()
        else:  # Both
            self._show_both_domains()
    
    def _show_frequency_domain(self):
        """Show frequency domain representation"""
        # TODO: Implement FFT
        QMessageBox.information(self, "Frequency Domain", "FFT implementation coming soon")
    
    def _show_both_domains(self):
        """Show both time and frequency domains"""
        # TODO: Implement split view
        pass
    
    def _on_zoom_changed(self, zoom: float):
        """Handle zoom level change"""
        self.zoom_level = zoom
        # TODO: Implement zoom
    
    def _fit_to_view(self):
        """Fit plot to current view"""
        self.plot_widget.autoRange()
        self.zoom_slider.setValue(1.0)
    
    def _export_data(self):
        """Export waveform data to file"""
        QMessageBox.information(self, "Export", "Export feature coming soon")
    
    def _clear_all(self):
        """Clear all waveforms"""
        reply = QMessageBox.question(
            self, "Clear All",
            "Clear all waveforms?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.waveforms.clear()
            self.active_waveforms.clear()
            
            # Clear UI
            for i in reversed(range(self.waveform_list_layout.count())): 
                self.waveform_list_layout.itemAt(i).widget().setParent(None)
            
            self.plot_widget.clear()
            self.statusBar().showMessage("All waveforms cleared")
    
    def load_csv_data(self, file_path: str):
        """Load waveform data from CSV"""
        try:
            import pandas as pd
            df = pd.read_csv(file_path)
            
            # Assume first column is time
            time = df.iloc[:, 0].values
            
            # Add other columns as waveforms
            for col in df.columns[1:]:
                self.add_waveform(col, time, df[col].values)
            
            self.statusBar().showMessage(f"Loaded: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load CSV: {str(e)}")
    
    def closeEvent(self, event):
        """Handle window close"""
        event.accept()
