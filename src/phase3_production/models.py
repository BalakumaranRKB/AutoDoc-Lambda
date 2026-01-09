"""
Simple data models without pydantic - using plain Python
"""
from typing import Dict, Any, Optional
from datetime import datetime


def create_cost_metrics(input_tokens: int, output_tokens: int, 
                       input_cost: float, output_cost: float) -> Dict[str, Any]:
    """Create cost metrics dictionary."""
    return {
        'input_tokens': input_tokens,
        'output_tokens': output_tokens,
        'total_tokens': input_tokens + output_tokens,
        'input_cost': input_cost,
        'output_cost': output_cost,
        'total_cost': input_cost + output_cost,
        'timestamp': datetime.utcnow().isoformat()
    }


def create_file_analysis(file_path: str, line_counts: Dict) -> Dict[str, Any]:
    """Create file analysis dictionary."""
    return {
        'file_path': file_path,
        'file_type': 'python',
        'total_lines': line_counts['total'],
        'code_lines': line_counts['code'],
        'comment_lines': line_counts['comment'],
        'blank_lines': line_counts['blank'],
        'elements': [],
        'imports': []
    }


def create_documentation_result(
    request_id: str,
    file_path: str,
    documentation: str,
    total_cost: float,
    total_tokens: int,
    processing_time: float,
    cached: bool = False,
    cache_key: Optional[str] = None
) -> Dict[str, Any]:
    """Create documentation result dictionary."""
    return {
        'request_id': request_id,
        'file_path': file_path,
        'status': 'completed',
        'documentation': documentation,
        'analysis': {},
        'total_cost': total_cost,
        'total_tokens': total_tokens,
        'processing_time_seconds': processing_time,
        'cached': cached,
        'cache_key': cache_key,
        'timestamp': datetime.utcnow().isoformat()
    }
