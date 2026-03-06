#!/usr/bin/env python3
"""
JupyterLab Integration with XNAi Foundation Vikunja Task Management

This module provides seamless integration between JupyterLab notebooks
and the XNAi Foundation's Vikunja-based task management system.

Features:
- Create research tasks from notebook cells
- Track task progress during notebook execution
- Complete tasks with detailed results
- Automatic model routing for research jobs
- Integration with the research queue system
"""

import os
import json
import requests
import logging
import yaml
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import asyncio
import aiohttp
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JobType(Enum):
    """Supported job types for research tasks."""
    ANALYSIS = "analysis"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"
    RESEARCH = "research"
    DOCUMENTATION = "documentation"


@dataclass
class TaskMetadata:
    """Metadata for research tasks."""
    notebook_path: str
    cell_id: Optional[str] = None
    execution_time: Optional[str] = None
    model_used: Optional[str] = None
    routing_info: Optional[Dict] = None


class VikunjaIntegration:
    """Integration with Vikunja task management system."""
    
    def __init__(self, vikunja_url: Optional[str] = None, api_token: Optional[str] = None):
        """
        Initialize Vikunja integration.
        
        Args:
            vikunja_url: URL of Vikunja API (defaults to environment variable)
            api_token: API token for authentication (defaults to environment variable)
        """
        self.vikunja_url = vikunja_url or os.getenv('VIKUNJA_URL', 'http://localhost:3456/api/v1')
        self.api_token = api_token or os.getenv('VIKUNJA_API_TOKEN', '')
        
        # Load model router configuration
        self.model_router_config = self._load_model_router_config()
        
        # Default project mapping
        self.project_mapping = {
            'Classical Studies': 1,
            'AI Research': 2,
            'Documentation': 3,
            'Development': 4
        }
        
        logger.info(f"Initialized Vikunja integration: {self.vikunja_url}")
    
    def _load_model_router_config(self) -> Dict:
        """Load model router configuration."""
        config_path = os.getenv('MODEL_ROUTER_CONFIG', 'configs/model-router.yaml')
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Model router config not found: {config_path}")
            return {}
        except yaml.YAMLError as e:
            logger.error(f"Error parsing model router config: {e}")
            return {}
    
    def _get_headers(self) -> Dict[str, str]:
        """Get authentication headers for Vikunja API."""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        if self.api_token:
            headers['Authorization'] = f'Bearer {self.api_token}'
        return headers
    
    def _select_model_for_job(self, job_type: JobType, content: str) -> Dict:
        """Select appropriate model based on job type and content."""
        # Default model selection logic
        model_selection = {
            'analysis': 'gpt-4o-mini',
            'translation': 'gpt-4o',
            'summarization': 'gpt-4o-mini',
            'research': 'gpt-4o',
            'documentation': 'gpt-4o-mini'
        }
        
        selected_model = model_selection.get(job_type.value, 'gpt-4o-mini')
        
        # Content-based model selection
        content_length = len(content)
        if content_length > 5000:
            selected_model = 'gpt-4o'  # Use larger model for long content
        
        # Check for classical studies content
        classical_keywords = ['greek', 'latin', 'ancient', 'classical', 'theology']
        if any(keyword in content.lower() for keyword in classical_keywords):
            selected_model = 'gpt-4o'  # Use more capable model for classical content
        
        return {
            'model': selected_model,
            'reasoning': f"Selected {selected_model} for {job_type.value} job",
            'content_length': content_length
        }
    
    def create_task_from_notebook(
        self,
        title: str,
        description: str,
        project: str,
        job_type: JobType,
        content: str,
        priority: int = 2,
        labels: Optional[List[str]] = None
    ) -> Optional[Dict]:
        """
        Create a research task from a Jupyter notebook cell.
        
        Args:
            title: Task title
            description: Task description
            project: Project name
            job_type: Type of research job
            content: Content to analyze/process
            priority: Task priority (1-5, where 5 is highest)
            labels: Optional list of labels
            
        Returns:
            Created task data or None if creation failed
        """
        try:
            # Select appropriate model
            model_info = self._select_model_for_job(job_type, content)
            
            # Prepare task data
            task_data = {
                'title': title,
                'description': description,
                'priority': priority,
                'project_id': self.project_mapping.get(project, 1),
                'labels': labels or ['research', 'jupyter'],
                'metadata': {
                    'job_type': job_type.value,
                    'model_routing': model_info,
                    'created_from': 'jupyter_notebook',
                    'timestamp': datetime.now().isoformat()
                }
            }
            
            # Create task in Vikunja
            response = requests.post(
                f"{self.vikunja_url}/tasks",
                headers=self._get_headers(),
                json=task_data
            )
            
            if response.status_code == 201:
                task = response.json()
                logger.info(f"Created task {task['id']}: {title}")
                
                # Add task to research queue
                self._add_to_research_queue(task, content)
                
                return task
            else:
                logger.error(f"Failed to create task: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return None
    
    def _add_to_research_queue(self, task: Dict, content: str):
        """Add task to the research queue for processing."""
        try:
            queue_data = {
                'task_id': task['id'],
                'content': content,
                'model': task['metadata']['model_routing']['model'],
                'job_type': task['metadata']['job_type'],
                'priority': task['priority']
            }
            
            # Add to research queue (this would integrate with the existing queue system)
            response = requests.post(
                f"{self.vikunja_url}/research-queue",
                headers=self._get_headers(),
                json=queue_data
            )
            
            if response.status_code == 201:
                logger.info(f"Added task {task['id']} to research queue")
            else:
                logger.warning(f"Failed to add task to research queue: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error adding to research queue: {e}")
    
    def update_task_progress(self, task_id: int, progress: int, notes: str = "") -> bool:
        """
        Update task progress.
        
        Args:
            task_id: ID of the task to update
            progress: Progress percentage (0-100)
            notes: Optional progress notes
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            update_data = {
                'progress': progress,
                'metadata': {
                    'last_updated': datetime.now().isoformat(),
                    'notes': notes
                }
            }
            
            response = requests.put(
                f"{self.vikunja_url}/tasks/{task_id}",
                headers=self._get_headers(),
                json=update_data
            )
            
            if response.status_code == 200:
                logger.info(f"Updated task {task_id} progress to {progress}%")
                return True
            else:
                logger.error(f"Failed to update task progress: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating task progress: {e}")
            return False
    
    def complete_research_task(self, task_id: int, completion_notes: str = "") -> bool:
        """
        Complete a research task.
        
        Args:
            task_id: ID of the task to complete
            completion_notes: Final completion notes
            
        Returns:
            True if completion successful, False otherwise
        """
        try:
            completion_data = {
                'status': 'completed',
                'completed_at': datetime.now().isoformat(),
                'metadata': {
                    'completion_notes': completion_notes,
                    'completed_from': 'jupyter_notebook'
                }
            }
            
            response = requests.put(
                f"{self.vikunja_url}/tasks/{task_id}",
                headers=self._get_headers(),
                json=completion_data
            )
            
            if response.status_code == 200:
                logger.info(f"Completed task {task_id}")
                return True
            else:
                logger.error(f"Failed to complete task: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error completing task: {e}")
            return False
    
    def get_tasks_from_notebook(self, notebook_path: str) -> List[Dict]:
        """
        Get all tasks associated with a notebook.
        
        Args:
            notebook_path: Path to the notebook file
            
        Returns:
            List of tasks associated with the notebook
        """
        try:
            # Query tasks by metadata
            params = {
                'metadata': json.dumps({
                    'notebook_path': notebook_path
                })
            }
            
            response = requests.get(
                f"{self.vikunja_url}/tasks",
                headers=self._get_headers(),
                params=params
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get tasks: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting tasks: {e}")
            return []
    
    def get_task_status(self, task_id: int) -> Optional[Dict]:
        """Get current status of a task."""
        try:
            response = requests.get(
                f"{self.vikunja_url}/tasks/{task_id}",
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get task status: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting task status: {e}")
            return None


# Global instance for easy access in notebooks
_research_environment = None


def init_research_environment() -> VikunjaIntegration:
    """
    Initialize the research environment for Jupyter notebooks.
    
    Returns:
        VikunjaIntegration instance
    """
    global _research_environment
    if _research_environment is None:
        _research_environment = VikunjaIntegration()
    return _research_environment


def create_task_from_notebook(
    title: str,
    description: str,
    project: str,
    job_type: JobType,
    content: str,
    priority: int = 2,
    labels: Optional[List[str]] = None
) -> Optional[Dict]:
    """
    Convenience function to create a task from a notebook.
    
    Args:
        title: Task title
        description: Task description
        project: Project name
        job_type: Type of research job
        content: Content to analyze/process
        priority: Task priority (1-5)
        labels: Optional list of labels
        
    Returns:
        Created task data or None if creation failed
    """
    env = init_research_environment()
    return env.create_task_from_notebook(
        title, description, project, job_type, content, priority, labels
    )


def get_tasks_from_notebook(notebook_path: str) -> List[Dict]:
    """
    Get all tasks associated with a notebook.
    
    Args:
        notebook_path: Path to the notebook file
        
    Returns:
        List of tasks associated with the notebook
    """
    env = init_research_environment()
    return env.get_tasks_from_notebook(notebook_path)


# Example usage and testing
if __name__ == "__main__":
    # Test the integration
    env = VikunjaIntegration()
    
    # Create a test task
    test_task = env.create_task_from_notebook(
        title="Test Research Task",
        description="This is a test task created from JupyterLab",
        project="Development",
        job_type=JobType.ANALYSIS,
        content="This is test content for the research task.",
        priority=3,
        labels=["test", "jupyter"]
    )
    
    if test_task:
        print(f"✅ Test task created: {test_task['id']}")
        
        # Update progress
        env.update_task_progress(test_task['id'], 50, "Halfway through analysis")
        
        # Complete task
        env.complete_research_task(test_task['id'], "Test task completed successfully")
    else:
        print("❌ Failed to create test task")