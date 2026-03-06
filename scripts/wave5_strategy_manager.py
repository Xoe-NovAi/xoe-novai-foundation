#!/usr/bin/env python3
"""
Wave 5 Strategy Manager
=======================
Implementation of Wave 5 strategy with split test system and model evaluation.

This system manages the Wave 5 strategy execution, including automated model
comparison, performance tracking, and strategy updates.

Author: XNAi Foundation
Created: 2026-02-28
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import yaml
import statistics

# Foundation stack imports
from app.XNAi_rag_app.core.agent_bus import AgentBusClient
from app.XNAi_rag_app.core.model_router import ModelRouter
from app.XNAi_rag_app.core.memory_bank import MemoryBankLoader
from app.XNAi_rag_app.core.iam_db import IAMDatabase
from app.XNAi_rag_app.core.iam_handshake import IAMHandshake

# Configuration
CONFIG_PATH = Path("configs/wave5-strategy-manager.yaml")
LOG_LEVEL = logging.INFO

@dataclass
class ModelTestResult:
    """Result of a model test."""
    model_id: str
    task_id: str
    task_type: str
    execution_time: float
    accuracy_score: float
    cost_per_token: float
    memory_usage: float
    success: bool
    error_message: Optional[str] = None
    created_at: str = ""

@dataclass
class StrategyUpdate:
    """Strategy update based on test results."""
    update_type: str  # "model_ranking", "fallback_strategy", "routing_rules"
    changes: Dict[str, Any]
    confidence: float
    created_at: str = ""

class Wave5StrategyManager:
    """Wave 5 Strategy Manager with split test system."""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.config = self._load_config()
        self.test_results = []
        self.model_rankings = {}
        self.strategy_updates = []
        
        # Foundation stack integration
        self.agent_bus = AgentBusClient()
        self.model_router = ModelRouter()
        self.memory_bank = MemoryBankLoader()
        self.iam_db = IAMDatabase()
        self.iam_handshake = IAMHandshake()
        
        # Strategy state
        self.is_running = False
        self.active_tests = {}
        self.performance_history = {}
        
        self.logger.info("Wave 5 Strategy Manager initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logging.basicConfig(
            level=LOG_LEVEL,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/wave5-strategy-manager.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        return logging.getLogger(__name__)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load Wave 5 strategy configuration."""
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, 'r') as f:
                return yaml.safe_load(f)
        else:
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "strategy": {
                "enabled": True,
                "update_interval_hours": 24,
                "test_interval_minutes": 60,
                "min_test_samples": 10,
                "confidence_threshold": 0.8
            },
            "split_testing": {
                "enabled": True,
                "test_types": ["performance", "accuracy", "cost"],
                "models_per_test": 3,
                "tasks_per_model": 5,
                "timeout_seconds": 300
            },
            "evaluation": {
                "metrics": ["execution_time", "accuracy", "cost", "memory_usage"],
                "weights": {"execution_time": 0.3, "accuracy": 0.4, "cost": 0.2, "memory_usage": 0.1},
                "normalization": True
            },
            "model_ranking": {
                "enabled": True,
                "history_window_days": 7,
                "ranking_algorithm": "weighted_score"
            },
            "strategy_updates": {
                "auto_apply": True,
                "backup_strategy": True,
                "rollback_on_failure": True
            }
        }
    
    async def start(self):
        """Start the Wave 5 strategy manager."""
        if self.is_running:
            self.logger.warning("Wave 5 Strategy Manager already running")
            return
        
        self.is_running = True
        self.logger.info("Starting Wave 5 Strategy Manager...")
        
        # Load existing data
        await self._load_existing_data()
        
        # Start monitoring tasks
        tasks = [
            asyncio.create_task(self._run_strategy_updates()),
            asyncio.create_task(self._run_split_tests()),
            asyncio.create_task(self._monitor_performance()),
            asyncio.create_task(self._generate_strategy_reports())
        ]
        
        self.logger.info(f"Wave 5 Strategy Manager started with {len(tasks)} monitoring tasks")
        
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            self.logger.info("Wave 5 Strategy Manager stopped by user")
        except Exception as e:
            self.logger.error(f"Wave 5 Strategy Manager error: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the Wave 5 strategy manager."""
        self.is_running = False
        self.logger.info("Stopping Wave 5 Strategy Manager...")
    
    async def _load_existing_data(self):
        """Load existing test results and strategy data."""
        try:
            # Load test results
            results_path = Path("memory_bank/handovers/split-test/outputs/test_results.json")
            if results_path.exists():
                with open(results_path, 'r') as f:
                    self.test_results = json.load(f)
                self.logger.info(f"Loaded {len(self.test_results)} existing test results")
            
            # Load model rankings
            rankings_path = Path("memory_bank/handovers/split-test/outputs/model_rankings.json")
            if rankings_path.exists():
                with open(rankings_path, 'r') as f:
                    self.model_rankings = json.load(f)
                self.logger.info(f"Loaded model rankings for {len(self.model_rankings)} models")
            
            # Load strategy updates
            updates_path = Path("memory_bank/handovers/split-test/outputs/strategy_updates.json")
            if updates_path.exists():
                with open(updates_path, 'r') as f:
                    self.strategy_updates = json.load(f)
                self.logger.info(f"Loaded {len(self.strategy_updates)} existing strategy updates")
        
        except Exception as e:
            self.logger.error(f"Error loading existing data: {e}")
    
    async def _run_strategy_updates(self):
        """Run periodic strategy updates based on test results."""
        self.logger.info("Starting strategy update loop")
        
        while self.is_running:
            try:
                # Check if it's time for strategy update
                if self._should_update_strategy():
                    await self._execute_strategy_update()
                
                # Wait for next update interval
                await asyncio.sleep(self.config["strategy"]["update_interval_hours"] * 3600)
            
            except Exception as e:
                self.logger.error(f"Error in strategy update loop: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour before retry
    
    def _should_update_strategy(self) -> bool:
        """Check if strategy update is needed."""
        if not self.config["strategy"]["enabled"]:
            return False
        
        # Check if enough test samples exist
        recent_tests = self._get_recent_tests(hours=self.config["strategy"]["update_interval_hours"])
        if len(recent_tests) < self.config["strategy"]["min_test_samples"]:
            return False
        
        # Check if significant performance changes detected
        if self._has_significant_performance_changes():
            return True
        
        return False
    
    def _get_recent_tests(self, hours: int = 24) -> List[ModelTestResult]:
        """Get test results from the last N hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_tests = []
        
        for test in self.test_results:
            test_time = datetime.fromisoformat(test["created_at"])
            if test_time > cutoff_time:
                recent_tests.append(ModelTestResult(**test))
        
        return recent_tests
    
    def _has_significant_performance_changes(self) -> bool:
        """Check if there are significant performance changes."""
        recent_tests = self._get_recent_tests(hours=24)
        
        if len(recent_tests) < 10:
            return False
        
        # Group by model
        model_performance = {}
        for test in recent_tests:
            if test.model_id not in model_performance:
                model_performance[test.model_id] = []
            model_performance[test.model_id].append(test.accuracy_score)
        
        # Check for significant changes in model performance
        for model_id, scores in model_performance.items():
            if len(scores) >= 5:
                mean_score = statistics.mean(scores)
                std_dev = statistics.stdev(scores) if len(scores) > 1 else 0
                
                # Check if performance deviates significantly from historical average
                historical_avg = self.performance_history.get(model_id, {}).get("avg_accuracy", 0)
                if historical_avg > 0 and abs(mean_score - historical_avg) > (std_dev * 2):
                    return True
        
        return False
    
    async def _execute_strategy_update(self):
        """Execute strategy update based on test results."""
        self.logger.info("Executing strategy update...")
        
        try:
            # Update model rankings
            await self._update_model_rankings()
            
            # Generate strategy recommendations
            recommendations = await self._generate_strategy_recommendations()
            
            # Apply strategy updates
            for recommendation in recommendations:
                await self._apply_strategy_update(recommendation)
            
            # Save updated data
            await self._save_strategy_data()
            
            self.logger.info("Strategy update completed successfully")
        
        except Exception as e:
            self.logger.error(f"Error executing strategy update: {e}")
    
    async def _update_model_rankings(self):
        """Update model rankings based on recent test results."""
        recent_tests = self._get_recent_tests(hours=self.config["strategy"]["history_window_days"] * 24)
        
        if not recent_tests:
            return
        
        # Calculate weighted scores for each model
        model_scores = {}
        for test in recent_tests:
            if test.model_id not in model_scores:
                model_scores[test.model_id] = []
            
            # Calculate weighted score
            weights = self.config["evaluation"]["weights"]
            score = (
                test.accuracy_score * weights["accuracy"] +
                (1 / test.execution_time) * weights["execution_time"] +
                (1 / test.cost_per_token) * weights["cost"] +
                (1 / test.memory_usage) * weights["memory_usage"]
            )
            
            model_scores[test.model_id].append(score)
        
        # Calculate average scores and rankings
        for model_id, scores in model_scores.items():
            avg_score = statistics.mean(scores)
            self.model_rankings[model_id] = {
                "avg_score": avg_score,
                "test_count": len(scores),
                "last_updated": datetime.now().isoformat()
            }
        
        # Sort by score
        self.model_rankings = dict(sorted(
            self.model_rankings.items(),
            key=lambda x: x[1]["avg_score"],
            reverse=True
        ))
        
        self.logger.info(f"Updated rankings for {len(self.model_rankings)} models")
    
    async def _generate_strategy_recommendations(self) -> List[StrategyUpdate]:
        """Generate strategy recommendations based on test results."""
        recommendations = []
        
        # Model ranking updates
        if len(self.model_rankings) > 1:
            top_model = list(self.model_rankings.keys())[0]
            current_primary = self.model_router.get_primary_model()
            
            if top_model != current_primary:
                recommendations.append(StrategyUpdate(
                    update_type="model_ranking",
                    changes={"primary_model": top_model, "previous_primary": current_primary},
                    confidence=0.9,
                    created_at=datetime.now().isoformat()
                ))
        
        # Fallback strategy updates
        fallback_updates = await self._analyze_fallback_strategy()
        if fallback_updates:
            recommendations.extend(fallback_updates)
        
        # Routing rule updates
        routing_updates = await self._analyze_routing_rules()
        if routing_updates:
            recommendations.extend(routing_updates)
        
        return recommendations
    
    async def _analyze_fallback_strategy(self) -> List[StrategyUpdate]:
        """Analyze and update fallback strategy."""
        fallback_updates = []
        
        # Analyze failure rates
        recent_tests = self._get_recent_tests(hours=24)
        failure_rates = {}
        
        for test in recent_tests:
            if test.model_id not in failure_rates:
                failure_rates[test.model_id] = {"total": 0, "failed": 0}
            
            failure_rates[test.model_id]["total"] += 1
            if not test.success:
                failure_rates[test.model_id]["failed"] += 1
        
        # Identify models with high failure rates
        for model_id, stats in failure_rates.items():
            failure_rate = stats["failed"] / stats["total"]
            if failure_rate > 0.2:  # 20% failure rate threshold
                fallback_updates.append(StrategyUpdate(
                    update_type="fallback_strategy",
                    changes={"model_id": model_id, "failure_rate": failure_rate, "action": "demote"},
                    confidence=0.8,
                    created_at=datetime.now().isoformat()
                ))
        
        return fallback_updates
    
    async def _analyze_routing_rules(self) -> List[StrategyUpdate]:
        """Analyze and update routing rules."""
        routing_updates = []
        
        # Analyze performance by task type
        recent_tests = self._get_recent_tests(hours=24)
        task_performance = {}
        
        for test in recent_tests:
            task_type = test.task_type
            if task_type not in task_performance:
                task_performance[task_type] = {}
            
            if test.model_id not in task_performance[task_type]:
                task_performance[task_type][test.model_id] = []
            
            task_performance[task_type][test.model_id].append(test.accuracy_score)
        
        # Generate task-specific model recommendations
        for task_type, model_scores in task_performance.items():
            if len(model_scores) > 1:
                # Find best model for this task type
                best_model = max(model_scores.keys(), key=lambda m: statistics.mean(model_scores[m]))
                
                routing_updates.append(StrategyUpdate(
                    update_type="routing_rules",
                    changes={"task_type": task_type, "recommended_model": best_model},
                    confidence=0.85,
                    created_at=datetime.now().isoformat()
                ))
        
        return routing_updates
    
    async def _apply_strategy_update(self, update: StrategyUpdate):
        """Apply a strategy update."""
        try:
            if update.update_type == "model_ranking":
                # Update model router configuration
                new_primary = update.changes["primary_model"]
                self.model_router.set_primary_model(new_primary)
                
                self.logger.info(f"Updated primary model to: {new_primary}")
            
            elif update.update_type == "fallback_strategy":
                # Update fallback strategy
                model_id = update.changes["model_id"]
                action = update.changes["action"]
                
                if action == "demote":
                    self.model_router.demote_model(model_id)
                
                self.logger.info(f"Applied fallback strategy update for {model_id}")
            
            elif update.update_type == "routing_rules":
                # Update routing rules
                task_type = update.changes["task_type"]
                recommended_model = update.changes["recommended_model"]
                
                self.model_router.update_routing_rule(task_type, recommended_model)
                
                self.logger.info(f"Updated routing rule for {task_type} -> {recommended_model}")
            
            # Store the update
            self.strategy_updates.append(asdict(update))
            
        except Exception as e:
            self.logger.error(f"Error applying strategy update: {e}")
    
    async def _run_split_tests(self):
        """Run periodic split tests for model comparison."""
        self.logger.info("Starting split test loop")
        
        while self.is_running:
            try:
                if self.config["split_testing"]["enabled"]:
                    await self._execute_split_test()
                
                # Wait for next test interval
                await asyncio.sleep(self.config["split_testing"]["test_interval_minutes"] * 60)
            
            except Exception as e:
                self.logger.error(f"Error in split test loop: {e}")
                await asyncio.sleep(600)  # Wait 10 minutes before retry
    
    async def _execute_split_test(self):
        """Execute a split test comparing multiple models."""
        self.logger.info("Executing split test...")
        
        try:
            # Select models for testing
            models_to_test = self._select_models_for_test()
            
            # Select tasks for testing
            tasks_to_test = self._select_tasks_for_test()
            
            # Execute tests
            test_results = []
            for model_id in models_to_test:
                for task in tasks_to_test:
                    result = await self._execute_model_test(model_id, task)
                    if result:
                        test_results.append(result)
            
            # Store results
            self.test_results.extend(test_results)
            
            # Update performance history
            await self._update_performance_history(test_results)
            
            self.logger.info(f"Split test completed with {len(test_results)} results")
        
        except Exception as e:
            self.logger.error(f"Error executing split test: {e}")
    
    def _select_models_for_test(self) -> List[str]:
        """Select models to include in split test."""
        # Get top models from current rankings
        top_models = list(self.model_rankings.keys())[:self.config["split_testing"]["models_per_test"]]
        
        # If not enough ranked models, get available models
        if len(top_models) < self.config["split_testing"]["models_per_test"]:
            available_models = self.model_router.list_available_models()
            top_models = available_models[:self.config["split_testing"]["models_per_test"]]
        
        return top_models
    
    def _select_tasks_for_test(self) -> List[Dict[str, Any]]:
        """Select tasks for split testing."""
        # Define test tasks based on configuration
        test_tasks = [
            {
                "task_type": "coding",
                "description": "Code generation and debugging",
                "complexity": "medium",
                "prompt": "Write a Python function to implement quicksort algorithm with detailed comments"
            },
            {
                "task_type": "analysis",
                "description": "Text analysis and summarization",
                "complexity": "medium",
                "prompt": "Analyze the following text and provide a 3-paragraph summary: [sample text]"
            },
            {
                "task_type": "reasoning",
                "description": "Logical reasoning and problem solving",
                "complexity": "high",
                "prompt": "Solve this logic puzzle step by step: [puzzle description]"
            }
        ]
        
        return test_tasks[:self.config["split_testing"]["tasks_per_model"]]
    
    async def _execute_model_test(self, model_id: str, task: Dict[str, Any]) -> Optional[ModelTestResult]:
        """Execute a test for a specific model and task."""
        try:
            start_time = datetime.now()
            
            # Execute task through Foundation stack
            result = await self._execute_task_with_model(model_id, task)
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            # Calculate metrics
            accuracy_score = self._calculate_accuracy_score(result, task)
            cost_per_token = self._calculate_cost_per_token(model_id, result)
            memory_usage = self._estimate_memory_usage(model_id)
            
            test_result = ModelTestResult(
                model_id=model_id,
                task_id=f"{model_id}_{task['task_type']}_{start_time.timestamp()}",
                task_type=task["task_type"],
                execution_time=execution_time,
                accuracy_score=accuracy_score,
                cost_per_token=cost_per_token,
                memory_usage=memory_usage,
                success=True,
                created_at=start_time.isoformat()
            )
            
            return test_result
        
        except Exception as e:
            self.logger.error(f"Error executing test for {model_id}: {e}")
            
            return ModelTestResult(
                model_id=model_id,
                task_id=f"{model_id}_{task['task_type']}_{datetime.now().timestamp()}",
                task_type=task["task_type"],
                execution_time=0,
                accuracy_score=0,
                cost_per_token=0,
                memory_usage=0,
                success=False,
                error_message=str(e),
                created_at=datetime.now().isoformat()
            )
    
    async def _execute_task_with_model(self, model_id: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task using a specific model."""
        # This would integrate with the actual model execution
        # For now, return mock result
        return {
            "model_id": model_id,
            "task_type": task["task_type"],
            "response": "Mock response for testing",
            "tokens_used": 100,
            "execution_time": 2.5
        }
    
    def _calculate_accuracy_score(self, result: Dict[str, Any], task: Dict[str, Any]) -> float:
        """Calculate accuracy score for a test result."""
        # This would implement actual accuracy calculation
        # For now, return mock score
        import random
        return random.uniform(0.7, 0.95)
    
    def _calculate_cost_per_token(self, model_id: str, result: Dict[str, Any]) -> float:
        """Calculate cost per token for a model."""
        # This would implement actual cost calculation
        # For now, return mock cost
        return 0.0001
    
    def _estimate_memory_usage(self, model_id: str) -> float:
        """Estimate memory usage for a model."""
        # This would implement actual memory estimation
        # For now, return mock memory usage
        return 1024.0  # MB
    
    async def _update_performance_history(self, test_results: List[ModelTestResult]):
        """Update performance history with new test results."""
        for result in test_results:
            if result.model_id not in self.performance_history:
                self.performance_history[result.model_id] = {
                    "accuracy_scores": [],
                    "execution_times": [],
                    "costs": [],
                    "memory_usage": []
                }
            
            history = self.performance_history[result.model_id]
            history["accuracy_scores"].append(result.accuracy_score)
            history["execution_times"].append(result.execution_time)
            history["costs"].append(result.cost_per_token)
            history["memory_usage"].append(result.memory_usage)
            
            # Keep only recent history
            max_history = 100
            for key in history:
                if isinstance(history[key], list) and len(history[key]) > max_history:
                    history[key] = history[key][-max_history:]
    
    async def _monitor_performance(self):
        """Monitor model performance and detect issues."""
        self.logger.info("Starting performance monitoring")
        
        while self.is_running:
            try:
                # Check for performance degradation
                await self._check_performance_degradation()
                
                # Check for model availability
                await self._check_model_availability()
                
                # Wait before next check
                await asyncio.sleep(300)  # 5 minutes
            
            except Exception as e:
                self.logger.error(f"Error in performance monitoring: {e}")
                await asyncio.sleep(300)
    
    async def _check_performance_degradation(self):
        """Check for performance degradation in models."""
        recent_tests = self._get_recent_tests(hours=1)
        
        if len(recent_tests) < 5:
            return
        
        # Group by model and check for degradation
        for model_id in set(test.model_id for test in recent_tests):
            model_tests = [test for test in recent_tests if test.model_id == model_id]
            
            if len(model_tests) >= 3:
                avg_accuracy = statistics.mean(test.accuracy_score for test in model_tests)
                avg_time = statistics.mean(test.execution_time for test in model_tests)
                
                # Check against historical averages
                historical = self.performance_history.get(model_id, {})
                if historical:
                    hist_accuracy = statistics.mean(historical.get("accuracy_scores", [0]))
                    hist_time = statistics.mean(historical.get("execution_times", [0]))
                    
                    # Alert if significant degradation
                    if avg_accuracy < hist_accuracy * 0.8 or avg_time > hist_time * 1.5:
                        await self._send_performance_alert(model_id, avg_accuracy, avg_time)
    
    async def _check_model_availability(self):
        """Check if models are available and responding."""
        available_models = self.model_router.list_available_models()
        
        # Check if primary model is available
        primary_model = self.model_router.get_primary_model()
        if primary_model and primary_model not in available_models:
            await self._handle_model_unavailable(primary_model)
    
    async def _send_performance_alert(self, model_id: str, current_accuracy: float, current_time: float):
        """Send performance degradation alert."""
        alert = {
            "type": "performance_degradation",
            "model_id": model_id,
            "current_accuracy": current_accuracy,
            "current_time": current_time,
            "timestamp": datetime.now().isoformat()
        }
        
        await self.agent_bus.publish("performance_alert", alert)
        self.logger.warning(f"Performance degradation detected for {model_id}")
    
    async def _handle_model_unavailable(self, model_id: str):
        """Handle unavailable model."""
        self.logger.warning(f"Model {model_id} is unavailable")
        
        # Update strategy to use fallback
        fallback_update = StrategyUpdate(
            update_type="fallback_strategy",
            changes={"model_id": model_id, "action": "unavailable"},
            confidence=1.0,
            created_at=datetime.now().isoformat()
        )
        
        await self._apply_strategy_update(fallback_update)
    
    async def _generate_strategy_reports(self):
        """Generate periodic strategy reports."""
        self.logger.info("Starting strategy report generation")
        
        while self.is_running:
            try:
                # Generate daily report
                await self._generate_daily_report()
                
                # Wait 24 hours
                await asyncio.sleep(86400)
            
            except Exception as e:
                self.logger.error(f"Error generating strategy reports: {e}")
                await asyncio.sleep(3600)
    
    async def _generate_daily_report(self):
        """Generate daily strategy report."""
        report = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "model_rankings": self.model_rankings,
            "test_results_count": len(self.test_results),
            "strategy_updates_count": len(self.strategy_updates),
            "performance_summary": self._get_performance_summary(),
            "recommendations": await self._get_daily_recommendations(),
            "generated_at": datetime.now().isoformat()
        }
        
        # Save report
        reports_dir = Path("memory_bank/handovers/split-test/outputs/reports")
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = reports_dir / f"daily_report_{datetime.now().strftime('%Y-%m-%d')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"Generated daily report: {report_file}")
    
    def _get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        recent_tests = self._get_recent_tests(hours=24)
        
        if not recent_tests:
            return {}
        
        # Calculate summary statistics
        avg_accuracy = statistics.mean(test.accuracy_score for test in recent_tests)
        avg_time = statistics.mean(test.execution_time for test in recent_tests)
        success_rate = sum(1 for test in recent_tests if test.success) / len(recent_tests)
        
        return {
            "avg_accuracy": avg_accuracy,
            "avg_execution_time": avg_time,
            "success_rate": success_rate,
            "total_tests": len(recent_tests)
        }
    
    async def _get_daily_recommendations(self) -> List[Dict[str, Any]]:
        """Get daily strategy recommendations."""
        recommendations = []
        
        # Model performance recommendations
        if self.model_rankings:
            top_model = list(self.model_rankings.keys())[0]
            recommendations.append({
                "type": "model_selection",
                "recommendation": f"Use {top_model} as primary model",
                "confidence": self.model_rankings[top_model]["avg_score"]
            })
        
        # Fallback strategy recommendations
        fallback_rec = await self._get_fallback_recommendations()
        recommendations.extend(fallback_rec)
        
        return recommendations
    
    async def _get_fallback_recommendations(self) -> List[Dict[str, Any]]:
        """Get fallback strategy recommendations."""
        fallback_recs = []
        
        # Analyze failure patterns
        recent_tests = self._get_recent_tests(hours=24)
        failure_rates = {}
        
        for test in recent_tests:
            if test.model_id not in failure_rates:
                failure_rates[test.model_id] = {"total": 0, "failed": 0}
            
            failure_rates[test.model_id]["total"] += 1
            if not test.success:
                failure_rates[test.model_id]["failed"] += 1
        
        for model_id, stats in failure_rates.items():
            failure_rate = stats["failed"] / stats["total"]
            if failure_rate > 0.1:  # 10% failure rate
                fallback_recs.append({
                    "type": "fallback_strategy",
                    "model_id": model_id,
                    "failure_rate": failure_rate,
                    "recommendation": "Consider demoting or adding fallback for this model"
                })
        
        return fallback_recs
    
    async def _save_strategy_data(self):
        """Save strategy data to persistent storage."""
        try:
            # Save test results
            results_path = Path("memory_bank/handovers/split-test/outputs/test_results.json")
            results_path.parent.mkdir(parents=True, exist_ok=True)
            with open(results_path, 'w') as f:
                json.dump(self.test_results, f, indent=2)
            
            # Save model rankings
            rankings_path = Path("memory_bank/handovers/split-test/outputs/model_rankings.json")
            with open(rankings_path, 'w') as f:
                json.dump(self.model_rankings, f, indent=2)
            
            # Save strategy updates
            updates_path = Path("memory_bank/handovers/split-test/outputs/strategy_updates.json")
            with open(updates_path, 'w') as f:
                json.dump(self.strategy_updates, f, indent=2)
            
            self.logger.info("Strategy data saved successfully")
        
        except Exception as e:
            self.logger.error(f"Error saving strategy data: {e}")
    
    def get_strategy_status(self) -> Dict[str, Any]:
        """Get current strategy status."""
        return {
            "is_running": self.is_running,
            "test_results_count": len(self.test_results),
            "model_rankings_count": len(self.model_rankings),
            "strategy_updates_count": len(self.strategy_updates),
            "active_tests": len(self.active_tests),
            "performance_history_models": len(self.performance_history)
        }

async def main():
    """Main Wave 5 strategy manager execution."""
    manager = Wave5StrategyManager()
    
    try:
        await manager.start()
    except KeyboardInterrupt:
        manager.stop()

if __name__ == "__main__":
    asyncio.run(main())