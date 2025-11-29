"""Test suite for simulation engine"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
import numpy as np
from backend.simulation.simulation_engine import SimulationEngine, SimulationConfig


class TestSimulationEngine:
    """Test simulation engine functionality"""
    
    def test_setup_dc_analysis(self):
        """Test DC analysis setup"""
        engine = SimulationEngine()
        config = engine.setup_dc_analysis()
        
        assert config.sim_type == "dc"
        assert engine.config == config
        
    def test_setup_ac_analysis(self):
        """Test AC analysis setup"""
        engine = SimulationEngine()
        config = engine.setup_ac_analysis(1, 1e6)
        
        assert config.sim_type == "ac"
        assert config.sweep_range == (1, 1e6)
        
    def test_setup_transient_analysis(self):
        """Test transient analysis setup"""
        engine = SimulationEngine()
        config = engine.setup_transient_analysis(1.0, 0.001)
        
        assert config.sim_type == "transient"
        assert config.duration == 1.0
        assert config.time_step == 0.001
        
    def test_run_without_config(self):
        """Test running without configuration"""
        engine = SimulationEngine()
        result = engine.run()
        
        assert result.status == "failed"
        assert "No simulation configuration set" in result.error_message
        
    def test_run_transient(self):
        """Test running transient simulation"""
        engine = SimulationEngine()
        engine.setup_transient_analysis(1.0, 0.01)
        result = engine.run()
        
        assert result.status == "success"
        assert len(result.time_points) > 0
        
    def test_callbacks(self):
        """Test callback mechanism"""
        engine = SimulationEngine()
        callback_called = False
        
        def callback(result):
            nonlocal callback_called
            callback_called = True
            
        engine.register_callback(callback)
        engine.setup_dc_analysis()
        engine.run()
        
        assert callback_called


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
