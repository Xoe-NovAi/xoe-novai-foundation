#!/usr/bin/env python3
"""
Session Intelligence Crawler (SIC)
==================================

Intelligent chat session management system for pruning excessive shell outputs
and optimizing session storage while preserving critical information.
"""

import asyncio
import json
import logging
import re
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib

logger = logging.getLogger(__name__)

class SessionType(Enum):
    """Types of chat sessions."""
    CLI_SESSION = "cli_session"
    IDE_SESSION = "ide_session"
    WEB_SESSION = "web_session"
    AGENT_SESSION = "agent_session"

class ContentCategory(Enum):
    """Categories of session content."""
    USER_PROMPT = "user_prompt"
    AGENT_RESPONSE = "agent_response"
    SHELL_OUTPUT = "shell_output"
    ERROR_MESSAGE = "error_message"
    SYSTEM_MESSAGE = "system_message"
    FILE_OPERATION = "file_operation"
    TOOL_USAGE = "tool_usage"

@dataclass
class SessionMetadata:
    """Metadata for a chat session."""
    session_id: str
    session_type: SessionType
    agent_id: str
    start_time: float
    end_time: float
    total_messages: int
    total_size: int
    compressed_size: int
    quality_score: float
    preservation_score: float
    last_modified: float

@dataclass
class ContentBlock:
    """A block of content within a session."""
    content_id: str
    category: ContentCategory
    content: str
    timestamp: float
    preserved: bool
    summary: Optional[str] = None
    compression_ratio: float = 1.0

class SessionIntelligenceCrawler:
    """
    Core SIC implementation for intelligent session management.
    """
    
    def __init__(self, sessions_directory: str = "data/sessions"):
        self.sessions_directory = Path(sessions_directory)
        self.sessions_directory.mkdir(parents=True, exist_ok=True)
        
        # Shell output patterns for detection
        self.shell_output_patterns = [
            # Command execution patterns
            r"Output: (.*?)Process Group PGID:",
            r"Exit Code: \d+",
            r"Command executed successfully",
            r"Command failed with exit code \d+",
            
            # Git output patterns
            r"commit [a-f0-9]{40}",
            r"Author: .*? <.*?>",
            r"Date:   .*",
            r"Merge: [a-f0-9]{7} [a-f0-9]{7}",
            
            # Build output patterns
            r"Compiling \d+ files",
            r"Build successful",
            r"Build failed",
            r"Error: .*",
            r"Warning: .*",
            
            # Docker output patterns
            r"Successfully built [a-f0-9]{12}",
            r"Container [a-f0-9]{12} started",
            r"Container [a-f0-9]{12} stopped",
            
            # Package manager patterns
            r"Installing \d+ packages",
            r"Package \w+ installed successfully",
            r"Package \w+ already installed",
        ]
        
        # Preservation rules
        self.preservation_rules = {
            ContentCategory.USER_PROMPT: True,
            ContentCategory.AGENT_RESPONSE: True,
            ContentCategory.ERROR_MESSAGE: True,
            ContentCategory.SYSTEM_MESSAGE: True,
            ContentCategory.FILE_OPERATION: True,
            ContentCategory.TOOL_USAGE: True,
            ContentCategory.SHELL_OUTPUT: False  # Will be processed for summarization
        }
        
        # Summarization thresholds
        self.summarization_threshold = 1000  # characters
        self.preservation_threshold = 5000   # characters (never prune if under this)
        
    def detect_shell_outputs(self, content: str) -> List[Tuple[int, int, str]]:
        """Detect shell output blocks in content."""
        shell_blocks = []
        
        for pattern in self.shell_output_patterns:
            matches = re.finditer(pattern, content, re.DOTALL | re.MULTILINE)
            for match in matches:
                start, end = match.span()
                block_content = content[start:end]
                shell_blocks.append((start, end, block_content))
        
        # Sort by position and merge overlapping blocks
        shell_blocks.sort()
        merged_blocks = []
        
        for start, end, content in shell_blocks:
            if not merged_blocks:
                merged_blocks.append((start, end, content))
            else:
                last_start, last_end, last_content = merged_blocks[-1]
                if start <= last_end:  # Overlapping
                    merged_blocks[-1] = (last_start, max(end, last_end), last_content + content)
                else:
                    merged_blocks.append((start, end, content))
        
        return merged_blocks
    
    def summarize_shell_output(self, shell_output: str) -> str:
        """Generate a concise summary of shell output."""
        try:
            # Extract key information
            lines = shell_output.split('\n')
            summary_lines = []
            
            # Look for important patterns
            important_patterns = [
                r"Error: .*",
                r"Warning: .*",
                r"Exit Code: \d+",
                r"Build (successful|failed)",
                r"commit [a-f0-9]{40}",
                r"Successfully built [a-f0-9]{12}",
                r"Container .* (started|stopped)",
                r"Installing \d+ packages",
                r"Package \w+ (installed|failed)"
            ]
            
            for line in lines:
                for pattern in important_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        summary_lines.append(line.strip())
                        break
            
            # If no important patterns found, take first and last lines
            if not summary_lines and lines:
                if len(lines) > 1:
                    summary_lines = [lines[0].strip(), "...", lines[-1].strip()]
                else:
                    summary_lines = [lines[0].strip()]
            
            # Generate summary
            if len(summary_lines) <= 3:
                return "Shell output: " + " | ".join(summary_lines)
            else:
                return f"Shell output ({len(lines)} lines): " + " | ".join(summary_lines[:3]) + "..."
                
        except Exception as e:
            logger.error(f"Failed to summarize shell output: {e}")
            return f"Shell output (summarized): {len(shell_output)} characters processed"
    
    def calculate_session_quality(self, session_data: Dict[str, Any]) -> float:
        """Calculate quality score for a session."""
        try:
            total_messages = len(session_data.get("messages", []))
            if total_messages == 0:
                return 0.0
            
            # Count different message types
            user_messages = 0
            agent_messages = 0
            shell_outputs = 0
            errors = 0
            
            for message in session_data.get("messages", []):
                content = message.get("content", "")
                if message.get("role") == "user":
                    user_messages += 1
                elif message.get("role") == "assistant":
                    agent_messages += 1
                
                # Check for shell output patterns
                if any(re.search(pattern, content, re.IGNORECASE) for pattern in self.shell_output_patterns):
                    shell_outputs += 1
                
                # Check for error patterns
                if re.search(r"Error:|Failed:|Exception:", content, re.IGNORECASE):
                    errors += 1
            
            # Calculate quality metrics
            user_ratio = user_messages / total_messages
            agent_ratio = agent_messages / total_messages
            shell_ratio = shell_outputs / total_messages
            error_ratio = errors / total_messages
            
            # Quality score calculation
            quality = 0.0
            
            # Good user/agent ratio
            if 0.3 <= user_ratio <= 0.7:
                quality += 0.4
            
            # Low shell output ratio
            if shell_ratio < 0.3:
                quality += 0.3
            
            # Low error ratio
            if error_ratio < 0.1:
                quality += 0.2
            
            # High agent engagement
            if agent_ratio > 0.4:
                quality += 0.1
            
            return min(quality, 1.0)
            
        except Exception as e:
            logger.error(f"Failed to calculate session quality: {e}")
            return 0.5
    
    def prune_session(self, session_file: Path) -> Tuple[bool, Dict[str, Any]]:
        """Prune a session file and return the result."""
        try:
            # Load session data
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            
            original_size = len(json.dumps(session_data))
            
            # Analyze session
            session_type = self._detect_session_type(session_data)
            session_id = session_file.stem
            agent_id = session_data.get("agent_id", "unknown")
            
            # Process messages
            pruned_messages = []
            total_pruned = 0
            total_preserved = 0
            
            for message in session_data.get("messages", []):
                content = message.get("content", "")
                category = self._categorize_content(content, message.get("role"))
                
                if self.preservation_rules.get(category, False):
                    # Preserve this content
                    pruned_messages.append(message)
                    total_preserved += 1
                else:
                    # Process for potential pruning
                    if len(content) > self.summarization_threshold:
                        # Summarize long content
                        summary = self.summarize_shell_output(content)
                        message["content"] = summary
                        message["metadata"] = message.get("metadata", {})
                        message["metadata"]["original_length"] = len(content)
                        message["metadata"]["summarized"] = True
                        pruned_messages.append(message)
                        total_pruned += 1
                    else:
                        # Keep short content
                        pruned_messages.append(message)
                        total_preserved += 1
            
            # Update session data
            session_data["messages"] = pruned_messages
            session_data["metadata"] = session_data.get("metadata", {})
            session_data["metadata"]["pruned"] = True
            session_data["metadata"]["pruned_at"] = datetime.now().isoformat()
            session_data["metadata"]["total_pruned"] = total_pruned
            session_data["metadata"]["total_preserved"] = total_preserved
            
            # Calculate quality score
            quality_score = self.calculate_session_quality(session_data)
            session_data["metadata"]["quality_score"] = quality_score
            
            # Save pruned session
            pruned_file = session_file.with_suffix('.pruned.json')
            with open(pruned_file, 'w') as f:
                json.dump(session_data, f, indent=2)
            
            new_size = len(json.dumps(session_data))
            compression_ratio = (original_size - new_size) / original_size if original_size > 0 else 0
            
            # Create metadata
            metadata = SessionMetadata(
                session_id=session_id,
                session_type=session_type,
                agent_id=agent_id,
                start_time=session_data.get("start_time", 0),
                end_time=session_data.get("end_time", 0),
                total_messages=len(pruned_messages),
                total_size=original_size,
                compressed_size=new_size,
                quality_score=quality_score,
                preservation_score=total_preserved / (total_preserved + total_pruned) if (total_preserved + total_pruned) > 0 else 1.0,
                last_modified=datetime.now().timestamp()
            )
            
            logger.info(f"Pruned session {session_id}: {compression_ratio:.2%} compression, quality: {quality_score:.2f}")
            return True, asdict(metadata)
            
        except Exception as e:
            logger.error(f"Failed to prune session {session_file}: {e}")
            return False, {}
    
    def _detect_session_type(self, session_data: Dict[str, Any]) -> SessionType:
        """Detect the type of session based on its content."""
        try:
            # Check for CLI-specific patterns
            if any("cline" in str(session_data.get(key, "")) for key in ["agent_id", "metadata"]):
                return SessionType.CLI_SESSION
            elif any("copilot" in str(session_data.get(key, "")) for key in ["agent_id", "metadata"]):
                return SessionType.CLI_SESSION
            elif any("opencode" in str(session_data.get(key, "")) for key in ["agent_id", "metadata"]):
                return SessionType.CLI_SESSION
            elif any("gemini" in str(session_data.get(key, "")) for key in ["agent_id", "metadata"]):
                return SessionType.CLI_SESSION
            elif any("extension" in str(session_data.get(key, "")) for key in ["agent_id", "metadata"]):
                return SessionType.IDE_SESSION
            elif any("web" in str(session_data.get(key, "")) for key in ["agent_id", "metadata"]):
                return SessionType.WEB_SESSION
            else:
                return SessionType.AGENT_SESSION
        except Exception:
            return SessionType.AGENT_SESSION
    
    def _categorize_content(self, content: str, role: str) -> ContentCategory:
        """Categorize content based on patterns and role."""
        try:
            content_lower = content.lower()
            
            # Check for error patterns
            if re.search(r"error:|failed:|exception:|traceback:", content_lower):
                return ContentCategory.ERROR_MESSAGE
            
            # Check for system messages
            if re.search(r"system:|info:|debug:", content_lower):
                return ContentCategory.SYSTEM_MESSAGE
            
            # Check for file operations
            if re.search(r"file:|directory:|path:|created:|modified:", content_lower):
                return ContentCategory.FILE_OPERATION
            
            # Check for tool usage
            if re.search(r"tool:|command:|execute:|run:", content_lower):
                return ContentCategory.TOOL_USAGE
            
            # Check for shell output patterns
            if any(re.search(pattern, content, re.IGNORECASE) for pattern in self.shell_output_patterns):
                return ContentCategory.SHELL_OUTPUT
            
            # Default based on role
            if role == "user":
                return ContentCategory.USER_PROMPT
            elif role == "assistant":
                return ContentCategory.AGENT_RESPONSE
            else:
                return ContentCategory.SYSTEM_MESSAGE
                
        except Exception:
            return ContentCategory.SYSTEM_MESSAGE
    
    async def crawl_sessions(self, max_sessions: int = 100) -> Dict[str, Any]:
        """Crawl and process session files."""
        try:
            # Find session files
            session_files = []
            for pattern in ["*.json", "*.session", "*.chat"]:
                session_files.extend(self.sessions_directory.glob(f"**/{pattern}"))
            
            # Filter out already pruned files
            session_files = [f for f in session_files if not f.name.endswith('.pruned.json')]
            
            # Sort by modification time (oldest first)
            session_files.sort(key=lambda x: x.stat().st_mtime)
            
            # Process sessions
            results = {
                "processed": 0,
                "pruned": 0,
                "failed": 0,
                "total_original_size": 0,
                "total_compressed_size": 0,
                "sessions": []
            }
            
            for session_file in session_files[:max_sessions]:
                try:
                    # Check if session needs pruning
                    with open(session_file, 'r') as f:
                        session_data = json.load(f)
                    
                    # Calculate current size
                    current_size = len(json.dumps(session_data))
                    
                    # Skip if already compressed enough or too small
                    if current_size < self.preservation_threshold:
                        continue
                    
                    # Check if already pruned
                    if session_data.get("metadata", {}).get("pruned", False):
                        continue
                    
                    # Prune the session
                    success, metadata = self.prune_session(session_file)
                    
                    if success:
                        results["pruned"] += 1
                        results["total_original_size"] += metadata["total_size"]
                        results["total_compressed_size"] += metadata["compressed_size"]
                        results["sessions"].append(metadata)
                    else:
                        results["failed"] += 1
                    
                    results["processed"] += 1
                    
                except Exception as e:
                    logger.error(f"Failed to process session {session_file}: {e}")
                    results["failed"] += 1
            
            # Calculate overall statistics
            if results["total_original_size"] > 0:
                results["overall_compression_ratio"] = (
                    results["total_original_size"] - results["total_compressed_size"]
                ) / results["total_original_size"]
            else:
                results["overall_compression_ratio"] = 0.0
            
            logger.info(f"Session crawling completed: {results['processed']} processed, {results['pruned']} pruned")
            return results
            
        except Exception as e:
            logger.error(f"Failed to crawl sessions: {e}")
            return {"error": str(e)}
    
    async def cleanup_old_sessions(self, max_age_days: int = 30) -> Dict[str, Any]:
        """Clean up old session files."""
        try:
            cutoff_time = datetime.now() - timedelta(days=max_age_days)
            cleaned_files = []
            
            for session_file in self.sessions_directory.glob("**/*.json"):
                try:
                    # Check modification time
                    mod_time = datetime.fromtimestamp(session_file.stat().st_mtime)
                    if mod_time < cutoff_time:
                        # Check if pruned version exists
                        pruned_file = session_file.with_suffix('.pruned.json')
                        if pruned_file.exists():
                            # Remove original, keep pruned
                            session_file.unlink()
                            cleaned_files.append(str(session_file))
                        elif session_file.stat().st_size > self.preservation_threshold:
                            # Prune before deleting
                            success, _ = self.prune_session(session_file)
                            if success:
                                session_file.unlink()
                                cleaned_files.append(str(session_file))
                
                except Exception as e:
                    logger.error(f"Failed to clean up {session_file}: {e}")
            
            logger.info(f"Cleaned up {len(cleaned_files)} old session files")
            return {"cleaned_files": cleaned_files, "count": len(cleaned_files)}
            
        except Exception as e:
            logger.error(f"Failed to cleanup old sessions: {e}")
            return {"error": str(e)}
    
    async def generate_session_report(self) -> Dict[str, Any]:
        """Generate a comprehensive session management report."""
        try:
            # Analyze all sessions
            session_files = list(self.sessions_directory.glob("**/*.json"))
            pruned_files = list(self.sessions_directory.glob("**/*.pruned.json"))
            
            # Calculate statistics
            total_sessions = len(session_files) + len(pruned_files)
            pruned_count = len(pruned_files)
            original_size = sum(f.stat().st_size for f in session_files)
            pruned_size = sum(f.stat().st_size for f in pruned_files)
            
            # Analyze session types
            session_types = {}
            for session_file in session_files:
                try:
                    with open(session_file, 'r') as f:
                        session_data = json.load(f)
                    session_type = self._detect_session_type(session_data).value
                    session_types[session_type] = session_types.get(session_type, 0) + 1
                except Exception:
                    pass
            
            report = {
                "timestamp": datetime.now().isoformat(),
                "total_sessions": total_sessions,
                "pruned_sessions": pruned_count,
                "pruning_rate": pruned_count / total_sessions if total_sessions > 0 else 0,
                "storage_statistics": {
                    "original_size_bytes": original_size,
                    "pruned_size_bytes": pruned_size,
                    "total_saved_bytes": original_size + pruned_size,
                    "compression_ratio": (original_size + pruned_size) / (original_size + pruned_size + 1) if (original_size + pruned_size) > 0 else 0
                },
                "session_types": session_types,
                "recommendations": []
            }
            
            # Generate recommendations
            if report["pruning_rate"] < 0.5:
                report["recommendations"].append("Consider increasing pruning frequency to reduce storage usage")
            
            if report["storage_statistics"]["compression_ratio"] < 0.3:
                report["recommendations"].append("Current compression ratio is low - consider more aggressive pruning")
            
            if any(count > 100 for count in session_types.values()):
                report["recommendations"].append("High session volume detected - consider implementing automatic cleanup")
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate session report: {e}")
            return {"error": str(e)}

# Global SIC instance
_sic_instance: Optional[SessionIntelligenceCrawler] = None

def get_sic() -> SessionIntelligenceCrawler:
    """Get the global SIC instance."""
    global _sic_instance
    if _sic_instance is None:
        _sic_instance = SessionIntelligenceCrawler()
    return _sic_instance

# Convenience functions
async def crawl_sessions(max_sessions: int = 100) -> Dict[str, Any]:
    """Crawl and process session files."""
    sic = get_sic()
    return await sic.crawl_sessions(max_sessions)

async def cleanup_old_sessions(max_age_days: int = 30) -> Dict[str, Any]:
    """Clean up old session files."""
    sic = get_sic()
    return await sic.cleanup_old_sessions(max_age_days)

async def generate_session_report() -> Dict[str, Any]:
    """Generate a comprehensive session management report."""
    sic = get_sic()
    return await sic.generate_session_report()