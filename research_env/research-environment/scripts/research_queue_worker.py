#!/usr/bin/env python3
"""
Research Queue Worker for XNAi Foundation

This module implements a worker that processes research tasks from a Redis queue,
integrates with the model router for intelligent model selection, and updates
task status in Vikunja.
"""

import asyncio
import logging
import json
import os
import sys
from typing import Dict, Any, Optional
import redis.asyncio as aioredis
import aiohttp
from datetime import datetime
import yaml

# Add the scripts directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from model_router import ModelRouter
from jupyter_vikunja_integration import VikunjaIntegration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResearchQueueWorker:
    """Worker for processing research tasks from the queue."""
    
    def __init__(self):
        """Initialize the research queue worker."""
        self.redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
        self.vikunja_url = os.getenv('VIKUNJA_URL', 'http://localhost:3456/api/v1')
        self.model_router_config = os.getenv('MODEL_ROUTER_CONFIG', 'config/model-router.yaml')
        
        # Initialize components
        self.redis_client = None
        self.model_router = None
        self.vikunja_client = None
        
        # Worker configuration
        self.queue_name = 'research_queue'
        self.max_concurrent_tasks = 3
        self.poll_interval = 1.0  # seconds
        
        logger.info("Initialized Research Queue Worker")
    
    async def initialize(self):
        """Initialize async components."""
        try:
            # Initialize Redis connection
            self.redis_client = aioredis.from_url(self.redis_url)
            await self.redis_client.ping()
            logger.info("Connected to Redis")
            
            # Initialize model router
            self.model_router = ModelRouter(self.model_router_config)
            logger.info("Initialized Model Router")
            
            # Initialize Vikunja client
            self.vikunja_client = VikunjaIntegration(self.vikunja_url)
            logger.info("Initialized Vikunja Client")
            
        except Exception as e:
            logger.error(f"Failed to initialize worker: {e}")
            raise
    
    async def process_task(self, task_data: Dict[str, Any]) -> bool:
        """
        Process a single research task.
        
        Args:
            task_data: Task data from the queue
            
        Returns:
            True if task completed successfully, False otherwise
        """
        task_id = task_data.get('task_id')
        content = task_data.get('content', '')
        job_type = task_data.get('job_type', 'analysis')
        priority = task_data.get('priority', 2)
        
        try:
            # Update task status to in_progress
            if self.vikunja_client:
                self.vikunja_client.update_task_progress(task_id, 10, "Starting research task")
            
            logger.info(f"Processing task {task_id}: {job_type} (priority: {priority})")
            
            # Select model using router
            model_info = await self.model_router.select_model(job_type, content)
            selected_model = model_info.get('model', 'gpt-4o-mini')
            
            logger.info(f"Selected model {selected_model} for task {task_id}")
            
            # Update task with model information
            if self.vikunja_client:
                self.vikunja_client.update_task_progress(
                    task_id, 30, f"Selected model: {selected_model}"
                )
            
            # Process the task content
            result = await self._execute_research_task(content, job_type, selected_model)
            
            # Update task progress
            if self.vikunja_client:
                self.vikunja_client.update_task_progress(task_id, 80, "Research completed, updating Vikunja")
            
            # Update Vikunja task with results
            if self.vikunja_client:
                completion_notes = f"""
                Research task completed successfully!
                
                Model used: {selected_model}
                Job type: {job_type}
                Content length: {len(content)} characters
                Processing time: {datetime.now().isoformat()}
                
                Results:
                {result.get('summary', 'No summary available')}
                """
                
                self.vikunja_client.complete_research_task(task_id, completion_notes)
            
            logger.info(f"Task {task_id} completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error processing task {task_id}: {e}")
            
            # Update task with error status
            if self.vikunja_client:
                self.vikunja_client.update_task_progress(
                    task_id, 0, f"Error: {str(e)}"
                )
            
            return False
    
    async def _execute_research_task(self, content: str, job_type: str, model: str) -> Dict[str, Any]:
        """
        Execute the actual research task using the selected model.
        
        Args:
            content: Content to process
            job_type: Type of research job
            model: Selected model for processing
            
        Returns:
            Dictionary containing task results
        """
        # This would integrate with the actual model API
        # For now, return a mock result
        return {
            'summary': f"Processed {len(content)} characters using {model}",
            'job_type': job_type,
            'model': model,
            'timestamp': datetime.now().isoformat()
        }
    
    async def run_worker(self):
        """Main worker loop."""
        await self.initialize()
        
        logger.info("Starting research queue worker...")
        
        while True:
            try:
                # Check for tasks in the queue
                task_data = await self.redis_client.lpop(self.queue_name)
                
                if task_data:
                    # Process task
                    task_dict = json.loads(task_data)
                    success = await self.process_task(task_dict)
                    
                    if success:
                        logger.info(f"Task {task_dict.get('task_id')} completed successfully")
                    else:
                        logger.error(f"Task {task_dict.get('task_id')} failed")
                        
                        # Re-queue failed tasks with delay
                        await asyncio.sleep(5)
                        await self.redis_client.rpush(self.queue_name, json.dumps(task_dict))
                else:
                    # No tasks available, wait before checking again
                    await asyncio.sleep(self.poll_interval)
                    
            except Exception as e:
                logger.error(f"Error in worker loop: {e}")
                await asyncio.sleep(self.poll_interval)
    
    async def shutdown(self):
        """Shutdown the worker gracefully."""
        if self.redis_client:
            await self.redis_client.close()
        logger.info("Research Queue Worker shutdown complete")


async def main():
    """Main entry point for the research queue worker."""
    worker = ResearchQueueWorker()
    
    try:
        await worker.run_worker()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        await worker.shutdown()


if __name__ == "__main__":
    asyncio.run(main())