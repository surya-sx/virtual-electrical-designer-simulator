"""
Script Runtime - execute user Python scripts with circuit and simulation access
"""
import sys
from typing import Dict, Any, Optional, Callable, List
import types
import io


class ScriptCallback:
    """Callback registration for circuit events"""
    
    def __init__(self):
        self.callbacks: Dict[str, List[Callable]] = {
            "component_added": [],
            "component_removed": [],
            "component_changed": [],
            "wire_added": [],
            "simulation_started": [],
            "simulation_finished": [],
        }
    
    def register(self, event: str, callback: Callable) -> bool:
        """Register callback for event"""
        if event in self.callbacks:
            self.callbacks[event].append(callback)
            return True
        return False
    
    def trigger(self, event: str, *args, **kwargs):
        """Trigger all callbacks for event"""
        if event in self.callbacks:
            for callback in self.callbacks[event]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    print(f"Callback error: {e}")
    
    def clear(self, event: Optional[str] = None):
        """Clear callbacks"""
        if event:
            self.callbacks[event] = []
        else:
            for key in self.callbacks:
                self.callbacks[key] = []


class ScriptRuntime:
    """Runtime environment for user scripts with circuit integration"""
    
    def __init__(self):
        self.circuit_reference = None
        self.simulation_reference = None
        self.variables: Dict[str, Any] = {}  # User-defined variables
        self.callbacks = ScriptCallback()
        self.execution_log: str = ""
        self.globals_dict: Dict[str, Any] = self._create_globals()
        
    def _create_globals(self) -> Dict[str, Any]:
        """Create globals dictionary for script execution"""
        return {
            "__builtins__": __builtins__,
            "print": self._print,
            "circuit": self.circuit_reference,
            "simulation": self.simulation_reference,
            "on_event": self._on_event,
            "get_variable": self._get_variable,
            "set_variable": self._set_variable,
            "math": __import__("math"),
            "np": __import__("numpy"),
        }
        
    def _print(self, *args, **kwargs):
        """Custom print function that logs output"""
        message = " ".join(str(arg) for arg in args)
        self.execution_log += message + "\n"
        print(message)  # Also print to console
        
    def _on_event(self, event: str, callback: Callable) -> bool:
        """Register event callback from script"""
        return self.callbacks.register(event, callback)
    
    def _get_variable(self, name: str) -> Any:
        """Get variable from script context"""
        return self.variables.get(name)
    
    def _set_variable(self, name: str, value: Any):
        """Set variable in script context"""
        self.variables[name] = value
        
    def set_circuit_reference(self, circuit_obj: Any):
        """Set reference to circuit object"""
        self.circuit_reference = circuit_obj
        self.globals_dict["circuit"] = circuit_obj
        
    def set_simulation_reference(self, sim_obj: Any):
        """Set reference to simulation object"""
        self.simulation_reference = sim_obj
        self.globals_dict["simulation"] = sim_obj
        
    def execute_script(self, script_code: str) -> Dict[str, Any]:
        """Execute user script in controlled environment"""
        self.execution_log = ""
        output_capture = io.StringIO()
        old_stdout = sys.stdout
        
        try:
            # Create a new module for script execution
            script_module = types.ModuleType("user_script")
            script_module.__dict__.update(self.globals_dict)
            script_module.__dict__.update(self.variables)
            
            # Capture output
            sys.stdout = output_capture
            
            # Execute the script
            exec(script_code, script_module.__dict__)
            
            # Update variables from script
            self.variables.update({
                k: v for k, v in script_module.__dict__.items() 
                if not k.startswith("_") and k not in self.globals_dict
            })
            
            # Get captured output
            captured_output = output_capture.getvalue()
            self.execution_log += captured_output
            
            return {
                "status": "success",
                "output": self.execution_log,
                "error": None,
                "variables": self.variables.copy(),
            }
            
        except SyntaxError as e:
            error_msg = f"Syntax Error: {str(e)} at line {e.lineno}"
            self.execution_log += error_msg + "\n"
            return {
                "status": "error",
                "output": self.execution_log,
                "error": error_msg,
                "variables": self.variables.copy(),
            }
            
        except Exception as e:
            error_msg = f"Runtime Error: {str(e)}"
            self.execution_log += error_msg + "\n"
            return {
                "status": "error",
                "output": self.execution_log,
                "error": error_msg,
                "variables": self.variables.copy(),
            }
        
        finally:
            sys.stdout = old_stdout
            output_capture.close()
            
    def register_custom_component(self, name: str, component_class: type) -> bool:
        """Register a custom component model"""
        try:
            self.globals_dict[name] = component_class
            self.variables[name] = component_class
            return True
        except Exception as e:
            self.execution_log += f"Error registering custom component: {e}\n"
            return False
    
    def trigger_event(self, event: str, *args, **kwargs):
        """Trigger event callbacks"""
        self.callbacks.trigger(event, *args, **kwargs)
    
    def clear_variables(self):
        """Clear all user variables"""
        self.variables.clear()
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get summary of script execution"""
        return {
            "log": self.execution_log,
            "variables_count": len(self.variables),
            "variable_names": list(self.variables.keys()),
        }
