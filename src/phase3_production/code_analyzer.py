"""
Simple code analyzer without pydantic
"""
import ast
import logging
from typing import Dict, Any
from utils import count_lines


logger = logging.getLogger(__name__)


class PythonCodeAnalyzer:
    """Analyzes Python source code structure."""
    
    def __init__(self):
        """Initialize the analyzer."""
        pass
    
    def analyze_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Analyze a Python file and extract structural information."""
        logger.info(f"Analyzing file: {file_path}")
        
        # Count lines
        line_counts = count_lines(content)
        
        # Simple analysis result
        return {
            'file_path': file_path,
            'file_type': 'python',
            'total_lines': line_counts['total'],
            'code_lines': line_counts['code'],
            'comment_lines': line_counts['comment'],
            'blank_lines': line_counts['blank']
        }
