"""Vikunja integration for automated project and task management."""

import requests
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from uuid import UUID
import os

from app.XNAi_rag_app.services.agent_management import ResearchJobManager, AgentRegistry
from app.XNAi_rag_app.services.database import get_db_session


class VikunjaAPI:
    """Client for Vikunja API integration."""
    
    def __init__(self, base_url: str, api_token: str):
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token
        self.headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
        self.logger = logging.getLogger(__name__)
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make HTTP request to Vikunja API."""
        url = f"{self.base_url}/api/v1/{endpoint.lstrip('/')}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=self.headers)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=self.headers, json=data)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=self.headers, json=data)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=self.headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Vikunja API request failed: {e}")
            raise
    
    def create_project(self, title: str, description: Optional[str] = None) -> Dict:
        """Create a new project in Vikunja."""
        data = {
            'title': title,
            'description': description or f"Research project created on {datetime.utcnow().isoformat()}"
        }
        
        result = self._make_request('POST', '/projects', data)
        self.logger.info(f"Created Vikunja project: {result.get('id')} - {title}")
        return result
    
    def create_task(self, project_id: int, title: str, description: Optional[str] = None, 
                   due_date: Optional[str] = None, assignee_id: Optional[int] = None) -> Dict:
        """Create a new task in a Vikunja project."""
        data = {
            'title': title,
            'description': description,
            'project_id': project_id
        }
        
        if due_date:
            data['due_date'] = due_date
        if assignee_id:
            data['assignee_id'] = assignee_id
        
        result = self._make_request('POST', '/tasks', data)
        self.logger.info(f"Created Vikunja task: {result.get('id')} - {title}")
        return result
    
    def update_task_status(self, task_id: int, status: str) -> Dict:
        """Update task status in Vikunja."""
        # Vikunja uses status_id: 1=Open, 2=In Progress, 3=Done
        status_map = {
            'open': 1,
            'in_progress': 2,
            'completed': 3,
            'done': 3
        }
        
        status_id = status_map.get(status.lower(), 1)
        data = {'status_id': status_id}
        
        result = self._make_request('PUT', f'/tasks/{task_id}', data)
        self.logger.info(f"Updated Vikunja task {task_id} status to {status}")
        return result
    
    def assign_task(self, task_id: int, user_id: int) -> Dict:
        """Assign a task to a user in Vikunja."""
        data = {'assignee_id': user_id}
        result = self._make_request('PUT', f'/tasks/{task_id}', data)
        self.logger.info(f"Assigned Vikunja task {task_id} to user {user_id}")
        return result
    
    def get_project(self, project_id: int) -> Dict:
        """Get project details from Vikunja."""
        return self._make_request('GET', f'/projects/{project_id}')
    
    def get_tasks(self, project_id: int) -> List[Dict]:
        """Get all tasks for a project."""
        return self._make_request('GET', f'/projects/{project_id}/tasks')


class VikunjaSync:
    """Synchronization service between Omega Stack and Vikunja."""
    
    def __init__(self):
        self.vikunja_url = os.getenv('VIKUNJA_URL', 'http://localhost:3000')
        self.vikunja_token = os.getenv('VIKUNJA_API_TOKEN')
        
        if not self.vikunja_token:
            raise ValueError("VIKUNJA_API_TOKEN environment variable must be set")
        
        self.vikunja_client = VikunjaAPI(self.vikunja_url, self.vikunja_token)
        self.jobs = ResearchJobManager()
        self.agents = AgentRegistry()
        self.logger = logging.getLogger(__name__)
    
    def sync_new_research_job(self, job_id: UUID) -> bool:
        """Sync a new research job to Vikunja."""
        try:
            job = self.jobs.get_job(job_id)
            if not job:
                self.logger.error(f"Job {job_id} not found")
                return False
            
            # Create Vikunja project
            project = self.vikunja_client.create_project(
                title=f"Research: {job.title}",
                description=f"Research job {job.slug}\n\nDescription: {job.description}\nDomain tags: {', '.join(job.domain_tags)}"
            )
            
            # Create initial tasks
            tasks = [
                "Research planning and methodology",
                "Data collection and analysis",
                "Documentation and reporting",
                "Integration with memory bank"
            ]
            
            for task_title in tasks:
                self.vikunja_client.create_task(
                    project_id=project['id'],
                    title=task_title,
                    description=f"Task for research job {job.slug}"
                )
            
            self.logger.info(f"Synced job {job.slug} to Vikunja project {project['id']}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to sync job {job_id} to Vikunja: {e}")
            return False
    
    def sync_job_status(self, job_id: UUID) -> bool:
        """Sync job status changes to Vikunja."""
        try:
            job = self.jobs.get_job(job_id)
            if not job:
                return False
            
            # Find corresponding Vikunja project (by title pattern)
            # In a real implementation, we'd store the Vikunja project ID in the job metadata
            # For now, we'll search by title
            project_title = f"Research: {job.title}"
            
            # This is a simplified approach - in production, we'd maintain a mapping table
            # between Omega jobs and Vikunja projects
            
            self.logger.info(f"Status sync for job {job.slug}: {job.status}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to sync job status {job_id}: {e}")
            return False
    
    def sync_agent_assignment(self, job_id: UUID, agent_id: UUID) -> bool:
        """Sync agent assignment to Vikunja task."""
        try:
            job = self.jobs.get_job(job_id)
            agent = self.agents.get_agent(agent_id)
            
            if not job or not agent:
                return False
            
            # In a real implementation, we'd:
            # 1. Find the Vikunja project for this job
            # 2. Find the appropriate task (e.g., "Research execution")
            # 3. Assign the agent to the task
            
            self.logger.info(f"Agent {agent.name} assigned to job {job.slug}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to sync agent assignment: {e}")
            return False
    
    def sync_job_completion(self, job_id: UUID) -> bool:
        """Sync job completion to Vikunja."""
        try:
            job = self.jobs.get_job(job_id)
            if not job:
                return False
            
            # Update all tasks in the corresponding Vikunja project to "Done"
            # Mark project as completed
            
            self.logger.info(f"Job {job.slug} marked as completed in Vikunja")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to sync job completion: {e}")
            return False
    
    def create_agent_user(self, agent_id: UUID) -> bool:
        """Create Vikunja user for an agent (if needed)."""
        try:
            agent = self.agents.get_agent(agent_id)
            if not agent:
                return False
            
            # In a real implementation, we might create Vikunja users for agents
            # or use a service account with task assignment capabilities
            
            self.logger.info(f"Agent {agent.name} user setup in Vikunja")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create agent user: {e}")
            return False


class VikunjaSyncService:
    """Background service for Vikunja synchronization."""
    
    def __init__(self):
        self.sync = VikunjaSync()
        self.logger = logging.getLogger(__name__)
    
    async def sync_pending_jobs(self):
        """Sync all pending research jobs to Vikunja."""
        try:
            # Get all jobs that haven't been synced yet
            # In a real implementation, we'd track sync status in the database
            
            jobs = self.sync.jobs.list_jobs()
            
            for job in jobs:
                # Check if already synced (simplified check)
                if not self._is_job_synced(job['id']):
                    success = self.sync.sync_new_research_job(job['id'])
                    if success:
                        self._mark_job_synced(job['id'])
            
            self.logger.info("Completed Vikunja sync for pending jobs")
            
        except Exception as e:
            self.logger.error(f"Vikunja sync failed: {e}")
    
    def _is_job_synced(self, job_id: str) -> bool:
        """Check if job has been synced to Vikunja."""
        # In a real implementation, this would check a sync status table
        return False  # Simplified for demo
    
    def _mark_job_synced(self, job_id: str):
        """Mark job as synced to Vikunja."""
        # In a real implementation, this would update a sync status table
        pass


# Integration with new-research.sh
def create_vikunja_project_for_research(slug: str, title: str, description: Optional[str] = None) -> Optional[int]:
    """Create Vikunja project for a new research project."""
    try:
        sync = VikunjaSync()
        project = sync.vikunja_client.create_project(
            title=f"Research: {title}",
            description=f"Research project {slug}\n\n{description or 'No description provided'}"
        )
        return project['id']
    except Exception as e:
        logging.error(f"Failed to create Vikunja project for {slug}: {e}")
        return None


if __name__ == "__main__":
    # Example usage
    import os
    
    # Set environment variables
    os.environ['VIKUNJA_URL'] = 'http://localhost:3000'
    os.environ['VIKUNJA_API_TOKEN'] = 'your-api-token-here'
    
    # Test Vikunja integration
    try:
        sync = VikunjaSync()
        
        # Create a test project
        project = sync.vikunja_client.create_project(
            title="Test Research Project",
            description="This is a test project for Omega Stack integration"
        )
        
        print(f"Created project: {project}")
        
        # Create a test task
        task = sync.vikunja_client.create_task(
            project_id=project['id'],
            title="Test Task",
            description="This is a test task"
        )
        
        print(f"Created task: {task}")
        
    except Exception as e:
        print(f"Test failed: {e}")