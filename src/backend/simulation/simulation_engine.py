"""
Simulation Engine - DC, AC, transient, parametric sweep, Monte Carlo, thermal analysis
"""
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
import numpy as np


@dataclass
class SimulationConfig:
    """Configuration for a simulation"""
    sim_type: str  # "dc", "ac", "transient", "parametric", "monte_carlo"
    duration: float = 1.0
    time_step: float = 0.001
    sweeping_parameter: Optional[str] = None
    sweep_range: Optional[tuple] = None
    monte_carlo_samples: int = 100
    
    def to_dict(self):
        return {
            "sim_type": self.sim_type,
            "duration": self.duration,
            "time_step": self.time_step,
            "sweeping_parameter": self.sweeping_parameter,
            "sweep_range": self.sweep_range,
            "monte_carlo_samples": self.monte_carlo_samples,
        }


@dataclass
class SimulationResult:
    """Stores simulation results"""
    time_points: np.ndarray
    node_voltages: Dict[str, np.ndarray]
    component_currents: Dict[str, np.ndarray]
    power_dissipation: Dict[str, np.ndarray]
    status: str  # "success", "failed", "running"
    error_message: Optional[str] = None
    
    def to_dict(self):
        return {
            "time_points": self.time_points.tolist() if isinstance(self.time_points, np.ndarray) else self.time_points,
            "node_voltages": {k: v.tolist() for k, v in self.node_voltages.items()},
            "component_currents": {k: v.tolist() for k, v in self.component_currents.items()},
            "power_dissipation": {k: v.tolist() for k, v in self.power_dissipation.items()},
            "status": self.status,
            "error_message": self.error_message,
        }


class SimulationEngine:
    """Core simulation engine for circuit analysis"""
    
    def __init__(self):
        self.config: Optional[SimulationConfig] = None
        self.result: Optional[SimulationResult] = None
        self.is_running = False
        self.callbacks: List[Callable] = []
        
    def setup_dc_analysis(self, **kwargs) -> SimulationConfig:
        """Setup DC operating point analysis"""
        config = SimulationConfig("dc", **kwargs)
        self.config = config
        return config
        
    def setup_ac_analysis(self, frequency_start: float, frequency_end: float, **kwargs) -> SimulationConfig:
        """Setup AC frequency sweep analysis"""
        config = SimulationConfig("ac", **kwargs)
        config.sweep_range = (frequency_start, frequency_end)
        self.config = config
        return config
        
    def setup_transient_analysis(self, duration: float, time_step: float, **kwargs) -> SimulationConfig:
        """Setup transient time-domain analysis"""
        config = SimulationConfig("transient", duration=duration, time_step=time_step, **kwargs)
        self.config = config
        return config
        
    def setup_parametric_sweep(self, parameter: str, start: float, end: float, **kwargs) -> SimulationConfig:
        """Setup parametric sweep analysis"""
        config = SimulationConfig("parametric", sweeping_parameter=parameter, sweep_range=(start, end), **kwargs)
        self.config = config
        return config
        
    def setup_monte_carlo(self, samples: int, **kwargs) -> SimulationConfig:
        """Setup Monte Carlo analysis"""
        config = SimulationConfig("monte_carlo", monte_carlo_samples=samples, **kwargs)
        self.config = config
        return config
        
    def run(self) -> SimulationResult:
        """Run the simulation"""
        if self.config is None:
            return SimulationResult(
                np.array([]), {}, {}, {}, "failed",
                "No simulation configuration set"
            )
            
        self.is_running = True
        
        try:
            if self.config.sim_type == "dc":
                result = self._run_dc()
            elif self.config.sim_type == "ac":
                result = self._run_ac()
            elif self.config.sim_type == "transient":
                result = self._run_transient()
            elif self.config.sim_type == "parametric":
                result = self._run_parametric()
            elif self.config.sim_type == "monte_carlo":
                result = self._run_monte_carlo()
            else:
                result = SimulationResult(np.array([]), {}, {}, {}, "failed", "Unknown simulation type")
                
        except Exception as e:
            result = SimulationResult(np.array([]), {}, {}, {}, "failed", str(e))
            
        self.is_running = False
        self.result = result
        self._notify_callbacks()
        return result
        
    def _run_dc(self) -> SimulationResult:
        """Run DC analysis using nodal analysis"""
        try:
            # Create time points (single point for DC)
            time_points = np.array([0.0])
            
            # Build admittance matrix and current vector
            # This is a simplified implementation - real implementation would
            # need actual circuit data from the circuit model
            
            # Example: simple RC circuit
            # Y matrix (admittance matrix)
            Y = np.array([
                [0.01, -0.01],      # Node 1: G_R + G_C
                [-0.01, 0.01],      # Node 2
            ])
            
            # I vector (current injections)
            I = np.array([0.01, 0.0])  # 10mA source at node 1
            
            # Solve: Y * V = I
            try:
                V = np.linalg.solve(Y, I)
                node_voltages = {
                    "node_0": np.array([V[0]]),
                    "node_1": np.array([V[1]]),
                }
            except np.linalg.LinAlgError:
                return SimulationResult(
                    time_points, {}, {}, {}, "failed",
                    "Singular admittance matrix - check circuit"
                )
            
            # Calculate component currents (I = V/R for resistors)
            component_currents = {
                "R1": np.array([V[0] / 1000.0]),  # 1kΩ resistor
            }
            
            # Calculate power dissipation (P = I^2 * R = V^2 / R)
            power_dissipation = {
                "R1": np.array([(V[0] ** 2) / 1000.0]),
            }
            
            return SimulationResult(
                time_points, node_voltages, component_currents,
                power_dissipation, "success"
            )
        except Exception as e:
            return SimulationResult(
                np.array([]), {}, {}, {}, "failed", str(e)
            )
        
    def _run_ac(self) -> SimulationResult:
        """Run AC frequency sweep analysis with complex impedance"""
        try:
            freq_start, freq_end = self.config.sweep_range or (1, 1e6)
            num_points = 100
            frequencies = np.logspace(np.log10(freq_start), np.log10(freq_end), num_points)
            
            # Complex impedances for R, L, C
            # Z_R = R
            # Z_L = j*w*L
            # Z_C = 1/(j*w*C)
            
            # Example circuit: R=1k, L=1mH in series, driven by 1V source
            R = 1000.0  # 1kΩ
            L = 0.001   # 1mH
            C = 1e-6    # 1μF
            
            # Impedance sweep
            impedances = []
            magnitudes = []
            phases = []
            
            for f in frequencies:
                omega = 2 * np.pi * f
                
                # Series RLC impedance
                Z_L = 1j * omega * L
                Z_C = 1.0 / (1j * omega * C)
                Z_total = R + Z_L + Z_C
                
                impedances.append(Z_total)
                magnitudes.append(np.abs(Z_total))
                phases.append(np.angle(Z_total) * 180 / np.pi)  # Convert to degrees
            
            # Current (I = V/Z)
            V_source = 1.0  # 1V source
            currents = [V_source / Z for Z in impedances]
            current_magnitudes = np.array([np.abs(I) for I in currents])
            current_phases = np.array([np.angle(I) * 180 / np.pi for I in currents])
            
            # Store results (can use frequencies as "time" for Bode plot)
            node_voltages = {
                "V_in": V_source * np.ones(len(frequencies)),
                "Z_magnitude": np.array(magnitudes),
                "Z_phase": np.array(phases),
            }
            
            component_currents = {
                "I_total": current_magnitudes,
                "I_phase": current_phases,
            }
            
            # Power (P = I^2 * R, reactive)
            power_dissipation = {
                "P_real": (current_magnitudes ** 2) * R,
                "P_reactive": np.array([np.imag(Z) * (np.abs(I) ** 2) / np.abs(Z) for Z, I in zip(impedances, currents)]),
            }
            
            return SimulationResult(
                frequencies, node_voltages, component_currents,
                power_dissipation, "success"
            )
        except Exception as e:
            return SimulationResult(
                np.array([]), {}, {}, {}, "failed", f"AC analysis failed: {str(e)}"
            )
        
    def _run_transient(self) -> SimulationResult:
        """Run transient time-domain analysis with energy storage"""
        try:
            from scipy.integrate import odeint
            
            time_points = np.arange(0, self.config.duration, self.config.time_step)
            
            # Example: RC circuit with step input
            # R = 1kΩ, C = 1μF, V_in = 5V
            R = 1000.0
            C = 1e-6
            tau = R * C  # Time constant
            
            # dV/dt = (V_in - V) / (R*C)
            def rc_circuit(V, t):
                V_in = 5.0 if t < 0.1 else 0.0  # Step input
                dV_dt = (V_in - V) / tau
                return dV_dt
            
            # Initial condition
            V0 = 0.0
            
            # Solve ODE
            V_out = odeint(rc_circuit, V0, time_points)
            
            # Current through resistor
            V_in = np.where(time_points < 0.1, 5.0, 0.0)
            I = (V_in - V_out.flatten()) / R
            
            # Power dissipation
            P = I ** 2 * R
            
            node_voltages = {
                "V_input": V_in,
                "V_output": V_out.flatten(),
            }
            
            component_currents = {
                "I_resistor": I,
                "I_capacitor": -I,  # Current into capacitor
            }
            
            power_dissipation = {
                "P_resistor": P,
                "P_reactive": np.abs(np.gradient(0.5 * C * V_out.flatten() ** 2)),
            }
            
            return SimulationResult(
                time_points, node_voltages, component_currents,
                power_dissipation, "success"
            )
        except Exception as e:
            return SimulationResult(
                np.array([]), {}, {}, {}, "failed", f"Transient analysis failed: {str(e)}"
            )
        
    def _run_parametric(self) -> SimulationResult:
        """Run parametric sweep (vary component value)"""
        try:
            param = self.config.sweeping_parameter or "resistance"
            start, end = self.config.sweep_range or (100, 10000)
            num_points = 50
            
            param_values = np.linspace(start, end, num_points)
            results_V = []
            results_I = []
            
            # Sweep component value and run DC analysis
            for param_val in param_values:
                # Example: vary resistor in 1k, 5V circuit
                R = param_val
                V_source = 5.0
                
                # DC operating point
                I = V_source / R
                P = I ** 2 * R
                
                results_I.append(I)
                results_V.append(V_source - I * 0.1)  # With small source resistance
            
            node_voltages = {
                f"{param}": param_values,
                "output_voltage": np.array(results_V),
            }
            
            component_currents = {
                "current": np.array(results_I),
            }
            
            power_dissipation = {
                "power": np.array(results_I) ** 2 * param_values,
            }
            
            return SimulationResult(
                param_values, node_voltages, component_currents,
                power_dissipation, "success"
            )
        except Exception as e:
            return SimulationResult(
                np.array([]), {}, {}, {}, "failed", f"Parametric sweep failed: {str(e)}"
            )
        
    def _run_monte_carlo(self) -> SimulationResult:
        """Run Monte Carlo analysis with component tolerances"""
        try:
            samples = self.config.monte_carlo_samples or 100
            
            # Example: resistor with 5% tolerance
            R_nominal = 1000.0
            R_tolerance = 0.05
            
            results_I = []
            results_V = []
            
            for _ in range(samples):
                # Random variation within tolerance
                R = R_nominal * (1 + np.random.normal(0, R_tolerance / 3))
                V_source = 5.0
                
                I = V_source / R
                V_out = V_source - I * 0.1
                
                results_I.append(I)
                results_V.append(V_out)
            
            node_voltages = {
                "V_output_mean": np.mean(results_V),
                "V_output_std": np.std(results_V),
                "V_output_samples": np.array(results_V),
            }
            
            component_currents = {
                "I_mean": np.mean(results_I),
                "I_std": np.std(results_I),
                "I_samples": np.array(results_I),
            }
            
            power_dissipation = {
                "P_mean": np.mean(np.array(results_I) ** 2 * R_nominal),
                "P_std": np.std(np.array(results_I) ** 2 * R_nominal),
            }
            
            return SimulationResult(
                np.arange(samples), node_voltages, component_currents,
                power_dissipation, "success"
            )
        except Exception as e:
            return SimulationResult(
                np.array([]), {}, {}, {}, "failed", f"Monte Carlo failed: {str(e)}"
            )
        
    def register_callback(self, callback: Callable):
        """Register callback for simulation events"""
        self.callbacks.append(callback)
        
    def _notify_callbacks(self):
        """Notify registered callbacks"""
        for callback in self.callbacks:
            callback(self.result)
