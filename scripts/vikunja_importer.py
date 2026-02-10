#!/usr/bin/env python3
"""
Vikunja Importer Script
Bulk import tasks from memory_bank export JSON to Vikunja API.
Supports dry-run mode and batch processing with retry logic.
"""

import json
import argparse
import asyncio
import aiohttp
import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


class VikunjaImporter:
    def __init__(self, api_url: str, token: str, batch_size: int = 50):
        self.api_url = api_url.rstrip('/')
        self.token = token
        self.batch_size = batch_size
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    @retry(
        retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, max=10),
        reraise=True
    )
    async def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a single task in Vikunja."""
        url = f"{self.api_url}/tasks"
        async with self.session.post(url, json=task_data) as response:
            if response.status in [200, 201]:
                return await response.json()
            elif response.status == 429:
                # Rate limited - wait and retry
                await asyncio.sleep(5)
                raise aiohttp.ClientResponseError(
                    request_info=response.request_info,
                    history=response.history,
                    status=response.status,
                    message="Rate limited"
                )
            else:
                error_text = await response.text()
                raise aiohttp.ClientResponseError(
                    request_info=response.request_info,
                    history=response.history,
                    status=response.status,
                    message=f"Failed to create task: {error_text}"
                )
    
    @retry(
        retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, max=10),
        reraise=True
    )
    async def get_or_create_label(self, label_name: str) -> Dict[str, Any]:
        """Get or create a label in Vikunja."""
        # First try to get existing label
        url = f"{self.api_url}/labels"
        async with self.session.get(url) as response:
            if response.status == 200:
                labels = await response.json()
                for label in labels:
                    if label.get('name') == label_name:
                        return label
        
        # Label doesn't exist, create it
        create_url = f"{self.api_url}/labels"
        label_data = {
            "name": label_name,
            "color": self._generate_color(label_name)
        }
        
        async with self.session.post(create_url, json=label_data) as response:
            if response.status in [200, 201]:
                return await response.json()
            else:
                error_text = await response.text()
                raise aiohttp.ClientResponseError(
                    request_info=response.request_info,
                    history=response.history,
                    status=response.status,
                    message=f"Failed to create label: {error_text}"
                )
    
    def _generate_color(self, label_name: str) -> str:
        """Generate a consistent color for a label based on its name."""
        import hashlib
        hash_object = hashlib.md5(label_name.encode())
        hex_dig = hash_object.hexdigest()
        # Use first 6 characters of hash to create a color
        return f"#{hex_dig[:6]}"
    
    async def process_batch(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process a batch of tasks with concurrent creation."""
        results = []
        tasks_with_labels = []
        
        # First, collect all unique labels and ensure they exist
        all_labels = set()
        for task in tasks:
            if 'labels' in task:
                all_labels.update(task['labels'])
        
        label_mapping = {}
        for label_name in all_labels:
            try:
                label_data = await self.get_or_create_label(label_name)
                label_mapping[label_name] = label_data['id']
            except Exception as e:
                print(f"Warning: Failed to create label '{label_name}': {e}")
                # Continue without this label
        
        # Prepare tasks with label IDs
        for task in tasks:
            task_copy = task.copy()
            if 'labels' in task_copy and label_mapping:
                task_copy['labels'] = [
                    {'id': label_mapping[label]} 
                    for label in task_copy['labels'] 
                    if label in label_mapping
                ]
            tasks_with_labels.append(task_copy)
        
        # Create tasks concurrently
        create_tasks = [self.create_task(task) for task in tasks_with_labels]
        try:
            results = await asyncio.gather(*create_tasks, return_exceptions=True)
        except Exception as e:
            print(f"Error creating tasks: {e}")
            return []
        
        # Filter out exceptions
        successful_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Warning: Failed to create task {i}: {result}")
            else:
                successful_results.append(result)
        
        return successful_results
    
    async def import_tasks(self, tasks: List[Dict[str, Any]], dry_run: bool = False) -> Dict[str, Any]:
        """Import tasks in batches."""
        total_tasks = len(tasks)
        successful_imports = 0
        failed_imports = 0
        
        print(f"Starting import of {total_tasks} tasks in batches of {self.batch_size}")
        
        for i in range(0, total_tasks, self.batch_size):
            batch = tasks[i:i + self.batch_size]
            batch_num = (i // self.batch_size) + 1
            total_batches = (total_tasks + self.batch_size - 1) // self.batch_size
            
            print(f"Processing batch {batch_num}/{total_batches} ({len(batch)} tasks)")
            
            if dry_run:
                print(f"  [DRY RUN] Would import {len(batch)} tasks")
                successful_imports += len(batch)
                continue
            
            try:
                results = await self.process_batch(batch)
                successful_imports += len(results)
                print(f"  Successfully imported {len(results)} tasks")
            except Exception as e:
                print(f"  Failed to import batch {batch_num}: {e}")
                failed_imports += len(batch)
        
        return {
            'total_tasks': total_tasks,
            'successful_imports': successful_imports,
            'failed_imports': failed_imports,
            'dry_run': dry_run
        }


def load_tasks_from_file(file_path: str) -> List[Dict[str, Any]]:
    """Load tasks from JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tasks = json.load(f)
        
        if not isinstance(tasks, list):
            raise ValueError("JSON file must contain an array of tasks")
        
        return tasks
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{file_path}': {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: Failed to load tasks from '{file_path}': {e}")
        sys.exit(1)


def validate_tasks(tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Validate and clean tasks before import."""
    validated_tasks = []
    
    for i, task in enumerate(tasks):
        if not isinstance(task, dict):
            print(f"Warning: Task {i} is not a dictionary, skipping")
            continue
        
        # Required fields
        if 'title' not in task:
            print(f"Warning: Task {i} missing title, skipping")
            continue
        
        # Clean up task data
        cleaned_task = {
            'title': task['title'][:255],  # Vikunja title length limit
            'description': task.get('description', ''),
            'priority': task.get('priority', 2),  # Default to medium
            'status': task.get('status', 'backlog')
        }
        
        # Add custom fields if present
        if 'custom_fields' in task and isinstance(task['custom_fields'], dict):
            cleaned_task['custom_fields'] = task['custom_fields']
        
        # Add labels if present
        if 'labels' in task and isinstance(task['labels'], list):
            cleaned_task['labels'] = task['labels']
        
        validated_tasks.append(cleaned_task)
    
    return validated_tasks


async def main():
    parser = argparse.ArgumentParser(description='Import tasks to Vikunja from JSON')
    parser.add_argument('file_path', help='Path to JSON file containing tasks')
    parser.add_argument('--api-url', default='http://localhost:3456/api/v1', 
                       help='Vikunja API URL (default: http://localhost:3456/api/v1)')
    parser.add_argument('--token', help='Vikunja API token')
    parser.add_argument('--batch-size', type=int, default=50, 
                       help='Batch size for imports (default: 50)')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Perform dry run without creating tasks')
    
    args = parser.parse_args()
    
    # Load tasks
    tasks = load_tasks_from_file(args.file_path)
    print(f"Loaded {len(tasks)} tasks from {args.file_path}")
    
    # Validate tasks
    validated_tasks = validate_tasks(tasks)
    print(f"Validated {len(validated_tasks)} tasks for import")
    
    if not validated_tasks:
        print("No valid tasks to import")
        sys.exit(1)
    
    # Get API token
    token = args.token
    if not token:
        if 'VIKUNJA_API_TOKEN' in os.environ:
            token = os.environ['VIKUNJA_API_TOKEN']
        else:
            print("Error: API token required. Use --token or set VIKUNJA_API_TOKEN environment variable")
            sys.exit(1)
    
    # Import tasks
    async with VikunjaImporter(args.api_url, token, args.batch_size) as importer:
        try:
            result = await importer.import_tasks(validated_tasks, args.dry_run)
            
            print(f"\nImport Summary:")
            print(f"  Total tasks: {result['total_tasks']}")
            print(f"  Successful: {result['successful_imports']}")
            print(f"  Failed: {result['failed_imports']}")
            print(f"  Dry run: {result['dry_run']}")
            
            if result['failed_imports'] > 0:
                sys.exit(1)
                
        except Exception as e:
            print(f"Import failed: {e}")
            sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())