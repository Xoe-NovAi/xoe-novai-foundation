#!/usr/bin/env python3
"""
Project Orchestrator - Core coordination for AI development ecosystem
=====================================================================

Manages project creation, tracking, and coordination across the entire
AI development ecosystem. Provides a simple, effective foundation for
organizing and managing multiple concurrent projects.
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any


class BasicProjectOrchestrator:
    """
    Basic project management system for the AI development ecosystem.

    Provides essential project coordination without complex ML algorithms.
    Focuses on reliability, simplicity, and immediate usability.
    """

    def __init__(self, projects_root: str = None):
        """
        Initialize the project orchestrator.

        Args:
            projects_root: Root directory for all projects (auto-detects if None)
        """
        if projects_root is None:
            # Auto-detect: find projects directory relative to this file
            current_file = Path(__file__)
            self.projects_root = current_file.parent.parent  # Go up from _meta to projects
        else:
            self.projects_root = Path(projects_root)

        self.templates_root = self.projects_root / "_templates"
        self.meta_root = self.projects_root / "_meta"
        self.projects = {}

        # Ensure required directories exist
        self._ensure_directories()

        # Load existing projects
        self._load_existing_projects()

    def _ensure_directories(self):
        """Ensure all required directories exist."""
        directories = [
            self.projects_root,
            self.templates_root,
            self.meta_root,
            self.projects_root / "_standards"
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def _load_existing_projects(self):
        """Load information about existing projects."""
        if not self.projects_root.exists():
            return

        # Find all project directories (excluding _meta, _templates, _standards)
        for item in self.projects_root.iterdir():
            if item.is_dir() and not item.name.startswith('_'):
                project_info = self._load_project_info(item.name)
                if project_info:
                    self.projects[item.name] = project_info

    def _load_project_info(self, project_name: str) -> Optional[Dict[str, Any]]:
        """Load project information from its metadata file."""
        project_dir = self.projects_root / project_name
        metadata_file = project_dir / "metadata.json"

        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                # Create basic info if metadata is corrupted
                return self._create_basic_project_info(project_name)

        # Create basic info if no metadata exists
        return self._create_basic_project_info(project_name)

    def _create_basic_project_info(self, project_name: str) -> Dict[str, Any]:
        """Create basic project information."""
        project_dir = self.projects_root / project_name
        created_time = datetime.fromtimestamp(project_dir.stat().st_ctime)

        return {
            "name": project_name,
            "type": "unknown",
            "status": "active",
            "created": created_time.isoformat(),
            "last_modified": created_time.isoformat(),
            "description": f"Project: {project_name}",
            "path": str(project_dir)
        }

    def create_project(self, name: str, template_type: str = "research-project",
                      description: str = "") -> bool:
        """
        Create a new project from a template.

        Args:
            name: Project name (must be unique)
            template_type: Template to use (research-project, development-project, experimental-project)
            description: Optional project description

        Returns:
            True if project was created successfully, False otherwise
        """
        # Validate project name
        if not self._is_valid_project_name(name):
            print(f"❌ Invalid project name: {name}")
            return False

        # Check if project already exists
        if name in self.projects:
            print(f"❌ Project '{name}' already exists")
            return False

        # Check if template exists
        template_dir = self.templates_root / template_type
        if not template_dir.exists():
            print(f"❌ Template '{template_type}' not found")
            return False

        try:
            # Create project directory
            project_dir = self.projects_root / name
            project_dir.mkdir(parents=True, exist_ok=False)

            # Copy template files
            self._copy_template_files(template_dir, project_dir, name)

            # Create project metadata
            metadata = self._create_project_metadata(name, template_type, description)
            metadata_file = project_dir / "metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)

            # Update internal registry
            self.projects[name] = metadata

            print(f"✅ Project '{name}' created successfully from template '{template_type}'")
            return True

        except Exception as e:
            # Clean up on failure
            if project_dir.exists():
                shutil.rmtree(project_dir)
            print(f"❌ Failed to create project '{name}': {e}")
            return False

    def _is_valid_project_name(self, name: str) -> bool:
        """Validate project name."""
        if not name or len(name.strip()) == 0:
            return False

        # Check for invalid characters
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|', ' ', '\t', '\n']
        if any(char in name for char in invalid_chars):
            return False

        # Check length
        if len(name) > 50:
            return False

        # Check if it's a reserved name
        reserved_names = ['_meta', '_templates', '_standards']
        if name in reserved_names:
            return False

        return True

    def _copy_template_files(self, template_dir: Path, project_dir: Path, project_name: str):
        """Copy template files to project directory."""
        for item in template_dir.iterdir():
            if item.is_file():
                # Read template content
                with open(item, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Replace template variables
                content = content.replace("{{PROJECT_NAME}}", project_name)
                content = content.replace("{{CREATED_DATE}}", datetime.now().strftime("%Y-%m-%d"))

                # Write to project directory
                dest_file = project_dir / item.name
                with open(dest_file, 'w', encoding='utf-8') as f:
                    f.write(content)

    def _create_project_metadata(self, name: str, template_type: str,
                               description: str) -> Dict[str, Any]:
        """Create project metadata."""
        now = datetime.now()

        metadata = {
            "name": name,
            "type": template_type,
            "status": "active",
            "created": now.isoformat(),
            "last_modified": now.isoformat(),
            "description": description or f"Project: {name}",
            "path": str(self.projects_root / name),
            "template_used": template_type,
            "version": "1.0.0",
            "tags": [],
            "milestones": [],
            "dependencies": [],
            "evaluation_criteria": {
                "success_metrics": [],
                "completion_criteria": []
            }
        }

        return metadata

    def list_projects(self, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all projects, optionally filtered by status.

        Args:
            status_filter: Optional status to filter by ('active', 'completed', 'archived')

        Returns:
            List of project information dictionaries
        """
        projects = list(self.projects.values())

        if status_filter:
            projects = [p for p in projects if p.get('status') == status_filter]

        # Sort by creation date (newest first)
        projects.sort(key=lambda x: x.get('created', ''), reverse=True)

        return projects

    def get_project_status(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed status information for a project.

        Args:
            name: Project name

        Returns:
            Project status information or None if not found
        """
        if name not in self.projects:
            return None

        project_info = self.projects[name].copy()
        project_dir = Path(project_info['path'])

        # Add file system information
        if project_dir.exists():
            project_info['file_count'] = sum(1 for _ in project_dir.rglob('*') if _.is_file())
            project_info['directory_count'] = sum(1 for _ in project_dir.rglob('*') if _.is_dir())
            project_info['total_size'] = sum(f.stat().st_size for f in project_dir.rglob('*') if f.is_file())

            # Check for recent activity
            latest_modification = max(
                (f.stat().st_mtime for f in project_dir.rglob('*') if f.is_file()),
                default=project_info.get('last_modified_timestamp', 0)
            )
            project_info['last_activity'] = datetime.fromtimestamp(latest_modification).isoformat()

        return project_info

    def update_project_status(self, name: str, status: str, description: str = "") -> bool:
        """
        Update a project's status.

        Args:
            name: Project name
            status: New status ('active', 'completed', 'archived', 'on-hold')
            description: Optional status update description

        Returns:
            True if update was successful, False otherwise
        """
        if name not in self.projects:
            print(f"❌ Project '{name}' not found")
            return False

        # Update in-memory data
        self.projects[name]['status'] = status
        self.projects[name]['last_modified'] = datetime.now().isoformat()

        if description:
            self.projects[name]['description'] = description

        # Update metadata file
        try:
            metadata_file = Path(self.projects[name]['path']) / "metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(self.projects[name], f, indent=2)

            print(f"✅ Project '{name}' status updated to '{status}'")
            return True

        except Exception as e:
            print(f"❌ Failed to update project status: {e}")
            return False

    def get_system_overview(self) -> Dict[str, Any]:
        """
        Get an overview of the entire project system.

        Returns:
            System-wide statistics and information
        """
        total_projects = len(self.projects)
        active_projects = sum(1 for p in self.projects.values() if p.get('status') == 'active')
        completed_projects = sum(1 for p in self.projects.values() if p.get('status') == 'completed')

        # Get project types distribution
        project_types = {}
        for project in self.projects.values():
            ptype = project.get('type', 'unknown')
            project_types[ptype] = project_types.get(ptype, 0) + 1

        return {
            "total_projects": total_projects,
            "active_projects": active_projects,
            "completed_projects": completed_projects,
            "project_types": project_types,
            "system_health": "healthy" if total_projects > 0 else "empty",
            "last_updated": datetime.now().isoformat()
        }


# Convenience functions for external use
def create_project(name: str, template: str = "research-project", description: str = "") -> bool:
    """Convenience function to create a project."""
    orchestrator = BasicProjectOrchestrator()
    return orchestrator.create_project(name, template, description)


def list_projects(status: Optional[str] = None) -> List[Dict[str, Any]]:
    """Convenience function to list projects."""
    orchestrator = BasicProjectOrchestrator()
    return orchestrator.list_projects(status)


def get_project_status(name: str) -> Optional[Dict[str, Any]]:
    """Convenience function to get project status."""
    orchestrator = BasicProjectOrchestrator()
    return orchestrator.get_project_status(name)


if __name__ == "__main__":
    # Test the orchestrator
    orchestrator = BasicProjectOrchestrator()

    print("🧠 Project Orchestrator initialized")
    print(f"📊 System Overview: {orchestrator.get_system_overview()}")
    print(f"📋 Available Projects: {len(orchestrator.list_projects())}")