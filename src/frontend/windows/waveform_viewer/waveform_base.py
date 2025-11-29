"""
Base Waveform Module - Core functionality for waveform display and analysis
Organizes waveform-related features with clear separation of concerns
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QCheckBox, QSpinBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import numpy as np
from typing import List, Tuple, Optional, Dict, Any


class WaveformData:
    """Container for waveform data with metadata"""
    
    def __init__(self, name: str, x_data: np.ndarray, y_data: np.ndarray, 
                 unit_x: str = "s", unit_y: str = "V", color: str = "#0066cc"):
        """
        Initialize waveform data
        
        Args:
            name: Waveform name/label
            x_data: X-axis data (time)
            y_data: Y-axis data (voltage/current/etc)
            unit_x: X-axis unit
            unit_y: Y-axis unit
            color: Plot color (hex format)
        """
        self.name = name
        self.x_data = np.asarray(x_data)
        self.y_data = np.asarray(y_data)
        self.unit_x = unit_x
        self.unit_y = unit_y
        self.color = color
        self.visible = True
        
        # Compute statistics
        self._stats = None
    
    @property
    def x_label(self) -> str:
        """Get formatted X-axis label"""
        return f"Time ({self.unit_x})"
    
    @property
    def y_label(self) -> str:
        """Get formatted Y-axis label"""
        return f"{self.name} ({self.unit_y})"
    
    @property
    def stats(self) -> Dict[str, float]:
        """Get waveform statistics"""
        if self._stats is None:
            self._stats = {
                'min': float(np.min(self.y_data)),
                'max': float(np.max(self.y_data)),
                'mean': float(np.mean(self.y_data)),
                'rms': float(np.sqrt(np.mean(self.y_data ** 2))),
                'peak_peak': float(np.max(self.y_data) - np.min(self.y_data)),
                'std': float(np.std(self.y_data)),
            }
        return self._stats
    
    def get_value_at(self, x: float) -> Optional[float]:
        """Get Y value at specific X position (interpolated)"""
        try:
            idx = np.searchsorted(self.x_data, x)
            if idx == 0:
                return float(self.y_data[0])
            elif idx >= len(self.y_data):
                return float(self.y_data[-1])
            else:
                # Linear interpolation
                x0, x1 = self.x_data[idx-1], self.x_data[idx]
                y0, y1 = self.y_data[idx-1], self.y_data[idx]
                return float(y0 + (x - x0) * (y1 - y0) / (x1 - x0))
        except:
            return None
    
    def get_range(self) -> Tuple[float, float, float, float]:
        """Get waveform range as (x_min, x_max, y_min, y_max)"""
        return (
            float(np.min(self.x_data)),
            float(np.max(self.x_data)),
            float(np.min(self.y_data)),
            float(np.max(self.y_data))
        )


class WaveformPlotter:
    """Base plotter interface for different plotting backends"""
    
    def __init__(self):
        self.waveforms: List[WaveformData] = []
        self.grid_enabled = True
        self.legend_enabled = True
        self.cursor_visible = False
        self.zoom_enabled = True
    
    def add_waveform(self, waveform: WaveformData):
        """Add waveform to plot"""
        self.waveforms.append(waveform)
    
    def remove_waveform(self, waveform_name: str):
        """Remove waveform by name"""
        self.waveforms = [w for w in self.waveforms if w.name != waveform_name]
    
    def clear_waveforms(self):
        """Clear all waveforms"""
        self.waveforms.clear()
    
    def update_plot(self):
        """Update plot display (to be implemented by subclasses)"""
        raise NotImplementedError
    
    def set_x_range(self, x_min: float, x_max: float):
        """Set X-axis range"""
        raise NotImplementedError
    
    def set_y_range(self, y_min: float, y_max: float):
        """Set Y-axis range"""
        raise NotImplementedError
    
    def auto_scale(self):
        """Auto-scale plot to fit all waveforms"""
        if not self.waveforms:
            return
        
        x_min, x_max = float('inf'), float('-inf')
        y_min, y_max = float('inf'), float('-inf')
        
        for waveform in self.waveforms:
            if waveform.visible:
                w_x_min, w_x_max, w_y_min, w_y_max = waveform.get_range()
                x_min = min(x_min, w_x_min)
                x_max = max(x_max, w_x_max)
                y_min = min(y_min, w_y_min)
                y_max = max(y_max, w_y_max)
        
        # Add 10% margin
        x_margin = (x_max - x_min) * 0.1 if x_max > x_min else 0.1
        y_margin = (y_max - y_min) * 0.1 if y_max > y_min else 0.1
        
        self.set_x_range(x_min - x_margin, x_max + x_margin)
        self.set_y_range(y_min - y_margin, y_max + y_margin)


class WaveformAnalyzer:
    """Analyze waveforms for features, peaks, crossings, etc."""
    
    @staticmethod
    def find_peaks(waveform: WaveformData, min_distance: int = 10) -> List[Tuple[float, float]]:
        """Find peaks in waveform
        
        Returns:
            List of (x, y) tuples for peaks
        """
        from scipy import signal
        
        peaks, _ = signal.find_peaks(waveform.y_data, distance=min_distance)
        return [(float(waveform.x_data[p]), float(waveform.y_data[p])) for p in peaks]
    
    @staticmethod
    def find_troughs(waveform: WaveformData, min_distance: int = 10) -> List[Tuple[float, float]]:
        """Find troughs (valleys) in waveform
        
        Returns:
            List of (x, y) tuples for troughs
        """
        from scipy import signal
        
        troughs, _ = signal.find_peaks(-waveform.y_data, distance=min_distance)
        return [(float(waveform.x_data[t]), float(waveform.y_data[t])) for t in troughs]
    
    @staticmethod
    def find_zero_crossings(waveform: WaveformData) -> List[float]:
        """Find zero crossing points
        
        Returns:
            List of x positions where waveform crosses zero
        """
        crossings = []
        for i in range(len(waveform.y_data) - 1):
            if waveform.y_data[i] * waveform.y_data[i+1] < 0:
                # Linear interpolation to find exact crossing
                x0, x1 = waveform.x_data[i], waveform.x_data[i+1]
                y0, y1 = waveform.y_data[i], waveform.y_data[i+1]
                x_cross = x0 - y0 * (x1 - x0) / (y1 - y0)
                crossings.append(float(x_cross))
        
        return crossings
    
    @staticmethod
    def compute_frequency(waveform: WaveformData) -> Optional[float]:
        """Estimate dominant frequency using FFT
        
        Returns:
            Dominant frequency or None
        """
        try:
            from scipy import fft
            
            # Compute FFT
            y_fft = fft.fft(waveform.y_data)
            freqs = fft.fftfreq(len(waveform.y_data), waveform.x_data[1] - waveform.x_data[0])
            
            # Find dominant frequency (positive frequencies only)
            positive_freqs = freqs[:len(freqs)//2]
            power = np.abs(y_fft[:len(y_fft)//2])
            
            # Skip DC component
            dom_freq_idx = np.argmax(power[1:]) + 1
            return float(positive_freqs[dom_freq_idx])
        except:
            return None
    
    @staticmethod
    def compute_harmonics(waveform: WaveformData, num_harmonics: int = 5) -> Dict[int, float]:
        """Compute harmonic content
        
        Returns:
            Dict mapping harmonic number to amplitude
        """
        try:
            from scipy import fft
            
            # Compute FFT
            y_fft = fft.fft(waveform.y_data)
            freqs = fft.fftfreq(len(waveform.y_data), waveform.x_data[1] - waveform.x_data[0])
            
            # Find fundamental frequency
            positive_freqs = freqs[:len(freqs)//2]
            power = np.abs(y_fft[:len(y_fft)//2])
            
            fundamental_idx = np.argmax(power[1:]) + 1
            fundamental_freq = positive_freqs[fundamental_idx]
            
            if fundamental_freq == 0:
                return {}
            
            # Compute harmonics
            harmonics = {}
            for n in range(1, num_harmonics + 1):
                target_freq = n * fundamental_freq
                closest_idx = np.argmin(np.abs(positive_freqs - target_freq))
                harmonics[n] = float(power[closest_idx])
            
            return harmonics
        except:
            return {}
    
    @staticmethod
    def compute_thd(waveform: WaveformData) -> Optional[float]:
        """Compute Total Harmonic Distortion
        
        Returns:
            THD percentage or None
        """
        harmonics = WaveformAnalyzer.compute_harmonics(waveform, num_harmonics=10)
        
        if len(harmonics) < 2:
            return None
        
        # THD = sqrt(sum of squares of harmonics 2-N) / fundamental
        fundamental = harmonics.get(1, 0)
        if fundamental == 0:
            return None
        
        harmonic_power = sum(harmonics[n]**2 for n in range(2, len(harmonics) + 1))
        thd = (np.sqrt(harmonic_power) / fundamental) * 100
        
        return float(thd)


class WaveformProcessor:
    """Process and transform waveforms"""
    
    @staticmethod
    def resample(waveform: WaveformData, num_points: int) -> WaveformData:
        """Resample waveform to different number of points"""
        x_new = np.linspace(waveform.x_data[0], waveform.x_data[-1], num_points)
        y_new = np.interp(x_new, waveform.x_data, waveform.y_data)
        
        new_waveform = WaveformData(
            waveform.name,
            x_new, y_new,
            waveform.unit_x, waveform.unit_y,
            waveform.color
        )
        return new_waveform
    
    @staticmethod
    def smooth(waveform: WaveformData, window_size: int = 5) -> WaveformData:
        """Apply smoothing filter to waveform"""
        from scipy import signal
        
        # Apply Savitzky-Golay filter
        window_size = min(window_size, len(waveform.y_data))
        if window_size % 2 == 0:
            window_size -= 1  # Must be odd
        
        if window_size < 3:
            window_size = 3
        
        y_smooth = signal.savgol_filter(waveform.y_data, window_size, 2)
        
        new_waveform = WaveformData(
            f"{waveform.name} (smooth)",
            waveform.x_data, y_smooth,
            waveform.unit_x, waveform.unit_y,
            waveform.color
        )
        return new_waveform
    
    @staticmethod
    def scale(waveform: WaveformData, scale_factor: float) -> WaveformData:
        """Scale waveform amplitude"""
        y_scaled = waveform.y_data * scale_factor
        
        new_waveform = WaveformData(
            waveform.name,
            waveform.x_data, y_scaled,
            waveform.unit_x, waveform.unit_y,
            waveform.color
        )
        return new_waveform
    
    @staticmethod
    def shift(waveform: WaveformData, shift_value: float) -> WaveformData:
        """Shift waveform vertically"""
        y_shifted = waveform.y_data + shift_value
        
        new_waveform = WaveformData(
            waveform.name,
            waveform.x_data, y_shifted,
            waveform.unit_x, waveform.unit_y,
            waveform.color
        )
        return new_waveform
