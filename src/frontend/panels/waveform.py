"""
Waveform Panel - signal visualization with pyqtgraph
"""
from typing import Dict, List, Optional, Tuple
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QPushButton, QLabel, QCheckBox, QComboBox
from PySide6.QtCore import Qt
import pyqtgraph as pg
import numpy as np
from scipy import signal as scipy_signal


class WaveformPanel(QWidget):
    """Panel for displaying waveform plots with advanced features"""
    
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        self.setLayout(layout)
        
        # Plot widget
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setLabel('bottom', 'Time', units='s')
        self.plot_widget.setLabel('left', 'Amplitude', units='V')
        self.plot_widget.setTitle('Waveform Viewer')
        self.plot_widget.showGrid(True, True)
        self.plot_widget.setBackground('w')
        layout.addWidget(self.plot_widget, stretch=3)
        
        # Right sidebar
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)
        
        # Channel list
        right_layout.addWidget(QLabel("Channels:"))
        self.channel_list = QListWidget()
        self.channel_list.itemSelectionChanged.connect(self._on_channel_selected)
        right_layout.addWidget(self.channel_list)
        
        # Display mode
        right_layout.addWidget(QLabel("\nDisplay Mode:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Time Domain", "Frequency (FFT)", "Delta Cursor"])
        self.mode_combo.currentTextChanged.connect(self._on_mode_changed)
        right_layout.addWidget(self.mode_combo)
        
        # Delta cursor mode checkbox
        self.delta_mode_cb = QCheckBox("Delta Mode (Δ)")
        self.delta_mode_cb.toggled.connect(self._on_delta_mode_toggled)
        right_layout.addWidget(self.delta_mode_cb)
        
        # Measurements
        right_layout.addWidget(QLabel("\nMeasurements:"))
        self.measurements_label = QLabel("No signal")
        self.measurements_label.setStyleSheet("font-size: 9px; font-family: monospace;")
        right_layout.addWidget(self.measurements_label)
        
        # Cursor info
        right_layout.addWidget(QLabel("\nCursor Info:"))
        self.cursor_label = QLabel("No cursor")
        self.cursor_label.setStyleSheet("font-size: 9px; font-family: monospace;")
        right_layout.addWidget(self.cursor_label)
        
        # Export button
        export_btn = QPushButton("Export Plot")
        export_btn.clicked.connect(self._export_plot)
        right_layout.addWidget(export_btn)
        
        # Export data button
        export_data_btn = QPushButton("Export Data")
        export_data_btn.clicked.connect(self._export_data)
        right_layout.addWidget(export_data_btn)
        
        right_layout.addStretch()
        layout.addWidget(right_panel, stretch=1)
        
        # Data storage
        self.curves: Dict[str, pg.PlotCurveItem] = {}
        self.data: Dict[str, Dict[str, np.ndarray]] = {}
        self.colors = [
            pg.intColor(i, hues=10)
            for i in range(10)
        ]
        
        # Cursor
        self.v_line = pg.InfiniteLine(angle=90, movable=True, pen=pg.mkPen('r', width=2))
        self.h_line = pg.InfiniteLine(angle=0, movable=True, pen=pg.mkPen('g', width=2))
        self.v_line_2 = pg.InfiniteLine(angle=90, movable=True, pen=pg.mkPen('b', width=1, style=Qt.DashLine))  # Delta cursor
        self.plot_widget.addItem(self.v_line, ignoreBounds=True)
        self.plot_widget.addItem(self.h_line, ignoreBounds=True)
        self.v_line.setCursor(Qt.OpenHandCursor)
        self.v_line_2.hide()  # Hidden by default
        
        # Connect cursor movement
        self.v_line.sigPositionChanged.connect(self._update_cursor_info)
        self.v_line_2.sigPositionChanged.connect(self._update_cursor_info)
        
        # Display mode state
        self.current_mode = "Time Domain"
        self.delta_mode = False
    
    def _on_mode_changed(self, mode: str):
        """Handle display mode change"""
        self.current_mode = mode
        self._refresh_display()
    
    def _on_delta_mode_toggled(self, checked: bool):
        """Toggle delta cursor mode"""
        self.delta_mode = checked
        if checked:
            self.plot_widget.addItem(self.v_line_2, ignoreBounds=True)
            self.v_line_2.show()
        else:
            self.plot_widget.removeItem(self.v_line_2)
            self.v_line_2.hide()
        self._update_cursor_info()
    
    def _refresh_display(self):
        """Refresh waveform display based on mode"""
        self.plot_widget.clear()
        
        if self.current_mode == "Time Domain":
            self._display_time_domain()
        elif self.current_mode == "Frequency (FFT)":
            self._display_fft()
        elif self.current_mode == "Delta Cursor":
            self._display_time_domain()
            self.delta_mode_cb.setChecked(True)
        
        # Re-add cursors
        self.plot_widget.addItem(self.v_line, ignoreBounds=True)
        self.plot_widget.addItem(self.h_line, ignoreBounds=True)
        if self.delta_mode:
            self.plot_widget.addItem(self.v_line_2, ignoreBounds=True)
    
    def _display_time_domain(self):
        """Display signals in time domain"""
        for name, curve in self.curves.items():
            self.plot_widget.addItem(curve)
    
    def _display_fft(self):
        """Display signals as FFT (frequency domain)"""
        self.plot_widget.setLabel('bottom', 'Frequency', units='Hz')
        self.plot_widget.setLabel('left', 'Magnitude', units='')
        self.plot_widget.setTitle('Frequency Response (FFT)')
        
        for name, data in self.data.items():
            time = data["time"]
            voltage = data["voltage"]
            
            # Calculate FFT
            fft_result = np.fft.fft(voltage)
            frequencies = np.fft.fftfreq(len(voltage), time[1] - time[0])
            
            # Only plot positive frequencies
            positive_freq_idx = frequencies > 0
            freq_positive = frequencies[positive_freq_idx]
            magnitude = np.abs(fft_result[positive_freq_idx])
            
            color_idx = list(self.data.keys()).index(name) % len(self.colors)
            self.plot_widget.plot(
                freq_positive, magnitude,
                pen=self.colors[color_idx],
                name=name
            )
        
    def add_signal(self, name: str, time: np.ndarray, voltage: np.ndarray):
        """Add signal to plot"""
        color_idx = len(self.curves) % len(self.colors)
        curve = self.plot_widget.plot(
            time, voltage,
            pen=self.colors[color_idx],
            name=name
        )
        
        self.curves[name] = curve
        self.data[name] = {"time": time, "voltage": voltage}
        
        # Add to channel list
        item = QListWidgetItem(name)
        item.setForeground(self.colors[color_idx])
        self.channel_list.addItem(item)
    
    def clear_signals(self):
        """Clear all signals"""
        for curve in self.curves.values():
            self.plot_widget.removeItem(curve)
        self.curves.clear()
        self.data.clear()
        self.channel_list.clear()
    
    def _on_channel_selected(self):
        """Handle channel selection"""
        selected_items = self.channel_list.selectedItems()
        if selected_items:
            selected_item = selected_items[0]
            channel_name = selected_item.text()
            self._update_measurements(channel_name)
    
    def _update_measurements(self, channel_name: str):
        """Calculate and display measurements for signal"""
        if channel_name not in self.data:
            return
        
        voltage = self.data[channel_name]["voltage"]
        
        # Calculate measurements
        rms = np.sqrt(np.mean(voltage ** 2))
        peak = np.max(np.abs(voltage))
        peak_to_peak = np.max(voltage) - np.min(voltage)
        mean = np.mean(voltage)
        
        # Frequency detection (using FFT)
        time = self.data[channel_name]["time"]
        dt = time[1] - time[0] if len(time) > 1 else 1.0
        fft_result = np.fft.fft(voltage)
        frequencies = np.fft.fftfreq(len(voltage), dt)
        
        # Find dominant frequency
        positive_freq_idx = frequencies > 0
        dominant_idx = np.argmax(np.abs(fft_result[positive_freq_idx]))
        dominant_freq = frequencies[positive_freq_idx][dominant_idx]
        
        measurements = f"""RMS:       {rms:.6f} V
Peak:      {peak:.6f} V
Peak-Peak: {peak_to_peak:.6f} V
Mean:      {mean:.6f} V
Freq:      {dominant_freq:.3f} Hz"""
        
        self.measurements_label.setText(measurements)
    
    def _update_cursor_info(self):
        """Update cursor information with delta mode support"""
        x_pos = self.v_line.value()
        y_pos = self.h_line.value()
        
        if self.delta_mode:
            x_pos_2 = self.v_line_2.value()
            delta_x = abs(x_pos_2 - x_pos)
            info = f"Cursor 1: {x_pos:.6f} s\nCursor 2: {x_pos_2:.6f} s\nΔTime: {delta_x:.6f} s"
        else:
            info = f"X: {x_pos:.6f} s\nY: {y_pos:.6f} V"
        
        # Find closest data point
        for channel_name, data in self.data.items():
            time = data["time"]
            voltage = data["voltage"]
            
            # Find closest index
            idx = np.argmin(np.abs(time - x_pos))
            if idx < len(voltage):
                v = voltage[idx]
                t = time[idx]
                if self.delta_mode:
                    # Also find value at second cursor
                    idx2 = np.argmin(np.abs(time - x_pos_2))
                    if idx2 < len(voltage):
                        v2 = voltage[idx2]
                        delta_v = abs(v2 - v)
                        info += f"\n{channel_name}:\n  Cursor1: {v:.6f}V\n  Cursor2: {v2:.6f}V\n  ΔValue: {delta_v:.6f}V"
                else:
                    info += f"\n{channel_name}: {v:.6f}V @ {t:.6f}s"
        
        self.cursor_label.setText(info)
    
    def _export_data(self):
        """Export waveform data to CSV"""
        from PySide6.QtWidgets import QFileDialog
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Data", "",
            "CSV Files (*.csv);;NumPy Files (*.npy)"
        )
        
        if not filename:
            return
        
        if filename.endswith('.csv'):
            self._export_csv(filename)
        else:
            self._export_npy(filename)
    
    def _export_csv(self, filename: str):
        """Export data as CSV"""
        import csv
        
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Header
            header = ['Time']
            for channel_name in self.data.keys():
                header.append(channel_name)
            writer.writerow(header)
            
            # Data (assume all have same time axis)
            if self.data:
                first_channel = list(self.data.keys())[0]
                time = self.data[first_channel]["time"]
                
                for i, t in enumerate(time):
                    row = [t]
                    for channel_name in self.data.keys():
                        voltage = self.data[channel_name]["voltage"]
                        if i < len(voltage):
                            row.append(voltage[i])
                    writer.writerow(row)
    
    def _export_plot(self):
        """Export plot as image"""
        from PySide6.QtWidgets import QFileDialog
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Plot", "",
            "PNG Files (*.png);;SVG Files (*.svg);;PDF Files (*.pdf)"
        )
        
        if not filename:
            return
        
        try:
            if filename.endswith('.svg'):
                exporter = pg.exporters.SVGExporter(self.plot_widget.plotItem)
            elif filename.endswith('.pdf'):
                exporter = pg.exporters.PDFExporter(self.plot_widget.plotItem)
            else:
                exporter = pg.exporters.ImageExporter(self.plot_widget.plotItem)
            
            exporter.export(fileName=filename)
        except Exception as e:
            print(f"Export failed: {e}")
    
    def _export_npy(self, filename: str):
        """Export data as NumPy file"""
        export_dict = {}
        for channel_name, data in self.data.items():
            export_dict[channel_name] = data["voltage"]
        
        # Also store time
        if self.data:
            first_channel = list(self.data.keys())[0]
            export_dict['time'] = self.data[first_channel]["time"]
        
        np.save(filename, export_dict)
    
    def fit_view(self):
        """Fit all curves in view"""
        if self.curves:
            self.plot_widget.enableAutoRange()
