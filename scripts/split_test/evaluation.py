#!/usr/bin/env python3
"""
Vikunja Integration for Split Tests
===================================
Manages split test tasks in Vikunja for tracking and coordination.

Usage:
    from split_test.evaluation import VikunjaTestTracker

    tracker = VikunjaTestTracker()
    task_id = tracker.create_test_task("wave5-split-test", models)
    tracker.update_progress(task_id, "raptor", "completed")
"""

import os
import logging
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class VikunjaTestTracker:
    """Tracks split tests in Vikunja."""

    def __init__(self, base_url: str = None, api_key: str = None):
        self.base_url = base_url or os.getenv("VIKUNJA_URL", "http://localhost:3456")
        self.api_key = api_key or os.getenv("VIKUNJA_API_KEY", "")
        self.headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

    def create_test_project(self, name: str = "Split Tests") -> Optional[int]:
        """Create a project for split tests."""
        url = f"{self.base_url}/v1/projects"
        data = {"title": name, "description": "AI Model Split Test Tracking"}

        try:
            response = requests.post(url, json=data, headers=self.headers)
            if response.status_code == 200:
                return response.json()["id"]
            else:
                logger.warning(f"Vikunja create project returned {response.status_code}: {response.text}")
        except Exception as e:
            logger.exception(f"Vikunja not available: {e}")

        return None

    def create_test_task(self, test_name: str, models: List[str], project_id: Optional[int] = None) -> Optional[Dict]:
        """Create a task for the entire split test."""
        url = f"{self.base_url}/v1/tasks"

        # Create description with all models
        description = f"Split Test: {test_name}\n\n"
        description += "## Models\n"
        for model in models:
            description += f"- {model}\n"

        data = {
            "title": f"Split Test: {test_name}",
            "description": description,
            "project_id": project_id,
            "due_date": datetime.now().isoformat(),
            "priority": 3,  # High
        }

        try:
            response = requests.post(url, json=data, headers=self.headers)
            if response.status_code in (200, 201):
                task = response.json()

                # Create subtasks for each model
                for model in models:
                    self._create_model_subtask(task["id"], model)

                return task
            else:
                logger.warning(f"Vikunja create task returned {response.status_code}: {response.text}")
        except Exception as e:
            logger.exception(f"Vikunja not available: {e}")

        return None

    def _create_model_subtask(self, parent_id: int, model_name: str) -> Optional[Dict]:
        """Create a subtask for a specific model."""
        url = f"{self.base_url}/v1/tasks"

        data = {
            "title": f"Model: {model_name}",
            "description": f"Run {model_name} for split test",
            "project_id": 0,  # Will be assigned by parent
            "parent_id": parent_id,
            "priority": 2,  # Medium
        }

        try:
            response = requests.post(url, json=data, headers=self.headers)
            if response.status_code in (200, 201):
                return response.json()
            else:
                logger.warning(f"Vikunja create subtask returned {response.status_code}: {response.text}")
        except Exception:
            logger.exception("Failed to create Vikunja subtask")

        return None

    def update_model_status(self, task_id: int, status: str, notes: str = "") -> bool:
        """Update the status of a model test."""
        url = f"{self.base_url}/v1/tasks/{task_id}"

        # Map status to Vikunja values
        status_map = {"pending": 0, "in_progress": 2, "completed": 3, "failed": 4}

        data = {"done": status == "completed", "status": status_map.get(status, 0), "description": notes}

        try:
            response = requests.patch(url, json=data, headers=self.headers)
            if response.status_code not in (200, 204):
                logger.warning(f"Vikunja update returned {response.status_code}: {response.text}")
            return response.status_code in (200, 204)
        except Exception:
            logger.exception("Failed to update Vikunja task")
            return False

    def get_test_progress(self, test_task_id: int) -> Dict[str, Any]:
        """Get progress for all models in a test."""
        url = f"{self.base_url}/v1/tasks/{test_task_id}/subtasks"

        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                subtasks = response.json()

                progress = {
                    "total": len(subtasks),
                    "completed": sum(1 for t in subtasks.get("subtasks", []) if t.get("done")),
                    "pending": sum(1 for t in subtasks.get("subtasks", []) if not t.get("done")),
                    "models": {},
                }

                for task in subtasks.get("subtasks", []):
                    progress["models"][task["title"].replace("Model: ", "")] = {
                        "done": task.get("done", False),
                        "status": "completed" if task.get("done") else "pending",
                    }

                return progress
            else:
                logger.warning(f"Vikunja get progress returned {response.status_code}: {response.text}")
        except Exception:
            logger.exception("Failed to fetch Vikunja progress")
            
        return {}

        return {}


# ============================================================================
# AGENT BUS INTEGRATION
# ============================================================================


class SplitTestAgentBus:
    """Integrates split tests with Agent Bus for coordination."""

    def __init__(self):
        self.stream_name = "xnai:split_test"

    def publish_test_event(self, event_type: str, data: Dict):
        """Publish an event to the agent bus."""
        # This would integrate with Redis Streams in production
        print(f"[AgentBus] {event_type}: {data}")

    def test_started(self, test_id: str, models: List[str]):
        """Publish test start event."""
        self.publish_test_event(
            "test_started", {"test_id": test_id, "models": models, "timestamp": datetime.now().isoformat()}
        )

    def model_started(self, test_id: str, model_id: str):
        """Publish model start event."""
        self.publish_test_event(
            "model_started", {"test_id": test_id, "model_id": model_id, "timestamp": datetime.now().isoformat()}
        )

    def model_completed(self, test_id: str, model_id: str, metrics: Dict, score: float):
        """Publish model completion event."""
        self.publish_test_event(
            "model_completed",
            {
                "test_id": test_id,
                "model_id": model_id,
                "metrics": metrics,
                "score": score,
                "timestamp": datetime.now().isoformat(),
            },
        )

    def test_completed(self, test_id: str, winner: str, scores: Dict[str, float]):
        """Publish test completion event."""
        self.publish_test_event(
            "test_completed", {"test_id": test_id, "winner": winner, "scores": scores, "timestamp": datetime.now().isoformat()}
        )


if __name__ == "__main__":
    # Example usage
    tracker = VikunjaTestTracker()

    # Create a test task
    task = tracker.create_test_task("Wave 5 Manual", ["raptor-mini", "haiku-4.5", "minimax-m2.5", "kat-coder-pro"])

    if task:
        print(f"Created test task: {task['id']}")

        # Get progress
        progress = tracker.get_test_progress(task["id"])
        print(f"Progress: {progress}")
