"""
Utility functions.
"""
import hashlib
import logging
from typing import Dict


def setup_logging(log_level: str = "INFO") -> None:
    """Configure logging for the application."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def calculate_file_hash(content: str) -> str:
    """Calculate SHA256 hash of file content."""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def count_lines(content: str) -> Dict[str, int]:
    """Count different types of lines in code."""
    lines = content.split('\n')
    total_lines = len(lines)
    blank_lines = sum(1 for line in lines if not line.strip())
    comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
    code_lines = total_lines - blank_lines - comment_lines
    
    return {
        "total": total_lines,
        "code": code_lines,
        "comment": comment_lines,
        "blank": blank_lines
    }
