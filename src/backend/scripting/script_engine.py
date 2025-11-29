"""
Script Execution Engine - Manages script execution and output capture
Runs scripts in isolated threads for non-blocking execution
"""

from PySide6.QtCore import QThread, Signal
from typing import Dict, Any, Optional, Callable
import sys
import io
import traceback
import time


class ScriptExecutionThread(QThread):
    """Thread for executing scripts without blocking UI"""
    
    # Signals
    output_received = Signal(str)
    error_occurred = Signal(str)
    execution_started = Signal()
    execution_finished = Signal(bool)  # True if successful, False if error
    progress_update = Signal(int)  # Progress percentage (0-100)
    
    def __init__(self, script_code: str, context: Dict[str, Any]):
        super().__init__()
        self.script_code = script_code
        self.context = context
        self.is_running = False
        self.is_paused = False
        self.output_buffer = io.StringIO()
        self.error_buffer = io.StringIO()
        self.start_time = None
        self.execution_time = 0.0
    
    def run(self):
        """Execute script in separate thread"""
        self.is_running = True
        self.start_time = time.time()
        self.execution_started.emit()
        
        try:
            # Redirect stdout and stderr
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = self.output_buffer
            sys.stderr = self.error_buffer
            
            # Create execution context with helpful utilities
            exec_context = {
                **self.context,
                '__name__': '__main__',
                '__builtins__': __builtins__,
            }
            
            # Execute the script
            exec(self.script_code, exec_context)
            
            # Get output
            output = self.output_buffer.getvalue()
            if output:
                self.output_received.emit(output)
            
            # Restore stdout/stderr
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            
            self.execution_time = time.time() - self.start_time
            self.execution_finished.emit(True)
            
        except KeyboardInterrupt:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            self.error_occurred.emit("Script interrupted by user")
            self.execution_finished.emit(False)
            
        except Exception as e:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            
            # Capture error with traceback
            error_msg = f"Error: {str(e)}\n\n{traceback.format_exc()}"
            self.error_occurred.emit(error_msg)
            self.execution_finished.emit(False)
            
        finally:
            self.is_running = False
    
    def stop(self):
        """Stop script execution"""
        self.is_running = False
        # For graceful termination, script should check a stop flag
        # Forceful termination would require more complex threading
    
    def pause(self):
        """Pause script execution (if supported)"""
        self.is_paused = True
    
    def resume(self):
        """Resume script execution"""
        self.is_paused = False
    
    def get_execution_time(self) -> float:
        """Get time taken to execute script"""
        if self.execution_time > 0:
            return self.execution_time
        if self.start_time:
            return time.time() - self.start_time
        return 0.0


class ScriptDebugger:
    """Provides debugging utilities for scripts"""
    
    def __init__(self):
        self.breakpoints: Dict[int, bool] = {}
        self.watched_variables: Dict[str, Any] = {}
        self.call_stack = []
        self.local_scope = {}
        self.global_scope = {}
    
    def set_breakpoint(self, line_number: int, enabled: bool = True):
        """Set or remove a breakpoint"""
        if enabled:
            self.breakpoints[line_number] = True
        elif line_number in self.breakpoints:
            del self.breakpoints[line_number]
    
    def add_watch(self, variable_name: str):
        """Add variable to watch list"""
        self.watched_variables[variable_name] = None
    
    def remove_watch(self, variable_name: str):
        """Remove variable from watch list"""
        if variable_name in self.watched_variables:
            del self.watched_variables[variable_name]
    
    def get_variable_value(self, var_name: str) -> Optional[Any]:
        """Get current value of a watched variable"""
        return self.watched_variables.get(var_name)
    
    def get_call_stack(self) -> list:
        """Get current call stack"""
        return self.call_stack.copy()


class ScriptProfiler:
    """Profiles script execution for performance analysis"""
    
    def __init__(self):
        self.function_times: Dict[str, float] = {}
        self.function_calls: Dict[str, int] = {}
        self.line_times: Dict[int, float] = {}
    
    def record_function_call(self, function_name: str, execution_time: float):
        """Record a function call and its execution time"""
        if function_name not in self.function_times:
            self.function_times[function_name] = 0.0
            self.function_calls[function_name] = 0
        
        self.function_times[function_name] += execution_time
        self.function_calls[function_name] += 1
    
    def record_line_time(self, line_number: int, execution_time: float):
        """Record line execution time"""
        if line_number not in self.line_times:
            self.line_times[line_number] = 0.0
        self.line_times[line_number] += execution_time
    
    def get_slowest_functions(self, count: int = 5) -> list:
        """Get slowest executing functions"""
        sorted_funcs = sorted(
            self.function_times.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_funcs[:count]
    
    def get_profile_report(self) -> str:
        """Generate a profiling report"""
        report = "=== Script Profiling Report ===\n\n"
        report += "Function Times (Top 10):\n"
        
        for func_name, total_time in self.get_slowest_functions(10):
            calls = self.function_calls.get(func_name, 0)
            avg_time = total_time / calls if calls > 0 else 0
            report += f"  {func_name}: {total_time:.4f}s ({calls} calls, avg {avg_time:.6f}s/call)\n"
        
        return report


class VariableInspector:
    """Inspects and displays variable values and types"""
    
    @staticmethod
    def get_variable_info(value: Any) -> Dict[str, Any]:
        """Get detailed information about a variable"""
        return {
            'value': value,
            'type': type(value).__name__,
            'type_module': type(value).__module__,
            'repr': repr(value),
            'str': str(value),
            'size': sys.getsizeof(value),
        }
    
    @staticmethod
    def format_variable_for_display(var_name: str, value: Any) -> str:
        """Format variable for display in UI"""
        var_type = type(value).__name__
        
        if isinstance(value, (list, tuple)):
            return f"{var_name}: {var_type} ({len(value)} items) = {repr(value)[:100]}..."
        elif isinstance(value, dict):
            return f"{var_name}: {var_type} ({len(value)} keys) = {repr(value)[:100]}..."
        elif isinstance(value, str):
            return f"{var_name}: {var_type} = {repr(value)[:100]}..."
        elif isinstance(value, (int, float, bool)):
            return f"{var_name}: {var_type} = {value}"
        else:
            return f"{var_name}: {var_type} = {repr(value)[:100]}..."
