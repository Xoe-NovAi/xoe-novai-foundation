"""
Utility functions for Documentation Generation Service

Provides common utilities for file operations, validation, and system integration.
"""

import os
import logging
from pathlib import Path
from typing import Union

logger = logging.getLogger(__name__)


def validate_output_path(output_path: str) -> bool:
    """
    Validate that output path is safe and within allowed directories.
    
    Args:
        output_path: Path to validate
        
    Returns:
        True if path is valid, raises ValueError otherwise
    """
    path = Path(output_path)
    
    # Check if path is absolute
    if not path.is_absolute():
        raise ValueError("Output path must be absolute")
    
    # Check if path is within allowed directories
    allowed_prefixes = [
        Path("/home/arcana-novai/Documents/xnai-foundation/docs"),
        Path("/home/arcana-novai/Documents/xnai-foundation/documentation"),
        Path("/workspace/docs"),  # For container environments
        Path("/workspace/documentation"),
    ]
    
    path_resolved = path.resolve()
    is_allowed = any(
        str(path_resolved).startswith(str(prefix.resolve()))
        for prefix in allowed_prefixes
    )
    
    if not is_allowed:
        raise ValueError(f"Output path '{output_path}' is not within allowed directories")
    
    # Check for directory traversal attempts
    try:
        path.resolve().relative_to(path.parent.resolve())
    except ValueError:
        raise ValueError("Output path contains invalid directory traversal")
    
    return True


def ensure_directory(directory: Union[str, Path]) -> Path:
    """
    Ensure directory exists, creating it if necessary.
    
    Args:
        directory: Directory path to ensure
        
    Returns:
        Path object for the directory
    """
    dir_path = Path(directory)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def get_file_size(file_path: Union[str, Path]) -> int:
    """
    Get file size in bytes.
    
    Args:
        file_path: Path to file
        
    Returns:
        File size in bytes, or 0 if file doesn't exist
    """
    try:
        return Path(file_path).stat().st_size
    except (FileNotFoundError, OSError):
        return 0


def is_text_file(file_path: Union[str, Path]) -> bool:
    """
    Check if file is likely a text file.
    
    Args:
        file_path: Path to file
        
    Returns:
        True if file appears to be text, False otherwise
    """
    text_extensions = {
        '.md', '.txt', '.rst', '.html', '.xml', '.json', '.yaml', '.yml',
        '.py', '.js', '.ts', '.java', '.go', '.rust', '.c', '.cpp', '.h',
        '.sh', '.bash', '.zsh', '.fish', '.ps1', '.bat', '.cmd'
    }
    
    file_path = Path(file_path)
    return file_path.suffix.lower() in text_extensions


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing or replacing unsafe characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Replace unsafe characters
    unsafe_chars = '<>:"/\\|?*'
    for char in unsafe_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing whitespace and dots
    filename = filename.strip().strip('.')
    
    # Ensure filename is not empty
    if not filename:
        filename = 'untitled'
    
    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    
    return filename


def get_mime_type(file_path: Union[str, Path]) -> str:
    """
    Get MIME type for a file based on extension.
    
    Args:
        file_path: Path to file
        
    Returns:
        MIME type string
    """
    file_path = Path(file_path)
    extension = file_path.suffix.lower()
    
    mime_types = {
        '.md': 'text/markdown',
        '.txt': 'text/plain',
        '.rst': 'text/x-rst',
        '.html': 'text/html',
        '.xml': 'application/xml',
        '.json': 'application/json',
        '.yaml': 'application/x-yaml',
        '.yml': 'application/x-yaml',
        '.py': 'text/x-python',
        '.js': 'application/javascript',
        '.ts': 'application/typescript',
        '.java': 'text/x-java-source',
        '.go': 'text/x-go',
        '.rust': 'text/x-rust-src',
        '.c': 'text/x-csrc',
        '.cpp': 'text/x-c++src',
        '.h': 'text/x-chdr',
        '.sh': 'application/x-sh',
        '.bash': 'application/x-bash',
        '.zsh': 'application/x-zsh',
        '.fish': 'application/x-fish',
        '.ps1': 'application/x-powershell',
        '.bat': 'application/x-bat',
        '.cmd': 'application/x-cmd',
    }
    
    return mime_types.get(extension, 'application/octet-stream')


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Human-readable file size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"


def get_git_status() -> dict:
    """
    Get current git repository status.
    
    Returns:
        Dictionary with git status information
    """
    try:
        import git
        repo = git.Repo(search_parent_directories=True)
        
        status = {
            'is_dirty': repo.is_dirty(),
            'untracked_files': repo.untracked_files,
            'active_branch': repo.active_branch.name,
            'head_commit': str(repo.head.commit)[:8],
            'remotes': [remote.name for remote in repo.remotes],
        }
        
        return status
    except Exception as e:
        logger.warning(f"Could not get git status: {str(e)}")
        return {
            'is_dirty': False,
            'untracked_files': [],
            'active_branch': 'unknown',
            'head_commit': 'unknown',
            'remotes': [],
        }


def create_backup(file_path: Union[str, Path], suffix: str = '.backup') -> Path:
    """
    Create a backup of a file.
    
    Args:
        file_path: Path to file to backup
        suffix: Suffix to add to backup file name
        
    Returns:
        Path to backup file
    """
    file_path = Path(file_path)
    backup_path = file_path.with_suffix(file_path.suffix + suffix)
    
    if file_path.exists():
        import shutil
        shutil.copy2(file_path, backup_path)
        logger.info(f"Created backup: {backup_path}")
    
    return backup_path


def atomic_write(file_path: Union[str, Path], content: str, encoding: str = 'utf-8') -> bool:
    """
    Atomically write content to a file.
    
    Args:
        file_path: Path to file to write
        content: Content to write
        encoding: File encoding
        
    Returns:
        True if write was successful
    """
    file_path = Path(file_path)
    
    try:
        # Write to temporary file first
        temp_path = file_path.with_suffix(file_path.suffix + '.tmp')
        
        with open(temp_path, 'w', encoding=encoding) as f:
            f.write(content)
        
        # Atomic move
        temp_path.replace(file_path)
        
        logger.debug(f"Successfully wrote to {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to write to {file_path}: {str(e)}")
        return False


def get_system_info() -> dict:
    """
    Get system information for debugging.
    
    Returns:
        Dictionary with system information
    """
    import platform
    import psutil
    
    try:
        return {
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'cpu_count': psutil.cpu_count(),
            'memory_total': format_file_size(psutil.virtual_memory().total),
            'memory_available': format_file_size(psutil.virtual_memory().available),
            'disk_usage': format_file_size(psutil.disk_usage('/').total),
            'working_directory': str(Path.cwd()),
            'environment': dict(os.environ),
        }
    except Exception as e:
        logger.warning(f"Could not get system info: {str(e)}")
        return {
            'platform': 'unknown',
            'python_version': platform.python_version(),
            'cpu_count': 'unknown',
            'memory_total': 'unknown',
            'memory_available': 'unknown',
            'disk_usage': 'unknown',
            'working_directory': str(Path.cwd()),
            'environment': {},
        }