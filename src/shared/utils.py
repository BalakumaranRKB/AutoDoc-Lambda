"""
Utility functions for the Code Documentation Generator.
"""
import hashlib
import json
import logging
from typing import Any, Dict, Optional
from datetime import datetime, timedelta


logger = logging.getLogger(__name__)


def setup_logging(log_level: str = "INFO") -> None:
    """Configure logging for the application."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def calculate_file_hash(content: str) -> str:
    """
    Calculate SHA256 hash of file content.
    
    Args:
        content: File content as string
        
    Returns:
        Hex digest of the hash
    """
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def format_currency(amount: float, currency: str = "INR") -> str:
    """
    Format amount as currency string.
    
    Args:
        amount: Amount to format
        currency: Currency code (INR, USD)
        
    Returns:
        Formatted currency string
    """
    if currency == "INR":
        return f"₹{amount:.2f}"
    elif currency == "USD":
        return f"${amount:.2f}"
    else:
        return f"{amount:.2f} {currency}"


def calculate_ttl(hours: int) -> int:
    """
    Calculate TTL timestamp for cache entries.
    
    Args:
        hours: Number of hours until expiration
        
    Returns:
        Unix timestamp for expiration
    """
    expiration = datetime.utcnow() + timedelta(hours=hours)
    return int(expiration.timestamp())


def is_expired(ttl: int) -> bool:
    """
    Check if a TTL timestamp has expired.
    
    Args:
        ttl: Unix timestamp
        
    Returns:
        True if expired, False otherwise
    """
    return datetime.utcnow().timestamp() > ttl


def safe_json_loads(data: str, default: Any = None) -> Any:
    """
    Safely parse JSON string.
    
    Args:
        data: JSON string
        default: Default value if parsing fails
        
    Returns:
        Parsed JSON or default value
    """
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError) as e:
        logger.warning(f"Failed to parse JSON: {e}")
        return default


def safe_json_dumps(data: Any, default: str = "{}") -> str:
    """
    Safely serialize to JSON string.
    
    Args:
        data: Data to serialize
        default: Default value if serialization fails
        
    Returns:
        JSON string or default value
    """
    try:
        return json.dumps(data)
    except (TypeError, ValueError) as e:
        logger.warning(f"Failed to serialize JSON: {e}")
        return default


def extract_file_extension(file_path: str) -> str:
    """
    Extract file extension from file path.
    
    Args:
        file_path: Path to file
        
    Returns:
        File extension (without dot)
    """
    return file_path.split('.')[-1].lower() if '.' in file_path else ""


def count_lines(content: str) -> Dict[str, int]:
    """
    Count different types of lines in code.
    
    Args:
        content: File content
        
    Returns:
        Dictionary with counts for total, code, comment, blank lines
    """
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


def truncate_string(s: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate string to maximum length.
    
    Args:
        s: String to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated string
    """
    if len(s) <= max_length:
        return s
    return s[:max_length - len(suffix)] + suffix


def bytes_to_human_readable(num_bytes: int) -> str:
    """
    Convert bytes to human-readable format.
    
    Args:
        num_bytes: Number of bytes
        
    Returns:
        Human-readable string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if num_bytes < 1024.0:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f} PB"


def merge_dicts(*dicts: Dict) -> Dict:
    """
    Merge multiple dictionaries.
    
    Args:
        *dicts: Variable number of dictionaries
        
    Returns:
        Merged dictionary
    """
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result
