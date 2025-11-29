"""
Command Manager - implements undo/redo pattern for circuit operations
"""
from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum


class CommandType(Enum):
    """Types of commands that can be undone/redone"""
    ADD_COMPONENT = "add_component"
    DELETE_COMPONENT = "delete_component"
    MOVE_COMPONENT = "move_component"
    ADD_WIRE = "add_wire"
    DELETE_WIRE = "delete_wire"
    EDIT_PROPERTY = "edit_property"
    DUPLICATE_COMPONENT = "duplicate_component"
    ROTATE_COMPONENT = "rotate_component"
    GROUP_COMPONENTS = "group_components"
    UNGROUP_COMPONENTS = "ungroup_components"


@dataclass
class Command:
    """Base command class for undo/redo"""
    cmd_type: CommandType
    data: Dict[str, Any]
    
    def execute(self):
        """Execute the command"""
        pass
    
    def undo(self):
        """Undo the command"""
        pass
    
    def redo(self):
        """Redo the command"""
        self.execute()


class CommandManager:
    """Manages undo/redo stack"""
    
    def __init__(self, max_undo_stack: int = 100):
        self.undo_stack: List[Command] = []
        self.redo_stack: List[Command] = []
        self.max_undo_stack = max_undo_stack
        self.is_recording = True
    
    def execute_command(self, command: Command) -> bool:
        """Execute a command and add to undo stack"""
        if not self.is_recording:
            return False
        
        try:
            command.execute()
            self.undo_stack.append(command)
            
            # Limit undo stack size
            if len(self.undo_stack) > self.max_undo_stack:
                self.undo_stack.pop(0)
            
            # Clear redo stack when new command executed
            self.redo_stack.clear()
            return True
        except Exception as e:
            print(f"Command execution failed: {e}")
            return False
    
    def undo(self) -> bool:
        """Undo last command"""
        if not self.undo_stack:
            return False
        
        try:
            command = self.undo_stack.pop()
            command.undo()
            self.redo_stack.append(command)
            return True
        except Exception as e:
            print(f"Undo failed: {e}")
            self.undo_stack.append(command)  # Restore on error
            return False
    
    def redo(self) -> bool:
        """Redo last undone command"""
        if not self.redo_stack:
            return False
        
        try:
            command = self.redo_stack.pop()
            command.redo()
            self.undo_stack.append(command)
            return True
        except Exception as e:
            print(f"Redo failed: {e}")
            self.redo_stack.append(command)  # Restore on error
            return False
    
    def can_undo(self) -> bool:
        """Check if undo is available"""
        return len(self.undo_stack) > 0
    
    def can_redo(self) -> bool:
        """Check if redo is available"""
        return len(self.redo_stack) > 0
    
    def clear_history(self):
        """Clear undo/redo stacks"""
        self.undo_stack.clear()
        self.redo_stack.clear()
    
    def get_undo_description(self) -> str:
        """Get description of what will be undone"""
        if self.undo_stack:
            return f"Undo: {self.undo_stack[-1].cmd_type.value}"
        return "Undo"
    
    def get_redo_description(self) -> str:
        """Get description of what will be redone"""
        if self.redo_stack:
            return f"Redo: {self.redo_stack[-1].cmd_type.value}"
        return "Redo"
