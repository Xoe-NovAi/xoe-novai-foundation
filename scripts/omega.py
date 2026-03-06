#!/usr/bin/env python3
"""Omega CLI helper for agent and research job management."""

import argparse
import sys
import uuid
from pathlib import Path
from typing import Optional

# Database imports
from uuid import UUID
from sqlalchemy.exc import IntegrityError

# Local services
from app.XNAi_rag_app.services.agent_management import (
    AgentRegistry, 
    ResearchJobManager, 
    AgentMetricsManager,
    AgentMemoryManager
)
from app.XNAi_rag_app.services.database import get_db_session


def get_services():
    """Get initialized service instances."""
    db_session = get_db_session()
    registry = AgentRegistry(db_session)
    jobs = ResearchJobManager(db_session)
    metrics = AgentMetricsManager(db_session)
    memory = AgentMemoryManager(db_session)
    return registry, jobs, metrics, memory, db_session


def list_jobs(args):
    """List available research jobs."""
    registry, jobs, metrics, memory, db_session = get_services()
    
    try:
        filters = {}
        if hasattr(args, 'status') and args.status:
            filters['status'] = args.status
        if hasattr(args, 'claimed_by') and args.claimed_by:
            filters['claimed_by'] = UUID(args.claimed_by)
        if hasattr(args, 'domain_tags') and args.domain_tags:
            filters['domain_tags'] = args.domain_tags.split(',')
        
        job_list = jobs.list_jobs(**filters)
        
        if not job_list:
            print("No jobs found.")
            return
        
        print(f"Found {len(job_list)} job(s):")
        print("-" * 80)
        for job in job_list:
            status_emoji = "🟢" if job['status'] == 'open' else "🟡" if job['status'] == 'claimed' else "🔴"
            print(f"{status_emoji} {job['slug']} ({job['id']})")
            print(f"   Title: {job['title']}")
            print(f"   Status: {job['status']}")
            if job['claimed_by']:
                print(f"   Claimed by: {job['claimed_by']}")
            if job['domain_tags']:
                print(f"   Domains: {', '.join(job['domain_tags'])}")
            print(f"   Created: {job['created_at']}")
            print()
    
    except Exception as e:
        print(f"Error listing jobs: {e}")
        sys.exit(1)


def claim_job(args):
    """Claim a job for an agent."""
    registry, jobs, metrics, memory, db_session = get_services()
    
    try:
        agent_id = UUID(args.agent_id)
        job_id = UUID(args.job_id)
    except ValueError:
        print("Invalid UUID provided")
        sys.exit(1)
    
    try:
        success = jobs.claim_job(job_id, agent_id)
        if success:
            print(f"✅ Agent {args.agent_id} successfully claimed job {args.job_id}")
        else:
            print("❌ Failed to claim job (job may not exist or already claimed)")
            sys.exit(1)
    except Exception as e:
        print(f"Error claiming job: {e}")
        sys.exit(1)


def invite_agent(args):
    """Invite an agent to collaborate on a job."""
    registry, jobs, metrics, memory, db_session = get_services()
    
    try:
        agent_id = UUID(args.agent_id)
        job_id = UUID(args.job_id)
        target_agent = UUID(args.target_agent)
    except ValueError:
        print("Invalid UUID provided")
        sys.exit(1)
    
    try:
        success = jobs.invite_collaborator(job_id, target_agent)
        if success:
            print(f"✅ Agent {args.target_agent} invited to job {args.job_id}")
        else:
            print("❌ Failed to invite agent (job or agent may not exist)")
            sys.exit(1)
    except Exception as e:
        print(f"Error inviting agent: {e}")
        sys.exit(1)


def list_agents(args):
    """List all registered agents."""
    registry, jobs, metrics, memory, db_session = get_services()
    
    try:
        filters = {}
        if hasattr(args, 'status') and args.status:
            filters['status'] = args.status
        
        agent_list = registry.list_agents(**filters)
        
        if not agent_list:
            print("No agents registered yet.")
            return
        
        print(f"Found {len(agent_list)} agent(s):")
        print("-" * 80)
        print(f"{'ID':<36} {'Name':<20} {'Model':<15} {'Priority':<10} {'Status'}")
        print("-" * 80)
        for agent in agent_list:
            print(f"{agent['id']:<36} {agent['name']:<20} {agent['model']:<15} {agent['priority']:<10} {agent['status']}")
    
    except Exception as e:
        print(f"Error listing agents: {e}")
        sys.exit(1)


def register_agent(args):
    """Register a new agent."""
    registry, jobs, metrics, memory, db_session = get_services()
    
    try:
        agent = registry.register_agent(
            name=args.name,
            model=args.model,
            runtime=getattr(args, 'runtime', 'unknown'),
            email=getattr(args, 'email', None)
        )
        print(f"✅ Agent '{agent.name}' registered successfully with ID: {agent.id}")
    except ValueError as e:
        print(f"❌ Registration failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error registering agent: {e}")
        sys.exit(1)


def update_agent_status(args):
    """Update agent status."""
    registry, jobs, metrics, memory, db_session = get_services()
    
    try:
        agent_id = UUID(args.agent_id)
        success = registry.update_agent_status(agent_id, args.status)
        if success:
            print(f"✅ Agent {args.agent_id} status updated to '{args.status}'")
        else:
            print("❌ Agent not found")
            sys.exit(1)
    except ValueError:
        print("Invalid UUID provided")
        sys.exit(1)
    except Exception as e:
        print(f"Error updating agent status: {e}")
        sys.exit(1)


def set_agent_preferences(args):
    """Set agent domain preferences."""
    registry, jobs, metrics, memory, db_session = get_services()
    
    try:
        agent_id = UUID(args.agent_id)
        preferences = {}
        for pref in args.preferences:
            domain, score = pref.split(':')
            preferences[domain] = float(score)
        
        success = registry.set_agent_preferences(agent_id, preferences)
        if success:
            print(f"✅ Agent {args.agent_id} preferences updated")
        else:
            print("❌ Failed to update preferences")
            sys.exit(1)
    except ValueError as e:
        print(f"Invalid input: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error setting preferences: {e}")
        sys.exit(1)


def create_job(args):
    """Create a new research job."""
    registry, jobs, metrics, memory, db_session = get_services()
    
    try:
        domain_tags = args.domain_tags.split(',') if args.domain_tags else None
        
        job = jobs.create_job(
            slug=args.slug,
            title=args.title,
            description=getattr(args, 'description', None),
            domain_tags=domain_tags
        )
        print(f"✅ Job '{job.title}' created successfully with ID: {job.id}")
    except ValueError as e:
        print(f"❌ Job creation failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error creating job: {e}")
        sys.exit(1)


def complete_job(args):
    """Mark a job as completed."""
    registry, jobs, metrics, memory, db_session = get_services()
    
    try:
        job_id = UUID(args.job_id)
        success = jobs.complete_job(job_id)
        if success:
            print(f"✅ Job {args.job_id} marked as completed")
        else:
            print("❌ Job not found")
            sys.exit(1)
    except ValueError:
        print("Invalid UUID provided")
        sys.exit(1)
    except Exception as e:
        print(f"Error completing job: {e}")
        sys.exit(1)


def record_metric(args):
    """Record a metric for an agent."""
    registry, jobs, metrics, memory, db_session = get_services()
    
    try:
        agent_id = UUID(args.agent_id)
        metric = metrics.record_metric(
            agent_id=agent_id,
            metric_name=args.metric_name,
            value=float(args.value)
        )
        print(f"✅ Metric '{args.metric_name}' recorded for agent {args.agent_id}")
    except ValueError as e:
        print(f"Invalid input: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error recording metric: {e}")
        sys.exit(1)


def update_ranking(args):
    """Update agent rankings based on metrics."""
    registry, jobs, metrics, memory, db_session = get_services()
    
    try:
        success = metrics.update_agent_ranking()
        if success:
            print("✅ Agent rankings updated based on metrics")
        else:
            print("❌ Failed to update rankings")
            sys.exit(1)
    except Exception as e:
        print(f"Error updating rankings: {e}")
        sys.exit(1)


def store_memory(args):
    """Store a memory for an agent."""
    registry, jobs, metrics, memory, db_session = get_services()
    
    try:
        agent_id = UUID(args.agent_id)
        memory_entry = memory.store_memory(
            agent_id=agent_id,
            memory_type=args.memory_type,
            content=args.content
        )
        print(f"✅ Memory stored for agent {args.agent_id}")
    except ValueError as e:
        print(f"Invalid input: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error storing memory: {e}")
        sys.exit(1)


def get_memories(args):
    """Get memories for an agent."""
    registry, jobs, metrics, memory, db_session = get_services()
    
    try:
        agent_id = UUID(args.agent_id)
        memory_list = memory.get_memories(
            agent_id=agent_id,
            memory_type=getattr(args, 'memory_type', None),
            limit=getattr(args, 'limit', 10)
        )
        
        if not memory_list:
            print("No memories found for this agent.")
            return
        
        print(f"Found {len(memory_list)} memory(ies):")
        print("-" * 80)
        for mem in memory_list:
            print(f"📝 {mem['memory_type']} ({mem['created_at']})")
            print(f"   Content: {mem['content'][:100]}{'...' if len(mem['content']) > 100 else ''}")
            print()
    
    except ValueError:
        print("Invalid UUID provided")
        sys.exit(1)
    except Exception as e:
        print(f"Error retrieving memories: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="omega",
        description="Omega Stack Agent and Research Job Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  omega agent list                                    # List all agents
  omega agent list-jobs --status open                # List open jobs
  omega agent claim agent123 job456                  # Claim a job
  omega agent register --name "Agent-X" --model "gpt-4"  # Register agent
  omega job create --slug "test-job" --title "Test"  # Create job
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Agent commands
    agent_parser = subparsers.add_parser("agent", help="Agent management commands")
    agent_subparsers = agent_parser.add_subparsers(dest="subcommand", help="Agent subcommands")
    
    # List agents
    list_agents_parser = agent_subparsers.add_parser("list", help="List all agents")
    list_agents_parser.add_argument("--status", help="Filter by status (active, inactive, etc.)")
    list_agents_parser.set_defaults(func=list_agents)
    
    # Register agent
    register_parser = agent_subparsers.add_parser("register", help="Register a new agent")
    register_parser.add_argument("--name", required=True, help="Agent name")
    register_parser.add_argument("--model", required=True, help="Agent model")
    register_parser.add_argument("--runtime", default="unknown", help="Agent runtime")
    register_parser.add_argument("--email", help="Agent email")
    register_parser.set_defaults(func=register_agent)
    
    # Update agent status
    status_parser = agent_subparsers.add_parser("status", help="Update agent status")
    status_parser.add_argument("agent_id", help="Agent UUID")
    status_parser.add_argument("status", choices=["active", "inactive", "busy"], help="New status")
    status_parser.set_defaults(func=update_agent_status)
    
    # Set agent preferences
    prefs_parser = agent_subparsers.add_parser("preferences", help="Set agent domain preferences")
    prefs_parser.add_argument("agent_id", help="Agent UUID")
    prefs_parser.add_argument("preferences", nargs="+", help="Domain:score pairs (e.g., ml:0.8 nlp:0.6)")
    prefs_parser.set_defaults(func=set_agent_preferences)
    
    # List jobs
    list_jobs_parser = agent_subparsers.add_parser("list-jobs", help="List available jobs")
    list_jobs_parser.add_argument("--status", help="Filter by job status")
    list_jobs_parser.add_argument("--claimed-by", help="Filter by claiming agent")
    list_jobs_parser.add_argument("--domain-tags", help="Filter by domain tags (comma-separated)")
    list_jobs_parser.set_defaults(func=list_jobs)
    
    # Claim job
    claim_parser = agent_subparsers.add_parser("claim", help="Claim a job")
    claim_parser.add_argument("agent_id", help="Agent UUID")
    claim_parser.add_argument("job_id", help="Job UUID")
    claim_parser.set_defaults(func=claim_job)
    
    # Invite collaborator
    invite_parser = agent_subparsers.add_parser("invite", help="Invite agent to collaborate")
    invite_parser.add_argument("agent_id", help="Inviting agent UUID")
    invite_parser.add_argument("job_id", help="Job UUID")
    invite_parser.add_argument("target_agent", help="Target agent UUID")
    invite_parser.set_defaults(func=invite_agent)
    
    # Job commands
    job_parser = subparsers.add_parser("job", help="Job management commands")
    job_subparsers = job_parser.add_subparsers(dest="subcommand", help="Job subcommands")
    
    # Create job
    create_job_parser = job_subparsers.add_parser("create", help="Create a new job")
    create_job_parser.add_argument("--slug", required=True, help="Job slug")
    create_job_parser.add_argument("--title", required=True, help="Job title")
    create_job_parser.add_argument("--description", help="Job description")
    create_job_parser.add_argument("--domain-tags", help="Comma-separated domain tags")
    create_job_parser.set_defaults(func=create_job)
    
    # Complete job
    complete_job_parser = job_subparsers.add_parser("complete", help="Mark job as completed")
    complete_job_parser.add_argument("job_id", help="Job UUID")
    complete_job_parser.set_defaults(func=complete_job)
    
    # Metrics commands
    metrics_parser = subparsers.add_parser("metrics", help="Metrics management commands")
    metrics_subparsers = metrics_parser.add_subparsers(dest="subcommand", help="Metrics subcommands")
    
    # Record metric
    record_metric_parser = metrics_subparsers.add_parser("record", help="Record a metric")
    record_metric_parser.add_argument("agent_id", help="Agent UUID")
    record_metric_parser.add_argument("metric_name", help="Metric name")
    record_metric_parser.add_argument("value", help="Metric value")
    record_metric_parser.set_defaults(func=record_metric)
    
    # Update ranking
    ranking_parser = metrics_subparsers.add_parser("ranking", help="Update agent rankings")
    ranking_parser.set_defaults(func=update_ranking)
    
    # Memory commands
    memory_parser = subparsers.add_parser("memory", help="Memory management commands")
    memory_subparsers = memory_parser.add_subparsers(dest="subcommand", help="Memory subcommands")
    
    # Store memory
    store_memory_parser = memory_subparsers.add_parser("store", help="Store a memory")
    store_memory_parser.add_argument("agent_id", help="Agent UUID")
    store_memory_parser.add_argument("memory_type", choices=["conversation", "task", "knowledge"], help="Memory type")
    store_memory_parser.add_argument("content", help="Memory content")
    store_memory_parser.set_defaults(func=store_memory)
    
    # Get memories
    get_memories_parser = memory_subparsers.add_parser("list", help="List agent memories")
    get_memories_parser.add_argument("agent_id", help="Agent UUID")
    get_memories_parser.add_argument("--memory-type", help="Filter by memory type")
    get_memories_parser.add_argument("--limit", type=int, default=10, help="Limit results")
    get_memories_parser.set_defaults(func=get_memories)
    
    # Parse arguments and execute
    args = parser.parse_args()
    
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
