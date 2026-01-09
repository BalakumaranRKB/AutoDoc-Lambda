"""
Cost tracker - simplified without pydantic
"""
import logging
from typing import Dict, Any


logger = logging.getLogger(__name__)


class CostTracker:
    """Tracks costs for documentation generation."""
    
    def __init__(self):
        """Initialize the cost tracker."""
        self.metrics = []
        self.file_costs = {}
        logger.info("Cost tracker initialized")
    
    def add_cost(self, file_path: str, metrics: Dict[str, Any]) -> None:
        """Add cost metrics for a file."""
        self.metrics.append(metrics)
        self.file_costs[file_path] = metrics
        
        logger.info(
            f"Cost added for {file_path}: "
            f"{metrics['total_tokens']} tokens, "
            f"${metrics['total_cost']:.6f}"
        )
    
    def get_total_cost(self) -> float:
        """Get total cost across all files."""
        return sum(m['total_cost'] for m in self.metrics)
    
    def get_total_tokens(self) -> int:
        """Get total token count across all files."""
        return sum(m['total_tokens'] for m in self.metrics)
