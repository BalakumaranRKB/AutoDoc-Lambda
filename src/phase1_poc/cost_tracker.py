"""
Cost tracking for API calls and documentation generation.

Tracks token usage and costs for Claude API calls.
"""
import logging
from typing import List, Dict, Any
from datetime import datetime
from models import CostMetrics


logger = logging.getLogger(__name__)


def format_currency(amount: float, currency: str = "USD") -> str:
    """Format amount as currency string."""
    if currency == "INR":
        return f"₹{amount:.2f}"
    elif currency == "USD":
        return f"${amount:.2f}"
    else:
        return f"{amount:.2f} {currency}"


class CostTracker:
    """
    Tracks costs for documentation generation.
    """
    
    def __init__(self):
        """Initialize the cost tracker."""
        self.metrics: List[CostMetrics] = []
        self.file_costs: Dict[str, CostMetrics] = {}
        logger.info("Cost tracker initialized")
    
    def add_cost(self, file_path: str, metrics: CostMetrics) -> None:
        """
        Add cost metrics for a file.
        
        Args:
            file_path: Path to the file
            metrics: Cost metrics to add
        """
        self.metrics.append(metrics)
        self.file_costs[file_path] = metrics
        
        logger.info(
            f"Cost added for {file_path}: "
            f"{metrics.total_tokens} tokens, "
            f"{format_currency(metrics.total_cost, 'USD')}"
        )
    
    def get_total_cost(self) -> float:
        """
        Get total cost across all files.
        
        Returns:
            Total cost in USD
        """
        return sum(m.total_cost for m in self.metrics)
    
    def get_total_tokens(self) -> int:
        """
        Get total token count across all files.
        
        Returns:
            Total token count
        """
        return sum(m.total_tokens for m in self.metrics)
    
    def get_file_cost(self, file_path: str) -> float:
        """
        Get cost for a specific file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Cost in USD (0.0 if not found)
        """
        metrics = self.file_costs.get(file_path)
        return metrics.total_cost if metrics else 0.0
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all costs.
        
        Returns:
            Dictionary with cost summary
        """
        total_cost = self.get_total_cost()
        total_tokens = self.get_total_tokens()
        file_count = len(self.file_costs)
        
        avg_cost_per_file = total_cost / file_count if file_count > 0 else 0.0
        avg_tokens_per_file = total_tokens // file_count if file_count > 0 else 0
        
        # Convert to INR (rough conversion: 1 USD = 83 INR)
        usd_to_inr = 83.0
        total_cost_inr = total_cost * usd_to_inr
        
        summary = {
            "total_files": file_count,
            "total_tokens": total_tokens,
            "total_cost_usd": round(total_cost, 4),
            "total_cost_inr": round(total_cost_inr, 2),
            "avg_tokens_per_file": avg_tokens_per_file,
            "avg_cost_per_file_usd": round(avg_cost_per_file, 4),
            "avg_cost_per_file_inr": round(avg_cost_per_file * usd_to_inr, 2),
            "files": [
                {
                    "file": file_path,
                    "tokens": metrics.total_tokens,
                    "cost_usd": round(metrics.total_cost, 4),
                    "cost_inr": round(metrics.total_cost * usd_to_inr, 2)
                }
                for file_path, metrics in self.file_costs.items()
            ]
        }
        
        return summary
    
    def print_summary(self) -> None:
        """Print a formatted cost summary."""
        summary = self.get_summary()
        
        print("\n" + "=" * 60)
        print("COST SUMMARY")
        print("=" * 60)
        print(f"Total Files Processed: {summary['total_files']}")
        print(f"Total Tokens Used: {summary['total_tokens']:,}")
        print(f"Total Cost (USD): ${summary['total_cost_usd']:.4f}")
        print(f"Total Cost (INR): ₹{summary['total_cost_inr']:.2f}")
        print(f"\nAverage per File:")
        print(f"  Tokens: {summary['avg_tokens_per_file']:,}")
        print(f"  Cost (USD): ${summary['avg_cost_per_file_usd']:.4f}")
        print(f"  Cost (INR): ₹{summary['avg_cost_per_file_inr']:.2f}")
        
        if summary['files']:
            print(f"\nPer-File Breakdown:")
            print("-" * 60)
            for file_info in summary['files']:
                print(f"{file_info['file']}")
                print(f"  Tokens: {file_info['tokens']:,}")
                print(f"  Cost: ${file_info['cost_usd']:.4f} (₹{file_info['cost_inr']:.2f})")
        
        print("=" * 60 + "\n")
    
    def export_to_cloudwatch(self) -> Dict[str, Any]:
        """
        Export metrics in CloudWatch-compatible format.
        
        Returns:
            Dictionary suitable for CloudWatch Metrics
        """
        summary = self.get_summary()
        
        return {
            "Namespace": "CodeDocumentation",
            "MetricData": [
                {
                    "MetricName": "TotalCost",
                    "Value": summary["total_cost_usd"],
                    "Unit": "None",
                    "Timestamp": datetime.utcnow().isoformat()
                },
                {
                    "MetricName": "TotalTokens",
                    "Value": summary["total_tokens"],
                    "Unit": "Count",
                    "Timestamp": datetime.utcnow().isoformat()
                },
                {
                    "MetricName": "FilesProcessed",
                    "Value": summary["total_files"],
                    "Unit": "Count",
                    "Timestamp": datetime.utcnow().isoformat()
                },
                {
                    "MetricName": "AvgCostPerFile",
                    "Value": summary["avg_cost_per_file_usd"],
                    "Unit": "None",
                    "Timestamp": datetime.utcnow().isoformat()
                }
            ]
        }
