"""
Project Manager - manage project creation, loading, saving, and version history
"""
from pathlib import Path
from datetime import datetime
import json
from typing import Optional, List


class Project:
    """Represents a circuit design project"""
    
    def __init__(self, name: str, path: Optional[Path] = None):
        self.name = name
        self.path = path or Path.home() / ".ved" / "projects" / name
        self.created_at = datetime.now()
        self.modified_at = datetime.now()
        self.version = "0.1.0"
        self.circuits = {}
        self.metadata = {}
        
    def to_dict(self):
        """Convert project to dictionary"""
        return {
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "modified_at": self.modified_at.isoformat(),
            "version": self.version,
            "circuits": self.circuits,
            "metadata": self.metadata,
        }
        
    @classmethod
    def from_dict(cls, data: dict):
        """Create project from dictionary"""
        project = cls(data["name"])
        project.created_at = datetime.fromisoformat(data["created_at"])
        project.modified_at = datetime.fromisoformat(data["modified_at"])
        project.version = data["version"]
        project.circuits = data.get("circuits", {})
        project.metadata = data.get("metadata", {})
        return project


class ProjectManager:
    """Manages project lifecycle"""
    
    def __init__(self, projects_dir: Optional[Path] = None):
        self.projects_dir = projects_dir or Path.home() / ".ved" / "projects"
        self.projects_dir.mkdir(parents=True, exist_ok=True)
        self.current_project: Optional[Project] = None
        
    def create_project(self, name: str) -> Project:
        """Create a new project"""
        project = Project(name)
        project.path.mkdir(parents=True, exist_ok=True)
        self.current_project = project
        return project
        
    def load_project(self, path: Path) -> Project:
        """Load project from file"""
        project_file = path / f"{path.name}.vedproj"
        
        if not project_file.exists():
            raise FileNotFoundError(f"Project file not found: {project_file}")
            
        with open(project_file, 'r') as f:
            data = json.load(f)
            
        project = Project.from_dict(data)
        project.path = path
        self.current_project = project
        return project
        
    def save_project(self, project: Optional[Project] = None) -> bool:
        """Save project to file"""
        project = project or self.current_project
        
        if project is None:
            return False
            
        project.modified_at = datetime.now()
        project.path.mkdir(parents=True, exist_ok=True)
        project_file = project.path / f"{project.name}.vedproj"
        
        try:
            with open(project_file, 'w') as f:
                json.dump(project.to_dict(), f, indent=2, default=str)
            return True
        except (IOError, TypeError) as e:
            print(f"Error saving project: {e}")
            return False
        
    def save_circuit_to_file(self, circuit_data: dict, filename: Path) -> bool:
        """Save circuit to .vedcir file"""
        try:
            with open(filename, 'w') as f:
                json.dump(circuit_data, f, indent=2, default=str)
            return True
        except IOError as e:
            print(f"Error saving circuit: {e}")
            return False
    
    def load_circuit_from_file(self, filename: Path) -> Optional[dict]:
        """Load circuit from .vedcir file"""
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error loading circuit: {e}")
            return None
        
    def list_recent_projects(self, limit: int = 10) -> List[Path]:
        """List recent projects"""
        if not self.projects_dir.exists():
            return []
            
        projects = sorted(
            self.projects_dir.glob("*/"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        return projects[:limit]
